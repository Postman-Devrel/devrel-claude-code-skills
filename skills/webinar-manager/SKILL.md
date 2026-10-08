---
name: webinar-manager
description: "Run a developer webinar end to end: create or update the Luma event, file the Jira social-promo-card request for the creative team, write the promotional email and Twitter/X + LinkedIn posts from the webinar brief, track status, and report Luma + Riverside metrics after the stream. Every Luma or Jira write is shown and approved first. Email and social copy are local drafts that the user approves and then posts or sends."
argument-hint: "new <title/brief> | luma [--dry-run] | jira | stream | email | promo [--card <path>] | status | metrics <slug> [riverside-export-path]"
allowed-tools: ["Bash", "Read", "Write", "Edit", "WebSearch", "WebFetch", "mcp__atlassian__searchJiraIssuesUsingJql", "mcp__atlassian__getJiraIssue", "mcp__atlassian__createJiraIssue", "mcp__atlassian__lookupJiraAccountId", "mcp__atlassian__getJiraIssueTypeMetaWithFields"]
---

# Webinar Manager

One skill, one brief, every stage of a developer webinar. Webinars are produced in Riverside and streamed live to a YouTube Live event and a LinkedIn Live event, which is where attendees watch. Registration goes through the Postman Dev Events Luma calendar.

| Stage | What it does | Writes to |
|-------|--------------|-----------|
| `new` | Collects the brief, then runs `luma`, `jira`, `stream`, `email`, `promo` in order | local files, Luma, Jira |
| `luma` | Creates or updates the Luma event (diff shown first) | Luma |
| `jira` | Files the parent webinar task and the "Social Promo Card" sub-task | Jira (`MKTG`) |
| `stream` | Prepares the YouTube Live and LinkedIn Live event details and the Riverside setup steps, records both viewing links, then updates the Luma event location | `stream.md`, Luma (after approval) |
| `email` | Fetches the promo card and writes a full promotional email (hook, problem, takeaways, speakers, logistics, related blog posts and YouTube videos, CTA), then asks for approval | `email.md` |
| `promo` | Fetches the promo card, writes a one-sentence promo and the LinkedIn and Twitter/X drafts, then asks for approval | `posts.md` |
| `status` | Shows stage progress and the promo card ticket status | nothing |
| `metrics` | Merges Luma stats with a Riverside export | `metrics.md` |

Nothing is ever posted or sent by this skill. The email and each social draft end with an approval question; an approval marks the draft final in the file and the user posts to Twitter/X and LinkedIn and sends the email themselves.

## Hard rules

1. **Approval before every external write.** Before any Luma create/update or Jira create, show exactly what will change and wait for an explicit "yes". `luma-webinar.py` also refuses to write unless `--apply` is passed.
2. **New Luma events are always created private.** After the event and host are confirmed, always ask the user whether to make it public. Only change `visibility` after an explicit "yes", and show the change first like any other Luma write. Never change visibility on an existing event during an `update`.
3. **No invented facts.** Speakers, dates, titles, and claims come from the brief. If a field is missing, ask once and save the answer to `brief.md`.
4. **Copy rules** (email, posts, Jira text): no "supercharge", "unlock", "revolutionize", or "leverage"; no em dashes anywhere; code blocks carry language identifiers; developer advocate voice, conversational and specific.
5. **UTM tags on Luma links in copy:** `?utm_source=twitter`, `?utm_source=linkedin`, or `?utm_source=email` by channel.
6. **Credentials come from the environment only.** Never write keys into files or print them.
7. **The host is always Talia Kohan** (`talia.kohan@postman.com`), on every webinar, regardless of who the speakers are. The Luma API key belongs to another user (Quinton Wall), so events it creates are owned by that user and Talia must be added as a host explicitly. Do this on every `luma` run, new or existing, using the `add-host` helper command (dry run first, `--apply` after approval, like any other Luma write). The Jira description and Luma description list Talia as host.

## Configuration

