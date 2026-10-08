# Webinar Manager Templates

Fill every `{placeholder}` from `brief.md`. Never invent speakers, dates, or claims. Copy rules apply to everything below: no "supercharge", "unlock", "revolutionize", or "leverage", and no em dashes.

## Jira: parent task

- Project: `MKTG` (site `postmanlabs.atlassian.net`), issue type `Task`
- Parent epic: `MKTG-8442` (Technical Content)
- Summary: `[Webinar] {title} {M/D}`
- Due date: webinar date

Description:

```text
Webinar will be {M/D}. We produce it in Riverside and stream live to YouTube Live and LinkedIn Live.

{abstract, 2 to 4 sentences}

Luma event: {luma_url}
Speakers: {name (title)}, ...
```

## Jira: social promo card sub-task

- Issue type: `Sub-task`, parent is the task above
- Summary: `Social Promo Card`
- Labels: `creative`
- Assignee: always Jonathan Holt, Creative Team (account id `712020:9cde7faf-7906-4356-9914-39bd911dac81`)
- Due date: 3 weeks (21 days) before the webinar, or tomorrow if the webinar is less than 3 weeks away

Description:

```text
Please create a social promo card for the webinar below. Reuse the template from MKTG-11062 (inputs: speaker faces, title, description, date, time).

Title: {title}
Description: {one-sentence description}
Date and time: {date} {time} {timezone}
Speakers: {name (title)} (headshots attached or at {headshot_path_or_link})
Stream: YouTube Live and LinkedIn Live (produced in Riverside)
Sizes needed: 1080x1080 (LinkedIn) and 1600x900 (Twitter/X)
Registration link: {luma_url}
```

## Email: skeleton

File: `webinar-output/{slug}/email.md`

```markdown
# Email: {title}

**Subject options**
1. {plain, specific subject, under 60 characters}
2. {question or outcome-led option}
3. {speaker or date-led option}

**Preview text:** {under 90 characters}

**Summary line:** {one sentence: abstract summary + date + time and timezone}

**Card:** {card_path_or_"card pending"}

**Status:** draft

---

Hi {first_name},

{Hook: one or two sentences that name a specific situation the reader has been in. No greeting filler.}

{The problem: a short paragraph on why this is hard today and why it matters now. Concrete, from the brief.}

On {weekday, date} at {time} {timezone}, {speaker names} will {what they will do, concrete}. Here is what you will walk away with:

**{Takeaway 1 as an outcome}**
{One or two sentences: what they will show or explain, and what you can do with it afterward.}

**{Takeaway 2 as an outcome}**
{One or two sentences.}

**{Takeaway 3 as an outcome}**
{One or two sentences.}

**Who this is for**
{One sentence naming the roles and the situation, for example "API developers who ...".}

**Who is presenting**
- {Speaker name}, {title}: {one line on why they are the right person for this topic, from the brief}

**The details**
- When: {weekday, date}, {time} {timezone} ({duration})
- Where: online, streamed live on YouTube and LinkedIn
  - YouTube Live: {youtube_live_url or "link pending"}
  - LinkedIn Live: {linkedin_live_url or "link pending"}
- Cost: free

[Save your spot]({luma_url}?utm_source=email)

**If you want background first**
- Blog: [{blog title}]({url}): {one line on what it covers}
- Video: [{video title}]({youtube_url}): {one line on what it covers}

Can't make it live? Register anyway and we will send the recording.

{sign-off}

P.S. {One line: a question to bring, or a reason to register today.}
```

Body target is 250 to 400 words. Every paragraph must be specific to this webinar. Drop the "Cost: free" line if the brief does not say the event is free. Drop the P.S. if it would only repeat the CTA.

Related content order: the brief first, then posts found on blog.postman.com and videos on the Postman YouTube channel, newest first (at most 3 of each), then matching `blog-output/` posts. Link only URLs that a search or fetch actually returned and that match the topic. Omit a list when nothing relevant exists and say so in a note under the draft.

## Social: Twitter/X skeleton

Keep each post under 280 characters. One link per post, `?utm_source=twitter`. Name the card file on the line after each post. The default is one announce post built on the promo sentence. Draft the reminder, day-of, and thread only when the user asks.

```markdown
**Promo sentence:** {one sentence: abstract summary + date + time and timezone}

### Twitter/X: Announce
Status: draft
{Promo sentence, trimmed to fit.}
{luma_url}?utm_source=twitter
Card: {card_path_or_"card pending"}

### Reminder (1 week out, only if asked)
{New angle: a specific thing the speakers will demo or answer.}
{luma_url}?utm_source=twitter
Card: ...

### Day of (only if asked)
Starting at {time} {tz}: {what they are doing today}. {luma_url}?utm_source=twitter
Card: ...

### Thread option (only if asked)
1/ {hook}
2/ {takeaway 1}
3/ {takeaway 2}
4/ {who it is for + link}
```

## Social: LinkedIn skeleton

Three to six short lines, plain language, link at the end with `?utm_source=linkedin`. Tag speakers by name only if the brief gives their handles.

```markdown
### LinkedIn: Announce
Status: draft
{Promo sentence as the opening line.}
{One or two lines on what attendees will see, from the takeaways.}
{Date, time, tz}. Streaming live on LinkedIn and YouTube.
Register: {luma_url}?utm_source=linkedin
Card: {card_path_or_"card pending"}

### Reminder (1 week out, only if asked)
...

### Day of (only if asked)
...
```

## Metrics report skeleton

File: `webinar-output/{slug}/metrics.md`

```markdown
# Webinar metrics: {title}

Date: {date}  |  Luma: {luma_url}

## Luma
| Metric | Value |
|--------|-------|
| Registered | {n} |
| Waitlisted | {n} |
| Checked in | {n} |
| Attendance rate | {pct}% |

## Riverside
| Metric | Value |
|--------|-------|
| Peak concurrent viewers | {n or "not provided"} |
| Unique viewers | {n or "not provided"} |
| Average watch time | {value or "not provided"} |
| Replay views | {n or "not provided"} |
| Q&A / chat messages | {n or "not provided"} |

## Notes
{Observations that follow from the numbers, for example the gap between Luma check-ins and Riverside viewers. Say so when the two sources measure different things.}
```
