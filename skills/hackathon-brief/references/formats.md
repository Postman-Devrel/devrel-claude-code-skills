# Format defaults

These are Postman's working assumptions. Use them as defaults and show them to the user as defaults. Anything the user overrides replaces them.

## Event types

| Type | Access | Registration target | Typical budget | Registration driven by | Length |
|------|--------|---------------------|----------------|------------------------|--------|
| Public hackathon | Open | ~300 | ~$30,000 | Marketing, Luma, Discord, partner channels | In-person 4 to 6 hours; virtual any length |
| Joint customer hackathon | Closed | 50 to 100 | ~$15,000 to $20,000 in person (around 100 people) | Sales team outreach to overlapping customers | In-person 2 to 3 hours |
| Influencer hackathon | Hybrid | Like public (~300) | Like public | Starts with Common Room influencer list, then opens to others | Like public |
| Challenge-based hackathon | Open or closed | Set by the user | Closed and influencer-sized events: 5 to 100 people | Depends on access model | In-person 2 to 3 hours; virtual any length |

Notes:
- Closed events and influencer events of 5 to 100 people use the closed budget band, not the public one.
- Challenge-based events replace "build anything with product X" with a fixed set of challenges completed and verified through Liftoff. Awards can go to most badges, fastest completion (speed run), or specific challenges.
- In-person always includes catering. Virtual does not.
- Any type can be in person or virtual.

## Goals and metrics

| Goal | Metric | Source |
|------|--------|--------|
| Badges earned | Badges issued during the event window | Liftoff admin stats |
| Discord community engagement | New members joined, messages in the event channel, members still active at 30 days | Discord dashboard |
| Product activation | Participants who created a workspace, ran a collection, installed the plugin | Product analytics |
| Community-contributed extensions | Skills and mods submitted, published, and installed | Repo and marketplace |
| Sales and opportunity influence | Attendees from the target customer list | Luma export matched to CRM |
| | Expansion opportunities influenced within 180 days | CRM |
| | Closed-won deals influenced within 180 days | CRM |
| | Cost per deal: total event cost divided by influenced closed-won deal value | Computed |

Always compute: cost per registrant, cost per attendee, and cost per target-list attendee. For sales influence, also compute the break-even deal value (total cost divided by the number of closed-won deals needed).

## Sample agendas

### Public (open), in person, full day

| Time | Segment |
|------|---------|
| 8:30 AM | Registration, breakfast, networking |
| 9:00 AM | Opening keynote and live demos: Postman AI vision, then live walkthroughs of the Claude Code plugin, Postman Agent Mode, Astro, and AI Engineer (45 min total) |
| 9:45 AM | Hacking begins. Teams have Postman workspaces, Claude API credits, and mentor support |
| 10:30 AM | Morning mentor office hours with Anthropic and Postman engineers |
| 1:00 PM | Lunch and midday check-in, optional office hours |
| 4:00 PM | Submissions close |
| 4:30 PM | Judging panel reviews |
| 5:30 PM | Finalist demo pitches, including an AI Engineer maintenance plan |
| 6:30 PM | Awards ceremony and closing reception |

Adapt the keynote contents, tools named, and finalist requirements to the chosen theme and partner.

### Closed (joint customers), in person, afternoon and evening

| Time | Segment |
|------|---------|
| 14:00 | Kickoff |
| 14:30 to 18:00 | Build |
| 18:00 to 18:30 | Dinner, networking, drinks |
| 18:30 to 18:45 | Announce winners |

### Virtual

Any length. Use an async-first structure: recorded kickoff, written Q&A in Discord, live check-ins timed for energy dips (roughly the midpoint and the last quarter), and a live demo session for finalists. Pick demo times that work across the time zones in the registration list.

## Default judging rubric

Score each 1 to 10. This sample is from a production-ready agents hackathon. Swap criteria to fit the chosen theme, keep 4 to 6 criteria, and show weights if they differ.

| Criterion | What judges look for |
|-----------|----------------------|
| Production readiness | APIs tested and monitored in Postman; agent has error handling, retry logic, and operational considerations such as evals, token optimization, guardrails |
| MCP quality | MCP server is well structured, documented, and exposes meaningful tools to the agent |
| Claude Code + Postman usage | Meaningful use of the Claude Code plugin and/or Postman Agent Mode in development or execution |
| Astro + operational concerns | Agents are ready for production; the team considered operational requirements, including Astro AI |
| Impact and ambition | Solves a real problem, with scope that extends beyond the hackathon into a viable production scenario |
| Judges preference | Personal preference, experience, interest, or creativity |

For challenge-based events, score by verified badges and time instead, with a tie-break demo.

## Enterprise and joint customer concept

Closed events can require specific technology to take part. Example:
- DevRel creates a Fabric Gateway instance connected to typical enterprise systems, including the Microsoft suite, with the SE organization (it may already exist).
- Must use Copilot plus the Postman plugin.
- Must consume 2 services from the Fabric Gateway.
- Agents must be deployed on Astropods.

## Prize defaults

| Type | Default |
|------|---------|
| Public | At least $10,000 total. Ask whether joint-funded or all Postman |
| Challenge-based | Pay on badges earned, specific challenges, or speed run placement |
| Enterprise / joint customer | Smaller prizes. Aligned with a CIO or executive sponsor, for example fund the winning project into production with credits from Postman and the partner. Add smaller personal prizes for winners |
| Influencer | Like public, plus recognition and content features for the influencers |
