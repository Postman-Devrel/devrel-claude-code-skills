# DevRel Claude Code Skills

A collection of Claude Code commands used by the Postman Developer Relations team for content creation, competitive intelligence, and community engagement.

## Getting Started

1. Clone this repo
2. Open Claude Code in the project directory: `claude`
3. Type `/` to see all available commands

Everything in `.claude/` is automatically loaded — no additional setup required.

## Available Commands

| Command | Description |
|---------|-------------|
| `/blog-ideas` | Search trending AI/API topics and generate scored blog content ideas (0-100) |
| `/blog-write` | Write technical blog posts with developer advocate voice, SEO frontmatter, and hands-on examples |
| `/blog-copyeditor` | Copy edit blog posts for grammar, structure, and SEO optimization |
| `/cfp-hunter` | Search for open Call-for-Papers at API and AI developer conferences |
| `/newsletter-agentsandapis` | Generate the monthly Agents & APIs meetup newsletter |
| `/competitor-sentiment` | Analyze Reddit sentiment about API developer tools |
| `/sentiment-competitors` | Analyze Reddit sentiment (alternate name) |

## Output Directories

Each command writes to a dedicated directory:

| Directory | Command | Naming Convention |
|-----------|---------|-------------------|
| `blog-output/` | `/blog-write` | Slugified title (e.g., `testing-auth-flows-in-postman.md`) |
| `cfp-output/` | `/cfp-hunter` | `current-cfps.md` |
| `newsletter-output/` | `/newsletter-agentsandapis` | `YYYY-MM` prefix (e.g., `2026-03-agents-and-apis.md`) |

## Hooks

A `PostToolUse` hook automatically triggers after any markdown file is written via the `Write` tool. If the file looks like a blog post, it suggests running `/blog-copyeditor` to review grammar, structure, and SEO. See [.claude/hooks/blog-copyeditor-hook.sh](.claude/hooks/blog-copyeditor-hook.sh).

## Project Structure

```
.claude/
├── commands/              # Slash commands (loaded automatically)
│   ├── blog-write.md
│   ├── blog-copyeditor.md
│   ├── blog-ideas.md
│   ├── cfp-hunter.md
│   ├── competitor-sentiment.md
│   ├── sentiment-competitors.md
│   └── newsletter-agentsandapis.md
├── hooks/
│   └── blog-copyeditor-hook.sh
└── settings.json          # Hook configuration
blog-output/               # Blog post output
cfp-output/                # CFP search results
newsletter-output/         # Newsletter output
prompts/                   # Standalone prompt templates
```

## Usage Examples

```bash
# Generate blog content ideas
/blog-ideas

# Write a blog post (outputs to blog-output/ with SEO frontmatter)
/blog-write Testing OAuth 2.0 flows in Postman

# Find speaking opportunities
/cfp-hunter

# Generate this month's newsletter
/newsletter-agentsandapis

# Run competitive analysis
/competitor-sentiment
```
