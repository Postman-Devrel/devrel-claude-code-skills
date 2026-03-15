---
name: newsletter-agentsandapis
description: "Generate the monthly Postman Agents & APIs meetup newsletter. Combines upcoming events from Luma calendar with latest AI and API news, focusing on MCP Apps, agent observability, API security, and ecosystem developments. Use at the start of each month to create newsletter content for subscribers."
---

# Monthly Meetup Newsletter Generator

Generate an informative, developer-focused newsletter for Postman Agents & APIs meetup subscribers that balances event promotion with valuable technical content.

## Newsletter Goals

1. **Keep developers informed** about latest AI and API developments
2. **Promote upcoming meetup events** without being marketing-heavy
3. **Highlight partner speakers** and their expertise
4. **Encourage community engagement** through meetups and learning

---

## Content Structure

### 1. Standard Header (Always Include First, but Paraphrase)

```markdown
Welcome to the **Agents & APIs Developer Newsletter** by Postman. We run in-person developer events worldwide, where we demo what's new with Postman, invite partners to share code, and generally chat about all things AI and API. Make sure you check the [event calendar](https://luma.com/calendar/cal-TGqTNpY4iyl7XYe) for the latest event dates.

Here's a roundup of the latest AI & API news:

---
```

### 2. Title with Month/Year

```markdown
# **What's New in Agents & APIs — [Month] [Year]**
```

### 3. Opening Paragraph (2-3 sentences)

Start with what's happening in the AI/API space this month. Make it conversational and set context for why the meetups and news matter.

**Example:**
```markdown
2026 is shaping up to be the year agent systems move from experiments to production. MCP Apps launched for interactive UIs in chat windows, Vercel shipped skills.sh (npm for agents), and both hit massive adoption within days. Meanwhile, 79% of enterprises lack visibility into what their agents are actually doing, and 96% of API attacks now come from authenticated sources, including compromised agents. We're covering the practical patterns at our February meetups, with speakers from Postman, Elastic, Snyk, Notion, and Fern.
```

### 4. What's New This Month (News Section)

```markdown
---

## **What's New in [Month]?**
```

Include 3-5 major developments. **Priority topics:**
1. **MCP ecosystem updates** (always check for new developments)
2. **Skills.sh or agent capability systems** (package managers, skill ecosystems)
3. **Agent observability** (monitoring, debugging, cost tracking)
4. **API security for agents** (authentication, authorization, machine IAM)
5. **Major API/SDK releases** (OpenAI, Anthropic, etc.)
6. **Major feature or product releases from AI providers** (OpenAI, Google, Anthropic, xAI, etc)
7. **New AI Agents** What new Agents are people building that the ecosystem is excited about (OpenClaw, Claude Code, Codex, etc)

