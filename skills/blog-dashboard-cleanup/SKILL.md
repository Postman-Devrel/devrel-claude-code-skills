---
name: blog-dashboard-cleanup
description: "Clean up the blog pipeline Kanban dashboard — removes cards that are stuck before the staging column (ideas, creating substages). Leaves cards in staging, review, and scheduled untouched."
argument-hint: "[--all] (omit to remove only pre-staging cards; pass --all to clear every card)"
---

# Blog Dashboard Cleanup

Remove stale or stuck cards from the blog pipeline Kanban board before they reach WordPress staging. Safe to run at any time — it never touches WordPress.

## What Gets Removed

By default (no argument), this skill removes cards whose stage is any of:

- `ideas` — never started
- `writing` — stuck in the writing substage
- `copyedit` — stuck in the copyedit substage
- `header_image` — stuck in the header image substage
- `creating` — stuck in the creating column (catch-all)

Cards in `staging`, `review`, or `scheduled` are left untouched — they have live WordPress drafts behind them.

If the user passes `--all`, remove every card regardless of stage.

## State File Location

The dashboard state lives at `dashboard/state.json` relative to the plugin root. Locate it using the `CLAUDE_PLUGIN_ROOT` env var if set, otherwise resolve it relative to this skill file:

```python
import os, json, fcntl

plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
state_path = os.path.join(plugin_root, "dashboard", "state.json")
```

## Steps

### Step 1: Read Current State

```python
if not os.path.exists(state_path):
    print("Dashboard state file not found — is the dashboard installed?")
    print(f"Expected: {state_path}")
    raise SystemExit(1)

with open(state_path, "r") as f:
    fcntl.flock(f, fcntl.LOCK_SH)
    try:
        data = json.load(f)
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)

cards = data.get("cards", [])
```

### Step 2: Identify Cards to Remove

```python
# Argument passed by user (may be None or "--all")
arg = "ARGUMENT_HERE"
remove_all = arg and arg.strip().lower() == "--all"

PRE_STAGING_STAGES = {"ideas", "writing", "copyedit", "header_image", "creating"}

if remove_all:
    to_remove = cards
    to_keep = []
else:
    to_remove = [c for c in cards if c.get("stage") in PRE_STAGING_STAGES]
    to_keep = [c for c in cards if c.get("stage") not in PRE_STAGING_STAGES]
```

### Step 3: Confirm Before Removing

If there is nothing to remove, tell the user:

```
Dashboard is already clean — no stuck cards found.

  Cards in staging / review / scheduled: N
```

If there are cards to remove, print a summary and ask for confirmation:

```
Cards to remove (stuck before staging):

  ID        Stage         Topic
  --------  ------------  ------------------------------------------
  a1b2c3d4  writing       Testing OAuth 2.0 Flows in Postman
  e5f6g7h8  ideas         GraphQL Testing with Postman

Remove these 2 card(s)? [y/N]
```

If the user passes `--all`, the confirmation message should say "Remove ALL N card(s) from the board?" instead.

Read the user's response. If they say anything other than `y` or `yes` (case-insensitive), abort:

```
Cancelled — no cards removed.
```

### Step 4: Write Updated State

```python
data["cards"] = to_keep

with open(state_path, "w") as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    try:
        json.dump(data, f, indent=2)
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
```

### Step 5: Confirm Result

```
Removed 2 card(s) from the dashboard.

  Kept (staging / review / scheduled): 3
  Board is clean — safe to continue the pipeline.
```

## Important Notes

- This skill only edits `dashboard/state.json`. It does **not** delete blog-output files, WordPress drafts, or any other files.
- If a card has a `wordpress_id` and is still in a pre-staging stage (e.g., stuck in `writing` with a WP ID somehow), it is still removed — the WP draft remains and can be found manually in wp-admin.
- The dashboard does not need to be running for this skill to work.
