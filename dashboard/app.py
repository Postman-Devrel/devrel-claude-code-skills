"""Blog Pipeline Kanban Dashboard — Flask application."""

import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from flask import Flask, redirect, render_template, request, send_from_directory, url_for

from watcher import check_and_advance, start_watcher

app = Flask(__name__)

STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")
QUEUE_FILE = os.path.join(os.path.dirname(__file__), "queue.json")
CALENDAR_FILE = os.path.join(os.path.dirname(__file__), "wp-calendar.json")
PST = timezone(timedelta(hours=-8))
CALENDAR_MAX_AGE = 300        # seconds before triggering a background refresh attempt
CALENDAR_ERROR_AGE = 86400    # seconds before showing the error banner (24h — data is still usable until then)


STAGES = [
    "ideas", "creating", "staging", "review", "scheduled",
]

# Internal stages that map to the "creating" column
CREATING_SUBSTAGES = {"writing", "copyedit", "header_image"}

STAGE_LABELS = {
    "ideas": "Ideas",
    "creating": "Creating",
    "staging": "Staging",
    "review": "Review",
    "scheduled": "Scheduled",
}

CREATING_SUBSTAGE_LABELS = {
    "writing": "Writing...",
    "copyedit": "Copyediting...",
    "header_image": "Generating image...",
}


# --- State Management ---

