# October 2026 LinkedIn Newsletter — staging checklist

1. Open `newsletter-body.html` in a browser, select all, copy.
2. Start a new LinkedIn Newsletter edition.
3. Set the **title** to: `Fabric Gateway is GA — and your agents just got a boss.`
4. Upload `cover-graphic.png` as the **cover image**.
5. Paste the copied content into the body. Confirm:
   - Headings rendered as real LinkedIn headings (not flattened to plain bold paragraphs).
   - The webinar callout shows its full text (title, date, description, Register Now) as plain paragraphs — there's no blockquote anymore.
   - Every link is still a live, clickable link with its UTM intact (not a flattened plain-text URL).

## Images — one per section/callout, directly under its tagline or label

Each placeholder in the pasted text is plain text, not a real image — delete it and upload the matching file in its place. Events and the hero have no usable image source this cycle (Events has no comparable source; the hero's own blog post has no in-body images), so they're text-only, on purpose. The webinar always gets an image, every cycle — this month it's the real "Code Brew" promo graphic you supplied, cropped to the standard frame.

| Placeholder text | Upload this file | Where | What it shows |
|---|---|---|---|
| `[IMAGE: webinar-promo.png]` | `webinar-promo.png` | Sub-hero, under "THIS MONTH'S WEBINAR" | The webinar's own promo graphic (Code Brew / "How to Govern AI Agents in Production using Agent Gateways," speaker Gbadebo Bello) — human-supplied, cropped to the standard frame |
| `[IMAGE: badge-intro-to-astro.png]` | `badge-intro-to-astro.png` | Liftoff, under the tagline | Liftoff module badge for "Introduction to Astropods" (this cycle's featured module), centered on a blurred brand-color swirl card |
| `[IMAGE: thumb-govern-mcp-servers-scale.png]` | `thumb-govern-mcp-servers-scale.png` | YouTube, under the tagline | Thumbnail for "How to Govern MCP Servers at Scale with Postman Fabric Gateway" (most on-theme video this cycle), cropped to fill the frame — no swirl, it's a real photo |
| `[IMAGE: update-credential-sprawl-passport.png]` | `update-credential-sprawl-passport.png` | Product Updates, under the tagline | In-article screenshot of Passport's approval-requests UI — most representative Product Updates image this cycle |

All 4 images are 1200×675 (fixed an earlier blurriness issue — they were 400×225 and getting upscaled by the browser) with rounded top corners / square bottom corners baked in — no further editing needed.

## Video embed — separate manual step

Click the media/embed icon in the Newsletter editor's compose UI, paste the URL, click Add:

- **How to Govern MCP Servers at Scale with Postman Fabric Gateway** — `https://www.youtube.com/watch?v=DIZNHi7TqO0`

(The other 4 videos this cycle are plain text links with no thumbnail — only the section's one chosen image above gets the visual treatment. They don't need an embed step either; a plain link is all they have.)

## Final step

Review the full draft once, then publish when ready. This skill never publishes on its own — that's always a manual action.
