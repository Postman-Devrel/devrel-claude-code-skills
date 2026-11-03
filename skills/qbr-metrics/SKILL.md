---
name: qbr-metrics
description: "Quarterly business review metrics for DevRel content and community. Asks for a date range, pulls blog views (Jetpack), YouTube (long-form vs Shorts, paid vs organic, subscribers), Luma events and contacts, the meetup sheet (ratings and cost), and Common Room segments (accounts, industry), compares each against the previous period, and builds a white-background HTML report with a stoplight summary, line charts with release and news markers, topic analysis and written insights."
argument-hint: "[FY27-Q3 | 2026-09 | 2026-W41 | START END] (optional; the skill always confirms the range)"
allowed-tools: ["Bash", "Read", "Write", "Edit", "AskUserQuestion"]
---

# QBR Metrics

Pull content and community numbers for a date range, compare them with the previous period, and write a branded report. Setup, data-source details, verified limits and troubleshooting are in `QBR-METRICS-README.MD` in this folder. Read it if anything fails.

## Step 1: Ask for the date range (every run)

Always ask which period the report should cover, every run, even when arguments were passed or the period seems obvious from context. If arguments were passed, show them as the proposed range and ask the user to confirm or change it. Ask in one short question:

> What period should this report cover: a **month**, a **week**, or a **quarter**?

Periods and how each is compared:

| Period | Dates | Compared with |
|---|---|---|
| Quarter (fiscal) | Q1 Feb 1 to Apr 30, Q2 May 1 to Jul 31, Q3 Aug 1 to Oct 31, Q4 Nov 1 to Jan 31 | The prior fiscal quarter |
| Month | A calendar month | The prior calendar month |
| Week | 7 days (an ISO week runs Monday to Sunday) | The prior 7 days |
| Custom | Any two dates | The same-length window ending the day before |

The fiscal year is named for the year it ends in: FY27 is Feb 2026 to Jan 2027, so Aug 1 to Oct 31, 2026 is FY27-Q3. If the user says "Q3" with no year, confirm the fiscal year by date ("Q3 FY27, Aug 1 to Oct 31, 2026?") before running. Validate that the period has finished (the end date is not in the future) and that start is not after end.

The runner accepts: `FY27-Q3`, a month as `2026-09`, an ISO week as `2026-W41`, or two dates (`2026-08-01 2026-10-31`). Month and week reports have small samples: say so in the insights, and charts use daily points for a week.

## Step 1b: Ask how the direction will be provided

"Where we are going" is the team's own writing. Right after the date range, first run `python3 skills/qbr-metrics/references/run-qbr.py <same range> --find-previous-direction`. If it prints a path, an earlier period has a direction with text, so add a fifth option below. Then ask once how they want to provide it for this period:

1. **I already have a direction.md.** Ask for its path, and pass it to the runner as `--direction=PATH` in Step 3. The runner copies it in. If the output folder already has a direction.md with text, it keeps that as `direction.previous.md` first.
2. **Ask me section by section now.** Run the interview below before Step 3.
3. **Ask me after I have seen the report.** Default. Follow Step 5.
4. **Skip it this time.** The chapter is left out.
5. **Review last period's direction first** (only when a previous file was found). Do this before any other option:
   - Read that file and show it to the user section by section, exactly as written.
   - Ask: "How did last period's direction go? Is there anything to record about programs, targets or asks, such as done, changed or dropped?" with a "Skip" option. Record the answer word for word under `## Review of last period`, placed first in the new `direction.md`.
   - For each section that had text, ask: "Carry forward as written", "I will write a new version", or "Drop it". Carry forward means copying that section's text verbatim, with the line `Carried forward from <previous period label>.` directly under the heading so the report shows it. A new version goes through the interview question for that section. Drop leaves it empty. Never carry anything forward without that explicit choice.
   - Then continue with option 1, 2 or 3 for any sections that remain.

**The interview.** Ask these five questions, one at a time, in this exact wording, each with a "Skip this section" option; the user types their answer in the free-text field:
- Trends: "What trends are you responding to?"
- Programs and bets: "What programs or bets are you planning? Include what, who owns it, when it starts and how you will measure it, as far as you know."
- Targets: "What targets do you want for next quarter?"
- Asks and decisions: "What do you need from others, such as budget, headcount or decisions?"
- Risks and dependencies: "What risks or dependencies should be noted?"

Rules, because these are the user's words and not yours: record each answer **word for word** under its heading (`## Trends we are responding to`, `## Programs and bets`, `## Targets for next quarter`, `## Asks and decisions needed`, `## Risks and dependencies`). Do not paraphrase, summarize, correct, reorder, add or suggest content, and do not put examples or numbers from the data in the questions. Turn a typed list into bullets only if the user typed it as a list. A skipped section stays empty. Before writing, check whether `direction.md` already has text; if it does, do not overwrite it without asking, and keep the old file as `direction.previous.md`. After writing, show the saved text back and ask the user to confirm it.

