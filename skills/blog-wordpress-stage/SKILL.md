---
name: blog-wordpress-stage
description: "Stage a blog post to WordPress (blog.postman.com). Takes a markdown file, header image, or a Google Docs URL. When given a Google Doc, converts it to markdown first. Creates or updates a draft post, uploads the featured image, sets SEO metadata."
argument-hint: "[markdown file path | Google Docs URL] [header image path] (e.g. 'blog-output/my-post.md' or 'https://docs.google.com/document/d/1abc.../edit')"
allowed-tools: ["Bash", "Read", "Write", "Edit"]
---

# WordPress Blog Post Stager — blog.postman.com

Stage blog posts to the Postman WordPress site. Converts markdown to HTML, uploads a featured image, sets SEO metadata, and finds the next open publish slot on the Tuesday/Wednesday/Thursday schedule.

Accepts either a local markdown file or a Google Docs URL — if given a Google Doc, it converts the doc to markdown first, then stages it.

## Input Handling

This skill accepts:

- **Markdown file path** — path to a blog post markdown file (e.g., `blog-output/testing-oauth-flows.md`)
- **Google Docs URL** — a link like `https://docs.google.com/document/d/1abc.../edit`; the skill will convert the doc to markdown before staging
- **Header image path** (optional) — path to a header image PNG; can be provided alongside either of the above

If no arguments are provided, ask the user whether they have a local markdown file or a Google Doc URL.

**Automatic header image detection:** If only the markdown file is provided (and no header image argument), automatically look for a matching header image at `blog-output/images/header/header-{markdown-basename}.png`. For example, if the markdown file is `blog-output/testing-oauth-flows.md`, check for `blog-output/images/header/header-testing-oauth-flows.png`. If found, use it as the featured image without asking. If not found, stage the post without a featured image.

**Google Doc detection:** If the argument contains `docs.google.com/document`, treat it as a Google Docs URL and run Step 0 before the normal workflow.

## Step 0: Convert Google Doc to Markdown (only if input is a Google Docs URL)

Skip this step if the input is already a local markdown file.

### Steps 0a–0d: Extract, fetch, download images, convert to markdown

Read `references/gdoc-to-markdown.py`, write it to `/tmp/gdoc-to-markdown.py`, replace `GOOGLE_DOCS_URL_HERE` with the actual URL, then run it:

```bash
python3 /tmp/gdoc-to-markdown.py
```

This outputs `blog-output/{slug}.md` with frontmatter and local image references.

After Step 0d completes, tell the user the Google Doc was converted and saved to `blog-output/{slug}.md`, then immediately proceed to Step 0e.

### Step 0e: Auto-Copyedit the Converted Markdown (Google Doc path only)

Before staging, run the full `blog-copyeditor` workflow on `blog-output/{slug}.md` in **hook mode** — auto-applying all safe, non-controversial fixes directly to the file. This ensures the Google Doc content meets Postman's writing standards before it reaches WordPress.

**What to do:**

1. Read all five Postman writing style guide files:
   - `postman-writing-style-guide/languageandgrammar.md`
   - `postman-writing-style-guide/brandedterms.md`
   - `postman-writing-style-guide/wordlist.md`
   - `postman-writing-style-guide/inclusivewords.md`
   - `postman-writing-style-guide/formatting.md`

2. Read `blog-output/{slug}.md` and run the full copy edit and SEO analysis pass (grammar, syntax, repetitive structures, style guide compliance, technical accuracy, SEO).

3. **Auto-apply** all safe, non-controversial fixes directly to `blog-output/{slug}.md` using the Edit tool:
   - Typo and spelling corrections
   - Missing or incorrect code fence language identifiers
   - Broken markdown syntax
   - Incorrect product name capitalization
   - Branded term corrections (per `brandedterms.md`)
   - Prohibited word replacements (per `wordlist.md`)
   - Inclusive language substitutions (per `inclusivewords.md`)
   - Update `suggested_title`, `meta_description`, `primary_keyword`, and `secondary_keywords` frontmatter fields with the SEO recommendations

4. Write the full copy edit report to `blog-output/{slug}-copyedit.md`.

5. Tell the user a brief summary: how many fixes were auto-applied and the overall quality score. Do **not** pause for user review — continue directly to Step 1 with the updated `blog-output/{slug}.md`.

