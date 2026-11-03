#!/usr/bin/env python3
"""YouTube metrics for qbr-metrics: long-form vs Shorts, paid vs organic, subscribers.

Usage: pull-youtube.py START END   (YYYY-MM-DD). Prints JSON to stdout.

Needs YT_OAUTH_CLIENT_ID, YT_OAUTH_CLIENT_SECRET, YT_OAUTH_REFRESH_TOKEN (see
youtube-oauth-setup.py). Paid = traffic source ADVERTISING; organic = total minus paid.
Impressions and CTR are not exposed by the Analytics API and are reported as unavailable.
Subscribers gained cannot be split by traffic source.
"""
import json
import os
import re
import statistics
import sys
from datetime import timedelta
from urllib.parse import urlencode

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

CHANNEL = os.environ.get("YT_CHANNEL_ID", "UCocudCGVb3MmhWQ1aoIgUQw")
FORMATS = {"long_form": "videoOnDemand", "shorts": "shorts"}
MAX_PER_VIDEO_QUERIES = 120


class YT:
    def __init__(self):
        for k in ("YT_OAUTH_CLIENT_ID", "YT_OAUTH_CLIENT_SECRET", "YT_OAUTH_REFRESH_TOKEN"):
            if not os.environ.get(k):
                sys.exit(f"{k} is required (run youtube-oauth-setup.py)")
        status, body = q.http_json("https://oauth2.googleapis.com/token", data={
            "client_id": os.environ["YT_OAUTH_CLIENT_ID"],
            "client_secret": os.environ["YT_OAUTH_CLIENT_SECRET"],
            "refresh_token": os.environ["YT_OAUTH_REFRESH_TOKEN"],
            "grant_type": "refresh_token"})
        if status != 200:
            sys.exit(f"YouTube token refresh failed: HTTP {status} {str(body)[:200]}")
        self.h = {"Authorization": f"Bearer {body['access_token']}"}

    def data(self, path, **params):
        status, body = q.http_json(f"https://www.googleapis.com/youtube/v3/{path}?{urlencode(params)}", self.h)
        if status != 200:
            sys.exit(f"YouTube Data API {path} failed: HTTP {status} {str(body)[:200]}")
        return body

    def analytics(self, start, end, metrics, dims=None, filters=None, sort=None, limit=None):
        p = {"ids": f"channel=={CHANNEL}", "startDate": str(start), "endDate": str(end), "metrics": metrics}
        if dims:
            p["dimensions"] = dims
        if filters:
            p["filters"] = filters
        if sort:
            p["sort"] = sort
        if limit:
            p["maxResults"] = limit
        status, body = q.http_json(f"https://youtubeanalytics.googleapis.com/v2/reports?{urlencode(p)}", self.h)
        if status != 200:
            return None
        return body.get("rows", [])


def iso_duration_seconds(s):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    dd, hh, mm, ss = (int(x or 0) for x in m.groups())
    return dd * 86400 + hh * 3600 + mm * 60 + ss


def format_block(yt, start, end, fmt_key):
    ctype = FORMATS[fmt_key]
    tot = yt.analytics(start, end, "views,estimatedMinutesWatched,subscribersGained", "creatorContentType") or []
    row = next((r for r in tot if r[0] == ctype), [ctype, 0, 0, 0])
    views, minutes, subs = row[1], row[2], row[3]
    src = yt.analytics(start, end, "views,estimatedMinutesWatched", "insightTrafficSourceType",
                       f"creatorContentType=={ctype}") or []
    paid = next((r for r in src if r[0] == "ADVERTISING"), ["ADVERTISING", 0, 0])
    paid_v, paid_m = paid[1], paid[2]
    day_all = yt.analytics(start, end, "views", "day", f"creatorContentType=={ctype}") or []
    day_src = yt.analytics(start, end, "views", "day,insightTrafficSourceType", f"creatorContentType=={ctype}") or []
    daily_total = {r[0]: r[1] for r in day_all}
    daily_paid = {r[0]: r[2] for r in day_src if r[1] == "ADVERTISING"}
    daily_org = {k: v - daily_paid.get(k, 0) for k, v in daily_total.items()}
    org_v, org_m = views - paid_v, minutes - paid_m
    return {
        "views": views, "watch_minutes": minutes, "subscribers_gained": subs,
        "avg_view_duration_s": round(minutes * 60 / views, 1) if views else None,
        "paid_views": paid_v, "organic_views": org_v,
        "paid_watch_minutes": paid_m, "organic_watch_minutes": org_m,
        "paid_share_pct": round(paid_v / views * 100, 1) if views else None,
        "organic_avg_view_duration_s": round(org_m * 60 / org_v, 1) if org_v > 0 else None,
        "weekly_views": q.weekly(daily_total, start, end),
        "weekly_paid_views": q.weekly(daily_paid, start, end),
        "weekly_organic_views": q.weekly(daily_org, start, end),
    }


