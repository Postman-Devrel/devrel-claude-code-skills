---
name: influencer-autoagent
description: "Find and rank developer influencers for an upcoming product launch. Searches across X/Twitter, YouTube, LinkedIn, Substack, Dev.to, and GitHub to identify technically credible voices in AI, APIs, agentic workflows, MCP, and developer tooling. Returns a scored and ranked list of influencer candidates."
argument-hint: "[product name or focus area] (optional, defaults to 'Autonomous Agent')"
allowed-tools: ["WebSearch", "WebFetch", "Read", "Write"]
---

# Influencer Finder for Product Launches

Search for and evaluate developer influencers who are strong candidates for amplifying an upcoming product launch. Default product context: **Postman Autonomous Agent** — an AI agent/team that, given a requirement or PRD, autonomously discovers APIs from the Postman Public API Network, finds relevant public MCPs, and sets up an entire suite of API services using the full Postman platform.

## Product Context

Read the full product PRD from `@skills/influencer-autoagent/autonomous-agent-prd.md` and use it to inform search queries, scoring criteria, and topic alignment evaluation.

If the user provides a different product name or focus area via argument, adapt the search queries and alignment criteria accordingly.

## Workflow

### Step 1: Search for Influencer Candidates

Run these searches **in parallel** using WebSearch to build a broad candidate list:

**AI & Agentic Workflow Influencers:**
```
top developer influencers AI agents 2025 2026
developer advocates AI agentic workflows YouTube Twitter
"AI agent" developer content creator tutorial
influential developers Claude Code MCP agentic
top technical YouTubers AI developer tools 2026
developer influencers autonomous AI coding agents
developer content creator OpenAI Codex N8N agent workflow
```

**API & Developer Tooling Influencers:**
```
top API developer influencers Twitter YouTube 2025 2026
developer advocates API tooling Postman
influential developers API-first development content
API developer content creators tutorials
developer influencers REST GraphQL API testing
```

**MCP & LLM Ecosystem Influencers:**
```
MCP Model Context Protocol developer content creators
developers creating MCP tutorials YouTube
influential developers LLM tooling integrations
developer influencers Claude Anthropic content
```

**Platform-Specific Searches:**
```
site:youtube.com AI agent developer tutorial 2025 2026 popular
site:substack.com AI developer tools newsletter popular
site:dev.to AI agents API development top authors
site:linkedin.com "developer advocate" AI agents API
top developer Twitter accounts AI API 2026
```

**Recent AI Launch Coverage (credibility signal):**
```
developer influencer reviewed Claude 4 Sonnet Opus launch
developer YouTuber reviewed GPT-4o launch demo
developer content creator Llama 3 Meta launch review
developers who demo AI model launches technical review
```

### Step 2: Deep-Dive on Candidates

For each promising candidate found in Step 1, use WebSearch and WebFetch to gather:

1. **Profile info:** Name, handle(s), platform(s), bio, follower/subscriber counts
2. **Content audit (last 6 months):**
   - Count of AI-related posts/videos — specifically look for content on AI agents (Claude Code skills, agent teams, autonomous agents, OpenAI Codex, N8N, etc.)
   - Count of API/developer tooling posts
   - Major AI launches they covered (OpenAI, Anthropic, Google, Meta, Mistral)
   - Content format: tutorials, demos, code walkthroughs, benchmarks, opinion pieces
3. **Engagement metrics:**
   - Average replies/comments per post
   - Average reposts/shares per post
   - Discussion quality (meaningful technical replies vs. spam)
4. **Technical credibility:**
   - GitHub profile and repos (if available)
   - Professional background (current/past roles)
   - Open-source contributions
   - Speaking engagements or conference talks
5. **Platform presence:**
   - Primary platform and secondary platforms
   - Publishing cadence (daily, weekly, biweekly)
   - Community involvement (Discord, Hugging Face, open-source)
6. **Brand safety:**
   - Check for undisclosed paid promotions
   - Check for controversial takes that could be a brand risk
   - General tone: constructive vs. purely contrarian vs. hype-driven

### Step 3: Score Each Candidate

