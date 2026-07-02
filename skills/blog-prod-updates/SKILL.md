---
name: blog-prod-updates
description: "Scan the Postman product updates Slack channel for the past 7 days and produce a blog-ready summary of shipped features, fixes, and improvements. Maintains memory of previously covered posts to avoid duplicates. Only includes posts with Product Stage >= 7 (externally safe). Output is designed as input for blog-write."
argument-hint: "[days] (optional, defaults to 7 — e.g. '14' for two weeks)"
allowed-tools: ["Bash", "WebFetch", "Read", "Write"]
---

# Blog Product Updates Summarizer

Read recent posts from the Postman product updates Slack channel and produce a developer-facing summary markdown file suitable as input for `blog-write`.

---

## Voice & Tone Rules

These rules apply to ALL generated output — the summary markdown, blog angle suggestions, and any text shown to the user.

1. **Highlight the positives and developer impact.** Every update should lead with what shipped and what it means for developers. Frame features in terms of workflows unlocked, friction removed, or capabilities gained. Do not qualify updates with caveats, limitations, or missing functionality.

2. **No "what's missing" or internal commentary.** This is a changelog, not an opinion piece. Do not speculate about gaps, missing features, incomplete rollouts, or what "would be nice." Do not include internal context like team excitement, engineering effort, or behind-the-scenes details. Stick to what shipped and how developers can use it.

3. **Write in third person: "we've shipped…"** Use "we" (Postman) and "you" (the developer reader). Never use first person singular ("I noticed", "I've been digging into", "I get why"). The voice is the Postman team announcing what's new, not an individual's personal take.

4. **No customer names.** Never include customer or company names in the output. We do not have permission to use customer names in external blog content. Replace any customer references from Slack posts with generic terms like "teams", "enterprise users", or "customers".

---

## Prerequisites

This skill requires a Slack Bot Token with `channels:history` and `channels:read` scopes for the Postman workspace.

Set the environment variable before running:

```
SLACK_BOT_TOKEN=xoxb-...
```

The target channel is **C08SPKCGZQ8** (`https://postman.enterprise.slack.com/archives/C08SPKCGZQ8`).

---

## Workflow

### Step 1: Load Memory

Read the memory file at `blog-output/.prod-update-memory.json`. If it doesn't exist, initialize with:

```json
{
  "processed_posts": [],
  "excluded_below_stage": [],
  "last_run": null
}
```

**Schema:**

| Field | Type | Description |
|-------|------|-------------|
| `processed_posts` | array | Objects with `ts`, `date`, `summary`, `product_stage`, `output_file` for each previously covered post |
| `excluded_below_stage` | array | Objects with `ts`, `date`, `product_stage`, `snippet` (first 80 chars) for posts excluded due to Product Stage < 7 |
| `last_run` | string | ISO 8601 timestamp of last successful run |

### Step 2: Fetch Slack Messages

Use the Slack Web API to pull messages from the past N days (default 7, or user-specified):

```bash
# Calculate the oldest timestamp (Unix epoch)
OLDEST=$(date -v-7d +%s)  # macOS — adjust if on Linux

curl -s \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/conversations.history?channel=C08SPKCGZQ8&oldest=$OLDEST&limit=200" \
  | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))"
```

**Important:**
- Filter out messages where `subtype` is `channel_join`, `channel_leave`, `bot_add`, or `bot_remove`.
- Filter out threaded replies (`thread_ts != ts`) unless they are the parent message.
- If `has_more` is true in the response, paginate using the `response_metadata.next_cursor` field.

### Step 3: Deduplicate Against Memory

Compare each message's `ts` (timestamp) against `processed_posts[].ts` in memory. Skip any message already processed. Report the count of skipped duplicates.

### Step 4: Product Stage Filter

Postman uses a **Product Stage** system to indicate whether content is ready for external use. Each Slack post in the product updates channel should reference a Product Stage number.

#### Rule

- **Product Stage >= 7** → Include in the summary (externally safe)
- **Product Stage < 7** → Exclude automatically and log to memory

#### How to Identify Product Stage

Look for the Product Stage in the Slack message. It may appear as:
- "Product Stage: 7" or "Stage 7" or "PS7" or "PS: 7"
- A field in a Slack message attachment or block
- Part of a structured template the channel uses for updates

If a message **does not mention a Product Stage at all**, exclude it by default and log the reason as `"No Product Stage specified"`.

#### Logging Exclusions

For each excluded message, record in `excluded_below_stage`:

```json
{
  "ts": "1714800000.000100",
  "date": "2026-05-04",
  "product_stage": 2,
  "snippet": "New internal dashboard for monitoring API gateway latency..."
}
```

If no stage was found, set `product_stage` to `null`.

### Step 5: Enrich with Context

For each qualifying message, attempt to enrich it:

1. **Extract linked URLs** — if a message links to a public changelog, docs page, or blog post, use WebFetch to pull additional context.
2. **Identify the product area** — categorize each update (e.g., API Platform, Collections, Monitors, Flows, MCP, API Catalog, Spec Hub, Postbot, Workspaces, Governance).
3. **Note the author** — capture the Slack display name of who posted the update.

