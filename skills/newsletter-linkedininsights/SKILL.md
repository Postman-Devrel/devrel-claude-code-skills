---
name: newsletter-linkedininsights
description: "Monthly Postman Developer Digest for LinkedIn's Newsletter feature, themed around the month's webinar. Leads with the webinar, adds a small YouTube section and up to 3 related blog items, formatted in a Techpresso / The Rundown style (digest preview, bulleted stories, 'Why it matters'). Outputs a paste-ready HTML draft, cover graphic, and staging checklist. Triggers: \"run the dev digest\", \"draft newsletter\", \"finalize digest\", scheduled 15th/20th runs."
argument-hint: "[webinar Luma URL] (optional — if omitted, the skill finds the in-window webinar itself)"
allowed-tools: ["WebFetch", "Read", "Write", "Bash"]
---

# Postman Developer Digest — monthly LinkedIn newsletter

**Goal: engagement and click-through.** Every edition is built around one theme, the month's webinar, and everything else is chosen because it relates to that theme. Style is modeled on [Techpresso](https://techpresso.co/archives/techpresso-20261107-7) (scannable digest preview, hook-first headlines, short punchy bullets) and [The Rundown](https://www.therundown.ai/articles/apple-big-week-begins-with-ipad-mini) (each story = one-line "Rundown", bulleted "details", "Why it matters").

## Edition shape (fixed order, every run)

1. **Webinar (lead and theme)** — the one thing readers should act on
2. **YouTube** — small section, up to 3 videos related to the theme
3. **Blog items** — **at most 3** posts related to the theme. Fewer is fine; never pad. Never add other sections.

No Events, Liftoff, or Product Updates sections. Conferences, meetups, and Liftoff are out unless one is itself the best related item (a Liftoff module may appear only as one of the 3 items, and only if it directly relates to the webinar). `liftoff-state.json` is no longer read or written.

## Sources

### 1. Webinar (the theme)

Source: the Luma API (same auth as `qbr-metrics`: `LUMA_API_KEY` env var, header `x-luma-api-key`, base `https://public-api.luma.com`; see `skills/qbr-metrics/references/pull-luma.py`). **Forward-looking, hard 45-day cutoff** (an event at day 46+ waits for next cycle). List events with `GET /v1/calendars/events/list?after=…&before=…&pagination_limit=50` and pick the in-window **webinar** (not meetups or conferences). If several, take the soonest and mention the others to the human. Check the key by name only, never print it; if it is missing, fall back to the public page `https://luma.com/postman-dev-events`.

- **The API is the source of truth for date and time.** `start_at`/`end_at` are UTC; convert with the event's `timezone` (e.g. `2026-11-17T18:00:00.000Z` + `America/Los_Angeles` = 10:00 AM PT). Event URL slugs can be stale after a reschedule (`/november-26-webinar` was really Nov 17), and a plain fetch of the event page or an LLM summary of it can show the wrong date, so never take the date from a slug or a summary.
- **Registration link is the webinar's Luma event page** (the `url` field from the API), tagged with UTM. No LinkedIn Event URL is needed. If the event has `waitlist_enabled` and is full, the CTA is "Join Waitlist" instead.
- **Promo image comes from the API too:** the event's `cover_url`. Download it, view it, and confirm it is a real promo graphic (title, speakers, date). If it is square or otherwise not 16:9, cover-crop to 1200x675 *positioned so the title, speakers, and date stay visible* (check the output by eye; a plain center crop can cut off the date line). If the cover is a bare photo with no promo text, or missing, ask the human for the promo image. Never generate a substitute.
- **No webinar in-window:** stop and ask the human for this cycle's theme (a topic or launch plus its URL or description). Use it exactly as the webinar copy would be used below, and skip the webinar block rather than faking one.

