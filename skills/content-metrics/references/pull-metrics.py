#!/usr/bin/env python3
"""
Content-metrics collector + Slack poster for the DevRel resonance funnel.

Two modes:
  1. Pull mode (default). Fetches blog posts from blog.postman.com and videos
     from the DevRel YouTube channel over a lookback window, writes one CSV
     row per piece to content-metrics/YYYY-Www.csv, and (optionally) posts a
     digest to Slack.
  2. Post-only mode (--from-csv). Skips fetch, reads an existing CSV, and
     posts to Slack. Used by the content-metrics skill so Claude can draft
     commentary between the pull and the post without triggering a second
     round of API calls.

Sources:
  Blog:    blog.postman.com WordPress REST API (all posts with status=publish
           in window). Populates title, ship_date, url, comments. All other
           blog resonance columns need GA4 / GSC (not wired).
  YouTube: youtube.com/postman via YouTube Data API v3 (channel
           UCocudCGVb3MmhWQ1aoIgUQw). Populates views, likes, comments per
           video. Every other YT resonance column (impressions, ctr_pct,
           view_read_time_min, completion_pct, repeat_pct, shares) needs the
           separate YouTube Analytics API — OAuth-only and requires channel-
           manager access on the Postman channel. Not wired; see
           docs/content-funnel.md 'YouTube data sources' for the path.

Env vars:
  WP_USERNAME, WP_APP_PASSWORD   already set in ~/.claude/settings.json
  YT_API_KEY                     Google API key with YouTube Data API v3
                                 enabled. Unlocks views/likes/comments only.
  YT_CHANNEL_ID                  optional override; defaults to the Postman
                                 channel.
  SLACK_WEBHOOK_URL              Incoming Webhook URL. Required with --slack.
  YT_OAUTH_CLIENT_ID,            Reserved for the YouTube Analytics API
  YT_OAUTH_CLIENT_SECRET,        adapter. Not read today. Populate them when
  YT_OAUTH_REFRESH_TOKEN         the adapter lands.
  PRODUCT_ANALYTICS_SOURCE       Selects the product-attribution adapter.
                                 Supported values:
                                   looker         (implemented — see below)
                                   ga4            (stub)
                                   amplitude      (stub)
                                   warehouse      (stub)
                                   postman-admin  (stub)

Looker adapter env vars (used when PRODUCT_ANALYTICS_SOURCE=looker):
  LOOKER_BASE_URL              defaults to https://postman.looker.com
  LOOKER_CLIENT_ID             required. Generate at {base}/admin/users.
  LOOKER_CLIENT_SECRET         required.
  LOOKER_LOOK_ID               required. Numeric ID of the saved Look with
                               per-utm_content signup / activation data.
  LOOKER_UTM_CONTENT_COL       column name in the Look output; default
                               "utm_content". Override if the Look uses a
                               view-prefixed name (e.g. "sessions.utm_content").
  LOOKER_SIGNUPS_COL           default "signups"
  LOOKER_FIRST_RUN_COL         default "first_run"
  LOOKER_DAY7_COL              default "day7_return"
  LOOKER_DAY30_COL             default "day30_return"

Missing WP creds => hard fail.
Missing YT creds => YouTube section skipped with a warning.
Missing SLACK_WEBHOOK_URL with --slack => hard fail (never silently drop).

Not pulled yet (see TODO markers):
  - Watch time / retention (needs YouTube Analytics API + OAuth).
  - Blog reach + UTM clicks (needs GA4 export).
  - Product-side signups filtered by UTM cohort.

Usage:
  python3 pull-metrics.py                                  # past 30 days, no Slack
  python3 pull-metrics.py --days 7                         # past 7 days
  python3 pull-metrics.py --days 30 --slack                # pull + post
  python3 pull-metrics.py --from-csv PATH --slack \\
                          --commentary-file /tmp/notes.txt # post-only + commentary
"""
import argparse
import base64
import csv
import html
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

