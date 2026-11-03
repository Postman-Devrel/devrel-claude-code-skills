#!/usr/bin/env python3
"""Tag blog posts and videos by topic and content style, then compare medians.

Usage: classify-topics.py OUT_DIR
Reads OUT_DIR/raw-wp.json and OUT_DIR/raw-youtube.json, writes OUT_DIR/topics.json.

Rules are keyword matches on the title, first match wins, so the labels are reproducible
between quarters. Edit TOPICS and STYLES below to change the taxonomy, then rerun. Review the
"Other" bucket for pieces that need a new rule. Groups with fewer than MIN_GROUP pieces are not
ranked. Blog metric: views in the period (Jetpack). Video metric: organic views (total minus
ad views). Localized duplicates and event recordings are excluded from the comparisons.
"""
import html
import json
import os
import statistics
import sys

MIN_GROUP = 3
AD_CREATIVE = ("thats like", "that's like", "ai without apis", "teaser")  # short ad spots; see paid vs organic

TOPICS = [  # (label, keywords) - first match wins
    ("Customer and partner stories", ("nubank", "cisco", "meraki", "paypal", "medibank", "case study", "customer", "accredited seller", "partner sales")),
    ("Events and community", ("apidays", "meetup", "paddle", "dev meetup")),
    ("MCP", ("mcp", "model context protocol")),
    ("API security and secrets", ("security", "secret", "passport", "wiz", "access control", "iso 42001", "certification", "hipaa", "compliant", "compliance", "api keys", "credential", "pii", "redact")),
    ("Testing, QE and performance", ("performance testing", " qe ", "qe pipeline", "qe program", "qe platform", "monitor", "quality", "playwright", "your api tests", "validate apis", "load test", "load testing")),
    ("Enterprise and private cloud", ("private cloud", "site-wide", "air-gapped", "enterprises:", "licensing")),
    ("API governance and catalog", ("governance", "catalog", "scorecard", "api health")),
    ("AI agents and context", ("agent", "agentic", "context", "loop", "beads", "quill", "orbit", "astropods", "ai engineer",
                               "autonomous engineer", "ai-ready", "ai is ready", "rag", "prompt engineering", "apiflow",
                               "postman.ai", "claude", "codex", "token", "ai coding", "astro", "ai code review", "analyzer", "assistant", "helper", "ai sprawl", "shadow it", "model routing", "ai costs", "llm", "gateway", "fabric")),
    ("API fundamentals and explainers", ("what is an api", "what are api", "api key", "api endpoint", "rest api", "api fundamentals", "fundamentals",
                                         "explained in", "http methods", "types of apis", "bearer token", "502 bad gateway", "status code")),
    ("Product features and how-tos", ("what's new", "whats new", "native datasets", "local project", "blueprint", "configuring",
                                      "live sessions", "share your local", "sdk", "webhook", "scripting", "api-sdk", "grpc",
                                      "graphql", "api drift", "drift", "mock", "local development", "cli", "dataset", "reusable requests", "git integration",
                                      "features tour", "new features", "introducing the new postman", "import postman collections", "postman collections")),
]
STYLES = [
    ("Announcement or release", ("announcing", "introducing", "what's new", "whats new", "now in", "earns", "launch")),
    ("Customer story", ("nubank", "cisco", "customer spotlight", "customer stories")),
    ("Explainer", ("what is", "types of", "explained", "why ", "sdk vs", "vs ")),
    ("Tutorial or how-to", ("how ", "build", "configuring", "deploy", "managing", "share", "scheduling", "develop and test",
                            "querying", "catching", "finding", "fixes", "makes changes", "multi-repo", "recipes", "increasing",
                            "first local", "native datasets", "performance testing")),
]


def label(title, rules, default):
    t = " " + title.lower() + " "
    for name, keys in rules:
        if any(k in t for k in keys):
            return name
    return default


def med(vals):
    vals = [v for v in vals if v is not None]
    return round(statistics.median(vals)) if vals else None


def summarize(items, key):
    groups = {}
    for it in items:
        groups.setdefault(it[key], []).append(it)
    out = []
    for name, g in groups.items():
        out.append({"label": name, "pieces": len(g), "median_metric": med([x["metric"] for x in g]) if len(g) >= MIN_GROUP else None,
                    "total_metric": sum(x["metric"] or 0 for x in g),
                    "ranked": len(g) >= MIN_GROUP, "titles": [x["title"] for x in sorted(g, key=lambda x: -(x["metric"] or 0))][:6]})
    return sorted(out, key=lambda x: (-(x["median_metric"] or -1), -x["pieces"]))


