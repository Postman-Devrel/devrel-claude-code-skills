#!/usr/bin/env python3
"""Background queue processor — pops items from queue.json and runs them.

Started automatically by start.sh alongside the Flask dashboard.
Handles three action types:
  sync-calendar  — direct WP API call via calendar_sync.py (no Claude needed)
  blog-pipeline  — runs /devrel-skills:blog-pipeline via claude --print
  schedule       — runs /devrel-skills:blog-wordpress-scheduler via claude --print
"""

import fcntl
import json
import os
import subprocess
import sys
import time

QUEUE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue.json")
PLUGIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POLL_INTERVAL = 5  # seconds between queue checks


def _read_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    try:
        with open(QUEUE_FILE, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except Exception:
        return []


def _write_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(queue, f, indent=2)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _pop_item():
    """Atomically pop and return the first item from the queue, or None."""
    queue = _read_queue()
    if not queue:
        return None
    item, rest = queue[0], queue[1:]
    _write_queue(rest)
    return item


def _run_claude(prompt):
    """Run claude --print with the devrel plugin loaded."""
    result = subprocess.run(
        [
            "claude", "--print",
            "--dangerously-skip-permissions",
            "--plugin-dir", PLUGIN_DIR,
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=900,  # 15 min ceiling
        cwd=PLUGIN_DIR,
    )
    if result.returncode != 0:
        print(f"[queue-processor] claude exited {result.returncode}: {result.stderr[:500]}", flush=True)
        return False
    return True


def _sync_calendar():
    """Sync WP calendar via Claude — direct HTTP is blocked by Cloudflare."""
    _run_claude("/devrel-skills:blog-wordpress-scheduler")


def main():
    print("[queue-processor] Started, polling queue.json every 5s...", flush=True)
    while True:
        try:
            item = _pop_item()
            if item:
                action = item.get("action", "")
                card_id = item.get("card_id", "")
                topic = item.get("topic", "")
                print(f"[queue-processor] {action} card={card_id}", flush=True)

                if action == "sync-calendar":
                    _sync_calendar()

                elif action == "blog-pipeline":
                    _run_claude(f"/devrel-skills:blog-pipeline {topic}")

                elif action == "schedule":
                    _run_claude(
                        f"/devrel-skills:blog-wordpress-scheduler schedule post {topic}"
                    )

                else:
                    print(f"[queue-processor] Unknown action: {action}", flush=True)

        except subprocess.TimeoutExpired:
            print("[queue-processor] Job timed out (15 min).", flush=True)
        except Exception as e:
            print(f"[queue-processor] Error: {e}", flush=True)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