- `LUMA_API_KEY` in `.claude/settings.json` under `env` (key with write access to the Postman Dev Events calendar). Check with `[ -n "$LUMA_API_KEY" ] && echo set`. Do not echo the value.
- Jira goes through the Atlassian MCP (`mcp__atlassian__*`), site `postmanlabs.atlassian.net`. If the tools are unavailable, tell the user to connect the Atlassian MCP and stop the Jira stage.
- `JIRA_EMAIL` and `JIRA_API_TOKEN` in `.claude/settings.json` under `env`, used only to download the promo card attachment (`references/jira-card.py`, read-only). Create the token at https://id.atlassian.com/manage-profile/security/api-tokens. Check with `[ -n "$JIRA_API_TOKEN" ] && echo set`. If they are missing, tell the user how to add them and fall back to asking for a local card path (`promo --card <path>`).
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
    "youtube_live_url": null,
    "linkedin_live_url": null,
    "jira_parent": "MKTG-11048",
    "jira_card": "MKTG-11062",
    "card_path": null,
    "stages": {"luma": false, "jira": false, "stream": false, "email": false, "promo": false, "metrics": false}
  }
}
```

Read the state file at the start of every stage. If it does not exist, create it. Update it after each stage succeeds.

## The brief

Required fields, saved to `webinar-output/{slug}/brief.md`:

- Title, date, start time, timezone, duration
- Speakers: name, title, headshot file path or link
- Abstract (2 to 4 sentences) and 3 key takeaways
- Riverside studio link for the speakers (may be blank)
- YouTube Live and LinkedIn Live viewing links (usually blank at the start: the `stream` stage prepares both events and asks for the links afterward)
- Related content: blog posts, docs, collections, earlier webinars (may be blank)
- Existing Luma event id (`evt-...`) if the event already exists, or "none". The Luma manage URL `https://luma.com/event/manage/evt-XXXX` contains it.

**Ask for the whole brief up front.** When `new` starts, send one message that lists every field above, numbered, and wait for the reply. Do not read state, build a slug, write files, or call Luma/Jira until the reply arrives. Use any fields the user already gave in the command arguments (for example the title) and list only the rest. After the reply, if a required field is still missing, ask for those fields in one follow-up. Only the join link and related content may be blank, and only if the user says so explicitly. Never fill a missing field with a guess or placeholder unless the user asks for placeholder or test values.

## Stage: `new`

1. Ask for the full brief (see "The brief") and wait. Nothing is created before every required field is answered.
2. Save `brief.md`, the slug, and a state entry.
3. Run `luma`, then `jira`, then `stream`, then `email`, then `promo`, pausing at each approval gate.
4. Finish with the `status` view.

## Stage: `luma [--dry-run]`

Helper: `references/luma-webinar.py`. Copy it to the scratchpad (not `/tmp` if a scratchpad directory is available) and run it with `python3`.

**Existing event** (state has `luma_api_id` or the user gave `evt-...`):

1. `python3 luma-webinar.py get {evt}` and read the current event.
2. Build `luma-payload.json` containing only the fields that should change, from the brief: `name`, `description_md`, `start_at` and `end_at` (UTC ISO8601 from date, time, timezone), `timezone`. Do not set `meeting_url` here unless `youtube_live_url` is already in state: the `stream` stage sets it. A fetched event with no location returns `location_type: "missing"` and `meeting_url: null`, so expect that until `stream` has run. The event may already be public: report `visibility` in the diff summary and never change it as part of an update.
3. `python3 luma-webinar.py update {evt} luma-payload.json` prints the field-by-field diff and writes nothing.
4. Show the diff. If the user approves and `--dry-run` was not requested, rerun with `--apply`.

**New event:**

1. Build the payload with these fields: `name`, `visibility: "private"`, `slug`, `calendar_api_id`, `start_at`, `end_at`, `timezone`, `duration_interval`, `description`, `description_md`, `waitlist_status: "enabled"`, `tags` (plain strings, for example `["webinar", "developer", "api", "ai"]`), `registration_questions` (`label`, `required`, `question_type: "short_answer"`; no `id` field), and `feedback_email` (`enabled: true`, `delay: "P0Y0M0DT0H45M0S"`). Add the online location fields for a webinar; confirm the `location_type` value and meeting URL field name against Luma's API docs on the first run, because this repo has only created in-person events so far.
2. `python3 luma-webinar.py create luma-payload.json` prints the payload without writing. Show it.
3. On approval, rerun with `--apply`. Print the full response and check for rejected fields. On a slug conflict, append `-2`, `-3`, and retry.
4. Fetch the new event with `get` and `update` (diff, then `--apply`) for any field that was dropped on create.

Description copy comes from the brief abstract and takeaways. Save the event `api_id` and URL to the state file and set `stages.luma` to true.

