---
name: events-agenttools
description: "Search for developer events for DevRel to drive PLG adoption of the postman-plugin among agentic coding tool users (Claude Code, Cursor, Codex, etc.) and headless-agent app builders. Returns a scored rubric with presence recommendations. Use when planning DevRel conference/event coverage for postman-plugin adoption."
argument-hint: "[none] — searches run automatically, no filter needed"
allowed-tools: ["WebSearch", "Write"]
---

# Agentic Dev Tools Event Finder

Search the internet for developer conferences, meetups, and hackathons where Postman DevRel should have a presence to drive **product-led growth (PLG) adoption of the Postman Agent Stack**, starting with [postman-plugin](https://github.com/postmanlabs/postman-plugin).

The postman-plugin brings filesystem-first, git-native API development directly into coding agents — Claude Code, Cursor, Codex, Factory Droid, Kimi Code, OpenCode, Pi — and into headless agent workflows via its CLI and MCP fallback. It spans two of the three concerns in the wider Postman Agent Stack on its own: specs/collections for **building** new endpoints from inside an agent tool, and mocking/testing for **maintaining** existing ones the same way. The rest of the stack covers what postman-plugin doesn't: [Orbit](https://www.buildwithorbit.ai/welcome) (building — API discovery over REST/MCP), [Context Graph](https://www.postman.com/context-graph/) (maintaining — dependency/blast-radius graph), and [Fabric Gateway](https://learning.postman.com/fabric-gateway/get-started/overview), [Astropods](https://astropods.com/), and [Passport](https://blog.postman.com/postman-passport-secure-api-access-for-the-agentic-era/) (a third concern, **operating** the agent itself once it's running — routing, policy, token/cost budgets, evals, audit trails, secure credential/identity access, and, for Astropods specifically, the runtime for running agents on a schedule or fully autonomously as managed agents in the cloud). The target audience across the whole stack is individual developers working inside an agentic coding tool, and the engineers who keep their agents and APIs running — not enterprise buyers. See `references/scoring.md` for how the stack maps to persona labels.

## Execution Instructions

Run all WebSearch calls below in a single parallel tool-use block, then write results straight from the search output — no WebFetch calls, no individual event-page lookups. Target completion time: under 30 seconds.

## Search Strategy

Run ALL searches below IN PARALLEL in a single tool-use block.

### Agentic coding tool events

1. `Claude Code developer meetup conference 2026`
2. `Cursor AI editor hackathon conference 2026`
3. `Codex ChatGPT coding agent developer event 2026`
4. `Kiro agentic IDE developer meetup 2026`
5. `Antigravity AI coding agent event 2026`
6. `AI coding agent hackathon 2026 sponsorship`

### Agent/MCP ecosystem events

7. `MCP Model Context Protocol developer conference meetup 2026`
8. `agentic AI developer conference 2026 sponsorship booth`
9. `headless agent autonomous AI developer event 2026`
10. `AI engineer summit 2026 agents tooling sponsor`

### PLG-signal venues (hackathons, community, hands-on)

11. `AI agent hackathon 2026 developer prizes`
12. `site:lu.ma AI coding agent meetup 2026`
13. `site:devpost.com agentic AI hackathon 2026`
14. `developer week AI agents conference 2026 sponsor exhibit`

### Agent Ops events (evals, observability, token cost, security, autonomous/scheduled agents)

15. `AI agent observability evals conference 2026 sponsor`
16. `LLM token cost FinOps AI conference 2026`
17. `AI agent security identity credentials conference 2026`
18. `autonomous AI agents cloud managed scheduled conference 2026`

## Link Sourcing

For every event, the **Link** column must point to the event's own primary source — the organizer's own domain, or the specific platform they actually run registration through (Luma, Devpost, Sessionize, a Linux Foundation events page, Meetup.com). Never link a recap blog, translated mirror, SEO aggregator, or news site that merely wrote about the event, even if it ranked higher or had a more descriptive snippet. Each WebSearch call already returns several result links — scan all of them for the organizer's own domain before picking one; most searches return it alongside the secondary sources. If every result for an event is a secondary source with no organizer site behind it (no official domain, no Luma/Devpost/Sessionize page), drop that event from the table rather than cite an unverifiable source — don't keep a placeholder link just to fill the row.

## Scoring & Recommendations

Read `references/scoring.md` for the full rubric: weighted scoring factors (0–100), score bands, presence-type recommendations, and target persona labels.

## Output Format

Write results to `events-agenttools-output/events-agenttools.md`. Create the directory if it doesn't exist.

### Header

```
# Agentic Dev Tools Events — postman-plugin PLG Targeting
Generated: {date}
Target: postman-plugin adoption among agentic coding tool developers
```

### Results Table

| Event Name | Date | Location | Est. Attendees | Agentic Tool Overlap | Format | Score | Target Persona | Recommended Presence | Link |
|------------|------|----------|-----------------|----------------------|--------|-------|-----------------|-----------------------|------|
| ... | ... | ... | ... | Claude Code / Cursor / Codex / Kiro / mixed | Conference / Hackathon / Meetup / Workshop | 85 | ... | Booth / Talk / Workshop / Hackathon sponsor / Demo table | ... |

**Agentic Tool Overlap** names the specific agent(s) the event's audience is known to use (see `references/scoring.md`). **Recommended Presence** is the single best-fit option from `references/scoring.md`'s presence-type guide.

Sort by score (highest first).

### After the table, include a "Top Picks" section

List the top 3 events with 2–3 sentences each explaining:
- Why the event's audience overlaps with the Postman Agent Stack's target developer (agentic-tool users, headless-agent builders, API-discovery/governance-minded teams)
- What specific demo would resonate (e.g., filesystem-first mocking inside Cursor via postman-plugin, Context Graph dependency checks before an agent ships a change, Orbit API discovery over MCP, Astropods governing an agent fleet)
- What presence format to pursue and why (hackathon sponsorship for a hands-on PLG audience vs. a conference talk for visibility)

### After Top Picks, include a "Pass" section

List any events that scored below 40, with a one-line reason they're a poor fit (e.g., enterprise buyer audience, no agentic-tool overlap).