def uploads_in_range(yt, start, end):
    """All uploads published between start and end (inclusive), newest first."""
    ch = yt.data("channels", part="contentDetails,statistics", id=CHANNEL)["items"][0]
    playlist = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    subs_total = int(ch["statistics"].get("subscriberCount", 0))
    items, token = [], None
    while True:
        params = {"part": "contentDetails", "playlistId": playlist, "maxResults": 50}
        if token:
            params["pageToken"] = token
        body = yt.data("playlistItems", **params)
        stop = False
        for it in body["items"]:
            pub = it["contentDetails"].get("videoPublishedAt", "")[:10]
            if not pub:
                continue
            if pub < str(start):
                stop = True
                continue
            if pub <= str(end):
                items.append((it["contentDetails"]["videoId"], pub))
        token = body.get("nextPageToken")
        if stop or not token:
            return items, subs_total


def video_details(yt, ids):
    out = {}
    for i in range(0, len(ids), 50):
        body = yt.data("videos", part="snippet,contentDetails,liveStreamingDetails", id=",".join(ids[i:i + 50]))
        for v in body["items"]:
            ls = v.get("liveStreamingDetails") or {}
            out[v["id"]] = {"title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"][:10],
                            "live_start": (ls.get("actualStartTime") or "")[:10],
                            "duration_s": iso_duration_seconds(v["contentDetails"]["duration"])}
    return out


def videos_block(yt, start, end):
    uploads, subs_total = uploads_in_range(yt, start, end)
    ids = [v for v, _ in uploads]
    pub = dict(uploads)
    details = video_details(yt, ids) if ids else {}
    shorts_set = set()
    if ids:
        rows = yt.analytics(min(pub.values()), end, "views", "video", "creatorContentType==shorts",
                            "-views", 500) or []
        shorts_set = {r[0] for r in rows}
    videos = []
    for i, vid in enumerate(ids):
        det = details.get(vid, {"title": vid, "duration_s": 0})
        fmt = "shorts" if (vid in shorts_set or 0 < det["duration_s"] <= 60) else "long_form"
        first_day = min(q.d(pub[vid]), q.d(det["live_start"])) if det.get("live_start") else q.d(pub[vid])
        p_start = max(first_day, q.d(start))
        row = yt.analytics(p_start, end, "views,estimatedMinutesWatched", None, f"video=={vid}") or [[0, 0]]
        views, minutes = (row[0][0], row[0][1]) if row else (0, 0)
        paid_v = None
        if i < MAX_PER_VIDEO_QUERIES:
            src = yt.analytics(p_start, end, "views", "insightTrafficSourceType", f"video=={vid}") or []
            paid_v = next((r[1] for r in src if r[0] == "ADVERTISING"), 0)
        videos.append({"id": vid, "title": det["title"], "published": pub[vid], "format": fmt, "live_start": det.get("live_start") or None,
                       "duration_s": det["duration_s"], "views": views, "watch_minutes": minutes,
                       "paid_views": paid_v,
                       "organic_views": (views - paid_v) if paid_v is not None else None})
    return videos, subs_total


def top_videos_block(yt, start, end, n=30):
    """The n most-viewed videos in the period (any publish date) with their paid and organic views.
    The per-video paid split needs one Analytics query per video, so n is kept modest."""
    rows = yt.analytics(start, end, "views", "video", sort="-views", limit=n) or []
    ids = [r[0] for r in rows]
    views = {r[0]: r[1] for r in rows}
    details = video_details(yt, ids) if ids else {}
    out = []
    for vid in ids:
        src = yt.analytics(start, end, "views", "insightTrafficSourceType", f"video=={vid}") or []
        paid = next((r[1] for r in src if r[0] == "ADVERTISING"), 0)
        det = details.get(vid, {"title": vid, "published": "", "duration_s": 0})
        out.append({"id": vid, "title": det["title"], "published": det["published"], "duration_s": det["duration_s"],
                    "views": views[vid], "paid_views": paid, "organic_views": views[vid] - paid})
    return out