For each news item:
- **Bold headline**
- Launch date or timeframe
- What it is and why it matters
- Technical details (how it works, what's new)
- **Tie to meetup speakers when relevant** (e.g., "Ruben will demo this at London")
- Real-world use cases or adoption metrics
- Security/cost implications if relevant
- Link to official announcement/docs

**Format:**
```markdown
### MCP Apps: Interactive UIs Inside AI Chat Windows

In December 2025, Anthropic donated the Model Context Protocol to the Agentic AI Foundation...

[Details about the technology, adoption, and impact]

**Postman was an early adopter.** [Connection to meetup demo]

This month, Ruben Casas will demonstrate **MCP Apps testing at our London meetup on February 12**.

[**Read the official announcement here**](https://example.com)
```

### 5. Events Section

```markdown
---

## **Attend an Agent & APIs Developer Meetup Near You!**
```

For each event:

```markdown
### US NYC — February 11, 5:30–7:30 p.m. EST

**[Venue Address]**

**Speakers:**

* **[Name]** ([Company]) — [Topic/Demo]
* **[Name]** ([Company]) — [Topic/Demo]
* **[Name]** ([Company]) — [Topic/Demo]

**What to expect:** [1-2 sentences about themes, topics, hands-on activities]

[**RSVP on Luma**](https://luma.com/event-id?utm_source=newsletter)

---
```

**Important:** Use flag emojis for cities (US GB IN DE NL)

### 6. Community Call-to-Action

```markdown
**Got Questions? Want to keep in touch?** Kindly reach out on the [Postman Discord Community](https://discord.gg/ajCXuHrXfV)

Can't wait to see you there!
```

### 7. Nerdy Disclaimer (Always Include at End)

```markdown
---

*This newsletter was crafted by humans and AI working together—because even our newsletters are built with the tools we talk about. Expect occasional dad jokes about APIs and the kind of technical accuracy you'd want from your CI/CD pipeline. Bugs? Let us know. We iterate fast.*
```

---

## Tone Guidelines

**Do:**
- Use "we" and "you" naturally
- Reference specific technical developments
- Name technologies and tools directly
- Share real use cases and patterns
- Keep sentences punchy and varied
- Be conversational but authoritative
- Show genuine enthusiasm for technical developments
- Include adoption metrics (downloads, usage stats)

**Don't:**
- Use "revolutionizing", "game-changing", "unlock", "supercharge"
- Say "don't miss out" or FOMO language
- Oversell the events—let the content speak for itself
- Use bullet points excessively—write like you're emailing a colleague
- Add emoji to every section (sparingly for flags/locations is fine)
- Use "leverage" as a verb
- Say "simply" or "just" when steps are complex

---

## Process

### 1. Fetch Events from Luma Calendar

```bash
# Use WebFetch to get event list from calendar:
# https://luma.com/calendar/cal-TGqTNpY4iyl7XYe
# Extract individual event URLs (e.g., https://luma.com/fifckjck)
```

### 2. Fetch Individual Event Pages

**CRITICAL:** Do not rely on calendar listing alone. Navigate to each event's individual page.

```bash
# For each event URL, use WebFetch to get full details:
# - Complete event description
# - ALL speakers mentioned (not just hosts)
# - Session topics and agenda
# - Partner organizations
# Extract: speaker names, titles, companies, and talk topics
```

### 3. Filter Events for Target Month

- If argument provided (e.g., "February"), use that month
- Otherwise, use events in the next 30-45 days
- Show 3-5 events maximum
- Include events from target month and next month if relevant

### 4. Search for Recent AI/API News

**Priority Search Topics:**
```bash
# Use WebSearch for each topic area:
# 1. "MCP Apps Model Context Protocol [month] 2026"
# 2. "skills.sh agent capabilities package manager [month] 2026"
# 3. "agent observability monitoring AI API [month] 2026"
# 4. "API security AI agents authentication [month] 2026"
# 5. "OpenAI Anthropic API updates [month] 2026"
# Focus on last 30 days, official sources preferred
```

**Look for:**
- MCP ecosystem updates (new MCP Apps, server implementations, tooling)
- Agent capability systems (skills, prompt libraries, tool registries)
- Observability platforms and patterns
- Security frameworks for agents
- Major API launches or breaking changes
- Enterprise adoption stories

### 5. Generate Newsletter

**Opening:**
- Start with standard header
- Title with current month/year
- Opening paragraph that ties recent news to meetup themes
- Mention speaker companies upfront

**News Section:**
- Lead with MCP/ecosystem developments (if any)
- Include 3-5 major items with full context
- Tie speakers to relevant news topics
- Link to official sources for each item
- Show adoption metrics where available

**Events:**
- Format each event cleanly with flag emoji
- List ALL speakers from event pages (not just hosts)
- Highlight what developers will learn
- Include "What to expect" for each event
- Add utm_source=newsletter to all Luma links

**Close:**
- Discord community link
- Nerdy disclaimer about human+AI generation

### 6. Output Format

- Save the finished newsletter as a Markdown file in the `/newsletter-output` directory. Create the directory if it doesn't exist.
- Prefix the filename with the current year and month in `YYYY-MM` format (e.g., `newsletter-output/2026-03-agents-and-apis.md`)
- Pure markdown
- Ready to copy into email or Luma announcement
- All event URLs include ?utm_source=newsletter parameter
- All news source links included
- Proper heading hierarchy (# for title, ## for sections, ### for subsections)

---

## Example Structure Reference

```markdown
Welcome to the **Agents & APIs Developer Newsletter** by Postman...

---

# **What's New in Agents & APIs — February 2026**

[Opening paragraph with context]

---

## **What's New in February?**

### MCP Apps: Interactive UIs Inside AI Chat Windows

[Full news item with technical details, adoption metrics, speaker tie-ins]

[**Read the official announcement**](https://link.com)

### Vercel Launches Skills.sh: npm for AI Agents

[Full news item with what, why, how, and impact]

[**Learn more here**](https://link.com)

---

### Agent Observability Becomes Critical

[Full news item with Gartner stats, tool comparisons, speaker reference]

---

## **Attend an Agent & APIs Developer Meetup Near You!**

### US NYC — February 11, 5:30–7:30 p.m. EST

**52 W 39th St, New York**

**Speakers:**
* **Kenneth Sinder** (Notion) — Notion's Agents SDK/API
* **Daniel Kimmelmann** (Postman) — Building MCP servers with Flows

**What to expect:** Live demos, SDK patterns, MCP server building.

[**RSVP on Luma**](https://luma.com/event?utm_source=newsletter)

---

**Got Questions?** Reach out on [Postman Discord](https://discord.gg/ajCXuHrXfV)

Can't wait to see you there!

---

*This newsletter was crafted by humans and AI working together—because even our newsletters are built with the tools we talk about...*
```

---

## Quality Checks

Before outputting the newsletter:

**Header & Structure:**
- [ ] Standard header included at start
- [ ] Title includes month and year
- [ ] Opening paragraph mentions speaker companies
- [ ] Nerdy disclaimer included at end

**Content Quality:**
- [ ] 3-5 news items with full technical context
- [ ] MCP/ecosystem news prioritized if available
- [ ] All news items have official source links
- [ ] Speakers tied to relevant news topics
- [ ] Adoption metrics included (downloads, usage, growth)

**Events:**
- [ ] All event links from individual event pages (not calendar)
- [ ] ALL speakers listed (not just hosts)
- [ ] Speaker names, companies, and topics included
- [ ] Flag emojis for each city
- [ ] All Luma links include ?utm_source=newsletter

**Tone:**
- [ ] Conversational but authoritative
- [ ] No marketing speak ("revolutionary", etc.)
- [ ] Technical details are accurate
- [ ] All claims have source links
- [ ] Discord link included

**Links:**
- [ ] All news sources linked with descriptive text
- [ ] Event URLs working and include UTM parameter
- [ ] Discord community link present
