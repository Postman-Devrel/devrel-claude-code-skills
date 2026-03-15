---
name: sentiment-competitors
description: Analyze Reddit comments about API developer tools and generate sentiment rankings. Searches Reddit for discussions about Postman, Apigee, Bruno, HTTPie, Insomnia, RapidAPI (includes Paw), Yaak, and Hopscotch. Also analyzes how AI coding agents (Claude Code, Cursor, GitHub Copilot) and MCP (Model Context Protocol) are disrupting API testing workflows. Categorizes sentiment by key capabilities (API Development, Pricing, Offline Storage, Collaboration, API Management, Uptime Monitoring, Security/Enterprise) and provides rankings from 0-100 with summarized feedback. Use when you need competitive intelligence or want to understand developer sentiment about API tools.
---

# Competitor Sentiment Analyzer

Analyze Reddit discussions about API developer tools to understand competitive positioning and developer sentiment.

## Reddit API Configuration

This skill uses the Reddit API for comprehensive data access. You need Reddit API credentials.

### Setup Instructions

1. **Create a Reddit App:**
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app..." at the bottom
   - Select "script" as the app type
   - Name: `competitor-sentiment-analyzer` (or any name)
   - Redirect URI: `http://localhost:8080` (required but not used for script apps)
   - Click "create app"

2. **Get Your Credentials:**
   - `client_id`: The string under your app name (e.g., `Ab1Cd2Ef3Gh4Ij`)
   - `client_secret`: The "secret" field

3. **Set Environment Variables:**
   ```bash
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   export REDDIT_USER_AGENT="competitor-sentiment-analyzer/1.0"
   ```

   Or create a `.env` file in your project:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USER_AGENT=competitor-sentiment-analyzer/1.0
   ```

### Authentication Flow

Before making API calls, obtain an access token:

```bash
# Get OAuth token (app-only auth for read-only access)
curl -X POST https://www.reddit.com/api/v1/access_token \
  -u "${REDDIT_CLIENT_ID}:${REDDIT_CLIENT_SECRET}" \
  -H "User-Agent: ${REDDIT_USER_AGENT}" \
  -d "grant_type=client_credentials"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "scope": "*"
}
```

Store the token for subsequent requests:
```bash
export REDDIT_ACCESS_TOKEN="eyJhbGc..."
```

## Workflow

### Step 1: Choose Search Method

**REQUIRED**: Before starting, ask the user which search method to use:

Use the AskUserQuestion tool with these options:

| Option | Label | Description |
|--------|-------|-------------|
| **Web Search** | Web Search (No setup required) | Uses web search to find Reddit discussions. Quick to start, no API credentials needed. May have less comprehensive results and limited ability to fetch full comment threads. Best for quick competitive snapshots. |
| **Reddit API** | Reddit API (More comprehensive) | Uses Reddit's official API for deeper access. Requires API credentials setup. Provides full comment threads, better pagination, and more reliable results. Best for thorough analysis. |

**Tradeoffs Summary:**

| Factor | Web Search | Reddit API |
|--------|------------|------------|
| **Setup** | None - works immediately | Requires Reddit app registration and credentials |
| **Data Quality** | Summarized results, may miss context | Full posts and comment threads |
| **Rate Limits** | Subject to web search limits | 60 requests/minute with proper auth |
| **Comment Access** | Limited to what appears in search results | Can fetch full comment trees for any post |
| **Pagination** | Limited | Full pagination support with `after` token |
| **Best For** | Quick insights, first-time users | Comprehensive analysis, regular use |

### Step 2: Gather Parameters

**REQUIRED**: After selecting the search method, ask the user:
- How many days back should I search for Reddit comments? (e.g., 7, 30, 90 days)

Use the AskUserQuestion tool with options like:
- 7 days (Recent discussions)
- 30 days (Past month)
- 90 days (Quarterly view)
- Custom (let user specify)

### Step 3: Search Reddit

Based on the user's choice in Step 1, use either the Web Search or Reddit API approach.

---

## Option A: Web Search Workflow

If the user selected **Web Search**, use the WebSearch tool to find Reddit discussions.

### Web Search Queries

Execute these searches using the WebSearch tool:

**Tool-specific searches:**
```
site:reddit.com Postman API testing [time period]
site:reddit.com Apigee API gateway [time period]
site:reddit.com Bruno API client [time period]
site:reddit.com HTTPie API client CLI [time period]
site:reddit.com Insomnia API [time period]
site:reddit.com RapidAPI OR "Paw API" Mac [time period]
site:reddit.com Yaak API client [time period]
site:reddit.com Hopscotch API client [time period]
```

**Comparison searches:**
```
site:reddit.com "Postman vs" API [time period]
site:reddit.com Postman alternatives [time period]
site:reddit.com "best API testing tool" [time period]
site:reddit.com API client comparison [time period]
```

**AI Agents & MCP searches:**
```
reddit Claude Code API testing MCP [year]
reddit "Claude Code" API development testing [year]
reddit MCP server API testing developer workflow [year]
reddit developers replacing Postman with AI CLI [year]
"Claude Code" vs Postman API testing developer workflow [year]
reddit Cursor Copilot API testing workflow [year]
```

**Time period mapping for search queries:**
| User Selection | Add to Query |
|----------------|--------------|
| 7 days | `after:2026-01-16` (adjust date dynamically) |
| 30 days | `after:2025-12-24` (adjust date dynamically) |
| 90 days | `after:2025-10-25` (adjust date dynamically) |

### Web Search Limitations

- Results are summarized, may miss nuanced comments
- Cannot easily fetch full comment threads
- May return fewer total results than API
- Some posts may be truncated

### Maximizing Web Search Results

1. Run multiple targeted searches per tool
2. Use WebFetch to visit high-value Reddit threads found in search results
3. Focus on posts with high engagement mentioned in search snippets
4. Cross-reference comparison threads for richer sentiment data

---

## Option B: Reddit API Workflow

If the user selected **Reddit API**, follow the API-based workflow below.

### Search Reddit via API

Use the Reddit API to search for discussions. Focus on developer-focused subreddits:

**Target Subreddits:**
- r/webdev
- r/programming
- r/node
- r/javascript
- r/devops
- r/api
- r/softwarearchitecture

**Reddit API Search Endpoint:**

```bash
# Search across all of Reddit
curl -X GET "https://oauth.reddit.com/search?q=QUERY&sort=new&t=TIME_PERIOD&limit=100" \
  -H "Authorization: Bearer ${REDDIT_ACCESS_TOKEN}" \
  -H "User-Agent: ${REDDIT_USER_AGENT}"
