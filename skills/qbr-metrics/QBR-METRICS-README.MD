# qbr-metrics

Quarterly business review metrics for DevRel content and community. Given a date range, the skill reports blog, video, audience and Common Room numbers, each with the percent change against the previous period, and renders them as a Postman-branded report with line charts.

## Status

| Piece | State |
|---|---|
| `SKILL.md` and the pull and report scripts | Built. First run completed for Q3 2026 against Q2 2026 |
| `references/youtube-oauth-setup.py` (YouTube OAuth helper) | Built and verified against the Postman channel |
| Blog (WordPress and Jetpack), YouTube, Luma, Common Room pulls | Built and run end to end |
| Owned community metrics | Placeholder, waiting on an MCP from the team |
| Quarter-at-a-glance stoplight, white theme | Built. Status is rule-based and overridable (see below) |
| Meetup sheet (ratings, cost), accounts and industry, topics, news overlay | Built and in the Q3 2026 report |
| Release and industry-news overlay | Research is done by Claude per run (Slack `#product-updates` and web search) and saved to `context.json`; not scripted |
| Common Room period-over-period change | First run saved the baseline; the next run shows change |

Everything below marked "verified" was checked against the live services. Anything else is the design, not a tested result.

## Output: a PDF in chapters

The main deliverable is `report.pdf` (Letter, with page numbers), built by printing `report-print.html` with headless Chrome (`run-qbr.py` finds Chrome, or set `CHROME_PATH`; without Chrome the PDF is skipped and the HTML report still builds). `report.html` is the same content for the screen, with the detail tables collapsed. Each chapter starts on its own page and the report opens with a contents page: Summary, Content, Events and meetups, Channels, Accounts and community, Context, Where we are going, and Limits and next tests. Inside every section the order is the numbers, then the insights for that section, then the recommendation. Insights are written once in `insights.md` under headings that map to sections (Are we amplifying the content, Paid vs organic, Topics style and length, News releases and campaigns, Meetups, New channels beyond Luma, Newsletters, Accounts influenced, Not covered); `build-report.py` splits the file on those headings and places each block with its section, so keep the headings. A slide deck was tried and dropped: it compressed the insights and recommendations too much.

### Google Drive copy

After the PDF is built, `run-qbr.py` copies it to the Drive folder **QBRs** (My Drive) as `devrel-qbr-{start}_to_{end}.pdf`, for example `devrel-qbr-2026-08-01_to_2026-10-31.pdf`. `upload-drive.py` does it. The target is `DRIVE_QBR_FOLDER_ID` (default `1zJp-zA3Z8ABa3v3t90zuxqQ2ivd4ABRe`). A file with the same name is replaced in place, so a rebuild never creates a duplicate. Skip the copy with `--no-drive` or `DRIVE_QBR_FOLDER_ID=off`. A failed copy never fails the run; the runner prints the reason, and the message names the file and link when it works.

**Method 1, preferred: Google Drive for Desktop.** If the folder is mounted on this Mac, the PDF is copied into it and Drive for Desktop uploads it as the signed-in person. No credentials are involved. The folder is found by its Drive ID, which Drive for Desktop keeps as the extended attribute `com.google.drivefs.item-id#S` on every synced item, so renaming or moving the folder does not break it. Set `DRIVE_QBR_LOCAL_DIR` to point at a folder directly. Drive for Desktop must be running for the upload to complete; the copy itself is instant.

**Method 2, fallback: the Google service account** in `GOOGLE_APPLICATION_CREDENTIALS` (`devrel-skills@gen-lang-client-0730526528.iam.gserviceaccount.com`), used when the folder is not mounted. It does not work today, for two Google rules: a service account has no storage quota, so it can only write inside a Shared Drive it is a member of, and the QBRs folder is in My Drive, where a service account cannot write, and the alternative DeveloperRelations shared drive (folder `1rJ7ysQLIGkT06uCaHsgJxkLv041VlWI3`) blocks members from outside Postman, which includes any service account (the Share dialog shows "This shared drive's settings prevent sharing outside Postman" and the account stays invisible to the API). A Workspace admin would have to allow it. 

### Where we are going (written by the team)

The chapter shows `direction.md` in the output folder, exactly as the team writes it: trends, programs and bets, targets, asks and decisions, risks. **The skill never drafts or fills this file.** It asks how you want to provide it, in one of three ways: point it to a file you already wrote (`run-qbr.py … --direction=PATH` copies it in, keeping any existing text as `direction.previous.md`), answer five questions section by section (your answers are recorded word for word), or write it in the template and say when it is saved. When an earlier period has a `direction.md` with text (found with `run-qbr.py … --find-previous-direction`), a fourth option reviews it first: it is shown as written, you record how it went (kept word for word under "Review of last period"), and for each section you choose carry forward as written (labeled "Carried forward from …" in the report), write a new version, or drop it. Nothing is carried forward without that choice. The question comes right after the date range, and again at the end of the run if the file is still empty. If it is missing, `run-qbr.py` creates an empty template whose comments are not printed, and never overwrites an existing file. Headings left empty are skipped, and the chapter is left out of the report until there is text. Markdown supports bold, bullets and pipe tables, and a line `Status: DRAFT` adds a draft banner. Copy last quarter's file as a starting point if useful.

## Periods and the fiscal calendar

