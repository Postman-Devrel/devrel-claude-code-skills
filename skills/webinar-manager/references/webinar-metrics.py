#!/usr/bin/env python3
"""Metrics helper for webinar-manager: YouTube public stats and Slack posting.

Usage:
  webinar-metrics.py youtube <video_id_or_url>
  webinar-metrics.py slack-post <message.txt> [--channel #developer-relations] [--thread-ts TS] [--apply]

Env: SLACK_BOT_TOKEN (chat:write). YOUTUBE_API_KEY (Data API v3) is optional: without it,
`youtube` reads the public watch page, which gives views and likes but no comment count.
slack-post prints the message and writes nothing unless --apply is passed.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_CHANNEL = "#developer-relations"


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
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
