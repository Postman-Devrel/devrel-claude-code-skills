#!/usr/bin/env python3
"""
One-time YouTube OAuth consent helper for qbr-metrics.

Runs the OAuth 2.0 loopback flow for a Desktop-app client, prints a refresh
token to the terminal, then verifies it against the YouTube Data API and the
YouTube Analytics API for the Postman channel.

The refresh token is printed to the terminal only. It is never written to a
file. Copy it into ~/.claude/settings.json under "env" yourself.

Env vars (read from the environment first, then from the "env" block of
~/.claude/settings.json and .claude/settings.json, so a plain terminal works):
  YT_OAUTH_CLIENT_ID       OAuth client ID (Desktop app type)
  YT_OAUTH_CLIENT_SECRET   OAuth client secret
  YT_CHANNEL_ID            optional; defaults to the Postman channel

Usage:
  python3 youtube-oauth-setup.py              # run consent, print token, verify
  python3 youtube-oauth-setup.py --no-browser # print the URL instead of opening it
  python3 youtube-oauth-setup.py --verify     # skip consent, verify the token
                                              # already in YT_OAUTH_REFRESH_TOKEN

Sign in with a Google account that has access to the Postman YouTube channel.
If the channel is a Brand Account, pick it in the account chooser.
"""
import json
import os
import secrets
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
DEFAULT_CHANNEL_ID = "UCocudCGVb3MmhWQ1aoIgUQw"
CONSENT_TIMEOUT_SECONDS = 300


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_settings_env():
    """Fill in missing env vars from Claude Code settings files.

    Claude Code only injects the settings.json "env" block into its own
    processes, so a script run from a plain terminal would not see them.
    Real environment variables win, then project settings over user settings,
    and local files over shared ones (highest precedence first below).
    """
    for path in (".claude/settings.local.json", ".claude/settings.json",
                 "~/.claude/settings.local.json", "~/.claude/settings.json"):
        try:
            with open(os.path.expanduser(path)) as f:
                env = json.load(f).get("env", {})
        except (OSError, ValueError):
            continue
        for key, value in env.items():
            if isinstance(value, str) and not os.environ.get(key):
                os.environ[key] = value


def post_form(url, fields):
    data = urllib.parse.urlencode(fields).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:400]
        die(f"token endpoint returned HTTP {e.code}: {detail}")


def get_json(url, access_token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
        return e.code, body


def run_consent(client_id, client_secret, open_browser):
    result = {}
    done = threading.Event()
    state = secrets.token_urlsafe(24)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" not in params and "error" not in params:
                self.send_response(404)
                self.end_headers()
                return
            if params.get("state", [""])[0] != state:
                result["error"] = "state mismatch (possible CSRF); aborting"
            elif "error" in params:
                result["error"] = params["error"][0]
            else:
                result["code"] = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            msg = "Consent failed. Return to the terminal." if "error" in result else \
                  "Consent received. You can close this tab and return to the terminal."
            self.wfile.write(f"<html><body style='font-family:sans-serif'><p>{msg}</p></body></html>".encode())
            done.set()

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    redirect_uri = f"http://127.0.0.1:{server.server_port}"
    threading.Thread(target=server.serve_forever, daemon=True).start()

    query = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    })
    url = f"{AUTH_URL}?{query}"

    print("Open this URL and approve access with a Google account that can see the Postman channel:\n")
    print(url + "\n")
    if open_browser:
        webbrowser.open(url)
    print(f"Waiting up to {CONSENT_TIMEOUT_SECONDS // 60} minutes for the redirect on {redirect_uri} ...")

    if not done.wait(CONSENT_TIMEOUT_SECONDS):
        server.shutdown()
        die("timed out waiting for consent")
    server.shutdown()
    if "error" in result:
        die(f"consent failed: {result['error']}")

    tokens = post_form(TOKEN_URL, {
        "code": result["code"],
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    })
    if "refresh_token" not in tokens:
        die("Google did not return a refresh_token. Revoke this app at "
            "https://myaccount.google.com/permissions and run again.")
    granted = set(tokens.get("scope", "").split())
    missing = [s for s in SCOPES if s not in granted]
    if missing:
        die(f"consent did not grant required scopes: {', '.join(missing)}")
    return tokens["refresh_token"]


