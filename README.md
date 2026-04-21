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

## Quickstart

The most common starting points — pick the one that fits your situation.

### I have a topic or idea

Use `/blog-pipeline` and the full workflow runs automatically: write, copyedit, generate a header image, and stage to WordPress as a draft.

```bash
/blog-pipeline Testing OAuth 2.0 flows in Postman
```

Not sure what to write about? Generate scored ideas first:

```bash
/blog-ideas MCP servers
```

Then kick off the pipeline with whichever topic looks best.

### I already have a Google Doc

Pass the doc URL directly to `/blog-wordpress-stage`. It converts the doc to markdown, runs the copyeditor automatically, and stages it to WordPress — no extra steps:

```bash
/blog-wordpress-stage https://docs.google.com/document/d/1abc.../edit
```

The Google Doc must be shared as "Anyone with the link can view".

### I want to write the post now and handle the header image later

Use `/blog-write` to produce a finished, copyedited markdown file. Then raise a design ticket for the header image and come back to stage when it's ready.

```bash
# Step 1 — write and copyedit the post
/blog-write Testing OAuth 2.0 flows in Postman
# → saves blog-output/testing-oauth-2-0-flows-in-postman.md

# Step 2 — raise a design ticket for the header image
# (share the .md file with the design team and reference the 2560×1355 PNG spec)

# Step 3 — stage to WordPress once the header image lands
/blog-wordpress-stage blog-output/testing-oauth-2-0-flows-in-postman.md blog-output/images/header/header-testing-oauth-2-0-flows-in-postman.png
```

If the header image isn't ready yet you can stage without it — just omit the image argument and attach it in wp-admin later.

---

That covers the three most common paths. Read on for the full pipeline, the Kanban dashboard, individual skills, and configuration options.

## Available Skills

### Blog Pipeline

The blog pipeline takes a post from idea to scheduled WordPress draft. You can run the full pipeline as a single command, or run individual skills for more control.

| Skill | Description |
|-------|-------------|
| `blog-pipeline` | Full pipeline — auto-detects input (topic, draft file, or Google Doc URL), then runs write/import, copyedit, header image, stage, and optionally schedule |
| `blog-write` | Write a technical blog post from a topic or draft file |
| `blog-create-from-gdoc` | Import a Google Doc as blog-ready markdown with downloaded images |
| `blog-copyeditor` | Copy edit for grammar, structure, and SEO |
| `blog-header-image` | Generate a Postman-branded header image (2560x1355 PNG) |
| `blog-wordpress-stage` | Stage post + header image to blog.postman.com as a draft with SEO metadata and tags |
| `blog-wordpress-scheduler` | Manage the editorial calendar — schedule posts, list upcoming/published, view monthly counts |
| `blog-ideas` | Search trending topics and generate scored blog content ideas |

### Other Skills

| Skill | Description |
|-------|-------------|
| `cfp-hunter` | Search for open Call-for-Papers at API and AI developer conferences |
| `newsletter-agentsandapis` | Generate the monthly Agents & APIs meetup newsletter |
| `sentiment-apitools` | Analyze Reddit sentiment about API developer tools |
| `influencer-autoagent` | Find and rank developer influencers for product launches |

## Blog Pipeline

There are two ways to run the blog pipeline: the **CLI pipeline skill** and the **Kanban dashboard**.

### Option 1: CLI Pipeline Skill

Run `/blog-pipeline` in Claude Code for an interactive, single-command pipeline:

```bash
# Write a new post from a topic
/blog-pipeline Testing OAuth 2.0 flows in Postman

# Import from a Google Doc
/blog-pipeline https://docs.google.com/document/d/1abc.../edit

# Use an existing draft file
/blog-pipeline prompts/my-draft.md

# No argument — it will ask what you want to do
/blog-pipeline
```

The pipeline auto-detects your input type and runs:

1. **Write or import** the blog post
2. **Copyedit** for grammar, style guide compliance, and SEO
3. **Generate a header image** (Postman-branded, 2560x1355)
4. **Stage to WordPress** as a draft with featured image, meta description, and tags
5. **Ask if you want to schedule** — if yes, runs the scheduler (with embargo date support)

### Option 2: Kanban Dashboard

A web-based Kanban board that runs the pipeline visually. Cards move through columns as agents produce output.

#### Starting the Dashboard

```bash
cd dashboard
./start.sh
```

Open **http://127.0.0.1:5001**. To stop: `./stop.sh`

#### Setup