LENGTH_BUCKETS = [("under 1 min", 0, 60), ("1 to 5 min", 60, 300), ("5 to 15 min", 300, 900), ("over 15 min", 900, 10 ** 9)]


def by_length(items, videos_by_title):
    out = []
    for label_, lo, hi in LENGTH_BUCKETS:
        g = [i for i in items if lo <= i["duration_s"] < hi]
        out.append({"bucket": label_, "pieces": len(g),
                    "median_organic_views": med([i["metric"] for i in g]) if len(g) >= MIN_GROUP else None})
    return out


def blog_items(posts):
    return [{"title": html.unescape(p["title"]), "metric": p["views_in_period"], "date": p["date"],
             "topic": label(html.unescape(p["title"]), TOPICS, "Other"), "style": label(html.unescape(p["title"]), STYLES, "Opinion or other")}
            for p in posts]


def video_items(videos):
    seen, items = {}, []
    for v in videos:
        key = (v["published"], v["duration_s"])
        title = html.unescape(v["title"])
        excluded = None
        if v["duration_s"] > 3600:
            excluded = "event recording"
        elif v["format"] == "shorts" and (title.strip().lower() == "postman" or any(k in title.lower() for k in AD_CREATIVE)):
            excluded = "paid ad creative (short ad spot)"
        elif key in seen and (v["organic_views"] or 0) == 0:
            excluded = "localized duplicate"
        seen.setdefault(key, v["id"])
        items.append({"title": title, "metric": v["organic_views"], "date": v["published"], "format": v["format"], "duration_s": v["duration_s"],
                      "topic": label(title, TOPICS, "Other"), "style": label(title, STYLES, "Opinion or other"),
                      "excluded": excluded})
    return items


def is_ad_creative(title):
    low = title.strip().lower()
    return low == "postman" or any(k in low for k in AD_CREATIVE)


def top_video_summary(top):
    rows = []
    for v in top:
        cat = "Paid ad creative" if is_ad_creative(v["title"]) else label(v["title"], TOPICS, "Other")
        rows.append(dict(v, category=cat, style=label(v["title"], STYLES, "Opinion or other")))
    agg = {}
    for r in rows:
        a = agg.setdefault(r["category"], {"category": r["category"], "videos": 0, "paid_views": 0, "organic_views": 0})
        a["videos"] += 1
        a["paid_views"] += r["paid_views"]
        a["organic_views"] += r["organic_views"]
    for a in agg.values():
        tot = a["paid_views"] + a["organic_views"]
        a["paid_share_pct"] = round(a["paid_views"] / tot * 100, 1) if tot else None
    return {"rows": rows, "by_category": sorted(agg.values(), key=lambda a: -(a["paid_views"] + a["organic_views"]))}


def main():
    out_dir = sys.argv[1]
    wp = json.load(open(os.path.join(out_dir, "raw-wp.json")))
    yt = json.load(open(os.path.join(out_dir, "raw-youtube.json")))
    result = {"min_group": MIN_GROUP, "metrics": {"blog": "views in the period (Jetpack)", "video": "organic views (total minus ad views)"}}
    for period in ("current", "previous"):
        blog = blog_items(wp[period]["published"])
        vids = video_items(yt[period]["videos"])
        used = [v for v in vids if not v["excluded"]]
        result[period] = {
            "blog": {"pieces": len(blog), "by_topic": summarize(blog, "topic"), "by_style": summarize(blog, "style"), "items": blog},
            "video": {"pieces": len(used), "by_length": by_length(used, None), "excluded": [{"title": v["title"], "why": v["excluded"]} for v in vids if v["excluded"]],
                      "by_topic": summarize(used, "topic"), "by_style": summarize(used, "style"), "items": vids},
        }
    for period in ("current", "previous"):
        if yt[period].get("top_videos"):
            result[period]["top_videos"] = top_video_summary(yt[period]["top_videos"])
    other = [i["title"] for i in result["current"]["blog"]["items"] + result["current"]["video"]["items"] if i["topic"] == "Other"]
    result["unclassified_current"] = other
    json.dump(result, open(os.path.join(out_dir, "topics.json"), "w"), indent=2)
    print(json.dumps({"unclassified": other}, indent=2))


if __name__ == "__main__":
    main()
