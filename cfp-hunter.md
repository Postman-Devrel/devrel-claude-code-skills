---
description: Search for open Call-for-Papers (CFPs) for API and AI developer conferences
allowed-tools: WebSearch, WebFetch, Write
---

Search the internet for currently open Call-for-Papers (CFPs) for developer conferences and events. I work as a Developer Advocate at Postman.com and am looking for speaking opportunities.

## Execution Instructions (IMPORTANT)

1. **Run all WebSearch calls in parallel** in a single tool-use block (do NOT run them sequentially)
2. **Do NOT fetch individual conference detail pages** - the search results contain enough information
3. **Write results immediately** after the searches complete - do not make additional fetches
4. **Target completion time: under 30 seconds**

## Target Developer Personas

Find CFPs that target these audiences:

### API Developers
- Backend developers building and testing APIs
- Frontend developers integrating with APIs
- QA engineers testing API functionality and performance
- DevOps engineers managing API infrastructure and automation

### AI Developers
- AI application builders — Developers integrating LLMs into products via APIs (OpenAI, Anthropic, etc.) and needing to test prompts, manage context, and debug responses
- MCP server developers — Building tools/resources that AI agents can access; need to test server implementations and simulate client interactions
- Agentic workflow builders — Creating multi-step AI agents that orchestrate tools, APIs, and data sources
- Prompt engineers / AI product teams — Iterating on prompts and evaluating outputs systematically

## Search Strategy

Run these 3 searches IN PARALLEL (single tool-use block):
1. `call for papers API developer conference 2026 open CFP`
2. `call for speakers DevOps backend conference 2026 CFP deadline`
3. `site:papercall.io OR site:sessionize.com developer conference 2026 CFP`

## Output Format

Write results to `current-cfps.md` immediately after searches complete:

### API Developer Events

| Event Name | Location | CFP Closes | Summary | CFP Link |
|------------|----------|------------|---------|----------|
| ... | ... | ... | ... | ... |

### AI Developer Events

| Event Name | Location | CFP Closes | Summary | CFP Link |
|------------|----------|------------|---------|----------|
| ... | ... | ... | ... | ... |

Sort each category by CFP closing date (soonest first). Only include events with CFPs that are currently open or opening soon.
