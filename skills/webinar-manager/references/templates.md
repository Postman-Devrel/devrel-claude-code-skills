# Webinar Manager Templates

Fill every `{placeholder}` from `brief.md`. Never invent speakers, dates, or claims. Copy rules apply to everything below: no "supercharge", "unlock", "revolutionize", or "leverage", and no em dashes.

## Jira: parent task

- Project: `MKTG` (site `postmanlabs.atlassian.net`), issue type `Task`
- Parent epic: `MKTG-8442` (Technical Content)
- Summary: `[Webinar] {title} {M/D}`
- Due date: webinar date

Description:

```text
Webinar will be {M/D} and we will stream on Riverside.

{abstract, 2 to 4 sentences}

Luma event: {luma_url}
Speakers: {name (title)}, ...
```

## Jira: social promo card sub-task

- Issue type: `Sub-task`, parent is the task above
- Summary: `Social Promo Card`
- Labels: `creative`
- Assignee: Jonathan Holt (look up the account id with `lookupJiraAccountId`)
- Due date: 10 days before the webinar, or tomorrow if the webinar is sooner

Description:

```text
Please create a social promo card for the webinar below. Reuse the template from MKTG-11062 (inputs: speaker faces, title, description, date, time).

Title: {title}
Description: {one-sentence description}
Date and time: {date} {time} {timezone}
Speakers: {name (title)} (headshots attached or at {headshot_path_or_link})
Stream: Riverside
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

---

Hi {first_name},

{One sentence on the problem the webinar addresses.}

On {date} at {time} {timezone}, {speaker names} will {what they will do, concrete}.

You will see:
- {takeaway 1}
- {takeaway 2}
- {takeaway 3}

{One sentence linking related content, for example "If you want background first, read {blog title}: {url}".}

[Save your spot]({luma_url}?utm_source=email)

Can't make it live? Register anyway and we will send the recording.

{sign-off}
```

Pull "related content" from the brief first, then from `blog-output/` posts that match the topic. Link only URLs that exist.

## Social: Twitter/X skeleton

Keep each post under 280 characters. One link per post, `?utm_source=twitter`. Name the card file on the line after each post.

```markdown
### Announce
{Hook about the problem or what attendees will see.} {Date}, {time} {tz}.
{luma_url}?utm_source=twitter
Card: {card_path_or_"card pending"}

### Reminder (1 week out)
{New angle: a specific thing the speakers will demo or answer.}
{luma_url}?utm_source=twitter
Card: ...

### Day of
Starting at {time} {tz}: {what they are doing today}. {luma_url}?utm_source=twitter
Card: ...

### Thread option
1/ {hook}
2/ {takeaway 1}
3/ {takeaway 2}
4/ {who it is for + link}
```

## Social: LinkedIn skeleton

Three to six short lines, plain language, link at the end with `?utm_source=linkedin`. Tag speakers by name only if the brief gives their handles.

```markdown
### Announce
{Problem statement in one line.}
{What the webinar covers in one or two lines.}
{Date, time, tz}. Streaming live.
Register: {luma_url}?utm_source=linkedin
Card: {card_path_or_"card pending"}

### Reminder (1 week out)
...

### Day of
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
