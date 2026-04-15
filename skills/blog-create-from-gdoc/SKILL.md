---
name: blog-create-from-gdoc
description: "Convert a Google Doc to a blog-ready markdown file with images. Takes a Google Docs URL, exports the content as markdown, downloads embedded images, and saves everything to blog-output/."
argument-hint: "[Google Docs URL] (e.g. 'https://docs.google.com/document/d/1abc.../edit')"
---

# Blog from Google Doc

Convert a Google Doc into a blog-ready markdown file with downloaded images, saved to `blog-output/`.

## Input Handling

This skill accepts a Google Docs URL:

- **A Google Docs URL** (e.g., `https://docs.google.com/document/d/1abc.../edit`) — fetch and convert
- **No argument** — ask the user for the URL

The URL can be in any format (edit link, published link, share link). The skill extracts the document ID from it.

## Prerequisites

The Google Doc must be accessible — either publicly shared ("Anyone with the link can view") or shared with the user's Google account. If the doc is private, tell the user to update sharing settings.

## Workflow

### Step 1: Extract the Document ID

Parse the Google Docs URL to extract the document ID. The ID is the long string between `/d/` and the next `/` in the URL.

```python
import re

url = "GOOGLE_DOCS_URL_HERE"

# Extract document ID from various Google Docs URL formats
match = re.search(r'/document/d/([a-zA-Z0-9_-]+)', url)
if not match:
    raise ValueError(f"Could not extract document ID from URL: {url}")
doc_id = match.group(1)
print(f"Document ID: {doc_id}")
```

### Step 2: Fetch the Document Title

Use the Google Docs export URL to fetch the document as HTML first, then extract the title:

```python
import urllib.request

# Fetch as HTML to get the title
html_url = f"https://docs.google.com/document/d/{doc_id}/export?format=html"
req = urllib.request.Request(html_url, headers={"User-Agent": "PostmanDevRelSkill/1.0"})
html_content = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

# Extract title from <title> tag
title_match = re.search(r'<title>(.*?)</title>', html_content)
doc_title = title_match.group(1).strip() if title_match else "untitled"
print(f"Document title: {doc_title}")

# Create a slug from the title
slug = re.sub(r'[^\w\s-]', '', doc_title.lower().strip())
slug = re.sub(r'[\s_]+', '-', slug)
slug = re.sub(r'-+', '-', slug).strip('-')
print(f"Slug: {slug}")
```

### Step 3: Download Images from the Document

Parse the HTML to find all embedded images, download them, and save to `blog-output/images/{slug}/`:

```python
import os, urllib.request, hashlib

image_dir = f"blog-output/images/{slug}"
os.makedirs(image_dir, exist_ok=True)

# Find all image URLs in the HTML
img_pattern = re.compile(r'<img[^>]+src="([^"]+)"', re.IGNORECASE)
img_urls = img_pattern.findall(html_content)

image_map = {}  # old URL → local path
for i, img_url in enumerate(img_urls, 1):
    try:
        # Google Docs images are served from googleusercontent.com
        if not img_url.startswith("http"):
            continue
        req = urllib.request.Request(img_url, headers={"User-Agent": "PostmanDevRelSkill/1.0"})
        img_data = urllib.request.urlopen(req, timeout=30).read()

        # Determine extension from content or default to png
        ext = "png"
        if img_url.endswith(".jpg") or img_url.endswith(".jpeg"):
            ext = "jpg"
        elif img_url.endswith(".gif"):
            ext = "gif"
        elif img_url.endswith(".svg"):
            ext = "svg"

        filename = f"image-{i}.{ext}"
        filepath = os.path.join(image_dir, filename)
        with open(filepath, "wb") as f:
            f.write(img_data)

        image_map[img_url] = f"images/{slug}/{filename}"
        print(f"Downloaded: {filename} ({len(img_data)} bytes)")
    except Exception as e:
        print(f"Failed to download image {i}: {e}")
```

### Step 4: Convert HTML to Markdown

Write and run a Python script to convert the HTML content to clean markdown:

```python
import subprocess, sys

# Install html2text if needed
subprocess.check_call([sys.executable, "-m", "pip", "install", "html2text", "-q"])

import html2text

h = html2text.HTML2Text()
h.body_width = 0  # Don't wrap lines
h.ignore_links = False
h.ignore_images = False
h.ignore_emphasis = False
h.protect_links = True
h.unicode_snob = True
h.skip_internal_links = True

markdown = h.handle(html_content)
```

### Step 5: Clean Up the Markdown

After conversion, clean up the markdown:

1. **Replace image URLs** — swap the Google-hosted image URLs with local paths from `image_map`
2. **Remove Google Docs artifacts** — strip empty links, tracking parameters, Google redirect wrappers
3. **Fix heading levels** — ensure the document starts with H1 and has proper hierarchy
4. **Clean up whitespace** — remove excessive blank lines (more than 2 consecutive)
5. **Add language identifiers** to code blocks that are missing them

```python
# Replace image URLs with local paths
for old_url, local_path in image_map.items():
    markdown = markdown.replace(old_url, local_path)

# Unwrap Google redirect links: https://www.google.com/url?q=REAL_URL&...
google_redirect = re.compile(r'https://www\.google\.com/url\?q=(.*?)&[^)]*')
markdown = google_redirect.sub(lambda m: urllib.parse.unquote(m.group(1)), markdown)

# Remove excessive blank lines
markdown = re.sub(r'\n{3,}', '\n\n', markdown)

# Strip Google Docs comment anchors and bookmark links
markdown = re.sub(r'\[([^\]]*)\]\(#[^)]*\)', r'\1', markdown)
```

### Step 6: Add Blog Frontmatter

Add YAML frontmatter at the top of the markdown file with metadata extracted from the document:

```yaml
---
suggested_title: "Title from the Google Doc"
meta_description: "Generated from the first paragraph — under 155 characters"
seo_score: 0
primary_keyword: ""
secondary_keywords: []
source_gdoc: "https://docs.google.com/document/d/{doc_id}/edit"
---
```

Set `seo_score` to 0 and leave keyword fields empty — the `blog-copyeditor` skill will fill these in during the copyedit pass.

Extract the `meta_description` from the first paragraph of the document body (under 155 characters, ending at a natural sentence boundary).

### Step 7: Save the Markdown File

Save the final markdown to `blog-output/{slug}.md`:

```python
output_path = f"blog-output/{slug}.md"
with open(output_path, "w") as f:
    f.write(markdown)
print(f"Saved: {output_path}")
```

### Step 8: Present Results

Summarize what was created:

```
Google Doc converted to markdown.

  Source:   https://docs.google.com/document/d/{doc_id}/edit
  Title:    "Document Title Here"
  Output:   blog-output/{slug}.md
  Images:   3 images saved to blog-output/images/{slug}/

Next steps:
  - Run /blog-copyeditor blog-output/{slug}.md to copyedit and add SEO metadata
  - Run /blog-header-image blog-output/{slug}.md to generate a header image
  - Run /blog-wordpress-stage blog-output/{slug}.md to stage to WordPress
```

## Error Handling

- **Invalid URL:** If the URL doesn't contain a Google Docs document ID, tell the user and show the expected format.
- **Access denied (403):** The document is private. Tell the user to change sharing to "Anyone with the link can view".
- **Document not found (404):** The document ID is invalid or the doc was deleted.
- **Image download failure:** Continue with the conversion — note which images failed and use the original URL as a placeholder in the markdown.
- **html2text not available:** Fall back to a basic regex-based HTML-to-markdown conversion (strip tags, convert `<h1>` to `#`, `<p>` to paragraphs, etc.).

## Important Guidelines

- **Do not modify the Google Doc** — this skill only reads from it.
- **Preserve all content** — tables, lists, code blocks, links, and formatting should survive the conversion.
- **Download all images locally** — don't leave references to Google-hosted URLs, as they expire.
- **Use the document title as the filename** — slugified, lowercase, hyphenated.
- **Add frontmatter with empty SEO fields** — the copyeditor skill fills these in later.
- **Unwrap Google redirect URLs** — Google Docs wraps all links in `google.com/url?q=` redirects. Always unwrap to the original URL.
