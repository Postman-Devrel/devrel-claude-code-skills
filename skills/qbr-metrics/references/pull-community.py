#!/usr/bin/env python3
"""Owned community metrics for qbr-metrics, from the Postman community dashboard MCP (Discord).

Usage: pull-community.py START END   (YYYY-MM-DD). Prints JSON to stdout.

Needs COMMUNITY_MCP_API_TOKEN (bearer token for https://www.postman-community-dashboard.dev/api/mcp). The server
speaks MCP over HTTP (JSON-RPC); this script calls its get_monthly_report tool once per month.

The dashboard reports whole calendar months, so a period is covered by the months that sit fully inside it. A fiscal
quarter or a calendar month works; a week or a custom range with no whole month is reported as not available.
Flows (joins, leaves, help topics, replies, event roles) are summed over the months. Stocks (total members) are taken at
the end of the last month. Active members is the average of the monthly counts.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

URL = os.environ.get("COMMUNITY_MCP_URL", "https://www.postman-community-dashboard.dev/api/mcp")


def call(token, name, args):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": args}}).encode()
    req = urllib.request.Request(URL, body, {"Authorization": "Bearer " + token, "Content-Type": "application/json",
                                             "Accept": "application/json, text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Community MCP returned HTTP {e.code}: {e.read().decode(errors='replace')[:200]}")
    res = out.get("result") or {}
    if "error" in out or res.get("isError"):
        sys.exit(f"Community MCP {name} failed: {str(out.get('error') or res)[:200]}")
    return json.loads(res["content"][0]["text"])


def whole_months(start, end):
    """YYYY-MM strings for the calendar months that lie fully inside start..end."""
    out, cur = [], date(start.year, start.month, 1)
    while cur <= end:
        nxt = date(cur.year + (cur.month == 12), cur.month % 12 + 1, 1)
        if cur >= start and nxt - timedelta(days=1) <= end:
            out.append(f"{cur.year}-{cur.month:02d}")
        cur = nxt
    return out


def window(token, start, end):
    months = whole_months(start, end)
    if not months:
        return None
    rows = []
    for m in months:
        rep = call(token, "get_monthly_report", {"month": m})["report"]
        if not rep.get("hasData"):
            sys.exit(f"Community MCP has no data for {m}")
        rows.append((m, rep))
    s = lambda f: sum(f(r) for _, r in rows)  # noqa: E731
    last = rows[-1][1]
    topics, answered = s(lambda r: r["helpForum"]["newTopics"]), s(lambda r: r["helpForum"]["topicsAnswered"])
    active = [r["engagement"]["activeMembers"] for _, r in rows]
    members_end = last["signups"]["totalMembers"]
    joins, leaves = s(lambda r: r["signups"]["joins"]), s(lambda r: r["retention"]["leaves"])
    lift = [r.get("liftoff") or {} for _, r in rows]
    cohort, started, done = (sum(x.get(k, 0) for x in lift) for k in ("cohortSize", "usersStarted", "usersCompleted"))
    return {
        "start": str(start), "end": str(end), "months": months,
        "joins": joins, "leaves": leaves, "net_members": joins - leaves, "members_end": members_end,
        "active_members_avg": round(sum(active) / len(active), 1),
        "active_rate_pct": round(sum(active) / len(active) / members_end * 100, 2),
        "help_topics": topics, "topics_answered": answered,
        "answer_rate_pct": round(answered / topics * 100, 1) if topics else None,
        "replies_on_topics": s(lambda r: r["helpForum"]["repliesOnNewTopics"]),
        "staff_bot_replies": s(lambda r: r["helpForum"]["staffAndBotResponses"]),
        "event_roles_granted": s(lambda r: r["eventAttendees"]["rolesGrantedInMonth"]),
        "event_role_holders": last["eventAttendees"]["totalWithRole"],
        "retention_pct": round(sum(r["retention"]["retentionRate"] for _, r in rows) / len(rows) * 100, 2),
        "liftoff_cohort": cohort, "liftoff_started": started, "liftoff_completed": done,
        "liftoff_start_rate_pct": round(started / cohort * 100, 1) if cohort else None,
        "monthly": [{"month": m, "joins": r["signups"]["joins"], "leaves": r["retention"]["leaves"], "active": r["engagement"]["activeMembers"],
                     "topics": r["helpForum"]["newTopics"], "members": r["signups"]["totalMembers"], "event_roles": r["eventAttendees"]["rolesGrantedInMonth"]}
                    for m, r in rows],
    }


def main():
    q.load_settings_env()
    token = os.environ.get("COMMUNITY_MCP_API_TOKEN")
    if not token:
        sys.exit("COMMUNITY_MCP_API_TOKEN is required")
    cur, prev = q.periods(sys.argv[1], sys.argv[2])
    c, p = window(token, *cur), window(token, *prev)
    if not c:
        sys.exit("The community dashboard reports whole calendar months; this period has no whole month. Use a month or a fiscal quarter.")
    if not p:
        sys.exit("The previous period has no whole calendar month, so there is nothing to compare with.")
    keys = ("joins", "leaves", "net_members", "members_end", "active_members_avg", "active_rate_pct", "help_topics", "answer_rate_pct",
            "replies_on_topics", "staff_bot_replies", "event_roles_granted", "retention_pct", "liftoff_cohort", "liftoff_started")
    json.dump({"current": c, "previous": p,
               "change": {k: q.pct_change(c[k], p[k]) for k in keys},
               "note": "Discord community, whole calendar months from the community dashboard MCP. Sums for flows, month-end for total members, average for active members."},
              sys.stdout)


if __name__ == "__main__":
    main()