After Step 0e completes, use `blog-output/{slug}.md` as the markdown file for the rest of the workflow (Steps 1–8).

## Prerequisites

This skill requires WordPress credentials. The following environment variables must be set in `~/.claude/settings.json` under `"env"`:

- `WP_USERNAME` — WordPress username for blog.postman.com
- `WP_APP_PASSWORD` — WordPress application password (generate one at blog.postman.com/wp-admin/profile.php under "Application Passwords")

If either is missing, tell the user:
> To use this skill, you need WordPress application credentials. Go to **blog.postman.com/wp-admin/profile.php**, scroll to "Application Passwords", create one, and add these to your `~/.claude/settings.json`:
> ```json
> "env": {
>   "WP_USERNAME": "your-username",
>   "WP_APP_PASSWORD": "xxxx xxxx xxxx xxxx xxxx xxxx"
> }
> ```

## Workflow

### Step 1: Read and Parse the Markdown File

1. Read the markdown file using the Read tool
2. Extract YAML frontmatter fields:
   - `suggested_title` — use as the WordPress post title
   - `meta_description` — use as the Yoast SEO meta description
   - `primary_keyword` — use as the Yoast focus keyphrase
   - `secondary_keywords` — for reference
3. Extract the markdown body (everything after the frontmatter closing `---`)
4. **Generate a meta description if missing or empty.** If `meta_description` is absent, blank, or a generic placeholder in the frontmatter, generate one by reading the full post body. The meta description must be:
   - Under 155 characters
   - A single complete sentence that summarizes what the reader will learn or accomplish
   - Include the primary topic/keyword naturally
   - Written in active voice, addressed to the reader (e.g., "Learn how to..." or "Build a...")
   - No marketing fluff — factual and specific to the post's content
   
   After generating, write the meta description back into the markdown file's `meta_description` frontmatter field using the Edit tool so the local file stays in sync.

### Step 2: Convert Markdown to HTML

Write and run a Python script to convert the markdown body to HTML suitable for WordPress. **CRITICAL: Save the HTML to a temp file** — do NOT try to embed the HTML inline in the post creation script, as this will break on quotes and special characters.

Read `references/wp-md-to-html.py`, write it to `/tmp/wp-md-to-html.py`, replace `INPUT_FILE` with the actual markdown path, then run it:

```bash
python3 /tmp/wp-md-to-html.py
```

The HTML is now at `/tmp/wp-post-content.html` for use in Step 5.

### Step 3: Upload All Images

Upload **all** images referenced in the blog post to WordPress — both the featured header image and any inline images in the markdown body.

#### 3a: Find All Local Images

Scan the HTML content (from Step 2) and the markdown body for local image references. These include:
- Relative paths like `images/{slug}/image-1.png` (from Google Doc imports)
- Paths like `blog-output/images/...`

Also check for the featured header image (auto-detected from `blog-output/images/header/header-{slug}.png` or provided as an argument).

#### 3b: Upload Each Image

For each local image, upload it to WordPress via the Media REST API and record the mapping from local path to WordPress URL.

Read `references/wp-upload-images.py`, write it to `/tmp/wp-upload-images.py`, replace `MARKDOWN_FILE` and `HEADER_IMAGE` with actual paths, then run it:

```bash
python3 /tmp/wp-upload-images.py
```

Results are saved to `/tmp/wp-image-results.json`. The HTML at `/tmp/wp-post-content.html` is updated with WordPress URLs.

### Step 4: Check for an Existing Post

Before creating a new post, search for an existing post with the same title to avoid duplicates. Only treat a post as a match if the title is **exactly** the same (case-insensitive comparison after stripping HTML entities):

Read `references/wp-check-post.py`, write it to `/tmp/wp-check-post.py`, replace `POST_TITLE_HERE` with the actual title, then run it:

```bash
python3 /tmp/wp-check-post.py
```

- If an **exact** title match is found, use its `post_id` to **update** the existing post in Step 5
- If no exact match is found (even if partial matches exist), **create** a new post in Step 5
- Tell the user whether you are creating or updating

### Step 5: Generate and Resolve Tags

Analyze the blog post content and choose **3 tags** that best describe the post's topic. Tags should be specific and useful for readers browsing by topic (e.g., "API Testing", "OAuth 2.0", "CI/CD" — not generic ones like "Postman" or "Development").