The skill always asks which period to cover: a month, a week or a quarter. Quarters follow the fiscal calendar: Q1 Feb 1 to Apr 30, Q2 May 1 to Jul 31, Q3 Aug 1 to Oct 31, Q4 Nov 1 to Jan 31. The fiscal year is named for the year it ends in (FY27 is Feb 2026 to Jan 2027), which matches the FY labels in the meetup sheet. `run-qbr.py` accepts `FY27-Q3`, `2026-09` (a month), `2026-W41` (an ISO week, Monday to Sunday) or two dates. A bare `Q3` is rejected because it needs a fiscal year. Charts use 7-day buckets, or daily points for a period of 14 days or less. Each pull records the exact windows in `period.json`, so a later `--rebuild` always matches the data. Month and week reports are small samples, and Common Room counts remain as of the run date.

## What the report covers

| Section | Metrics |
|---|---|
| Blog | Posts published, total views, views per post, top posts, weekly views series |
| YouTube long-form | Videos published, views, watch time, average view duration, subscribers gained |
| YouTube Shorts | Same metrics, reported separately |
| Shorts vs long-form | Side-by-side comparison chart (see below) |
| Trend analysis and insights | What is driving views: topic, length, format, traffic source, and overlap with news and releases (see below) |
| Audience | YouTube subscribers (net gained, total), Luma calendar contacts (net gained, total) |
| Quarter at a glance | Stoplight table at the top: Developers Reached, Accounts influenced, Community Engagement Rate, Blogs, Video, each with a status and notes |
| Luma events | Events held, registrations, attendance, events by city and country, new subscribers, new corporate accounts (proxy) |
| Meetup ratings and cost | Average rating (sheet column U), spend (S), cost per attendee (T), by region, event table |
| Accounts and industry | Accounts influenced from event attendees, Tier 1 share, economic buyer share, industry breakdown |
| Topics and content style | Blog and video medians by topic and style, current vs previous period |
| Releases and news | Numbered markers on the weekly charts, with a table of Postman releases, industry news and paid campaigns |
| Common Room | Developers influenced, organizations influenced, % economic buyers, overall sentiment |
| Owned community | Placeholder. Metrics for Postman-owned community channels, to come from an MCP not yet connected (see Common Room section) |

Every metric shows the current period, the previous period, and the percent change. The previous period depends on the period type: a fiscal quarter compares with the prior fiscal quarter, a calendar month with the prior month, a 7-day week with the prior 7 days, and any other range with the same-length window ending the day before the start. If the previous value is zero, the change shows `n/a`. A blank cell means the source is not connected. A zero means the source is connected and the count is zero.

### Paid vs organic

Paid and organic are reported separately in every section where the source data allows it. Totals are always shown too, so nothing is hidden. A section where the split is not possible says so on the tile.

| Section | Split | How | Verified |
|---|---|---|---|
| YouTube views and watch minutes, total and per format | Yes | Analytics `insightTrafficSourceType`: `ADVERTISING` is paid, everything else is organic. Per format, query by source with `filters=creatorContentType==shorts` (or `videoOnDemand`) | Yes, Q3 2026 |
| YouTube per video | Yes, one query per video | `filters=video==ID` with source as the dimension. A single query across all videos is rejected as unsupported, so the skill loops over the period's videos | Yes, on one video |
| YouTube paid detail | Yes | `insightTrafficSourceDetail` with the `ADVERTISING` filter names the ad format, for example TrueView in-stream and Homepage Video Ad | Yes |
| YouTube subscribers gained | **No** | `subscribersGained` is rejected with a source dimension, so subscribers are shown as a total only | Yes (rejected) |
| Blog views | **No** | Jetpack UTM stats return 403 because the blog's plan does not allow them, and Jetpack referrers do not identify paid clicks. See below | Yes (403) |

**Q3 2026 example, YouTube views:**

| | Total | Paid | Organic | Paid share |
|---|---|---|---|---|
| Shorts | 470,324 | 445,738 | 24,586 | 95% |
| Long-form | 1,241,221 | 1,066,180 | 175,041 | 86% |

Organic is total minus paid. Paid watch minutes were 84,591 of 101,472 for Shorts. Average view duration is recomputed per group from minutes and views, not subtracted.

**Blog paid traffic is not measurable today.** Two options to close the gap, either of which the team can choose:
1. Keep a short list of promoted content in `references/paid-content.json` (blog URLs and video IDs, with campaign dates and spend if known). The report then labels those pieces "promoted" and separates them. This is manual but works for both blog and video, and also covers promotion that does not show up as `ADVERTISING` (paid social, newsletter sponsorships).
2. Use UTM tagging on paid blog links and read it from another source such as GA4 or the product analytics Looker Look. This is out of scope for now.

Until one of these is in place, blog numbers are labeled "paid not tracked", and are not assumed organic.

### Shorts vs long-form chart

A dedicated comparison of how the two formats performed in the period:

- **Weekly views line chart** with one line for Shorts and one for long-form, so shifts in mix are visible over time. The previous period is drawn as a dashed line for each format.
- **Side-by-side tiles** for views, watch minutes, average view duration, subscribers gained, views per video published, and each format's share of total views. Each tile shows both formats and the percent change against the previous period. Views and watch minutes are drawn as stacked paid and organic segments. The line chart plots organic views as solid lines and paid views as lighter lines, so a campaign shows up as a separate band, not as a change in the format's performance.
- Live streams are a third `creatorContentType` bucket and are tiny (about 1,800 views in Q3 2026). They are excluded from the comparison and noted in a footnote.

