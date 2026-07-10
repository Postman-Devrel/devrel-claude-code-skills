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



Not sure what to write about? Generate scored ideas first:

```bash
/blog-ideas MCP servers
```

Then kick off the pipeline with whichever topic looks best.

### Start from a blog draft in google docs

Pass the doc URL directly to `/blog-wordpress-stage`. It converts the doc to markdown, runs the copyeditor automatically, and stages it to WordPress — no extra steps:

```bash
/blog-wordpress-stage https://docs.google.com/document/d/1abc.../edit
```

The Google Doc must be shared as "Anyone with the link can view".

### Start from a prompt or rough outline

Use `/blog-write` to produce a finished, copyedited markdown file. Then raise a design ticket for the header image and come back to stage when it's ready.

The recommended approach is create a draft or outline in markdown or google docs, then pass that path to /blog-write to complete it, including automatically running a copy edit, utilizing postman writing style guides, for you. 

```bash
# Step 1 — write and copyedit the post
/blog-write Testing OAuth 2.0 flows in Postman
# → saves blog-output/testing-oauth-2-0-flows-in-postman.md

#Step 1 - start from a markdown outline or draft
/blog-write prompts/my-blog-outline.md

#Step 1 - start from a google doc link
/blog-write https://docs.google.com/document/d/1noytoyCGZY7uKuwK1l3R5hukI_qqd-ZjvJfFDJdCeFg/edit

# Step 2 — raise a design ticket for the header image
# (share the .md file with the design team and reference the 2560×1355 PNG spec)

# Step 3 — stage to WordPress once the header image lands
/blog-wordpress-stage blog-output/testing-oauth-2-0-flows-in-postman.md blog-output/images/header/header-testing-oauth-2-0-flows-in-postman.png
```

If the header image isn't ready yet you can stage without it — just omit the image argument and attach it in wp-admin later.

```bash
#Step 4 - schedule it
/blog-wordpress-scheduler
```

In order to use the /blog-wordpress* commands, you will need your wordpress username and an Application Key. You can generate this via Users > Profile > scroll to the bottom where you will see *Application Passwords*. Generate a new one and copy it to the clipboard. The first time you run /blog-wordpress-stage, it will prompt you to set up your credentials.

**Note:**
/blog-wordpress-scheduler is primarily reserved for admins. As an author you can use /blog-wordpress-scheduler list to see all scheduled posts, but only admins can schedule a post to published. 

### Full autononmous pipeline (experimental)

