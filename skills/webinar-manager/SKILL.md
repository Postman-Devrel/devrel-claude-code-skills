---
name: webinar-manager
description: "Run a developer webinar end to end: create or update the Luma event, file the Jira social-promo-card request for the creative team, write the promotional email and Twitter/X + LinkedIn posts from the webinar brief, track status, and report Luma + Riverside metrics after the stream. Every Luma or Jira write is shown and approved first. Email and social copy are local drafts only."
argument-hint: "new <title/brief> | luma [--dry-run] | jira | email | promo [--card <path>] | status | metrics <slug> [riverside-export-path]"
allowed-tools: ["Bash", "Read", "Write", "Edit", "mcp__atlassian__searchJiraIssuesUsingJql", "mcp__atlassian__getJiraIssue", "mcp__atlassian__createJiraIssue", "mcp__atlassian__lookupJiraAccountId", "mcp__atlassian__getJiraIssueTypeMetaWithFields"]
---

# Webinar Manager

One skill, one brief, every stage of a developer webinar. Webinars stream on Riverside and are registered through the Postman Dev Events Luma calendar.

| Stage | What it does | Writes to |
|-------|--------------|-----------|
| `new` | Collects the brief, then runs `luma`, `jira`, `email`, `promo` in order | local files, Luma, Jira |
| `luma` | Creates or updates the Luma event (diff shown first) | Luma |
| `jira` | Files the parent webinar task and the "Social Promo Card" sub-task | Jira (`MKTG`) |
| `email` | Drafts the promotional email | `email.md` |
| `promo` | Drafts Twitter/X and LinkedIn posts that use the promo card | `posts.md` |
| `status` | Shows stage progress and the promo card ticket status | nothing |
| `metrics` | Merges Luma stats with a Riverside export | `metrics.md` |

Nothing is ever posted or sent by this skill. Talia posts to Twitter/X and LinkedIn and sends the email herself.

## Hard rules

1. **Approval before every external write.** Before any Luma create/update or Jira create, show exactly what will change and wait for an explicit "yes". `luma-webinar.py` also refuses to write unless `--apply` is passed.
2. **New Luma events are created private.** Making one public is a separate request.
3. **No invented facts.** Speakers, dates, titles, and claims come from the brief. If a field is missing, ask once and save the answer to `brief.md`.
4. **Copy rules** (email, posts, Jira text): no "supercharge", "unlock", "revolutionize", or "leverage"; no em dashes anywhere; code blocks carry language identifiers; developer advocate voice, conversational and specific.
5. **UTM tags on Luma links in copy:** `?utm_source=twitter`, `?utm_source=linkedin`, or `?utm_source=email` by channel.
6. **Credentials come from the environment only.** Never write keys into files or print them.

## Configuration

- `LUMA_API_KEY` in `.claude/settings.json` under `env` (key with write access to the Postman Dev Events calendar). Check with `[ -n "$LUMA_API_KEY" ] && echo set`. Do not echo the value.
- Jira goes through the Atlassian MCP (`mcp__atlassian__*`), site `postmanlabs.atlassian.net`. If the tools are unavailable, tell the user to connect the Atlassian MCP and stop the Jira stage.
- Luma calendar: `cal-TGqTNpY4iyl7XYe`.

## Files and state

```text
webinar-output/
  .webinar-state.json         # per-webinar state, see below
  {slug}/
    brief.md                  # the saved brief
    luma-payload.json         # last payload sent or proposed to Luma
    email.md
    posts.md
    metrics.md
```

`{slug}` is the title lowercased with hyphens plus the date, for example `fabric-gateway-webinar-261020` (`YYMMDD`).

State file shape:

```json
{
  "fabric-gateway-webinar-261020": {
    "title": "Fabric Gateway Webinar",
    "date": "2026-10-20",
    "luma_api_id": "evt-...",
    "luma_url": "https://luma.com/...",
    "jira_parent": "MKTG-11048",
    "jira_card": "MKTG-11062",
    "card_path": null,
    "stages": {"luma": false, "jira": false, "email": false, "promo": false, "metrics": false}
  }
}
```

Read the state file at the start of every stage. If it does not exist, create it. Update it after each stage succeeds.

## The brief

Required fields. Ask once for anything missing, then save to `webinar-output/{slug}/brief.md`:

- Title, date, start time, timezone, duration
- Speakers: name, title, headshot file path or link
- Abstract (2 to 4 sentences) and 3 key takeaways
- Riverside stream or join link
- Related content: blog posts, docs, collections, earlier webinars
- Existing Luma event id (`evt-...`) if the event already exists. The Luma manage URL `https://luma.com/event/manage/evt-XXXX` contains it.

## Stage: `new`

1. Collect the brief and slug. Save `brief.md` and a state entry.
2. Run `luma`, then `jira`, then `email`, then `promo`, pausing at each approval gate.
3. Finish with the `status` view.

## Stage: `luma [--dry-run]`

Helper: `references/luma-webinar.py`. Copy it to the scratchpad (not `/tmp` if a scratchpad directory is available) and run it with `python3`.

**Existing event** (state has `luma_api_id` or the user gave `evt-...`):

