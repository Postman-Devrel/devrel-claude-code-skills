"""Sync editorial calendar from WordPress on dashboard startup.

Runs the same WP API reads that blog-wordpress-scheduler uses,
writing results to wp-calendar.json for the dashboard to display.
Credentials are read from ~/.claude/settings.json (same source agents use).

Cloudflare blocks direct API requests from this machine. To bypass it:
  1. Visit https://blog.postman.com/wp-admin in your browser
  2. Open DevTools → Application → Cookies → blog.postman.com
  3. Copy the value of the 'cf_clearance' cookie
  4. Add it to ~/.claude/settings.json under "env":
       "CF_CLEARANCE": "your-cf_clearance-value-here"
  5. Restart the dashboard — syncs will work until the cookie expires (~24h)
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
    """Load WP credentials and optional cf_clearance from ~/.claude/settings.json."""
    settings_path = Path.home() / ".claude" / "settings.json"
    if not settings_path.exists():
        return None, None, None
    try:
        with open(settings_path, "r") as f:
            env = json.load(f).get("env", {})
        return env.get("WP_USERNAME"), env.get("WP_APP_PASSWORD"), env.get("CF_CLEARANCE")
    except (json.JSONDecodeError, KeyError):
        return None, None, None


def _extract_arc_cf_clearance():
    """Extract cf_clearance from Arc browser on macOS using Arc Safe Storage keychain key."""
    import sys
    if sys.platform != "darwin":
        return None

    import glob
    import hashlib
    import shutil
    import sqlite3
    import subprocess
    import tempfile
    from pathlib import Path

    arc_base = Path.home() / "Library" / "Application Support" / "Arc" / "User Data"
    if not arc_base.exists():
        return None

    # Get Arc's encryption key from the macOS keychain
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "Arc Safe Storage", "-a", "Arc", "-w"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return None
        keychain_password = result.stdout.strip()
    except Exception:
        return None

    # Derive AES-128 key via PBKDF2-SHA1 (Chromium standard)
    try:
        key = hashlib.pbkdf2_hmac("sha1", keychain_password.encode("utf-8"), b"saltysalt", 1003, dklen=16)
    except Exception:
        return None

    # Search all Arc profiles
    profile_dirs = list(arc_base.glob("Default")) + list(arc_base.glob("Profile *"))
    for profile_dir in sorted(profile_dirs):
        cookie_db = profile_dir / "Cookies"
        if not cookie_db.exists():
            continue

        # Copy DB to temp file — original may be locked by Arc
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
                tmp_path = tmp.name
            shutil.copy2(str(cookie_db), tmp_path)
            conn = sqlite3.connect(tmp_path)
            rows = conn.execute(
                "SELECT name, encrypted_value FROM cookies WHERE host_key LIKE '%postman.com%'"
            ).fetchall()
            conn.close()
        except Exception:
            continue
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        for name, encrypted in rows:
            if name != "cf_clearance" or not encrypted:
                continue
            # Chromium v10 format: b"v10" + ciphertext, IV = 16 space bytes
            if encrypted[:3] == b"v10":
                try:
                    from Crypto.Cipher import AES
                    cipher = AES.new(key, AES.MODE_CBC, IV=b" " * 16)
                    decrypted = cipher.decrypt(encrypted[3:])
                    pad_len = decrypted[-1]
                    return decrypted[:-pad_len].decode("utf-8", errors="ignore")
                except Exception:
                    continue

    return None


def _auto_extract_cf_clearance():
    """Try to pull cf_clearance from the local browser cookie store."""
    # Try Arc first (most likely browser on this machine)
    arc_val = _extract_arc_cf_clearance()
    if arc_val:
        print("Calendar sync: using cf_clearance from Arc browser")
        return arc_val

    # Fall back to browser_cookie3 for standard browsers
    try:
        import browser_cookie3
    except ImportError:
        return None

    # Chrome: search all profiles (Default, Profile 1, Profile 2, ...)
    import sys
    if sys.platform == "darwin":
        from pathlib import Path
        chrome_base = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
        profile_dirs = [chrome_base / "Default"] + sorted(chrome_base.glob("Profile *"))
        for profile_dir in profile_dirs:
            cookie_file = profile_dir / "Cookies"
            if not cookie_file.exists():
                continue
            try:
                jar = browser_cookie3.chrome(cookie_file=str(cookie_file), domain_name=".blog.postman.com")
                for cookie in jar:
                    if cookie.name == "cf_clearance":
                        return cookie.value
            except Exception:
                continue

    # Firefox and Safari (single profile is fine)
    for loader in [browser_cookie3.firefox, browser_cookie3.safari]:
        try:
            jar = loader(domain_name=".blog.postman.com")
            for cookie in jar:
                if cookie.name == "cf_clearance":
                    return cookie.value
        except Exception:
            continue
    return None


def _wp_get(path, auth, cf_clearance=None):
    headers = {
        "Authorization": f"Basic {auth}",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    if cf_clearance:
        headers["Cookie"] = f"cf_clearance={cf_clearance}"
    req = urllib.request.Request(f"{WP_BASE}/{path}", headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def _normalize(post):
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


def has_cf_clearance():
    """Return True if a cf_clearance cookie is available (settings or browser)."""
    _, _, cf = _load_credentials()
    return bool(cf) or bool(_auto_extract_cf_clearance())


def sync_calendar():
    """Fetch scheduled + published posts from WP and write wp-calendar.json."""
    username, app_password, cf_clearance = _load_credentials()
    if not username or not app_password:
        print("Calendar sync: WP credentials not found in ~/.claude/settings.json")
        return False

    # Try browser auto-extract if not in settings
    if not cf_clearance:
        cf_clearance = _auto_extract_cf_clearance()
        if cf_clearance:
            print("Calendar sync: using cf_clearance from browser cookie store")

    if not cf_clearance:
        print("Calendar sync: cf_clearance not found in settings or browser.")
        print("  Visit blog.postman.com/wp-admin in your browser, then restart the dashboard.")
        return "cf_clearance_missing"

    auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
    now = datetime.now(PST)

    try:
        drafts = _wp_get(
            f"posts?status=draft&after=2026-03-31T00:00:00&per_page=50&orderby=modified&order=desc&_embed=wp:featuredmedia",
            auth, cf_clearance
        )

        after = now.strftime("%Y-%m-%dT00:00:00")
        until = (now + timedelta(weeks=8)).strftime("%Y-%m-%dT23:59:59")
        scheduled = _wp_get(
            f"posts?status=future&after={after}&before={until}&per_page=100&orderby=date&order=asc",
            auth, cf_clearance
        )

        six_months_ago = (now - timedelta(days=180)).strftime("%Y-%m-%dT00:00:00")
        published = _wp_get(
            f"posts?status=publish&after={six_months_ago}&per_page=100&orderby=date&order=desc",
            auth, cf_clearance
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

    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("Calendar sync: 403 — cf_clearance cookie may be expired. Refresh it from your browser.")
            return "cf_clearance_expired"
        print(f"Calendar sync failed: {e}")
        return str(e)
    except Exception as e:
        print(f"Calendar sync failed: {e}")
        return str(e)
