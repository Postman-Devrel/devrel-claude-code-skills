#!/usr/bin/env python3
"""Find the next available publish slot using Tue/Thu-first priority, respecting embargo dates."""
from datetime import date, timedelta

# Expects: today_date (date), POST_ID (int), EMBARGO_DATE (date|None),
#          wp_get (callable), us_public_holidays (callable)

holidays = us_public_holidays(today_date.year)
two_weeks_out = today_date + timedelta(weeks=2)
if two_weeks_out.year != today_date.year:
    holidays |= us_public_holidays(two_weeks_out.year)

earliest = today_date + timedelta(days=1)
if EMBARGO_DATE and EMBARGO_DATE > earliest:
    earliest = EMBARGO_DATE


def slot_available(candidate):
    cand_str = candidate.isoformat()
    if cand_str in holidays:
        return False
    url = f"posts?status=future&after={cand_str}T00:00:00&before={cand_str}T23:59:59&per_page=10"
    existing = wp_get(url)
    return not [p for p in existing if p["id"] != POST_ID]


target = None

# Step 1: Available Tue/Thu in next 2 weeks
candidate = earliest
while candidate <= two_weeks_out:
    if candidate.weekday() in (1, 3) and slot_available(candidate):
        target = candidate
        break
    candidate += timedelta(days=1)

# Step 2: All Tue/Thu booked — try Mon/Wed in next 2 weeks
if not target:
    candidate = earliest
    while candidate <= two_weeks_out:
        if candidate.weekday() in (0, 2) and slot_available(candidate):
            target = candidate
            break
        candidate += timedelta(days=1)

# Step 3: Nothing in 2 weeks — search beyond with [Tue, Thu, Wed, Mon] priority
if not target:
    priority_days = [1, 3, 2, 0]
    check_from = two_weeks_out + timedelta(days=1)
    week_start = check_from - timedelta(days=check_from.weekday())
    while not target:
        if week_start.year != today_date.year:
            holidays |= us_public_holidays(week_start.year)
        for weekday in priority_days:
            candidate = week_start + timedelta(days=weekday)
            if candidate >= check_from and slot_available(candidate):
                target = candidate
                break
        if not target:
            week_start += timedelta(weeks=1)

if EMBARGO_DATE:
    print(f"Next available date (after embargo {EMBARGO_DATE}): {target.strftime('%A, %B %d, %Y')}")
else:
    print(f"Next available date: {target.strftime('%A, %B %d, %Y')}")

# target is now the resolved date — use it as TARGET_DATE in the validation step