The split uses the Analytics API `creatorContentType` dimension, with values `videoOnDemand` (long-form), `shorts` and `liveStream`. Verified for Q3 2026: long-form 1,241,221 views and 601,239 watch minutes, Shorts 470,324 views and 101,472 watch minutes. Per-video lists use the same value as a filter, for example `filters=creatorContentType==shorts`, which is also how videos published per format are counted.

### Trend analysis and insights

A closing section that asks what is driving views, and where the answer is weak, says so. Scripts compute the evidence. Claude writes the interpretation.

**Step 1: separate paid from organic.** This comes first because it changes every conclusion. In Q3 2026, `ADVERTISING` was 1,511,918 of the roughly 1.7M YouTube views (YT_SEARCH was 115,485, EXT_URL 42,825, SUBSCRIBER 9,890). The Aug 13–18 and Aug 27 spikes trace to Shorts from a paid 15-second campaign published Aug 11–12. All driver analysis below runs on **organic views only**, using the Analytics `insightTrafficSourceType` dimension. Paid views are reported in their own tile, not mixed in. Per-video organic views need one Analytics query per video (see Paid vs organic). Blog traffic cannot be split into paid and organic with current access, so blog driver analysis uses total views and says so, unless a `paid-content.json` list is provided.

**Step 2: tag every piece with attributes.** One record per blog post and per video:

| Attribute | Blog | Video |
|---|---|---|
| Length | Word count from the post body (WP REST) | Duration from the Data API (`contentDetails.duration`) |
| Format | Post vs video vs Short, plus content style (tutorial, announcement, comparison, opinion) | Same, with `creatorContentType` for Shorts vs long-form |
| Topic | WP categories and tags, then Claude classifies by title and body into a fixed topic list (for example MCP, agents, testing, API design, release) | Claude classifies from title and description |
| Publish date, day of week | WP `date` | Data API `publishedAt` |
| Organic views, watch time | Jetpack `/post/{id}` | Analytics, filtered to non-ADVERTISING sources |

YouTube tags are sparse on this channel (the sampled videos have two each), so topic comes from titles and descriptions, not tags. The topic list is fixed in `SKILL.md` so labels stay consistent between quarters.

**Step 3: compare groups.** Median organic views per piece by topic, by length bucket, by format, and by publish weekday, for the current and previous period. Medians, not averages, because a few outliers dominate. A group with fewer than 3 pieces is reported as "too few to compare", not ranked. The report lists the top and bottom performers with their attributes so a reader can check the pattern by eye.

**Step 4: overlay events on the line charts.** The weekly views chart gets markers for things that happened at the same time:

| Overlay | Source |
|---|---|
| Postman releases and product updates | Release notes and the product-updates Slack channel (the same inputs as `blog-prod-updates`) |
| Postman events | Luma calendar events (`luma-stats` pipeline) |
| Industry news and launches | Web search of the period for major AI and API launches and conference dates |
| Paid campaigns | Detected from the `ADVERTISING` traffic spikes in Step 1 |

Industry news is a judgment call, not a data feed. It is labeled as such, and each marker links to its source.

**Step 5: write the insights.** Claude writes a short section: three to five findings, each stating the evidence (numbers and the pieces involved), a confidence level, and what to try next. Rules:

- Overlap is not cause. A spike that coincides with a release is reported as "coincided with", never "was caused by", unless traffic-source data supports it (for example a jump in referrals from a launch post).
- Small samples are named as small.
- Anything the data cannot answer is listed as an open question, not guessed.
- Blank means no data, zero means a real zero, same as the rest of the report.

Example of the intended style, not real output: "Organic Shorts median 340 views (n=14) vs long-form median 910 (n=9), up 12% vs Q2. The 6 pieces on MCP averaged 2.1x the median of other topics, but 4 of them shipped the week of a major model release, so topic and timing cannot be separated yet."

Not yet verified: Jetpack referrer and search-term endpoints return data, but their shape for per-post attribution needs a script pass. Whether the Slack product-updates history reaches back far enough for prior quarters is untested.

Charts are inline SVG using the Postman brand tokens from `skills/newsletter-linkedininsights/references/cover-template.html`: a white page background (easier to read than the dark brand theme, per the team), `#FF6C37` for the current period, a dashed grey line for the previous period, a darker green for positive deltas, Space Grotesk and JetBrains Mono. The stoplight status colors follow the team's status note (bright green, amber, red, grey).

### Quarter at a glance (stoplight)

The first section is a table in the style of the team's status note: KPI / Activity, Status, Notes. The five KPIs and how each status is calculated:

| KPI | Output signal (left of a gradient) | Result signal (right) |
|---|---|---|
| Developers Reached | Luma events held vs previous period | Luma registrations vs previous period |
| Accounts influenced | none | Growth in total corporate accounts reached through Luma vs previous period (proxy). The change in new accounts is in the note, not the color, because it falls naturally as the base grows |
| Community Engagement Rate | none | none; shows "Not connected" until the owned community MCP is connected |
| Blogs | Posts published | Blog views |
| Video | DevRel videos published (excludes paid ad creatives and localized duplicates) | Organic views (paid ad views are not an outcome) |

