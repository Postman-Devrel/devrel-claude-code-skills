#!/usr/bin/env python3
"""Write scheduled/published/draft posts to dashboard/wp-calendar.json for the Kanban UI."""
import html, os, json

# Expects: today (datetime), scheduled (list), published (list), drafts (list)
# All sourced from wp_get() calls in the list subcommand steps (with _embed=author).


def _author_name(p):
    embedded_author = p.get("_embedded", {}).get("author", [])
    if embedded_author:
        return embedded_author[0].get("name", "Unknown")
    return "Unknown"


calendar_data = {
    "updated_at": today.isoformat(),
    "scheduled": [
        {
            "id": p["id"],
            "title": html.unescape(p["title"]["rendered"]),
            "date": p["date"],
            "status": "future",
            "link": p.get("link", ""),
            "edit_link": f"https://blog.postman.com/wp-admin/post.php?post={p['id']}&action=edit",
            "author": _author_name(p),
        }
        for p in scheduled
    ],
    "published": [
        {
            "id": p["id"],
            "title": html.unescape(p["title"]["rendered"]),
            "date": p["date"],
            "status": "publish",
            "link": p.get("link", ""),
            "edit_link": f"https://blog.postman.com/wp-admin/post.php?post={p['id']}&action=edit",
            "author": _author_name(p),
        }
        for p in published
    ],
    "drafts": [
        {
            "id": p["id"],
            "title": html.unescape(p["title"]["rendered"]),
            "modified": p["modified"],
            "status": "draft",
            "link": p.get("link", ""),
            "edit_link": f"https://blog.postman.com/wp-admin/post.php?post={p['id']}&action=edit",
            "author": _author_name(p),
        }
        for p in drafts
    ],
}

calendar_path = os.path.join(os.environ.get("CLAUDE_PLUGIN_ROOT", ""), "dashboard", "wp-calendar.json")
if not os.environ.get("CLAUDE_PLUGIN_ROOT"):
    calendar_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "dashboard", "wp-calendar.json")

os.makedirs(os.path.dirname(calendar_path), exist_ok=True)
with open(calendar_path, "w") as f:
    json.dump(calendar_data, f, indent=2)

print(f"Dashboard calendar updated: {len(calendar_data['scheduled'])} scheduled, "
      f"{len(calendar_data['published'])} published, {len(calendar_data['drafts'])} drafts")
