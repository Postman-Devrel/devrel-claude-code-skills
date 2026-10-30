#!/usr/bin/env python3
"""Metrics helper for webinar-manager: YouTube public stats and Slack posting.

Usage:
  webinar-metrics.py youtube <video_id_or_url>
  webinar-metrics.py slack-post <message.txt> [--channel #developer-relations] [--thread-ts TS] [--apply]
  webinar-metrics.py history-add <history.csv> <row.json>   # upsert one webinar by slug
  webinar-metrics.py history-show <history.csv>             # trend table with change vs previous

Env: SLACK_BOT_TOKEN (chat:write). YOUTUBE_API_KEY (Data API v3) is optional: without it,
`youtube` reads the public watch page, which gives views and likes but no comment count.
slack-post prints the message and writes nothing unless --apply is passed.
"""

import csv
import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_CHANNEL = "#developer-relations"

HISTORY_COLUMNS = [
    "slug", "title", "date",
    "luma_registered", "luma_waitlisted", "luma_checked_in", "linkedin_registrations",
    "yt_views", "yt_avg_view_seconds", "yt_watch_hours", "yt_engaged_views", "yt_likes", "yt_chat_messages",
    "li_viewers", "li_avg_watch_seconds", "li_engagement_pct", "li_comments",
    "updated",
]
TREND_COLUMNS = [
    ("luma_registered", "Luma reg"), ("linkedin_registrations", "LI reg"),
    ("yt_views", "YT views"), ("yt_avg_view_seconds", "YT avg view"),
    ("li_viewers", "LI viewers"), ("li_avg_watch_seconds", "LI avg watch"),
    ("li_engagement_pct", "LI eng %"),
]


def video_id(value):
    m = re.search(r"(?:v=|youtu\.be/|/live/|/video/)([A-Za-z0-9_-]{11})", value)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    sys.exit(f"Could not read a YouTube video id from: {value}")


def first_int(pattern, text):
    m = re.search(pattern, text)
    return int(m.group(1)) if m else None


def cmd_youtube_public(vid):
    req = urllib.request.Request(
        f"https://www.youtube.com/watch?v={vid}",
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
            "Accept-Language": "en-US",
        },
    )
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf8", "ignore")
    title = re.search(r'<meta name="title" content="([^"]*)"', html)
    views = first_int(r'"viewCount":"(\d+)"', html)
    if views is None:
        sys.exit(f"Could not read views for {vid} from the public page (private, removed, or page layout changed)")
    print(json.dumps({
        "video_id": vid,
        "source": "public-page",
        "title": title.group(1) if title else None,
        "views": views,
        "likes": first_int(r'"likeCount":"?(\d+)', html),
        "comments": None,
    }, indent=2))


def cmd_youtube(value):
    vid = video_id(value)
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        return cmd_youtube_public(vid)
    params = urllib.parse.urlencode(
        {"part": "statistics,snippet,liveStreamingDetails", "id": vid, "key": key}
    )
    try:
        raw = urllib.request.urlopen(
            f"https://www.googleapis.com/youtube/v3/videos?{params}", timeout=30
        ).read()
    except urllib.error.HTTPError as e:
        sys.exit(f"YouTube API error {e.code}: {e.read().decode()[:300]}")
    items = json.loads(raw).get("items", [])
    if not items:
        sys.exit(f"No video found for id {vid} (private, deleted, or wrong id)")
    item = items[0]
    stats = item.get("statistics", {})
    live = item.get("liveStreamingDetails", {})
    print(json.dumps({
        "video_id": vid,
        "source": "data-api",
        "title": item["snippet"]["title"],
        "views": int(stats["viewCount"]) if "viewCount" in stats else None,
        "likes": int(stats["likeCount"]) if "likeCount" in stats else None,
        "comments": int(stats["commentCount"]) if "commentCount" in stats else None,
        "actual_start": live.get("actualStartTime"),
        "actual_end": live.get("actualEndTime"),
    }, indent=2))