PST = timezone(timedelta(hours=-8))
REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "content-metrics"

# Postman YouTube channel — https://www.youtube.com/postman (handle @postman)
POSTMAN_YT_CHANNEL_ID = "UCocudCGVb3MmhWQ1aoIgUQw"

CSV_HEADER = [
    "content_id",
    "title",
    "type",
    "ship_date",
    "url",
    # Stage 2 — reach (impressions come from GSC + LinkedIn for blogs, YT
    # Analytics API for videos; views come from GA4 for blogs, YT Data API v3
    # for videos)
    "impressions",
    "views",
    # Stage 3 — resonance
    "ctr_pct",              # TODO_YT_ANALYTICS (video) / TODO_GSC (blog)
    "view_read_time_min",   # TODO_YT_ANALYTICS (video) / TODO_GA4 (blog)
    "completion_pct",       # TODO_YT_ANALYTICS (video) / TODO_GA4_SCROLL (blog)
    "repeat_pct",           # TODO_YT_ANALYTICS (video) / TODO_GA4 (blog)
    "likes",
    "comments",
    "shares",               # TODO: LinkedIn / X reshare for blogs; YT Analytics for videos
    # Stage 4 — intent (top of the product-attribution chain)
    "utm_clicks",           # TODO_GA4: sessions from utm_content filter
    # Stage 5 — activation (Postman product) — filled by fetch_product_activation()
    "attributed_signups",     # TODO_PRODUCT: GA4 sign_up event by utm_content, or equivalent
    "attributed_first_run",   # TODO_PRODUCT: first meaningful product action (workspace, agent run)
    # Stage 6 — adoption (Postman product) — filled by fetch_product_activation()
    "attributed_day7_return",   # TODO_PRODUCT: cohort returned within 7 days
    "attributed_day30_return",  # TODO_PRODUCT: cohort returned within 30 days
    # Derived scores — computed after merge
    "resonance_score",
    "activation_score",
    "adoption_score",
    "impact_score",
    "notes",
]