**Host (every run):** `python3 luma-webinar.py add-host {evt} talia.kohan@postman.com "Talia Kohan"` shows what it would send. After approval, rerun with `--apply`. A successful call returns `{}` with HTTP 200. `get` does not return a hosts field, so the API cannot confirm it: tell the user to check the host list on the event's Luma manage page. If Luma rejects the call, say so and tell the user to add Talia as host in the Luma UI. Do not mark `stages.luma` complete until the call succeeded or the user acknowledges the manual step.

**Visibility (new events only):** after the host step, ask "The event is private. Make it public?" If yes, send `{"visibility": "public"}` through `update` (diff first, then `--apply`). If no, leave it private and note that in the final report.

## Stage: `jira`

Reuse what the team already does: a parent task `[Webinar] {title} {M/D}` under epic `MKTG-8442` (Technical Content), with a sub-task `Social Promo Card` labeled `creative`, assigned to the creative designer. Templates are in `references/templates.md`.

1. **Look for existing tickets first.** Run `searchJiraIssuesUsingJql` with `project = MKTG AND summary ~ "{distinctive title words}" ORDER BY created DESC` and also `parent = {key}` for sub-tasks. Request only the fields you need (`summary`, `status`, `parent`, `assignee`, `duedate`, `labels`) to keep results small. If a matching `[Webinar]` task or `Social Promo Card` sub-task exists, link it in state and do not create a duplicate.
2. **Create what is missing.** Fetch field metadata with `getJiraIssueTypeMetaWithFields` for `Task` and `Sub-task` in `MKTG` if you are unsure of required fields. The Social Promo Card sub-task is always assigned to Jonathan Holt on the Creative Team: `assignee_account_id` `712020:9cde7faf-7906-4356-9914-39bd911dac81` (jonathan.holt@postman.com) and label `creative`, which is how the Creative Team is marked on the reference ticket MKTG-11062 (it has no team field or component). Do not ask who to assign it to and do not look up another user. Only re-run `lookupJiraAccountId` if the create call rejects that id. Show the full ticket text, assignee, and due date, wait for approval, then `createJiraIssue`.
3. Save the keys to state as `jira_parent` and `jira_card`, set `stages.jira` to true.
4. **Re-check on every run.** For an existing `jira_card`, fetch its status. When it is Done, the `email` and `promo` stages download the card themselves (see "Promo card" below). The Atlassian MCP cannot download attachments, so the download uses `jira-card.py`.

## Stage: `stream`

Riverside is the production studio. Viewers watch on YouTube Live and LinkedIn Live, so both events must exist before the email and posts can link to them. Neither can be created from here: the YouTube Live API needs OAuth credentials this repo does not have, and the LinkedIn Live API is restricted to approved partners. So this stage prepares everything and the user creates the two events.

1. Read `brief.md`, state, and the promo card ("Promo card") if it exists.
2. Write `webinar-output/{slug}/stream.md` with a section for each destination, filled from the brief only:
   - **YouTube Live (scheduled broadcast):** title (the webinar title), description (abstract, takeaways, and the Luma link with `?utm_source=youtube`), scheduled start (date, time, timezone), visibility (public), thumbnail (the card, or "card pending"), and live chat on.
   - **LinkedIn Live (event):** event name, description (abstract and the Luma link with `?utm_source=linkedin`), start date and time with timezone, and the cover image (the card, or "card pending"). Host is Talia Kohan.
   - **Riverside:** the steps to add YouTube and LinkedIn as live streaming destinations in the studio, run a test stream, and send both to air together at the start time.
3. **Stream keys and RTMP URLs are secrets.** Never ask the user to paste them into the chat and never write them to a file. The user enters them directly in Riverside.
4. Show the draft and tell the user to create both events, then paste back the two viewing links (the YouTube watch URL and the LinkedIn event URL).
5. Validate each link: YouTube must be a `youtube.com` or `youtu.be` URL, LinkedIn must be a `linkedin.com` URL. Save them to the brief and to state as `youtube_live_url` and `linkedin_live_url`. A webinar may proceed with only one of the two if the user says so.
6. **Update the Luma event** (Luma approval rules apply): set `meeting_url` to the YouTube Live URL, and add a "Watch live" line to `description_md` with both links. Show the diff with `update`, then `--apply` after approval. Never change `visibility`.
7. Set `stages.stream` to true once the links are saved and the Luma update is applied or declined. Until then, `email` and `promo` say "viewing links pending" instead of a link.

## Promo card

Used by `email` and `promo` before any copy is written.