Use `/blog-pipeline` and the full workflow runs automatically: write, copyedit, generate a header image, and stage to WordPress as a draft. (There is also a experimental UI version of this. see [this video](https://github.com/Postman-Devrel/devrel-claude-code-skills/raw/main/dashboard/blog-pipeline-ux.mp4) or check out more information below)

```bash
/blog-pipeline Testing OAuth 2.0 flows in Postman
```


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
| `blog-wordpress-scheduler` | Manage the editorial calendar — schedule posts (Tue/Thu priority), list upcoming/published, view monthly counts |
| `blog-dashboard-cleanup` | Remove stuck/stale Kanban cards before staging. Pass `--all` to clear the entire board. Safe to run anytime — never touches WordPress. |
| `blog-ideas` | Search trending topics and generate scored blog content ideas |
| `blog-prod-updates` | Scan #product-updates Slack channel (past 7 days), summarize shipped features for `blog-write`. Only includes Product Stage >= 7. Maintains memory of covered posts. |

### Other Skills

| Skill | Description |
|-------|-------------|
| `cfp-hunter` | Search for open Call-for-Papers at API and AI developer conferences. Writes `cfp-output/current-cfps.md`, which `cfp-tracker` can import |
| `cfp-tracker` | Manage the team's CFP submissions on the Confluence "Team CFP Tracker" page (add/update/delete/archive, status tracking incl. **Planned**). Imports CFPs discovered by `cfp-hunter`. Confluence is the single source of truth |
| `newsletter-agentsandapis` | Generate the monthly Agents & APIs meetup newsletter |
| `influencer-autoagent` | Find and rank developer influencers for product launches |
| `meetup-calendar` | Read, sync, and update the internal Postman meetup calendar spreadsheet — see commands below |

> `sentiment-apitools` moved to its own plugin repo: [Postman-Devrel/competitor-sentiment-analysis](https://github.com/Postman-Devrel/competitor-sentiment-analysis).

## Meetup Calendar

The `meetup-calendar` skill reads, syncs, and updates the internal Postman meetup and user group calendar spreadsheet.

| Command | What it does |
|---------|-------------|
| `/meetup-calendar` | Summarize all events grouped by upcoming/past and region |
| `/meetup-calendar upcoming` | Upcoming events only |
| `/meetup-calendar past` | Past events only |
| `/meetup-calendar 2026` | Events from a specific year |
| `/meetup-calendar London` | Events from a specific city or region |
| `/meetup-calendar --sync` | Match Luma events to spreadsheet rows and write Luma URLs. Prompts before creating any missing events — pick one, many, or all. |
| `/meetup-calendar --sync https://luma.com/calendar/manage/cal-.../events` | Same, using a specific Luma calendar |
| `/meetup-calendar --sync --dry-run` | Preview matches without writing anything |
| `/meetup-calendar --update-stats` | Fetch Luma registration, waitlist, and attendance counts and write them back to the sheet. Prompts before fetching. |

### `--sync` event creation

When `--sync` finds spreadsheet rows with no matching Luma event, it lists them and asks which to create. You can pick one, many, or all. For each created event:

- Clones the template event for description, timezone, and structure
- Generates the slug as `YY-MM-agents-and-apis-{city}` (e.g. `26-09-agents-and-apis-berlin`)
- Sets visibility to **private**
- **Cover image**: reuses the cover from a past Luma event in the same city if one exists; otherwise generates a new Postman-branded image via Gemini and uploads it directly to the Luma event
- Writes the new Luma URL back to the spreadsheet

### Required env vars

| Variable | Used by | Set in |
|----------|---------|--------|
| `MEETUP_SHEET_ID` | all | `~/.claude/settings.json` |
| `GOOGLE_APPLICATION_CREDENTIALS` | all | `~/.claude/settings.local.json` |
| `LUMA_API_KEY` | `--sync`, `--update-stats` | `~/.claude/settings.json` |
| `LUMA_CALENDAR_ID` | `--sync` | `~/.claude/settings.json` |
| `GEMINI_API_KEY` | `--sync` (image generation) | `~/.claude/settings.json` |

---

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

A web-based Kanban board that runs the pipeline visually. Cards move through columns as agents produce output. See the [dashboard README](dashboard/README.md) for full setup instructions including Gemini and WordPress credentials.

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
| `influencer-output/` | `influencer-autoagent` | `influencer-candidates-YYMMDD.md` |
| `blog-output/` | `blog-prod-updates` | `prod-updates-YYMMDD.md` + `.prod-update-memory.json` |

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
  cfp-tracker/                 # CFP submission tracking (Confluence)
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

# Summarize recent product updates for blog content
/blog-prod-updates
/blog-prod-updates 14

# Find speaking opportunities, then track the ones worth pursuing
/cfp-hunter
/cfp-tracker add the top 3 from the hunter results   # imports them as "Planned"

# Generate this month's newsletter
/newsletter-agentsandapis March

# Find influencers for a product launch
/influencer-autoagent Autonomous Agent

# Summarize events
/meetup-calendar                          # all events, grouped by upcoming/past and region
/meetup-calendar upcoming                 # upcoming events only
/meetup-calendar past                     # past events only
/meetup-calendar 2026                     # events from a specific year
/meetup-calendar London                   # events from a specific city or region

# Match Luma events to spreadsheet rows and write Luma URLs
/meetup-calendar --sync                   # match and write; prompts before creating missing events
/meetup-calendar --sync https://luma.com/calendar/manage/cal-TGqTNpY4iyl7XYe/events  # use a specific calendar
/meetup-calendar --sync --dry-run         # preview matches without writing anything

# Fetch Luma registration, waitlist, and attendance and write to sheet
/meetup-calendar --update-stats
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

### Editorial Calendar Rules (`blog-wordpress-scheduler`)

The scheduler enforces these rules in priority order:

- **Tuesday and Thursday are the primary publish days.** The scheduler always fills Tue/Thu slots before offering any others.
- **Monday and Wednesday are overflow days only.** They become available only when all Tuesday and Thursday slots in the next 2 weeks are already booked.
- **No Friday, Saturday, or Sunday scheduling** — ever.
- **No US public holidays** — the scheduler checks fixed and floating holidays for the target year.
- **No same-day conflicts** — only one post per day is allowed.
- **All posts publish at 8:00 AM PST.**

When using `reschedule <id> next`, the scheduler follows this logic:

1. Scan all Tue/Thu dates in the next 2 weeks — return the earliest open one.
2. If all Tue/Thu in the next 2 weeks are booked → offer Mon/Wed within the same 2-week window.
3. If the entire 2-week window is full → search beyond 2 weeks using Tue/Thu priority.

If you manually pick a Monday or Wednesday date when open Tue/Thu slots still exist in the next 2 weeks, the scheduler will reject the date and show you the available Tue/Thu options.

### Slack Setup (for `blog-prod-updates`)

The `blog-prod-updates` skill reads from the Postman #product-updates Slack channel. You'll need a Slack Bot Token:

1. Go to **api.slack.com/apps** and click **Create New App** > **From scratch**
2. Name it (e.g. "DevRel Blog Bot") and select the Postman workspace
3. Go to **OAuth & Permissions** in the sidebar
4. Under **Bot Token Scopes**, add `channels:history` and `channels:read`
5. Click **Install to Workspace** at the top and approve the permissions
6. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
7. In Slack, go to the #product-updates channel and type `/invite @DevRel Blog Bot` to give the bot access

Add the token to your settings:

```json
{
  "env": {
    "SLACK_BOT_TOKEN": "xoxb-your-token-here"
  }
}
```

For local use, add it to `.claude/settings.local.json` (git-ignored). For Vercel deployment, set it as an environment variable in the Vercel project dashboard (Settings > Environment Variables).

No redirect URL is needed — the bot token is issued directly on workspace install.

### Google Sheets Setup (for `meetup-calendar`)

The `meetup-calendar` skill reads a private internal Google Sheet using the Sheets API v4, authenticated via a Google Cloud service account. This is a one-time setup per machine.

#### Step 1 — Create a Google Cloud project and enable the Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com) and select or create a project
2. Navigate to **APIs & Services → Enable APIs & Services**
3. Search for **Google Sheets API** and click **Enable**

#### Step 2 — Create a service account

1. Go to **IAM & Admin → Service Accounts**
2. Click **Create Service Account**
3. Give it a name (e.g. `devrel-skills`) and click **Done** — no IAM roles are needed
4. Click on the service account you just created
5. Go to the **Keys** tab → **Add Key → Create new key → JSON**
6. A `.json` file downloads to your machine — save it somewhere safe (e.g. `~/.config/gcloud/devrel-sheets-sa.json`)

> **Important:** Never commit this file to git. It is a private key. The repo's `.gitignore` already excludes `skills/meetup-calendar/*.json` if you store it there.

#### Step 3 — Share the spreadsheet with the service account

1. Open the [Postman meetup calendar spreadsheet](https://docs.google.com/spreadsheets/d/1vu5Nr_xP0-fBj9zJITb5xhC5iTKpPMkI3H9uMFaHNEI)
2. Click **Share** (top right)
3. Paste the service account email — it looks like `devrel-skills@your-project-id.iam.gserviceaccount.com` and can be found in the Google Cloud Console under Service Accounts
4. Set the role to **Editor** (required for future write-back features)
5. Click **Send**

#### Step 4 — Add credentials to Claude settings

Add to `~/.claude/settings.json` (global, so the skill works from any directory):

```json
{
  "env": {
    "MEETUP_SHEET_ID": "1vu5Nr_xP0-fBj9zJITb5xhC5iTKpPMkI3H9uMFaHNEI",
    "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/your-service-account-key.json"
  }
}
```

Replace the path with wherever you saved the JSON key file in Step 2.

#### Verifying the setup

Run the skill with no arguments — it will validate both env vars and attempt to fetch the sheet before producing output:

```bash
/devrel-skills:meetup-calendar
```

If you see a 403 error from the Sheets API, the service account hasn't been granted access to the sheet — repeat Step 3. If the credentials file isn't found, check the path in `GOOGLE_APPLICATION_CREDENTIALS`.

---

### Atlassian / Confluence Setup (for `cfp-tracker`)

The `cfp-tracker` skill reads and writes the "Team CFP Tracker" Confluence page
(`postmanlabs.atlassian.net`, page ID `8268251220`) directly through the official
**Atlassian MCP server**. Without this connector, the skill cannot fetch or update
the page. This is a one-time setup per machine.

#### Step 1 — Add the Atlassian MCP server

The Atlassian remote MCP server uses OAuth (no API token to manage). Add it to
Claude Code:

```bash
claude mcp add --transport http atlassian https://mcp.atlassian.com/v1/mcp
```

#### Step 2 — Authenticate

Start Claude Code and run `/mcp`. Select **atlassian** and complete the OAuth flow
in your browser, signing in to the `postmanlabs.atlassian.net` site. You only need
to authorize once; tokens refresh automatically.

#### Step 3 — Verify

Run the skill with no arguments — it will fetch the tracker page before doing
anything else:

```bash
/devrel-skills:cfp-tracker
```

If you see an error that the `getConfluencePage` / `updateConfluencePage` tools
aren't available, the connector isn't loaded — re-check `/mcp` and confirm the
Atlassian server shows as **connected**. If a fetch fails with a permissions error,
make sure your Atlassian account has access to the DE (Developer Evangelism) space.

---

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

## License

MIT
