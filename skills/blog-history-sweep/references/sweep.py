#!/usr/bin/env python3
"""Sweep published posts on blog.postman.com for keywords and flag the ones
that mention them without referencing current content.

Usage:
  python3 sweep.py --keywords "Postman MCP,Claude Code plugin" \
      --markers "github.com/postmanlabs/postman-plugin" --exclude "Astropods" \
      --note-id postman-plugin-update --note-file notes/postman-plugin-update.html \
      --out-dir sweep-output [--since 2024-01-01] [--label postman-plugin]

Writes:
  {out-dir}/sweep-{label}-YYMMDD.json  full results (every matching post)
  {out-dir}/sweep-{label}-YYMMDD.md    reviewable checklist (flagged posts pre-checked)
"""
import argparse, base64, html, json, os, re, sys, time, urllib.parse, urllib.request
from datetime import datetime

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"
NEAR_CHARS = 120  # ~20 words either side of a context keyword


def auth_headers():
    username = os.environ.get("WP_USERNAME")
    app_password = os.environ.get("WP_APP_PASSWORD")
    if not username or not app_password:
        sys.exit("ERROR: WP_USERNAME and WP_APP_PASSWORD must be set")
    auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
    return {"Authorization": f"Basic {auth}", "User-Agent": "PostmanDevRelDashboard/1.0"}


def get_json(url, headers):
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=headers)
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except urllib.error.HTTPError as e:
            if e.code == 400 and "rest_post_invalid_page_number" in e.read().decode():
                return []
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 1:
                raise
            time.sleep(2)


def search_posts(keyword, since, headers):
    """WordPress search matches title + content, word-based (not phrase)."""
    posts, page = [], 1
    while True:
        params = {
            "search": keyword,
            "status": "publish",
            "per_page": 100,
            "page": page,
            "_fields": "id,title,link,date,content",
        }
        if since:
            params["after"] = f"{since}T00:00:00"
        batch = get_json(f"{WP_BASE}/posts?{urllib.parse.urlencode(params)}", headers)
        posts.extend(batch)
        if len(batch) < 100:
            return posts
        page += 1


