# DevRel content resonance funnel

Operational funnel and scorecard for measuring how DevRel-produced content (blog posts, YouTube videos, livestreams, sample repos, demos) actually resonates with developers — not just how much of it we ship.

## Why this exists

We are shipping a lot. Volume is easy to measure and easy to mistake for impact. This funnel exists so we can tell the difference between "we published 40 things this quarter" and "3 of those 40 moved users into the product." Assume marketing and product will not build this for us; the funnel has to be cheap enough for one person to keep alive.

## The funnel

Each stage names the question, the specific "yes" signals to look at, the smell to watch for (false positive that fakes resonance), the data source, and whether the metric is manual (M) or automated (A).


| #   | Stage             | Question                      | "Yes" signals (specific)                                                                                                             | Smell to watch                                            | Data source                                                | M/A             |
| --- | ----------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------- | ---------------------------------------------------------- | --------------- |
| 1   | **Ship**          | What did we make?             | Count of blog posts published on blog.postman.com + videos published on our YouTube channel in period                                | Counting Stage 1 as impact                                | blog.postman.com WP API + YouTube channel uploads          | A               |
| 2   | **Reach**         | Did the content surface at all?     | **Impressions** and **views** across both content types. For blogs: search impressions (GSC) + social impressions (LinkedIn, X) + page views (GA4). For videos: impressions across browse/search/suggested (YT Analytics) + views (YT Data API). | Viral views with zero downstream (algorithm inflation)    | GSC, GA4, LinkedIn/X analytics, YT Data + Analytics APIs   | A (partial) |
| 3   | **Resonance**     | Did people actually consume it?     | **CTR**, **watch/read time**, **completion %**, **repeat consumption**, and **comments**. For blogs: search+social CTR, avg engagement time, scroll-to-end %, returning-visitor %, comment count. For videos: impression-to-play CTR, avg view duration, avg % viewed, returning-viewer %, comment count. See the "Resonance metrics by content type" table below for the full mapping. | High views + short watch/read time (algorithm inflation, clickbait titles) | YT Analytics API, GA4 engagement metrics, GSC, WordPress + YT comment counts | A (partial) |
| 4   | **Intent**        | Did they go looking for more? | UTM'd clicks to docs / product / GitHub, repo clones, cross-content pull (video → blog)                                              | High CTA clicks with 0-second landing time (misfired UTM) | GA/PostHog, GitHub referrer, UTM per link                  | A               |
| 5   | **Activation**    | Did they try the product?     | New workspaces, AI Engineer sessions started, Context Graph connected, first agent run, first flow generated, filtered by UTM cohort | Signups from a campaign that never open the product       | Product telemetry keyed by UTM                             | A (needs setup) |
| 6   | **Adoption**      | Did they get value?           | Day-7 / Day-30 return, 2+ agent runs, 1+ integration, PR reviews run, evaluated for the cohort you brought in                        | Adoption stats for the whole product (not your cohort)    | Product telemetry, cohort filter on `content_source`       | A (needs setup) |
| 7   | **Amplification** | Did they bring others?        | Community threads referencing the content, customer quotes, inbound "I saw your video" in sales calls, other devs remixing / forking | Retweets by other devrels (echo chamber)                  | CRM, community, sales-call notes, brand search             | M               |

*Legend — **M** = manual (someone types the number in each week). **A** = automated (a script or dashboard pulls it). **A (needs setup)** = will be automated once the underlying instrumentation lands (product `content_source` event, GA4 export, or YouTube Analytics OAuth). **A (partial)** = some columns are pulled today, others need the same additional setup.*

## Resonance metrics by content type

Blogs and videos are different mediums, but the resonance question is the same: **how many people saw it, how many clicked in, how much of it did they actually consume, and did they come back.** This table names the concrete metric to pull for each content type, so blogs and videos land on the same axes and can be compared without apples-to-oranges caveats.