Evaluate each candidate using this **Influencer Score (0-100)** rubric:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Developer Audience** | 15 pts | Audience is primarily developers/engineers/technical practitioners (not general tech press or consumers). Engagement rate matters more than raw follower count |
| **Technical Content Quality** | 15 pts | Publishes tutorials, demos, code walkthroughs, or build-along videos. Content goes beyond press release regurgitation — they demo, critique, or build |
| **AI Launch Coverage** | 25 pts | Covered 2-3+ major AI launches in the past 6 months with original technical content (not just reshares) |
| **Platform Reach & Cadence** | 10 pts | Active on 1+ developer-centric platforms with consistent publishing. Bonus for multi-platform presence and developer community activity |
| **Technical Credibility** | 15 pts | Verifiable technical background (engineer, researcher, builder). Referenced by other credible developers. Independently tests and forms opinions |
| **Amplification Behavior** | 10 pts | Posts about new launches within 24-72 hours. Creates original content around launches. Posts generate meaningful discussion |
| **Topic Alignment** | 10 pts | Has covered APIs, agentic workflows, developer tooling, AI/LLM, Claude Code, MCP, or adjacent topics. US/Europe primary audience. Constructive, technically credible tone |

**Score Bands:**
- **85-100**: Tier 1 — High-priority outreach. Strong alignment, proven amplification, technically credible
- **70-84**: Tier 2 — Strong candidate. Good fit with minor gaps (e.g., hasn't covered APIs specifically but strong on AI agents)
- **55-69**: Tier 3 — Worth considering. Decent reach and credibility but weaker alignment or engagement
- **40-54**: Tier 4 — Watch list. Emerging voice or partial fit — revisit for future launches
- **Below 40**: Not recommended for this launch

### Step 4: Reality Check

Before finalizing rankings, apply these two filters to every candidate:

**Budget Feasibility ($2,000 cap):**
We are aiming to pay each influencer no more than **$2,000** for them to create content. Evaluate whether the candidate realistically fits this budget based on:
- Follower/subscriber count (creators with 500K+ followers on a primary platform likely charge well above this)
- Previous sponsored content signals (frequent brand deals suggest established rates)
- Platform norms (YouTube sponsorships tend to cost more than Twitter/Substack collaborations)
- Engagement-to-follower ratio (micro-influencers with high engagement are often more budget-friendly)

Mark candidates as: **Within budget**, **Borderline** (might negotiate), or **Likely over budget**. Candidates marked "Likely over budget" should be flagged but can still be ranked — note the budget risk in their detail block.

**Will They Care?**
There are many releases from major AI players competing for influencer attention. Assess whether this influencer would realistically be interested in collaborating with Postman specifically:
- Do they cover developer tooling / API platforms, or only foundation model releases?
- Have they shown interest in "building with AI" rather than just "AI model news"?
- Is Postman's product category (API platform + AI agents) something they've touched before?
- Would this launch give them something novel to demo or build with?

Mark candidates as: **High interest**, **Moderate interest**, or **Low interest**. Low-interest candidates should be deprioritized regardless of score.

### Step 5: Output Format

Present results sorted by score (highest first):

```markdown
# Influencer Candidates — Postman Autonomous Agent Launch

**Generated:** [date]
**Product:** Postman Autonomous Agent
**Candidates Evaluated:** [number]
**Sources Searched:** X/Twitter, YouTube, LinkedIn, Substack, Dev.to, GitHub

---

## Scoring Rubric

| Criterion | Max Points | What We Looked For |
|-----------|-----------|-------------------|
| Developer Audience | 15 | Primarily dev/eng followers; engagement rate over raw count |
| Technical Content Quality | 15 | Tutorials, demos, code walkthroughs; builds with the tech, not just reports on it |
| AI Launch Coverage | 25 | 2-3+ major AI launches covered in past 6 months with original content |
| Platform Reach & Cadence | 10 | Active on dev platforms; consistent publishing; multi-platform bonus |
| Technical Credibility | 15 | Verifiable eng/research background; cited by peers; independent opinions |
| Amplification Behavior | 10 | Posts within 24-72hrs of launches; creates original content; sparks discussion |
| Topic Alignment | 10 | Covers APIs, agentic AI, dev tooling, MCP, Claude Code; US/EU audience; constructive tone |

---

## Candidate Rankings

A single table of all candidates sorted by score, grouped by tier. Profile links point to each candidate's primary platform.

| Rank | Name | Profile | Score | Tier | Primary Platform | Key Strength | Budget | Interest | Outreach Angle | Brand Safety |
|------|------|---------|-------|------|-----------------|--------------|--------|----------|----------------|--------------|
| | | | | **Tier 1 — High-Priority Outreach (85-100)** | | | | | |
| 1 | [Name] | [profile link] | XX/100 | 1 | [platform] | [key strength] | [Within/Borderline/Over] | [High/Moderate/Low] | [suggested approach] | [flags or all clear] |
| 2 | [Name] | [profile link] | XX/100 | 1 | [platform] | [key strength] | [Within/Borderline/Over] | [High/Moderate/Low] | [suggested approach] | [flags or all clear] |
| | | | | **Tier 2 — Strong Candidates (70-84)** | | | | | |
| 3 | [Name] | [profile link] | XX/100 | 2 | [platform] | [key strength] | [Within/Borderline/Over] | [High/Moderate/Low] | [suggested approach] | [flags or all clear] |
| | | | | **Tier 3 — Worth Considering (55-69)** | | | | | |
| 4 | [Name] | [profile link] | XX/100 | 3 | [platform] | [key strength] | [Within/Borderline/Over] | [High/Moderate/Low] | [suggested approach] | [flags or all clear] |
| | | | | **Tier 4 — Watch List (40-54)** | | | | | |
| 5 | [Name] | [profile link] | XX/100 | 4 | [platform] | [key strength] | [Within/Borderline/Over] | [High/Moderate/Low] | [gap to close] | [flags or all clear] |

For each candidate, also include a detail block below the table:

---

### [Rank]. [Name] — Score: XX/100 | Tier [N]

**Profile:** [link to primary profile]
**Additional Platforms:** [secondary platform links]
**Followers/Subscribers:** [counts per platform]
**Publishing Cadence:** [frequency]

| Criterion | Score | Evidence |
|-----------|-------|----------|
| Developer Audience | XX/15 | [specific evidence] |
| Technical Content Quality | XX/15 | [specific evidence] |
| AI Launch Coverage | XX/25 | [launches covered with links if available] |
| Platform Reach & Cadence | XX/10 | [specific evidence] |
| Technical Credibility | XX/15 | [background, repos, citations] |
| Amplification Behavior | XX/10 | [specific evidence] |
| Topic Alignment | XX/10 | [relevant topics covered] |

**Why this person:** [2-3 sentences on why they're a strong fit for this specific launch]
**Recent relevant content:** [1-3 examples with links]
**Budget assessment:** [Within budget / Borderline / Likely over budget — with reasoning based on follower count, platform, and sponsorship signals]
**Interest assessment:** [High / Moderate / Low — with reasoning on whether they'd realistically engage with a Postman AI agent launch]
**Brand safety notes:** [details if flagged in summary table]

[Repeat for each candidate across all tiers. Tier 3-4 candidates can use a condensed version with fewer evidence details.]

---

## Outreach Strategy Notes

### Recommended Approach by Tier
- **Tier 1:** [suggested outreach strategy — early access, exclusive briefings, etc.]
- **Tier 2:** [suggested outreach strategy]
- **Tier 3:** [suggested outreach strategy]

### Timing Recommendations
- [Suggestions on when to reach out relative to launch]
- [Sequencing recommendations — who gets early access first]

### Content Collaboration Ideas
- [Ideas for how influencers could create content around the launch]
- [Formats that would work well: live demos, tutorials, review videos, etc.]

---

## Methodology Notes
- **Search date:** [date]
- **Search sources:** [list of platforms and queries used]
- **Evaluation period:** Content from the past 6 months was assessed
- **Limitations:** [any data gaps — e.g., private accounts, platforms not searched, engagement metrics that couldn't be verified]
- **Bias notes:** Candidates with stronger web presence are naturally easier to find and evaluate. Emerging voices with smaller followings but high engagement may be underrepresented
```

### Step 6: Save Output

Save the report to `influencer-output/influencer-candidates-YYMMDD.md` where YYMMDD is the current date (e.g., `influencer-output/influencer-candidates-260325.md` for March 25, 2026). Create the `influencer-output/` directory if it doesn't exist.

## Important Guidelines

- **Aim for 15-25 candidates** across all tiers — enough breadth to be useful, not so many that quality drops
- **Verify claims** — don't assume someone is technical just because their bio says so. Look for actual code, repos, or technical content
- **Engagement over vanity metrics** — 5,000 followers with 100 meaningful replies per post beats 500,000 followers with 10 generic comments
- **Recency matters** — someone who was active in AI content 2 years ago but hasn't posted in 6 months is not a good candidate
- **Geographic focus** — prioritize US and European audience, but don't exclude strong candidates from other regions if their content is in English and reaches these markets
- **No marketing language** in the report — keep it factual and evidence-based
- **Be honest about gaps** — if you can't verify engagement metrics or background, note it rather than guessing
- **Brand safety is non-negotiable** — flag any concerns, even for high-scoring candidates
- **Diverse voices** — aim for diversity in background, platform, content style, and audience segment
- **Budget-conscious** — prioritize candidates likely within the $2,000 budget. Micro-influencers with high engagement and strong topic alignment often deliver better ROI than big names who won't engage at this price point
- **Realistic interest** — deprioritize candidates who only cover foundation model releases and have never touched developer tooling or API platforms. The best candidates are builders who would genuinely want to demo the product