```bash
cd dashboard
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

#### How It Works

The dashboard is a UI layer on top of the same skills. It spawns `claude` CLI agents in the background and tracks progress via file watching.

| Column | What happens |
|--------|-------------|
| **Ideas** | Enter a topic or paste a Google Docs URL. Click "Start Pipeline". |
| **Creating** | Agent is working — writing, copyediting, generating the header image. Status updates as each substep completes. |
| **Staging** | Agent is staging the post to WordPress. |
| **Review** | Draft is in WordPress. Click the link to review. Flip the toggle to "Schedule It" when ready. |
| **Scheduled** | Post is scheduled with a publish date (8:00 AM PST). |

- **Auto-refresh** — the board reloads every 60 seconds to pick up changes
- **File watcher** — polls `blog-output/` every 3 seconds and advances cards as agents produce files
- **WordPress sync** — on startup, fetches drafts and scheduled posts from blog.postman.com
- **Published tab** — shows published posts grouped by month with links
- **Admin tab** — view and manage pipeline cards, clear the board

#### Dashboard Architecture

The dashboard does **not** call the WordPress API for writes — all staging and scheduling goes through the agents (same skills as the CLI). It only reads from WordPress to populate the Scheduled column and Published tab.

```
User creates card → Dashboard spawns claude CLI agent → Agent runs skills →
File watcher detects output → Card advances through columns →
User reviews in WordPress → User flips toggle → Agent schedules post
```

## Output Directories

Each skill writes to a dedicated directory:

| Directory | Skill | Naming Convention |
|-----------|-------|-------------------|
| `blog-output/` | `blog-write`, `blog-create-from-gdoc` | Slugified title (e.g., `testing-auth-flows-in-postman.md`) |
| `blog-output/images/header/` | `blog-header-image` | `header-{slug}.png` (2560x1355) |
| `blog-output/images/{slug}/` | `blog-create-from-gdoc` | Downloaded images from Google Docs |
| `cfp-output/` | `cfp-hunter` | `current-cfps.md` |
| `newsletter-output/` | `newsletter-agentsandapis` | `YYYY-MM` prefix (e.g., `2026-03-agents-and-apis.md`) |
| `sentiment-output/` | `sentiment-apitools` | `sentiment-analysis-YYMMDD.md` |
| `influencer-output/` | `influencer-autoagent` | `influencer-candidates-YYMMDD.md` |

## Hooks

A `PostToolUse` hook automatically triggers after any markdown file is written via the `Write` tool. If the file looks like a blog post, it suggests running `blog-copyeditor` to review grammar, structure, and SEO.

## Plugin Structure

```
.claude-plugin/
  plugin.json                  # Plugin manifest
skills/
  blog-pipeline/               # Full pipeline orchestrator
  blog-write/                  # Blog writing
  blog-copyeditor/             # Copy editing & SEO
  blog-create-from-gdoc/       # Google Doc import
  blog-header-image/           # Header image generation
  blog-wordpress-stage/        # WordPress staging
  blog-wordpress-scheduler/    # Editorial calendar management
  blog-ideas/                  # Blog idea generation
  cfp-hunter/                  # CFP search
  sentiment-apitools/          # Sentiment analysis
  newsletter-agentsandapis/    # Newsletter generation
  influencer-autoagent/        # Influencer finder
hooks/
  hooks.json                   # Hook configuration
  blog-copyeditor-hook.sh      # Post-write hook script
dashboard/                     # Kanban web dashboard
  app.py                       # Flask application
  watcher.py                   # File system watcher
  calendar_sync.py             # WordPress calendar sync (read-only)
  start.sh / stop.sh           # Start and stop scripts
  templates/                   # Jinja2 templates
  static/                      # CSS
blog-output/                   # Blog post output
cfp-output/                    # CFP search results
newsletter-output/             # Newsletter output
sentiment-output/              # Sentiment analysis output
influencer-output/             # Influencer candidate output
```

## Usage Examples

```bash
# Full blog pipeline (auto-detects input type)
/blog-pipeline Testing OAuth 2.0 flows in Postman
/blog-pipeline https://docs.google.com/document/d/1abc.../edit
/blog-pipeline prompts/my-draft.md

# Individual blog skills
/blog-write Testing OAuth 2.0 flows in Postman
/blog-create-from-gdoc https://docs.google.com/document/d/1abc.../edit
/blog-copyeditor blog-output/testing-auth-flows-in-postman.md
/blog-header-image blog-output/testing-auth-flows-in-postman.md
/blog-wordpress-stage blog-output/testing-auth-flows-in-postman.md
/blog-wordpress-scheduler list
/blog-wordpress-scheduler reschedule 12345 next

# Generate blog content ideas
/blog-ideas MCP

# Find speaking opportunities
/cfp-hunter

# Generate this month's newsletter
/newsletter-agentsandapis March

# Run API tool sentiment analysis
/sentiment-apitools

# Find influencers for a product launch
/influencer-autoagent Autonomous Agent
```

## Prerequisites

### WordPress Setup (for staging and scheduling)

The `blog-wordpress-stage` and `blog-wordpress-scheduler` skills require WordPress application credentials:

1. Go to **blog.postman.com/wp-admin/profile.php**
2. Scroll to **Application Passwords** and create a new one
3. Add the credentials to `~/.claude/settings.json`:

```json
{
  "env": {
    "WP_USERNAME": "your-wordpress-username",
    "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
  }
}
```

The dashboard also reads these credentials (for populating the Scheduled column and Published tab on startup).

### Google Docs Setup (for `blog-create-from-gdoc`)

The Google Doc must be shared with "Anyone with the link can view" access. No API keys required — the skill uses the public export URL.

### Gemini API Setup (for `blog-header-image`)

Header image generation requires a Gemini API key:

```json
{
  "env": {
    "GEMINI_API_KEY": "your-gemini-api-key"
  }
}
```

### Reddit API Setup (for `sentiment-apitools`)

The `sentiment-apitools` skill can use web search with no setup, but for deeper analysis with full comment threads, configure Reddit API credentials:

1. Go to https://www.reddit.com/prefs/apps and click "create another app..."
2. Select **script** as the app type
3. Set redirect URI to `http://localhost:8080`
4. Note your `client_id` (string under the app name) and `client_secret`

```json
{
  "env": {
    "REDDIT_CLIENT_ID": "your_client_id",
    "REDDIT_CLIENT_SECRET": "your_client_secret",
    "REDDIT_USER_AGENT": "competitor-sentiment-analyzer/1.0"
  }
}
```

## License

MIT