**Principle: score what DevRel controls.** The status covers events and content DevRel creates and the organic results they earn. Paid media (ad views, ad creatives) is shown beside the row for context and is never scored, so a change in ad spend cannot turn a DevRel status red or green. The blog cannot be split into paid and organic, so blog views are total views until a promoted-content list or UTM data exists.

Bands, applied to the percent change against the previous period. **Output:** green at or above last period, amber down to -20%, red below that. **Result:** green at +5% or better, amber from -20% to +5%, red at -20% or worse. When output and result agree the cell is solid; when they differ it is a left-to-right gradient from output to result, like the example note. No data shows grey. These are mechanical rules, not judgment. To override a row, put `{"rows": {"Blogs": {"status": ["green", "amber"], "note": "..."}}}` in `stoplight.json` in the output folder. Notes are generated from the data and can be replaced the same way.

### Channels (Luma, YouTube Live, LinkedIn)

A Channels table shows event and live channels side by side with the same measures and the change against the previous period. **YouTube Live** is automatic: live streams that started in the period (a video counts only if YouTube Analytics classes it as a live stream, because premieres carry live-streaming details but are not live), views on live content (which include replays and older archives), watch time and subscribers gained. **LinkedIn Live webinars and the LinkedIn newsletter** sit behind a LinkedIn login, so their numbers come from `channels-input.json` in the output folder (see the file for the format). A field left out shows as n/a, never zero. Webinars are produced in Riverside and streamed to both YouTube and LinkedIn, so the two audiences can overlap and are not added together. The public newsletter page shows editions and comments only. Common Room has no webinar or LinkedIn Live activity for the periods checked.

**Newsletters.** Mailchimp is automatic: `pull-mailchimp.py` reads sent campaigns through the Marketing API (`MAILCHIMP_API_KEY`, which ends in the data center, for example `-us20`; the key has full account access and is only used for read calls) and their reports (emails sent, unique opens and clickers, unsubscribes, bounces). Optional scope settings: `MAILCHIMP_AUDIENCE_ID`, `MAILCHIMP_TITLE_CONTAINS`, and `MAILCHIMP_MIN_RECIPIENTS` (default 100; smaller sends are treated as tests). Open rates are inflated by Apple Mail Privacy Protection, so clicks lead. Mailchimp history is complete, so a period with no sends is a real zero. The account had sent nothing before Sep 29, 2026, when a test went out; real newsletters began Oct 1. Newsletters moved from Luma to Mailchimp in October 2026, so Luma newsletters are not part of the report and Mailchimp has no comparable previous period before Oct 1.

**LinkedIn (scoped to DevRel content).** The LinkedIn numbers cover only three kinds of content: reshared blog posts, newsletter editions and webinars. Page-wide totals, ads (dark posts) and every other organic post are left out on purpose. `pull-linkedin.py` reads the page through the LinkedIn Community Management API with an organization-admin token, read-only. It uses `LINKEDIN_ACCESS_TOKEN` if set, otherwise the token file named by `LINKEDIN_TOKEN_FILE`, which defaults to the state file of the `agent-team-socialmedia` app (`~/Code/agent-teams/agent-team-socialmedia/state/linkedin_oauth.json`, same organization, valid until 2027-01-01 at the time of writing). The token is read, never printed or copied. Only organic posts are considered (`feedDistribution` is not NONE). A post is a **blog reshare** if it links to blog.postman.com, directly or through a lnkd.in short link; a **newsletter** post if it references a newsletter edition (`urn:li:linkedInArticle`) or names the Dev Digest; a **webinar** post if it references a live video or event, or announces a webinar or live session, plus each LinkedIn Live event's announcement post. The rules are keyword based (see `classify()` in the script), so check the top-post tables. Per-post statistics (impressions, unique impressions, clicks, reactions, comments, shares) come from `organizationalEntityShareStatistics`, and LinkedIn Live events from the Events API (`liveVideo` format).

**LinkedIn limits.** LinkedIn lists organic posts only from when the social agent began posting through the API (Aug 24, 2026 at the time of writing), so earlier periods have no per-post data and show n/a, not zero. A blog post shared with the link only in a comment or image is not identified, so reshares are a floor. The API does not return event registrants or attendees (404), live viewer counts, or newsletter subscribers and article views; those go in `channels-input.json`. If the token is missing or expires, run `linkedin-oauth-setup.py` after registering `http://localhost:8765/callback` as a redirect URL in the LinkedIn app.

### Reach per piece and where paid views go

The stoplight scores growth in totals, so it cannot say whether content is being amplified enough. Two sections address that directly. **Reach per piece** shows the median views per blog post and organic views per DevRel video, how much of the total sits in the top 3 pieces, how many pieces got under 100 views, the typical video's reach as a share of subscribers, the share of organic YouTube views, and the share of views that go to content published in the period rather than the back catalog. **Where paid and organic views go** takes the most-viewed videos in the period (any publish date), splits each into paid and organic views with one Analytics query per video, groups them by topic with the same keyword rules as the topic analysis, and lists the top videos. Only YouTube ads are visible, so promotion on other platforms is not counted. The report cannot measure amplification effort (what was done to distribute each piece); that needs a distribution checklist kept by the team.

