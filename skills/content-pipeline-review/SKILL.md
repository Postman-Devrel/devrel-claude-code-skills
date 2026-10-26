---
name: content-pipeline-review
description: >-
  Review the Developer Marketing Jira board and list blog and video work that is
  In Progress or In Review. Use when the user asks "what's in the content
  pipeline", "what blogs are in review", "what videos are in progress", "content
  status", "what's on the Developer Marketing board", or wants a snapshot of
  content work in flight. Read-only — never edits Jira.
argument-hint: "[blogs|videos|all] [--assignee me|name] [--save]"
---

# Content Pipeline Review

Read-only snapshot of blog and video tickets on the **Developer Marketing** Jira
board, limited to **In Progress** and **In Review** work.

## Target

- Cloud ID: `0d13b137-2934-4b74-a921-694ab83c54c5` (`postmanlabs.atlassian.net`)
- Board: the **Developer Marketing** work lives under epic **MKTG-8442**
  ("Technical Content") in the **MKTG** project. There is no Jira project named
  "Developer Marketing"; query by epic parent.

## Prerequisites

Uses the Atlassian MCP server (OAuth), the same connector as `cfp-tracker`. See
"Atlassian / Confluence Setup" in the README. If the Atlassian tools are not
available or not authenticated, tell the user to authorize the connector (`/mcp`
in an interactive session, or their claude.ai connector settings) and stop.

## Step 1: Query tickets

Run one JQL search with `searchJiraIssuesUsingJql` (`searchResultMode: "all"`,
`maxResults: 100`, paginate with `nextPageToken` until `isLast`):

```
parent = MKTG-8442 AND status in ("In Progress", "In Review") ORDER BY status ASC, updated DESC
```

Request fields: summary, status, issuetype, assignee, labels, duedate, updated.
Responses are large (avatar URLs); if the result is saved to a file, extract the
fields with `jq` instead of reading it raw. Do not query without the status
filter: the epic has 100+ children and a single page won't cover them.

## Step 2: Classify and filter

Issue type is **not** reliable: videos are filed as both `Blog content` and
`Task`. Classify in this order, first match wins:

1. Title contains "video" (e.g. `[Video]`, `[Passport Video]`, `Video - What Is…`) or label `video` → **Video**
2. Title contains "blog" or label `blog` → **Blog**
3. Issue type `Blog content` → **Blog**
4. Otherwise → **Other** (e.g. launch/GA tasks, or tasks with no content marker)

Apply the `blogs` / `videos` argument and `--assignee` (`me` = the authenticated
Jira user via `atlassianUserInfo`; otherwise match the name case-insensitively).
Show **Other** tickets in a short separate list so nothing is silently dropped,
and let the user say how to classify them.

## Step 3: Present results

Group by content type, then status (In Review first, since those are closest to
shipping). Dates in PST. Today's date is the reference for overdue/stale.

```
## Content Pipeline — Developer Marketing (as of Mon DD, YYYY)

### Blogs (N)
**In Review (n)**
| Ticket | Title | Assignee | Due | Updated |
|--------|-------|----------|-----|---------|
| [DM-123](https://postmanlabs.atlassian.net/browse/DM-123) | ... | ... | ... | ... |

**In Progress (n)**
...

### Videos (N)
...

**Totals:** X blogs (a in review, b in progress) · Y videos (c in review, d in progress)
```

Flag, with a short note after the tables:

- **Overdue** — due date in the past
- **Stale** — not updated in 14+ days
- **Unassigned**

Omit empty sections rather than printing empty tables. If nothing matches, say so.

## Rules

- Read-only: never transition, comment on, or edit tickets.
- Link every ticket key to `https://postmanlabs.atlassian.net/browse/<KEY>`.
- Don't open individual tickets unless a title is truncated or classification is unclear.
