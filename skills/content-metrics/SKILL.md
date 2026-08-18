# Content → Product Metrics

Measure how DevRel content ties to Postman product activation and adoption. Pulls blog stats from blog.postman.com and video stats from youtube.com/postman, joins them with product-side attribution (signups, first product action, Day-7 return, Day-30 return) when a data source is wired, and posts a **Content → Product** digest with Claude's commentary to the team Slack channel. Implements the full funnel documented in `docs/content-funnel.md`, including the `impact_score = resonance + activation + adoption` model.

Use when the user wants to:
- See how content shipped in the past N days converted to Postman signups and product activity
- Post a Content → Product digest to Slack with Claude's interpretation of what landed
- Investigate which pieces drove real activation vs which just drove views

## Current state (what fills, what's blank)

Filled today for every row:
- `title`, `ship_date`, `url`, `type`, `content_id`
- Blog: `comments` (from WordPress REST API)
- Video: `views`, `likes`, `comments` (from YouTube Data API v3)

Filled when `PRODUCT_ANALYTICS_SOURCE=looker` and Looker env vars are set:
- `attributed_signups`, `attributed_first_run`, `attributed_day7_return`, `attributed_day30_return`
- Computed: `activation_score`, `adoption_score`, `impact_score`

Blank today (pending instrumentation, see `docs/content-funnel.md`):
- Blog: `impressions`, `views`, `ctr_pct`, `view_read_time_min`, `completion_pct`, `repeat_pct` (needs GA4 + Search Console)
- Video: `impressions`, `ctr_pct`, `view_read_time_min`, `completion_pct`, `repeat_pct`, `shares` (needs YouTube Analytics API OAuth + channel access)
- Cross-content: `utm_clicks` (needs GA4)

## Input Handling

Accepts a single optional argument:

- **Integer** (e.g., `7`, `30`, `90`) — lookback window in days. If a number is passed, it overrides the default.
- **Natural phrase** — Claude resolves to days:
  - `last week`, `past week`, `this week` → 7
  - `last month`, `past month`, `this month` → 30
  - `last quarter`, `past quarter`, `this quarter` → 90
- **`--no-slack`** — pull and interpret but do not post to Slack
- **No arg** — defaults to **30 days**

Examples:
- `/devrel-skills:content-metrics` — past 30 days, post to Slack
- `/devrel-skills:content-metrics 7` — past 7 days
- `/devrel-skills:content-metrics 90` — past 90 days
- `/devrel-skills:content-metrics last week` — past 7 days
- `/devrel-skills:content-metrics 7 --no-slack` — pull and show, do not post

## Data sources