### Topics, news and releases

`classify-topics.py` tags each blog post and video with one topic and one style using keyword rules on the title (edit `TOPICS` and `STYLES` in the script to change them) and compares medians between periods. Blog metric: views in the period. Video metric: organic views. Paid ad creatives, localized duplicates and event recordings are excluded from the video comparisons, and a group of fewer than 3 pieces is not ranked.

The release and news overlay is research Claude does on each run and saves to `context.json`: Postman releases from the `#product-updates` Slack channel (externally available items only), industry launches from web search, and paid campaign dates from YouTube. Each event gets a numbered marker on the weekly charts and a row in the context table. Markers show timing, not cause. Industry items come from third-party roundups and are not verified against primary sources, and the report says so. The insights test whether weeks with a release or news item differ in traffic from other weeks (Q3 2026: they did not move blog views).

## Data sources

### Blog views: Jetpack Stats

WordPress core has no view counts. blog.postman.com runs Jetpack Stats, and the existing `WP_USERNAME` and `WP_APP_PASSWORD` already work against it. Site ID is `199676833`. No GA4 is needed.

Verified endpoints, under `https://blog.postman.com/wp-json/jetpack/v4/stats-app/sites/199676833/stats`:

- `/visits?unit=week&quantity=N&date=YYYY-MM-DD` returns weekly views and visitors
- `/top-posts?period=day&date=YYYY-MM-DD&num=N` returns views per post
- `/post/{post_id}` returns the daily series for one post

`/summary` returns 403 for this account, so it is not used. Post counts come from the WordPress REST API (`/wp/v2/posts`), as in `blog-wordpress-stats`.

### YouTube

Uses the YouTube Data API (titles, subscriber total) and the YouTube Analytics API (views, watch time, average view duration, subscribers gained and lost, and the long-form vs Shorts split). Per-day and per-video queries are supported.

**Impressions and click-through rate are not available.** The Analytics API rejected `videoThumbnailImpressions` and `videoThumbnailImpressionsClickRate` as unsupported queries at the channel total, by day, by video, and by content type. These numbers exist in YouTube Studio only. I have not checked whether the separate YouTube Reporting API exposes them. Until that is resolved, the report shows impressions and CTR as "not available" with the reason. The workaround is a manual Studio export each quarter, which the skill can read if you drop the CSV in a known location.

**Why not the service account?** The Google service account used by `meetup-calendar` for Sheets does not work here. The Data API is disabled in that project, and the Analytics API returns 403 for the Postman channel. YouTube's APIs do not support service accounts for channel analytics, so a user OAuth consent is required once.

### Luma

The Luma API (`https://public-api.luma.com`, header `x-luma-api-key`) has no calendar subscriber endpoint, and neither does the Luma MCP. The closest data is `GET /v1/calendars/contacts/list`, the calendar's people list. The report labels this "Luma calendar contacts", not "subscribers". Each contact has a `created_at` timestamp, so total and net growth in a period are computed from that, and no snapshot is needed.

Luma metrics in the report:

| Metric | Source | Verified |
|---|---|---|
| Events held | `GET /v1/calendars/events/list` filtered by `start_at` (Q3 2026: 11 events) | Yes |
| Registrations, waitlist, attendance, attendance rate | `GET /v1/events/guests/list` per event, same logic as `luma-stats` | Yes (existing skill) |
| Events by city and country | `geo_address_json` on each event (`city`, `region`, `country`). Online events have none and are reported as "online" using `location_type`. In Q3 2026 all 11 events were in person: New York, Milano, Mumbai, Los Angeles, San Francisco, Copenhagen and others | Yes |
| Calendar contacts, net new | `created_at` on `calendars/contacts/list` | Yes |

**Feedback ratings come from the meetup sheet, not Luma.** The Luma API has no rating or survey data (the only "feedback" field is `feedback_email`, the post-event email setting). The team records an average rating per event in column U ("Rating (out of 5)") of the "Meetups & User Group Cal" tab of the FY27 Developer Meetups sheet, with Cost in column S and Cost per attendee in column T. `pull-sheet.py` reads that tab with the same service account as `meetup-calendar` (`GOOGLE_APPLICATION_CREDENTIALS`, `MEETUP_SHEET_ID`). Events are matched to the period by Start Date. Blank cells mean not recorded and are excluded, never counted as zero. A `$0` cost is kept as zero and reported as a separate count, and cost per attendee uses only events with a cost above $0 and attendance recorded. The sheet's attendee counts differ from Luma check-ins, so the two sections will not match exactly. The same tab has a monthly "Luma Subscribers" table, which tracks the calendar contact count.

**New corporate accounts via Luma (proxy).** `pull-luma.py` counts corporate (non free-mail) email domains whose earliest calendar contact was created in the period. It covers Luma only, so it excludes APIdays and other events, and it cannot see people who register with a personal address.

**Attendee geography is not available either.** Guest records have no location, so the geographic breakdown is by event location only, not by where attendees live.

Existing config: `LUMA_API_KEY` and `LUMA_CALENDAR_ID`, shared with `luma-stats` and `meetup-calendar`.

### Common Room

Uses the `cr` CLI (v0.4.0), authenticated through `COMMONROOM_API_TOKEN`. Metrics are defined from three segments in the Postman community (`3391`). In the CLI, segment IDs take an `s_` prefix.

