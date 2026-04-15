#!/usr/bin/env python3
"""Scrape ~200 blog header images from blog.postman.com and categorize into folders."""

import os
import re
import time
import json
from urllib.parse import urlparse, urljoin
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://blog.postman.com"
OUTPUT_DIR = Path(__file__).parent / "images"
MANIFEST_FILE = Path(__file__).parent / "manifest.json"
TARGET_COUNT = 200
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# Category keywords mapping - first match wins
CATEGORIES = {
    "ai-and-agents": ["ai", "agent", "llm", "gpt", "claude", "copilot", "machine learning", "genai", "generative", "artificial intelligence", "model context protocol", "mcp"],
    "api-design": ["api design", "api-first", "schema", "openapi", "swagger", "graphql", "grpc", "protobuf", "specification", "api style", "api governance"],
    "api-testing": ["test", "qa", "automat", "newman", "collection runner", "monitor", "assertion", "mock", "postbot"],
    "api-security": ["security", "auth", "oauth", "jwt", "token", "encrypt", "vulnerab", "penetration", "ssl", "tls", "certificate", "secret"],
    "tutorials-and-guides": ["tutorial", "how to", "how-to", "guide", "step-by-step", "walkthrough", "getting started", "beginner", "learn", "intro to", "introduction to"],
    "product-updates": ["new feature", "release", "update", "launch", "announce", "changelog", "what's new", "introducing", "now available", "v10", "v11"],
    "developer-experience": ["developer experience", "dx ", "workflow", "productivity", "collaboration", "workspace", "team", "onboard"],
    "integrations": ["integrat", "github", "jenkins", "ci/cd", "cicd", "pipeline", "aws", "azure", "gcp", "slack", "webhook", "connect"],
    "community": ["community", "event", "conference", "hackathon", "contributor", "open source", "recap", "galaxy", "post/con", "postcon"],
    "industry-and-trends": ["trend", "state of", "survey", "report", "industry", "future of", "landscape", "ecosystem"],
}


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80].rstrip('-')


def categorize(title: str) -> str:
    lower = title.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in lower:
                return category
    return "general"


def get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def extract_posts_from_homepage() -> list:
    posts = []
    soup = get_soup(BASE_URL)
    hero_link = soup.select_one("section.home_hero_container a.home_hero_title")
    if hero_link:
        posts.append({
            "url": urljoin(BASE_URL, hero_link["href"]),
            "title": hero_link.get_text(strip=True),
        })
    cards = soup.select('h2.h3 > a[id="homepage-card-header"]')
    for card in cards:
        posts.append({
            "url": urljoin(BASE_URL, card["href"]),
            "title": card.get_text(strip=True),
        })
    return posts


def extract_posts_from_postspage(page_num: int) -> list:
    posts = []
    if page_num == 1:
        url = f"{BASE_URL}/postspage/"
    else:
        url = f"{BASE_URL}/postspage/page/{page_num}/"
    try:
        soup = get_soup(url)
    except requests.HTTPError:
        return []
    cards = soup.select('h2.h3 > a[id="homepage-card-header"]')
    for card in cards:
        posts.append({
            "url": urljoin(BASE_URL, card["href"]),
            "title": card.get_text(strip=True),
        })
    return posts


def get_header_image_url(post_url: str) -> str | None:
    try:
        soup = get_soup(post_url)
        og = soup.select_one('meta[property="og:image"]')
        if og and og.get("content"):
            return og["content"]
    except Exception as e:
        print(f"  Error fetching {post_url}: {e}")
    return None


def download_image(img_url: str, filepath: Path) -> bool:
    try:
        resp = requests.get(img_url, headers=HEADERS, timeout=30, stream=True)
        resp.raise_for_status()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  Download error: {e}")
        return False


def get_extension(url: str) -> str:
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    return ext if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg") else ".jpg"


def main():
    print("=== Postman Blog Header Image Scraper ===\n")

    # Step 1: Collect post URLs and titles
    print("Collecting blog post listings...")
    all_posts = []
    seen_urls = set()

    homepage_posts = extract_posts_from_homepage()
    for p in homepage_posts:
        if p["url"] not in seen_urls:
            seen_urls.add(p["url"])
            all_posts.append(p)
    print(f"  Homepage: {len(homepage_posts)} posts")

    page = 1
    while len(all_posts) < TARGET_COUNT:
        posts = extract_posts_from_postspage(page)
        if not posts:
            print(f"  No more posts at postspage page {page}, stopping.")
            break
        new = 0
        for p in posts:
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                all_posts.append(p)
                new += 1
        print(f"  Postspage page {page}: {len(posts)} posts ({new} new)")
        page += 1
        time.sleep(0.5)

    all_posts = all_posts[:TARGET_COUNT]
    print(f"\nCollected {len(all_posts)} posts total.\n")

    # Step 2: Download header images and categorize
    print("Downloading header images...\n")
    manifest = []
    downloaded = 0
    skipped = 0

    for i, post in enumerate(all_posts, 1):
        title = post["title"]
        category = categorize(title)
        slug = slugify(title)

        print(f"[{i}/{len(all_posts)}] {title[:70]}...")
        print(f"  Category: {category}")

        img_url = get_header_image_url(post["url"])
        if not img_url:
            print("  No header image found, skipping.")
            skipped += 1
            continue

        ext = get_extension(img_url)
        filename = f"{slug}{ext}"
        filepath = OUTPUT_DIR / category / filename

        if filepath.exists():
            print("  Already downloaded.")
            downloaded += 1
        else:
            if download_image(img_url, filepath):
                print(f"  Saved: {filepath.relative_to(OUTPUT_DIR)}")
                downloaded += 1
            else:
                skipped += 1
                continue

        manifest.append({
            "title": title,
            "category": category,
            "filename": filename,
            "image_url": img_url,
            "post_url": post["url"],
            "path": str(filepath.relative_to(OUTPUT_DIR)),
        })

        time.sleep(0.3)

    # Save manifest
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n=== Done ===")
    print(f"Downloaded: {downloaded}")
    print(f"Skipped:    {skipped}")
    print(f"Manifest:   {MANIFEST_FILE}")

    cat_counts = {}
    for entry in manifest:
        cat_counts[entry["category"]] = cat_counts.get(entry["category"], 0) + 1
    print(f"\nCategories:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
