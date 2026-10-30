---
name: blog-history-sweep
description: "Sweep published posts on blog.postman.com for a topic or keywords, flag the ones that don't reference current content (e.g. old Postman MCP / Claude Code plugin install steps), and write a reviewable checklist. Optionally prepends an HTML editor's note to the approved posts, with backups and restore."
argument-hint: "[preset-name | \"keyword1, keyword2\"] (e.g. 'postman-plugin')"
allowed-tools: ["Bash", "Read", "Write", "Edit", "AskUserQuestion"]
---

# Blog History Sweep — blog.postman.com

Find published posts that talk about a topic but are out of date, list them for review, and (only after approval) add an editor's note to the top of each.

`<skill-dir>` below means the directory containing this SKILL.md (`${CLAUDE_SKILL_DIR}`). Output goes to `sweep-output/` in the current project.

## Prerequisites

Needs `WP_USERNAME` and `WP_APP_PASSWORD` in `~/.claude/settings.json` under `"env"` — the same credentials as `blog-wordpress-stage`. If either is missing, tell the user to create an application password at **blog.postman.com/wp-admin/profile.php** and add both to `"env"`, then stop.

## Step 1: Gather Inputs

Read `<skill-dir>/references/presets.json` and list `<skill-dir>/notes/*.html`.

- **If the argument names a preset** (e.g. `postman-plugin`), use its `keywords`, `context_keywords`, `near`, `exclude`, `current_markers`, and `note`. Show them to the user and confirm before continuing.
- **Otherwise**, ask the user (one `AskUserQuestion` call or a short prompt):
  1. **Topic / keywords** — comma-separated phrases to search for (from the argument if given).
  2. **Current-content markers** — strings whose presence means a post is already up to date, such as a URL or install command (e.g. `github.com/postmanlabs/postman-plugin`). Can be blank, which flags every match.
  3. **Context keywords** (optional) — terms too broad to match alone (e.g. `Codex`, `Antigravity`, `Gemini`) plus the **near** terms that must appear within ~20 words for them to count (e.g. `install, plugin, marketplace, set up`).
  4. **Exclude** (optional) — comma-separated phrases; any post whose title or body matches one is left out (e.g. `Astropods`).
  5. **Editor's note** — pick an existing file from `notes/`, or paste a new HTML snippet. For a new snippet, ask for a short kebab-case id and save it to `<skill-dir>/notes/{id}.html`.
  6. **Since** (optional) — only sweep posts published on or after `YYYY-MM-DD`.

  Offer to save the new combination as a preset in `presets.json` so it can be re-run by name.

The note id is the filename without `.html`. It is also written into each updated post as `<!-- editor-note:{id} -->`, which is how later sweeps know a post already has the note.

## Step 2: Run the Sweep

```bash
python3 <skill-dir>/references/sweep.py \
  --keywords "KW1,KW2" --context-keywords "CK1,CK2" --near "N1,N2" \
  --markers "M1,M2" --exclude "EX1,EX2" \
  --note-id NOTE_ID --note-file <skill-dir>/notes/NOTE_ID.html \
  --out-dir sweep-output --label LABEL [--since YYYY-MM-DD]
```

`LABEL` is the preset name, or a slug of the first keyword. The script searches each keyword through the WordPress REST API, confirms an actual phrase match in the title or body (WP search is word-based; context keywords also need a near term within ~20 words), and sorts every match into:

| Status | Meaning |
|---|---|
| `flagged` | Mentions a keyword, has no current-content marker, and doesn't have the note |
| `current` | Already contains at least one marker |
| `noted` | Already has this editor's note |
| `excluded` | Matches an exclude phrase — listed for reference, never updated |

It writes `sweep-output/sweep-{label}-YYMMDD.md` (the review list) and a matching `.json`, then prints a JSON summary.

## Step 3: Present for Review

Show the summary counts and the flagged list (title, date, link, matched keywords). Point the user at the review file:

> Review `sweep-output/sweep-{label}-YYMMDD.md`. Flagged posts are pre-checked — uncheck any that shouldn't get the note. Spot-check the snippets: a keyword match isn't always about the topic (e.g. a third-party "MCP server" post).

Read a few flagged snippets yourself and call out any that look like false positives, but leave the checkboxes for the user to change.

**Stop here unless the user asks to apply the note.** The review list is the default deliverable.

## Step 4: Apply the Editor's Note (only on explicit request)

This edits **live, published posts**. Before running it:

1. Re-read the review file to pick up the user's edits. Count the checked posts.
2. Run a dry run and show the result:
   ```bash
   python3 <skill-dir>/references/apply-notes.py --review REVIEW_FILE \
     --note-file <skill-dir>/notes/NOTE_ID.html --note-id NOTE_ID \
     --backup-dir sweep-output/backups/LABEL-YYMMDD --dry-run
   ```
3. Show the note HTML and the list of posts, and ask: "Add this note to N published posts?" Proceed only on a clear yes.
4. Run the same command without `--dry-run`.

The script fetches each post's raw content, backs it up to `{backup-dir}/{id}.json`, and prepends the note in a `wp:html` block. Only `content` is written, so the publish date, status, slug, and Yoast fields stay as they are. Posts that already have the marker are skipped, so it's safe to re-run.

Report each post as updated/skipped with its link, and give the backup directory path.

## Undo

```bash
python3 <skill-dir>/references/apply-notes.py --restore sweep-output/backups/LABEL-YYMMDD [--ids 123,456]
```

This restores the backed-up content exactly. Confirm with the user before running it, since it also writes to live posts.

## Error Handling

- **401/403:** credentials are invalid or expired, or the user can't edit that post. Suggest regenerating the application password. The sweep only needs read access; applying needs editor rights.
- **Network timeout:** the sweep retries once. If it still fails, ask the user to check their network or VPN.
- **Apply fails partway:** posts updated so far have backups. Report which IDs succeeded. A re-run skips them because of the marker.
