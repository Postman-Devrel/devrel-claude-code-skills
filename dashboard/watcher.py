"""File system watcher that auto-advances Kanban cards based on blog-output/ changes."""

import logging
import os
import threading
import time
from datetime import datetime
import yaml


BLOG_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "blog-output")
HEADER_DIR = os.path.join(BLOG_OUTPUT, "images", "header")
LOG_FILE = os.path.join(os.path.dirname(__file__), "watcher.log")
POLL_INTERVAL = 3  # seconds
WRITING_TIMEOUT_MINUTES = 30  # mark error if stuck in writing longer than this

_logger = logging.getLogger("watcher")
_logger.setLevel(logging.INFO)
_fh = logging.FileHandler(LOG_FILE)
_fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
_logger.addHandler(_fh)

# Track files we've already seen so we can detect new ones
_known_markdown = set()
_known_copyedit = set()
_known_headers = set()


def _read_frontmatter(filepath):
    """Extract YAML frontmatter from a markdown file."""
    try:
        with open(filepath, "r") as f:
            content = f.read()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return yaml.safe_load(parts[1])
    except Exception:
        pass
    return {}


def _scan_files():
    """Scan blog-output/ and return current file state."""
    state = {"markdown": {}, "copyedit": {}, "headers": {}, "wordpress_ids": {}}

    if os.path.isdir(BLOG_OUTPUT):
        for name in os.listdir(BLOG_OUTPUT):
            if not name.endswith(".md"):
                continue
            filepath = os.path.join(BLOG_OUTPUT, name)
            if name.endswith("-copyedit.md"):
                slug = name.replace("-copyedit.md", "")
                state["copyedit"][slug] = filepath
            else:
                slug = name.replace(".md", "")
                state["markdown"][slug] = filepath
                fm = _read_frontmatter(filepath)
                if fm.get("wordpress_id"):
                    state["wordpress_ids"][slug] = fm["wordpress_id"]

    if os.path.isdir(HEADER_DIR):
        for name in os.listdir(HEADER_DIR):
            if name.startswith("header-") and name.endswith(".png"):
                slug = name.replace("header-", "").replace(".png", "")
                state["headers"][slug] = os.path.join(HEADER_DIR, name)

    return state


def _update_card(state_manager, card_id, **kwargs):
    """Update arbitrary fields on a card."""
    data = state_manager._read()
    for card in data["cards"]:
        if card["id"] == card_id:
            for key, val in kwargs.items():
                card[key] = val
            break
    state_manager._write(data)


def _oldest_card_in_stage(state_manager, stage):
    """Find the oldest card in a given stage."""
    cards = [c for c in state_manager.get_cards() if c["stage"] == stage]
    if not cards:
        return None
    return min(cards, key=lambda c: c.get("created_at", ""))


