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

### Technical Leadership (Manager+)

**Platform Engineering**
- Director, Platform Engineering
- Director, Developer Platform
- Product Delivery Vice President, Enterprise Technology
- Director of Digital Transformation and Data Platforms
- Manager, Platform Delivery

**DevOps**
- Director, Cloud and DevOps
- Director, DevOps

**Developer Experience**
- Vice President, Experience (NOT User Experience or UX)
- Director, DevEx
- Developer Experience Director
- Head of Partner Connectivity and Developer Experience

**Architect**
- Enterprise Architect
- Vice President, Enterprise Architecture
- Solutions Architect / Cloud Solutions Architect Leader
- AI Architect / AI Architecture Lead
- System Architect / Lead System Architect
- Digital Solution Architect
- Global Director, Digital Solutions Payments Solutions

**Cloud**
- Director, Cloud and DevOps
- Manager, Cloud Technologies
- Cloud Infrastructure Lead
- Cloud Application Infrastructure Lead

**Infrastructure**
- Cloud Application Infrastructure Lead
- Cloud Infrastructure Manager
- Director, Infrastructure
- Head of Infrastructure Architecture

**Data Strategy & Governance** (note: not "data engineering")
- Senior Director, Data Strategy
- Director, Data Strategy and Collection
- Data Strategy and Governance-Global Payments Solutions

**API Delivery**
- Head of Delivery and Data Governance
- Manager, Platform Delivery

**API Ecosystem**
- Director, Product Ecosystem
- Vice President, Platform and Ecosystem
- Global Head Platform Ecosystem Transformation

## Search Strategy

Run these 3 searches IN PARALLEL (single tool-use block):
1. `call for papers API developer conference 2026 open CFP`
2. `call for speakers DevOps backend conference 2026 CFP deadline`
3. `site:papercall.io OR site:sessionize.com developer conference 2026 CFP`

## Additional CFP Sources to Check

After the web searches, fetch these curated CFP aggregator sites IN PARALLEL for additional opportunities:

- https://redcanary.com/blog/news-events/cfp-tracker-january-2026/
- https://www.womenonstage.net/conferences
- https://jsconf.com/
- https://confs.tech/cfp
- https://dev.to/josefine/speaking-at-tech-conferences-finding-a-cfp-238n
- https://github.com/scraly/developers-conferences-agenda?tab=readme-ov-file
- https://plus.techtalksweekly.io/issues/88-talks-l1xzwg12
- https://sessionize.com/linux-foundation-events?opencfs=true
- https://www.papercall.io/events?cfps-scope=&keywords=API

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
