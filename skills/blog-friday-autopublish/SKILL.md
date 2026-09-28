---
name: blog-friday-autopublish
description: "AUTOMATED weekly pipeline, invoked by a local launchd job every Friday. Scans #product-updates Slack, drafts a blog post via blog-write, stages it to WordPress with the fixed Changelog header image (media ID 19880), and auto-schedules it to the next open Tue/Thu slot with NO human review. Posts a Slack notification to #devrel-staff with the edit link as the only safety net."
argument-hint: "(no arguments — invoked on schedule; running manually will auto-schedule a real post with no review step)"
allowed-tools: ["Bash", "Read", "Write", "Edit", "WebFetch", "WebSearch"]
---

# Friday Auto-Publish Pipeline

**This skill deliberately overrides the human-review guardrails documented in `blog-wordpress-stage` and `blog-wordpress-scheduler`.** Those skills exist specifically because AI-drafted content should be reviewed by a person before it's scheduled to go live on the public Postman blog. This pipeline was explicitly requested to skip that: it drafts, stages, and auto-schedules a post every Friday with zero human review. The only safety net is a Slack notification to `#devrel-staff` posted immediately after scheduling — the team has until the scheduled date (the next open Tue/Thu, 8:00 AM PST) to catch a bad post and pull it before it publishes.

If a human runs this skill manually (not via the scheduled job), tell them plainly that it will draft, stage, and auto-schedule a real post with no review step, and confirm they want that before proceeding.

## Prerequisites

Requires all of these environment variables (in `~/.claude/settings.json` under `"env"`):

- `WP_USERNAME`, `WP_APP_PASSWORD` — WordPress credentials for blog.postman.com
- `SLACK_BOT_TOKEN` — Slack bot token with `channels:history`, `channels:read`, and `chat:write` scopes

If any are missing, stop immediately and report which one.

## Step 1: Generate the product updates summary

Run `/devrel-skills:blog-prod-updates` (default 7-day window).

Read the resulting `blog-output/prod-updates-YYMMDD.md`. If it indicates there were no new posts, or that every post in the window was a duplicate already covered, **stop the pipeline here** — do not draft or stage anything. Skip to Step 6 and send a short Slack message to `#devrel-staff` noting the run was skipped and why, then end.

Otherwise, continue to Step 2.

## Step 2: Draft the blog post

Run `/devrel-skills:blog-write blog-output/prod-updates-YYMMDD.md`.

Tell blog-write to pick the single strongest angle from the "Blog Angle Suggestions" section of the prod-updates file (combining whichever updates make the most coherent post) and write that as a `What's new in Postman: …` post. Do not ask a human to choose between angles — pick the best one and proceed.

This produces `blog-output/{slug}.md` with YAML frontmatter, and automatically triggers the copyeditor hook.

## Step 3: Read frontmatter and convert to HTML

Same as `blog-wordpress-stage` Steps 1–2:

1. Read `blog-output/{slug}.md`. Extract `suggested_title`, `meta_description`, `primary_keyword`, `secondary_keywords`. If `meta_description` is missing or a placeholder, generate one (under 155 characters, single sentence, active voice) and write it back into the frontmatter.
2. Read `skills/blog-wordpress-stage/references/wp-md-to-html.py`, write it to `/tmp/wp-md-to-html.py`, replace `INPUT_FILE` with the `blog-output/{slug}.md` path, and run it. This produces `/tmp/wp-post-content.html`.

## Step 4: Upload inline images and attach the fixed header image

**Never generate or upload a new header image for this pipeline.** The featured image is always WordPress media ID `19880` (`https://blog.postman.com/wp-content/uploads/2026/05/Changelog-scaled.png`) — the same image every week.