1. `python3 luma-webinar.py get {evt}` and read the current event.
2. Build `luma-payload.json` containing only the fields that should change, from the brief: `name`, `description_md`, `start_at` and `end_at` (UTC ISO8601 from date, time, timezone), `timezone`, and the Riverside stream link in `meeting_url`. A fetched event with no location returns `location_type: "missing"` and `meeting_url: null`, so expect to set both. The event may already be public: report `visibility` in the diff summary and never change it as part of an update.
3. `python3 luma-webinar.py update {evt} luma-payload.json` prints the field-by-field diff and writes nothing.
4. Show the diff. If the user approves and `--dry-run` was not requested, rerun with `--apply`.

**New event:**

1. Build the payload with these fields: `name`, `visibility: "private"`, `slug`, `calendar_api_id`, `start_at`, `end_at`, `timezone`, `duration_interval`, `description`, `description_md`, `waitlist_status: "enabled"`, `tags` (plain strings, for example `["webinar", "developer", "api", "ai"]`), `registration_questions` (`label`, `required`, `question_type: "short_answer"`; no `id` field), and `feedback_email` (`enabled: true`, `delay: "P0Y0M0DT0H45M0S"`). Add the online location fields for a webinar; confirm the `location_type` value and meeting URL field name against Luma's API docs on the first run, because this repo has only created in-person events so far.
2. `python3 luma-webinar.py create luma-payload.json` prints the payload without writing. Show it.
3. On approval, rerun with `--apply`. Print the full response and check for rejected fields. On a slug conflict, append `-2`, `-3`, and retry.
4. Fetch the new event with `get` and `update` (diff, then `--apply`) for any field that was dropped on create.

Description copy comes from the brief abstract and takeaways. Save the event `api_id` and URL to the state file and set `stages.luma` to true.

## Stage: `jira`

Reuse what the team already does: a parent task `[Webinar] {title} {M/D}` under epic `MKTG-8442` (Technical Content), with a sub-task `Social Promo Card` labeled `creative`, assigned to the creative designer. Templates are in `references/templates.md`.

1. **Look for existing tickets first.** Run `searchJiraIssuesUsingJql` with `project = MKTG AND summary ~ "{distinctive title words}" ORDER BY created DESC` and also `parent = {key}` for sub-tasks. Request only the fields you need (`summary`, `status`, `parent`, `assignee`, `duedate`, `labels`) to keep results small. If a matching `[Webinar]` task or `Social Promo Card` sub-task exists, link it in state and do not create a duplicate.
2. **Create what is missing.** Fetch field metadata with `getJiraIssueTypeMetaWithFields` for `Task` and `Sub-task` in `MKTG` if you are unsure of required fields. Find the assignee with `lookupJiraAccountId` (default: Jonathan Holt; ask if the user wants someone else). Show the full ticket text, assignee, and due date, wait for approval, then `createJiraIssue`.
3. Save the keys to state as `jira_parent` and `jira_card`, set `stages.jira` to true.
4. **Re-check on every run.** For an existing `jira_card`, fetch its status. The Atlassian MCP cannot download attachments, so when the status is Done tell the user to download the finished card, then run `promo --card {path}` so the agent knows where it is.

## Stage: `email`

1. Read `brief.md`. Search `blog-output/` (and `blog-output/.prod-update-memory.json` if present) for posts related to the topic and add them to related content only when they actually exist.
2. Write `webinar-output/{slug}/email.md` using the email skeleton in `references/templates.md`: 3 subject lines, preview text, body, one CTA to the Luma link with `?utm_source=email`.
3. Run the copy-rule check (below) and fix any hit before reporting.

## Stage: `promo [--card <path>]`

1. Read `brief.md` and state. If `--card` is given, verify the file exists and store it as `card_path`.
2. Write `webinar-output/{slug}/posts.md` using the Twitter/X and LinkedIn skeletons: announce, reminder (one week out), and day-of for each channel, plus one Twitter/X thread option.
3. Each post names the card file on a `Card:` line. If `card_path` is null, write `Card: card pending` and tell the user the card ticket must be Done first.
4. Include a posting schedule suggestion based on the webinar date. Do not post anything.
5. Run the copy-rule check and fix any hit.

## Stage: `status`

For each webinar in state (or the one named), print: stage checklist, Luma link, Jira keys, the live status of `jira_card`, card path, and the next action. Read-only.

## Stage: `metrics <slug> [riverside-export-path]`

1. **Luma:** `python3 luma-webinar.py stats {evt}` returns registered, waitlisted, checked in, and attendance rate. If the event has not happened yet, say so and stop.
2. **Riverside:** read the export the user provides (CSV, PDF, or pasted numbers). Riverside metrics to extract: peak concurrent viewers, unique viewers, average watch time, replay views, and Q&A or chat message count. If no export was provided, ask for one; if the user has none, fill the Luma section and mark every Riverside value `not provided`. Never estimate a Riverside number.
3. Write `webinar-output/{slug}/metrics.md` from the metrics skeleton in `references/templates.md`. Note when Luma check-ins and Riverside viewers differ and why the two measure different things.
4. Set `stages.metrics` to true and print the report summary.

## Copy-rule check

Run before reporting `email` or `promo` complete:

```bash
grep -nEi "supercharge|unlock|revolutionize|leverage|—" webinar-output/{slug}/email.md webinar-output/{slug}/posts.md
```

Any output is a failure. Rewrite those lines and rerun until the command prints nothing.

## Final report

After any stage, print a short summary: what changed, where the files are, what needs the user's action next (approve a diff, post the drafts, supply the card or the Riverside export).