def verify(client_id, client_secret, refresh_token, channel_id):
    print("\nVerifying ...")
    tokens = post_form(TOKEN_URL, {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    })
    at = tokens["access_token"]
    ok = True

    status, body = get_json("https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true", at)
    items = body.get("items", [])
    if status == 200 and items:
        print(f"  [ok]   token belongs to channel: {items[0]['snippet']['title']} ({items[0]['id']})")
        if items[0]["id"] != channel_id:
            print(f"  [warn] that is not {channel_id}. If this is a personal channel, re-run and pick "
                  "the Postman Brand Account in the account chooser.")
    elif status == 200:
        print("  [warn] token has no channel of its own (normal for a Brand Account manager); continuing.")
    else:
        ok = False
        print(f"  [fail] channels.list mine=true: HTTP {status} {body.get('error', {}).get('message', '')}")

    status, body = get_json(
        f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}", at)
    if status == 200 and body.get("items"):
        subs = body["items"][0]["statistics"].get("subscriberCount", "hidden")
        print(f"  [ok]   Data API: subscriberCount = {subs}")
    else:
        ok = False
        msg = body.get("error", {}).get("message", "")
        print(f"  [fail] Data API: HTTP {status} {msg[:160]}")
        if "not been used" in msg or "disabled" in msg:
            print("         Enable 'YouTube Data API v3' in the Google Cloud project that owns this OAuth client.")

    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=6)
    q = urllib.parse.urlencode({
        "ids": f"channel=={channel_id}",
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "metrics": "views,estimatedMinutesWatched,subscribersGained",
    })
    status, body = get_json(f"https://youtubeanalytics.googleapis.com/v2/reports?{q}", at)
    if status == 200 and body.get("rows"):
        v, m, s = body["rows"][0]
        print(f"  [ok]   Analytics API ({start} to {end}): views={v} watch_minutes={m} subs_gained={s}")
    elif status == 200:
        print(f"  [ok]   Analytics API reachable ({start} to {end}) but returned no rows.")
    else:
        ok = False
        msg = body.get("error", {}).get("message", "")
        print(f"  [fail] Analytics API: HTTP {status} {msg[:160]}")
        if status == 403:
            print("         The signed-in account likely lacks access to this channel, or the "
                  "'YouTube Analytics API' is not enabled in the project.")
    return ok


def main():
    load_settings_env()
    client_id =os.environ.get("YT_OAUTH_CLIENT_ID", "")
    client_secret = os.environ.get("YT_OAUTH_CLIENT_SECRET", "")
    channel_id = os.environ.get("YT_CHANNEL_ID", DEFAULT_CHANNEL_ID)
    if not client_id or not client_secret:
        die("set YT_OAUTH_CLIENT_ID and YT_OAUTH_CLIENT_SECRET in ~/.claude/settings.json under \"env\" first.")

    if "--verify" in sys.argv:
        refresh_token = os.environ.get("YT_OAUTH_REFRESH_TOKEN", "")
        if not refresh_token:
            die("YT_OAUTH_REFRESH_TOKEN is not set.")
    else:
        refresh_token = run_consent(client_id, client_secret, "--no-browser" not in sys.argv)
        print("\nConsent granted. Add this to ~/.claude/settings.json under \"env\":\n")
        print(f'  "YT_OAUTH_REFRESH_TOKEN": "{refresh_token}"')
        print("\nTreat it like a password. Do not commit it or paste it into chat.")

    sys.exit(0 if verify(client_id, client_secret, refresh_token, channel_id) else 2)


if __name__ == "__main__":
    main()