| Metric              | What it tells you                                                    | Blog source                                                                    | Video source                                                          | Available today? |
| ------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------- | ---------------- |
| **Impressions**     | How many times the title/thumbnail was shown to a potential consumer | Google Search Console (search impressions) + LinkedIn / X analytics (social)   | YouTube Analytics API (browse, search, suggested surfaces)            | No — needs GSC + YT Analytics OAuth |
| **Views**           | How many people clicked through and started consuming                | GA4 page views (or unique users on the page)                                   | YouTube Data API v3 (`viewCount`)                                     | Videos yes; blogs need GA4 export |
| **CTR**             | How compelling the packaging was (title, hook, thumbnail)            | GSC search CTR + calculated social CTR (clicks / impressions per post)         | YouTube Analytics API (impression CTR, %)                             | No — same setup as impressions |
| **Watch / read time** | How much of the piece was actually consumed                        | GA4 average engagement time on page (seconds)                                  | YouTube Analytics API (avg view duration, seconds)                    | No — needs GA4 export + YT Analytics OAuth |
| **Completion %**    | Whether people got to the end                                        | Scroll-depth tracking to end of article (GA4 event or custom snippet)          | YouTube Analytics API (avg % viewed)                                  | No — needs custom scroll event on blog + YT Analytics OAuth |
| **Repeat consumption** | Whether the piece became a reference people came back to          | GA4 returning-user % on that page                                              | YouTube returning-viewer segment                                      | No — needs GA4 + YT Analytics OAuth |
| **Comments**        | Whether the piece prompted a technical response                      | WordPress comment count (`/wp-json/wp/v2/comments?post=id`)                    | YouTube comment count (Data API `commentCount`)                       | Yes for both |
| **Shares / saves**  | Whether people are recirculating the content                         | LinkedIn / X reshare counts (manual today; social API if enabled)              | YouTube shares (Analytics API)                                        | Partial — manual for now |

**How to read this table.** Every row treats blog and video as parallel first-class artifacts. If a metric is available for one and not the other, that's a data-source gap to close — not an excuse to score one type by richer signals than the other. The "Available today?" column is the honest instrumentation status; see the setup checklist below to close each gap.

## YouTube data sources

Two YouTube APIs are relevant here, and only one is wired up today. The gap between them is where every blank YouTube column in the CSV comes from.

### What's pulled today (YouTube Data API v3)