```

**Parameters:**
- `q`: Search query (URL encoded)
- `sort`: `new`, `relevance`, `hot`, `top`, `comments`
- `t`: Time period - `hour`, `day`, `week`, `month`, `year`, `all`
- `limit`: Results per request (max 100)
- `after`: Pagination token for next page

**Search queries to execute for each tool:**

```bash
# Tool-specific searches
curl "https://oauth.reddit.com/search?q=Postman%20API&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=Apigee&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=Bruno%20API%20client&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=HTTPie%20API&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=Insomnia%20API&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=Hopscotch%20API&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=Yaak%20API%20client&sort=new&t=month&limit=100" ...

# RapidAPI (includes Paw) - search for both terms and combine results
curl "https://oauth.reddit.com/search?q=RapidAPI&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=Paw%20API%20Mac&sort=new&t=month&limit=100" ...

# Comparison searches
curl "https://oauth.reddit.com/search?q=Postman%20vs&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=Postman%20alternatives&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=best%20API%20testing%20tool&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=API%20client%20comparison&sort=new&t=month&limit=100" ...

# AI Agents & MCP searches
curl "https://oauth.reddit.com/search?q=Claude%20Code%20API%20testing%20MCP&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=MCP%20server%20API%20testing&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=AI%20coding%20agent%20API%20testing&sort=new&t=month&limit=100" ...
curl "https://oauth.reddit.com/search?q=Cursor%20Copilot%20API%20testing&sort=new&t=month&limit=100" ...
```

**Subreddit-specific search:**

```bash
# Search within a specific subreddit
curl "https://oauth.reddit.com/r/webdev/search?q=Postman&restrict_sr=true&sort=new&t=month&limit=100" ...
```

**Fetching comments from a post:**

```bash
# Get post with all comments (replace POST_ID with actual ID)
curl "https://oauth.reddit.com/comments/POST_ID?sort=top&limit=500" \
  -H "Authorization: Bearer ${REDDIT_ACCESS_TOKEN}" \
  -H "User-Agent: ${REDDIT_USER_AGENT}"