Use the `primary_keyword` and `secondary_keywords` from the frontmatter as a starting point, but adjust based on the actual content.

For each tag, check if it already exists in WordPress. If it does, use the existing tag ID. If not, create it.

Read `references/wp-manage-tags.py`, write it to `/tmp/wp-manage-tags.py`, replace `TAG_NAMES` with 3 tags chosen from the post content, then run it:

```bash
python3 /tmp/wp-manage-tags.py
```

Save the printed tag IDs for use in Step 6.

### Step 6: Create or Update the Post

Read `references/wp-stage-post.py`, write it to `/tmp/wp-stage-post.py`, then fill in `POST_TITLE`, `META_DESCRIPTION_HERE`, `FOCUS_KEYPHRASE_HERE`, `TAG_IDS`, and `POST_ID` (from previous steps), and run it:

```bash
python3 /tmp/wp-stage-post.py
```

### Step 7: Write WordPress Post ID Back to Markdown

After a successful create or update, write the WordPress post ID into the markdown file's YAML frontmatter as `wordpress_id`. This links the local file to the WordPress post for future updates.

- If `wordpress_id` already exists in the frontmatter, update it with the new value
- If it does not exist, add it after the last frontmatter field (before the closing `---`)

Use the Edit tool to add or update the `wordpress_id` field in the frontmatter. For example, if the frontmatter is:

```yaml
---
suggested_title: "Testing OAuth 2.0 Flows in Postman"
meta_description: "Learn how to test OAuth 2.0 authorization flows..."
---
```

It should become:

```yaml
---
suggested_title: "Testing OAuth 2.0 Flows in Postman"
meta_description: "Learn how to test OAuth 2.0 authorization flows..."
wordpress_id: 12345
---
```

Additionally, when checking for existing posts in Step 4, if the markdown file already contains a `wordpress_id` in its frontmatter, use that ID to fetch the post directly instead of searching by title. This is the most reliable way to match a local file to its WordPress post.

### Step 8: Present Results

This skill only saves the post as a **draft**. It does NOT schedule or suggest publish dates — that is the `blog-wordpress-scheduler` skill's job, and scheduling only happens after a human reviews the draft.

Summarize the result to the user:

1. **Post status** — created or updated, with the WordPress post ID
2. **Edit link** — direct link to edit the post in wp-admin: `https://blog.postman.com/wp-admin/post.php?post={id}&action=edit`
3. **Featured image** — whether it was uploaded and attached (include the image URL)
4. **Meta description** — the meta description that was set
5. **Next step** — remind the user to review the draft in wp-admin, then run `blog-wordpress-scheduler` when ready to schedule

Example output format:

```
WordPress post staged as draft.

  Post:           "Testing OAuth 2.0 Flows in Postman" (draft)
  Post ID:        12345
  Edit:           https://blog.postman.com/wp-admin/post.php?post=12345&action=edit
  Featured image: Uploaded (header-testing-oauth-flows.png)
  Meta desc:      "Learn how to test OAuth 2.0 authorization flows..."

Next step: Review the draft in wp-admin, then run /blog-wordpress-scheduler to pick a publish date.
```

## Error Handling

- **Authentication failure (401/403):** Tell the user their credentials may be invalid or expired. Suggest regenerating the application password.
- **Post not found on update (404):** Fall back to creating a new post.
- **Image upload failure:** Stage the post without a featured image and tell the user the image upload failed with the error message. They can upload manually via wp-admin.
- **Network timeout:** Retry once. If it fails again, show the error and suggest the user check their network connection or VPN.
- **Missing Yoast SEO plugin:** If the meta fields are rejected, warn the user that Yoast SEO may not be installed. The post will still be created but without SEO metadata.

## Important Guidelines

- **Always create posts as drafts** — never publish or schedule directly. The user must review the draft first.
- **Never suggest or set publish dates** — that is the `blog-wordpress-scheduler` skill's responsibility, and only after human review.
- **Only modify the markdown source file to write back `wordpress_id`** — do not change any other content in the file.
- **Preserve all formatting** — code blocks, tables, lists, and headings must render correctly in WordPress.
- **Check for duplicates first** — always search for an existing post before creating a new one to avoid duplicate content.
- **Read HTML from temp file** — never embed HTML content inline in the post creation script. Always read from `/tmp/wp-post-content.html`.
