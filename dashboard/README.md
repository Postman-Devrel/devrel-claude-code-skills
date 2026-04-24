# Blog Pipeline Dashboard

A Kanban board for the Postman DevRel blog publishing pipeline. Track posts from idea to publication — the agents do all the work, this is just the UI.

https://github.com/Postman-Devrel/devrel-claude-code-skills/raw/main/dashboard/blog-pipeline-ux.mp4

## Prerequisites

The dashboard spawns Claude Code agents that run the blog pipeline skills. You need credentials for three external services before starting.

### WordPress

Required for staging and scheduling posts.

1. Go to **blog.postman.com/wp-admin/profile.php**
2. Scroll to **Application Passwords** and generate a new one
3. Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "WP_USERNAME": "your-wordpress-username",
    "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
  }
}
```

> **Note:** `/blog-wordpress-scheduler` is primarily reserved for admins. Authors can run `/blog-wordpress-scheduler list` to see scheduled posts, but only admins can schedule a post to publish.

### Gemini API

Required for header image generation (`blog-header-image`). The pipeline will stall at the image step without this.

1. Get a key at [aistudio.google.com](https://aistudio.google.com) → API Keys
2. Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "GEMINI_API_KEY": "your-gemini-api-key"
  }
}
```

Your full `~/.claude/settings.json` env block should look like:

```json
{
  "env": {
    "WP_USERNAME": "your-wordpress-username",
    "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx",
    "GEMINI_API_KEY": "your-gemini-api-key"
  }
}
```

## Setup

```bash
cd dashboard
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Running

```bash
.venv/bin/python app.py
```

Open **http://localhost:5001**

## How It Works

The dashboard is a thin UI layer on top of the existing agent pipeline. It does NOT call the WordPress API or run skills directly — the agents handle all of that.

### Board Columns

| Column | What happens |
|--------|-------------|
| **Ideas** | Enter a topic. Click "Start Pipeline" to queue it. |
| **Writing** | Agent is writing. Auto-advances when `.md` appears in `blog-output/`. |
| **Copyedit** | Agent is copyediting. Auto-advances when `-copyedit.md` appears. |
| **Header Image** | Agent is generating the image. Auto-advances when `header-*.png` appears. |
| **Staging** | Agent is staging to WordPress. Auto-advances when `wordpress_id` appears in frontmatter. |
| **Review** | Draft is in WordPress. Click the link to review. Click "Schedule It" when ready. |
| **Scheduled** | Agent found a date and scheduled the post. |
| **Published** | Post is live. Grouped by month. |

### Data Flow

1. **You** enter a topic → card created in Ideas
2. **You** click "Start Pipeline" → request written to `queue.json`
3. **Agents** run the blog-pipeline skills (write, copyedit, header image, stage)
4. **File watcher** polls `blog-output/` every 3 seconds and advances cards as agents produce files
5. **You** review the WordPress draft via the edit link
6. **You** click "Schedule It" → schedule request written to `queue.json`
7. **Scheduler agent** finds the next open date and schedules the post
8. Card moves to Scheduled, then Published when it goes live

### What the Dashboard Does NOT Do

- Does not call the WordPress API directly
- Does not run Claude Code skills or agents
- Does not modify blog-output/ files

All WordPress interaction and content creation is handled by the existing agents. The dashboard reads `state.json` and watches `blog-output/` for file changes.

### Real-Time Updates

- **SSE** pushes updates when the file watcher detects changes
- **Focus refresh** reloads the board when you switch back to the browser tab

## Cleaning Up Stuck Cards

If cards get stuck in the writing, copyedit, or header image stages (usually from a failed or cancelled agent run), use the cleanup skill from Claude Code:

```bash
# Remove only cards stuck before staging (safe default)
/blog-dashboard-cleanup

# Clear everything off the board
/blog-dashboard-cleanup --all
```

The skill shows you exactly what it will remove and asks for confirmation. It only edits `dashboard/state.json` — WordPress drafts and `blog-output/` files are never touched.

You can also manage cards manually via the **Admin** tab at **http://localhost:5001/admin** — remove individual cards or clear the board from there.

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask application — routes, state management, SSE, queue |
| `watcher.py` | File watcher — monitors `blog-output/` and advances cards |
| `state.json` | Pipeline state (gitignored, auto-created) |
| `queue.json` | Agent requests (gitignored, auto-created) |
| `requirements.txt` | Python dependencies: flask, watchdog, pyyaml |
