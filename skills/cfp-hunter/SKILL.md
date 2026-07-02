---
name: cfp-hunter
description: "Search for open Call-for-Papers (CFPs) for API and AI developer conferences. Runs 8 parallel WebSearch queries and writes results to cfp-output/current-cfps.md; never fetches individual conference pages."
argument-hint: "[focus] (optional, e.g. 'AI', 'API', 'DevOps')"
allowed-tools: ["WebSearch", "Write"]
---

Search the internet for currently open Call-for-Papers (CFPs) for developer conferences and events. I work as a Developer Advocate at Postman.com and am looking for speaking opportunities.

## Execution Instructions (IMPORTANT)

1. **Run all WebSearch calls in parallel** in a single tool-use block (do NOT run them sequentially)
2. **Do NOT fetch individual conference detail pages** - the search results contain enough information
3. **Write results immediately** after the searches complete - do not make additional fetches
4. **Target completion time: under 30 seconds**

## Target Developer Personas

Read `references/personas.md` for the full target persona taxonomy (API developers, AI developers, technical leadership).

## Search Strategy

Run ALL 8 searches IN PARALLEL in a single tool-use block:

**Core searches:**
1. `call for papers API developer conference 2026 open CFP`
2. `call for speakers DevOps platform engineering conference 2026 CFP deadline`
3. `AI developer conference LLM agents 2026 call for papers CFP`

**CFP platform searches:**
4. `site:papercall.io API developer conference 2026 CFP open`
5. `site:sessionize.com API DevOps cloud conference 2026 CFP`

**Aggregator site searches:**
6. `site:confs.tech CFP 2026 developer API`
7. `site:github.com developers-conferences-agenda 2026 CFP`
8. `Linux Foundation events 2026 call for proposals CFP open`

## Reference Sites

Read `references/cfp-sites.md` for curated CFP tracking sites to check manually.

**CRITICAL: Do NOT make any WebFetch calls.** The search results contain sufficient information. Write results immediately after searches complete.

## Output Format

Write results to `/cfp-output/current-cfps.md` immediately after searches complete. Create the directory if it doesn't exist.

### API Developer Events

| Event Name | Location | CFP Closes | Summary | CFP Link |
|------------|----------|------------|---------|----------|
| ... | ... | ... | ... | ... |

### AI Developer Events

| Event Name | Location | CFP Closes | Summary | CFP Link |
|------------|----------|------------|---------|----------|
| ... | ... | ... | ... | ... |

Sort each category by CFP closing date (soonest first). Only include events with CFPs that are currently open or opening soon.