## Step 2: Check credentials

Env vars come from `~/.claude/settings.json` or `.claude/settings.json`. Check names only, never print values.

| Source | Required |
|---|---|
| Blog | `WP_USERNAME`, `WP_APP_PASSWORD` (required: stop if missing) |
| YouTube | `YT_OAUTH_CLIENT_ID`, `YT_OAUTH_CLIENT_SECRET`, `YT_OAUTH_REFRESH_TOKEN` (see `references/youtube-oauth-setup.py`) |
| Luma | `LUMA_API_KEY` |
| Meetup sheet (ratings, cost) | `MEETUP_SHEET_ID`, `GOOGLE_APPLICATION_CREDENTIALS` (same service account as `meetup-calendar`) |
| Mailchimp | `MAILCHIMP_API_KEY` (optional scope: `MAILCHIMP_AUDIENCE_ID`, `MAILCHIMP_TITLE_CONTAINS`) |
| LinkedIn | `LINKEDIN_ACCESS_TOKEN`, or a token file via `LINKEDIN_TOKEN_FILE` (defaults to the agent-team-socialmedia app's state file); `LINKEDIN_AUTHOR_URN` |
| Common Room | `COMMONROOM_API_TOKEN`, and the `cr` CLI on the path |

A missing optional source is not fatal. Tell the user which will show as "not connected" and continue.

## Step 3: Run the pulls and build the report

From the repo root:

```bash
python3 skills/qbr-metrics/references/run-qbr.py FY27-Q3
```

This pulls all seven sources in parallel, tags topics, builds the report and a chapter-by-chapter `report.pdf` (needs Chrome), and writes `qbr-output/START_to_END/` with `raw-*.json`, `topics.json`, `metrics.json`, `report.html` and `report.md`. Expect several minutes: Luma pages through every calendar contact, and Common Room pages through every segment member. A source that fails is recorded in `errors.json` and shown as "not connected"; the rest still builds. Progress prints to stderr.

The footer of every report states the tokens and estimated API-list-price cost of the Claude session that produced it (`references/session-cost.py`, written to `cost.json` on each build). By default it counts the whole session. To count only this run, set the start time first: `export QBR_RUN_SINCE=$(date -u +%Y-%m-%dT%H:%M:%SZ)` before Step 1's pulls, in the same shell. The figure is an estimate (main session only, no sub-agents, not an invoice) and is refreshed again on `--rebuild`, so it includes the insights step.

If rate-limited (Luma 429), the scripts retry with backoff. If the run was interrupted, rerun only the failed source with `--only=luma`, then `--rebuild`.

## Step 4: Write the insights

Read `metrics.json`. Write `qbr-output/START_to_END/insights.md` in the format of the existing file in that folder (`### heading`, bullets, `**bold**` lead phrases). Then rebuild the report without re-pulling:

```bash
python3 skills/qbr-metrics/references/run-qbr.py START END --rebuild
```

Before writing, research the period and save `context.json` in the output folder (format: `{"events": [{"date", "kind": "release|industry|campaign", "label", "source"}]}`; see the existing file). Postman releases come from the `#product-updates` Slack channel (read the period with `slack_read_channel`; include only externally available items, no customer names). Industry launches come from `WebSearch` (AI model launches, MCP and API standards; prefer primary sources and say when only roundups were found). Paid campaign dates come from the YouTube data. Then rerun with `--rebuild` so the charts get markers. Optionally write `stoplight.json` to override a status or note (see the README).

Also write `recommendations.json` in the output folder: one short paragraph (3 to 5 sentences) per section, keyed `stoplight`, `reach`, `channels`, `linkedin`, `newsletters`, `blog`, `youtube`, `shorts_vs_long`, `paid_topics`, `luma`, `sheet`, `commonroom`, `community`, `topics`, `context`, `insights`. Each recommendation must follow from a number in that section, name it, and say what to do or test next. Hedge small samples, do not recommend from a group under 3 pieces, and keep paid media out of DevRel scoring. Plain language, no marketing words.

Lead the insights with reach: the report asks whether content is being amplified enough. Use the Reach per piece table (median reach, concentration in the top 3, share of views on new vs catalog content) and be explicit that the stoplight scores growth in totals, not amplification. Also say which topics receive paid views (the "Where paid and organic views go" table) and note that only YouTube ads are visible.

For the Channels section, LinkedIn statistics come from `pull-linkedin.py` and are scoped to reshared blog posts, newsletter editions and webinars only (never report page-wide totals or ads). Registrants, viewers, newsletter subscribers and article views are not in LinkedIn's API: read the newsletter's public page for edition dates and comment counts, ask the user for the rest from LinkedIn analytics, and record them in `channels-input.json`. Newsletters go only through Mailchimp now (moved from Luma in October 2026), so Mailchimp has no comparable previous period before Oct 1. Never present a missing LinkedIn number as zero, and remember LinkedIn lists organic posts only from Aug 24, 2026, so earlier periods are unavailable.

Write `insights.md` under these exact `###` headings so each block lands in its own section of the PDF: "Are we amplifying the content?", "Paid vs organic", "Topics, style and length", "News, releases and campaigns", "Meetups: ratings and cost", "New channels beyond Luma", "Newsletters", "Accounts influenced and industry", "Not covered in this run".

**Where we are going is written by the user, never by you.** Do not draft `direction.md`, fill its sections or ask the user to dictate it. If the file is missing the runner creates an empty template (it never overwrites). Tell the user it exists and that the chapter appears once they write something. Do not carry content from earlier notes into it.

Cover these, in order:
1. **Paid vs organic first.** Compare YouTube organic views separately from paid. Paid views are ad spend, not audience; never rank pieces or formats on total views.
2. **Length and format.** Use `video_summary` in the YouTube data. Do not rank a group with fewer than 3 pieces.
3. **Topic, content style and length.** `topics.json` has the tags and medians. Check the unclassified list, compare topic and style medians with the previous period, note how many pieces are in each group, and do not rank groups under 3 pieces. Mention what was excluded (ad creatives, duplicates, event recordings).
4. **News and releases.** Test whether weeks with a release or industry item differ in blog and YouTube organic traffic from other weeks, and whether posts written to accompany a release beat the median. Name any that coincide with a spike. Say "coincided with", not "caused", unless traffic-source data supports it.
5. **Meetups: ratings and cost.** Use `raw-sheet.json`: rating vs turnout and cost per attendee, which events pulled cost per attendee up, events with no data, subscriber growth. Blank sheet cells are not zero.
6. **Accounts and industry.** Accounts influenced, Tier 1 and economic buyer shares, industry mix, and the new-accounts proxy. Say these are as-of-today counts.
7. **Blog and Luma drivers.** Top posts, evergreen vs announcement, events by city and size.
8. **Not covered.** List anything skipped, so a gap is never mistaken for a finding.

Rules:
- Three to six findings. Each states the evidence (numbers and the pieces involved) and a confidence level.
- Factual, no marketing language, no adjectives like "great" or "strong". No em dashes.
- Name pieces by their actual title. Numbers use thousands separators.
- Small samples are named as small. Anything the data cannot answer goes under "Not covered".
- Blank or "not available" means the source cannot supply it, not zero.

## Step 5: Report back, and ask about the direction

Show, in under 12 lines: the range and previous period, the path to `report.pdf` and `report.html`, which sources connected and which did not, and the three biggest findings. Do not publish the report anywhere unless asked.

Then check `direction.md` in the output folder. If the user already gave it in Step 1b, say which headings have text and move on. Otherwise ask, every run:
- **No text yet:** say where the file is and offer the three ways again: they can point to a file they have written (rerun with `--direction=PATH`), answer the five questions now (the interview in Step 1b), or write it in the file and tell you when it is saved. Never offer to draft it.
- **Has text** (written for this period, or copied from an earlier one): say which headings have text and ask whether it is current. If it is a copy from an earlier period, ask before keeping it.
- After the user supplies it, rebuild with `--rebuild` and confirm the chapter appears.

## Known limits (do not paper over these)

- **YouTube impressions and CTR** are not exposed by the Analytics API. Report "not available".
- **Paid vs organic on the blog** cannot be measured (Jetpack UTM stats are blocked by the plan). Blog numbers are totals.
- **YouTube subscribers** cannot be split by traffic source.
- **Luma** has no feedback ratings and no attendee location. Ratings and cost come from the meetup sheet (columns U, S, T). Geography is by event location only. "Calendar contacts" are the subscriber count.
- **Stoplight statuses** are mechanical rules (see the README). Call out any row whose status depends on a proxy, such as Accounts influenced.
- **Common Room segments hold current members**, so counts are as of the run date. Change figures come from the previous saved snapshot in `references/snapshots.json`; the first run has none.
- **Common Room sentiment** is a UI report with no API. Report "not available".
- **Owned community metrics** are a placeholder until an MCP is connected.
- Per-video paid splits take one Analytics query per video; the script caps these at 120 videos.

## Error handling

| Problem | Action |
|---|---|
| `WP_USERNAME` or `WP_APP_PASSWORD` missing | Stop. Point to the README setup. |
| YouTube 403 or token refresh fails | Section shows "not connected". Suggest `youtube-oauth-setup.py --verify`. |
| Luma 429 | Retries with backoff. If it still fails, rerun with `--only=luma`. |
| `cr` not installed or unauthenticated | Common Room shows "not connected". `brew install common-room/tap/cr`, then `cr auth login`. |
| Empty period (no content published) | Still build. Zero is a finding. |
