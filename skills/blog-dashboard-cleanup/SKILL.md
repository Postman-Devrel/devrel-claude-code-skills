---
name: blog-dashboard-cleanup
description: "Clean up the blog pipeline Kanban dashboard — removes cards that are stuck before the staging column (ideas, creating substages). Leaves cards in staging, review, and scheduled untouched."
argument-hint: "[--all] (omit to remove only pre-staging cards; pass --all to clear every card)"
allowed-tools: ["Read", "Write", "Bash"]
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

The dashboard state lives at `dashboard/state.json` relative to the plugin root. Read `references/state-file-ops.md` for the path-resolution and file-locking patterns used in the steps below.

## Steps

### Step 1: Read Current State

Use the path resolution and shared-lock read pattern from `references/state-file-ops.md`. Load `cards = data.get("cards", [])`.

### Step 2: Identify Cards to Remove

Use the filter-cards pattern from `references/state-file-ops.md`, passing the user's argument (`None` or `"--all"`).

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

Set `data["cards"] = to_keep`, then use the exclusive-lock write pattern from `references/state-file-ops.md`.

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