def strip_tags(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def phrase_regex(phrase):
    # Flexible whitespace/hyphen between words, optional possessive ("Postman’s MCP"),
    # case-insensitive, word-bounded
    parts = [re.escape(p) for p in re.split(r"[\s\-]+", phrase.strip()) if p]
    return re.compile(r"\b" + r"(?:['’]s)?[\s\-]+".join(parts) + r"\b", re.I)


def snippets(text, regexes, limit=3, width=110):
    out, seen = [], []
    for rx in regexes:
        for m in rx.finditer(text):
            if any(abs(m.start() - s) < width for s in seen):
                continue
            seen.append(m.start())
            a, b = max(0, m.start() - width), min(len(text), m.end() + width)
            snip = text[a:m.start()] + "**" + m.group(0) + "**" + text[m.end():b]
            out.append(("…" if a else "") + snip + ("…" if b < len(text) else ""))
            if len(out) >= limit:
                return out
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keywords", required=True, help="comma-separated phrases")
    ap.add_argument("--context-keywords", default="",
                    help="comma-separated phrases that only count when a --near term is within ~20 words")
    ap.add_argument("--near", default="", help="comma-separated context terms for --context-keywords")
    ap.add_argument("--exclude", default="", help="comma-separated phrases; posts matching any are excluded")
    ap.add_argument("--markers", default="", help="comma-separated strings that mean the post is already current")
    ap.add_argument("--note-id", required=True)
    ap.add_argument("--note-file", help="note HTML, used to detect notes added by hand")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--since", help="only posts published on/after YYYY-MM-DD")
    ap.add_argument("--label", help="filename label (defaults to note id)")
    args = ap.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    markers = [m.strip().lower() for m in args.markers.split(",") if m.strip()]
    kw_rx = {k: phrase_regex(k) for k in keywords}
    ctx_keywords = [k.strip() for k in args.context_keywords.split(",") if k.strip()]
    near_rx = [phrase_regex(n.strip()) for n in args.near.split(",") if n.strip()]
    if ctx_keywords and not near_rx:
        sys.exit("ERROR: --context-keywords needs --near terms")
    ctx_rx = {k: phrase_regex(k) for k in ctx_keywords}
    excludes = [e.strip() for e in args.exclude.split(",") if e.strip()]
    ex_rx = {e: phrase_regex(e) for e in excludes}
    note_marker = f"editor-note:{args.note_id}"
    note_text = ""
    if args.note_file:
        note_text = strip_tags(open(args.note_file).read()).lower()[:80]

    headers = auth_headers()
    found = {}
    for kw in keywords + ctx_keywords:
        results = search_posts(kw, args.since, headers)
        print(f"  search '{kw}': {len(results)} candidate posts", file=sys.stderr)
        for p in results:
            found.setdefault(p["id"], p)

    rows = []
    for p in found.values():
        body = p["content"]["rendered"]
        title = html.unescape(p["title"]["rendered"])
        text = strip_tags(body)
        haystack = f"{title} {text}"
        matched = [k for k, rx in kw_rx.items() if rx.search(haystack)]
        ctx_windows = []
        for k, rx in ctx_rx.items():
            hits = []
            for m in rx.finditer(haystack):
                window = haystack[max(0, m.start() - NEAR_CHARS):m.end() + NEAR_CHARS]
                if any(n.search(window) for n in near_rx):
                    hits.append(window)
            if hits:
                matched.append(k)
                ctx_windows += hits
        if not matched:
            continue  # WP word search hit, but no actual phrase match
        hit_excludes = [e for e, rx in ex_rx.items() if rx.search(haystack)]
        lower = body.lower()
        has_note = note_marker in lower or (note_text and note_text in text.lower())
        hit_markers = [m for m in markers if m in lower]
        status = ("excluded" if hit_excludes else "noted" if has_note
                  else "current" if hit_markers else "flagged")
        rows.append({
            "id": p["id"],
            "title": title,
            "link": p["link"],
            "date": p["date"][:10],
            "matched": matched,
            "markers_found": hit_markers,
            "excludes_found": hit_excludes,
            "status": status,
            "snippets": snippets(" ".join(ctx_windows) + " " + haystack,
                                 [kw_rx.get(k) or ctx_rx[k] for k in matched]),
        })

    rows.sort(key=lambda r: r["date"], reverse=True)
    os.makedirs(args.out_dir, exist_ok=True)
    stamp = datetime.now().strftime("%y%m%d")
    label = args.label or args.note_id
    base = os.path.join(args.out_dir, f"sweep-{label}-{stamp}")

    meta = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "keywords": keywords,
        "context_keywords": ctx_keywords,
        "near": [n.strip() for n in args.near.split(",") if n.strip()],
        "markers": markers,
        "excludes": excludes,
        "note_id": args.note_id,
        "note_file": args.note_file,
        "since": args.since,
    }
    with open(base + ".json", "w") as f:
        json.dump({"meta": meta, "posts": rows}, f, indent=2)

    flagged = [r for r in rows if r["status"] == "flagged"]
    current = [r for r in rows if r["status"] == "current"]
    noted = [r for r in rows if r["status"] == "noted"]
    excluded = [r for r in rows if r["status"] == "excluded"]

    md = [
        f"# Blog History Sweep — {label}",
        "",
        f"Generated {meta['generated']} · keywords: {', '.join(f'`{k}`' for k in keywords)}",
        (f"Context keywords: {', '.join(f'`{k}`' for k in ctx_keywords)} (only within ~20 words of "
         f"{', '.join(f'`{n}`' for n in meta['near'])})") if ctx_keywords else "",
        f"Current-content markers: {', '.join(f'`{m}`' for m in markers) or '_none_'}",
        f"Excluded phrases: {', '.join(f'`{e}`' for e in excludes) or '_none_'}",
        f"Editor's note: `{args.note_id}`" + (f" · since {args.since}" if args.since else ""),
        "",
        f"**{len(flagged)} flagged** · {len(current)} already current · {len(noted)} already have the note · {len(excluded)} excluded",
        "",
        "## Flagged — needs editor's note",
        "",
        "Uncheck (`- [ ]`) any post that should NOT get the note. Only checked posts are updated.",
        "",
    ]
    if not flagged:
        md.append("_No flagged posts._")
    for r in flagged:
        md.append(f"- [x] [{r['title']}]({r['link']}) · ID {r['id']} · {r['date']}")
        md.append(f"  - Matched: {', '.join(r['matched'])}")
        for s in r["snippets"]:
            md.append(f"  - > {s}")
    for heading, group in (("Already current (reference only)", current),
                           ("Already has this editor's note", noted),
                           ("Excluded (reference only)", excluded)):
        md += ["", f"## {heading}", ""]
        if not group:
            md.append("_None._")
        for r in group:
            extra = f" · markers: {', '.join(r['markers_found'])}" if r["markers_found"] else ""
            if r["excludes_found"]:
                extra += f" · excluded by: {', '.join(r['excludes_found'])}"
            md.append(f"- [{r['title']}]({r['link']}) · ID {r['id']} · {r['date']}{extra}")

    with open(base + ".md", "w") as f:
        f.write("\n".join(md) + "\n")

    print(json.dumps({
        "review_file": base + ".md",
        "results_file": base + ".json",
        "flagged": len(flagged),
        "current": len(current),
        "noted": len(noted),
        "excluded": len(excluded),
    }, indent=2))


if __name__ == "__main__":
    main()
