---
name: cfp-tracker
description: >-
  Manage the team's Call-for-Papers (CFP) submissions on the Confluence "Team CFP
  Tracker" page. Use whenever the user wants to add, update, delete, or archive a
  CFP, change a submission's status (planned / submitted / accepted / rejected /
  waitlisted / withdrawn), record a CFP response or event date, import CFPs
  discovered by cfp-hunter as "planned" to submit to, or asks "what CFPs are open",
  "which talks did we submit", "track these CFPs I want to submit to", "mark the AXA
  talk accepted", "archive last year's events". Confluence is the single source of
  truth — there is no spreadsheet.
---

# CFP Tracker

Manages the team's conference CFP submissions. The **Confluence page is the single
source of truth**; every action reads and writes that page directly via the
Atlassian connector. There is no Google Sheet.

## Target page

- Cloud / site: `postmanlabs.atlassian.net`
- Page ID: `8268251220`
- Space: `DE` (Developer Evangelism)
- Title: `Team CFP Tracker`

Always fetch the page first with `getConfluencePage` (contentFormat `html`) so you
edit the current body, then write back with `updateConfluencePage` (contentFormat
`html`). Preserve any `data-local-id` attributes on existing nodes. Use a clear
`versionMessage` describing the change.

> Note: if the page is still an unpublished draft, updates keep it a draft — the
> user must click **Publish** in Confluence once. First-time publish cannot be done
> through the API.

## Column contract

The "Active submissions" table has exactly these columns, in order:

1. **Talk Title** — proposed session title.
2. **Event** — conference / event name.
3. **Location** — city, country, or "Virtual".
4. **Lead** — internal owner driving the submission.
5. **Speaker(s)** — team member(s) presenting. May be more than one; separate
   multiple names with commas (e.g. "Anthony Viard, Pooja Mistry").
6. **Duration** — e.g. "30 min".
7. **CFP Deadline** — submission cutoff. Use `<time datetime="YYYY-MM-DD">`.
8. **CFP Response Date** — when the organizer replied; "Pending" until then.
9. **Event Date** — when the event runs. Use `<time>`; ranges shown as "3–5 Nov 2026".
10. **Status** — one of the values below, as a Confluence status chip.
11. **Links** — `<a>` links, typically "CFP" (Sessionize/form) and "Abstract"
    (Confluence abstract page), separated by " · ".

### Status values (and chip colors)

- **Planned** — `data-color="purple"` — discovered CFP the team intends to submit
  to, but has not submitted yet (e.g. imported from `cfp-hunter`)
- **Submitted** — `data-color="blue"` — awaiting decision
- **Accepted** — `data-color="green"` — confirmed
- **Rejected** — `data-color="red"` — declined
- **Waitlisted** — `data-color="yellow"` — on hold
- **Withdrawn** — `data-color="neutral"` — pulled by speaker

Status chip HTML: `<span data-type="status" data-color="blue">Submitted</span>`.

Lifecycle: a CFP typically starts as **Planned** (we want to speak there), moves to
**Submitted** once the abstract is sent, then to a decided value
(Accepted / Rejected / Waitlisted) or **Withdrawn**.

## Identity & duplicate handling

A submission is uniquely identified by **Event name + Event year + Talk Title**
(case-insensitive, trimmed). This is deliberate:

- The same talk can be submitted to **multiple events** — different Event, so not a
  duplicate.