```

**Time period mapping:**
| User Selection | API `t` Parameter |
|----------------|-------------------|
| 7 days | `week` |
| 30 days | `month` |
| 90 days | `year` (then filter by date) |

**Rate Limits:**
- Reddit API allows 60 requests per minute
- Add a small delay between requests if needed
- Use pagination (`after` token) to get more than 100 results

### Step 4: Analyze Comments (Both Methods)

For each tool, categorize comments by these **Key Capability Areas**:

| Category | What to Look For |
|----------|------------------|
| **API Development & Testing** | Ease of use, request building, debugging, GraphQL support, WebSocket testing |
| **Pricing Model** | Cost complaints, value perception, free tier limitations, enterprise pricing |
| **Offline/Local Storage** | Cloud sync requirements, local-first mentions, privacy concerns, Git integration |
| **Team Collaboration** | Sharing collections, workspace features, team workflows, permissions |
| **API Management** | Gateway features, lifecycle management, versioning, documentation generation |
| **Uptime Monitoring** | Monitoring capabilities, alerting, scheduled tests, health checks |
| **Security / Enterprise** | SSO, compliance, audit logs, self-hosting, data residency |

### Step 5: Sentiment Scoring

For each tool and category, calculate a **Relative Strength Score (0-100)**:

**Scoring Methodology:**
- **0-25**: Predominantly negative sentiment (complaints, frustrations, switching away)
- **26-50**: Mixed/neutral sentiment (some issues mentioned, but functional)
- **51-75**: Positive sentiment (recommendations, praise, satisfaction)
- **76-100**: Strongly positive (enthusiastic endorsements, preferred choice)

**Factors to consider:**
- Volume of positive vs negative mentions
- Strength of language used
- Recency bias (newer comments weighted slightly higher)
- Context (is the tool being recommended or complained about?)
- Comparative mentions (when tool X is preferred over tool Y)

### Step 6: Output Format

**REQUIRED**: Save the report to a file named `sentiment-analysis-YYMMDD.md` where YYMMDD is the current date (e.g., `sentiment-analysis-260127.md` for January 27, 2026). Save the file in the current working directory.

Present results in this structure:

```markdown
# API Tools Competitor Sentiment Analysis

**Analysis Period:** [X] days (from [date] to [date])
**Total Comments Analyzed:** [number]
**Subreddits Searched:** [list]

---

## Executive Summary

### Key Takeaways
- [3-5 bullet points highlighting the most important findings]
- [Focus on actionable insights for product and strategy teams]
- [Include any surprising or counter-intuitive discoveries]

### Market Sentiment Snapshot
[1-2 sentences describing the overall competitive landscape and where Postman stands]

### Top Trends
1. **[Trend Name]**: [Brief description of emerging pattern in developer sentiment]
2. **[Trend Name]**: [Brief description of emerging pattern in developer sentiment]
3. **[Trend Name]**: [Brief description of emerging pattern in developer sentiment]

### Recommended Actions
- **Immediate**: [Quick wins or urgent items based on sentiment]
- **Short-term**: [Actions for the next quarter]
- **Strategic**: [Longer-term considerations]

---

## Overall Rankings

| Rank | Tool | Overall Score | Trend |
|------|------|---------------|-------|
| 1 | [Tool] | [XX]/100 | ↑/↓/→ |
| 2 | [Tool] | [XX]/100 | ↑/↓/→ |
| ... | ... | ... | ... |

---

## Detailed Breakdown by Tool

### [Tool Name]
**Overall Score: [XX]/100**

| Category | Score | Summary |
|----------|-------|---------|
| API Development & Testing | [XX]/100 | [1-2 sentence summary] |
| Pricing Model | [XX]/100 | [1-2 sentence summary] |
| Offline/Local Storage | [XX]/100 | [1-2 sentence summary] |
| Team Collaboration | [XX]/100 | [1-2 sentence summary] |
| API Management | [XX]/100 | [1-2 sentence summary] |
| Uptime Monitoring | [XX]/100 | [1-2 sentence summary] |
| Security / Enterprise | [XX]/100 | [1-2 sentence summary] |

**Key Positive Themes:**
- [Bullet point summaries of positive sentiment]

**Key Concerns:**
- [Bullet point summaries of negative sentiment]

**Notable Quotes:**
> "[Direct quote from Reddit]" - r/[subreddit]

---

[Repeat for each tool]

---

## Category Leaderboards