def live_block(yt, start, end, videos=None):
    """YouTube Live: channel-level totals for live content, plus the live streams that started in the period.

    A video counts as a live stream only if Analytics classes it as creatorContentType liveStream (premieres
    carry live-streaming details but are not live streams). Views on live content include replays and older
    archives, so streams started in the period are listed separately, with views counted from the stream start."""
    row = yt.analytics(start, end, "views,estimatedMinutesWatched,averageViewDuration,subscribersGained,shares", "creatorContentType",
                       "creatorContentType==liveStream") or []
    r = row[0] if row else ["liveStream", 0, 0, 0, 0, 0]
    live_rows = yt.analytics(start, end, "views,estimatedMinutesWatched", "video", "creatorContentType==liveStream", "-views", 50) or []
    details = video_details(yt, [x[0] for x in live_rows]) if live_rows else {}
    streams = [{"id": x[0], "title": details[x[0]]["title"], "started": details[x[0]]["live_start"], "duration_s": details[x[0]]["duration_s"],
                "views": x[1], "watch_minutes": x[2]}
               for x in live_rows if x[0] in details and details[x[0]].get("live_start") and str(start) <= details[x[0]]["live_start"] <= str(end)]
    return {"views": r[1], "watch_minutes": r[2], "avg_view_duration_s": r[3], "subscribers_gained": r[4], "shares": r[5],
            "streams_started": len(streams), "streams": streams}


def summarize_videos(videos):
    def med(vals):
        vals = [v for v in vals if v is not None]
        return round(statistics.median(vals)) if vals else None
    out = {}
    for fmt in ("long_form", "shorts"):
        vs = [v for v in videos if v["format"] == fmt]
        out[fmt] = {"published": len(vs), "median_views": med([v["views"] for v in vs]),
                    "median_organic_views": med([v["organic_views"] for v in vs])}
    buckets = [("under 1 min", 0, 60), ("1 to 5 min", 60, 300), ("5 to 15 min", 300, 900), ("over 15 min", 900, 10**9)]
    out["by_length"] = []
    for label, lo, hi in buckets:
        vs = [v for v in videos if lo <= v["duration_s"] < hi]
        out["by_length"].append({"bucket": label, "pieces": len(vs),
                                 "median_organic_views": med([v["organic_views"] for v in vs]) if len(vs) >= 3 else None})
    return out


def window(yt, start, end):
    blocks = {k: format_block(yt, start, end, k) for k in FORMATS}
    chan = yt.analytics(start, end, "subscribersGained,subscribersLost") or [[0, 0]]
    gained, lost = chan[0][0], chan[0][1]
    daily = yt.analytics(start, end, "subscribersGained,subscribersLost", "day") or []
    net_daily = {r[0]: r[1] - r[2] for r in daily}
    sources = yt.analytics(start, end, "views", "insightTrafficSourceType", sort="-views") or []
    ad_detail = yt.analytics(start, end, "views", "insightTrafficSourceDetail",
                             "insightTrafficSourceType==ADVERTISING", "-views", 5) or []
    videos, subs_total = videos_block(yt, start, end)
    return {
        "start": str(start), "end": str(end),
        "formats": blocks,
        "totals": {k: sum(b[k] for b in blocks.values())
                   for k in ("views", "watch_minutes", "paid_views", "organic_views")},
        "subscribers": {"gained": gained, "lost": lost, "net": gained - lost,
                        "weekly_net": q.weekly(net_daily, start, end)},
        "traffic_sources": [{"source": r[0], "views": r[1]} for r in sources[:8]],
        "paid_ad_formats": [{"format": r[0], "views": r[1]} for r in ad_detail],
        "videos": videos,
        "top_videos": top_videos_block(yt, start, end),
        "live": live_block(yt, start, end, videos),
        "video_summary": summarize_videos(videos),
        "_subs_total_now": subs_total,
    }


def main():
    q.load_settings_env()
    cur, prev = q.periods(sys.argv[1], sys.argv[2])
    yt = YT()
    q.log("YouTube: current period")
    c = window(yt, *cur)
    q.log("YouTube: previous period")
    p = window(yt, *prev)
    subs_now = c.pop("_subs_total_now")
    p.pop("_subs_total_now")
    change = {}
    for fmt in FORMATS:
        for k in ("views", "organic_views", "paid_views", "watch_minutes", "subscribers_gained"):
            change[f"{fmt}.{k}"] = q.pct_change(c["formats"][fmt][k], p["formats"][fmt][k])
    for k in ("views", "organic_views", "paid_views", "watch_minutes"):
        change[f"total.{k}"] = q.pct_change(c["totals"][k], p["totals"][k])
    change["subscribers_net"] = q.pct_change(c["subscribers"]["net"], p["subscribers"]["net"])
    json.dump({
        "current": c, "previous": p, "change": change,
        "subscribers_total_now": subs_now,
        "impressions_ctr": "not available (the YouTube Analytics API does not expose them)",
        "subscribers_paid_split": "not available (subscribersGained cannot be split by traffic source)",
    }, sys.stdout)


if __name__ == "__main__":
    main()
