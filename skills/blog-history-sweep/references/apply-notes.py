#!/usr/bin/env python3
"""Prepend an editor's note to the posts checked in a sweep review file.

Usage:
  python3 apply-notes.py --review sweep-output/sweep-x-YYMMDD.md \
      --note-file notes/x.html --note-id x --backup-dir sweep-output/backups/x-YYMMDD [--dry-run]
  python3 apply-notes.py --restore sweep-output/backups/x-YYMMDD [--ids 123,456]

Every post's raw content is backed up before it is changed. Only `content` is
written, so publish date, status, slug, and SEO fields are untouched.
"""
import argparse, base64, glob, json, os, re, sys, urllib.request

WP_BASE = "https://blog.postman.com/wp-json/wp/v2"


def headers():
    u, p = os.environ.get("WP_USERNAME"), os.environ.get("WP_APP_PASSWORD")
    if not u or not p:
        sys.exit("ERROR: WP_USERNAME and WP_APP_PASSWORD must be set")
    auth = base64.b64encode(f"{u}:{p}".encode()).decode()
    return {"Authorization": f"Basic {auth}", "User-Agent": "PostmanDevRelDashboard/1.0",
            "Content-Type": "application/json"}


def wp(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{WP_BASE}{path}", data=data, headers=headers(), method=method)
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def checked_ids(review_path):
    ids = []
    for line in open(review_path):
        m = re.match(r"^- \[[xX]\] .*?· ID (\d+) ·", line)
        if m:
            ids.append(int(m.group(1)))
    return ids


def apply(args):
    note = open(args.note_file).read().strip()
    marker = f"<!-- editor-note:{args.note_id} -->"
    block = f"<!-- wp:html -->\n{marker}\n{note}\n<!-- /wp:html -->\n\n"
    ids = checked_ids(args.review)
    if not ids:
        sys.exit("No checked posts in review file.")
    if not args.dry_run:
        os.makedirs(args.backup_dir, exist_ok=True)
    results = []
    for pid in ids:
        post = wp("GET", f"/posts/{pid}?context=edit&_fields=id,title,link,status,content")
        raw = post["content"]["raw"]
        title = post["title"]["raw"]
        if marker in raw:
            results.append({"id": pid, "title": title, "result": "skipped (note already present)"})
            continue
        if args.dry_run:
            results.append({"id": pid, "title": title, "result": "would update"})
            continue
        with open(os.path.join(args.backup_dir, f"{pid}.json"), "w") as f:
            json.dump({"id": pid, "title": title, "link": post["link"], "content_raw": raw}, f, indent=2)
        wp("POST", f"/posts/{pid}", {"content": block + raw})
        results.append({"id": pid, "title": title, "link": post["link"], "result": "updated"})
    print(json.dumps(results, indent=2))


def restore(args):
    only = {int(i) for i in args.ids.split(",")} if args.ids else None
    results = []
    for path in sorted(glob.glob(os.path.join(args.restore, "*.json"))):
        b = json.load(open(path))
        if only and b["id"] not in only:
            continue
        wp("POST", f"/posts/{b['id']}", {"content": b["content_raw"]})
        results.append({"id": b["id"], "title": b["title"], "result": "restored"})
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--note-file")
    ap.add_argument("--note-id")
    ap.add_argument("--backup-dir")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--restore", help="backup dir to restore from")
    ap.add_argument("--ids", help="with --restore: comma-separated post IDs")
    a = ap.parse_args()
    if a.restore:
        restore(a)
    elif a.review and a.note_file and a.note_id and a.backup_dir:
        apply(a)
    else:
        ap.error("need --review, --note-file, --note-id, --backup-dir (or --restore)")