Uses only `YT_API_KEY`, no OAuth. Three endpoints called per run against channel `UCocudCGVb3MmhWQ1aoIgUQw` ([youtube.com/postman](https://www.youtube.com/postman)):

1. `channels?part=contentDetails&id={channel}` — resolve the uploads playlist ID for the channel.
2. `playlistItems?playlistId={uploads}` — walk backward through recent uploads until videos fall past the cutoff.
3. `videos?part=snippet,statistics&id={batch}` — batched stats call, up to 50 video IDs per request.

Fields captured per video:

| CSV column | Data API field           | What it is                                     |
| ---------- | ------------------------ | ---------------------------------------------- |
| `views`    | `statistics.viewCount`   | Lifetime view count                            |
| `likes`    | `statistics.likeCount`   | Lifetime like count                            |
| `comments` | `statistics.commentCount`| Total comment count                            |

Plus `title`, `publishedAt`, and the canonical watch URL. These are the same public counts anyone can read on the video page. That is the entire Data API surface.

### What's blank (needs the YouTube Analytics API)

Every other YouTube column in the CSV is `""` today with a `TODO_YT_ANALYTICS` marker:

- `impressions` — how many times the thumbnail was shown across browse, search, and suggested surfaces
- `ctr_pct` — impression-to-play click-through rate
- `view_read_time_min` — average view duration in minutes
- `completion_pct` — average % viewed (the retention curve, aggregated to a single number)
- `repeat_pct` — returning-viewer segment
- `shares` — YouTube share count

Beyond the columns above, the Analytics API also exposes **traffic source breakdown** (YouTube Search, Browse features, Suggested videos, External, Notifications, Playlists). That signal is not in the current scorecard but is worth adding once the API is wired, because it separates "this video is compounding as evergreen search" from "this video is riding a short-lived algorithm boost."

### Why they're blank

The YouTube Data API v3 only exposes public counts. Everything above requires the [**YouTube Analytics API**](https://developers.google.com/youtube/analytics), which is a separate API with a different auth model and a permission model that depends on channel access, not just project access.

### What's needed to close the gap

Four things, ordered by effort (smallest first, biggest political ask last):

1. **Enable the YouTube Analytics API** in the same Google Cloud project as `YT_API_KEY`. Free, one-click, no cost impact.
2. **OAuth 2.0 client credentials.** The Analytics API refuses API keys. You need:
   - An OAuth Client ID (Desktop app or Web app type) created in Google Cloud Console
   - A one-time consent flow to get a refresh token
   - Three env vars in `~/.claude/settings.json`: `YT_OAUTH_CLIENT_ID`, `YT_OAUTH_CLIENT_SECRET`, `YT_OAUTH_REFRESH_TOKEN`
   - Scope: `https://www.googleapis.com/auth/yt-analytics.readonly`
3. **Channel-manager access on youtube.com/postman.** This is the actual blocker. The Analytics API only returns data for channels the authenticated Google account has permission to view analytics for. Whoever owns the Postman YouTube channel today (marketing or content ops) has to grant your Google account **Viewer (limited)** or higher via YouTube Studio → Settings → Permissions. Without this, OAuth completes fine but Analytics API calls return empty datasets.
4. **Adapter code** — a `fetch_youtube_analytics(video_ids)` helper in `skills/content-metrics/references/pull-metrics.py` that calls `youtubeAnalytics.reports.query()` per video and merges the numbers into each row. Roughly 50 lines. Uses `google-auth`, `google-auth-oauthlib`, and `google-api-python-client` (or a hand-rolled OAuth flow to stay stdlib-only).

### Realistic sequence

1. Ask the channel owner for "Viewer (limited)" access. Frame as read-only for DevRel content attribution. This is the longest-lead item; start it first.
2. While waiting, enable the Analytics API and generate OAuth credentials in the Cloud console.
3. Once channel access lands, implement the `fetch_youtube_analytics()` adapter. The CSV starts filling `impressions`, `ctr_pct`, `view_read_time_min`, `completion_pct`, `repeat_pct`, `shares` on the next run.

## Product attribution architecture

The whole point of this funnel is to connect content to Postman product activation and adoption. That requires three things to be in place. Two DevRel owns outright; the third needs a product-side data source but has a clean plug-in point in the pull script.

### 1. UTM convention (DevRel-owned)

Every outbound link from a blog post, video description, livestream chat, or sample repo uses this UTM shape:

```
utm_source=devrel
utm_medium={blog|youtube|livestream|talk|repo}
utm_campaign={product-slug: ai-engineer, context-graph, flows, mcp, ...}
utm_content={content_id}
```

`utm_content` matches the `content_id` column in the CSV exactly (`wp-20414` for a blog post, `yt-abc123` for a video). That single field is the join key that makes cross-system attribution work. Without it, product-side data cannot be attributed to a specific piece.

The convention is enforceable at authoring time: the blog-write and blog-wordpress-stage skills can rewrite outbound `*.postman.com` links to include the UTM at staging. Same for video-description templates.

### 2. Product-side data source (needs setup)

`skills/content-metrics/references/pull-metrics.py` has a `fetch_product_activation(content_ids, since_date)` function. Today it returns blank rows with a "not configured" note. When you plug in one of the following data sources, it starts returning real numbers:

| Data source                                            | Status              | What it gives you                                                                    | How to wire it                                                                          |
| ------------------------------------------------------ | ------------------- | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| **Looker ([postman.looker.com](https://postman.looker.com))** | **Implemented**     | Whatever the target Look surfaces — typically `signups`, `first_run`, `day7_return`, `day30_return` dimensioned by `utm_content` | Set `PRODUCT_ANALYTICS_SOURCE=looker` and provide `LOOKER_CLIENT_ID`, `LOOKER_CLIENT_SECRET`, `LOOKER_LOOK_ID`. See "Looker adapter" below. |
| **GA4 measuring postman.com**                          | Stub                | `sign_up` events with `utm_content` preserved                                        | GA4 Data API v1 + service-account credential; filter events by `utm_content` values     |
| **Amplitude / Mixpanel / Segment / Heap**              | Stub                | Same, higher fidelity if UTMs are captured on the signup event                       | Product-analytics tool's HTTP API; same filter                                          |
| **Internal data warehouse (Snowflake / BigQuery / …)** | Stub                | Widest scope — signup, first_run, D-7/D-30 tables joined on user                     | SQL query with `content_source = utm_content`; read-only warehouse role                 |
| **Postman admin API**                                  | Stub                | Coarse: org-wide workspace creation, active user counts, no per-content attribution  | Admin API key; correlate ship dates with lagged workspace activity                      |

The function signature is the contract. Whichever source you plug in, it returns the same shape:

```python
def fetch_product_activation(content_ids: list[str], since: date) -> dict[str, dict]:
    """Return {content_id: {'signups': int, 'first_run': int,
                            'day7_return': int, 'day30_return': int}}"""
```

Empty entries default to zero. Missing content_ids default to zero (not "unknown"), because a content_id with no signal really did produce zero attributable outcomes.

### 2a. Looker adapter (implemented)

`skills/content-metrics/references/pull-metrics.py` includes a working [Looker](https://postman.looker.com) adapter behind `PRODUCT_ANALYTICS_SOURCE=looker`. It authenticates with the Looker API v4, runs a saved Look, and remaps its rows to the standard `{content_id: {...}}` shape.

**Setup (one-time):**

1. In [postman.looker.com](https://postman.looker.com), open the target Look (the one on board 197 that surfaces per-`utm_content` signup and activation counts). Note the numeric Look ID from the URL (`/looks/{id}`).
2. Go to `postman.looker.com/admin/users`, find your user, and generate API keys under "API Keys." You get a `client_id` and `client_secret`.
3. Add to `~/.claude/settings.json` under `"env"`:

   ```json
   "PRODUCT_ANALYTICS_SOURCE": "looker",
   "LOOKER_CLIENT_ID": "…",
   "LOOKER_CLIENT_SECRET": "…",
   "LOOKER_LOOK_ID": "1234"
   ```

4. On the next run, the adapter will call the Look and populate `attributed_signups`, `attributed_first_run`, `attributed_day7_return`, `attributed_day30_return` for every content_id that appears in the Look's output.

**Column name overrides.** Looker often returns view-prefixed column names (e.g. `sessions.utm_content` rather than plain `utm_content`). The adapter's defaults are the plain names; override via env vars if the Look uses a different convention:

| Column purpose | Env var                    | Default          |
| -------------- | -------------------------- | ---------------- |
| utm_content    | `LOOKER_UTM_CONTENT_COL`   | `utm_content`    |
| Signups        | `LOOKER_SIGNUPS_COL`       | `signups`        |
| First product action | `LOOKER_FIRST_RUN_COL` | `first_run`      |
| Day-7 return   | `LOOKER_DAY7_COL`          | `day7_return`    |
| Day-30 return  | `LOOKER_DAY30_COL`         | `day30_return`   |

If the adapter runs and the columns don't match, it prints the actual column names present in the response so you can set the correct override without guessing. It does not fail — the columns just come back blank.

**Aggregation across rows.** If the Look groups by date (one row per content per day, for example), the adapter sums the metrics across all rows for the same `content_id`. Behavior is idempotent within a single run.

**LOOKER_BASE_URL** defaults to `https://postman.looker.com` and rarely needs to be set.

### 3. The join (already built)

`pull-metrics.py` pulls the content-side CSV (Stages 1-3), calls `fetch_product_activation()` with the content_id list, and merges the two on content_id to produce the full row. It then computes `activation_score`, `adoption_score`, and `impact_score` per the formulas above. No product-side data source == all attributed_* columns are blank == impact_score collapses to resonance_score. The system degrades gracefully.

### What to expect while waiting on setup

Until the product-side source is wired:

- `impressions`, `ctr_pct`, `view_read_time_min`, `completion_pct`, `repeat_pct` are blank pending GA4/GSC/YT Analytics setup.
- `utm_clicks`, `attributed_signups`, `attributed_first_run`, `attributed_day7_return`, `attributed_day30_return` are blank pending the product-side source.
- The Slack digest leads with "Content → Product this week: attribution pending" so nobody mistakes zero for zero.
- The impact_score ranks pieces by resonance_score alone, and the doc says so.

Do not fake the numbers with proxies. Blank is more honest than made-up.

## Per-content scorecard

One row per blog post or YouTube video. This is the artifact that answers the real question: which use cases resonated. Aggregate weekly, review monthly, prune quarterly. The columns map 1:1 to the "Resonance metrics by content type" table above, so blogs and videos are ranked on the same axes.

| Content                       | Type    | Ship date  | Views  | CTR % | Read/view (min) | Compl % | Comments | Signups | First run | D-7 ret | D-30 ret | Impact score |
| ----------------------------- | ------- | ---------- | ------ | ----- | --------------- | ------- | -------- | ------- | --------- | ------- | -------- | ------------ |
| Three-way drift + AI Engineer | Blog    | 2026-08-25 | 4,200  | 11.1% | 3.8             | 44%     | 6        | 12      | 8         | 5       | 2        | 314          |
| Multi-repo API changes        | Blog    | 2026-08-13 | 2,900  | 12.9% | 2.1             | 28%     | 2        | 6       | 3         | 1       | 0        | 146          |
| Loops & beads                 | YouTube | 2026-08-12 | 11,000 | 12.0% | 5.2             | 38%     | 14       | 34      | 19        | 19      | 11       | 1,208        |
| …                             | …       | …          | …      | …     | …               | …       | …        | …       | …         | …       | …        | …            |

Full scorecard (all columns): impressions, views, ctr_pct, view_read_time_min, completion_pct, repeat_pct, likes, comments, shares, utm_clicks, attributed_signups, attributed_first_run, attributed_day7_return, attributed_day30_return, resonance_score, activation_score, adoption_score, impact_score. The truncated view above shows the ones you'll look at most; the CSV has everything.

Blank cells are fine while instrumentation is landing. The scorecard is designed to be filled incrementally — start with what you can pull today (views + comments for both types), add CTR / watch-and-read time / completion as GA4 and YT Analytics come online, and use the resonance score as an overall rank once at least three columns are populated.

## Impact score (content → product)

The scoring model is deliberately split so activation and adoption dominate the total. A piece of content that produces attributed signups matters more than one with high views but nothing downstream, and the score should say that out loud.

```
resonance_score  = (ctr_% × 4) + (view_read_time_min × 5) + (completion_% × 0.5)
                 + (repeat_% × 3) + (tech_comments × 3) + (shares × 0.5)

activation_score = (attributed_signups × 10) + (attributed_first_run × 15)

adoption_score   = (attributed_day7_return × 20) + (attributed_day30_return × 40)

impact_score = resonance_score + activation_score + adoption_score
```

**Why this shape.** Resonance is a leading indicator (did anyone engage). Activation is what the content is actually trying to produce (did engaged people try Postman). Adoption is what matters to the business (did they stay). The coefficients make a single attributed Day-30 return worth roughly the same as a strong resonance profile on its own, because that's the honest weighting: a piece that produces one Day-30 retained Postman user is worth more than a piece with high watch time but no product outcome.

**Applied identically to blog posts and YouTube videos.** Every input has a blog-side and a video-side source (see "Resonance metrics by content type" above and "Product attribution architecture" below), so a blog and a video are ranked on the same axes.

**Interpretation.** Rank by impact_score. Break ties by activation_score (product-side signal dominates), then by resonance_score. A piece more than one standard deviation below the type median on impact_score is a candidate for retirement or reformatting. If activation_score is universally zero (because the product-side data source isn't wired yet), the impact_score collapses to resonance_score, and the ranking is honest about being resonance-only for that window.

**Tuning.** The constants are opinionated defaults. Tune them once, after three months of real numbers, by correlating the score against a Stage 7 signal you trust (sales-call mentions, customer references). Do not tune them in the first month or you're tuning to noise.

## What this doesn't measure

Read this before you present the leaderboard to anyone. The funnel measures **correlated activity** well. It does not measure **causal impact**, and pretending otherwise is how the program loses credibility the first time someone pushes on the numbers.


| Gap                                                                                                                                                 | Why it matters                                                                                         | Severity                                                         |
| --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| **No counterfactual.** We track "signed up after seeing content X," never "signed up because of content X."                                         | Someone who was going to sign up anyway can pass through your UTM and inflate every metric downstream. | High. Structural.                                                |
| **Slow-burn conversion is invisible.** A blog seeds a mental model, the developer converts four months later on a new device with no referrer.      | The best educational content works on this timescale. The weekly CSV cannot see it.                    | High for evergreen content, low for launches.                    |
| **Signup is not the same as a good user.** The cohort could sign up and bounce.                                                                     | Content that attracts skimmers can outscore content that attracts serious builders.                    | Medium. Fixable by weighting Day-30 return heavily in the score. |
| **Attribution decay.** UTM sticky cookies expire at 30 days, on device switch, on cookie clear. Deep converters often violate all three.            | You lose exactly the cohort you most want to see.                                                      | Medium-high. Structural to the web.                              |
| **Brand lift and shaped thinking.** "I read your post six months ago" showing up in a sales call is the truest signal, and it is not in the funnel. | Amplification (Stage 7) tries to capture this, but it is manual and lossy.                             | High, and mostly unmeasurable at DevRel scale.                   |
| **Resonance score weights are guesses.** `tech_comments × 3` vs `× 30` is opinion until validated against actual downstream outcomes.               | For the first three months, rankings will be noisy. Do not act on them yet.                            | Medium. Self-corrects with data.                                 |


### The single biggest blind spot

No counterfactual. Everything in this funnel is "content shipped, thing happened." Even with perfect instrumentation you cannot distinguish content that caused adoption from content that surfed alongside adoption that was going to happen anyway. Real causal measurement requires either a control group (some cohort deliberately gets no content) or a matched-pair analysis (compare adoption curves of users who saw content X against statistically similar users who did not). Neither is trivial and both are politically hard.

### How to close the gap without a research budget

Four cheap additions that push the funnel closer to real impact measurement:

1. **Quarterly qualitative pass.** Read comments, DMs, and sales-call quotes referencing your content. Pick one "story of the quarter" — a named user whose behavior changed. This is what the funnel cannot compute, and it is often the single most persuasive number in a review.
2. **Brand-lift micro-survey at signup.** One free-text question: "How did you first hear about Postman AI Engineer?" Ten answers a month beats any dashboard for surfacing content that shaped a decision months earlier.
3. **One holdout experiment per year.** Withhold one substantial piece from one segment (e.g., do not send it to the newsletter list) and compare adoption curves afterward. Painful; informative.
4. **Correlate the resonance score to Stage 6 monthly.** Once you have three months of data, check whether high-resonance pieces actually produced higher Day-30 retention cohorts. If not, retune the weights, or throw the score out and pick different signals.

### How to talk about the funnel

Use this funnel to **prioritize and rank**, not to **prove causation**. When someone asks "which content drove adoption," the honest answer is "these five pieces correlate strongly with adoption; here is the qualitative evidence; here is what we still cannot measure." That posture holds up under scrutiny. Overclaiming does not.

## Volume-trap red flags

Signals you are shipping to hit a number instead of to move users. Any of these appearing consistently means the funnel is not being used to make decisions.

1. **Ship cadence is fixed regardless of what performed.** You publish 2 things a week no matter what. Stage 1 becomes the KPI.
2. **You report averages across content types.** One breakout video hides ten misses. Break out top / median / bottom, always.
3. **Every CTA links to the same URL with no UTM.** You have no way to attribute Stage 4 onward. This is the #1 killer of the funnel.
4. **Vanity metrics reported in isolation.** Impressions, views, subscribers, or followers on their own tell you nothing. The funnel treats impressions and views as *inputs to CTR and watch/read time*, not as ends. If a deck shows "1M impressions" without the CTR alongside it, that's the vanity trap.
5. **No content ever gets retired or reformatted.** Winning use cases do not get pushed harder; losing ones do not get pulled.

## Setup checklist (what to instrument this month)

Cheap version, since product and marketing will not build this for us. The list is ordered so early items unblock later ones.

**Resonance data sources** (fills the Stage 2 and Stage 3 columns in the scorecard):

- [ ] **YouTube Analytics API + channel manager access.** Wires impressions, CTR, watch time, retention, repeat viewers, and shares for every video row. Requires enabling the Analytics API, an OAuth 2.0 client with a refresh token, AND read access to youtube.com/postman granted by the channel owner. See "YouTube data sources" section above for the 4-step path. Longest-lead item because of the channel-permission ask; start it first.
- [ ] **GA4 property with an export.** Blog page views, average engagement time, and returning-user % all come from GA4. Confirm the blog is measured in GA4 and enable an export (BigQuery, or a scheduled Looker Studio pull) so the metrics script can read it. Without this, the blog side of every resonance column stays blank.
- [ ] **Google Search Console linked.** GSC is the only source of search impressions and search CTR for blog posts. Verify the blog.postman.com property is claimed by DevRel and connect it via the Search Analytics API.
- [ ] **Scroll-depth event on every blog post.** Fire a GA4 event when the reader scrolls past the end of the article. This is what turns "views" into "completion %" for the blog side and makes it comparable to a YouTube retention curve.
- [ ] **YouTube chapters on every video.** Retention curves are useless without chapters — you cannot see which section lost people.

**Attribution / downstream** (fills Stages 4-6):

- [ ] **UTM taxonomy.** Every CTA in a video description or blog uses `utm_source=devrel&utm_medium={blog|youtube|livestream}&utm_campaign={product}&utm_content={slug}`. One convention, no exceptions.
- [ ] **Product event with `content_source`.** Whoever owns signup / first-run events adds a single string field populated from the UTM (via sticky cookie). This is the one product ask you have to win.

**Ongoing discipline:**

- [ ] **Ask a question at the end of every piece.** Comments are the free resonance signal. If you do not prompt, you do not get them.
- [ ] **Quarterly review.** Sort the scorecard by resonance score. Kill the bottom quartile of formats. Double down on the top quartile's shape (topic, length, hook).

## Cadence

- **Weekly (15 min).** Run `/devrel-skills:content-metrics` in Claude Code. It pulls the past week's ships, drafts a short commentary on outliers and trends, and posts a digest to the team Slack channel. Cheap, kept fresh.
- **Monthly (1 hr).** Fill Stages 4-6 from product telemetry. Look at the resonance-score leaderboard and take one action from it (kill, reformat, or amplify).
- **Quarterly (half day).** Kill / keep decisions. What topics won? What formats? What CTAs converted? Reallocate the ship pipeline based on the answer, not the calendar.

## Related files

- **`/devrel-skills:content-metrics`** (in `skills/content-metrics/`) is the human-triggered weekly review. It pulls WordPress + YouTube stats, drafts commentary on outliers and trends, and posts a digest to Slack.
- `skills/content-metrics/references/pull-metrics.py` is the underlying pull + post script. It can also be run directly if you want to skip the LLM commentary step: `python3 skills/content-metrics/references/pull-metrics.py --days 7 --slack`.
- `content-metrics/` holds the weekly CSV snapshots. Diff them week over week to see which pieces are still growing.

### Slack setup (one-time)

1. Go to [api.slack.com/apps](https://api.slack.com/apps), create an app (or open an existing one owned by the DevRel team).
2. Enable **Incoming Webhooks** and click **Add New Webhook to Workspace**. Pick your team channel.
3. Copy the webhook URL (`https://hooks.slack.com/services/T.../B.../...`) and add it to `~/.claude/settings.json`:

   ```json
   "env": {
     "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/T.../B.../..."
   }
   ```

4. Test the raw script: `python3 skills/content-metrics/references/pull-metrics.py --days 7 --slack`. If the webhook is wrong, the script fails loudly (by design).