- One event can host **multiple talks** — different Talk Title, so not a duplicate.
- A recurring conference in a **different year** (e.g. "DevBcn 2025" vs "DevBcn
  2026") is **not** a duplicate — the year is part of the key. Derive the year from
  the Event name, the CFP deadline, or the event date; if none is available, ask.

**Before adding any CFP** — whether typed manually or imported from cfp-hunter —
check the active table for a row with the same key. If a match exists, **do not
silently add or silently skip**. Tell the user it already exists (show the matching
row) and ask which they want:

- **Update** — apply the new details to the existing row (see the `update` action), or
- **Skip** — leave the existing row unchanged.

Only append a brand-new `<tr>` when no matching row exists. When importing several
CFPs at once, resolve each match individually and summarize update/skip/added counts
at the end.

## Archived CFPs

Archived rows (past events or finally-decided CFPs moved to the "Archived" section)
are **not tracked as active**. By default:

- Reads / listings ("what CFPs are open", "which talks did we submit") show only the
  **active** table and exclude the Archived section — unless the user explicitly
  asks (e.g. "include archived", "show last year's events").
- The cfp-hunter import skips any discovered CFP whose deadline has already passed,
  and never adds into the Archived section, unless the user explicitly asks to track
  a closed/archived one.
- Duplicate checks match against the **active** table only; an archived row does not
  block re-adding an event that has come around again.

## Actions

### add
Add a new CFP as a row in the "Active submissions" table.
1. Gather: title, event, location, lead, speaker(s), duration, CFP deadline, event
   date, status (default **Submitted**), and any links. If the user gives a
   Sessionize/CFP URL, fetch it for event date, location, and deadline. If they
   give a Confluence abstract URL, fetch it for the title and use it as the
   Abstract link. Do not invent missing values — leave CFP Response Date as
   "Pending" and ask only if a required field is truly unknown.
2. Run the duplicate check (Event + year + Talk Title, see "Identity & duplicate
   handling"). If a matching active row exists, offer update-or-skip instead of
   appending.
3. Append a new `<tr>` following the column contract.
4. Recompute the Summary counts.

### add from cfp-hunter results
Import CFPs the `cfp-hunter` skill discovered into the tracker as **Planned** rows.
This is the handoff for "I ran the hunter, now track these so we can plan to
submit."

1. Read the hunter output at `cfp-output/current-cfps.md` (relative to the repo /
   working directory). If it is missing, tell the user to run
   `/devrel-skills:cfp-hunter` first.
2. Show the discovered events and let the user pick which to add (by number, event
   name, or "all"). **Do not auto-add everything** — the user chooses.
3. For each chosen event, map the hunter columns to the column contract:
   - Event → **Event**
   - Location → **Location**
   - CFP Closes → **CFP Deadline** (`<time datetime="YYYY-MM-DD">`)
   - CFP Link → **Links** (as the "CFP" link)
   - Summary → context only; not a stored column (may inform the abstract later)
   - **Status** → **Planned** (`data-color="purple"`)
   - **CFP Response Date** → "Pending"
   - **Talk Title**, **Lead**, **Speaker(s)**, **Duration**, **Event Date** → leave
     as "TBD" (a discovered CFP has no talk/owner yet). Ask only if the user offers
     the info; do not block the import on it.
4. Skip any discovered CFP whose deadline has already passed (do not import
   closed/archived CFPs unless the user explicitly asks).
5. For each chosen event, run the duplicate check (Event + year + Talk Title, see
   "Identity & duplicate handling"). If a matching active row already exists, ask the
   user whether to **update** it or **skip** it — don't silently skip and don't
   create a second row.
6. Append one `<tr>` per newly-added event, and summarize added / updated / skipped
   counts. Recompute the Summary counts.

### update
Change fields on an existing CFP (most often Status or CFP Response Date).
1. Identify the row by talk title + event (confirm with the user if ambiguous).
2. Edit only the requested cells. When setting Status to a decided value
   (Accepted/Rejected/Waitlisted), also set CFP Response Date to that date (ask if
   not given).
3. Recompute the Summary counts.

### delete
Remove a CFP row entirely. Deletion is destructive, so **always confirm** the
specific row with the user before removing it. Deleting the wrong entry loses data.
After removal, recompute the Summary counts.

### archive
Move a CFP out of "Active submissions" into the "Archived" section — used for past
events or finally-decided CFPs the user wants out of the active view.
1. Identify the row, confirm.
2. Remove it from the active table and add it under the "Archived" heading (a
   compact table or bullet with title, event, event date, final status).
3. Recompute the Summary counts (archived rows are not counted as active).

## After every write

- Update the "Last updated" date in the info panel to today.
- Recompute Summary counts to match the active table.
- Report back to the user exactly what changed (which row, which fields).
- Never touch other Confluence pages. Only edit page `8268251220`.
