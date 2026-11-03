#!/usr/bin/env python3
"""Mailchimp newsletter metrics for qbr-metrics.

Usage: pull-mailchimp.py START END   (YYYY-MM-DD). Prints JSON to stdout.

Read-only, Mailchimp Marketing API v3. Needs MAILCHIMP_API_KEY (ends in the data center, for example -us20).
Optional scope settings:
  MAILCHIMP_AUDIENCE_ID       only campaigns sent to this audience (default: every audience)
  MAILCHIMP_TITLE_CONTAINS    only campaigns whose title or subject contains this text (case-insensitive)
  MAILCHIMP_MIN_RECIPIENTS    campaigns sent to fewer recipients are treated as tests and skipped (default 100)

Open rates are inflated by Apple Mail Privacy Protection, so lead with clicks. Mailchimp history is complete, so
a period with no sends is a real zero. Audience growth history is not used because the API returns no usable
subscriber history for this account; only the current audience size is reported.
"""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402


class MC:
    def __init__(self):
        key = os.environ.get("MAILCHIMP_API_KEY", "")
        if "-" not in key:
            sys.exit("MAILCHIMP_API_KEY is required (the key ends in the data center, for example -us20)")
        self.base = f"https://{key.rsplit('-', 1)[1]}.api.mailchimp.com/3.0"
        self.h = {"Authorization": "Basic " + base64.b64encode(f"qbr:{key}".encode()).decode(), "Accept": "application/json"}

    def get(self, path, **params):
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        s, b = q.http_json(self.base + path + (("?" + qs) if qs else ""), self.h, retries=2)
        if s != 200:
            sys.exit(f"Mailchimp {path} failed: HTTP {s} {str(b)[:200]}")
        return b


def window(mc, start, end, audience, contains, min_recipients):
    params = {"count": 200, "status": "sent", "sort_field": "send_time", "sort_dir": "ASC",
              "since_send_time": f"{start}T00:00:00%2B00:00", "before_send_time": f"{end}T23:59:59%2B00:00",
              "fields": "campaigns.id,campaigns.settings.title,campaigns.settings.subject_line,campaigns.send_time,campaigns.emails_sent,campaigns.recipients.list_id,campaigns.recipients.list_name"}
    if audience:
        params["list_id"] = audience
    camps = mc.get("/campaigns", **params).get("campaigns", [])
    rows, skipped = [], 0
    for c in camps:
        text = ((c["settings"].get("title") or "") + " " + (c["settings"].get("subject_line") or "")).lower()
        if (c.get("emails_sent") or 0) < min_recipients or (contains and contains.lower() not in text):
            skipped += 1
            continue
        r = mc.get(f"/reports/{c['id']}", fields="emails_sent,opens.unique_opens,opens.open_rate,clicks.unique_subscriber_clicks,clicks.click_rate,unsubscribed,bounces.hard_bounces,bounces.soft_bounces,send_time,subject_line")
        rows.append({"date": r["send_time"][:10], "subject": r["subject_line"], "audience": c["recipients"].get("list_name"),
                     "sent": r["emails_sent"], "unique_opens": r["opens"]["unique_opens"], "open_rate_pct": round(r["opens"]["open_rate"] * 100, 1),
                     "unique_clickers": r["clicks"]["unique_subscriber_clicks"], "click_rate_pct": round(r["clicks"]["click_rate"] * 100, 1),
                     "unsubscribed": r["unsubscribed"], "bounces": r["bounces"]["hard_bounces"] + r["bounces"]["soft_bounces"]})
    sent = sum(r["sent"] for r in rows)
    opens = sum(r["unique_opens"] for r in rows)
    clicks = sum(r["unique_clickers"] for r in rows)
    return {"start": str(start), "end": str(end), "newsletters": len(rows), "tests_or_out_of_scope_skipped": skipped, "recipients": sent,
            "unique_opens": opens, "unique_clickers": clicks, "unsubscribed": sum(r["unsubscribed"] for r in rows), "bounces": sum(r["bounces"] for r in rows),
            "open_rate_pct": round(opens / sent * 100, 1) if sent else None, "click_rate_pct": round(clicks / sent * 100, 1) if sent else None,
            "campaigns": rows}


def main():
    q.load_settings_env()
    cur, prev = q.periods(sys.argv[1], sys.argv[2])
    mc = MC()
    audience = os.environ.get("MAILCHIMP_AUDIENCE_ID") or None
    contains = os.environ.get("MAILCHIMP_TITLE_CONTAINS") or None
    min_recipients = int(os.environ.get("MAILCHIMP_MIN_RECIPIENTS", "100"))
    lists = mc.get("/lists", count=50, fields="lists.id,lists.name,lists.stats.member_count,lists.stats.unsubscribe_count").get("lists", [])
    scoped = [l for l in lists if not audience or l["id"] == audience]
    c, p = (window(mc, a, b, audience, contains, min_recipients) for a, b in (cur, prev))
    json.dump({
        "audiences": [{"name": l["name"], "members": l["stats"]["member_count"]} for l in scoped],
        "audience_members_now": sum(l["stats"]["member_count"] for l in scoped),
        "current": c, "previous": p,
        "change": {k: q.pct_change(c[k], p[k]) for k in ("newsletters", "recipients", "unique_opens", "unique_clickers", "unsubscribed")},
        "scope": {"audience_id": audience, "title_contains": contains, "min_recipients": min_recipients},
        "note": "Open rates are inflated by Apple Mail Privacy Protection; clicks are more reliable. Campaigns under the minimum recipient count are treated as tests.",
    }, sys.stdout)


if __name__ == "__main__":
    main()