class StateManager:
    def __init__(self, path):
        self.path = path

    def _read(self):
        if not os.path.exists(self.path):
            return {"cards": []}
        with open(self.path, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def _write(self, data):
        with open(self.path, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def get_cards(self):
        return self._read().get("cards", [])

    def get_card(self, card_id):
        for card in self.get_cards():
            if card["id"] == card_id:
                return card
        return None

    def create_card(self, topic):
        data = self._read()
        slug = _slugify(topic)
        now = datetime.now(PST).isoformat()
        card = {
            "id": uuid.uuid4().hex[:8],
            "topic": topic,
            "slug": slug,
            "stage": "ideas",
            "wordpress_id": None,
            "scheduled_date": None,
            "edit_link": None,
            "post_link": None,
            "header_image": None,
            "created_at": now,
            "stage_history": {"ideas": now},
            "error": None,
        }
        data["cards"].append(card)
        self._write(data)
        return card

    def advance_card(self, card_id, new_stage, **kwargs):
        data = self._read()
        now = datetime.now(PST).isoformat()
        for card in data["cards"]:
            if card["id"] == card_id:
                card["stage"] = new_stage
                card["stage_history"][new_stage] = now
                for key, val in kwargs.items():
                    if key in card:
                        card[key] = val
                break
        self._write(data)

    def delete_card(self, card_id):
        data = self._read()
        data["cards"] = [c for c in data["cards"] if c["id"] != card_id]
        self._write(data)

    def set_error(self, card_id, error):
        data = self._read()
        for card in data["cards"]:
            if card["id"] == card_id:
                card["error"] = error
                break
        self._write(data)


state = StateManager(STATE_FILE)

PLUGIN_ROOT = os.path.join(os.path.dirname(__file__), "..")


# --- Agent Runner ---

def _find_claude():
    """Find the claude CLI binary."""
    return shutil.which("claude")


def run_agent(card_id, topic, action="blog-pipeline"):
    """Run a Claude Code agent in a background thread for a pipeline action.
    Claude routes HTTP calls through WebFetch (Anthropic infra), bypassing Cloudflare."""
    claude = _find_claude()
    if not claude:
        state.set_error(card_id, "claude CLI not found in PATH")
        return

    plugin_root_abs = os.path.abspath(PLUGIN_ROOT)

    if action == "blog-pipeline":
        is_gdoc = "docs.google.com/document" in topic
        if is_gdoc:
            prompt = (
                f"Run the full blog pipeline for this Google Doc: {topic}\n\n"
                f"1. Run /blog-create-from-gdoc \"{topic}\"\n"
                f"2. Run /blog-copyeditor on the output file\n"
                f"3. Run /blog-header-image on the output file\n"
                f"4. Run /blog-wordpress-stage on the output file\n\n"
                f"Run each step in order. Wait for each to complete before starting the next."
            )
        else:
            prompt = (
                f"Run the full blog pipeline for this topic: \"{topic}\"\n\n"
                f"1. Run /blog-write \"{topic}\"\n"
                f"2. Run /blog-copyeditor on the output file\n"
                f"3. Run /blog-header-image on the output file\n"
                f"4. Run /blog-wordpress-stage on the output file\n\n"
                f"Run each step in order. Wait for each to complete before starting the next."
            )
    elif action == "schedule":
        prompt = f"Run /blog-wordpress-scheduler reschedule \"{topic}\" next"
    else:
        return

    def _run():
        try:
            result = subprocess.run(
                [claude, "--plugin-dir", plugin_root_abs, "-p", "--dangerously-skip-permissions", prompt],
                cwd=plugin_root_abs,
                timeout=1800,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                error_msg = (result.stderr or result.stdout or "Agent exited with error").strip()
                state.set_error(card_id, f"Agent failed (exit {result.returncode}): {error_msg[:500]}")
        except subprocess.TimeoutExpired:
            state.set_error(card_id, "Agent timed out after 30 minutes")
        except Exception as e:
            state.set_error(card_id, str(e))

    threading.Thread(target=_run, daemon=True).start()


# --- Helpers ---

def _slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _read_calendar():
    """Read wp-calendar.json written by the scheduler agent."""
    if not os.path.exists(CALENDAR_FILE):
        return None
    try:
        with open(CALENDAR_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _calendar_is_stale():
    """Check if the calendar file is missing or older than CALENDAR_MAX_AGE."""
    if not os.path.exists(CALENDAR_FILE):
        return True
    age = time.time() - os.path.getmtime(CALENDAR_FILE)
    return age > CALENDAR_MAX_AGE


_calendar_refresh_running = False

def _request_calendar_refresh():
    """Sync the calendar by running the blog-wordpress-scheduler skill via Claude.
    Claude routes HTTP calls through WebFetch (Anthropic infra), bypassing Cloudflare."""
    global _calendar_refresh_running
    if _calendar_refresh_running:
        return

    claude = _find_claude()
    if not claude:
        return

    plugin_root_abs = os.path.abspath(PLUGIN_ROOT)

    def _sync():
        global _calendar_refresh_running
        _calendar_refresh_running = True
        try:
            subprocess.run(
                [claude, "--plugin-dir", plugin_root_abs, "-p", "--dangerously-skip-permissions",
                 "Run /blog-wordpress-scheduler list to sync the editorial calendar"],
                cwd=plugin_root_abs,
                timeout=120,
                capture_output=True,
                text=True,
            )
        except Exception:
            pass
        finally:
            _calendar_refresh_running = False

    threading.Thread(target=_sync, daemon=True).start()


def _build_board():
    """Build the board from state.json + wp-calendar.json.
    All WP data comes from the scheduler agent, not direct API calls."""
    cards_by_stage = {s: [] for s in STAGES}

    if _calendar_is_stale():
        _request_calendar_refresh()

    cal_age = time.time() - os.path.getmtime(CALENDAR_FILE) if os.path.exists(CALENDAR_FILE) else float("inf")
    visible_error = None
    if not os.path.exists(CALENDAR_FILE):
        visible_error = "calendar_syncing"
    elif cal_age > CALENDAR_ERROR_AGE:
        visible_error = "calendar_stale"

    # Build set of WP post IDs that still exist (from calendar sync)
    cal = _read_calendar()
    wp_draft_ids = set()
    wp_scheduled_ids = set()
    if cal:
        wp_draft_ids = {p["id"] for p in cal.get("drafts", [])}
        wp_scheduled_ids = {p["id"] for p in cal.get("scheduled", [])}
        all_wp_ids = wp_draft_ids | wp_scheduled_ids

        # Prune local cards whose WP posts were deleted (only if card is old)
        now = datetime.now(PST)
        for card in state.get_cards():
            wp_id = card.get("wordpress_id")
            if wp_id and card["stage"] in ("review", "staging", "scheduling"):
                if wp_id not in all_wp_ids:
                    # Only prune if the card has been in this stage for over an hour
                    stage_time = card.get("stage_history", {}).get(card["stage"], "")
                    if stage_time:
                        try:
                            entered = datetime.fromisoformat(stage_time)
                            if (now - entered).total_seconds() > 3600:
                                state.delete_card(card["id"])
                        except (ValueError, TypeError):
                            pass

    # Local cards — always show. These are actively in the pipeline.
    for card in state.get_cards():
        stage = card["stage"]

        if stage in CREATING_SUBSTAGES:
            cards_by_stage["creating"].append(card)
        elif stage == "scheduling":
            cards_by_stage["review"].append(card)
        elif stage in cards_by_stage:
            cards_by_stage[stage].append(card)

    # WP data — drafts, scheduled, all from WordPress (source of truth)
    if cal:
        # Drafts → review column (skip any already tracked by local cards)
        local_wp_ids = {c.get("wordpress_id") for c in state.get_cards() if c.get("wordpress_id")}
        # Also skip scheduled posts shown via local cards
        local_wp_ids.update(c.get("wordpress_id") for c in state.get_cards() if c.get("wordpress_id"))
        for post in cal.get("drafts", []):
            if post["id"] in local_wp_ids:
                continue
            cards_by_stage["review"].append(_wp_card(post, "review"))

        # Scheduled → always from WP (source of truth)
        for post in cal.get("scheduled", []):
            cards_by_stage["scheduled"].append(_wp_card(post, "scheduled"))

    return cards_by_stage, visible_error


def _wp_card(post, stage):
    """Create a card dict from a WP calendar entry."""
    return {
        "id": f"wp-{post['id']}",
        "topic": post["title"],
        "slug": "",
        "stage": stage,
        "wordpress_id": post["id"],
        "scheduled_date": post.get("date", "")[:10] if stage == "scheduled" else None,
        "edit_link": post.get("edit_link", ""),
        "post_link": post.get("link", ""),
        "header_image": None,
        "featured_image": post.get("featured_image"),
        "created_at": post.get("date", ""),
        "stage_history": {},
        "error": None,
    }


# --- Routes ---

@app.route("/")
def index():
    cards_by_stage, calendar_error = _build_board()
    return render_template(
        "board.html",
        stages=STAGES,
        stage_labels=STAGE_LABELS,
        cards_by_stage=cards_by_stage,
        calendar_error=calendar_error,
        creating_substage_labels=CREATING_SUBSTAGE_LABELS,
    )


@app.route("/admin")
def admin():
    cards = state.get_cards()
    return render_template("admin.html", cards=cards)


@app.route("/api/cards/clear", methods=["POST"])
def clear_all_cards():
    """Remove all cards from state."""
    data = {"cards": []}
    state._write(data)

    return redirect(url_for("admin"))


@app.route("/published")
def published():
    cal = _read_calendar()
    monthly_summary = defaultdict(lambda: {"count": 0, "posts": []})
    if cal:
        for post in cal.get("published", []):
            month_key = post.get("date", "")[:7]
            monthly_summary[month_key]["count"] += 1
            monthly_summary[month_key]["posts"].append({
                "title": post["title"],
                "date": post.get("date", "")[:10],
                "link": post.get("link", ""),
            })
    return render_template(
        "published.html",
        monthly_summary=dict(monthly_summary),
    )


@app.route("/api/cards", methods=["POST"])
def create_card():
    topic = request.form.get("topic", "").strip()
    if not topic:
        return redirect(url_for("index"))
    state.create_card(topic)

    return redirect(url_for("index"))


@app.route("/api/cards/<card_id>/start", methods=["POST"])
def start_pipeline(card_id):
    card = state.get_card(card_id)
    if card and card["stage"] == "ideas":
        state.advance_card(card_id, "writing")
        run_agent(card_id, card["topic"], action="blog-pipeline")
    
    return redirect(url_for("index"))


@app.route("/api/cards/<card_id>/schedule", methods=["POST"])
def schedule_card(card_id):
    """Trigger the scheduler agent to find the next date and schedule."""
    # Get wordpress_id from local card or from form (for WP-sourced cards)
    card = state.get_card(card_id)
    wp_id = None

    if card:
        wp_id = card.get("wordpress_id")
    else:
        # WP-sourced card (wp-XXXXX) — create a local card to track it
        wp_id_str = request.form.get("wp_id")
        if wp_id_str:
            wp_id = int(wp_id_str)
        elif card_id.startswith("wp-"):
            wp_id = int(card_id[3:])

        if wp_id:
            # Find the topic from the calendar data
            cal = _read_calendar()
            topic = f"Post {wp_id}"
            if cal:
                for post in cal.get("drafts", []):
                    if post["id"] == wp_id:
                        topic = post["title"]
                        break
            card = state.create_card(topic)
            card_id = card["id"]
            state.advance_card(card_id, "writing")
            state.advance_card(card_id, "copyedit")
            state.advance_card(card_id, "header_image")
            state.advance_card(card_id, "staging")
            state.advance_card(card_id, "review", wordpress_id=wp_id,
                edit_link=f"https://blog.postman.com/wp-admin/post.php?post={wp_id}&action=edit")

    if not wp_id:
        return redirect(url_for("index"))

    # Move to scheduling stage and run the agent
    state.advance_card(card_id, "scheduling")
    run_agent(card_id, str(wp_id), action="schedule")

    return redirect(url_for("index"))


@app.route("/api/cards/<card_id>", methods=["DELETE", "POST"])
def delete_card(card_id):
    if request.method == "POST" and request.form.get("_method") != "DELETE":
        return redirect(url_for("index"))
    state.delete_card(card_id)

    return redirect(url_for("index"))


HEADER_IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "blog-output", "images", "header")


@app.route("/images/<filename>")
def serve_header_image(filename):
    return send_from_directory(HEADER_IMAGE_DIR, filename)



@app.route("/api/refresh", methods=["POST"])
def refresh():
    """Force a file watcher check and calendar refresh."""
    check_and_advance(state)
    _request_calendar_refresh()
    return "", 204


@app.route("/api/board-hash")
def board_hash():
    """Lightweight endpoint for polling: returns a hash of current card states.
    When the hash changes, the client knows to reload the board."""
    cards = state.get_cards()
    digest = hashlib.md5(json.dumps(
        sorted([(c["id"], c["stage"], bool(c.get("error"))) for c in cards])
    ).encode()).hexdigest()
    return {"hash": digest}


# --- Startup ---

if __name__ == "__main__":
    _request_calendar_refresh()  # queue a sync on startup
    start_watcher(state)

    # Recover pipelines that were running when the server last stopped.
    # A "writing" card with no output file and no live agent means the agent
    # was killed (e.g. server restart). Restart it if it's been writing for
    # more than 5 minutes (gives any orphaned subprocess time to finish first).
    now_ts = time.time()
    blog_output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blog-output"))
    for card in state.get_cards():
        if card["stage"] != "writing" or card.get("error"):
            continue
        slug = card["slug"]
        if os.path.exists(os.path.join(blog_output_dir, f"{slug}.md")):
            continue  # file already written — watcher will advance the card
        writing_str = card.get("stage_history", {}).get("writing", "")
        try:
            elapsed_minutes = (now_ts - datetime.fromisoformat(writing_str).timestamp()) / 60
        except (ValueError, TypeError):
            elapsed_minutes = 999
        if elapsed_minutes > 5:
            print(f" * Recovering stale pipeline ({elapsed_minutes:.0f}m): {card['topic']}")
            run_agent(card["id"], card["topic"], action="blog-pipeline")

    print(" * Running on http://127.0.0.1:5001")
    print(" * Press Ctrl+C to quit")

    import atexit
    atexit.register(lambda: os._exit(0))

    try:
        app.run(port=5001, threaded=True)
    except KeyboardInterrupt:
        pass
    finally:
        os._exit(0)
