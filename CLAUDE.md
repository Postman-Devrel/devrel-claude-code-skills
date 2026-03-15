# DevRel Claude Code Skills

Developer advocacy toolkit for Postman.com — a collection of Claude Code commands for content creation, competitive intelligence, and community engagement.

## Available Commands

| Command | Description |
|---------|-------------|
| `/blog-ideas` | Search trending AI/API topics and generate scored blog content ideas (0-100) |
| `/blog-write` | Write technical blog posts with developer advocate voice, SEO frontmatter, and hands-on examples |
| `/blog-copyeditor` | Copy edit blog posts for grammar, structure, and SEO. Also runs automatically via hook after `/blog-write` |
| `/cfp-hunter` | Search for open Call-for-Papers at API and AI developer conferences |
| `/newsletter-agentsandapis` | Generate the monthly Agents & APIs meetup newsletter from Luma calendar + AI/API news |
| `/competitor-sentiment` | Analyze Reddit sentiment about API developer tools (Postman, Bruno, Insomnia, etc.) |
| `/sentiment-competitors` | Same as above (alternate name) |

## Output Directories

Each command writes output to a dedicated directory:

- `blog-output/` — Blog posts (slugified title, includes SEO frontmatter)
- `cfp-output/` — CFP search results (`current-cfps.md`)
- `newsletter-output/` — Newsletters (prefixed with `YYYY-MM`)

## Hooks

A `PostToolUse` hook on the `Write` tool automatically suggests running `/blog-copyeditor` when a blog post markdown file is written. See `.claude/hooks/blog-copyeditor-hook.sh`.

## Conventions

- Blog posts use the Postman developer advocate voice: conversational, authoritative, hands-on
- All blog code blocks must have language identifiers for syntax highlighting
- Blog output includes YAML frontmatter with `suggested_title`, `meta_description`, `seo_score`, and keywords
- Newsletter filenames use `YYYY-MM` prefix format
- Luma event links include `?utm_source=newsletter`
- No marketing language: avoid "supercharge", "unlock", "revolutionize", "leverage"