| Tool | API Dev | Pricing | Offline | Collab | API Mgmt | Monitoring | Security |
|------|---------|---------|---------|--------|----------|------------|----------|
| [Tool 1] | [XX] | [XX] | [XX] | [XX] | [XX] | [XX] | [XX] |
| [Tool 2] | [XX] | [XX] | [XX] | [XX] | [XX] | [XX] | [XX] |
| ... | ... | ... | ... | ... | ... | ... | ... |

*Scores out of 100. API Dev = API Development & Testing, Collab = Team Collaboration, API Mgmt = API Management*

---

## Competitive Insights

### Postman Position
[2-3 paragraphs analyzing Postman's competitive position based on the sentiment data]

### Emerging Threats
[Analysis of tools gaining positive sentiment momentum]

### Opportunities
[Areas where competitors are weak that Postman could capitalize on]

---

## AI Agents & MCP: The Emerging Disruption Layer

[Analyze how AI coding agents and MCP are reshaping API testing workflows. This section should NOT score AI agents as direct competitors but instead analyze them as a workflow-level disruption. Cover:]

### What's Happening
[How developers are using AI agents (Claude Code, Cursor, Copilot) for API testing tasks. Volume and nature of discussion.]

### Claude Code's Role in API Workflows
[Specific API testing capabilities: natural language test execution, MCP server consumption, integration with Postman via MCP]

### Postman's Strategic Response
[How Postman is adapting: MCP server, AI Agent Builder, MCP Generator. Assess whether the response is adequate.]

### The "Postman for MCP" Category
[Emerging tools built specifically for testing MCP servers (e.g., Hoot). New category formation.]

### Developer Sentiment
[How developers view the relationship between AI agents and API clients: complementary vs competitive. What the discussion patterns reveal.]

### Implications for Postman
[Risk/opportunity matrix: ad-hoc testing, test automation, API discovery, developer onboarding, collection management]

### Key Takeaway
[1 paragraph synthesis: workflow disruption vs tool replacement, and what it means for Postman's strategy]

---

## Methodology Notes
- Search method used: [Web Search / Reddit API]
- Search queries used: [list]
- Comments excluded: [spam, off-topic, etc.]
- Limitations: [any data gaps or caveats]
```

## Tools to Analyze

### API Clients & Platforms (Head-to-Head Comparison)
1. **Postman** - The market leader in API development platforms
2. **Apigee** - Google Cloud's API management platform
3. **Bruno** - Open-source, offline-first API client
4. **HTTPie** - Developer-friendly CLI and desktop HTTP client
5. **Insomnia** - Kong's API client with GraphQL focus
6. **RapidAPI** (includes Paw) - API marketplace, testing platform, and native macOS client
7. **Yaak** - Lightweight API client from the original Insomnia developer
8. **Hopscotch** - Open-source, web-based API client

### AI Agents & MCP (Disruption Analysis - Separate Section)
9. **Claude Code** - Anthropic's terminal-first AI coding agent with MCP support. Analyze as a workflow-level disruptor, not a direct API client competitor. Focus on: how developers use it for API testing, MCP integration with Postman, and whether it's replacing or complementing traditional API clients.
10. **Cursor** - AI-first IDE. Note mentions in context of API testing workflows.
11. **GitHub Copilot** - Microsoft's AI coding assistant. Note mentions in context of API testing workflows.
12. **MCP ecosystem** - The Model Context Protocol as a standard. Analyze how MCP servers (Postman MCP, Apidog MCP, etc.) are changing tool integration patterns and whether new "Postman for MCP" tools are emerging.

## Key Capability Categories

1. **API Development & Testing** - Core functionality for building and testing APIs
2. **Pricing Model** - Cost, value, free tier, enterprise pricing
3. **Offline/Local Storage** - Local-first, no cloud requirement, Git-friendly
4. **Team Collaboration** - Sharing, workspaces, team workflows
5. **API Management** - Gateway, lifecycle, versioning, documentation
6. **Uptime Monitoring** - Scheduled tests, alerts, health checks
7. **Security / Enterprise** - SSO, compliance, self-hosting, audit

## Important Guidelines

- **Be objective**: Report sentiment as found, even if negative about Postman
- **Cite sources**: Include subreddit names and paraphrase or quote comments
- **Note volume**: Distinguish between many mentions vs few mentions
- **Identify trends**: Note if sentiment is improving or declining
- **Context matters**: A complaint in a "what's wrong with X" thread differs from unsolicited criticism
- **Recency**: Weight recent comments more heavily but note historical trends

## Example Workflows

### Web Search Example Workflow

```
1. Ask user: "Which search method would you like to use?"
   - User selects: "Web Search (No setup required)"

2. Ask user: "How many days back should I search?"
   - User selects: "30 days"

3. Execute WebSearch queries (run in parallel):
   - "reddit Postman API testing [year]"
   - "reddit Apigee API gateway [year]"
   - "reddit Bruno API client [year]"
   - "reddit HTTPie API client CLI [year]"
   - "reddit Insomnia API client [year]"
   - "reddit RapidAPI Paw API client [year]"
   - "reddit Yaak API client [year]"
   - "reddit Hoppscotch API client [year]"

4. Execute comparison searches:
   - "reddit Postman alternatives [year] best API client"
   - "reddit best API testing tool [year] comparison"
   - "reddit Postman vs API [year]"

5. Execute AI/MCP searches:
   - "reddit Claude Code API testing MCP [year]"
   - "Claude Code vs Postman API testing developer workflow [year]"
   - "MCP server API testing replacing Postman developer workflow [year]"
   - "reddit developers replacing Postman with AI CLI [year]"

6. For high-value threads found, use WebFetch to get full content

7. Extract and categorize sentiment from results

8. Calculate scores based on sentiment distribution

9. Generate comprehensive report and save to sentiment-analysis-YYMMDD.md
```

### Reddit API Example Workflow

```
1. Ask user: "Which search method would you like to use?"
   - User selects: "Reddit API (More comprehensive)"

2. Verify Reddit API credentials are configured:
   - Check for REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET env vars
   - If missing, prompt user to set them up

3. Authenticate and get access token:
   curl -X POST https://www.reddit.com/api/v1/access_token \
     -u "${REDDIT_CLIENT_ID}:${REDDIT_CLIENT_SECRET}" \
     -H "User-Agent: ${REDDIT_USER_AGENT}" \
     -d "grant_type=client_credentials"

4. Ask user: "How many days back should I search?"
   - User selects: "30 days"

5. Search for each tool (parallel where possible):
   - Postman: /search?q=Postman%20API&sort=new&t=month
   - Apigee: /search?q=Apigee&sort=new&t=month
   - Bruno: /search?q=Bruno%20API%20client&sort=new&t=month
   - HTTPie: /search?q=HTTPie%20API&sort=new&t=month
   - Insomnia: /search?q=Insomnia%20API&sort=new&t=month
   - RapidAPI: /search?q=RapidAPI&sort=new&t=month AND /search?q=Paw%20API&sort=new&t=month
   - Yaak: /search?q=Yaak%20API%20client&sort=new&t=month
   - Hopscotch: /search?q=Hopscotch%20API&sort=new&t=month

6. Search for comparison discussions:
   - /search?q=Postman%20vs&sort=new&t=month
   - /search?q=Postman%20alternatives&sort=new&t=month
   - /search?q=best%20API%20testing%20tool&sort=new&t=month

7. Search for AI/MCP discussions:
   - /search?q=Claude%20Code%20API%20testing%20MCP&sort=new&t=month
   - /search?q=MCP%20server%20API%20testing&sort=new&t=month
   - /search?q=AI%20coding%20agent%20API%20testing&sort=new&t=month

8. For high-engagement posts, fetch full comments:
   - /comments/{post_id}?sort=top&limit=500

9. Extract and categorize sentiment from comments

10. Calculate scores based on sentiment distribution

11. Generate comprehensive report and save to sentiment-analysis-YYMMDD.md
```

## API Response Structure

**Search results:**
```json
{
  "data": {
    "children": [
      {
        "data": {
          "id": "abc123",
          "title": "Post title",
          "selftext": "Post body text",
          "subreddit": "webdev",
          "score": 142,
          "num_comments": 87,
          "created_utc": 1705881600,
          "permalink": "/r/webdev/comments/abc123/post_title/"
        }
      }
    ],
    "after": "t3_xyz789"  // pagination token
  }
}
```

**Comments structure:**
```json
[
  { "data": { /* post data */ } },
  {
    "data": {
      "children": [
        {
          "data": {
            "body": "Comment text here",
            "score": 45,
            "author": "username",
            "created_utc": 1705882000,
            "replies": { /* nested replies */ }
          }
        }
      ]
    }
  }
]
```

## Output Expectations

- Provide actionable competitive intelligence
- Highlight areas where Postman excels and where it needs improvement
- Identify emerging competitors gaining developer mindshare
- Surface specific feature requests or pain points from the community
- Be honest about Postman's weaknesses as well as strengths
