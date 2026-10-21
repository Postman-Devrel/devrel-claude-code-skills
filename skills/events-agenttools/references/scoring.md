# Scoring & Recommendations — postman-plugin PLG Events

## The Postman Agent Stack

postman-plugin doesn't stand alone — it's the entry point into a set of Postman products aimed at **AI builders**, split across three concerns: building the agent, maintaining the APIs it calls, and operating the agent itself once it's running.

| Product | Role in the stack | Primary persona |
|---------|--------------------|------------------|
| [postman-plugin](https://github.com/postmanlabs/postman-plugin) | Filesystem-first, git-native API dev *inside the agent tool itself* (Claude Code, Cursor, Codex, Kiro, Antigravity, and others): specs and collections for building new endpoints, mocking and testing for verifying existing ones still work | API/Platform Engineers |
| [Orbit](https://www.buildwithorbit.ai/welcome) | Free API discovery service so an agent can design against and call the right public API over REST or MCP | Agentic App Builders, Headless Agents (a design/build capability, not its own audience) |
| [Context Graph](https://www.postman.com/context-graph/) | Dependency graph across an API estate — lets an agent (or the human behind it) answer "what breaks if I change this endpoint?" before shipping a change | API/Platform Engineers |
| [Fabric Gateway](https://learning.postman.com/fabric-gateway/get-started/overview) | Agent gateway that routes, governs, and observes LLM/MCP/agent traffic through a single endpoint — policy enforcement, fallbacks, credential centralization | Agent Ops Engineers |
| [Astropods](https://astropods.com/) | Governance/ops layer for running a fleet of agents in production — registry, budget limits, audit trail, *and* the runtime for running those agents on a schedule or fully autonomously (managed agents in the cloud, not just a dashboard over agents running elsewhere) | Agent Ops Engineers |
| [Passport](https://blog.postman.com/postman-passport-secure-api-access-for-the-agentic-era/) | Secure API access for agents — credential references instead of exposed API keys, a Secure Access Proxy, and durable/ephemeral agent identities with scoped, inheritable permissions | Agent Ops Engineers |

postman-plugin is the only product that spans both the building concern and the maintaining concern, because it runs inside the agent tool itself at both stages: building a new endpoint and testing/mocking an existing one are the same filesystem-first workflow, just pointed at different specs. Both stages belong to the same persona, API/Platform Engineers — they're the ones who use the coding agent to do the building and the maintaining, not a separate "power user" audience. Context Graph is about the *APIs* an agent depends on (blast radius, who consumes what) — also an API/Platform Engineers concern. Fabric Gateway, Astropods, and Passport are about the *agents themselves* once they're running — routing, policy, cost/token budgets, audit trails, reliability, and now credential/identity security — a third, distinct concern (and distinct persona, Agent Ops Engineers) from both building and API maintenance.

Any event whose audience would plausibly adopt one of these six is in scope, not just postman-plugin specifically. Score the event on the stack as a whole and note in "Topic/demo opportunity" which product(s) fit the room.

## Relevance Scoring (0–100)

Weighted for PLG adoption of the Postman Agent Stack by individual developers who build with agentic coding tools — not for enterprise/SLG pipeline.

| Factor | Weight | Description |
|--------|--------|-------------|
| Agentic-tool audience fit | 30 | Are attendees known users of Claude Code, Cursor, Codex, Kiro, Antigravity, Factory Droid, Kimi Code, OpenCode, or Pi — or API/platform engineers responsible for the services those agents call, or agent ops engineers responsible for the agents themselves (evals, token cost, reliability, governance)? |
| Headless/agent-workflow relevance | 25 | Does the event cover agentic app building, autonomous agents calling APIs, scheduled/autonomous managed agents running in the cloud, agent evals/observability/cost, agent-to-agent governance, credential/identity security for agents, CLI-first/git-native dev workflows — the problems postman-plugin, Orbit, Context Graph, Fabric Gateway, Astropods, or Passport solve? |
| PLG format signal | 20 | Is the format hands-on and individual-developer-led (hackathon, workshop, hands-on lab, community meetup) rather than buyer-facing (analyst conference, exec summit)? |
| Reach & timing | 15 | Estimated attendee count, relevance to 2026, and whether a DevRel presence (talk, booth, sponsorship) is realistically available |
| Topic/demo opportunity | 10 | Is there a natural slot for a live demo of postman-plugin, Orbit, Context Graph, Fabric Gateway, Astropods, or Passport (lightning talk, workshop track, hackathon mentorship) rather than just a booth? |

### Score Bands

- **80–100**: Strong fit — core agentic-coding-tool audience, hands-on format, clear demo slot
- **60–79**: Good fit — agent/AI-adjacent audience, some format or topic overlap
- **40–59**: Moderate fit — general AI/dev audience with partial agentic-tool overlap
- **20–39**: Weak fit — tangential AI audience, buyer-heavy or topic mismatch
- **0–19**: Poor fit — no agentic-tool overlap, enterprise/analyst audience

## Agentic Tool Overlap Labels

Use the most specific label(s) the search results support; use "mixed" when the event covers agentic coding tools broadly without naming one tool as primary.

- Claude Code
- Cursor
- Codex
- Kiro
- Antigravity
- Factory Droid
- Kimi Code
- OpenCode
- Pi
- Mixed (agentic coding tools broadly, agent frameworks, MCP ecosystem)

## Presence-Type Recommendations

Pick the single best-fit option per event, driven by format and score band:

| Format signal | Recommended presence |
|----------------|------------------------|
| Hackathon, hands-on PLG audience, score 70+ | **Hackathon sponsor** — API credits/prizes, mentors on-site, live demo station for postman-plugin, Orbit, Fabric Gateway, Astropods, or Passport |
| Conference with a talk track, score 60+ | **Talk** — session on filesystem-first API dev inside agentic coding tools, Context Graph for agent-driven changes, Fabric Gateway/Astropods for governing and observing an agent fleet (token cost, evals, policy), running managed agents on a schedule or fully autonomously in the cloud (Astropods), or Passport for securing agent-to-API credentials |
| Workshop/lab track | **Workshop** — hands-on session installing postman-plugin and mocking an API, wiring an agent to Orbit for live API discovery, routing agent traffic through Fabric Gateway, or swapping exposed API keys for Passport credential references |
| Community meetup, smaller scale | **Demo table** — lightweight presence, no formal talk required |
| Mixed/general AI conference, score 40–59 | **Booth** only — broad audience, narrower postman-plugin fit |
| Score below 40 | **Pass** — not worth DevRel bandwidth |

## Target Persona Labels

Every persona below works inside or alongside an agentic coding tool (Claude Code, Cursor, Codex, Kiro, Antigravity, Factory Droid, Kimi Code, OpenCode, Pi, or similar) — that's the common thread across the whole stack, not just one bucket.

- **Agentic App Builders** — developers designing and building apps where agents call APIs autonomously, from inside an agent tool; includes discovering/evaluating the right API (Orbit), not just wiring one up
- **Headless Agents** — building and operating agents that run without a human in the loop, authored inside an agent tool; also lean on Orbit for runtime API discovery
- **API/Platform Engineers** — own the APIs and production systems that agents call, and use a coding agent (Claude Code, Cursor, Codex, Kiro, Antigravity, or similar) as the tool to both build new specs/collections and maintain/test existing ones via postman-plugin, plus Context Graph for dependency/blast-radius awareness before shipping a change
- **Agent Ops Engineers** — responsible for the agents themselves once they're running in production, including the agent tools generating their code: evals, token/cost utilization, reliability, observability, credential/identity security, policy and governance across an agent fleet; map to Fabric Gateway (routing/policy/observability), Astropods (registry/budget/audit, and running managed agents on a schedule or fully autonomously in the cloud), and Passport (credential references and scoped agent identities instead of exposed API keys)