| Metric | Definition | Segment |
|---|---|---|
| Developers influenced | Contacts in the segment | `s_4163088` Event - All - Attended |
| Organizations influenced | Distinct organizations among the contacts in the segment | `s_4342069` Tier 1 Accounts - Developer Engagement - Attended |
| % economic buyers | Contacts in both `s_4163088` and `s_4196221`, divided by contacts in `s_4163088` | `s_4196221` Economic Buyers - Global |
| Overall sentiment | Room Overview sentiment | `reports/room-overview/overview` |

#### Accounts influenced and industry

Accounts influenced are the distinct companies among contacts in the all-events-attended segment (`s_4163088`), taken from each contact's current employer. About 73% of attendee contacts have a company, so the count is a floor. Tier 1 share is the Tier 1 segment's distinct companies divided by accounts influenced. Industry comes from the employer's industry label and is grouped into broad categories in `qbrlib.py` (`INDUSTRY_GROUPS`; edit it to change the groups, then `--rebuild`, no re-pull needed because the pull saves the raw labels). One count per account. Accounts with no industry show as "Industry not recorded". Counts are as of the run date, because segments hold current members.

#### Owned community metrics (placeholder: waiting on an MCP)

**Placeholder.** Owned community metrics will come from an MCP server that is being provided separately. Until it is connected, the report shows an "Owned community" section marked "not connected", and no numbers. The metric list, the MCP name and its tools, and any credentials go here once known. The Common Room analysis below is background on why the saved report could not be used, and the candidate metrics are a fallback only if the MCP does not cover them.

The team wants owned-community numbers from the Common Room saved report "Community Room" (report 91, 12-week interval, community `3391`). **Saved reports are not reachable through the CLI or API.** There is no report command or object type in `cr`, and `GET /api/v2/reports`, `/saved-reports` and `/saved-reports/91` all return 404. So the skill cannot read that report, and what it contains is not yet known here. Nothing below should be treated as that report's metrics.

What the CLI can compute from underlying data. This is a proposal, untested, and only the provider list was verified:

| Candidate metric | How |
|---|---|
| Active community members | Distinct contacts with an Activity from an owned provider in the window |
| New community members | Contacts whose first owned-provider activity falls in the window |
| Posts, replies, reactions | Activity counts by activity type for those providers |
| Top contributors | Contacts ranked by activity count |
| Community sentiment | `ActivitySentiment` labels (Positive, Negative) on those activities |

Providers in this workspace that look like owned community: `Postman Community` and `Postman Japan Community`. Others seen: `postmanlabs`, `Reddit`, `Hacker News`, `Medium`, `YouTube`, `Connpass`, and event providers. Whether `postmanlabs` (probably GitHub) counts as owned is a decision for the team.

To pin this down, one of these is needed:
1. The list of metrics the saved report shows, with each definition (for example "active members = anyone with 1+ activity in 12 weeks").
2. An export of the report (CSV or screenshot), so the skill's numbers can be checked against it.
3. A decision to compute the candidate metrics above instead, with the report used only as a manual cross-check.

Because that report uses a 12-week window and the QBR uses arbitrary dates, the skill computes from raw activity for the QBR window. It will not reuse the report's numbers.

Things to know:

- **All three segments are contact segments**, including the Tier 1 one. "Organizations influenced" is computed from each contact's `currentCompany`, not read from a segment count.
- **Segments hold current members, not members at a point in time.** To compare against a previous period, the skill should filter on activity date if the API allows it, and also write a snapshot each run. Whether date filtering works is untested.
- **Sentiment is a UI report.** The API lists activity sentiment labels but no Room Overview aggregate. Options are to aggregate the labels over the window (may not match the UI number), or to enter the Room Overview number by hand. The report states which method was used.
- The CLI help does not document the `--filter` (LightFilter) syntax. Start from `cr catalog describe Contact`.

## Setup

All keys go in the `env` block of `.claude/settings.json` (gitignored) or `~/.claude/settings.json`.

| Variable | Used for | Status |
|---|---|---|
| `WP_USERNAME`, `WP_APP_PASSWORD` | WordPress and Jetpack | Existing |
| `LUMA_API_KEY`, `LUMA_CALENDAR_ID` | Luma | Existing |
| `COMMONROOM_API_TOKEN` | Common Room CLI | Set |
| `YT_OAUTH_CLIENT_ID`, `YT_OAUTH_CLIENT_SECRET` | YouTube OAuth client | Set |
| `YT_OAUTH_REFRESH_TOKEN` | YouTube Analytics access | Set and verified |
| `YT_CHANNEL_ID` | Optional override | Defaults to the Postman channel `UCocudCGVb3MmhWQ1aoIgUQw` |

### One-time YouTube OAuth consent

Needed once per person or machine that will run the skill, and again if the token is revoked.