def iso_days_ago(days):
    return (datetime.now(PST) - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00")


def http_get_json(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


# --------------------------------------------------------------------------
# WordPress: blog.postman.com (all published posts in the window)
# --------------------------------------------------------------------------
def fetch_wordpress_posts(days):
    username = os.environ.get("WP_USERNAME")
    app_password = os.environ.get("WP_APP_PASSWORD")
    if not (username and app_password):
        raise SystemExit("Missing WP_USERNAME or WP_APP_PASSWORD in env.")

    auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "User-Agent": "PostmanDevRelFunnel/0.1",
    }

    after = iso_days_ago(days)
    base = "https://blog.postman.com/wp-json/wp/v2"
    url = (
        f"{base}/posts"
        f"?after={after}"
        f"&status=publish"
        f"&per_page=100"
        f"&orderby=date&order=desc"
        f"&_embed=author"
    )

    posts = http_get_json(url, headers=headers)
    rows = []
    for p in posts:
        published = datetime.fromisoformat(p["date_gmt"]).replace(tzinfo=timezone.utc)
        ship_date = published.astimezone(PST).date().isoformat()
        title = html.unescape(p["title"]["rendered"]).strip()
        rows.append({
            "content_id": f"wp-{p['id']}",
            "title": title,
            "type": "blog",
            "ship_date": ship_date,
            "url": p.get("link", ""),
            "impressions": "",         # TODO_GSC (search) + TODO_SOCIAL (LinkedIn/X)
            "views": "",               # TODO_GA4: WP core has no view count
            "ctr_pct": "",             # TODO_GSC
            "view_read_time_min": "",  # TODO_GA4: avg engagement time
            "completion_pct": "",      # TODO_GA4_SCROLL: needs scroll-depth event
            "repeat_pct": "",          # TODO_GA4: returning users on URL
            "likes": "",
            "comments": _wp_comment_count(p["id"], headers, base),
            "shares": "",              # TODO_SOCIAL: reshare counts
            "utm_clicks": "",
            "attributed_signups": "",
            "attributed_first_run": "",
            "attributed_day7_return": "",
            "attributed_day30_return": "",
            "resonance_score": "",     # computed after all rows fetched
            "activation_score": "",
            "adoption_score": "",
            "impact_score": "",
            "notes": "",
        })
    return rows


def _wp_comment_count(post_id, headers, base):
    try:
        comments = http_get_json(
            f"{base}/comments?post={post_id}&per_page=100&status=approve",
            headers=headers,
        )
        return len(comments)
    except Exception as exc:
        return f"err:{exc.__class__.__name__}"


# --------------------------------------------------------------------------
# YouTube Data API v3 (public stats: views, likes, comments)
# --------------------------------------------------------------------------
def fetch_youtube_videos(days):
    api_key = os.environ.get("YT_API_KEY")
    # Defaults to the Postman channel (https://www.youtube.com/postman). Only
    # override YT_CHANNEL_ID if you're pointing this at a different channel.
    channel_id = os.environ.get("YT_CHANNEL_ID", POSTMAN_YT_CHANNEL_ID)
    uploads_playlist = os.environ.get("YT_UPLOADS_PLAYLIST")

    if not api_key:
        print("[warn] YT_API_KEY not set; skipping YouTube.", file=sys.stderr)
        return []

    if not uploads_playlist:
        chan_url = (
            "https://www.googleapis.com/youtube/v3/channels"
            f"?part=contentDetails&id={channel_id}&key={api_key}"
        )
        chan = http_get_json(chan_url)
        items = chan.get("items", [])
        if not items:
            print(f"[warn] Channel {channel_id} not found; skipping YouTube.",
                  file=sys.stderr)
            return []
        uploads_playlist = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    cutoff = datetime.now(PST) - timedelta(days=days)
    video_ids = []
    page_token = ""
    while True:
        pl_url = (
            "https://www.googleapis.com/youtube/v3/playlistItems"
            f"?part=snippet,contentDetails&maxResults=50"
            f"&playlistId={uploads_playlist}&key={api_key}"
        )
        if page_token:
            pl_url += f"&pageToken={page_token}"
        page = http_get_json(pl_url)

        keep_paging = True
        for item in page.get("items", []):
            published_at = item["contentDetails"].get("videoPublishedAt")
            if not published_at:
                continue
            pub_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            if pub_dt.astimezone(PST) < cutoff:
                keep_paging = False
                break
            video_ids.append(item["contentDetails"]["videoId"])
        page_token = page.get("nextPageToken", "")
        if not page_token or not keep_paging:
            break

    if not video_ids:
        return []

    rows = []
    for i in range(0, len(video_ids), 50):
        batch = ",".join(video_ids[i:i + 50])
        stats_url = (
            "https://www.googleapis.com/youtube/v3/videos"
            f"?part=snippet,statistics&id={batch}&key={api_key}"
        )
        stats = http_get_json(stats_url)
        for v in stats.get("items", []):
            s = v.get("statistics", {})
            sn = v.get("snippet", {})
            published = datetime.fromisoformat(
                sn["publishedAt"].replace("Z", "+00:00")
            )
            rows.append({
                "content_id": f"yt-{v['id']}",
                "title": sn.get("title", ""),
                "type": "youtube",
                "ship_date": published.astimezone(PST).date().isoformat(),
                "url": f"https://www.youtube.com/watch?v={v['id']}",
                "impressions": "",         # TODO_YT_ANALYTICS
                "views": s.get("viewCount", "0"),
                "ctr_pct": "",             # TODO_YT_ANALYTICS
                "view_read_time_min": "",  # TODO_YT_ANALYTICS
                "completion_pct": "",      # TODO_YT_ANALYTICS
                "repeat_pct": "",          # TODO_YT_ANALYTICS
                "likes": s.get("likeCount", "0"),
                "comments": s.get("commentCount", "0"),
                "shares": "",              # TODO_YT_ANALYTICS
                "utm_clicks": "",
                "attributed_signups": "",
                "attributed_first_run": "",
                "attributed_day7_return": "",
                "attributed_day30_return": "",
                "resonance_score": "",
                "activation_score": "",
                "adoption_score": "",
                "impact_score": "",
                "notes": "",
            })
    return rows


# --------------------------------------------------------------------------
# Product attribution (Postman) — plug-in point
# --------------------------------------------------------------------------
# Dispatch to whichever adapter is configured via PRODUCT_ANALYTICS_SOURCE.
# Each adapter has the same signature and returns the same shape. See
# docs/content-funnel.md "Product attribution architecture" for the contract.
def fetch_product_activation(content_ids, since_date):
    """
    Return {content_id: {"signups": int, "first_run": int,
                          "day7_return": int, "day30_return": int}}
    for each content_id passed in. Missing content_ids default to zero.

    Returns an empty dict when no product-side data source is configured. The
    caller treats missing entries as blank cells (not zero) so the Slack
    digest can honestly say "attribution pending" instead of reporting fake
    zeros.
    """
    source = os.environ.get("PRODUCT_ANALYTICS_SOURCE")
    if not source:
        print("[warn] PRODUCT_ANALYTICS_SOURCE not set; activation and "
              "adoption columns will be blank. See docs/content-funnel.md "
              "'Product attribution architecture' for setup.",
              file=sys.stderr)
        return {}

    if source == "looker":
        return _fetch_looker_attribution(content_ids, since_date)
    if source == "ga4":
        # TODO_PRODUCT_GA4: implement using google-analytics-data client
        raise NotImplementedError("GA4 adapter not implemented yet")
    if source == "amplitude":
        # TODO_PRODUCT_AMPLITUDE: implement using Amplitude HTTP API
        raise NotImplementedError("Amplitude adapter not implemented yet")
    if source == "warehouse":
        # TODO_PRODUCT_WAREHOUSE: implement using Snowflake / BigQuery
        raise NotImplementedError("Warehouse adapter not implemented yet")
    if source == "postman-admin":
        # TODO_PRODUCT_POSTMAN_ADMIN: coarse signal via Postman admin API
        raise NotImplementedError("Postman admin API adapter not implemented yet")

    raise SystemExit(f"Unknown PRODUCT_ANALYTICS_SOURCE: {source}")


# --------------------------------------------------------------------------
# Looker adapter — https://postman.looker.com
# --------------------------------------------------------------------------
# Runs a saved Look and remaps its rows to the {content_id: {...}} shape the
# rest of the pipeline expects. The Look must expose utm_content as a
# dimension alongside the four metric columns. Column names are configurable
# via env vars so the adapter doesn't have to be edited when the Look schema
# changes.
def _looker_login(base_url, client_id, client_secret):
    """POST /api/4.0/login. Returns a bearer token."""
    url = f"{base_url}/api/4.0/login"
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read())
    return payload["access_token"]


