#!/usr/bin/env python3
"""LinkedIn metrics for qbr-metrics, scoped to DevRel content: reshared blog posts, newsletter editions and webinars.

Usage: pull-linkedin.py START END   (YYYY-MM-DD). Prints JSON to stdout.

Read-only. Uses the LinkedIn Community Management API with an organization-admin access token. The token is
taken from LINKEDIN_ACCESS_TOKEN, else from the JSON file named by LINKEDIN_TOKEN_FILE (default: the state file of
the agent-team-socialmedia app, which holds a token for the same organization). The token is never printed.

Scope. Only organic posts (feedDistribution not NONE) are considered, and only three kinds are reported:
  blog reshare   a post linking to blog.postman.com, directly or through a lnkd.in short link
  newsletter     a post referencing a LinkedIn newsletter edition (urn:li:linkedInArticle) or naming the Dev Digest
  webinar        a post referencing a live video or event, or announcing a webinar or session; plus each LinkedIn Live
                 event's own announcement post
Page-wide totals, ads (dark posts) and every other organic post are left out on purpose.

Limits. LinkedIn lists organic posts only from when the social agent began posting through the API, so earlier
periods have no per-post data and are reported as unavailable, not zero. Posts whose blog link is only in a comment
or an image cannot be identified, so the blog reshare count is a floor. LinkedIn does not return event registrants or
attendees, live viewer counts, or newsletter subscribers and article views.
"""
import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

API = "https://api.linkedin.com"
DEFAULT_TOKEN_FILE = "~/Code/agent-teams/agent-team-socialmedia/state/linkedin_oauth.json"
MAX_POSTS = 6000
WEBINAR_WORDS = ("webinar", "live session", "this session", "join us live", "register now", "livestream", "live stream", "workshop")
STAT_KEYS = ("impressions", "unique_impressions", "clicks", "reactions", "comments", "shares")


def token():
    t = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    if t:
        return t
    path = os.path.expanduser(os.environ.get("LINKEDIN_TOKEN_FILE", DEFAULT_TOKEN_FILE))
    try:
        with open(path) as f:
            return json.load(f)["access_token"]
    except (OSError, ValueError, KeyError):
        sys.exit("No LinkedIn token: set LINKEDIN_ACCESS_TOKEN or LINKEDIN_TOKEN_FILE (see linkedin-oauth-setup.py)")


class LI:
    def __init__(self):
        self.org = os.environ.get("LINKEDIN_AUTHOR_URN", "urn:li:organization:3795851")
        self.enc = urllib.parse.quote(self.org, safe="")
        self.h = {"Authorization": f"Bearer {token()}", "X-Restli-Protocol-Version": "2.0.0",
                  "LinkedIn-Version": os.environ.get("LINKEDIN_VERSION", "202610")}

    def get(self, path, params=""):
        return q.http_json(API + path + (("?" + params) if params else ""), self.h, retries=2)

    def paged(self, path, params, page=100, cap=10 ** 9):
        out, start = [], 0
        while start < cap:
            s, b = self.get(path, f"{params}&count={page}&start={start}")
            if s != 200:
                sys.exit(f"LinkedIn {path} failed: HTTP {s} {str(b)[:200]}")
            els = b.get("elements", [])
            out += els
            start += len(els)
            total = (b.get("paging") or {}).get("total")
            if not els or (total is not None and start >= total):
                break
        return out

    def post_stats(self, urns):
        """Per-post statistics for share and ugcPost URNs, 20 at a time. Returns {urn: stats}."""
        out = {}
        for kind, param in (("urn:li:share:", "shares"), ("urn:li:ugcPost:", "ugcPosts")):
            mine = [u for u in urns if u.startswith(kind)]
            for i in range(0, len(mine), 20):
                chunk = mine[i:i + 20]
                lst = ",".join(urllib.parse.quote(u, safe="") for u in chunk)
                s, b = self.get("/rest/organizationalEntityShareStatistics", f"q=organizationalEntity&organizationalEntity={self.enc}&{param}=List({lst})")
                if s != 200:
                    continue
                for e in b.get("elements", []):
                    key = e.get("share") or e.get("ugcPost")
                    t = e.get("totalShareStatistics") or {}
                    out[key] = {"impressions": t.get("impressionCount") or 0, "unique_impressions": t.get("uniqueImpressionsCount") or 0,
                                "clicks": t.get("clickCount") or 0, "reactions": t.get("likeCount") or 0,
                                "comments": t.get("commentCount") or 0, "shares": t.get("shareCount") or 0}
        return out


_resolved = {}


def resolve(url):
    """Follow a lnkd.in short link to its destination. Other URLs are returned as they are."""
    if "lnkd.in" not in url:
        return url
    if url not in _resolved:
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
            _resolved[url] = urllib.request.urlopen(req, timeout=15).geturl()
        except Exception:  # noqa: BLE001 - an unresolved link just means the post is not counted as a blog reshare
            _resolved[url] = url
    return _resolved[url]


def post_text(p):
    return (p.get("commentary") or "") + " " + json.dumps(p.get("content") or {})


def classify(p):
    """Return 'newsletter', 'webinar', 'blog_reshare' or None (out of scope)."""
    content = p.get("content") or {}
    ref = ((content.get("reference") or {}).get("id") or "")
    text = (p.get("commentary") or "").lower()
    if ref.startswith("urn:li:linkedInArticle") or "dev digest" in text or "newsletter" in text:
        return "newsletter"
    if ref.startswith(("urn:li:liveVideo", "urn:li:event")) or any(w in text for w in WEBINAR_WORDS):
        return "webinar"
    for u in re.findall(r"https?://[^\s\"\\)\]]+", post_text(p)):
        if urllib.parse.urlparse(resolve(u)).netloc == "blog.postman.com":
            return "blog_reshare"
    return None


