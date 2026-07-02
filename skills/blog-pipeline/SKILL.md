---
name: blog-pipeline
description: "Full blog creation pipeline — write (from topic, draft, or Google Doc), copyedit, generate header image, and stage to WordPress. Detects input type automatically."
argument-hint: "[topic, file path, or Google Docs URL] (e.g. 'OAuth 2.0 in Postman', 'prompts/draft.md', or Google Docs URL)"
allowed-tools: ["Bash", "Write"]
---

# Blog Pipeline

End-to-end blog creation: from idea to WordPress draft. Detects input type and routes through the appropriate skills.

## Input Handling

This skill accepts flexible input:

- **A topic string** (e.g., "Testing OAuth 2.0 flows in Postman") — write a blog post from scratch
- **A file path** (e.g., `prompts/my-draft.md` or `blog-output/existing-post.md`) — use as a draft or outline
- **A Google Docs URL** (e.g., `https://docs.google.com/document/d/1abc.../edit`) — import and convert from Google Docs
- **No argument** — ask the user: "Enter a topic, file path to a draft, or Google Docs URL"

## Input Detection

Determine the input type:

1. If the input contains `docs.google.com/document` → **Google Doc import**
2. If the input ends in `.md` or contains `/` and the file exists → **Draft/outline**
3. Otherwise → **Topic string** (write from scratch)

## Pipeline Steps

### Step 1: Create the Blog Post

Based on the detected input type, run the appropriate skill:

- **Topic string** → Run `/blog-write <topic>`
- **File path** → Run `/blog-write <filepath>`
- **Google Docs URL** → Run `/blog-create-from-gdoc <url>`

Wait for the skill to complete. Note the output file path — it will be in `blog-output/` as a `.md` file.

### Step 2: Copyedit

Run `/blog-copyeditor <output-file-path>` on the file produced in Step 1.

Wait for it to complete.

### Step 3: Generate Header Image

Run `/blog-header-image <output-file-path>` on the original blog post file (not the copyedit report).

Wait for it to complete. The image will be saved to `blog-output/images/header/`.

### Step 4: Stage to WordPress

Run `/blog-wordpress-stage <output-file-path>` on the blog post file.

This uploads the post as a draft, attaches the header image as the featured image, sets SEO metadata and tags, and writes the `wordpress_id` back to the markdown frontmatter.

Wait for it to complete.

### Step 5: Report Results

Summarize the pipeline run:

```
Blog pipeline complete.

  Input:          [topic / file / Google Doc URL]
  Blog post:      blog-output/{slug}.md
  Copyedit:       blog-output/{slug}-copyedit.md
  Header image:   blog-output/images/header/header-{slug}.png
  WordPress:      https://blog.postman.com/wp-admin/post.php?post={id}&action=edit
```

### Step 6: Offer to Schedule

After reporting, ask the user:

> "Would you like to schedule this post now? (yes/no)"

If the user says **yes**:
- Run `/blog-wordpress-scheduler reschedule <wordpress_id> next`
- The scheduler will ask about embargo dates and find the next available slot
- Report the scheduled date when done

If the user says **no**:
- Tell the user: "The post is staged as a draft. Run `/blog-wordpress-scheduler` when you're ready to schedule."

## Important Guidelines

- **Run steps sequentially** — each step depends on the previous one's output.
- **Do not skip steps** — every post gets copyedited, gets a header image, and gets staged.
- **Note the output file path from Step 1** — all subsequent steps use this same file.
- **If any step fails**, stop the pipeline, report the error, and tell the user which step failed so they can retry from that point.