def _looker_run_look(base_url, access_token, look_id, limit=5000):
    """GET /api/4.0/looks/{id}/run/json. Returns a list of row dicts."""
    url = f"{base_url}/api/4.0/looks/{look_id}/run/json?limit={limit}"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {access_token}"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def _looker_row_int(row, key):
    v = row.get(key)
    if v is None or v == "":
        return 0
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def _fetch_looker_attribution(content_ids, since_date):
    base_url = os.environ.get("LOOKER_BASE_URL", "https://postman.looker.com").rstrip("/")
    client_id = os.environ.get("LOOKER_CLIENT_ID")
    client_secret = os.environ.get("LOOKER_CLIENT_SECRET")
    look_id = os.environ.get("LOOKER_LOOK_ID")

    missing = [name for name, val in (
        ("LOOKER_CLIENT_ID", client_id),
        ("LOOKER_CLIENT_SECRET", client_secret),
        ("LOOKER_LOOK_ID", look_id),
    ) if not val]
    if missing:
        raise SystemExit(
            "Looker adapter is missing required env vars: "
            f"{', '.join(missing)}. Add them to ~/.claude/settings.json. "
            "See docs/content-funnel.md § 'Product attribution architecture' "
            "for setup."
        )

    # Column-name overrides. Defaults are the plain field names; override
    # via env vars if the Look uses view-prefixed names (e.g., "users.signups").
    col_content = os.environ.get("LOOKER_UTM_CONTENT_COL", "utm_content")
    col_signups = os.environ.get("LOOKER_SIGNUPS_COL", "signups")
    col_first_run = os.environ.get("LOOKER_FIRST_RUN_COL", "first_run")
    col_day7 = os.environ.get("LOOKER_DAY7_COL", "day7_return")
    col_day30 = os.environ.get("LOOKER_DAY30_COL", "day30_return")

    try:
        token = _looker_login(base_url, client_id, client_secret)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"Looker login failed: {exc.code} {exc.reason}. "
            f"Verify LOOKER_CLIENT_ID and LOOKER_CLIENT_SECRET at "
            f"{base_url}/admin/users."
        )

    try:
        rows = _looker_run_look(base_url, token, look_id)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"Looker Look {look_id} failed: {exc.code} {exc.reason}. "
            f"Verify LOOKER_LOOK_ID is correct and the API user has access."
        )

    if not rows:
        print(f"[warn] Looker Look {look_id} returned 0 rows.", file=sys.stderr)
        return {}

    # Sanity-check the expected columns. Print a helpful hint if names differ.
    available_cols = set(rows[0].keys())
    expected = {col_content, col_signups, col_first_run, col_day7, col_day30}
    missing_cols = expected - available_cols
    if missing_cols:
        print(
            f"[warn] Looker response missing expected columns: "
            f"{sorted(missing_cols)}. Available columns: {sorted(available_cols)}. "
            f"Override via LOOKER_UTM_CONTENT_COL, LOOKER_SIGNUPS_COL, "
            f"LOOKER_FIRST_RUN_COL, LOOKER_DAY7_COL, LOOKER_DAY30_COL env vars.",
            file=sys.stderr,
        )

    content_id_set = set(content_ids)
    result = {}
    for row in rows:
        cid = row.get(col_content)
        if not cid or cid not in content_id_set:
            continue
        # If a content_id appears in multiple rows (Look grouped by date, for
        # example), sum the metrics across rows.
        agg = result.setdefault(cid, {
            "signups": 0, "first_run": 0,
            "day7_return": 0, "day30_return": 0,
        })
        agg["signups"] += _looker_row_int(row, col_signups)
        agg["first_run"] += _looker_row_int(row, col_first_run)
        agg["day7_return"] += _looker_row_int(row, col_day7)
        agg["day30_return"] += _looker_row_int(row, col_day30)

    print(
        f"[info] Looker: matched {len(result)}/{len(content_ids)} content_ids "
        f"({len(rows)} rows scanned from Look {look_id})."
    )
    return result


