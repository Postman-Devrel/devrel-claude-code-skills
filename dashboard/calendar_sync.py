"""Sync editorial calendar from WordPress on dashboard startup.

Runs the same WP API reads that blog-wordpress-scheduler uses,
writing results to wp-calendar.json for the dashboard to display.
Credentials are read from ~/.claude/settings.json (same source agents use).
"""

import base64
import html
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
PST = timezone(timedelta(hours=-8))
CALENDAR_FILE = os.path.join(os.path.dirname(__file__), "wp-calendar.json")


def _load_credentials():
    """Load WP credentials from ~/.claude/settings.json."""
    settings_path = Path.home() / ".claude" / "settings.json"
    if not settings_path.exists():
        return None, None
    try:
        with open(settings_path, "r") as f:
            env = json.load(f).get("env", {})
        return env.get("WP_USERNAME"), env.get("WP_APP_PASSWORD")
    except (json.JSONDecodeError, KeyError):
        return None, None


def _wp_get(path, auth):
    req = urllib.request.Request(
        f"{WP_BASE}/{path}",
        headers={
            "Authorization": f"Basic {auth}",
            "User-Agent": "PostmanDevRelDashboard/1.0",
        },
    )
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def _normalize(post):
    # Extract featured image URL from embedded data
    featured_image = None
    embedded = post.get("_embedded", {})
    media = embedded.get("wp:featuredmedia", [])
    if media and isinstance(media, list) and len(media) > 0:
        src = media[0].get("source_url")
        if src:
            featured_image = src

    return {
        "id": post["id"],
        "title": html.unescape(post["title"]["rendered"]),
        "date": post.get("date", ""),
        "status": post["status"],
        "link": post.get("link", ""),
        "edit_link": f"https://blog.postman.com/wp-admin/post.php?post={post['id']}&action=edit",
        "featured_image": featured_image,
    }


def sync_calendar():
    """Fetch scheduled + published posts from WP and write wp-calendar.json."""
    username, app_password = _load_credentials()
    if not username or not app_password:
        print("Calendar sync: WP credentials not found in ~/.claude/settings.json")
        return False

    auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
    now = datetime.now(PST)

    try:
        # Drafts — posts waiting for review (created after 2026-03-31)
        # _embed gives us featured image URLs inline
        drafts = _wp_get(
            f"posts?status=draft&after=2026-03-31T00:00:00&per_page=50&orderby=modified&order=desc&_embed=wp:featuredmedia", auth
        )

        # Scheduled (next 8 weeks) — same query as blog-wordpress-scheduler
        after = now.strftime("%Y-%m-%dT00:00:00")
        until = (now + timedelta(weeks=8)).strftime("%Y-%m-%dT23:59:59")
        scheduled = _wp_get(
            f"posts?status=future&after={after}&before={until}"
            f"&per_page=100&orderby=date&order=asc", auth
        )

        # Published (last 6 months)
        six_months_ago = (now - timedelta(days=180)).strftime("%Y-%m-%dT00:00:00")
        published = _wp_get(
            f"posts?status=publish&after={six_months_ago}"
            f"&per_page=100&orderby=date&order=desc", auth
        )

        calendar_data = {
            "updated_at": now.isoformat(),
            "drafts": [_normalize(p) for p in drafts],
            "scheduled": [_normalize(p) for p in scheduled],
            "published": [_normalize(p) for p in published],
        }

        with open(CALENDAR_FILE, "w") as f:
            json.dump(calendar_data, f, indent=2)

        print(f"Calendar synced: {len(drafts)} drafts, {len(scheduled)} scheduled, {len(published)} published")
        return True

    except Exception as e:
        print(f"Calendar sync failed: {e}")
        return False
