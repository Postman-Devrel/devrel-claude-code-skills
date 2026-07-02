---
name: social-media-manager
description: "Weekly social media agent team — researches Postman blog, release notes, and trending news, creates 5 LinkedIn/Twitter posts, packages an employee advocacy kit, and auto-posts to Twitter on Mon/Wed at 10am PST."
argument-hint: "[twitter-handle] (e.g. @getpostman) — the Twitter/X account to post from"
allowed-tools: ["Bash", "Write"]
---

# Social Media Manager — Agent Team

An automated weekly social media pipeline powered by a Claude Agent Team. Four specialized agents collaborate to research, create, distribute, and post Postman developer content.

## Team Overview

| Agent | Role | Trigger |
|-------|------|---------|
| **researcher** | Scrapes blog.postman.com, release notes, and trending dev news | Monday 5:00 AM PST (cron) |
| **content-creator** | Crafts 5 social posts (LinkedIn + Twitter/X) from the research brief | After researcher completes |
| **employee-advocacy** | Repackages posts into Slack-ready messages for employee sharing | After content-creator completes |
| **social-poster** | Posts 2 selected tweets to Twitter/X via API | Monday & Wednesday 10:00 AM PST |

## Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `TWITTER_API_KEY` | Twitter/X API key |
| `TWITTER_API_SECRET` | Twitter/X API key secret |
| `TWITTER_ACCESS_TOKEN` | Twitter/X access token for the posting account |
| `TWITTER_ACCESS_SECRET` | Twitter/X access token secret |

## Output Directory

All output goes to `social-media-output/`:

| File | Agent | Description |
|------|-------|-------------|
| `research-brief-YYMMDD.md` | researcher | Raw research: blog posts, release notes, trending news |
| `social-posts-YYMMDD.md` | content-creator | 5 ready-to-publish posts (LinkedIn + Twitter versions) |
| `employee-advocacy-YYMMDD.md` | employee-advocacy | Slack-ready posts for employee sharing |
| `employee-advocacy-YYMMDD-slack.json` | employee-advocacy | Slack Block Kit JSON version |
| `twitter-log-YYMMDD.md` | social-poster | Posting log with tweet IDs and URLs |

## How to Run

### Option 1: Full Weekly Pipeline (Scheduled)

Invoke this skill to set up the weekly cron schedule. The researcher agent wakes up every Monday at 5:00 AM PST and kicks off the full pipeline automatically.

```
/devrel-skills:social-media-manager @getpostman
```

This will:
1. Create the `social-media-manager` agent team
2. Schedule the Monday 5:00 AM PST cron trigger
3. Schedule the Monday and Wednesday 10:00 AM PST Twitter posting triggers
4. Start the pipeline (or wait for the next scheduled trigger)

### Option 2: Run Now (Manual)

To run the full pipeline immediately without waiting for the cron:

```
/devrel-skills:social-media-manager @getpostman --now
```

### Option 3: Run a Single Agent

To re-run just one agent (e.g., regenerate posts from an existing research brief):

```
/devrel-skills:social-media-manager @getpostman --agent content-creator
```

---

## Team Orchestration

When this skill is invoked, you are the **team lead**. Follow these steps:

### Step 0: Setup

1. Parse the argument to extract the Twitter/X handle. If no handle is provided, ask: "Which Twitter/X handle should I post from? (e.g., @getpostman)"
2. Check for `--now` or `--agent` flags.
3. Create the output directory if it doesn't exist:
   ```bash
   mkdir -p social-media-output
   ```

### Step 1: Create the Team

```
TeamCreate:
  team_name: social-media-manager
  description: "Weekly social media pipeline for Postman DevRel"
  agent_type: team-lead
```

### Step 2: Define Tasks

Create tasks for the team's task list:

| # | Task | Owner | Depends On | Status |
|---|------|-------|------------|--------|
| 1 | Research blog posts, release notes, and trending news | researcher | — | pending |
| 2 | Create 5 social media posts from research brief | content-creator | Task 1 | blocked |
| 3 | Package posts into employee advocacy Slack messages | employee-advocacy | Task 2 | blocked |
| 4 | Select 2 posts and post to Twitter/X (Mon + Wed 10am PST) | social-poster | Task 2 | blocked |

### Step 3: Spawn Agents

Read the agent prompt files and spawn each teammate:

**Researcher Agent:**
```
Agent:
  name: researcher
  team_name: social-media-manager
  subagent_type: general-purpose
  prompt: [contents of skills/social-media-manager/agents/researcher.md]
```

**Content Creator Agent** (spawn after researcher completes Task 1):
```
Agent:
  name: content-creator
  team_name: social-media-manager
  subagent_type: general-purpose
  prompt: [contents of skills/social-media-manager/agents/content-creator.md]
         + "Research brief is at: social-media-output/research-brief-YYMMDD.md"
```

