#!/usr/bin/env python3
"""Blog metrics for qbr-metrics: WordPress post counts + Jetpack Stats views.

Usage: pull-wp.py START END   (YYYY-MM-DD). Prints JSON to stdout.

Views come from Jetpack Stats via the WordPress REST proxy, authenticated with
WP_USERNAME / WP_APP_PASSWORD. Jetpack cannot split paid from organic traffic
on this plan (UTM stats return 403), so blog views are totals only.
"""
import base64
import json
import os
import sys
from datetime import timedelta

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

WP = "https://blog.postman.com/wp-json"
JETPACK = f"{WP}/jetpack/v4/stats-app/sites/199676833/stats"


def headers():
    user, pw = os.environ.get("WP_USERNAME"), os.environ.get("WP_APP_PASSWORD")
    if not (user and pw):
        sys.exit("WP_USERNAME and WP_APP_PASSWORD are required")
    tok = base64.b64encode(f"{user}:{pw}".encode()).decode()
    return {"Authorization": f"Basic {tok}", "User-Agent": "PostmanDevRelDashboard/1.0"}


def posts_published(h, start, end):
    out, page = [], 1
    while True:
        url = (f"{WP}/wp/v2/posts?status=publish&per_page=100&page={page}&orderby=date&order=asc"
               f"&after={start}T00:00:00&before={end}T23:59:59&_fields=id,date,link,title")
        status, body = q.http_json(url, h)
        if status != 200:
            sys.exit(f"WordPress posts query failed: HTTP {status} {str(body)[:200]}")
        out += body
        if len(body) < 100:
            return out
        page += 1


def window(h, start, end):
    days = (end - start).days + 1
    status, vis = q.http_json(f"{JETPACK}/visits?unit=day&quantity={days}&date={end}", h)
    if status != 200:
        sys.exit(f"Jetpack visits failed: HTTP {status} {str(vis)[:200]}")
    daily_views = {row[0]: row[1] for row in vis["data"]}
    visitors = sum(row[2] for row in vis["data"])
    status, top = q.http_json(
        f"{JETPACK}/top-posts?period=day&date={end}&num={days}&summarize=1&max=500", h)
    views_by_id = {}
    if status == 200:
        for p in top.get("summary", {}).get("postviews", []):
            if p.get("type") == "post":
                views_by_id[p["id"]] = p
    posts = posts_published(h, start, end)
    published = []
    for p in posts:
        v = views_by_id.get(p["id"], {}).get("views")
        published.append({"id": p["id"], "title": p["title"]["rendered"], "url": p["link"],
                          "date": p["date"][:10], "views_in_period": v})
    top_posts = sorted(views_by_id.values(), key=lambda p: p["views"], reverse=True)[:5]
    return {
        "start": str(start), "end": str(end),
        "posts_published": len(posts),
        "views": sum(daily_views.values()),
        "visitors": visitors,
        "views_per_published_post": None,
        "weekly_views": q.weekly(daily_views, start, end),
        "top_posts": [{"title": p["title"], "url": p["href"], "views": p["views"]} for p in top_posts],
        "published": published,
        "top_posts_note": "Top posts by views in the period, including posts published earlier",
    }


def main():
    q.load_settings_env()
    cur, prev = q.periods(sys.argv[1], sys.argv[2])
    h = headers()
    result = {"current": window(h, *cur), "previous": window(h, *prev),
              "paid_split": "not available (Jetpack UTM stats are blocked by the blog's plan)"}
    c, p = result["current"], result["previous"]
    for w in (c, p):
        w["views_per_published_post"] = round(w["views"] / w["posts_published"]) if w["posts_published"] else None
    result["change"] = {k: q.pct_change(c[k], p[k]) for k in ("posts_published", "views", "visitors")}
    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