1. **Enable the APIs.** In Google Cloud Console, enable **YouTube Data API v3** and **YouTube Analytics API** in the project that owns the OAuth client.
2. **Set the audience.** Under Google Auth Platform, open **Audience**. If the user type is **Internal**, only accounts in the project's Google Workspace organization can sign in, and anyone else sees "can only be used within its organization". Switch to **External**, then **Publish app**. If the app stays in Testing, refresh tokens expire after 7 days.
3. **Add the scopes.** Under **Data Access**, add `youtube.readonly` and `yt-analytics.readonly`.
4. **Create the client.** Under Credentials, create an OAuth client of type **Desktop app**. There is no redirect URI to set. The helper uses a random loopback port, which Desktop clients allow automatically. A Web application client will not work with the helper.
5. **Store the client ID and secret** as `YT_OAUTH_CLIENT_ID` and `YT_OAUTH_CLIENT_SECRET`.
6. **Run the helper:**
   ```bash
   python3 skills/qbr-metrics/references/youtube-oauth-setup.py
   ```
   Sign in with a Google account that has access to the Postman YouTube channel (Manager or higher is the safe choice). If the channel is a Brand Account, choose it in the account chooser. Google shows an "unverified app" warning because the app is not verified. Click **Advanced**, then **Go to DevRelSkills (unsafe)**. It is your own app.
7. **Copy the printed `YT_OAUTH_REFRESH_TOKEN` line** into the `env` block. The helper only prints it and never writes it to a file.
8. **Verify any time** with `python3 skills/qbr-metrics/references/youtube-oauth-setup.py --verify`. It checks which channel the token belongs to, the Data API subscriber count, and a 7-day Analytics query. It exits 0 if all pass and 2 if any fail.

Useful flags: `--no-browser` prints the consent URL instead of opening it.

The helper reads credentials from the real environment first, then from settings files in this order: `.claude/settings.local.json`, `.claude/settings.json`, `~/.claude/settings.local.json`, `~/.claude/settings.json`. This is needed because Claude Code only injects the `env` block into its own processes, so a script run from a plain terminal would not otherwise see it.

## Layout

```
skills/qbr-metrics/
  QBR-METRICS-README.MD
  SKILL.md
  references/
    run-qbr.py               runs all pulls in parallel, then builds the report
    qbrlib.py                shared helpers: periods, % change, weekly buckets, HTTP retry
    pull-wp.py               WordPress post count + Jetpack views
    pull-youtube.py          Data + Analytics APIs, long-form vs Shorts, paid vs organic
    pull-luma.py             events, registrations, attendance, geography, calendar contacts
    pull-commonroom.py       segment counts via cr
    build-report.py          merge, render HTML (inline SVG charts), Markdown, metrics.json
    session-cost.py          tokens and estimated cost of the Claude session, for the report footer
    pull-sheet.py            meetup sheet: ratings (U), cost (S), cost per attendee (T), Luma subscribers table
    classify-topics.py       topic and style tags, medians by group
    youtube-oauth-setup.py   one-time YouTube OAuth consent and verification
    pull-mailchimp.py        Mailchimp newsletter sends, opens, clicks and unsubscribes
    pull-linkedin.py         LinkedIn reshared blog posts, newsletter and webinar posts, plus LinkedIn Live events
    linkedin-oauth-setup.py  LinkedIn OAuth consent and API probe, only needed if the token is missing or expired
    snapshots.json           created on the first run (gitignored), for Common Room change figures
```

Files written per run into the output folder besides the raw pulls: `topics.json`, `context.json` (releases and news, written by Claude), `stoplight.json` (optional overrides), `channels-input.json` (LinkedIn numbers that cannot be pulled automatically), `insights.md` and `recommendations.json` (one short evidence-based paragraph per section, including `reach` and `paid_topics`, written by Claude and shown as a callout at the end of each section), `cost.json`.

Not built yet: `paid-content.json` (optional hand-kept list of promoted content for the blog gap).

Run it with `python3 skills/qbr-metrics/references/run-qbr.py START END`, or `--rebuild` to rebuild from existing raw data after editing `insights.md`. Output goes to `qbr-output/{start}_to_{end}/`: `report.pdf`, `report.html`, `report.md`, `metrics.json`, `insights.md`, `errors.json` and the `raw-*.json` pulls. `qbr-output/` is gitignored and listed in `CLAUDE.md`.