def apply_product_attribution(rows, since_date):
    """Merge product-side attribution into each row and compute the three
    downstream scores. Rows without attribution data get blank cells for the
    attributed_* columns and impact_score collapses to resonance_score."""
    content_ids = [r["content_id"] for r in rows]
    try:
        attribution = fetch_product_activation(content_ids, since_date)
    except NotImplementedError as exc:
        print(f"[warn] {exc}; leaving attribution columns blank.",
              file=sys.stderr)
        attribution = {}

    for r in rows:
        data = attribution.get(r["content_id"])
        if data:
            r["attributed_signups"] = data.get("signups", 0)
            r["attributed_first_run"] = data.get("first_run", 0)
            r["attributed_day7_return"] = data.get("day7_return", 0)
            r["attributed_day30_return"] = data.get("day30_return", 0)

        r["resonance_score"] = _compute_resonance_score(r)
        r["activation_score"] = _compute_activation_score(r)
        r["adoption_score"] = _compute_adoption_score(r)
        r["impact_score"] = _compute_impact_score(r)


def _num(row, key):
    """Parse a possibly-blank CSV cell into a float. Blank => 0.0."""
    v = row.get(key, "")
    if v == "" or v is None:
        return 0.0
    try:
        # Handle "12.5%" style
        if isinstance(v, str) and v.endswith("%"):
            v = v[:-1]
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _compute_resonance_score(row):
    return round(
        _num(row, "ctr_pct") * 4
        + _num(row, "view_read_time_min") * 5
        + _num(row, "completion_pct") * 0.5
        + _num(row, "repeat_pct") * 3
        + _num(row, "comments") * 3
        + _num(row, "shares") * 0.5,
        1,
    )


