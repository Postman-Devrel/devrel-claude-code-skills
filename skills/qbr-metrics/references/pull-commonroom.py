#!/usr/bin/env python3
"""Common Room metrics for qbr-metrics, computed from three segments via the `cr` CLI.

Usage: pull-commonroom.py START END   (YYYY-MM-DD). Prints JSON to stdout.

Segments hold CURRENT members, not members at a point in time, so counts are
as of today. Period-over-period change comes from the previous snapshot in
snapshots.json (created or updated on each run). With no snapshot, change is n/a.

Metrics:
  developers influenced      contacts in s_4163088 (Event - All - Attended)
  organizations influenced   distinct companies among contacts in s_4342069 (Tier 1 ... Attended)
  economic buyer %           contacts in s_4163088 AND s_4196221, divided by s_4163088
  accounts influenced        distinct companies among contacts in s_4163088 (company from the contact's
                             current employer; only contacts with a known company count)
  tier 1 share               Tier 1 companies divided by accounts influenced
  industry breakdown         accounts influenced grouped by the employer's industry label
  sentiment                  not available (Room Overview is a UI report with no API)
"""
import json
import os
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

ATTENDED, ECON, TIER1 = "s_4163088", "s_4196221", "s_4342069"
SNAPSHOTS = os.path.join(os.path.dirname(__file__), "snapshots.json")


def seg_filter(*ids):
    return json.dumps({"type": "and", "clauses": [
        {"type": "stringListFilter", "field": "memberSegmentId", "params": {"op": "any", "value": [i]}}
        for i in ids]})


def enumerate_contacts(ids, cols):
    """Yield every contact record in the AND of the given segments."""
    cursor = None
    while True:
        cmd = ["cr", "contact", "list", "--json", "--limit", "1000", "--filter", seg_filter(*ids)]
        for c in cols:
            cmd += ["--col", c]
        if cursor:
            cmd += ["--cursor", cursor]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            sys.exit(f"cr failed: {proc.stderr[:300] or proc.stdout[:300]}")
        body = json.loads(proc.stdout)
        yield from body.get("records", [])
        cursor = body.get("nextCursor")
        if not cursor:
            return


def company_key(rec):
    cc = rec.get("currentCompany") or {}
    key = (cc.get("domain") or rec.get("companyWebsite") or cc.get("companyName") or rec.get("companyName") or "")
    return key.strip().lower() or None


def org_details(rec):
    cc = rec.get("currentCompany") or {}
    return company_key(rec), ((cc.get("industry") or {}).get("subIndustry"))


def load_snapshots():
    try:
        with open(SNAPSHOTS) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def main():
    q.load_settings_env()
    if not os.environ.get("COMMONROOM_API_TOKEN"):
        sys.exit("COMMONROOM_API_TOKEN is required")
    start, end = sys.argv[1], sys.argv[2]
    q.log("Common Room: enumerating attendees with company and industry ...")
    attended, orgs_all, org_industry, with_company = 0, {}, {}, 0
    for rec in enumerate_contacts([ATTENDED], ["id", "currentCompany", "companyName", "companyWebsite"]):
        attended += 1
        key, label = org_details(rec)
        if key:
            with_company += 1
            orgs_all.setdefault(key, label)
            if label and not orgs_all[key]:
                orgs_all[key] = label
    q.log(f"  attended={attended}; counting attendees who are economic buyers ...")
    econ_attended = sum(1 for _ in enumerate_contacts([ATTENDED, ECON], ["id"]))
    q.log(f"  economic buyers among attendees={econ_attended}; enumerating Tier 1 contacts ...")
    tier1_contacts, orgs = 0, set()
    for rec in enumerate_contacts([TIER1], ["id", "currentCompany", "companyName", "companyWebsite"]):
        tier1_contacts += 1
        key = company_key(rec)
        if key:
            orgs.add(key)
    tier1_orgs = orgs & set(orgs_all) if orgs_all else set()
    by_group, raw_labels = {}, {}
    for key, label in orgs_all.items():
        by_group[q.industry_group(label)] = by_group.get(q.industry_group(label), 0) + 1
        if label:
            raw_labels[label] = raw_labels.get(label, 0) + 1
    metrics = {
        "accounts_influenced": len(orgs_all),
        "contacts_with_known_company": with_company,
        "company_coverage_pct": round(with_company / attended * 100, 1) if attended else None,
        "tier1_accounts": len(orgs),
        "tier1_accounts_found_among_attendee_accounts": len(tier1_orgs),
        "tier1_share_of_accounts_pct": round(len(orgs) / len(orgs_all) * 100, 1) if orgs_all else None,
        "industry_breakdown": dict(sorted(by_group.items(), key=lambda kv: -kv[1])),
        "industry_top_labels": dict(sorted(raw_labels.items(), key=lambda kv: -kv[1])[:12]),
        "industry_labels": dict(sorted(raw_labels.items(), key=lambda kv: -kv[1])[:300]),
        "developers_influenced": attended,
        "organizations_influenced_tier1": len(orgs),
        "tier1_contacts": tier1_contacts,
        "economic_buyers_among_attendees": econ_attended,
        "economic_buyer_pct": round(econ_attended / attended * 100, 1) if attended else None,
    }
    snaps = load_snapshots()
    key = f"{start}_{end}"
    prior = [(k, v) for k, v in snaps.items() if k.split("_")[1] < start] if snaps else []
    prior.sort(key=lambda kv: kv[0].split("_")[1])
    previous = prior[-1][1] if prior else None
    change = {}
    if previous:
        for k in ("developers_influenced", "accounts_influenced", "organizations_influenced_tier1", "economic_buyer_pct"):
            change[k] = q.pct_change(metrics[k], previous["metrics"].get(k))
    snaps[key] = {"taken": date.today().isoformat(), "metrics": metrics}
    with open(SNAPSHOTS, "w") as f:
        json.dump(snaps, f, indent=2)
    json.dump({
        "as_of": date.today().isoformat(), "metrics": metrics,
        "previous_snapshot": {"key": prior[-1][0], "metrics": previous["metrics"]} if previous else None,
        "change": change,
        "sentiment": "not available (Room Overview is a UI report; the API has no aggregate)",
        "note": "Segments hold current members, so these counts are as of today, not as of the period end.",
    }, sys.stdout)


if __name__ == "__main__":
    main()