- **Blog:** all posts with `status=publish` on [blog.postman.com](https://blog.postman.com) whose publish date falls within the lookback window. Fetched via the WordPress REST API. Populates the `title`, `ship_date`, `url`, and `comments` columns; all other blog columns need GA4 / GSC instrumentation (see `docs/content-funnel.md`).
- **YouTube:** all videos uploaded to the [Postman channel](https://www.youtube.com/postman) (channel ID `UCocudCGVb3MmhWQ1aoIgUQw`) within the lookback window. Channel is hardcoded — do not require the user to configure it. Uses the **YouTube Data API v3** (API key only), which populates `views`, `likes`, and `comments`. Every other YT resonance column (`impressions`, `ctr_pct`, `view_read_time_min`, `completion_pct`, `repeat_pct`, `shares`) needs the **YouTube Analytics API** — a separate API that requires OAuth + channel-manager access on the Postman channel. Not wired yet; see `docs/content-funnel.md` § "YouTube data sources" for the 4-step path.

## Prerequisites

Env vars in `~/.claude/settings.json` under `"env"`:

- **`WP_USERNAME`, `WP_APP_PASSWORD`** — required. WordPress app password for blog.postman.com.
- **`YT_API_KEY`** — optional. Google API key with the YouTube **Data API v3** enabled. Missing => YouTube section is skipped with a warning. This key only unlocks `views` / `likes` / `comments` per video; it does NOT unlock impressions, CTR, watch time, or retention.
- **`SLACK_WEBHOOK_URL`** — required for Slack posting. Incoming Webhook URL bound to the team channel.
- **`YT_CHANNEL_ID`** — optional override for the YouTube channel. Defaults to the Postman channel; only set if you're pointing at a different channel.
- **`YT_OAUTH_CLIENT_ID`, `YT_OAUTH_CLIENT_SECRET`, `YT_OAUTH_REFRESH_TOKEN`** — reserved for the future YouTube Analytics API adapter. Not read by the script today; set them when the adapter lands.
- **`PRODUCT_ANALYTICS_SOURCE`** — selects the product-attribution adapter (see `docs/content-funnel.md` § "Product attribution architecture"). Supported values: `looker` (**implemented**), `ga4` / `amplitude` / `warehouse` / `postman-admin` (stubs, not implemented yet). Unset => attribution columns stay blank; the digest reports "attribution pending" instead of a fake zero.
- **Looker adapter env vars** (only when `PRODUCT_ANALYTICS_SOURCE=looker`): `LOOKER_CLIENT_ID`, `LOOKER_CLIENT_SECRET`, `LOOKER_LOOK_ID` are required. `LOOKER_BASE_URL` defaults to `https://postman.looker.com`. Column-name overrides (`LOOKER_UTM_CONTENT_COL`, `LOOKER_SIGNUPS_COL`, `LOOKER_FIRST_RUN_COL`, `LOOKER_DAY7_COL`, `LOOKER_DAY30_COL`) are optional; the adapter prints the actual column names if the defaults don't match.

If a required env var is missing, tell the user which one and stop. Do not silently skip.

## Workflow

### Step 1: Parse the argument

Determine:
- `days` (integer) — from the input per the rules above. Default **30**.
- `skip_slack` (bool) — true if the arg contains `--no-slack`, otherwise false.

If the user's phrasing is ambiguous, ask a single clarifying question rather than guessing.

### Step 2: Pull metrics (skip if user requested a repost of an existing CSV)

Run the pull script from the repo root:

```bash
python3 skills/content-metrics/references/pull-metrics.py --days {days}
```

The script:
- Fetches blog posts published in the past `{days}` days from blog.postman.com
- Fetches videos uploaded in the past `{days}` days from the DevRel YouTube channel
- Writes `content-metrics/YYYY-Www.csv` (one row per piece)
- Prints `[csv] {absolute_path}` as its last stdout line before returning

Capture the CSV path from that `[csv]` line.

### Step 3: Read the CSV and interpret

Read the CSV. The columns follow the full three-stage impact model defined in `docs/content-funnel.md`: resonance (Stages 2-3), activation (Stage 5), and adoption (Stage 6). Each row includes the four `attributed_*` columns and the three computed sub-scores (`resonance_score`, `activation_score`, `adoption_score`) plus the combined `impact_score`.

**Lead with product outcomes when they exist.** If any row has non-blank `attributed_signups` or `attributed_first_run`, the interpretation opens with the Content → Product story:

- Total attributed signups, first-run, Day-7 return, Day-30 return across the window
- Which specific pieces produced the most activation (name them with numbers)
- Whether high-resonance pieces also produced activation (correlation check — a piece with high views but zero attributed signups is worth calling out)

**Fall back to resonance-only interpretation when attribution data is missing.** If the `attributed_*` columns are universally blank (which is the current state until `PRODUCT_ANALYTICS_SOURCE` is configured), say so explicitly — "attribution pending, ranking by resonance only" — and continue with:

1. **Top mover** — the piece with the highest views. Name it explicitly with its actual title and number. If CTR or view/read time data is present, prefer that over raw views.
2. **Outliers** — any piece where `views`, `ctr_pct`, `view_read_time_min`, `completion_pct`, `likes`, or `comments` is more than 2× the median for its type. Numeric only; do not read subjective quality into the numbers.
3. **Packaging wins vs consumption wins** — high CTR with low completion_pct means the title landed but the content didn't. High completion_pct with low CTR means the content is strong but the packaging is losing at the top of the funnel. Both are actionable and different.
4. **Suspected duds** — pieces at least 3 days old with views under 500 AND zero comments AND zero likes AND (if populated) completion_pct under 20%. Candidates for reformatting or retirement.
5. **Type comparison** — how blogs performed vs videos in aggregate.
6. **Week-over-week trend** — if prior weekly CSVs exist in `content-metrics/`, compare ship count, median views, and (when available) total attributed_signups against the previous 1-2 weeks.

**When both resonance and attribution data are present, always call out the mismatch cases:**

- Pieces with high `resonance_score` but zero `activation_score` — content resonated but didn't drive product action. Is the CTA missing, mis-targeted, or wrong?
- Pieces with low `resonance_score` but non-zero `activation_score` — small audience but converts. Amplify.

Do not treat blank cells as zero when reporting. A blank cell means the data source isn't wired; a zero means the source is wired and the count really is zero. The distinction matters when someone reads the digest.

### Step 4: Draft commentary

Write 3-4 sentences in Slack `mrkdwn` format. Save to `/tmp/content-metrics-commentary.txt`.

Structure (product outcomes lead when data exists):

1. **Content → Product headline** — total attributed signups, first-run, Day-7 return, and Day-30 return across the window. When attribution is pending, say: `Content → Product: attribution pending (source not configured).`
2. **Best converter** — the piece with the highest `activation_score` (or `impact_score`), named explicitly with specific numbers. Fall back to highest-resonance piece if attribution is pending.
3. **Notable pattern** — an outlier, a mismatch case (high resonance / zero activation is the classic), or a type-comparison observation.
4. **One recommendation** — kill, reformat, or amplify one specific piece, with a one-clause reason grounded in activation or resonance data.
5. (Optional) **Trend** — week-over-week direction if prior CSVs exist. Prefer trending activation over trending views when available.

Commentary rules:
- Factual only. No marketing language, no adjectives like "great" or "strong."
- Name pieces by their actual title. Do not say "the AI Engineer post" when there are three of them.
- Numbers use commas as thousands separators and at most one decimal place.
- No em dashes. Use periods, commas, or colons.
- Use Slack's `*bold*` sparingly for a single title per sentence.
- Keep the whole thing under 400 characters. Slack readers scan; they do not read.

Example commentary (attribution wired, product outcomes lead):
```
*Content → Product:* 47 signups • 31 first product actions • 22 Day-7 returned • 9 Day-30 returned across 12 pieces this window.
*Best converter:* *Loops & beads* drove 18 signups and 11 Day-30 returned users, roughly 4× the video median.
*Mismatch:* *Three-way drift + AI Engineer* has 4,200 views and 6 comments but only 2 attributed signups. CTA likely broken or mis-targeted; audit before amplifying.
*Trend:* Attributed signups up 22% vs last window; ship count flat (3 blogs + 3 videos).
```

Example commentary (attribution pending, resonance only):
```
*Content → Product:* attribution pending (source not configured).
20 blog posts shipped in the past 30 days on blog.postman.com; 0 recorded comments across all of them. All resonance columns are blank pending GA4 + Search Console setup, so `impact_score` is 0 for every piece and the leaderboard cannot yet rank them.
*Recommendation:* wire the Looker adapter next. Until then this run confirms ship cadence but cannot distinguish which posts landed.
```

### Step 5: Post to Slack (unless `skip_slack` is true or `SLACK_WEBHOOK_URL` is missing)

Run the post-only mode of the script, passing the CSV path from Step 2 and the commentary file:

```bash
python3 skills/content-metrics/references/pull-metrics.py \
  --from-csv {csv_path} \
  --commentary-file /tmp/content-metrics-commentary.txt \
  --days {days}
```

This reads the existing CSV (no re-fetch) and posts the Block Kit message with:
- **Header:** `Content → Product — YYYY-Www`
- **Context line:** window dates + ship count (`X blog posts + Y videos`)
- **Product headline:** total attributed signups / first-run / D-7 / D-30 across the window, or `attribution pending (source not configured)` when Looker/other source isn't wired
- **Commentary section:** the 3-5 sentences you drafted
- **Top-pieces table:** top 10 by views, monospace code block with Content / Type / Views / Likes / Cmts columns
- **Footer:** reminder about pending instrumentation + relative CSV path

If `SLACK_WEBHOOK_URL` is not set, the script fails loudly with a setup message. If `skip_slack` was requested, do not run this step.

### Step 6: Report back to the user

Show:
- The lookback window and ship count
- The commentary you drafted (verbatim)
- Whether it was posted to Slack, and if not, why
- Path to the CSV

Keep this summary under 10 lines.

## Error Handling

- **Missing `WP_USERNAME` / `WP_APP_PASSWORD`:** script fails immediately. Tell the user to add them to `~/.claude/settings.json`.
- **Missing YouTube credentials:** YouTube section is skipped. Continue with blog-only results and note in the report that YouTube was skipped.
- **Missing `SLACK_WEBHOOK_URL` when Slack is requested:** script fails. Point the user to `docs/content-funnel.md` for the one-time setup steps.
- **`PRODUCT_ANALYTICS_SOURCE` unset:** attribution columns stay blank and the digest reports "attribution pending." This is expected until a data source is wired.
- **`PRODUCT_ANALYTICS_SOURCE=looker` with missing Looker env vars:** hard failure with a message naming which vars are missing (`LOOKER_CLIENT_ID`, `LOOKER_CLIENT_SECRET`, `LOOKER_LOOK_ID`). Point the user to `docs/content-funnel.md` § "Looker adapter" for setup.
- **Looker column names don't match:** the adapter prints a warning listing the actual columns present in the Look output. Tell the user to set the appropriate `LOOKER_*_COL` override env var and re-run. Continue with blank attribution for this run.
- **Looker authentication / Look-run failure (401, 403, 404, network):** script exits with a specific SystemExit message. Do not attempt to post partial data to Slack. The user needs to fix creds or Look access before rerunning.
- **`PRODUCT_ANALYTICS_SOURCE=ga4|amplitude|warehouse|postman-admin`:** these are stubs. The script raises NotImplementedError and continues with blank attribution. Tell the user which adapters are implemented (`looker` only, today).
- **Empty result set (zero pieces shipped):** still post to Slack. "0 blogs + 0 videos this window" is itself a useful signal. Commentary should note the empty window and, if prior CSVs exist, whether this is a change from last time.
- **Network / API errors on the pull side:** show the error and stop. Do not attempt to post partial results to Slack.

## Important Guidelines

- **Two invocations per run, one pull.** Step 2 fetches; Step 5 reads the same CSV. Never run the script twice with `--days` in a single skill invocation, or you double the API load.
- **Never edit the CSV between steps.** Claude's job is to read and interpret, not rewrite the data. If the numbers look wrong, note it in the commentary and stop; do not patch the CSV to make the story cleaner.
- **Commentary is factual, not editorial.** The reader is a DevRel teammate who will act on this. Overclaiming loses trust faster than underclaiming.
- **Do not schedule this skill.** The skill is human-triggered by design. If the user wants an automated weekly (or monthly) post, tell them to wire a cron job that calls the underlying script directly (`python3 skills/content-metrics/references/pull-metrics.py --days 30 --slack`). That path skips Claude's commentary layer but still delivers the CSV, the product-outcome headline, and the top-pieces table to Slack.
- **When talking about attribution numbers, always name the source.** "Signups via Looker" is different from "signups reported by product analytics" is different from "signups (attribution pending)." Ambiguity here is how the funnel loses credibility with a skeptical reviewer.