def _compute_activation_score(row):
    return round(
        _num(row, "attributed_signups") * 10
        + _num(row, "attributed_first_run") * 15,
        1,
    )


def _compute_adoption_score(row):
    return round(
        _num(row, "attributed_day7_return") * 20
        + _num(row, "attributed_day30_return") * 40,
        1,
    )


def _compute_impact_score(row):
    return round(
        _num(row, "resonance_score")
        + _num(row, "activation_score")
        + _num(row, "adoption_score"),
        1,
    )


# --------------------------------------------------------------------------
# CSV I/O
# --------------------------------------------------------------------------
def write_csv(rows, week_tag, dry_run=False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{week_tag}.csv"

    if dry_run:
        print(f"[dry-run] would write {len(rows)} rows to {out_path}")
        for row in rows:
            print(json.dumps(row))
        return out_path

    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return out_path


def read_csv(path):
    with Path(path).open("r", newline="") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------
# Slack
# --------------------------------------------------------------------------
def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _fmt_int(value):
    n = _int(value, None)
    if n is None:
        return "-"
    return f"{n:,}"


def _truncate(text, width):
    text = text.strip()
    if len(text) <= width:
        return text
    return text[: width - 1] + "…"


def _build_table(rows, top_n=10):
    top = sorted(rows, key=lambda r: _int(r.get("views")), reverse=True)[:top_n]
    header = f"{'Content':<40}  {'Type':<7}  {'Views':>7}  {'Likes':>6}  {'Cmts':>5}"
    sep = "-" * len(header)
    lines = [header, sep]
    for r in top:
        lines.append(
            f"{_truncate(r['title'], 40):<40}  "
            f"{r['type']:<7}  "
            f"{_fmt_int(r['views']):>7}  "
            f"{_fmt_int(r['likes']):>6}  "
            f"{_fmt_int(r['comments']):>5}"
        )
    return "\n".join(lines)


def _sum_col(rows, key):
    return sum(_int(r.get(key)) for r in rows)


def _build_product_headline(rows):
    """Return the 'Content -> Product' line for the Slack digest. If any
    attribution data is present, report totals; if all rows are blank on
    attribution, say attribution is pending (never fake a zero)."""
    any_attributed = any(
        r.get("attributed_signups") not in ("", None) for r in rows
    )
    if not any_attributed:
        return (
            "*Content → Product this window:* attribution pending "
            "(product-side data source not configured; see "
            "`docs/content-funnel.md` § Product attribution architecture)."
        )
    signups = _sum_col(rows, "attributed_signups")
    first_run = _sum_col(rows, "attributed_first_run")
    d7 = _sum_col(rows, "attributed_day7_return")
    d30 = _sum_col(rows, "attributed_day30_return")
    return (
        f"*Content → Product this window:* "
        f"{signups} signups • {first_run} first product actions • "
        f"{d7} Day-7 returned • {d30} Day-30 returned "
        f"(attributed via utm_content)"
    )


def post_to_slack(rows, csv_path, week_tag, days, commentary_text=None):
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        raise SystemExit(
            "Missing SLACK_WEBHOOK_URL. Create an Incoming Webhook at "
            "https://api.slack.com/apps and add the URL to ~/.claude/settings.json."
        )

    now = datetime.now(PST)
    window_start = (now - timedelta(days=days)).strftime("%b %d")
    window_end = now.strftime("%b %d, %Y")
    blog_count = sum(1 for r in rows if r["type"] == "blog")
    yt_count = sum(1 for r in rows if r["type"] == "youtube")

    if not rows:
        table = "No content shipped in this window."
    else:
        table = _build_table(rows)

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"Content → Product — {week_tag}"},
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"Window: *{window_start} – {window_end}*  |  "
                        f"Ship count: *{blog_count} blog posts + {yt_count} videos*"
                    ),
                }
            ],
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": _build_product_headline(rows)},
        },
    ]

    if commentary_text and commentary_text.strip():
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": commentary_text.strip()},
        })

    blocks.extend([
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Top pieces by views*\n```{table}```"},
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        "Blank columns (impressions, CTR, watch/read time, "
                        "completion, attribution) are pending instrumentation. "
                        "See `docs/content-funnel.md`. "
                        f"Full CSV: `{csv_path.relative_to(REPO_ROOT)}`"
                    ),
                }
            ],
        },
    ])

    payload = json.dumps({"blocks": blocks, "text": f"Content → Product — {week_tag}"}).encode()
    req = urllib.request.Request(
        webhook,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            if body.strip() != "ok":
                print(f"[warn] Slack responded with: {body}", file=sys.stderr)
            else:
                print("[done] Posted to Slack.")
    except urllib.error.HTTPError as exc:
        print(f"[error] Slack POST failed: {exc.code} {exc.reason}", file=sys.stderr)
        print(exc.read().decode(errors="replace"), file=sys.stderr)
        raise


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=30,
                    help="Look-back window in days (default: 30). Ignored with --from-csv.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print rows to stdout instead of writing CSV")
    ap.add_argument("--skip-yt", action="store_true",
                    help="Skip YouTube even if credentials are set")
    ap.add_argument("--skip-wp", action="store_true",
                    help="Skip WordPress")
    ap.add_argument("--slack", action="store_true",
                    help="Post a digest to Slack (needs SLACK_WEBHOOK_URL)")
    ap.add_argument("--from-csv", type=str, default=None,
                    help="Skip fetch; post using this existing CSV path (implies --slack)")
    ap.add_argument("--commentary-file", type=str, default=None,
                    help="Path to a text file with commentary to inject into the Slack post")
    args = ap.parse_args()

    now = datetime.now(PST)
    iso_year, iso_week, _ = now.isocalendar()
    week_tag = f"{iso_year}-W{iso_week:02d}"

    if args.from_csv:
        csv_path = Path(args.from_csv).resolve()
        rows = read_csv(csv_path)
        print(f"[info] Loaded {len(rows)} rows from {csv_path}")
        args.slack = True
    else:
        rows = []
        if not args.skip_wp:
            wp_rows = fetch_wordpress_posts(args.days)
            print(f"[info] WordPress rows: {len(wp_rows)}")
            rows.extend(wp_rows)
        if not args.skip_yt:
            yt_rows = fetch_youtube_videos(args.days)
            print(f"[info] YouTube rows:   {len(yt_rows)}")
            rows.extend(yt_rows)

        # Merge Postman product activation + adoption data into each row and
        # compute the three-part impact_score. Missing data source leaves the
        # attributed_* columns blank (documented behavior).
        since_date = (datetime.now(PST) - timedelta(days=args.days)).date()
        apply_product_attribution(rows, since_date)

        csv_path = write_csv(rows, week_tag, dry_run=args.dry_run)
        print(f"[done] {len(rows)} rows -> {csv_path}")
        print(f"[csv] {csv_path}")

    if args.slack:
        commentary_text = None
        if args.commentary_file:
            with open(args.commentary_file, "r") as f:
                commentary_text = f.read()
        post_to_slack(rows, csv_path, week_tag, args.days, commentary_text=commentary_text)


if __name__ == "__main__":
    main()
