---
name: event-sponsorships
description: "Search for developer events with open sponsorship opportunities in the API and AI space. Filter by focus area (AI, API, or mixed). Returns event summaries with PLG/SLG classification and Postman relevance scores."
argument-hint: "[ai | api | mixed] — focus area filter (default: mixed)"
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

## Event Classification

For each event found, classify it as **PLG** or **SLG** based on these criteria:

### PLG (Product-Led Growth)
Events primarily attended by individual developers and practitioners who can adopt Postman directly:
- Hackathons, community meetups, developer festivals
- Open-source conferences
- Hands-on workshops, tutorials, code-along events
- Events with free or low-cost tickets aimed at individual developers
- Community-driven events (DevOpsDays, API Days, local meetups)
- **Typical attendee titles**: Software Engineer, Backend Developer, QA Engineer, DevOps Engineer, Full-Stack Developer, API Developer

### SLG (Sales-Led Growth)
Events primarily attended by enterprise buyers and decision-makers:
- Industry analyst conferences (Gartner, Forrester)
- Enterprise technology summits
- C-suite / VP-level leadership events
- Events with $1,000+ ticket prices targeting enterprise buyers
- Events emphasizing vendor evaluation, procurement, digital transformation
- **Typical attendee titles**: CTO, VP Engineering, Director of Platform, Enterprise Architect, Head of Digital Transformation

If an event has strong signals for both, classify as **PLG+SLG**.

## Relevance Scoring

Score each event 0–100 based on alignment with Postman's products and activities:

| Factor | Weight | Description |
|--------|--------|-------------|
| Audience fit | 30 | Are attendees API developers, testers, DevOps, or AI builders who use API tooling? |
| Topic alignment | 25 | Does the event cover API development, testing, collaboration, AI agents, or MCP? |
| Postman product relevance | 20 | Could Postman demo API testing, collections, monitors, flows, or AI agent tooling? |
| Reach & prestige | 15 | Estimated attendee count, industry reputation, media coverage |
| Timing & logistics | 10 | Is the event in a reachable location? Is sponsorship still available? |

### Scoring guidelines:
- **80–100**: Strong fit — core API/AI developer audience, high visibility, clear product demo opportunity
- **60–79**: Good fit — relevant audience with some topic overlap, moderate visibility
- **40–59**: Moderate fit — adjacent audience or partial topic alignment
- **20–39**: Weak fit — tangential relevance, limited sponsorship ROI
- **0–19**: Poor fit — misaligned audience or topics

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

The **Target Persona** column lists the 3–5 most likely attendee profiles using these labels:

**PLG personas (practitioners):**
- AI App Builders — developers integrating LLMs into products via APIs
- MCP Server Devs — building tools/resources that AI agents access
- Agentic Workflow Builders — creating multi-step AI agent orchestrations
- Prompt Engineers — iterating on prompts and evaluating outputs
- Software Engineers, Backend Developers, Full-Stack Developers
- ML Engineers, Research Engineers, DevOps Engineers, QA Engineers, Platform Engineers

**SLG personas (buyers/leaders):**
- CTO, VP Engineering, VP Platform
- Director of Platform Engineering, Director of Digital Transformation
- Enterprise Architect, Solutions Architect, AI Architect
- Director of Data Strategy, Cloud Infrastructure Lead
- Engineering Manager, Head of Developer Experience

Sort by relevance score (highest first).

### After the table, include a brief "Top Picks" section:

List the top 3 events with 2–3 sentences each explaining why they are the strongest sponsorship opportunities for Postman, what product demos would resonate, and what type of leads to expect (developer sign-ups vs enterprise pipeline).

### PDF Output

After writing the markdown file, also generate a PDF version at `sponsorship-output/event-sponsorships.pdf` using:

```bash
npx --yes md-to-pdf sponsorship-output/event-sponsorships.md --pdf-options '{"format":"A4","landscape":true,"margin":{"top":"15mm","bottom":"15mm","left":"15mm","right":"15mm"}}'
```

This produces a shareable landscape PDF suitable for sending to stakeholders.