1. If `--card <path>` was given, verify it exists and store it as `card_path`.
2. Otherwise, if state has `jira_card`, run `python3 jira-card.py list {jira_card}`, then `python3 jira-card.py download {jira_card} webinar-output/{slug}/` (copy the helper to the scratchpad first). It saves the newest image attachment and prints the path; store that as `card_path` in state.
3. If the ticket has no image yet (exit code 2) or the Jira credentials are missing, set `Card: card pending`, say which of the two it is, and continue. Never invent or substitute an image.

## Promo sentence

The `promo` stage builds its posts on a one-sentence promo, and the `email` stage uses it only as a short summary line under the subject options. The email itself is a full promotional email, not this sentence (see "Stage: `email`"). The sentence is saved at the top of `posts.md` and `email.md`. It must summarize the abstract in plain words, name the date, and name the time with timezone, for example: "{what the webinar shows, from the abstract} on {Weekday, Month D} at {time} {tz}." One sentence, from the brief only, no claims that are not in the abstract.

## Approval checkpoint

After a draft file is written and passes the copy-rule check, show the full draft (and the card path) and ask: "Approve this {email|LinkedIn post|Twitter/X post}?" On approval, set `Status: approved` at the top of that section in the file and tell the user it is ready for them to post or send. On requested changes, edit the file and ask again. Never post, send, or schedule anything.

## Stage: `email`

1. Read `brief.md`. Get the promo card ("Promo card") and write the promo sentence ("Promo sentence").
2. **Find related content, newest first.** Always search these, in addition to the brief's related content:
   - **Postman blog:** `WebSearch` for `site:blog.postman.com {topic keywords}` and check `blog-output/` (and `blog-output/.prod-update-memory.json` if present). Keep posts from the last 12 months that are clearly about the webinar topic.
   - **Postman YouTube channel:** `WebSearch` for `site:youtube.com Postman {topic keywords}` and for the channel's latest uploads (`youtube.com/@Postman`, fetched with `WebFetch`). Keep videos that are clearly about the topic, newest first.
   - Include at most 3 blog posts and 3 videos. Link only URLs that were returned by the search or fetch and that match the topic. If nothing relevant turns up for one source, say so in the draft's notes and leave that source out. Never guess a URL or a video title.
3. **Think the email through before writing it.** This is a promotional email a developer reads in under a minute, not a one-line announcement. Work out, from the brief only: the specific problem or situation the audience recognizes; why this topic matters now; what attendees will be able to do after the session (one concrete outcome per takeaway); who it is for; what happens live (demo, walkthrough, Q&A) and why the speakers are the right people. Pull in the related posts and videos from step 2 where they genuinely add background. If the brief does not support a claim, leave the claim out.
4. Write `webinar-output/{slug}/email.md` using the email skeleton in `references/templates.md`: 3 subject lines, preview text, a hook, the problem, what the session covers with one short paragraph per takeaway, who it is for, the speakers with a line each, the logistics block (with the YouTube Live and LinkedIn Live viewing links from state, or "viewing links pending" if `stream` has not run), the related reading and videos list from step 2, one CTA to the Luma link with `?utm_source=email`, and a recording note. Target 250 to 400 words in the body, scannable, with short paragraphs.
5. Run the copy-rule check (below) and fix any hit.
6. Reread the draft as the recipient: every paragraph must say something specific to this webinar. Cut filler and any sentence that would fit any webinar. Then run the approval checkpoint for the email.

## Stage: `promo [--card <path>]`

1. Read `brief.md` and state. Get the promo card ("Promo card") and write the promo sentence ("Promo sentence").
2. Write `webinar-output/{slug}/posts.md` using the Twitter/X and LinkedIn skeletons: the promo sentence, one LinkedIn post, and one Twitter/X post, each built on the promo sentence and each naming the card file. Draft the reminder (one week out), day-of, and Twitter/X thread posts only if the user asks for them.
3. Each post names the card file on a `Card:` line. If `card_path` is null, write `Card: card pending` and tell the user why (ticket not Done, no image attached, or Jira credentials missing).
4. Include a posting schedule suggestion based on the webinar date.
5. Run the copy-rule check and fix any hit.
6. Run the approval checkpoint once for LinkedIn and once for Twitter/X.

## Stage: `status`

For each webinar in state (or the one named), print: stage checklist, Luma link, YouTube Live and LinkedIn Live links, Jira keys, the live status of `jira_card`, card path, and the next action. Read-only.

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
