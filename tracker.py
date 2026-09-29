import json
import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# ============================================================
# TECH TRACKER
# ============================================================

HEADERS = {
    "User-Agent": "TechTracker/1.0"
}

STATE_FILE = "seen.json"


# ============================================================
# YOUR GITHUB PROJECTS
# Add/remove projects here.
# Format:
# "Name": "owner/repository"
# ============================================================

GITHUB_PROJECTS = {
    "UTM": "utmapp/UTM",

    # Add projects you personally want to track:
    # "Dopamine": "opa334/Dopamine",
    # "Example": "owner/repository",
}


# ============================================================
# NEWS SOURCES
# These are RSS feeds, not specific GitHub projects.
# ============================================================

RSS_SOURCES = {
    "iOS / Jailbreak": [
        "https://www.idownloadblog.com/feed/",
    ],

    "PS4 / Homebrew": [
        "https://wololo.net/feed/",
    ],

    "iOS / Emulation": [
        "https://www.macstories.net/feed/",
        "https://9to5mac.com/feed/",
    ],
}


# ============================================================
# WORDS THAT USUALLY MEAN "NOT USEFUL NEWS"
# ============================================================

IGNORE_WORDS = [
    "help",
    "how do i",
    "how can i",
    "can someone",
    "anyone know",
    "question",
    "looking for",
    "where can i",
    "what is",
    "what's the best",
    "which one",
    "tutorial",
    "guide",
    "need help",
]


# ============================================================
# WORDS THAT SUGGEST ACTUAL DEVELOPMENT / NEWS
# ============================================================

IMPORTANT_WORDS = [
    "release",
    "released",
    "update",
    "updated",
    "beta",
    "alpha",
    "exploit",
    "vulnerability",
    "jailbreak",
    "kernel",
    "rootless",
    "tweak",
    "tool",
    "developer",
    "development",
    "research",
    "researcher",
    "support",
    "port",
    "implementation",
    "commit",
    "build",
    "patch",
    "fix",
    "ios",
    "iphone",
    "ipad",
    "ps4",
    "homebrew",
    "goldhen",
    "payload",
    "emulator",
    "emulation",
    "qemu",
    "utm",
    "windows",
]


# ============================================================
# LOAD WHAT WE HAVE ALREADY SEEN
# ============================================================

def load_state():
    if not os.path.exists(STATE_FILE):
        return {
            "github": {},
            "news": []
        }

    try:
        with open(STATE_FILE, "r") as file:
            return json.load(file)

    except Exception:
        return {
            "github": {},
            "news": []
        }


# ============================================================
# SAVE STATE
# ============================================================

def save_state(state):
    with open(STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)


# ============================================================
# GITHUB RELEASE TRACKER
# ============================================================

def check_github(state):

    print("\n")
    print("=" * 60)
    print("GITHUB PROJECT UPDATES")
    print("=" * 60)

    for name, repo in GITHUB_PROJECTS.items():

        url = f"https://api.github.com/repos/{repo}/releases/latest"

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=10
            )

            if response.status_code == 404:
                print(f"\n{name}: No release found.")
                continue

            if response.status_code != 200:
                print(
                    f"\n{name}: GitHub error "
                    f"{response.status_code}"
                )
                continue

            release = response.json()

            version = release.get("tag_name", "Unknown")
            title = release.get("name") or version
            link = release.get("html_url")

            previous = state["github"].get(name)

            print(f"\n{name}")
            print("-" * 40)

            if previous == version:

                print(f"✓ No new release")
                print(f"  Current: {version}")

            else:

                print("🔥 NEW RELEASE")
                print(f"  {title}")
                print(f"  Version: {version}")
                print(f"  Link: {link}")

                state["github"][name] = version

        except requests.RequestException as error:

            print(f"\n{name}: Network error")
            print(f"  {error}")


# ============================================================
# CHECK WHETHER A NEWS TITLE IS USEFUL
# ============================================================

def useful_news(title):

    text = title.lower()

    # Remove obvious questions/help posts
    for word in IGNORE_WORDS:

        if word in text:
            return False

    # Require at least one relevant development keyword
    for word in IMPORTANT_WORDS:

        if word in text:
            return True

    return False


# ============================================================
# RSS NEWS
# ============================================================

def check_rss(state):

    print("\n")
    print("=" * 60)
    print("NEWS / DEVELOPMENT")
    print("=" * 60)

    new_news = []

    for category, feeds in RSS_SOURCES.items():

        print(f"\n[{category}]")
        print("-" * 40)

        for url in feeds:

            try:

                response = requests.get(
                    url,
                    headers=HEADERS,
                    timeout=10
                )

                if response.status_code != 200:
                    continue

                root = ET.fromstring(response.text)

                # RSS feeds
                items = root.findall(".//item")

                for item in items[:10]:

                    title_element = item.find("title")
                    link_element = item.find("link")

                    if title_element is None:
                        continue

                    title = title_element.text or ""

                    link = ""

                    if link_element is not None:
                        link = link_element.text or ""

                    if not useful_news(title):
                        continue

                    news_id = title + link

                    if news_id in state["news"]:
                        continue

                    new_news.append(news_id)

                    print(f"\n🔥 {title}")

                    if link:
                        print(f"   {link}")

            except (
                requests.RequestException,
                ET.ParseError
            ):
                continue

    # Remember news we've already shown
    state["news"].extend(new_news)

    # Keep state file from growing forever
    state["news"] = state["news"][-500:]


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("              TECH RADAR")
    print("=" * 60)

    state = load_state()

    check_github(state)

    check_rss(state)

    save_state(state)

    print("\n")
    print("=" * 60)
    print("Scan complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
