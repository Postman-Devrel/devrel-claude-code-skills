# DevRel Claude Code Skills

A Claude Code plugin used by the Postman Developer Relations team for content creation, competitive intelligence, and community engagement.

## Installation

### As a Local Project (recommended approach)

Clone the repo and open Claude Code in the project directory:

```bash
git clone https://github.com/Postman-Devrel/devrel-claude-code-skills.git
cd devrel-claude-code-skills
claude --plugin-dir /path/to/devrel-claude-code-skills
```

When running locally, skills are available without the namespace prefix.


Once installed, skills are available in any project with the `devrel-skills:` namespace prefix.


### As a Plugin (not yet available)

Install directly from the repository:

```bash
claude plugin install devrel-skills
```



## Available Skills

| Skill | Description |
|-------|-------------|
| `blog-ideas` | Search trending AI/API topics and generate scored blog content ideas (0-100) |
| `blog-write` | Write technical blog posts with developer advocate voice, SEO frontmatter, and hands-on examples |
| `blog-copyeditor` | Copy edit blog posts for grammar, structure, and SEO optimization |
| `cfp-hunter` | Search for open Call-for-Papers at API and AI developer conferences |
| `newsletter-agentsandapis` | Generate the monthly Agents & APIs meetup newsletter |
| `sentiment-apitools` | Analyze Reddit sentiment about API developer tools |

## Output Directories

Each skill writes to a dedicated directory:

| Directory | Skill | Naming Convention |
|-----------|-------|-------------------|
| `blog-output/` | `blog-write` | Slugified title (e.g., `testing-auth-flows-in-postman.md`) |
| `cfp-output/` | `cfp-hunter` | `current-cfps.md` |
| `newsletter-output/` | `newsletter-agentsandapis` | `YYYY-MM` prefix (e.g., `2026-03-agents-and-apis.md`) |

## Hooks

A `PostToolUse` hook automatically triggers after any markdown file is written via the `Write` tool. If the file looks like a blog post, it suggests running `blog-copyeditor` to review grammar, structure, and SEO.

## Plugin Structure

```
.claude-plugin/
  plugin.json               # Plugin manifest
skills/
  blog-write/
    SKILL.md                # Blog writing skill
  blog-copyeditor/
    SKILL.md                # Copy editing & SEO skill
  blog-ideas/
    SKILL.md                # Blog idea generation skill
  cfp-hunter/
    SKILL.md                # CFP search skill
  sentiment-apitools/
    SKILL.md                # Competitive sentiment analysis skill
  newsletter-agentsandapis/
    SKILL.md                # Newsletter generation skill
hooks/
  hooks.json                # Hook configuration
  blog-copyeditor-hook.sh   # Post-write hook script
blog-output/                # Blog post output
cfp-output/                 # CFP search results
newsletter-output/          # Newsletter output
```

## Usage Examples

```bash
# Generate blog content ideas (optionally pass a focus area)
/devrel-skills:blog-ideas MCP

# Write a blog post — pass a topic, a file path to a draft, or nothing
/devrel-skills:blog-write Testing OAuth 2.0 flows in Postman
/devrel-skills:blog-write prompts/my-draft.md

# Copy edit a blog post (auto-detects most recent, or pass a filename)
/devrel-skills:blog-copyeditor blog-output/testing-auth-flows-in-postman.md

# Find speaking opportunities
/devrel-skills:cfp-hunter

# Generate this month's newsletter (optionally pass a month)
/devrel-skills:newsletter-agentsandapis March

# Run api tool sentiment analysis
/devrel-skills:sentiment-apitools
```

## Prerequisites

Some skills require web access to function:

- **blog-ideas**, **cfp-hunter**, **newsletter-agentsandapis**, **sentiment-apitools** — use `WebSearch` and `WebFetch` tools

### Reddit API Setup (for `sentiment-apitools`)

The `sentiment-apitools` skill can use web search with no setup, but for deeper analysis with full comment threads, configure Reddit API credentials:

1. Go to https://www.reddit.com/prefs/apps and click "create another app..."
2. Select **script** as the app type
3. Set redirect URI to `http://localhost:8080`
4. Note your `client_id` (string under the app name) and `client_secret`

Set environment variables:

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

When you run the skill, it will ask whether to use web search (no setup) or the Reddit API (more comprehensive).

## License
 
MIT