def check_and_advance(state_manager):
    """Check files and advance any cards that match."""
    files = _scan_files()
    cards = state_manager.get_cards()
    changed = False

    # Find new markdown files (not yet known)
    new_markdown = set(files["markdown"].keys()) - _known_markdown
    new_copyedit = set(files["copyedit"].keys()) - _known_copyedit
    new_headers = set(files["headers"].keys()) - _known_headers

    # Track slugs claimed this poll so two writing cards don't grab the same file
    claimed_slugs = {c["slug"] for c in cards if c["stage"] != "writing"}

    # --- Timeout: writing cards stuck too long with no output file ---
    now_ts = time.time()
    for card in cards:
        if card["stage"] != "writing" or card.get("error"):
            continue
        writing_time_str = card.get("stage_history", {}).get("writing")
        if not writing_time_str:
            continue
        try:
            writing_ts = datetime.fromisoformat(writing_time_str).timestamp()
        except (ValueError, TypeError):
            continue
        elapsed_minutes = (now_ts - writing_ts) / 60
        if elapsed_minutes > WRITING_TIMEOUT_MINUTES:
            slug = card["slug"]
            if slug not in files["markdown"]:
                _logger.warning("timeout: card %s (%s) stuck in writing for %.0fm", card["id"], slug, elapsed_minutes)
                state_manager.set_error(
                    card["id"],
                    f"No output file found after {WRITING_TIMEOUT_MINUTES} minutes. "
                    f"The pipeline agent may have failed silently. "
                    f"Delete this card and re-run /blog-pipeline \"{card['topic']}\" to retry."
                )
                changed = True

    # --- Stage: writing → copyedit ---
    # 1) Exact slug match (fastest path)
    # 2) Fallback: any file modified after this card entered the writing stage
    #    — handles slug mismatches and files that existed before server restart
    for card in cards:
        if card["stage"] != "writing":
            continue
        slug = card["slug"]
        matched_slug = None

        if slug in files["markdown"] and slug not in claimed_slugs:
            matched_slug = slug
        else:
            # Parse when this card entered writing so we can compare mtime
            writing_time = None
            writing_time_str = card.get("stage_history", {}).get("writing")
            if writing_time_str:
                try:
                    writing_time = datetime.fromisoformat(writing_time_str).timestamp()
                except (ValueError, TypeError):
                    pass

            if writing_time is not None:
                for file_slug, filepath in files["markdown"].items():
                    if file_slug in claimed_slugs:
                        continue
                    if os.path.getmtime(filepath) > writing_time:
                        matched_slug = file_slug
                        break

        if matched_slug:
            _known_markdown.add(matched_slug)
            claimed_slugs.add(matched_slug)
            fm = _read_frontmatter(files["markdown"][matched_slug])
            title = fm.get("suggested_title", card["topic"])
            _update_card(state_manager, card["id"], slug=matched_slug, topic=title)
            state_manager.advance_card(card["id"], "copyedit")
            _logger.info("advance: card %s writing -> copyedit (slug=%s)", card["id"], matched_slug)
            changed = True

    # Any remaining new markdown files with no writing card to claim them
    for new_slug in list(new_markdown):
        if new_slug in _known_markdown or new_slug in claimed_slugs:
            continue
        writing_card = _oldest_card_in_stage(state_manager, "writing")
        if writing_card:
            _known_markdown.add(new_slug)
            claimed_slugs.add(new_slug)
            fm = _read_frontmatter(files["markdown"][new_slug])
            title = fm.get("suggested_title", new_slug.replace("-", " ").title())
            _update_card(state_manager, writing_card["id"], slug=new_slug, topic=title)
            state_manager.advance_card(writing_card["id"], "copyedit")
            changed = True

    # --- Stage: copyedit → header_image ---
    for card in state_manager.get_cards():
        if card["stage"] != "copyedit":
            continue
        slug = card["slug"]
        if slug in files["copyedit"]:
            _known_copyedit.add(slug)
            state_manager.advance_card(card["id"], "header_image")
            _logger.info("advance: card %s copyedit -> header_image (slug=%s)", card["id"], slug)
            changed = True

    # --- Stage: header_image → staging ---
    for card in state_manager.get_cards():
        if card["stage"] != "header_image":
            continue
        slug = card["slug"]
        if slug in files["headers"]:
            _known_headers.add(slug)
            state_manager.advance_card(
                card["id"], "staging",
                header_image=f"header-{slug}.png",
            )
            _logger.info("advance: card %s header_image -> staging (slug=%s)", card["id"], slug)
            changed = True

    # --- Stage: staging → review ---
    for card in state_manager.get_cards():
        if card["stage"] != "staging":
            continue
        slug = card["slug"]
        if slug in files["wordpress_ids"]:
            wp_id = files["wordpress_ids"][slug]
            state_manager.advance_card(
                card["id"], "review",
                wordpress_id=wp_id,
                edit_link=f"https://blog.postman.com/wp-admin/post.php?post={wp_id}&action=edit",
            )
            _logger.info("advance: card %s staging -> review (slug=%s, wp_id=%s)", card["id"], slug, wp_id)
            changed = True

    # --- Auto-discover: new files with no card at all ---
    all_card_slugs = {c["slug"] for c in state_manager.get_cards()}
    for file_slug in set(files["markdown"].keys()) - _known_markdown:
        if file_slug in all_card_slugs:
            continue
        _known_markdown.add(file_slug)

        fm = _read_frontmatter(files["markdown"][file_slug])
        topic = fm.get("suggested_title", file_slug.replace("-", " ").title())
        card = state_manager.create_card(topic)
        _update_card(state_manager, card["id"], slug=file_slug)

        # Advance to furthest known stage
        if file_slug in files["wordpress_ids"]:
            wp_id = files["wordpress_ids"][file_slug]
            state_manager.advance_card(card["id"], "writing")
            state_manager.advance_card(card["id"], "copyedit")
            state_manager.advance_card(card["id"], "header_image")
            state_manager.advance_card(card["id"], "staging")
            state_manager.advance_card(
                card["id"], "review",
                wordpress_id=wp_id,
                edit_link=f"https://blog.postman.com/wp-admin/post.php?post={wp_id}&action=edit",
            )
        elif file_slug in files["headers"]:
            state_manager.advance_card(card["id"], "writing")
            state_manager.advance_card(card["id"], "copyedit")
            state_manager.advance_card(card["id"], "header_image")
            state_manager.advance_card(
                card["id"], "staging",
                header_image=f"header-{file_slug}.png",
            )
        elif file_slug in files["copyedit"]:
            state_manager.advance_card(card["id"], "writing")
            state_manager.advance_card(card["id"], "copyedit")
            state_manager.advance_card(card["id"], "header_image")
        else:
            state_manager.advance_card(card["id"], "writing")
            state_manager.advance_card(card["id"], "copyedit")

        changed = True

    return changed


def start_watcher(state_manager):
    """Start the file watcher in a background thread."""
    # Seed known files so we don't auto-discover existing ones on first run
    files = _scan_files()
    _known_markdown.update(files["markdown"].keys())
    _known_copyedit.update(files["copyedit"].keys())
    _known_headers.update(files["headers"].keys())

    def _poll():
        while True:
            try:
                check_and_advance(state_manager)
            except Exception as e:
                _logger.exception("poll error: %s", e)
            time.sleep(POLL_INTERVAL)

    t = threading.Thread(target=_poll, daemon=True)
    t.start()
    return t
