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
| `/devrel-skills:blog-header-image` | Generate Postman-branded blog header images (2560×1355 PNG, no text) using Gemini/nanobanana |
| `/devrel-skills:blog-pipeline` | Full blog pipeline — write/import, copyedit, header image, stage, and optionally schedule |
| `/devrel-skills:blog-create-from-gdoc` | Convert a Google Doc to blog-ready markdown with downloaded images |
| `/devrel-skills:blog-wordpress-stage` | Stage a blog post to blog.postman.com WordPress as a draft — accepts a local markdown file or a Google Docs URL (converts the doc first), with SEO metadata |
| `/devrel-skills:blog-wordpress-scheduler` | Manage the editorial calendar — list scheduled/published posts, reschedule dates, monthly post counts, YTD summary with drafts. Enforces Mon-Thu only, no holidays, no same-day conflicts |
| `/devrel-skills:blog-dashboard-cleanup` | Remove stuck/stale Kanban cards that haven't reached staging yet. Pass `--all` to clear the entire board. Never touches WordPress or blog-output files. |
| `/devrel-skills:cfp-hunter` | Search for open Call-for-Papers at API and AI developer conferences |
| `/devrel-skills:newsletter-agentsandapis` | Generate the monthly Agents & APIs meetup newsletter from Luma calendar + AI/API news |
| `/devrel-skills:sentiment-apitools` | Reactive Reddit sentiment analysis of API developer tools — skewed towards PLG offerings (Postman, Bruno, Insomnia, etc.) |
| `/devrel-skills:influencer-autoagent` | Find and rank developer influencers for product launches — scores candidates on technical credibility, audience reach, and topic alignment |
| `/devrel-skills:luma-stats` | Pull event stats from the Postman Dev Events Luma calendar — registrations, waitlist, attendee count, and engagement score per event. Filter by MMM-YY, YYYY, or all time. Shows aggregate sum totals. |
| `/devrel-skills:blog-prod-updates` | Scan #product-updates Slack channel (past 7 days), summarize shipped features for blog-write input. Maintains memory of covered posts, auto-excludes internal-only content |
| `/devrel-skills:social-media-manager` | Weekly social media agent team — researches blog, release notes, and trending news; creates 5 LinkedIn/Twitter posts; packages employee advocacy kit; auto-posts to Twitter Mon/Wed at 10am PST |

## Output Directories

Each skill writes output to a dedicated directory:

- `blog-output/` — Blog posts (slugified title, includes SEO frontmatter)
- `blog-output/images/header/` — Blog header images (`header-*.png`, 2560×1355 PNG)
- `cfp-output/` — CFP search results (`current-cfps.md`)
- `newsletter-output/` — Newsletters (prefixed with `YYYY-MM`)
- `sentiment-output/` — Sentiment analysis reports (`sentiment-analysis-YYMMDD.md`)
- `influencer-output/` — Influencer candidate reports (`influencer-candidates-YYMMDD.md`)
- `luma-output/` — Luma event stats reports (`luma-stats-{filter}.md`)
- `social-media-output/` — Social media posts, research briefs, advocacy kits, and Twitter posting logs

## Hooks

A `PostToolUse` hook on the `Write` tool automatically suggests running `/devrel-skills:blog-copyeditor` when a blog post markdown file is written.

## Conventions

- Blog posts use the Postman developer advocate voice: conversational, authoritative, hands-on
- All blog code blocks must have language identifiers for syntax highlighting
- Blog output includes YAML frontmatter with `suggested_title`, `meta_description`, `seo_score`, and keywords
- Newsletter filenames use `YYYY-MM` prefix format
- Luma event links include `?utm_source=newsletter`
- No marketing language: avoid "supercharge", "unlock", "revolutionize", "leverage"