def title_of(p):
    art = (p.get("content") or {}).get("article") or {}
    return (art.get("title") or (p.get("commentary") or "")[:80]).strip().replace("\n", " ")


def scoped(li, posts, lo, hi, history_from, live_posts):
    """Per-type statistics for in-scope organic posts published between lo and hi (ISO dates)."""
    available = history_from is not None and history_from <= hi
    out = {"start": lo, "end": hi, "available": available, "complete": bool(history_from and history_from <= lo),
           "coverage_from": history_from, "types": {}, "out_of_scope_organic_posts": 0}
    if not available:
        return out
    mine = [p for p in posts if lo <= p["_day"] <= hi]
    typed = {}
    for p in mine:
        k = classify(p)
        if k:
            typed.setdefault(k, []).append(p)
        else:
            out["out_of_scope_organic_posts"] += 1
    for u in live_posts:  # each LinkedIn Live event's announcement post counts as a webinar post
        if lo <= u["day"] <= hi and not any(p["id"] == u["urn"] for p in typed.get("webinar", [])):
            typed.setdefault("webinar", []).append({"id": u["urn"], "_day": u["day"], "commentary": u["name"], "content": {}})
    stats = li.post_stats([p["id"] for ps in typed.values() for p in ps])
    for kind, ps in typed.items():
        total = {k: 0 for k in STAT_KEYS}
        rows = []
        for p in ps:
            s = stats.get(p["id"], {})
            for k in STAT_KEYS:
                total[k] += s.get(k, 0)
            rows.append({"day": p["_day"], "title": title_of(p), "impressions": s.get("impressions"), "reactions": s.get("reactions"),
                         "comments": s.get("comments"), "have_stats": bool(s)})
        rows.sort(key=lambda r: -(r["impressions"] or 0))
        out["types"][kind] = dict(total, posts=len(ps), top=rows[:5], titles=[r["title"] for r in rows])
    return out


def main():
    q.load_settings_env()
    cur, prev = q.periods(sys.argv[1], sys.argv[2])
    li = LI()
    s, b = li.get(f"/rest/networkSizes/{li.enc}", "edgeType=COMPANY_FOLLOWED_BY_MEMBER")
    if s != 200:
        sys.exit(f"LinkedIn token rejected (HTTP {s}); run linkedin-oauth-setup.py. {str(b)[:160]}")
    q.log("LinkedIn: events")
    events, seen = [], set()
    for e in li.paged("/rest/events", f"q=eventsByOrganizer&organizer={li.enc}", page=50):
        if not e.get("startsAt"):
            continue
        name = next(iter(((e.get("name") or {}).get("localized") or {"": "?"}).values()))
        day = datetime.datetime.fromtimestamp(e["startsAt"] / 1000, datetime.timezone.utc).date().isoformat()
        fmt = next(iter((((e.get("type") or {}).get("online") or {}).get("format") or {}).keys()), None) or next(iter((e.get("type") or {}).keys()), "other")
        if (day, name) in seen:  # the API lists some events twice
            continue
        seen.add((day, name))
        events.append({"date": day, "name": name, "format": fmt, "id": e["id"]})
    live_posts = []
    for e in events:
        if prev[0].isoformat() <= e["date"] <= cur[1].isoformat() and e["format"] == "liveVideo":
            s2, b2 = li.get(f"/rest/events/{e['id']}")
            if s2 == 200 and b2.get("ugcPost"):
                live_posts.append({"urn": b2["ugcPost"], "day": e["date"], "name": e["name"]})
    q.log("LinkedIn: posts")
    posts, start = [], 0
    while start < MAX_POSTS:
        s, b = li.get("/rest/posts", f"author={li.enc}&q=author&count=100&start={start}&sortBy=LAST_MODIFIED")
        if s != 200:
            sys.exit(f"LinkedIn posts failed: HTTP {s} {str(b)[:160]}")
        els = b.get("elements", [])
        for p in els:
            p["_day"] = datetime.datetime.fromtimestamp(p["publishedAt"] / 1000, datetime.timezone.utc).date().isoformat()
        posts += els
        start += len(els)
        if not els:
            break
    organic = [p for p in posts if (p.get("distribution") or {}).get("feedDistribution") != "NONE"]
    history_from = min((p["_day"] for p in organic), default=None)
    q.log(f"LinkedIn: {len(organic)} organic posts from {history_from}")
    c = scoped(li, organic, cur[0].isoformat(), cur[1].isoformat(), history_from, live_posts)
    p = scoped(li, organic, prev[0].isoformat(), prev[1].isoformat(), history_from, live_posts)
    for per in (c, p):
        evs = [e for e in events if per["start"] <= e["date"] <= per["end"]]
        per["events"] = {"total": len(evs), "linkedin_live": sum(1 for e in evs if e["format"] == "liveVideo"),
                         "external": sum(1 for e in evs if e["format"] == "external"), "in_person": sum(1 for e in evs if e["format"] == "inPerson")}
        per["live_events"] = [{"date": e["date"], "name": e["name"]} for e in evs if e["format"] == "liveVideo"]
    json.dump({
        "current": c, "previous": p, "organic_history_from": history_from, "organic_posts_listed": len(organic),
        "not_available": "Event registrants and attendees, live viewer counts, newsletter subscribers and article views are not returned by the LinkedIn API.",
        "note": "Scoped to organic reshared blog posts, newsletter editions and webinars. Page-wide totals, ads and other posts are excluded. "
                "LinkedIn lists organic posts only from when the social agent began posting, so earlier periods are unavailable, not zero.",
    }, sys.stdout)


if __name__ == "__main__":
    main()
