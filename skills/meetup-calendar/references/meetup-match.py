#!/usr/bin/env python3
import sys, json, re, difflib
from datetime import datetime

def normalize(s):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', '', s.lower())).strip()

def parse_date(raw):
    if not raw:
        return None
    raw = raw.strip().replace("Z", "+00:00")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z",
                "%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y",
                "%b %d, %Y", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(raw[:len(fmt)+4], fmt).date()
        except Exception:
            pass
    try:
        return datetime.fromisoformat(raw).date()
    except Exception:
        return None

def name_score(a, b):
    return difflib.SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def date_close(d1, d2, days=14):
    return bool(d1 and d2 and abs((d1 - d2).days) <= days)

def col_letter(idx):
    result = ""
    while idx >= 0:
        result = chr(idx % 26 + ord('A')) + result
        idx = idx // 26 - 1
    return result

with open('/tmp/sheet-data.json') as f:
    sheet_input = json.load(f)
with open('/tmp/luma-events.json') as f:
    luma_events = json.load(f)

rows = sheet_input["rows"]
luma_col_idx = sheet_input["luma_col_idx"]

for ev in luma_events:
    ev["date"] = parse_date(ev.get("start_at", ""))

matches, unmatched_luma, skipped = [], list(luma_events), 0

for row in rows:
    if row.get("existing_luma_url"):
        skipped += 1
        continue
    sheet_name = row.get("name", "").strip()
    if not sheet_name:
        continue
    sheet_date = parse_date(row.get("date_raw", ""))
    best_score, best_luma = 0, None
    for lev in luma_events:
        ns = name_score(sheet_name, lev.get("name", ""))
        dc = date_close(sheet_date, lev.get("date"))
        if (ns >= 0.70 and dc) or ns >= 0.88:
            score = ns + (0.15 if dc else 0)
            if score > best_score:
                best_score, best_luma = score, lev
    if best_luma:
        matches.append({
            "sheet_row": row["sheet_row"], "sheet_name": sheet_name,
            "luma_name": best_luma["name"], "luma_url": best_luma["url"],
            "col_letter": col_letter(luma_col_idx), "score": round(best_score, 3),
        })
        unmatched_luma = [e for e in unmatched_luma if e["url"] != best_luma["url"]]
    else:
        row["no_match"] = True

unmatched_sheet = [r for r in rows if r.get("no_match") and not r.get("existing_luma_url") and r.get("name")]

print(json.dumps({
    "matches": matches,
    "unmatched_luma": [{"name": e["name"], "url": e["url"]} for e in unmatched_luma],
    "unmatched_sheet": [{"sheet_row": r["sheet_row"], "name": r["name"], "date_raw": r.get("date_raw","")} for r in unmatched_sheet],
    "skipped_already_filled": skipped,
    "col_letter": col_letter(luma_col_idx),
}))
