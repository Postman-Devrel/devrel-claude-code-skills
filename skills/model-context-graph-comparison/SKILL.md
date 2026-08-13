---
name: model-context-graph-comparison
description: "Autopilot skill that fires within an hour of a new AI model or coding framework/harness release, benchmarks it against Postman's context graph, produces a short study with charts + token-optimization data, posts to all Postman social accounts, and regenerates the harness config to use the new model. Focus: APIs, coding, agentic autonomy."
argument-hint: "[--now [model-name]] | [--watchlist] | [--dry-run]"
allowed-tools: ["Bash", "WebSearch", "WebFetch", "Read", "Write", "Edit"]
---

# Model × Context Graph — Autopilot

Every time a new AI model or coding framework/harness ships, we want a data-backed post out the door within an hour: "Postman's context graph makes `<model>` X% better at APIs, Y% cheaper per task, Z% more autonomous." This skill runs the study, produces the visuals, posts to social, and regenerates the harness config to use the new model as its default.

## What "context graph" and "AI harness" mean here

- **Context graph** — Postman's structured, machine-readable representation of an API surface (endpoints, schemas, examples, auth, dependencies). Fed to a model, it collapses the "what tools do I have and how do I call them" reasoning into a single lookup.
- **AI harness** — the software infrastructure that wraps around an LLM to turn it into an autonomous agent. The LLM is the brain; the harness provides the tools, sandboxed environments, memory, and security guardrails required to safely execute multi-step coding tasks. When a new model ships, the harness config (model ID, context window, tool schemas, sampling params) needs to be regenerated to unlock the new model's capabilities.

## When it runs

- **Hourly cron** (default). Checks the watchlist below; if a new release is detected, kicks off the pipeline.
- **On demand** via `--now [model-name]` to force a run against a specific model.
- **Watchlist management** via `--watchlist` to list, add, or remove tracked sources.

## Watchlist — what counts as a "release"

Two categories trigger a study:

**AI models** (any of):
- Anthropic (Claude family)
- OpenAI (GPT / o-series)
- Google DeepMind (Gemini)
- Meta AI (Llama)
- xAI (Grok)
- Mistral, DeepSeek, Qwen, Cohere
- Any model debuting on the [Artificial Analysis](https://artificialanalysis.ai/) leaderboard at ≥ current SOTA on coding, tool-use, or long-context benchmarks

**Coding frameworks / harnesses** (any of):
- Claude Code, Cursor, Windsurf, Zed AI, Aider, Cline, Continue, Cody
- OpenAI Agents SDK, Anthropic Agent SDK, LangGraph, PydanticAI, AutoGen, CrewAI, LlamaIndex Agents
- New MCP-first agent runtimes

Release-detection sources (checked in parallel per run):

| Source | Feed |
|--------|------|
| Anthropic | `https://www.anthropic.com/news` (WebFetch), Anthropic X account |
| OpenAI | `https://openai.com/blog`, `https://platform.openai.com/docs/models` |
| Google DeepMind | `https://deepmind.google/discover/blog/` |
| Meta AI | `https://ai.meta.com/blog/` |
| xAI | `https://x.ai/blog` |
| Mistral | `https://mistral.ai/news/` |
| Artificial Analysis | `https://artificialanalysis.ai/` |
| GitHub releases | `github.com/anthropics/claude-code`, `github.com/openai/openai-agents-python`, `github.com/langchain-ai/langgraph`, `github.com/pydantic/pydantic-ai`, `github.com/cursor-ai/cursor`, `github.com/paul-gauthier/aider` |
| HuggingFace | Trending models filtered to last 24h |

State is kept in `model-context-graph-comparison-output/seen.json` (release id → first-seen timestamp) so we never post the same drop twice.

## Required environment variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Run benchmarks against Claude models |
| `OPENAI_API_KEY` | Run benchmarks against OpenAI models |
| `GOOGLE_API_KEY` | Run benchmarks against Gemini |
| `POSTMAN_API_KEY` | Pull the context graph for a target workspace / collection |
| `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET` | Auto-post to @getpostman |
| `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_ORG_ID` | Post to the Postman LinkedIn company page |
| `WP_USERNAME`, `WP_APP_PASSWORD` | Publish the study as a blog post via `blog-wordpress-stage` |

If a credential is missing, that channel is skipped and the run log records `channel_skipped` — the study still ships to the channels that are configured.

## Output directory

All output goes to `model-context-graph-comparison-output/`:

| File | Description |
|------|-------------|
| `seen.json` | Deduplication state (release id → first-seen UTC timestamp) |
| `studies/YYYYMMDD-<model-slug>.md` | The full study markdown (blog-ready) |
| `studies/YYYYMMDD-<model-slug>/charts/*.png` | Chart PNGs (see Visuals) |
| `studies/YYYYMMDD-<model-slug>/data.csv` | Raw benchmark rows |
| `posts/YYYYMMDD-<model-slug>-twitter.md` | Twitter thread (5–7 tweets) |
| `posts/YYYYMMDD-<model-slug>-linkedin.md` | LinkedIn post |
| `posts/YYYYMMDD-<model-slug>-youtube-short.md` | YT Short script (30–60s) |
| `harness/YYYYMMDD-<model-slug>.json` | Regenerated harness config |
| `run-log-YYYYMMDD-<model-slug>.md` | End-to-end run log with timings and channel status |

## Pipeline — end to end, ≤ 60 minutes

The full run is a single deterministic pipeline. Every stage writes intermediate output so a failed stage can be resumed without redoing prior work.

### Stage 1 — Detect (target: ≤ 5 min)

1. In parallel, `WebFetch` each source in the watchlist table.
2. Extract candidate release records: `{id, vendor, name, released_at, url, category: model|framework, claims: [...]}`.
3. Filter against `seen.json`. If empty → exit cleanly, log `no-new-releases`.
4. For each new release, load the vendor-provided model card / release notes; extract: context window, pricing per 1M tokens, tool-use support, self-reported benchmarks (SWE-bench, τ-bench, HumanEval, MMLU, LiveCodeBench, AIME).

### Stage 2 — Benchmark against the context graph (target: ≤ 25 min)

Run the model on four task suites, first **without** the context graph (baseline) then **with** it. Reuse the same seeds and prompts so the delta is causal, not noise.

| Suite | What it measures | Task count | Metric |
|-------|------------------|------------|--------|
| `api-tasks` | Call the right endpoint with the right params from a natural-language ask against a Postman workspace | 30 | Task success rate, tokens per successful task, wall-clock |
| `coding-tasks` | Fix or extend code that calls the same APIs (SWE-bench-lite-style, scoped to API-integration bugs) | 20 | Pass@1, tokens per task, wall-clock |
| `autonomy-tasks` | Multi-step goals that require chaining 3+ endpoints with no human turn (τ-bench-style) | 15 | Goal completion rate, tool-call efficiency (calls-per-goal), tokens per goal |
| `downstream-update-tasks` | Given an upstream API change (new version, deprecated field, renamed param, tightened auth, changed response shape), identify every downstream consumer and generate correct patches for each | 20 | Consumer recall (%), consumer precision (%), patch correctness (pass@1), tokens per completed migration, wall-clock |

**Why `downstream-update-tasks` is a first-class suite.** This is the task the context graph is uniquely built for. A vanilla model sees the upstream change and then has to grep-and-guess across the codebase — it doesn't know which collections, environments, integrations, or repos call the endpoint, and it doesn't know which fields are actually read downstream. The context graph carries that topology: `endpoint → consumers → the specific request/response fields each one touches`. In practice this collapses a "read every file that mentions `/v1/users`" search into "traverse three edges of the graph."

Each `downstream-update-tasks` scenario ships with a seeded fixture repo + workspace + collection so the run is reproducible:
- `upstream_change` — the exact diff to the OpenAPI spec / collection.
- `ground_truth_consumers` — the full list of downstream artifacts that require edits.
- `ground_truth_patches` — the reference patch for each consumer, plus a test suite that must pass after patching.

For every scenario record:
- `consumers_identified` (set) — used to compute recall vs `ground_truth_consumers`.
- `consumers_touched_but_not_needed` (set) — used to compute precision.
- `patch_test_pass_rate` — fraction of ground-truth tests that pass after the model's patches are applied.
- `tokens_in`, `tokens_out`, `tool_calls`, `wall_ms`.

For every task record:
- `tokens_in`, `tokens_out`, `tool_calls`, `wall_ms`, `success (bool)`, `error_category`
- Baseline (no context graph): the model gets only the natural-language ask.
- Context graph: the model gets the same ask + the relevant slice of the graph as tool schemas + example calls.

Compute:
- `success_delta` = success_with_graph − success_baseline
- `token_delta_pct` = (tokens_baseline − tokens_with_graph) / tokens_baseline
- `cost_per_success_delta` using the vendor's published $/1M pricing
- `autonomy_delta` = (goals completed with ≤ N tool calls with graph) − (baseline)
- `dependency_recall_delta` = consumer recall with graph − baseline
- `dependency_precision_delta` = consumer precision with graph − baseline
- `migration_pass_delta` = patch_test_pass_rate with graph − baseline

Write the raw rows to `studies/YYYYMMDD-<slug>/data.csv`.

### Stage 3 — Generate visuals (target: ≤ 10 min)

Follow the `dataviz` skill's conventions for palette, mark specs, and legend rules. Produce PNGs at 2× density so they read well on LinkedIn and X.

Required charts:

1. **Bar chart** — Task success rate: baseline vs context graph, one bar pair per suite (4 pairs). Include the delta as an inline label.
2. **Grouped bar** — Tokens per successful task, baseline vs context graph, one group per suite. Percentage saving labeled on top of the "with graph" bar.
3. **Bar chart** — Cost per successful task, baseline vs context graph. Same layout as (2), but in USD.
4. **Line chart** — Cumulative goal completion over tool-call budget (autonomy suite). One line per condition. The X axis is "tool calls allowed"; the Y is "goals completed."
5. **Scatter or 2×2 quadrant** — Downstream-update suite: consumer recall (X) vs consumer precision (Y), one point per scenario. Two series (baseline / context graph). The context-graph cluster should sit in the top-right; the baseline cluster typically drifts down-and-left. A dashed diagonal marks the "F1 = 1" line for reference.
6. **Stacked bar** — Migration cost per scenario in the downstream-update suite: tokens split into `discovery` (finding consumers) vs `patching` (writing edits). The delta on the discovery segment is usually the dramatic one — that's the context graph's job.
7. **Radar (optional)** — model self-reported benchmarks vs measured-with-graph across the four suites.
8. **Header image** — hand off to `/devrel-skills:blog-header-image` with a prompt like `Postman context graph amplifying <model-name>` (2560×1355 PNG, no text).

Chart script location: `skills/model-context-graph-comparison/references/make_charts.py` (matplotlib, uses the dataviz palette).

### Stage 4 — Write the study (target: ≤ 10 min)

Produce `studies/YYYYMMDD-<slug>.md` with the following structure. Voice matches the Postman developer-advocate voice used by `blog-write` (conversational, authoritative, hands-on). Never use "supercharge", "unlock", "revolutionize", or "leverage."

```
---
title: "Postman's context graph makes <Model> <headline delta>"
suggested_title: "..."
meta_description: "<= 150 chars"
seo_score: <computed>
keywords: [...]
---

## The one-line result
<Model> ships today. On API + coding + autonomy + downstream-migration tasks,
Postman's context graph lifts task success by X%, cuts tokens per successful
task by Y%, reduces cost per completed goal by Z%, and finds W% more of the
downstream consumers that need updating when an upstream API changes.

## Why it matters (qualitative)
- The model isn't the bottleneck; the *context* it's given is.
- The context graph replaces "here are 800 API docs, figure it out" with
  "here is the exact slice you need."
- For agentic autonomy, this is the difference between a demo and a shippable
  agent.
- For downstream migrations, the context graph is the API's dependency map —
  the model no longer has to grep-and-guess which consumers use a field.

## The four benchmarks
### API tasks
<chart 1 embed>
<paragraph with 2–3 concrete task examples and what changed>

### Coding tasks
<chart 2 embed>
<paragraph>

### Agentic autonomy
<chart 4 embed>
<paragraph>

### Downstream dependency updates
<chart 5 + 6 embed>
Walk through one concrete migration end-to-end: the upstream diff, the list
of consumers the graph surfaced (that a vanilla model missed or hallucinated),
the patch it generated, and the test pass rate. Show the token split between
discovery and patching — this is where the context graph earns its keep.

## Token economics
<chart 2 + 3 embed>
<table: raw numbers>

## Reproducing this
<link to data.csv, harness config, and the exact prompts used>

## What we're shipping
<harness config regenerated with the new model, link to the diff>
```

### Stage 5 — Regenerate the harness (target: ≤ 5 min)

Emit `harness/YYYYMMDD-<slug>.json`:

```json
{
  "model": "<vendor/model-id>",
  "context_window": <int>,
  "pricing": {"input_per_1m": <float>, "output_per_1m": <float>},
  "tools": [
    {"name": "context_graph.query", "schema_ref": "postman.context_graph.v1"},
    {"name": "http_request", "schema_ref": "postman.http.v1"},
    {"name": "collection_run", "schema_ref": "postman.collection_runner.v1"}
  ],
  "sampling": {"temperature": <chosen from benchmark sweep>, "top_p": 1.0},
  "guardrails": {
    "sandboxed_execution": true,
    "max_tool_calls_per_goal": <derived from autonomy chart>,
    "secrets_redaction": true
  },
  "notes": "Regenerated <UTC> after <model> release. See study <path>."
}
```

Open a PR against the appropriate config file if the harness lives in the repo; otherwise write the file and log a follow-up TODO in the run log.

### Stage 6 — Post (target: ≤ 5 min)

Reuse the posting patterns from `social-media-manager`. Post to every channel where credentials are configured, in parallel:

1. **Twitter/X** — 6–8 tweet thread. Tweet 1 is the headline delta. Tweet 2 is chart 1 (success rate across all four suites). Tweet 3 is chart 2 (token savings). Tweet 4 is chart 5 (downstream-update recall/precision) with a one-line "the model finds the consumers it couldn't grep for" caption. Tweet 5 is the qualitative why. Tweet 6 links to the study. Tweet 7 links to the regenerated harness config.
2. **LinkedIn** — long-form post version, chart 1 as the cover image, chart 2 inline. CTA: read the study, try the harness config.
3. **YouTube Short** — 30–60s script + b-roll callouts (charts, terminal, Postman UI). Written to `posts/*-youtube-short.md`; production hand-off is manual for now.
4. **Blog** — stage the study to WordPress via `/devrel-skills:blog-wordpress-stage` as a draft with the header image and SEO frontmatter.
5. **Discord** — post a short announcement in `#announcements` with the headline delta and a link to the blog.

Every posted URL is recorded in `run-log-YYYYMMDD-<slug>.md`.

## Guardrails

- **Never post an unfavorable result silently.** If any of the three suites shows the context graph making the model *worse*, halt at Stage 4 and require a human before Stage 6.
- **No made-up numbers.** Every delta on a chart or in the study must come from a row in `data.csv`. Regenerate visuals from CSV so the chart and the number cannot disagree.
- **Cite the model's own claims.** If a vendor advertises "20% better on SWE-bench," include their claim next to our measured delta on the same task. Contrast, don't hide.
- **No marketing language.** Guardrail list: avoid "supercharge", "unlock", "revolutionize", "leverage", "game-changing", "revolutionary."
- **Speed vs quality.** If the pipeline exceeds 55 min, ship the Twitter thread + blog draft on time and let the LinkedIn / YouTube Short land in the following hour. Better to be first with something correct than late with everything.

## How to run

### Autopilot (default)

```
/devrel-skills:model-context-graph-comparison
```

Sets up the hourly cron. First invocation:
1. Writes `model-context-graph-comparison-output/seen.json` seeded with the last 7 days of releases so it doesn't backfill-spam.
2. Schedules an hourly `CronCreate` to invoke this skill.

### Manual run against a known drop

```
/devrel-skills:model-context-graph-comparison --now "Claude 5.1 Opus"
```

Skips detection, targets the named model, runs Stages 2–6.

### Dry run

```
/devrel-skills:model-context-graph-comparison --dry-run
```

Executes Stages 1–5 but writes posts to disk without publishing. Use before enabling autopilot in a new environment.

### Watchlist

```
/devrel-skills:model-context-graph-comparison --watchlist              # list
/devrel-skills:model-context-graph-comparison --watchlist add <url>    # add a source
/devrel-skills:model-context-graph-comparison --watchlist remove <url> # remove a source
```

Watchlist is persisted at `model-context-graph-comparison-output/watchlist.json`.

## Related skills

- `/devrel-skills:blog-write` — voice + SEO frontmatter conventions applied to the study.
- `/devrel-skills:blog-header-image` — Postman-branded header image (2560×1355 PNG).
- `/devrel-skills:blog-wordpress-stage` — stage the study to WordPress.
- `/devrel-skills:social-media-manager` — Twitter/X posting mechanics, employee advocacy kit format.
- `/devrel-skills:content-metrics` — 7 days after posting, pull the row for this study from the weekly Content → Product digest and append its impact_score to the study's run log. Feeds back into deciding whether the next drop gets the same treatment.
- `dataviz` — palette, mark specs, and legend rules for the charts.
