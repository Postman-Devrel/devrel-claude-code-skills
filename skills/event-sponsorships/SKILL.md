---
name: event-sponsorships
description: "Search for developer events with open sponsorship opportunities in the API and AI space. Filter by focus area (AI, API, or mixed). Returns event summaries with PLG/SLG classification and Postman relevance scores."
argument-hint: "[ai | api | mixed] — focus area filter (default: mixed)"
allowed-tools: ["AskUserQuestion", "WebSearch", "Write", "Bash"]
---

# Event Sponsorship Finder

Search the internet for developer conferences and events with open sponsorship opportunities. We are the Developer Relations team at Postman.com and are looking for events to sponsor that align with our API platform and AI tooling strategy.

## Focus Area Selection

Before searching, ask the user which event focus they want using AskUserQuestion:

| Option | Description |
|--------|-------------|
| AI | AI/ML conferences — LLMs, agents, MCP, AI infrastructure |
| API | API-focused conferences — REST, GraphQL, API management, testing, DevOps |
| Mixed | Both AI and API events (default) |

If the user already provided a focus area as an argument (`ai`, `api`, or `mixed`), skip the question and use that value directly.

## Execution Instructions (IMPORTANT)

1. **Run all WebSearch calls in parallel** in a single tool-use block (do NOT run them sequentially)
2. **Do NOT fetch individual event detail pages** — the search results contain enough information
3. **Write results immediately** after the searches complete — do not make additional fetches
4. **Target completion time: under 30 seconds**

## Search Strategy

Adjust searches based on the selected focus area. Run ALL applicable searches IN PARALLEL in a single tool-use block.

### API-focused searches (run when focus is `api` or `mixed`):

1. `API developer conference 2026 sponsorship opportunities packages`
2. `DevOps platform engineering conference 2026 sponsor exhibit`
3. `site:sessionize.com API developer conference 2026 sponsor`
4. `REST GraphQL API conference 2026 sponsorship prospectus`
5. `developer tools conference 2026 sponsor booth exhibit`

### AI-focused searches (run when focus is `ai` or `mixed`):

6. `AI developer conference LLM agents 2026 sponsorship packages`
7. `machine learning AI infrastructure conference 2026 sponsor exhibit`
8. `AI engineering summit 2026 sponsorship opportunities`
9. `agentic AI MCP developer conference 2026 sponsor`
10. `generative AI developer tools conference 2026 sponsor booth`

### General searches (always run):

11. `developer conference 2026 sponsorship prospectus PDF open`
12. `site:confs.tech developer conference 2026`

**CRITICAL: Do NOT make any WebFetch calls.** The search results contain sufficient information. Write results immediately after searches complete.

## Event Classification & Relevance Scoring

Read `references/classification.md` for PLG/SLG criteria, the scoring rubric (weighted 0–100), and target persona labels.

## Output Format

Write results to `sponsorship-output/event-sponsorships.md`. Create the directory if it doesn't exist.

The output file should include:

### Header

```
# Event Sponsorship Opportunities — {Focus Area}
Generated: {date}
Focus: {AI | API | Mixed}
```

### Results Table

| Event Name | Date | Location | Est. Attendees | Growth Type | Relevance | Target Persona | Summary | Sponsorship Link |
|------------|------|----------|----------------|-------------|-----------|----------------|---------|------------------|
| ... | ... | ... | ... | PLG / SLG / PLG+SLG | 85 | ... | ... | ... |

The **Target Persona** column lists the 3–5 most likely attendee profiles — see `references/classification.md` for the full persona label list.

Sort by relevance score (highest first).

### After the table, include a brief "Top Picks" section:

List the top 3 events with 2–3 sentences each explaining why they are the strongest sponsorship opportunities for Postman, what product demos would resonate, and what type of leads to expect (developer sign-ups vs enterprise pipeline).

### PDF Output

After writing the markdown file, also generate a PDF version at `sponsorship-output/event-sponsorships.pdf` using:

```bash
npx --yes md-to-pdf sponsorship-output/event-sponsorships.md --pdf-options '{"format":"A4","landscape":true,"margin":{"top":"15mm","bottom":"15mm","left":"15mm","right":"15mm"}}'
```

This produces a shareable landscape PDF suitable for sending to stakeholders.
