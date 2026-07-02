---
name: luma-stats
description: "Pull event statistics from the Postman Dev Events Luma calendar — registrations, waitlist, attendee count, and engagement score per event. Supports filtering by MMM-YY (e.g. Apr-26), YYYY (e.g. 2026), or blank for all time. Shows sum totals across all matching events."
argument-hint: "[MMM-YY | YYYY] (optional, e.g. 'Apr-26' or '2026' — blank for all time)"
allowed-tools: ["Bash", "Write"]
---

# Luma Event Stats

Pull registration, waitlist, attendance, and engagement data for all events on the [Postman Dev Events](https://luma.com/postman-dev-events) Luma calendar. Useful for measuring event program health, spotting trends, and reporting on community growth.

## How the data is fetched

The Luma Public API v1 does not include guest counts directly on event objects. Stats are derived by paging through dedicated endpoints:

- **Registered** — guests with `approval_status == "approved"` (from `event/get-guests`)
- **Waitlisted** — guests with `approval_status == "waitlisted"` or `"pending"` (from `event/get-guests`)
- **Attended** — guests where `checked_in_at` is not null (from `event/get-guests`)
- **Score** — `(attended ÷ registered) × 5.0`, shown as `x.x/5.0`
Progress is printed to stderr as each event is processed.

---

## Configuration

This skill requires a Luma API key with read access to the calendar.

### Setup

1. **Get your Luma API key:**
   - Log in to [lu.ma](https://lu.ma) as a calendar admin
   - Go to **Settings → Integrations → API**
   - Create a new API key with read permissions

2. **Set the environment variable** in `.claude/settings.json`:
   ```json
   {
     "env": {
       "LUMA_API_KEY": "your-luma-api-key"
     }
   }
   ```

---

## Process

### Step 1: Verify API key

Check that `LUMA_API_KEY` is set. If it is not present, stop and tell the user to set the environment variable as described above.

```bash
echo $LUMA_API_KEY
```

### Step 2: Write and run the data-fetch script

Read `references/luma-stats.py`, write it to `/tmp/luma-stats.py`, then execute it.

```bash
python3 /tmp/luma-stats.py [filter-arg]  # e.g. "Apr-26", "2026", or omit for all time
```

Capture the JSON from stdout. Progress messages go to stderr and can be ignored.

---

### Step 3: Render the report

From the JSON output, produce a clean markdown report and display it in the chat immediately.

```
## Luma Event Stats — Postman Developer Events
**Filter:** {filter}  |  **Events:** {N}

| Date | Event | Registered | Waitlisted | Attended | Score |
|------|-------|-----------|-----------|---------|-------|
| 15 Apr 2026 | NYC Meetup | 142 | 23 | 98 | 3.4/5.0 |
| 03 Apr 2026 | London Meetup | 87 | 0 | 71 | 4.1/5.0 |
| **TOTAL** | **{N} events** | **{sum}** | **{sum}** | **{sum}** | **{score}/5.0** |

**Score** = (checked-in ÷ registered) × 5.0. Future events show `—` until check-in data is recorded.
```

- Sort events newest-first
- Append `%` to score values
- Show `—` for score when registered = 0
- Bold the TOTAL row

### Step 4: Save to file

Save the same report to `luma-output/` — create the directory if it doesn't exist.

Filename pattern:
- All time → `luma-output/luma-stats-all-time.md`
- Year → `luma-output/luma-stats-2026.md`
- Month → `luma-output/luma-stats-Apr-26.md`

Append a **Notes** section at the bottom of the file:
```markdown
---
*Generated: {today's date} | Calendar: https://luma.com/postman-dev-events*
*Score = checked-in ÷ registered × 100. Future events show 0 attended until check-in data is recorded.*
*Subscriber count not available via Luma Public API v1.*
```

---

## Score Metric

Score = `(checked-in ÷ registered) × 5.0`, displayed as `x.x/5.0`.

| Score | Interpretation |
|-------|---------------|
| 4.0–5.0 | Excellent turnout |
| 3.0–3.9 | Good — typical for in-person tech meetups |
| 2.0–2.9 | Below average — consider venue, timing, or topic |
| < 2.0 | Low — flag for review |
| — | No registrations, or future event with no check-in data yet |

---

## Error Handling

| Error | Action |
|-------|--------|
| `LUMA_API_KEY` not set | Stop. Show setup instructions above. |
| HTTP 403 Cloudflare block | The User-Agent header is required — verify it is present in `HEADERS`. |
| HTTP 401 Unauthorized | API key is invalid or expired. Ask user to regenerate in Luma Settings → Integrations → API. |
| Zero events returned | Check that the filter format is correct (e.g. `Apr-26` not `April-26`). Print the parsed filter value. |
| All counts are 0 | Future events have no check-ins yet — this is expected. Past events with 0 attended may not have used Luma check-in. |