### Step 6: Generate Summary Markdown

Write the output file to `blog-output/prod-updates-YYMMDD.md` (where YYMMDD is today's date). Create the directory if it doesn't exist.

**Output format:**

```markdown
# Postman Product Updates Summary

**Period:** [start date] — [end date]
**Generated:** [today's date]
**Source:** #product-updates Slack channel
**Posts analyzed:** [total] | **Included (Stage >= 7):** [count] | **Skipped (duplicate):** [count] | **Excluded (Stage < 7):** [count]

---

## Updates by Product Area

### [Product Area Name]

#### [Feature/Update Title]

**Posted by:** [author] | **Date:** [date]

[2-4 sentence summary written in third person ("we've shipped…", "you can now…"). Focus on what shipped, why it matters to API developers, and how they can use it. Lead with the positive impact. Include relevant API endpoints, UI changes, or configuration details. Do not mention limitations, missing features, or internal context.]

**Key details:**
- [Bullet point with specific technical detail]
- [Bullet point with specific technical detail]

**Links:** [any public URLs from the original post]

---

[Repeat for each update, grouped by product area]

---

## Blog Angle Suggestions

Based on this batch of updates, here are potential angles for `blog-write`:

1. **What's new in Postman: [Suggested title]** — [1 sentence on why this angle works, which updates it combines]
2. **What's new in Postman: [Suggested title]** — [1 sentence on angle]
3. **What's new in Postman: [Suggested title]** — [1 sentence on angle]

---

## Excluded Posts (Product Stage < 7)

The following posts were excluded because their Product Stage is below 7:

| Date | Product Stage | Snippet |
|------|--------------|---------|
| [date] | [stage or "not specified"] | [first ~60 chars of post] |
| [date] | [stage] | [snippet] |

To review excluded posts, check `blog-output/.prod-update-memory.json` under `excluded_below_stage`.

<!-- EXCLUDED_BELOW_STAGE_COUNT: [N] -->
```

### Step 7: Update Memory

After writing the output file, update `blog-output/.prod-update-memory.json`:

1. **Append** each included message to `processed_posts`:

```json
{
  "ts": "1714800000.000100",
  "date": "2026-05-04",
  "summary": "API Catalog: Added service monitoring endpoints",
  "product_stage": 8,
  "output_file": "prod-updates-260504.md"
}
```

2. **Append** each excluded message to `excluded_below_stage` (schema shown in Step 4).

3. **Update** `last_run` to the current ISO 8601 timestamp.

4. **Prune** entries older than 90 days from both `processed_posts` and `excluded_below_stage` to keep the file manageable.

### Step 8: Report Results

Print a brief summary to the user:

```
Product updates summary written to blog-output/prod-updates-YYMMDD.md

Processed: X new posts with Product Stage >= 7 (Y duplicates skipped)
Excluded:  Z posts with Product Stage < 7
Areas:     [list of product areas covered]

Run /devrel-skills:blog-write blog-output/prod-updates-YYMMDD.md to draft a blog post.
```

---

## Product Stage Reference

| Product Stage | External Use | Description |
|---------------|-------------|-------------|
| 1–6 | No | Internal stages — not ready for external content |
| **7** | **Yes** | **Ready for external use — safe for blog content** |
| **8+** | **Yes** | **Established / mature feature** |

---

## Memory File Location

The memory file lives at `blog-output/.prod-update-memory.json` — a dotfile so it doesn't clutter the output directory. The skill reads it at start and writes it at end of every run. Never delete this file manually; the 90-day pruning in Step 7 keeps it from growing unbounded.

---

## Error Handling

- **Missing `SLACK_BOT_TOKEN`:** Stop immediately and tell the user to set the environment variable. Do not proceed without it.
- **Slack API errors (rate limit, auth failure):** Report the error code and message. Do not write partial output.
- **Empty channel (no messages in window):** Write a minimal output file noting "No new product updates in the past N days" and still update `last_run` in memory.
- **All messages are duplicates:** Write a minimal output file noting "All posts in this window were previously covered" with a pointer to the last output file.

---

## Quality Checks

Before writing the output file:

- [ ] Every included post has Product Stage >= 7
- [ ] Posts without a Product Stage were excluded by default
- [ ] Each update has a clear product area categorization
- [ ] Summaries are written in third person ("we've shipped", "you can now") — no first person singular ("I noticed", "I think", "I get why")
- [ ] Every update leads with the positive impact for developers — no caveats, limitations, or "what's missing" commentary
- [ ] No internal commentary (team excitement, engineering effort, behind-the-scenes context) — only what shipped and how to use it
- [ ] No customer or company names appear anywhere in the output — all replaced with generic terms
- [ ] All blog angle suggestion titles start with "What's new in Postman: "
- [ ] Blog angle suggestions reference specific updates from this batch
- [ ] Memory file is updated with all processed posts and excluded-below-stage posts
- [ ] Output filename uses correct YYMMDD date format
