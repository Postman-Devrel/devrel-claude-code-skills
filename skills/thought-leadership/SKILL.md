---
name: thought-leadership
description: "Manage thought leadership pitches — generate vendor-neutral PR pitches, list existing pitches, write a full draft from a pitch, or mark a pitch as accepted. Use when the user wants contributed content pitches, thought leadership ideas, or to manage the pitch pipeline."
argument-hint: "pitches [focus] | list | write | accepted"
allowed-tools:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Bash
---

# Thought Leadership Manager

Manage the full lifecycle of vendor-neutral thought leadership pitches: generate, track, draft, and close.

## Commands

Parse the first argument to determine the command:

| Command | Description |
|---------|-------------|
| `pitches [focus]` | Research trending topics and generate 5 new pitches. Optional focus area narrows the search (e.g. "agent security", "MCP") |
| `list` | Show all pitches from memory with their status |
| `write` | Select a pitch and write the full contributed article draft |
| `accepted` | Mark a pitch as accepted and done |

If no argument is provided, prompt the user to choose a command.

---

## Shared: Pitch memory

All commands read from `pitch-output/.pitch-memory.json`. If it doesn't exist, initialize with:

```json
{
  "pitches": [],
  "last_run": null
}
```

Each entry in `pitches` has: `id` (sequential int), `date`, `topic`, `angle`, `outlets`, `output_file`, `status` ("open" | "writing" | "accepted"), `draft_file` (null or path).

---

## Command: `pitches`

Research trending developer topics in the AI space that overlap with Postman's product areas, then generate 5 vendor-neutral pitches for contributed content at tech publications.

### Voice and framing rules

1. **Vendor neutral.** Pitches focus on the trending topic, industry problem, or developer challenge. Do not mention Postman, any competitor, or any specific product by name. The pitch sells an expert perspective on a topic, not a product.
2. **One paragraph per pitch.** Each pitch is a single paragraph (4-6 sentences) that frames the trend, states the angle, and hints at the insight the article would deliver. It should make an editor want to read the full piece.
3. **Expert voice.** Write as a senior technologist proposing a byline. Authoritative, opinionated, specific. No marketing language ("unlock", "supercharge", "revolutionize", "leverage").
4. **Actionable angles.** Each pitch should propose a clear, differentiated angle. "AI agents are changing APIs" is too broad. "Why your API error messages are the biggest blocker to agent adoption" is specific enough.

### Workflow

#### 1. Load pitch memory

Read `pitch-output/.pitch-memory.json`.

#### 2. Load Postman AI topic areas

Read `references/postman-ai-topics.md` to understand which AI topic areas overlap with Postman's capabilities. These are the topic guardrails, not content to include in pitches.

#### 3. Research trending topics

Run parallel WebSearch queries to find what's trending in AI and APIs right now.

If a focus area was provided, tailor all queries toward that focus. Otherwise use these defaults:

**Batch 1 (run in parallel):**
- `"AI agents API" trending 2026` — agent-to-API interaction trends
- `"agentic AI" enterprise challenges 2026` — enterprise adoption friction
- `"API security AI agents" 2026` — security concerns with AI calling APIs
- `"MCP protocol" OR "model context protocol" developer` — MCP ecosystem growth
- `"AI gateway" OR "agent gateway" API management` — infrastructure for AI traffic

**Batch 2 (run in parallel):**
- `"API observability AI" OR "agent observability"` — monitoring AI-driven API calls
- `"AI SDK" OR "AI developer tools" trends` — tooling for AI app builders
- `"API governance AI" compliance enterprise` — governance in the age of agents
- `site:techcrunch.com OR site:thenewstack.io AI agents API 2026` — what outlets are already covering

After searches complete, use WebFetch on the top 2-3 most relevant results to get deeper context on the freshest trends.

#### 4. Cross-reference and select topics

Compare the trending topics against the Postman AI topic areas from Step 2. Select 5 topics where:
- The topic is genuinely trending (multiple recent sources, not just one article)
- It overlaps with at least one Postman AI capability area (so the company could credibly author it)
- The angle hasn't been pitched before (check against pitch memory from Step 1)
- Same topic with a different angle is allowed and not considered a duplicate

#### 5. Generate pitches

For each of the 5 selected topics, write:

