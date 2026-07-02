---
name: meetup-calendar
description: "Summarize, sync, or update-stats the internal Postman meetup and user group calendar spreadsheet. Use to view upcoming events, link Luma URLs, or write back registration and attendance figures."
argument-hint: "[filter | --sync [luma-url] [--dry-run] | --update-stats] — filter: 'upcoming', 'past', 'YYYY', or city. --sync matches Luma events to the sheet. --update-stats fetches registration/attendance numbers."
allowed-tools: ["Bash", "Read", "Write"]
---

# Meetup Calendar Summary

Read the Postman internal meetup and user group calendar from Google Sheets and produce a summary of events grouped by upcoming vs. past and by region.

---

## Configuration

This skill reads a private Google Sheet using the Sheets API v4, authenticated via a Google Cloud service account key. This avoids OAuth browser flows and works reliably for automated/skill use.

### One-time setup

1. **Enable the Sheets API** in [Google Cloud Console](https://console.cloud.google.com):
   APIs & Services → Enable APIs → search "Google Sheets API" → Enable

2. **Create a service account:**
   IAM & Admin → Service Accounts → Create Service Account (any name, no IAM roles needed)

3. **Download the JSON key:**
   Click the service account → Keys tab → Add Key → Create new key → JSON → Save the file somewhere safe (e.g. `~/.config/gcloud/postman-sheets-sa.json`)

4. **Share the spreadsheet** with the service account's email address (shown in the console, looks like `name@project-id.iam.gserviceaccount.com`). Grant it **Editor** access for read/write.

5. **Add to `.claude/settings.json`:**
   ```json
   {
     "env": {
       "MEETUP_SHEET_ID": "1vu5Nr_xP0-fBj9zJITb5xhC5iTKpPMkI3H9uMFaHNEI",
       "GOOGLE_APPLICATION_CREDENTIALS": "/Users/you/.config/gcloud/postman-sheets-sa.json"
     }
   }
   ```

---

## Process

### Step 1: Verify prerequisites

Check that the required env vars are set:

```bash
echo "SHEET_ID: $MEETUP_SHEET_ID" && echo "CREDS: $GOOGLE_APPLICATION_CREDENTIALS"
```

If `MEETUP_SHEET_ID` is empty, stop and tell the user to add it to `.claude/settings.json`.
If `GOOGLE_APPLICATION_CREDENTIALS` is empty or the file does not exist, stop and show the setup instructions above.

### Step 2: Get a fresh access token

Read `references/get-google-token.py`, write it to `/tmp/get-google-token.py`, and run it:

```bash
python3 /tmp/get-google-token.py
```

Capture the token output (a `ya29...` string). If the script errors with a file-not-found, the `GOOGLE_APPLICATION_CREDENTIALS` path is wrong. If it errors with an HTTP 401, the service account key may be revoked — regenerate it in Google Cloud Console.

### Step 3: Fetch spreadsheet metadata

Use the token to discover all tabs in the spreadsheet:

```bash
curl -s \
  -H "Authorization: Bearer TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/$MEETUP_SHEET_ID?fields=sheets.properties"
```

Parse the response to find the sheet named exactly `Meetups & User Group Cal`. Extract its `sheetId`. If no tab with that name exists, list the available tab names and ask the user which one to use.

### Step 4: Fetch the tab data

Use `includeGridData=true` to fetch both cell values and formatting (needed to detect strikethrough rows):

```bash
curl -s \
  -H "Authorization: Bearer TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/$MEETUP_SHEET_ID?includeGridData=true&ranges=Meetups%20%26%20User%20Group%20Cal!A28:ZZ"
```

The response is a `sheets[].data[].rowData[]` structure. Each row has a `values[]` array where each cell has:
- `userEnteredValue.stringValue` — the cell text
- `userEnteredFormat.textFormat.strikethrough` — `true` if the cell has strikethrough formatting

Row 28 of the sheet (the first rowData entry) contains the headers.

### Step 5: Write and run the parse script

Read `references/meetup-parse.py`, write it to `/tmp/meetup-parse.py`, then pipe the curl response into it:

```bash
curl -s \
  -H "Authorization: Bearer TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/$MEETUP_SHEET_ID?includeGridData=true&ranges=Meetups%20%26%20User%20Group%20Cal!A28:ZZ" \
  | python3 /tmp/meetup-parse.py
```

Capture the JSON output.

---

### Step 6: Apply optional filter

If the user passed a filter argument:
- `upcoming` — show only upcoming events
- `past` — show only past events (this year + prior years)
- `YYYY` (e.g. `2026`) — show only events from that year
- A city/country name (e.g. `London`) — show only events where city or country contains that string (case-insensitive)

Apply filtering to the JSON output before rendering.

---

### Step 7: Render the report

Produce a clean markdown report and display it in the chat.

#### Upcoming Events

```
## Upcoming Meetups & User Group Events

| Date | Event | Location | Type | Organizer |
|------|-------|----------|------|-----------|
| 15 Jul 2026 | NYC API Meetup | New York, US | In-person | Jane Smith |
| 22 Aug 2026 | London User Group | London, UK | Hybrid | Tom Lee |
```

#### Past Events (This Year)

```
## Past Events — 2026

| Date | Event | Location | Type |
|------|-------|----------|------|
| 10 Jun 2026 | SF API Meetup | San Francisco, US | In-person |
```

#### Regional Summary

```
## By Region

| Region | Events |
|--------|--------|
| New York, US | 4 |
| London, UK | 3 |
| San Francisco, US | 2 |
```

Formatting rules:
- Sort upcoming events ascending by date, past events descending
- If `url` is present, make the event name a markdown link: `[name](url)`
- If `status` is present and not empty, append it in italics after the event name: `[Name](url) _Draft_`
- Show `—` for any empty cell
- If `unparsed_date` events exist, add a note at the bottom: `⚠ N events had unrecognizable date formats and were excluded`
- If the col_map shows any key mapped to `null`, add a note listing which columns were not found in the sheet

---

### Step 8: Save the report

Save the full report to `meetup-output/`. Create the directory if it doesn't exist.

Filename pattern: `meetup-output/meetup-calendar-YYMMDD.md` where YYMMDD is today's date.

Append at the bottom of the file:
```markdown
---
*Generated: {today's date} | Sheet: Meetups & User Group Cal*
*Filter: {filter or 'none'}*
```

---

---

## `--sync` Mode

When the argument is `--sync`, skip the summary/filter flow and enter Luma sync mode. This matches Luma calendar events to spreadsheet rows by name and date, writes the Luma event URL into a `Luma Event URL` column, then offers to create Luma events for any unmatched spreadsheet rows.

### Parsing `--sync` arguments

| Argument | Description |
|----------|-------------|
| Luma calendar URL | Optional. A full URL like `https://luma.com/calendar/manage/cal-TGqTNpY4iyl7XYe/events`. The `cal-` ID is extracted automatically. Defaults to `LUMA_CALENDAR_ID` env var, then `cal-TGqTNpY4iyl7XYe`. |
| `--dry-run` | Preview matches without writing anything to the sheet. |

**Also verify `LUMA_API_KEY` is set** before proceeding (in addition to the standard Google prereqs from Steps 1–2).

---

### SYNC-1: Find or create the "Luma Event URL" column in row 28

Fetch the full tab with formatting (needed for strikethrough detection):

```bash
curl -s \
  -H "Authorization: Bearer $GTOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/$MEETUP_SHEET_ID?includeGridData=true&ranges=Meetups%20%26%20User%20Group%20Cal!A28:ZZ"
```

**Skip any row where ANY cell has `userEnteredFormat.textFormat.strikethrough == true`.** These rows are cancelled/removed events and must be excluded from matching and creation entirely.

**Also skip any row where the `Type` column (column E) does not equal `Meetup` (case-insensitive).** All other types (e.g. Conference, Workshop, Webinar) are ignored by this skill.

Look for a header matching `luma event url` or `luma url` (case-insensitive). If not found, note the next empty column index to append the header after writing starts.

Use this helper to convert a 0-based column index to a sheet letter:
```python
def col_letter(idx):
    result = ""
    while idx >= 0:
        result = chr(idx % 26 + ord('A')) + result
        idx = idx // 26 - 1
    return result
```

---

### SYNC-2: Fetch all Luma events

Use the same auth headers and pagination pattern as `luma-stats` (see `skills/luma-stats/SKILL.md`). Read `references/luma-fetch.py`, write it to `/tmp/luma-fetch.py`, then run it:

```bash
LUMA_EVENTS=$(python3 /tmp/luma-fetch.py "$CALENDAR_ID")
echo "$LUMA_EVENTS" > /tmp/luma-events.json
```

---

### SYNC-3: Match and write Luma URLs

Read `references/meetup-match.py`, write it to `/tmp/meetup-match.py`, and run it.

Build `/tmp/sheet-data.json` from the data gathered in Steps 3–4:
```json
{
  "rows": [{"name": "...", "date_raw": "...", "existing_luma_url": "", "sheet_row": 29}, ...],
  "luma_col_idx": 12
}
```

Run it: `python3 /tmp/meetup-match.py`

If `--dry-run`, display the match table and stop. Otherwise write the header (if new column) and all matched URLs via `batchUpdate`:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $GTOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "valueInputOption": "RAW",
    "data": [
      {"range": "Meetups & User Group Cal!X29", "values": [["https://lu.ma/..."]]},
      {"range": "Meetups & User Group Cal!X31", "values": [["https://lu.ma/..."]]}
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/$MEETUP_SHEET_ID/values:batchUpdate"
```

Display a summary after writing:

```
## --sync Results

**Matched & written:** N | **Already filled:** N | **Luma events unmatched in sheet:** N
```

---

### SYNC-4: Offer to create unmatched spreadsheet events in Luma

For each spreadsheet row with no Luma match and no existing URL, ask the user:

```
These spreadsheet events have no Luma event. Create them in Luma?

  Row 33 — Berlin User Group — 12 Sep 2026
  Row 35 — Tokyo Meetup — 20 Oct 2026

Reply with row numbers (e.g. "33 35"), "all", or "none".
```

For each confirmed creation:

1. **Fetch the template event** by slug and print the full raw JSON response:
   ```bash
   curl -s -H "x-luma-api-key: $LUMA_API_KEY" \
     -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36" \
     "https://api.lu.ma/public/v1/event/get?url=https://luma.com/june-SF-agents-API-meetup"
   ```

   The template returns the following confirmed field names — use these exactly:

   | Field | Value to carry over |
   |-------|-------------------|
   | `description` | Generic intro + legal text only — strip any speaker bios (those are SF-specific). Keep: the "Join us…" opener, the Discord/accessibility/legal footer. |
   | `description_md` | Same as above in markdown format |
   | `duration_interval` | `"P0Y0M0DT2H0M0S"` (2 hours) — use this to compute `end_at` from `start_at` |
   | `timezone` | Adapt to the target city's local timezone (e.g. `Europe/London`, `Europe/Berlin`). Do not copy SF's `America/Los_Angeles` |
   | `location_type` | `"offline"` — always, for every event |
   | `location_visibility` | `"public"` |
   | `waitlist_status` | `"enabled"` |
   | `feedback_email` | `{"enabled": true, "delay": "P0Y0M0DT0H45M0S"}` |
   | `registration_questions` | Pass as-is: `[{"label": "What company do you work for?", "required": true, "question_type": "text"}, {"label": "What is your job title?", "required": true, "question_type": "text"}]` |
   | `tags` | Pass tag `api_id` values for `agents`, `ai`, `api`, `developer` — omit `north-america` and any other region-specific tags |
   | `cover_url` | Fallback only if no city image found in step 2 |

   For `geo_address_json`, build from the spreadsheet row's location data:
   ```json
   {
     "city": "{city from sheet}",
     "country": "{country from sheet}",
     "region": "{state/region if available}",
     "city_state": "{city}, {region or country}",
     "full_address": "{venue name and address from sheet if available, otherwise just city, country}",
     "description": ""
   }
   ```

2. **Find a cover image for the city** — run these two checks in order:

   **2a. Look for a past Luma event from the same city.**
   Search the already-fetched Luma events (from SYNC-2) for events whose name contains the city name (case-insensitive) AND whose `start_at` is before today. Sort matches by `start_at` descending and take the **most recent** one (to ensure the latest image version is used). Extract its `cover_url`.

   If a match is found → use that `cover_url` for the new event. Log: `Using cover image from past event: {matched event name} ({date})`.

   **2b. If no past city event exists → generate a new image with Gemini.**

   Use the same Gemini API as `blog-header-image` (`gemini-3-pro-image-preview`, `GEMINI_API_KEY`) but with a meetup-specific prompt and square format.

   The reference images at `skills/meetup-calendar/meetup1.png` (Austin) and `skills/meetup-calendar/meetup2.png` (NYC) define the **visual style only** — use them to understand the color palette, gradient, layout proportions, and typography treatment. Do NOT describe their city skylines in the prompt and do NOT pass them as image inputs to Gemini. The Gemini prompt must describe ONLY the target city.

   The image must match this exact layout:
   - **Background**: deep purple-to-violet gradient — dark at the very top and bottom edges, vibrant mid-purple in the middle third
   - **Top**: Postman logo (orange filled circle with a white pen icon) on the left, "POSTMAN" in bold white sans-serif to its right — the pair is horizontally centered at the top
   - **Center**: the city name (e.g. `Berlin`) in very large, bold white sans-serif text, centered
   - **Lower third**: ONE single continuous solid black shape spanning the full width — a solid filled black ground base with the city's recognizable skyline rising from it. No gaps, no holes, no purple visible between or beneath buildings, bridge cables, arches, or any other element. Think of it as black paint filled from the bottom up to the tops of the landmarks.
   - **Footer**: a dark semi-transparent horizontal bar at the very bottom containing "Agents & APIs Meetup" in white text, centered

   Write `/tmp/generate-meetup-cover.py` and run it:

   ```python
   import json, base64, urllib.request, os

   API_KEY = os.environ.get("GEMINI_API_KEY")
   if not API_KEY:
       raise ValueError("GEMINI_API_KEY not set")
   MODEL = "gemini-3-pro-image-preview"
   URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

   CITY = "CITY_NAME_HERE"
   CITY_SLUG = "city-slug-here"

   prompt = f"""Square event poster for a {CITY} tech meetup. Match the EXACT style of meetup1.png (Austin) and meetup2.png (NYC).

BACKGROUND: Smooth deep purple gradient — near-black (#1a0a2e) at very top, bright vibrant violet (#8B30D0) in center. The gradient covers only the upper portion of the image. The bottom portion is the solid black silhouette base.

LAYOUT top to bottom:
1. Top 15%: Orange filled circle with white pen icon + "POSTMAN" in bold white uppercase, side by side on one line, centered.
2. Next 25%: "{CITY}" in very large bold white, title case, centered on the purple gradient.
3. Middle: Purple gradient fades as the skyline silhouette rises.
4. Bottom 45%: A PURE SOLID BLACK region — the silhouette base — extending all the way to the very bottom edge of the image with no purple below it. The top edge of this black region forms the {CITY} skyline profile. "Agents & APIs Meetup" in bold white text is centered inside this black base area near the bottom.

SKYLINE: The top edge of the solid black region shows recognizable {CITY} landmarks as a pure flat black silhouette — NO interior detail, NO windows, NO lines, NO lighter tones inside any shape. Exactly like the Austin/NYC reference images. Landmarks spread evenly left to right with clearly varied heights. ONLY landmarks from {CITY}. No suspension bridges. All connected with no gaps. The solid black ground fills the entire bottom of the image.

HIDDEN EASTER EGG: Somewhere along the top edge of the black silhouette — tucked between buildings, on a rooftop, or perched on a ledge — hide a tiny Postmanaut astronaut silhouette in pure solid black. It should be very small (no more than 3-4% of the image height), easy to miss at first glance but findable on closer look. The Postmanaut silhouette is a simple astronaut shape with a rounded helmet — pure black, no detail, blending into the skyline.

Square. No other text. No detail inside the black silhouette.
   """

   payload = {{
       "contents": [{{"parts": [{{"text": prompt}}]}}],
       "generationConfig": {{
           "responseModalities": ["IMAGE"],
           "imageConfig": {{
               "aspectRatio": "1:1",
               "imageSize": "2K"
           }}
       }}
   }}

   req = urllib.request.Request(
       URL,
       data=json.dumps(payload).encode(),
       headers={{"x-goog-api-key": API_KEY, "Content-Type": "application/json"}}
   )

   resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
   for part in resp["candidates"][0]["content"]["parts"]:
       if "inlineData" in part:
           img_data = base64.b64decode(part["inlineData"]["data"])
           with open(f"/tmp/meetup-cover-raw-{{CITY_SLUG}}.png", "wb") as f:
               f.write(img_data)
           print(f"Saved to /tmp/meetup-cover-raw-{{CITY_SLUG}}.png")
           break
   ```

   After saving the raw image, auto-crop any white/light border Gemini adds, then resize to 2000×2000:

   ```python
   # Add this after saving the raw image, before sips resize
   from PIL import Image
   img = Image.open("/tmp/meetup-cover-raw-{cityslug}.png").convert("RGB")
   w, h = img.size
   px = img.load()
   threshold = 240
   def is_border_row(px, y, w):
       return all(px[x, y][0] > threshold and px[x, y][1] > threshold and px[x, y][2] > threshold for x in range(w))
   def is_border_col(px, x, h):
       return all(px[x, y][0] > threshold and px[x, y][1] > threshold and px[x, y][2] > threshold for y in range(h))
   top = 0
   while top < h and is_border_row(px, top, w): top += 1
   bottom = h - 1
   while bottom > 0 and is_border_row(px, bottom, w): bottom -= 1
   left = 0
   while left < w and is_border_col(px, left, h): left += 1
   right = w - 1
   while right > 0 and is_border_col(px, right, h): right -= 1
   if top > 0 or left > 0 or bottom < h-1 or right < w-1:
       img.crop((left, top, right+1, bottom+1)).save("/tmp/meetup-cover-raw-{cityslug}.png")
   ```

   Then resize to exactly 2000×2000:
   ```bash
   mkdir -p /Users/quintonwall/Code/devrel-claude-code-skills/meetup-output/images
   sips -z 2000 2000 /tmp/meetup-cover-raw-{cityslug}.png \
     --out /Users/quintonwall/Code/devrel-claude-code-skills/meetup-output/images/cover-{YY-MM}-{cityslug}.png
   ```

   **Quality check** — use the Read tool to view the generated image and verify:

   | Check | Pass condition |
   |-------|---------------|
   | Purple gradient background | Smooth deep purple, dark at edges, vibrant in middle |
   | Postman logo + "POSTMAN" at top | Orange circle with white pen icon, white bold text beside it |
   | City name centered | Large, bold, white, correct city name |
   | City skyline silhouette | Recognizable flat black skyline for that city |
   | "Agents & APIs Meetup" footer | White text in dark bar at bottom |
   | Square format | Equal width and height |

   If any check fails, regenerate with a revised prompt emphasizing the failed element. Retry up to 2 times.

   Save a copy to `meetup-output/images/cover-{YY-MM}-{cityslug}.png` in the devrel-claude-code-skills project root (the same directory that contains the `skills/` folder). Create the directory if it doesn't exist. Do NOT use `${CLAUDE_PLUGIN_ROOT}` or any other variable — use this exact relative path from the project root.

   **2c. Upload the generated image to GCS to get a public URL.**

   Luma's public API only accepts a `cover_url` — it has no file upload endpoint. Upload the image to Google Cloud Storage using the same service account token already obtained in Step 2, then use the public GCS URL as `cover_url` when creating the event.

   ```bash
   FILENAME="cover-{YY-MM}-{cityslug}.png"
   GCS_BUCKET="$MEETUP_GCS_BUCKET"

   curl -s -X POST \
     -H "Authorization: Bearer $GTOKEN" \
     -H "Content-Type: image/png" \
     --data-binary @"/Users/quintonwall/Code/devrel-claude-code-skills/meetup-output/images/$FILENAME" \
     "https://storage.googleapis.com/upload/storage/v1/b/$GCS_BUCKET/o?uploadType=media&name=meetup-covers/$FILENAME&predefinedAcl=publicRead"
   ```

   The public URL will be: `https://storage.googleapis.com/{MEETUP_GCS_BUCKET}/meetup-covers/{FILENAME}`

   Use this URL as `cover_url` in the event create call (step 4).

   If `MEETUP_GCS_BUCKET` is not set, fall back to the template's `cover_url` for now and note the local file path in the report for manual upload.

3. **Build the slug** — format: `YY-MM-agents-and-apis-{cityname}`
   - City lowercased, spaces → hyphens (`New York` → `new-york`)
   - Example: Berlin, 12 Sep 2026 → `26-09-agents-and-apis-berlin`

4. **Create the event** — `POST https://api.lu.ma/public/v1/event/create`:

   Build the request body with these exact field names:
   ```json
   {
     "name": "{event name from sheet}",
     "visibility": "private",
     "slug": "{generated slug}",
     "calendar_api_id": "{LUMA_CALENDAR_ID}",
     "start_at": "{sheet date at 18:00 local time → UTC ISO8601}",
     "end_at": "{start_at + 2 hours → UTC ISO8601}",
     "timezone": "{city timezone, e.g. Europe/Lisbon}",
     "location_type": "offline",
     "location_visibility": "public",
     "geo_address_json": { ... built from sheet location fields ... },
     "waitlist_status": "enabled",
     "description": "{generic description from template, speaker section stripped}",
     "description_md": "{generic description_md from template, speaker section stripped}",
     "duration_interval": "P0Y0M0DT2H0M0S",
     "feedback_email": {"enabled": true, "delay": "P0Y0M0DT0H45M0S"},
     "registration_questions": [
       {"label": "What company do you work for?", "required": true, "question_type": "short_answer"},
       {"label": "What is your job title?", "required": true, "question_type": "short_answer"}
     ],
     "tags": ["agents", "ai", "api", "developer", "{regional-tag}"]
   }
   ```

   **Registration questions:** Do NOT include an `id` field — the `id` in the template response is an internal Luma identifier assigned to existing questions and will be rejected on create. Only pass `label`, `required`, and `question_type`. Use `"short_answer"` not `"text"` for the question type.

   **Tags:** Pass as plain strings (tag names), not as objects or `api_id` values. The regional tag should be derived from the event's country/region:
   - Europe → `"emea"`
   - Asia / India / Middle East → `"apac"`
   - US / Canada / Latin America → `"north-america"`
   - Use the country field from the spreadsheet row to determine the region.

   **Print the full create response** — check for errors and confirm which fields were accepted.

   On slug conflict (HTTP 409 or similar), append `-2`, `-3`, etc. and retry.

5. **Verify and patch missing fields** — immediately fetch the newly created event:
   ```bash
   curl -s -H "x-luma-api-key: $LUMA_API_KEY" \
     -H "User-Agent: ..." \
     "https://api.lu.ma/public/v1/event/get?api_id={NEW_EVENT_API_ID}"
   ```

   Compare the created event against the template. For any field that is empty/missing in the created event but present in the template, issue an `event/update` call to patch it:
   ```bash
   curl -s -X POST \
     -H "x-luma-api-key: $LUMA_API_KEY" \
     -H "Content-Type: application/json" \
     -H "User-Agent: ..." \
     -d '{"api_id": "NEW_EVENT_API_ID", "FIELD_NAME": "VALUE"}' \
     "https://api.lu.ma/public/v1/event/update"
   ```

   Patch each missing field separately and confirm each update succeeds. Log a summary of what was set on create vs. what required a patch.

6. **Cover image** — already included as `cover_url` in the create call (step 4) using the GCS public URL from step 2c. No separate upload step needed. If `MEETUP_GCS_BUCKET` was not set and the template fallback was used instead, note the local image path in the report.

7. **Write the new URL back** to the `Luma Event URL` column for that row.

Final report:
```
## --sync Complete

**Matched:** N | **Created:** N | **Skipped by user:** N

### Created Events

| Event | City | Slug | Cover Image | Luma URL |
|-------|------|------|-------------|----------|
| Berlin User Group | Berlin | 26-09-agents-and-apis-berlin | Reused from: Agents & APIs Berlin Mar 2026 | https://lu.ma/... |
| Tokyo Meetup | Tokyo | 26-10-agents-and-apis-tokyo | Generated + attached | https://lu.ma/... |
```

If the Luma file upload API is not supported, the report will instead show:
```
⚠ Cover image upload not supported via API. Attach manually in Luma's event editor:
  - meetup-output/images/cover-26-10-tokyo.png → https://lu.ma/26-10-agents-and-apis-tokyo
```

---

## `--update-stats` Mode

When the argument is `--update-stats`, skip the summary/filter flow entirely and enter stats sync mode. This fetches Luma registration and attendance data for each spreadsheet event that has a Luma URL and writes the numbers back into the sheet.

**Also verify `LUMA_API_KEY` is set** before proceeding.

### US-1: Verify additional prerequisite

Check that `LUMA_API_KEY` is set:

```bash
echo $LUMA_API_KEY
```

If missing, stop and tell the user to add it to `~/.claude/settings.json`. Then run the normal Steps 1–4 to get a Google token and fetch the sheet.

---

### US-2: Find or create stats columns in row 28

Fetch the full tab with formatting (reuse the same `includeGridData=true` call from US-1 if already fetched):

```bash
curl -s \
  -H "Authorization: Bearer $GTOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/$MEETUP_SHEET_ID?includeGridData=true&ranges=Meetups%20%26%20User%20Group%20Cal!A28:ZZ"
```

Locate these four columns (case-insensitive substring match):

| Column name | Look for |
|-------------|----------|
| `Luma Event URL` | `luma event url`, `luma url` |
| `Registered` | `registered`, `registrations` |
| `Waitlisted` | `waitlisted`, `waitlist` |
| `Attended` | `attended`, `checked in`, `attendance` |

For any of the three stats columns that don't exist yet, append them after the last non-empty header cell in row 28. Write missing headers now before processing rows (same PUT approach as `meetup-luma-sync` Step 7a). Record each column's letter for later writes.

---

### US-3: Classify spreadsheet rows

Parse all data rows (row 29+) from the `includeGridData` response. Skip a row if:
- ANY cell has `userEnteredFormat.textFormat.strikethrough == true` — cancelled event
- The `Type` column does not equal `Meetup` (case-insensitive) — not in scope

For each remaining row record:
- `sheet_row` — the 1-based sheet row number
- `name` — event name
- `date` — parsed date
- `luma_url` — value in `Luma Event URL` column (empty string if missing)
- `registered` — value in `Registered` column
- `waitlisted` — value in `Waitlisted` column
- `attended` — value in `Attended` column
- `is_past` — whether the event date is before today

Classify each row:

| Class | Condition |
|-------|-----------|
| `no_luma_url` | `luma_url` is empty — cannot fetch stats, skip |
| `already_filled` | All three stats columns are non-empty — skip |
| `needs_stats` | Has a Luma URL AND at least one stats column is empty AND event is in the past — fetch automatically |
| `upcoming_no_stats` | Has a Luma URL AND stats are empty AND event is upcoming — skip silently |

---

### US-4: Fetch stats automatically for past events with a Luma URL

A row with a Luma URL is confirmed as a real Luma event — no prompt needed. Fetch stats automatically for all `needs_stats` rows without asking.

Display a brief progress note before fetching:
```
Fetching Luma stats for N past events...
```

If there are no `needs_stats` rows, report that all past events with Luma URLs are already up to date.

Note any `no_luma_url` past events at the end of the report:
```
⚠ N past events have no Luma URL — run /devrel-skills:meetup-calendar --sync first to link them.
```

---

### US-5: Fetch all Luma events to build URL → api_id map

The Luma `get-guests` endpoint requires an `event_api_id` (e.g. `evt-XXXXXX`), not a URL. Build a lookup map from Luma URL to `api_id` by paging through all calendar events — same pattern as `luma-stats` and `meetup-luma-sync` (see `skills/luma-stats/SKILL.md` for the full helper with correct headers and pagination).

Write `/tmp/luma-map.py`:

```python
#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse

API_KEY = os.environ.get("LUMA_API_KEY", "")
BASE_URL = "https://api.lu.ma/public/v1"
CALENDAR_API_ID = os.environ.get("LUMA_CALENDAR_ID", "cal-TGqTNpY4iyl7XYe")
HEADERS = {
    "x-luma-api-key": API_KEY,
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

def luma_get(path, params=None):
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

url_to_api_id = {}
cursor = None
while True:
    params = {"calendar_api_id": CALENDAR_API_ID, "pagination_limit": 100}
    if cursor:
        params["pagination_cursor"] = cursor
    data = luma_get("/calendar/list-events", params)
    for e in data.get("entries", []):
        if e.get("url") and e.get("api_id"):
            url_to_api_id[e["url"]] = e["api_id"]
    if not data.get("has_more"):
        break
    cursor = data.get("next_cursor")
    if not cursor:
        break

print(json.dumps(url_to_api_id))
```

```bash
python3 /tmp/luma-map.py > /tmp/luma-url-map.json
```

---

### US-6: Fetch guest counts per event

For each confirmed row, look up its `api_id` from the URL map. Then fetch guest counts using the same `event/get-guests` pagination pattern from `luma-stats` (see `skills/luma-stats/SKILL.md`):

- **Registered** — guests where `approval_status == "approved"`
- **Waitlisted** — guests where `approval_status` is `"waitlisted"` or `"pending"`
- **Attended** — guests where `checked_in_at` is not null

If the Luma URL doesn't appear in the map (event may have been deleted or is on a different calendar), note it and skip that row.

Write `/tmp/luma-guests.py` following the `count_guests` function from `luma-stats`:

```python
#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.parse

API_KEY = os.environ.get("LUMA_API_KEY", "")
BASE_URL = "https://api.lu.ma/public/v1"
HEADERS = {
    "x-luma-api-key": API_KEY,
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

def luma_get(path, params=None):
    url = f"{BASE_URL}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

def count_guests(event_api_id):
    registered = waitlisted = attended = 0
    cursor = None
    while True:
        params = {"event_api_id": event_api_id, "pagination_limit": 500}
        if cursor:
            params["pagination_cursor"] = cursor
        data = luma_get("/event/get-guests", params)
        for g in data.get("entries", []):
            status = g.get("approval_status", "")
            if status == "approved":
                registered += 1
            elif status in ("waitlisted", "pending"):
                waitlisted += 1
            if g.get("checked_in_at"):
                attended += 1
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        if not cursor:
            break
    return registered, waitlisted, attended

# Read event_api_ids from stdin: {"sheet_row": N, "api_id": "evt-XXX", "name": "..."}
events = json.load(sys.stdin)
results = []
for ev in events:
    r, w, a = count_guests(ev["api_id"])
    print(f"  fetched: {ev['name'][:60]} — {r} registered, {w} waitlisted, {a} attended", file=sys.stderr)
    results.append({"sheet_row": ev["sheet_row"], "registered": r, "waitlisted": w, "attended": a})

print(json.dumps(results))
```

---

### US-7: Write stats back to the sheet

For each result, write the three stats values into their respective columns using a `batchUpdate`:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $GTOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "valueInputOption": "RAW",
    "data": [
      {"range": "Meetups & User Group Cal!{REG_COL}{ROW}", "values": [[142]]},
      {"range": "Meetups & User Group Cal!{WAIT_COL}{ROW}", "values": [[23]]},
      {"range": "Meetups & User Group Cal!{ATT_COL}{ROW}", "values": [[98]]}
    ]
  }' \
  "https://sheets.googleapis.com/v4/spreadsheets/$MEETUP_SHEET_ID/values:batchUpdate"
```

Only overwrite cells that were empty — do not overwrite cells that already had a value.

---

### US-8: Display final report

```
## Luma Stats Sync — Complete

**Updated:** N events
**Skipped (already filled):** N
**Skipped (no Luma URL):** N
**Skipped (upcoming):** N

### Stats Written

| Row | Event | Date | Registered | Waitlisted | Attended |
|-----|-------|------|-----------|-----------|---------|
| 29 | NYC API Meetup | 10 Apr 2026 | 142 | 23 | 98 |
| 31 | London User Group | 22 Mar 2026 | 87 | 0 | 71 |

⚠ N past events have no Luma URL — run /devrel-skills:meetup-luma-sync to link them first.
```

---

## Error Handling

| Error | Action |
|-------|--------|
| `MEETUP_SHEET_ID` not set | Stop. Tell user to add it to `.claude/settings.json` env block. |
| `GOOGLE_APPLICATION_CREDENTIALS` not set or file missing | Stop. Show service account setup instructions. |
| Token script fails with HTTP 401 | Service account key is invalid or revoked. Regenerate in Google Cloud Console → Service Accounts → Keys. |
| HTTP 403 from Sheets API | Service account email hasn't been granted access to the sheet. Share the sheet with the service account email (Editor access). |
| HTTP 404 from Sheets API | Sheet ID is wrong. Double-check `MEETUP_SHEET_ID` in settings. |
| Tab not found in metadata | List available tab names and ask user to confirm the correct name. |
| `values` array is empty | Sheet tab exists but has no data. Confirm the correct tab is selected. |
| Python parse error | Print the raw first 3 rows from the API response for debugging. |
