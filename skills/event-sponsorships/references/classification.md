# Event Classification & Relevance Scoring

## PLG vs SLG Classification

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

## Relevance Scoring (0–100)

| Factor | Weight | Description |
|--------|--------|-------------|
| Audience fit | 30 | Are attendees API developers, testers, DevOps, or AI builders who use API tooling? |
| Topic alignment | 25 | Does the event cover API development, testing, collaboration, AI agents, or MCP? |
| Postman product relevance | 20 | Could Postman demo API testing, collections, monitors, flows, or AI agent tooling? |
| Reach & prestige | 15 | Estimated attendee count, industry reputation, media coverage |
| Timing & logistics | 10 | Is the event in a reachable location? Is sponsorship still available? |

### Score Bands
- **80–100**: Strong fit — core API/AI developer audience, high visibility, clear product demo opportunity
- **60–79**: Good fit — relevant audience with some topic overlap, moderate visibility
- **40–59**: Moderate fit — adjacent audience or partial topic alignment
- **20–39**: Weak fit — tangential relevance, limited sponsorship ROI
- **0–19**: Poor fit — misaligned audience or topics

## Target Persona Labels

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
