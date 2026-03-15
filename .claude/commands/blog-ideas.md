---
name: blog-ideas
description: "Search trending topics in AI, APIs, and Postman.com to generate scored blog content ideas. Returns ideas ranked 0-100 based on trend potential, audience fit, and content gaps. Use when brainstorming what to write next."
argument-hint: "[focus area] (optional, e.g. 'MCP', 'API security', 'testing')"
---

# Blog Ideas Generator

Search for trending topics across AI, APIs, and Postman.com to surface blog content ideas ranked by their likelihood to trend well.

## Workflow

### Step 1: Gather Trending Topics

Run these searches **in parallel** using WebSearch:

**AI & Developer Trends:**
```
trending AI developer tools 2026
trending API development topics 2026
"developer experience" trends 2026
MCP Model Context Protocol latest news
AI agents API development
LLM API integration patterns
```

**API Industry Trends:**
```
API security trends 2026
GraphQL vs REST latest discussion
API gateway trends
API-first development trends
API testing automation trends
OpenAPI specification latest updates
```

**Postman-Specific:**
```
site:postman.com/blog latest
site:blog.postman.com latest
Postman new features 2026
Postman MCP server
Postman AI agent builder
Postman Flows automation
```

**Reddit/Community Pulse:**
```
site:reddit.com API development pain points 2026
site:reddit.com "Postman" developer workflow
site:reddit.com API testing best practices
site:dev.to API development trending
site:hackernews API tools
```

**If the user provided a focus area**, add targeted searches:
```
{focus area} trending 2026
{focus area} developer tutorial
{focus area} best practices latest
site:reddit.com {focus area} developer
```

### Step 2: Analyze Postman.com Content Gaps

Use WebFetch to check recent posts on:
- `https://blog.postman.com/` — scan the latest 10-15 posts to identify what's already been covered

Note which trending topics are **not yet covered** by the Postman blog — these represent content gaps and score higher.

### Step 3: Score Each Idea

For each blog idea, calculate a **Trend Score (0-100)** based on these weighted criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Search Volume & Buzz** | 25 pts | How much current discussion exists (Reddit threads, HN posts, tweets, search trends) |
| **Content Gap** | 25 pts | Not already covered well on postman.com/blog or by competitors. Fresh angle available |
| **Postman Relevance** | 20 pts | Can naturally showcase Postman features or tie into the Postman ecosystem |
| **Audience Fit** | 15 pts | Matches API developer audience interests (not too niche, not too broad) |
| **Timeliness** | 15 pts | Is this moment-dependent? Will it lose relevance if not published soon? |

**Score Bands:**
- **80-100**: Publish ASAP — high trend momentum, strong content gap, timely
- **60-79**: Strong idea — good potential, plan for this month
- **40-59**: Solid idea — worth writing but no urgency
- **20-39**: Low priority — limited trending signals or already well-covered
- **0-19**: Skip — low interest or poor fit

### Step 4: Output Format

Present results sorted by score (highest first):

```markdown
# Blog Ideas Report

**Generated:** [date]
**Focus Area:** [user-specified or "General AI & API trends"]
**Sources Scanned:** [count of searches performed]

---

## Top Ideas

### 1. [Blog Title Idea] — Score: XX/100

| Criterion | Score | Notes |
|-----------|-------|-------|
| Search Volume & Buzz | XX/25 | [why] |
| Content Gap | XX/25 | [why] |
| Postman Relevance | XX/20 | [why] |
| Audience Fit | XX/15 | [why] |
| Timeliness | XX/15 | [why] |

**Angle:** [1-2 sentences on the recommended angle/hook for this post]
**Target keyword:** [primary SEO keyword]
**Why now:** [what makes this timely]
**Postman tie-in:** [how to naturally incorporate Postman]

---

[Repeat for each idea, aim for 8-12 ideas]

---

## Quick Reference

| Rank | Title | Score | Urgency |
|------|-------|-------|---------|
| 1 | [Title] | XX/100 | 🔴 Publish ASAP / 🟡 This month / 🟢 Backlog |
| 2 | [Title] | XX/100 | ... |
| ... | ... | ... | ... |

---

## Trends to Watch

[2-3 emerging topics that don't have enough signal yet for a full blog post but are worth monitoring]
```

### Step 5: Save Output

Save the report to `blog-output/blog-ideas-YYMMDD.md` where YYMMDD is the current date. Create the `blog-output` directory if it doesn't exist.

## Important Guidelines

- **Be specific with titles** — "How to Build an MCP Server for Your REST API" beats "MCP Overview"
- **Favor tutorials and how-tos** — developer audiences engage most with actionable content
- **Look for controversy or debate** — topics where developers disagree tend to drive traffic (e.g., "REST vs GraphQL in 2026")
- **Check for recency** — a topic trending 6 months ago may be stale; prioritize what's buzzing *now*
- **Consider series potential** — note if an idea could spawn a multi-part series
- **Cross-reference sources** — a topic trending on Reddit AND Hacker News AND dev.to scores higher than one source alone
- **Postman integration should feel natural** — forced product placement lowers content quality. If Postman doesn't fit an idea, still include it but note the weak tie-in in the score