The report footer states the tokens and estimated spend of producing it. `session-cost.py` reads per-message token usage from the Claude Code session transcript and prices it at Claude API list prices for the model used (for `claude-sonnet-5-5`: $2.00 input, $10.00 output, $0.20 cache read, and cache writes at 1.25x for 5-minute or 2x for 1-hour entries, per the claude-api skill's price table cached 2026-09-25). Treat it as an estimate: it covers the main session only (no sub-agents), a subscription or enterprise plan may bill differently, and by default it counts the whole session including building the skill. Set `QBR_RUN_SINCE` to an ISO timestamp to count only a single run. The pull scripts themselves use no tokens. The first Q3 2026 report showed 17.8M tokens, about $6.08, mostly cache reads of the growing conversation.

A full run takes several minutes, mostly Luma (every calendar contact) and Common Room (every segment member).

Each source fails independently. A missing credential renders that section as "not connected" with the setup step, and the rest of the report still builds. WordPress is the only hard requirement.

The scripts fetch and compute. Claude writes a short, factual summary: biggest movers, one risk, one recommendation, with missing data stated plainly.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Helper says the keys are not set, but they are in `settings.json` | You ran it from a plain terminal. Update to the current helper, which reads settings files itself |
| `Error 401: invalid_client` | The client ID does not exist. Check the values are real: the ID ends in `.apps.googleusercontent.com`, the secret starts with `GOCSPX-`. Also confirm the client type is Desktop app |
| "Access blocked: ... can only be used within its organization" | Consent screen is Internal. Switch to External and publish (setup step 2) |
| "Google hasn't verified this app" | Expected. Advanced, then Go to the app |
| "Branding is not being shown to users" in Cloud Console | Harmless. It only affects the app name and logo on the consent screen |
| No refresh token returned | Revoke the app at https://myaccount.google.com/permissions and run the helper again |
| Token works but Analytics returns 403 | The signed-in account lacks access to the channel, or the token belongs to a personal channel. Rerun and pick the Postman Brand Account |
| Data API 403 "has not been used in project" | Enable YouTube Data API v3 in the project that owns the OAuth client |
| Refresh token stops working after about 7 days | App is still in Testing. Publish it and re-consent |
| Analytics 400 "query is not supported" for impressions or CTR | These metrics are not exposed by the Analytics API. See the YouTube section |
| Jetpack `/stats/utm/...` returns 403 "plan does not allow fetching UTM stats" | The blog's Jetpack plan excludes UTM stats. Use `paid-content.json` or another UTM source |
| Analytics 400 when combining `subscribersGained` with a traffic source, or `video` with a source dimension | Unsupported combinations. Query one video at a time, and show subscribers as a total only |
| Jetpack `/summary` returns 403 | Expected for this account. Use `/visits` and `/top-posts` |
| `cr` returns "Invalid segment id" | Use the `s_` prefix, for example `s_4163088` |

## Security

- `.claude/settings.json` is gitignored and untracked. It has been committed in the past, so check history before relying on that for old credentials. Rotate anything that was ever real.
- Never paste the OAuth secret or refresh token into chat, issues or commits.
- The helper requests read-only YouTube scopes only.
- Common Room and Luma tokens grant broader access than this skill needs. Keep them in settings files, not scripts.


## TL;DR and stoplight rules (added Nov 2026)

- `tldr.md` in the output folder holds a short bulleted executive summary written by Claude each run. It shows at the top of page 1, above the contents. It is skipped if the file is missing.
- Developers Reached is scored differently from content rows because the number of events is a planning choice. Fewer events is capped at amber (never red) on the output side, and the result side is judged on registrations per event together with new subscriber growth; if those two disagree, it is amber. A quarter with fewer events, steady per-event demand and slower subscriber growth therefore reads amber.

## Owned community (Discord dashboard MCP)

`pull-community.py` calls the `get_monthly_report` tool of the community dashboard MCP (`https://www.postman-community-dashboard.dev/api/mcp`, MCP over HTTP with a JSON-RPC `tools/call`; the Accept header must list both `application/json` and `text/event-stream`). Set `COMMUNITY_MCP_API_TOKEN` in the `env` block of your settings.json; the token is sent as a bearer header and never written to a file.

- **Periods:** the dashboard reports whole calendar months, so the pull uses the months fully inside the period. A fiscal quarter or a month works; a week or a range with no whole month is reported as not available, and the report says so.
- **Metrics:** joins, leaves, net new members, total members, active members (average of the monthly counts) and active rate, help topics and how many were answered, staff and bot replies, retention, event attendee roles granted, and Liftoff World Explorer cohort, starts and completions. Flows are summed over the months, total members is the month end.
- **Stoplight:** Community Engagement Rate is scored on active members and joins together (amber when they disagree), and is red whenever fewer than 1% of members are active in a month, because a percent change cannot see a level problem. Change the floor with `COMMUNITY_MIN_ACTIVE_RATE`. The help-topic answer rate is not scored: it only reflects 30 or so topics a quarter.
- **Liftoff and badges:** the section shows members who joined Liftoff in the period, how many started, badges earned, badge rate, finish rate of starters and the onboarding-link split. The dashboard has one badge (World Explorer), so badges earned equals completions; it has no total badges held and no breakdown by badge.
- **Limits:** the active rate is small (about 0.5% of members), so read it as a trend. "Members holding the Event Attendee role" is a current figure, not a historical one. The MCP has no sentiment measure.

## Liftoff totals (admin stats API)

`pull-liftoff.py` posts to `https://www.postman.com/liftoff/api/admin/stats/` (the trailing slash is required; without it the server answers 308 and a POST is not retried) with `LIFTOFF_ADMIN_API_TOKEN` as a bearer token. It sends the period plus a `compare` period, and the API's `to` date is exclusive, so the script sends the end date plus one day.

- **Metrics:** new signups, active users, badges earned (the API's `modulesCompleted`, one badge per module), steps completed, points earned, anonymous conversions and anonymous visitor conversions (names as the API returns them; the definitions are not documented here), weekly series, top modules by completions, and drop-offs per module with the worst step.
- **Campaigns:** the API has no campaign or UTM breakdown. The charts carry the release and event markers, and the insights compare signup and badge weeks with events and releases. That shows timing only, never cause. Adding a campaign or UTM capture at signup is the fix.
- **Relation to the Discord numbers:** the community dashboard follows only the World Explorer module for members who joined Discord. When the Liftoff pull works, the Liftoff section replaces that block in the community section.
- **Public Liftoff MCP:** `https://www.postman.com/liftoff/api/mcp/` needs no token and returns the module catalog only (17 modules, 5 paths), plus any active limited-time badge campaigns; it has no learner or badge counts.