def cmd_slack_post(path, channel, thread_ts, apply):
    text = open(path).read().strip()
    if not text:
        sys.exit("Message file is empty")
    if not apply:
        print(f"Dry run. Would post to {channel}" + (f" (thread {thread_ts})" if thread_ts else "") + ":\n")
        print(text)
        print("\nRe-run with --apply to post.")
        return
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        sys.exit("SLACK_BOT_TOKEN is not set")
    body = {"channel": channel, "text": text, "unfurl_links": False}
    if thread_ts:
        body["thread_ts"] = thread_ts
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if not resp.get("ok"):
        sys.exit(f"Slack post failed: {resp.get('error')}")
    print(json.dumps({"channel": resp["channel"], "ts": resp["ts"]}))


def read_history(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def cmd_history_add(path, row_path):
    row = json.load(open(row_path))
    unknown = set(row) - set(HISTORY_COLUMNS)
    if unknown or not row.get("slug") or not row.get("date"):
        sys.exit(f"Row needs slug and date, and only known columns. Unknown: {sorted(unknown)}")
    rows = read_history(path)
    existing = next((r for r in rows if r["slug"] == row["slug"]), None)
    is_new = existing is None
    if is_new:
        existing = {c: "" for c in HISTORY_COLUMNS}
        rows.append(existing)
    # Only overwrite a stored value with a real one, so a rerun that fills pending
    # numbers never blanks what an earlier run captured.
    for k, v in row.items():
        if v not in (None, ""):
            existing[k] = str(v)
    existing["updated"] = datetime.date.today().isoformat()
    rows.sort(key=lambda r: r["date"])
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HISTORY_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{'Added' if is_new else 'Updated'} {row['slug']} in {path} ({len(rows)} webinars)")


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fmt(col, v):
    n = num(v)
    if n is None:
        return "-"
    if col.endswith("_seconds"):
        return f"{int(n // 60)}:{int(n % 60):02d}"
    return f"{n:g}"


def cmd_history_show(path):
    rows = read_history(path)
    if not rows:
        sys.exit("No history yet. Run metrics for a finished webinar first.")
    cols = [("date", "Date")] + TREND_COLUMNS
    table = [[h for _, h in cols]]
    for r in rows:
        table.append([r["date"]] + [fmt(c, r[c]) for c, _ in TREND_COLUMNS])
    widths = [max(len(t[i]) for t in table) for i in range(len(cols))]
    for t in table:
        print("  ".join(v.ljust(widths[i]) for i, v in enumerate(t)))
    if len(rows) < 2:
        print("\nOnly one webinar so far. Trends start with the second.")
        return
    last, prev = rows[-1], rows[:-1]
    print(f"\nLatest ({last['date']}) vs previous webinar, and vs the average of {len(prev)} earlier:")
    for c, h in TREND_COLUMNS:
        cur, before = num(last[c]), num(prev[-1][c])
        avg_vals = [num(r[c]) for r in prev if num(r[c]) is not None]
        if cur is None:
            print(f"  {h}: not captured")
            continue
        parts = []
        if before:
            parts.append(f"{(cur - before) / before * 100:+.0f}% vs previous")
        if avg_vals and sum(avg_vals):
            avg = sum(avg_vals) / len(avg_vals)
            parts.append(f"{(cur - avg) / avg * 100:+.0f}% vs average")
        print(f"  {h}: {fmt(c, cur)}" + (f" ({', '.join(parts)})" if parts else " (no earlier value to compare)"))


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    cmd = argv[1]
    if cmd == "youtube":
        cmd_youtube(argv[2])
    elif cmd == "slack-post":
        rest = argv[3:]
        channel, thread_ts = DEFAULT_CHANNEL, None
        if "--channel" in rest:
            channel = rest[rest.index("--channel") + 1]
        if "--thread-ts" in rest:
            thread_ts = rest[rest.index("--thread-ts") + 1]
        cmd_slack_post(argv[2], channel, thread_ts, "--apply" in rest)
    elif cmd == "history-add" and len(argv) >= 4:
        cmd_history_add(argv[2], argv[3])
    elif cmd == "history-show":
        cmd_history_show(argv[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