**The webinar's own copy is the source for the title, the theme, and the content search. Always.** Get the full copy (title, description, learning objectives, speakers, format) from the event page or the API's event-get endpoint (`GET /v1/event/get?id={event_id}`), and reuse its exact phrases wherever they hold up: the title options, the "What you'll walk away with" bullets (one per learning objective, in the webinar's own words, tightened), and the keywords. Do not invent a theme from outside the webinar copy.

Frame the theme as **where Postman fits in the reader's agentic coding tools** (the plugin and skills inside the agent they already use), then ground it in this webinar's specifics. From the copy, write a short **theme statement** and **5-8 keywords** (product names, protocols, concepts, and the nouns from the learning objectives, e.g. "agentic SDLC", "Claude Code", "dependencies", "mocks", "CI", "monitoring"). Everything downstream (the three title options, the blog search, the video search, the "Why it matters" lines) is derived from this theme and keyword list, and the draft notification states which keywords were used.

### 2. Related blog items (max 3)

Search for posts related to the webinar theme and keywords (from the webinar copy, above), in both blogs:
- Postman: `https://blog.postman.com/wp-json/wp/v2/posts?search={keyword}&per_page=10&_fields=id,date,link,title,excerpt` (one query per top keyword; dedupe)
- Astropods: `https://blog.astropods.com/` (read the listing and match by title/excerpt)

Rank by **relevance first, recency second**. Prefer the last 90 days; allow older evergreen posts only when they are clearly the best fit. Prefer a mix (e.g. one concept post, one hands-on, one product update) over three near-duplicates. Never include unpublished posts. For each pick, fetch the post to write real copy and to find an in-body image (screenshot or diagram, never the header/`og:image` banner; skip if none).

### 3. YouTube (small section)

Source: `https://www.youtube.com/@postman/videos`, RSS at `https://www.youtube.com/feeds/videos.xml?channel_id=UCocudCGVb3MmhWQ1aoIgUQw`.

Pick **up to 3** videos related to the webinar theme and keywords (match on video titles and descriptions), most relevant first (recent preferred, older allowed if clearly on-theme). If nothing relates, show the single most recent video or omit the section; never pad. The `/videos` page and RSS are JS-rendered and can come back empty to a plain fetch, so try a real browser render before declaring a source unreachable. Relative ages are a drafting check only; never print them.

## Copy: engagement rules

- **Hook first.** Every headline states the payoff or the tension, not the topic. Not "Webinar on MCP testing" but "Your agents pass the demo. Here is why they fail in prod."
- **Short.** Bullets are 1–2 lines. Rundown lines are 1–2 sentences. Lead each bullet with a bolded key phrase.
- **Specific.** Numbers, product names, and concrete outcomes beat adjectives. Never invent a stat; use only what the source says.
- **Second person, conversational**, third person for shipped features ("we've shipped"). No marketing words: "supercharge", "unlock", "revolutionize", "leverage", "game-changer".
- **One CTA per block**, clear verb, bold link text. Webinar CTA appears **twice** (top and sign-off). Blog and video CTAs name the thing ("Read the post", "Watch the demo"), never "click here".
- **Emoji:** one emoji at the start of each `<h2>`/`<h3>` headline, and in the digest preview, as in the reference newsletters. Pick meaningful ones, no strings of emoji, none inside body sentences. (This reverses the old no-emoji rule on purpose.)
- **Reader prompt in the sign-off.** End with one question tied to the theme that invites a comment (LinkedIn ranks comments), e.g. "What is the hardest part of testing agents today? Tell us in the comments."

## Edition title (review gate)

After the theme is set from the webinar copy and **before pulling blog or video content or drafting anything else**, write **three distinct title options**, each built from the webinar copy's own language (its title, description, or learning objectives) rather than invented phrasing, (a hook, not a description; each structured differently; confident, dev-focused, a little wry, no exclamation marks). Present all three; the human picks, requests a revision, or supplies their own. Do not continue until one is approved.

The approved title is used verbatim in three places: the body `<h1>`, `{{HEADLINE}}` on the cover graphic, and the suggested LinkedIn Newsletter edition title (call this out in the draft notification, since the human pastes it in).

Also write one `{{HERO_BADGE}}` phrase, used verbatim as the bold line under the h1 and on the cover. **It is the subtitle: a hook about the newsletter's theme that continues the title.** It is not a label, a webinar promo or date, a list of what the edition contains, or a restatement of the webinar's workflow steps. The standing theme is where Postman sits in the reader's agentic coding toolchain (the plugin and skills inside the coding agent they already use), so state the cycle's version of that, grounded in the webinar copy and the picked content (e.g. title "The agentic SDLC fits in one terminal" + badge "POSTMAN, BUILT INTO THE CODING AGENT YOU ALREADY USE"). Uppercase, under about 60 characters so it fits the pill on one line. Only claim what the webinar copy and sources support. The webinar date and counts live in the body, not the badge.

## UTM tagging — non-negotiable

Every outbound link goes through `references/add_utm.py` before the draft is done. Never hand-write a UTM string.

- `utm_source=linkedin`, `utm_medium=social`
- `utm_campaign=dev-digest-{YYYY}-{MM}` (the month the digest covers)
- `utm_content`: `webinar` (top webinar CTA), `webinar-footer` (sign-off CTA), `blog` (blog items), `youtube` (videos). Both webinar CTAs point to the Luma event URL.

```bash
python3 references/add_utm.py "https://blog.postman.com/example/" "2026-11" "blog"
```

Some destinations (youtube.com, postman.com/liftoff) strip the UTM from the visible address bar after load via client-side routing. That is not a tagging bug; reproduce the click before re-tagging anything.

## Output

Save to `newsletter-output/linkedin-insights/{YYYY-MM}/` (create as needed; never loose in the parent). Local only, never Google Drive or other cloud storage. Five artifacts:

### 1. newsletter-body.html

LinkedIn's Newsletter editor keeps only a safe subset on paste and strips everything else. Use **only**: `<h1>` `<h2>` `<h3>`, `<strong>`, `<em>`, `<ul>`/`<ol>`/`<li>`, `<a href>`, `<hr>`, `<p>`. No `style` attribute, no `<style>` block, no `<blockquote>` (retired after repeated paste failures: it drops children and strips `<br>`), no inline `<img>` (images are native uploads marked by placeholders), no tables. **Never type a literal em/en dash**; write `&mdash;` / `&ndash;`. Emoji are literal characters, so include `<meta charset="utf-8">` at the top of the file.

Structure, in this order:

```html
<meta charset="utf-8">
<h1>{approved title}</h1>
<p><strong>{HERO_BADGE}</strong></p>
<p>{Opener: 1–2 sentences, conversational, names the theme and why it matters this month. Starts with a greeting or a hook, never "This month we're featuring".}</p>

<p><strong>IN THIS DIGEST</strong></p>
<ul>
  <li>{emoji} {webinar hook, 6–10 words}</li>
  <li>{emoji} {blog item 1 hook}</li>
  <li>{emoji} {blog item 2 hook}</li>
  <li>{emoji} {blog item 3 hook}</li>
  <li>{emoji} {video hook}</li>
</ul>
<hr>

<h2>{emoji} {webinar hook headline}</h2>
<p>[IMAGE: webinar-promo.png]</p>
<p><strong>The Rundown:</strong> {1–2 sentences: what it is and the payoff.}</p>
<p><strong>{Day, Month Date}</strong> &middot; {time and timezone}</p>
<p><strong>What you'll walk away with:</strong></p>
<ul>
  <li><strong>{key phrase}:</strong> {1 line}</li>
  <li>... (3–5 bullets)</li>
</ul>
<p><strong>Why it matters:</strong> {2 sentences max, tie to a real developer pain.}</p>
<p><strong><a href="{UTM'd Luma event URL, webinar}">Save your spot &rarr; Register Now</a></strong></p>
<hr>

<h2>{emoji} Related reading</h2>   <!-- skip the whole section if no related posts -->

<h3>{emoji} {hook headline for post 1}</h3>
<p>[IMAGE: blog-1.png]</p>   <!-- only if a real in-body image exists -->
<p><strong>The Rundown:</strong> {1–2 sentences.}</p>
<p><strong>The details:</strong></p>
<ul>
  <li><strong>{key phrase}:</strong> {1 line}</li>
  <li>... (3–4 bullets)</li>
</ul>
<p><strong>Why it matters:</strong> {1–2 sentences, ties back to the webinar theme.}</p>
<p><strong><a href="{UTM'd URL, blog}">Read the post</a></strong></p>

<hr>   <!-- always a divider between each blog item -->
... posts 2 and 3 in the same shape, each preceded by an <hr> (max 3 total) ...
<hr>

<h2>{emoji} Watch</h2>
<p>[IMAGE: youtube-thumb.png]</p>   <!-- one image for the whole section -->
<ul>
  <li><strong>{video title}</strong> &mdash; {one-line hook}. <a href="{UTM'd URL, youtube}">Watch</a></li>
  ... (up to 3)
</ul>
<hr>

<p>{Sign-off: 1–2 sentences, then the reader question.}</p>
<p><strong><a href="{UTM'd Luma event URL, webinar-footer}">Register Now</a></strong></p>
<p><em>postman developer digest</em></p>
```

Rules for the body:
- The **digest preview bullets** must match, in order and in spirit, the headlines below them; no emoji reuse across bullets.
- Registration-type CTA labels are **"Register Now"**, never a platform name (never "Register on Luma"/"LinkedIn"); a full event uses **"Join Waitlist"**.
- Links always use readable anchor text, never bare URLs.
- "Why it matters" and "The details" use bold lead-ins exactly as shown, so they scan like the references. Do not add new section labels per cycle.
- No relative ages, no "(new)/(updated)/(featured)" tags, no explanations of how items were chosen.
- If an in-body image is missing for a post, omit that placeholder; never fall back to the header banner.

### 2. cover-graphic.png

Fill `references/cover-template.html` (only tokens change, never layout, type, or color) and render to a **1200×627** PNG of the `.canvas` element (headless Chrome or similar). If no renderer is available, save the filled HTML and flag that the PNG export is manual this month.

- `{{MONTH_LABEL}}` e.g. `November 2026`
- `{{SEASON}}` lowercase, deterministic Northern hemisphere lookup (Dec/Jan/Feb winter, Mar/Apr/May spring, Jun/Jul/Aug summer, Sep/Oct/Nov autumn); never ask the human
- `{{HEADLINE}}` the approved title verbatim, wrapped in the template's `<h1>`, with exactly **one** word or short phrase in `<span style="color:#FF6C37;">` (the word carrying the news, never a connecting word). No forced `<br>`.
- `{{HERO_BADGE}}` the same phrase as the body, as `<div class="hero-badge">…</div>`. Never leave the literal token visible.

The body `<h1>` is plain text (color cannot survive paste); only the cover gets the highlight.

### 3. Images (native upload files, plain-text placeholders in the body)

Every image is uploaded through LinkedIn's image button and marked in the body by `<p>[IMAGE: {filename}]</p>`. Placeholders and files must be in **exact 1:1 correspondence**: never a placeholder without a saved file, never a file without a placeholder.

Images this edition: `webinar-promo.png` (from the Luma API `cover_url`), `blog-N.png` (one per related post, only when a real in-body image exists), `youtube-thumb.png` (one for the whole YouTube section, from the video most relevant to the theme).

Processing for all of them (Pillow):
- **Frame 1200×675.** Smaller frames came out blurry in LinkedIn's wide column. Use the highest-resolution source: YouTube `maxresdefault.jpg` when real (HEAD check; under a few KB means missing, fall back to `hqdefault.jpg`), a blog image's full native file rather than a `-{w}x{h}` thumbnail.
- **Cover-crop** to fill the frame (scale the shorter side to fit, center-crop the overflow). No padding, no generated backgrounds, no swirl cards.
- **Rounded top corners, square bottom corners, baked into the pixels** (`rounded_rectangle(..., corners=(True, True, False, False))` alpha mask, radius 48px). CSS cannot do this since it gets stripped. Save as **PNG** for real transparency.
- Never use a header/`og:image` banner or a "related articles" thumbnail from the page bottom.

### 4. staging-checklist.md

The exact manual runbook, every line naming a specific file or URL:
1. Open `newsletter-body.html` in a browser, select all, copy.
2. Start a new LinkedIn Newsletter edition; set its title to the approved title; upload `cover-graphic.png` as the cover.
3. Paste the body. Confirm headings rendered as real headings (not flattened bold), emoji rendered, bullets are real lists, and every link is clickable with its UTM intact (not flattened to plain text).
4. A lookup table, one row per `[IMAGE: …]` placeholder, mapping exact placeholder text to exact file and position.
5. For each YouTube video, one line: click the media/embed icon, paste this exact URL, click Add (the thumbnail is a static image, not a player; the embed is a separate manual step).
6. Review once, then publish when ready. This skill never publishes.

### 5. The draft notification (chat message, not a file)

Names the suggested edition title, the webinar, and the keywords used to find content, lists which blog posts and videos were picked and why they relate (one line each), flags anything skipped (no in-body image, no webinar, renderer missing), and points to `staging-checklist.md` instead of re-explaining the steps.

## Run order

1. Find the in-window webinar via the Luma API. Pull the date, time, URL, cover image, and full copy from the Luma API. Ask the human only if something is missing (no webinar in-window, or no usable promo image).
2. Extract the theme and keywords from the webinar copy. Write three title options from that copy. **Wait for approval.**
3. Pull related blog posts and videos; select max 3 posts and up to 3 videos.
4. Draft the body, run every link through `add_utm.py`, build images, fill and render the cover, write the checklist.
5. Report in the draft notification.

## What this skill must never do

- Never place two blog items back to back without an `<hr>` divider between them. Every related-reading post is separated from the next by a horizontal rule, every run.
- Never exceed **3 blog items**, add a fourth section (Events, Liftoff, Product Updates), or pad with unrelated posts to reach a count.
- Never pick content that does not relate to the webinar theme just because it is recent.
- Never skip the title review gate: three real, distinct options and one approved before any source pulling or drafting.
- Never use `<blockquote>`, `<img>`, tables, a `style` attribute, or a `<style>` block in `newsletter-body.html`.
- Never type a literal em dash or en dash into the body; always `&mdash;` / `&ndash;`.
- Never open with a mechanical disclaimer ("This month we're featuring…") or write topic-label headlines instead of hooks.
- Never invent statistics, quotes, or product claims; use only what the source says. No customer names in product-update copy.
- Never name the platform in a CTA label. The registration href is the webinar's Luma event URL.
- Never take a webinar's date from a URL slug, a page summary, or memory; use the Luma API `start_at` and `timezone`.
- Never invent a theme, title, or keyword list that is not grounded in the webinar copy, and never search for related content before the title is approved.
- Never generate or fake the webinar's promo image; use the Luma `cover_url`, ask the human if it is unusable, and skip it if they have none. Never ship a crop that cuts off the date.
- Never report a date as unconfirmed, or a JS-rendered source as empty, from a plain fetch alone.
- Never skip the UTM script, or reuse a `utm_content` slug across different roles (webinar top vs. footer, blog, youtube).
- Never leave `{{HERO_BADGE}}` or any `{{TOKEN}}` visible in the rendered cover, and never write a second, different headline for the cover.
- Never highlight more than one word or phrase in the cover headline.
- Never use a header/`og:image` banner as an in-body image.
- Never skip baking rounded-top/square-bottom corners into every image, or generate at a size smaller than 1200×675.
- Never skip `staging-checklist.md`, never let it go generic, and never duplicate its steps in the notification.
- Never publish, post, or schedule the LinkedIn newsletter. This skill ends at a reviewed-ready package.
- Never write output to Google Drive or any cloud storage.
- Never carry over last month's content; if a source has nothing relevant, say so plainly instead of padding.
