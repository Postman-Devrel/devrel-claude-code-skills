# Blog Pipeline Dashboard

A Kanban board for the Postman DevRel blog publishing pipeline. Track posts from idea to publication — the agents do all the work, this is just the UI.

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

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask application — routes, state management, SSE, queue |
| `watcher.py` | File watcher — monitors `blog-output/` and advances cards |
| `state.json` | Pipeline state (gitignored, auto-created) |
| `queue.json` | Agent requests (gitignored, auto-created) |
| `requirements.txt` | Python dependencies: flask, watchdog, pyyaml |
