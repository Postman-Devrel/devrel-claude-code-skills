#!/usr/bin/env python3
"""Metrics helper for webinar-manager: YouTube public stats and Slack posting.

Usage:
  webinar-metrics.py youtube <video_id_or_url>
  webinar-metrics.py youtube-analytics <video_id_or_url> <start YYYY-MM-DD> [end]   # owner Analytics via the QBR OAuth token
  webinar-metrics.py slack-post <message.txt> [--channel #developer-relations] [--thread-ts TS] [--apply]
  webinar-metrics.py history-add <history.csv> <row.json>   # upsert one webinar by slug
  webinar-metrics.py history-show <history.csv>             # trend table with change vs previous
  webinar-metrics.py chart <history.csv> [out.html]         # self-contained HTML chart, one panel per metric

Env: YT_OAUTH_CLIENT_ID, YT_OAUTH_CLIENT_SECRET, YT_OAUTH_REFRESH_TOKEN (same as qbr-metrics) for youtube-analytics. SLACK_BOT_TOKEN (chat:write). YOUTUBE_API_KEY (Data API v3) is optional: without it,
`youtube` reads the public watch page, which gives views and likes but no comment count.
slack-post prints the message and writes nothing unless --apply is passed.
history-add also rewrites metrics-chart.html next to the CSV, so every metrics run refreshes the chart.
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
    "li_post_impressions", "li_post_reactions", "li_post_comments",
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


def cmd_youtube_analytics(value, start, end=None):
    """Channel-owner numbers (engaged views, watch time, average view duration) from the YouTube Analytics API.
    Live chat message counts are not exposed by any API after the stream ends, so they stay Studio-only."""
    for k in ("YT_OAUTH_CLIENT_ID", "YT_OAUTH_CLIENT_SECRET", "YT_OAUTH_REFRESH_TOKEN"):
        if not os.environ.get(k):
            sys.exit(f"{k} is not set (same credentials as qbr-metrics; see skills/qbr-metrics/references/youtube-oauth-setup.py)")
    vid = video_id(value)
    tok = _post_form("https://oauth2.googleapis.com/token", {
        "client_id": os.environ["YT_OAUTH_CLIENT_ID"], "client_secret": os.environ["YT_OAUTH_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_OAUTH_REFRESH_TOKEN"], "grant_type": "refresh_token"})
    h = {"Authorization": "Bearer " + tok["access_token"]}
    channel = os.environ.get("YT_CHANNEL_ID", "UCocudCGVb3MmhWQ1aoIgUQw")
    metrics = ["views", "engagedViews", "estimatedMinutesWatched", "averageViewDuration", "likes", "comments", "shares", "subscribersGained"]
    qs = urllib.parse.urlencode({"ids": f"channel=={channel}", "startDate": start,
                                 "endDate": end or datetime.date.today().isoformat(),
                                 "metrics": ",".join(metrics), "filters": f"video=={vid}"})
    req = urllib.request.Request("https://youtubeanalytics.googleapis.com/v2/reports?" + qs, headers=h)
    try:
        rows = json.load(urllib.request.urlopen(req, timeout=30)).get("rows") or []
    except urllib.error.HTTPError as e:
        sys.exit(f"YouTube Analytics failed: HTTP {e.code} {e.read()[:200]!r}")
    if not rows:
        sys.exit("No Analytics rows for that video and date range.")
    out = dict(zip(metrics, rows[0]))
    out.update(video_id=vid, watch_hours=round(out["estimatedMinutesWatched"] / 60, 1))
    print(json.dumps(out, indent=2))


def _post_form(url, fields):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode())
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        sys.exit(f"Token refresh failed: HTTP {e.code} {e.read()[:200]!r}")


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
        return [{c: r.get(c) or "" for c in HISTORY_COLUMNS} for r in csv.DictReader(f)]


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
    cmd_chart(path)


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


# Categorical series colors (light, dark), fixed order, one per webinar (latest 8 shown).
SERIES = [("#2a78d6", "#3987e5"), ("#eb6834", "#d95926"), ("#1baf7a", "#199e70"), ("#eda100", "#c98500"),
          ("#e87ba4", "#d55181"), ("#008300", "#008300"), ("#4a3aa7", "#9085e9"), ("#e34948", "#e66767")]
CHART_COLUMNS = TREND_COLUMNS + [("yt_watch_hours", "YT watch hours"), ("yt_likes", "YT likes"),
                                 ("li_post_impressions", "LI post impressions"), ("li_post_reactions", "LI post reactions"),
                                 ("li_post_comments", "LI post comments")]

CHART_CSS = """
:root{--bg:#f7f7f5;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--grid:#e6e5e0;%(light)s}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#121211;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--grid:#2d2d2b;%(dark)s;color-scheme:dark}}
:root[data-theme=dark]{--bg:#121211;--surface:#1a1a19;--ink:#fff;--ink2:#c3c2b7;--grid:#2d2d2b;%(dark)s;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;padding:28px 16px}
.wrap{max-width:900px;margin:0 auto}h1{font-size:1.4rem;margin:0}.sub{color:var(--ink2);margin:4px 0 16px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;color:var(--ink2);font-size:.85rem;margin-bottom:16px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.card{background:var(--surface);border:1px solid var(--grid);border-radius:8px;padding:14px;min-width:0}
h2{font-size:.95rem;margin:0 0 10px}.row{display:grid;grid-template-columns:54px 1fr auto;gap:8px;align-items:center;margin:6px 0}
.row span{color:var(--ink2);font-size:.8rem}.track{height:14px}.bar{height:14px;border-radius:0 4px 4px 0}
.val{font-variant-numeric:tabular-nums;font-weight:600;font-size:.85rem}.na{color:var(--ink2);font-weight:400}
.note{color:var(--ink2);font-size:.85rem;margin-top:16px}
"""


def cmd_chart(path, out=None):
    rows = read_history(path)
    if not rows:
        sys.exit("No history yet. Run metrics for a finished webinar first.")
    rows = rows[-len(SERIES):]
    out = out or os.path.join(os.path.dirname(os.path.abspath(path)), "metrics-chart.html")
    esc = lambda t: (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    light = ";".join(f"--s{i}:{c[0]}" for i, c in enumerate(SERIES))
    dark = ";".join(f"--s{i}:{c[1]}" for i, c in enumerate(SERIES))
    legend = "".join(f'<span><i style="background:var(--s{i})"></i>{esc(r["date"])} {esc(r["title"])}</span>'
                     for i, r in enumerate(rows))
    cards, missing = [], []
    for col, head in CHART_COLUMNS:
        vals = [num(r[col]) for r in rows]
        top = max((v for v in vals if v is not None), default=None)
        if top is None:
            missing.append(head)
            continue
        body = ""
        for i, (r, v) in enumerate(zip(rows, vals)):
            label = esc(r["date"][5:])
            if v is None:
                body += f'<div class="row"><span>{label}</span><div></div><b class="val na">not captured</b></div>'
            else:
                w = max(v / top * 100, 1) if top else 1
                body += (f'<div class="row" title="{esc(r["title"])}: {fmt(col, v)}"><span>{label}</span>'
                         f'<div class="track"><div class="bar" style="width:{w:.1f}%;background:var(--s{i})"></div></div>'
                         f'<b class="val">{fmt(col, v)}</b></div>')
        cards.append(f'<section class="card"><h2>{esc(head)}</h2>{body}</section>')
    sums = []
    for col, head in CHART_COLUMNS:
        if col.endswith("_seconds") or col.endswith("_pct"):
            continue
        v = [num(r[col]) for r in rows if num(r[col]) is not None]
        if v:
            sums.append(f'<div class="card"><h2>{esc(head)}</h2><b class="val">{sum(v):,.4g}</b>'
                        f'<span class="na"> across {len(v)} of {len(rows)} webinars</span></div>')
    totals = f'<h2 style="margin:18px 0 10px">All webinars combined</h2><div class="grid">{"".join(sums)}</div>'
    note = f'<p class="note">Not captured for any webinar yet: {", ".join(missing)}.</p>' if missing else ""
    html = (f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Webinar Metrics</title><style>{CHART_CSS % {"light": light, "dark": dark}}</style>'
            f'<div class="wrap"><h1>Webinar metrics</h1><p class="sub">Updated {datetime.date.today().isoformat()}. '
            f'Each panel has its own scale. A blank means the value was not captured.</p>'
            f'<div class="legend">{legend}</div>{totals}<h2 style="margin:18px 0 10px">By metric</h2><div class="grid">{"".join(cards)}</div>{note}</div>')
    with open(out, "w") as f:
        f.write(html)
    print(f"Chart written to {out}")


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    cmd = argv[1]
    if cmd == "youtube":
        cmd_youtube(argv[2])
    elif cmd == "youtube-analytics" and len(argv) >= 4:
        cmd_youtube_analytics(argv[2], argv[3], argv[4] if len(argv) > 4 else None)
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
    elif cmd == "chart":
        cmd_chart(argv[2], argv[3] if len(argv) > 3 else None)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