1. **Topic**: 3-5 word label (e.g., "Agent-to-API authentication gaps")
2. **Pitch**: One paragraph (4-6 sentences). Frame the trend, state the angle, hint at the insight. Vendor neutral. No product names.
3. **Suggested outlets**: 2-3 publications that cover this space and accept contributed content. Read `references/outlets.md` for the outlet reference.
4. **Why these outlets**: One sentence per outlet explaining why it fits.
5. **Postman overlap**: One sentence (internal note, not part of the pitch) noting which Postman AI area connects. This helps the PR team position the author.

#### 6. Write output

Save to `pitch-output/pitches-YYMMDD.md` using this format:

```markdown
# Thought Leadership Pitches

**Generated:** [date]
**Pitches:** 5 | **New topics:** [count] | **New angles on existing topics:** [count]

---

## 1. [Topic label]

**Pitch:**
[Single paragraph pitch text]

**Suggested outlets:**
- [Outlet 1] — [why it fits]
- [Outlet 2] — [why it fits]
- [Outlet 3] — [why it fits]

**Internal note:** Overlaps with [Postman AI area]. Potential author: [suggest role, e.g., "CTO", "Head of AI", "Developer Advocate"].

---

[Repeat for pitches 2-5]
```

#### 7. Update pitch memory

Append each pitch to `pitch-output/.pitch-memory.json` with a sequential `id`, `status: "open"`, and `draft_file: null`.

Update `last_run` to the current ISO 8601 timestamp. Prune entries older than 6 months (except those with status "writing" or "accepted").

#### 8. Report results

Print a summary:

```
Pitches written to pitch-output/pitches-YYMMDD.md

Topics covered:
  1. [Topic] → [Outlet 1], [Outlet 2]
  2. [Topic] → [Outlet 1], [Outlet 2], [Outlet 3]
  ...

Previous pitches on file: [count]
```

---

## Command: `list`

Display all pitches from `pitch-output/.pitch-memory.json` in a table:

```
ID | Date       | Topic                              | Status   | Outlets                    | Draft
---|------------|-------------------------------------|----------|----------------------------|------
1  | 2026-08-14 | Agent-to-API authentication gaps    | open     | TechCrunch, The New Stack  | —
2  | 2026-08-14 | API error messages block agents     | writing  | InfoQ, DZone               | pitch-output/draft-2.md
3  | 2026-07-20 | MCP server testing strategies       | accepted | The New Stack              | pitch-output/draft-3.md
```

Group by status: **Open** first, then **Writing**, then **Accepted**. Show counts per status at the bottom.

---

## Command: `write`

Write a full contributed article draft from a selected pitch.

### Workflow

1. Read `pitch-output/.pitch-memory.json` and show only pitches with status "open" or "writing" in a numbered list.
2. Ask the user to select a pitch by number.
3. Read the pitch's output file to get the full pitch details (topic, angle, outlets, Postman overlap).
4. Read `references/outlets.md` to understand the target audience for the suggested outlets.
5. Research the topic further with 3-4 targeted WebSearch queries to gather supporting data, examples, and recent developments.
6. Write a 1200-1800 word contributed article draft that:
   - Matches the pitch angle exactly
   - Is vendor neutral (no product names, no Postman)
   - Uses an expert byline voice — opinionated, backed by specifics
   - Opens with a hook that frames the problem or trend
   - Includes 2-3 concrete examples, data points, or scenarios
   - Ends with a forward-looking take, not a sales pitch
   - Uses subheadings to break up the piece
   - Targets the audience of the first suggested outlet
7. Save the draft to `pitch-output/draft-[id]-[slugified-topic].md` with frontmatter:

```markdown
---
pitch_id: [id]
topic: [topic]
target_outlet: [primary outlet]
word_count: [count]
status: draft
---

# [Article title]

[Article body]
```

8. Update the pitch in `.pitch-memory.json`: set `status: "writing"` and `draft_file` to the path.
9. Print a summary with the file path and word count.

---

## Command: `accepted`

Mark a pitch as accepted and complete.

### Workflow

1. Read `pitch-output/.pitch-memory.json` and show pitches with status "open" or "writing" in a numbered list.
2. Ask the user to select a pitch by number.
3. Update the pitch in `.pitch-memory.json`: set `status: "accepted"`.
4. Print confirmation with the topic and outlet.

---

## Done when

The requested command completes successfully and pitch memory is up to date.
