# DevRel Claude Code Skills

Developer advocacy toolkit for Postman.com — a Claude Code plugin with skills for content creation, competitive intelligence, and community engagement.

## Plugin Structure

This project is a Claude Code plugin. Install it with:

```bash
claude plugin install devrel-skills
```

Or test locally with:

```bash
claude --plugin-dir /path/to/devrel-claude-code-skills
```

## Available Skills

Skills are namespaced under `devrel-skills:` when installed as a plugin.

| Skill | Description |
|-------|-------------|
| `/devrel-skills:blog-ideas` | Search trending AI/API topics and generate scored blog content ideas (0-100) |
| `/devrel-skills:blog-write` | Write technical blog posts with developer advocate voice, SEO frontmatter, and hands-on examples |
| `/devrel-skills:blog-copyeditor` | Copy edit blog posts for grammar, structure, and SEO. Also runs automatically via hook after `blog-write` |
| `/devrel-skills:cfp-hunter` | Search for open Call-for-Papers at API and AI developer conferences |
| `/devrel-skills:newsletter-agentsandapis` | Generate the monthly Agents & APIs meetup newsletter from Luma calendar + AI/API news |
| `/devrel-skills:sentiment-apitools` | Reactive Reddit sentiment analysis of API developer tools — skewed towards PLG offerings (Postman, Bruno, Insomnia, etc.) |

## Output Directories

Each skill writes output to a dedicated directory:

- `blog-output/` — Blog posts (slugified title, includes SEO frontmatter)
- `cfp-output/` — CFP search results (`current-cfps.md`)
- `newsletter-output/` — Newsletters (prefixed with `YYYY-MM`)

## Hooks

A `PostToolUse` hook on the `Write` tool automatically suggests running `/devrel-skills:blog-copyeditor` when a blog post markdown file is written.

## Conventions

- Blog posts use the Postman developer advocate voice: conversational, authoritative, hands-on
- All blog code blocks must have language identifiers for syntax highlighting
- Blog output includes YAML frontmatter with `suggested_title`, `meta_description`, `seo_score`, and keywords
- Newsletter filenames use `YYYY-MM` prefix format
- Luma event links include `?utm_source=newsletter`
- No marketing language: avoid "supercharge", "unlock", "revolutionize", "leverage"