**Employee Advocacy Agent** (spawn after content-creator completes Task 2):
```
Agent:
  name: employee-advocacy
  team_name: social-media-manager
  subagent_type: general-purpose
  prompt: [contents of skills/social-media-manager/agents/employee-advocacy.md]
         + "Social posts file is at: social-media-output/social-posts-YYMMDD.md"
```

**Social Poster Agent** (spawn after content-creator completes Task 2):
```
Agent:
  name: social-poster
  team_name: social-media-manager
  subagent_type: general-purpose
  prompt: [contents of skills/social-media-manager/agents/social-poster.md]
         + "Social posts file is at: social-media-output/social-posts-YYMMDD.md"
         + "Twitter handle: [handle from argument]"
```

Note: `employee-advocacy` and `social-poster` can run **in parallel** since they both depend on the content-creator's output but not on each other.

### Step 4: Schedule Cron Jobs

Set up recurring triggers (session-scoped, 7-day auto-expiry):

**Monday 5:00 AM PST — Research trigger:**
```
CronCreate:
  cron: "3 5 * * 1"
  prompt: "/devrel-skills:social-media-manager [handle] --now"
  recurring: true
```

**Monday 10:00 AM PST — Twitter post 1:**
```
CronCreate:
  cron: "3 10 * * 1"
  prompt: "Post Monday's tweet for the social-media-manager team. Read social-media-output/social-posts-YYMMDD.md, find the post marked for Monday, and post it to Twitter/X using the social-poster agent workflow."
  recurring: true
```

**Wednesday 10:00 AM PST — Twitter post 2:**
```
CronCreate:
  cron: "3 10 * * 3"
  prompt: "Post Wednesday's tweet for the social-media-manager team. Read social-media-output/social-posts-YYMMDD.md, find the post marked for Wednesday, and post it to Twitter/X using the social-poster agent workflow."
  recurring: true
```

### Step 5: Monitor and Report

As team lead, monitor agent progress:

1. When the **researcher** completes → unblock Task 2, send the research brief path to the content-creator
2. When the **content-creator** completes → unblock Tasks 3 and 4, spawn employee-advocacy and social-poster in parallel
3. When **employee-advocacy** completes → note the advocacy kit path
4. When **social-poster** gets approval → confirm the posting plan or adjust

### Step 6: Final Report

When all agents have completed their work, present a summary:

```
Social Media Manager — Weekly Pipeline Complete

  Research brief:      social-media-output/research-brief-YYMMDD.md
  Social posts:        social-media-output/social-posts-YYMMDD.md
  Employee advocacy:   social-media-output/employee-advocacy-YYMMDD.md
  Twitter log:         social-media-output/twitter-log-YYMMDD.md

  Posts created:       5
  Twitter posts:       2 scheduled (Mon + Wed @ 10am PST)
  Advocacy kit:        Ready for Slack distribution

  Cron schedules active (7-day expiry):
    - Research: Monday 5:00 AM PST
    - Twitter post 1: Monday 10:00 AM PST
    - Twitter post 2: Wednesday 10:00 AM PST
```

### Step 7: Shutdown

After the final report, gracefully shut down all teammates:

```
SendMessage to each agent: { type: "shutdown_request" }
```

Wait for shutdown confirmations, then clean up:

```
TeamDelete
```

---

## Pipeline Flow

```
Monday 5:00 AM PST
       │
       ▼
  ┌─────────────┐
  │  researcher  │  ── scrapes blog, release notes, trending news
  └──────┬──────┘
         │  research-brief-YYMMDD.md
         ▼
  ┌─────────────────┐
  │ content-creator  │  ── crafts 5 LinkedIn + Twitter posts
  └──────┬──────────┘
         │  social-posts-YYMMDD.md
         ├──────────────────┐
         ▼                  ▼
  ┌──────────────┐   ┌──────────────┐
  │  employee-   │   │   social-    │
  │  advocacy    │   │   poster     │
  └──────┬───────┘   └──────┬───────┘
         │                  │
         ▼                  ▼
  Slack advocacy kit   Mon 10am: Tweet 1
                       Wed 10am: Tweet 2
```

## Guidelines

- The team lead (you) coordinates the pipeline — don't let agents run unsupervised
- The researcher must complete before any other agent starts
- Content-creator must complete before employee-advocacy and social-poster start
- Employee-advocacy and social-poster run in parallel
- The social-poster agent must get team lead approval before posting to Twitter
- All output files use the YYMMDD date format (e.g., `260429` for April 29, 2026)
- Cron schedules are session-scoped and auto-expire after 7 days — the user will need to re-invoke the skill for the next week
- If any agent fails, report the error and offer to retry that specific agent