Read `references/wp-upload-and-fix-image.py`, write it to `/tmp/wp-upload-and-fix-image.py`, replace `MARKDOWN_FILE_HERE` with the `blog-output/{slug}.md` path, and run it. This uploads any inline images referenced in the post body, rewrites their URLs in `/tmp/wp-post-content.html`, and writes `/tmp/wp-image-results.json` with `featured_media_id: 19880`.

## Step 5: Check for duplicates, generate tags, and create the draft

1. Read `skills/blog-wordpress-stage/references/wp-check-post.py`, write to `/tmp/wp-check-post.py`, replace `POST_TITLE_HERE` with the post title, run it. If an exact match exists, use that `post_id` to update instead of create.
2. Choose 3 specific tags from the content. Read `skills/blog-wordpress-stage/references/wp-manage-tags.py`, write to `/tmp/wp-manage-tags.py`, replace `TAG_NAMES`, run it, and note the tag IDs.
3. Read `skills/blog-wordpress-stage/references/wp-stage-post.py`, write to `/tmp/wp-stage-post.py`, fill in `POST_TITLE`, `META_DESCRIPTION_HERE`, `FOCUS_KEYPHRASE_HERE`, `TAG_IDS`, and `POST_ID` (from the duplicate check, or `None`), and run it. This creates the draft with `featured_media` already set to 19880 from `/tmp/wp-image-results.json`.
4. Write the returned WordPress post ID back into `blog-output/{slug}.md`'s frontmatter as `wordpress_id`, same as `blog-wordpress-stage` Step 7.

## Step 6: Auto-schedule to the next open slot

Unlike `blog-wordpress-scheduler`, this runs with **no embargo and no human confirmation**.

Read `references/wp-auto-schedule.py`, write it to `/tmp/wp-auto-schedule.py`, replace `POST_ID` with the ID from Step 5, and run it. This finds the next open Tue/Thu slot (falling back to Mon/Wed, then searching further out — same priority rules as `blog-wordpress-scheduler`), skips US holidays and existing conflicts, and `POST`s the post to `date_gmt` at `T16:00:00` (8:00 AM PST) with `status: "future"`. It prints and saves the result to `/tmp/wp-autoschedule-result.json`.

## Step 7: Notify #devrel-staff on Slack

Read `references/slack-notify.py`, write it to `/tmp/slack-notify.py`.

Build the message from the Step 6 result and the post title:

```
🤖 Friday auto-publish (no human review): "{title}"

Drafted from this week's #product-updates, staged with the standard Changelog header image, and auto-scheduled to go live {scheduled_display} at 8:00 AM PST.

Nobody has reviewed this post. If something's off, edit or unschedule it before then:
{edit_link}
```

Replace `MESSAGE_TEXT_HERE` in the script with this message, then run it.

**If the skipped-run case from Step 1 applies instead**, send this shorter message and stop:

```
🤖 Friday auto-publish: no new product updates (Product Stage ≥ 7) this week — nothing drafted.
```

## Error Handling

- **Missing env var:** Stop immediately, report which one, do not attempt a Slack notification (it likely can't be sent either).
- **Any failure from Step 2 onward** (blog-write, staging, scheduling): still attempt to send a Slack message to `#devrel-staff` reporting what step failed and why, so the team knows the automation needs attention. Do not leave a half-staged post silently orphaned without at least a Slack heads-up.
- **WordPress auth failure (401/403):** Report in the Slack failure message that credentials may need regenerating.
- **Image upload failure:** Continue without inline images rather than aborting the whole run; the featured image (19880) is independent of inline image upload and should still be set.

## Important Guidelines

- **Never generate a new header image.** Always use media ID `19880`.
- **Never ask a human to pick a blog angle or approve the schedule.** This skill exists specifically to run unattended.
- **Always send the Slack notification** after a successful schedule (or after a failure) — it is the only review signal anyone gets.
- **Times are always PST, hardcoded to 8:00 AM (`T16:00:00` UTC)** regardless of the machine's local timezone, consistent with `blog-wordpress-scheduler`.
