---
name: blog-dashboard
description: "Start or stop the blog pipeline Kanban dashboard (Flask app at dashboard/app.py, served on http://localhost:5001)."
argument-hint: "start|stop"
allowed-tools: ["Bash"]
---

# Blog Dashboard

Start or stop the local Flask dashboard that visualizes the blog pipeline Kanban board. The dashboard itself never runs skills directly — it just watches `blog-output/` and `dashboard/state.json` and spawns agents via `queue.json`. See `dashboard/README.md` for the full architecture.

Resolve `<plugin-root>` the same way other dashboard-touching skills do: the directory containing `dashboard/app.py`, either the current plugin root or `CLAUDE_PLUGIN_ROOT` if set.

The action is the first argument (`start` or `stop`). If missing or not one of those two, ask the user which one they meant — do not guess.

## start

1. Check if it's already running:
   ```bash
   lsof -i :5001 -sTCP:LISTEN -t
   ```
   If this returns a PID, tell the user the dashboard is already running at http://localhost:5001 and stop — do not start a second instance.

2. Ensure the virtualenv exists. If `<plugin-root>/dashboard/.venv` is missing, create it and install deps:
   ```bash
   cd <plugin-root>/dashboard && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```

3. Launch the app in the background, logging output and capturing its PID so `stop` can find it later. Put the `cd` on its own line — chaining it as `cd dir && nohup ... &` backgrounds the whole `cd && nohup` pair in a subshell, so the following `echo $!` line runs in the wrong directory and writes the pidfile to the wrong place:
   ```bash
   cd <plugin-root>/dashboard
   nohup .venv/bin/python app.py > .dashboard.log 2>&1 &
   echo $! > .dashboard.pid
   ```
   Run this with the Bash tool's `run_in_background` unset (it's already detached via `nohup ... &`) — just run it and move on, don't block on it.

4. Give the server a moment to bind, then confirm:
   ```bash
   sleep 1 && lsof -i :5001 -sTCP:LISTEN -t
   ```
   If a PID comes back, tell the user the dashboard is running at **http://localhost:5001**. If not, read the last ~20 lines of `dashboard/.dashboard.log` and show the user what went wrong (commonly: missing venv deps, or missing `WP_APP_PASSWORD`/`GEMINI_API_KEY` env vars — see `dashboard/README.md` prerequisites).

## stop

1. Find the listening process:
   ```bash
   lsof -i :5001 -sTCP:LISTEN -t
   ```
   If nothing is returned, tell the user the dashboard isn't running and stop.

2. Kill it:
   ```bash
   kill $(lsof -i :5001 -sTCP:LISTEN -t)
   ```

3. Clean up the pidfile if present:
   ```bash
   rm -f <plugin-root>/dashboard/.dashboard.pid
   ```

4. Confirm to the user that the dashboard has been stopped.

## Notes

- Always resolve the port (5001) by checking `lsof`, not just the pidfile — the pidfile can go stale if the process was killed out-of-band or the machine restarted.
- Never touch `dashboard/state.json`, `queue.json`, or `blog-output/` from this skill — that's `/blog-dashboard-cleanup`'s job, and normal pipeline operation otherwise.
