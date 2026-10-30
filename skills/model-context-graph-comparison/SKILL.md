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

## Context Graph API — placeholder (release TBD, expected mid-August 2026)

The skill talks to the context graph through the forthcoming **Context Graph API**. That API is not GA yet, so the client below is stubbed. Everything else in the pipeline is real; only the network call is faked.

```
# skills/model-context-graph-comparison/references/context_graph_client.py (to be added)
# TODO(release): replace stub with real HTTP client when the Context Graph API ships.

BASE_URL = os.getenv(
    "POSTMAN_CONTEXT_GRAPH_API_URL",
    "https://api.postman.com/context-graph/v1",  # placeholder — confirm on release
)
API_KEY = os.getenv("POSTMAN_CONTEXT_GRAPH_API_KEY")  # not yet issued
```

Expected endpoints (based on internal spec — subject to change on release):

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/graphs/{workspace_id}` | Fetch the full graph for a workspace |
| `POST` | `/graphs/{workspace_id}/query` | Return a task-relevant slice given a natural-language ask or endpoint ref |
| `GET` | `/graphs/{workspace_id}/consumers` | List all downstream consumers of an endpoint or field (powers `downstream-update-tasks`) |
| `GET` | `/graphs/{workspace_id}/diff?from=...&to=...` | Compute upstream-change → downstream-impact for a given version bump |

**Stub behavior until GA.** The client returns fixture data from `references/fixtures/context_graph/` so benchmark runs still complete end-to-end and the pipeline is exercised on every release. When the API goes live, only the client module changes; the four suites and the harness template layer are unaffected.

**Swap-in checklist (do this the day the API ships):**
- [ ] Replace `BASE_URL` placeholder with the announced production URL.
- [ ] Issue a `POSTMAN_CONTEXT_GRAPH_API_KEY` and add it to `~/.claude/settings.json`.
- [ ] Confirm the four expected endpoints match the final spec; adjust `context_graph_client.py` if renamed.
- [ ] Delete `references/fixtures/context_graph/` (or keep it as an offline-mode fallback — decide at release).
- [ ] Bump the `schema_ref` in the harness template from `postman.context_graph.v1.stub` to `postman.context_graph.v1`.
- [ ] Run `/devrel-skills:model-context-graph-comparison --dry-run` end-to-end against a real workspace before re-enabling autopilot.

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
| `POSTMAN_API_KEY` | Pull workspaces / collections / environments |
| `POSTMAN_CONTEXT_GRAPH_API_KEY` | **Placeholder — not yet issued.** Auth for the forthcoming Context Graph API (release mid-August 2026). Until GA, the client falls back to fixtures in `references/fixtures/context_graph/`. |
| `POSTMAN_CONTEXT_GRAPH_API_URL` | Optional base URL override for the Context Graph API. Defaults to the placeholder `https://api.postman.com/context-graph/v1` — confirm on release. |
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

The skill does not run the models directly. It delegates to the **ai-harness** at [`buildwithtalia/ai-harness`](https://github.com/buildwithtalia/ai-harness), which is the benchmark backend that owns the agent / model / context matrix and the deterministic + LLM-judge scoring.

#### 2.1 — Invoke the harness

Two supported invocations of `.github/workflows/on-model-release.yml` in the ai-harness repo. Both take the same payload; pick whichever fits the skill's execution context.

**Preferred — `repository_dispatch` (fire-and-forget from anywhere with a PAT):**

```bash
gh api repos/buildwithtalia/ai-harness/dispatches \
  -f event_type=new-model-release \
  -F 'client_payload[model]=<vendor>/<model-id>' \
  -F 'client_payload[adapter]=<claude|codex|devin|cursor|raw>' \
  -F 'client_payload[releaseUrl]=<vendor release / model-card URL>' \
  -F 'client_payload[dispatchedBy]=skill:model-context-graph-comparison'
```

Requires a PAT with `repo` scope on `buildwithtalia/ai-harness`, stored on the skill side as `AI_HARNESS_DISPATCH_TOKEN`.

**Alternative — `workflow_dispatch` (equivalent, more visible in the Actions UI):**

```bash
gh workflow run on-model-release.yml \
  --repo buildwithtalia/ai-harness \
  -f model=<vendor>/<model-id> \
  -f adapter=<claude|codex|devin|cursor|raw> \
  -f releaseUrl=<vendor release / model-card URL> \
  -f dispatchedBy=skill:model-context-graph-comparison
```

Payload fields:

| Field | Meaning |
|---|---|
| `model` (required) | New model identifier in Vercel AI Gateway naming, e.g. `anthropic/claude-5-opus`, `openai/gpt-6`. |
| `adapter` | Which slot to update. `claude` / `codex` / `devin` / `cursor` swap the `MODEL` constant in `src/core/agents/<adapter>.ts`. `raw` (default) appends the model to `agent-benchmark`'s `models` list as a new raw-model target that goes straight through `generateText` (no adapter). |
| `releaseUrl` | Vendor release / model-card URL. Recorded on the run's `triggerContext`. |
| `dispatchedBy` | Free-form caller label; use `skill:model-context-graph-comparison` for autopilot runs so the harness's audit log distinguishes skill-driven runs from manual ones. |

`on-model-release.yml` then does the full pipeline server-side: applies the model update (`scripts/apply-model-update.mjs`), runs `pnpm build`, runs `pnpm eval agent-benchmark`, uploads artifacts, and commits the adapter bump back to `main` with `[skip ci]` on success — **that commit is what completes Stage 5 (regenerate the harness) for us**.

#### 2.2 — What the harness runs today

`agent-benchmark` ships one suite with **12 cases** across three categories, all framed APIFlow-Bench-style (broken call + error hint + ticket wrapper):

| Category | Cases | Focus |
|---|---|---|
| `build` | 5 | Add API field, add service, v1→v2 migration, refactor to middleware, OAuth cutover |
| `find` | 3 | API-down blast radius, trace a value through the system, DB-change blast radius |
| `ask` | 4 | Three-way spec/collection/code drift, most-dependent endpoints, docs drift, OWASP API Top 10 review |

Each case carries `difficulty` (easy / medium / hard) and `capabilityAxis[]` tags (`authentication`, `discovery`, `schema_repair`, `multistep`, `error_recovery`, `pagination`, `statefulness`, `impact_analysis`, `docs_alignment`, `security_review`). Grading is a **deterministic** scorer (must-mention, regex, structured-output against a Zod schema) on cases with ground truth, plus an **LLM judge** on category-specific 5-dimension rubrics. `passed = aggregateScore >= 0.5`.

Every run automatically covers **agent × model × context** — every base agent (Claude Code, Devin, Cursor, Codex) composed against every registered context provider (baseline / `+cg` / `+orbit`) at the requested model. That's the matrix a single dispatch fills.

#### 2.3 — What the harness returns

The workflow uploads two artifacts (30-day retention):

- `runs/<id>/` — raw per-case JSONL (`cases.jsonl`) + `manifest.json`.
- `results/skill-input.json` — the normalised summary the skill consumes.

`results/skill-input.json` is also POSTed to `SKILL_WEBHOOK_URL` on completion (with an optional `SKILL_WEBHOOK_TOKEN` bearer) so the skill can consume runs without polling the Actions API. Shape:

```jsonc
{
  "runId": "2026-08-18T21-14-02-118Z__agent-benchmark",
  "suite": "agent-benchmark",
  "status": "completed",
  "startedAt": "…", "finishedAt": "…",
  "models": ["claude", "claude+cg", "claude+orbit", …],
  "caseCount": 12,
  "aggregate": {
    "perModel": {
      "<target>": { "meanScore", "passRate", "totalCostUsd", "totalInputTokens", "totalOutputTokens", "p50LatencyMs", "p95LatencyMs" }
    }
  },
  "perCategoryByTarget": [
    { "target": "claude", "category": "build", "passRate": 0.6, "meanScore": 0.71, "caseCount": 5 },
    …
  ],
  "providerDeltas": [
    { "agent": "claude", "model": "anthropic/claude-opus-4-7", "providerId": "cg",
      "passRateDelta": 0.10, "meanScoreDelta": 0.09, "costDelta": 0.02, "p50LatencyDelta": 340 },
    …
  ],
  "triggerContext": {
    "modelId": "anthropic/claude-5-opus",
    "adapterChanged": "claude",
    "releaseUrl": "https://www.anthropic.com/news/claude-5-opus",
    "workflowRunUrl": "https://github.com/buildwithtalia/ai-harness/actions/runs/1234",
    "dispatchedBy": "skill:model-context-graph-comparison"
  },
  "emittedAt": "…"
}
```

Every `providerDeltas` row is keyed on **`(agent, model, providerId)`**, so the skill can attribute the tagline per triple (e.g. *"the graph helps Claude Opus 4.7 more than Claude Sonnet 4.5"*).

#### 2.4 — Compute the tagline deltas

From the JSON above (and, when per-case detail is needed, `cases.jsonl` in the uploaded artifact):

- `success_delta` / **"X% better at APIs"** — `providerDeltas[].meanScoreDelta` or `passRateDelta`, filtered against `perCategoryByTarget` where `category ∈ {build, ask}` for API-shaped work.
- `token_delta_pct` — token deltas per case are in `cases.jsonl`; aggregates per target in `aggregate.perModel[target].totalOutputTokens`.
- `cost_per_success_delta` / **"Y% cheaper per task"** — `totalCostUsd / passCount` for base vs `+provider` on the same (agent, model).
- `autonomy_delta` / **"Z% more autonomous"** — `diagnostics.toolCallCount + stepCount` per case in `cases.jsonl`. `(baseline_tools − provider_tools) / baseline_tools` at equal-or-higher `aggregateScore`.

Write the raw rows to `studies/YYYYMMDD-<slug>/data.csv` (denormalise the harness's per-case JSONL: one row per `(target, case)` with the aggregated + per-category + per-provider fields inlined).

#### 2.5 — Planned expansion (v2 of this pipeline)

The four-suite shape below — `api-tasks` / `coding-tasks` / `autonomy-tasks` / `downstream-update-tasks` — is the aspirational target. It requires deterministic-mock backends per task and validators per case, which the harness has scaffolding for (`groundTruth.checks[]`, Zod `structured-output` checks, deterministic scorer) but hasn't fully populated. Until it lands, the pipeline runs the 12-case `agent-benchmark` suite and reports the same axes (success, tokens, cost, autonomy) via the mapping above.

| Suite (planned) | What it measures | Task count | Metric |
|-------|------------------|------------|--------|
| `api-tasks` | Call the right endpoint with the right params from a natural-language ask against a Postman workspace | 30 | Task success rate, tokens per successful task, wall-clock |
| `coding-tasks` | Fix or extend code that calls the same APIs (SWE-bench-lite-style, scoped to API-integration bugs) | 20 | Pass@1, tokens per task, wall-clock |
| `autonomy-tasks` | Multi-step goals that require chaining 3+ endpoints with no human turn (τ-bench-style) | 15 | Goal completion rate, tool-call efficiency (calls-per-goal), tokens per goal |
| `downstream-update-tasks` | Given an upstream API change (new version, deprecated field, renamed param, tightened auth, changed response shape), identify every downstream consumer and generate correct patches for each | 20 | Consumer recall (%), consumer precision (%), patch correctness (pass@1), tokens per completed migration, wall-clock |

**Why `downstream-update-tasks` matters.** A vanilla model sees the upstream change and has to grep-and-guess across the codebase — it doesn't know which collections, environments, integrations, or repos call the endpoint, and it doesn't know which fields are actually read downstream. The context graph carries that topology: `endpoint → consumers → the specific request/response fields each one touches`. In practice this collapses a "read every file that mentions `/v1/users`" search into "traverse three edges of the graph." When this suite ships in the harness, its `dependency_recall_delta`, `dependency_precision_delta`, and `migration_pass_delta` will flow into `providerDeltas` alongside the existing metrics.

### Stage 3 — Generate visuals (target: ≤ 10 min)

Follow the `dataviz` skill's conventions for palette, mark specs, and legend rules. Produce PNGs at 2× density so they read well on LinkedIn and X. Every chart is generated from the harness's return payloads — `results/skill-input.json` for aggregates and per-(agent, model, provider) deltas, and `runs/<id>/cases.jsonl` (in the workflow artifact) for per-case detail. The chart and the number cannot disagree because they share a source file.

Required charts (all derivable from the current 12-case `agent-benchmark` shape):

1. **Bar chart — pass rate.** One bar pair per `(agent, model)` row that has both a baseline and a `+cg` variant in the run. X ticks show `<agent>@<short-model>`; two bars per group (`baseline`, `+cg`); delta inline. Source: `providerDeltas[]` for the paired rows, `aggregate.perModel[<target>].passRate` for the raw numbers.
2. **Grouped bar — output tokens per passed case.** Same X axis as (1). Bars = `totalOutputTokens / passCount` for `baseline` vs `+cg`. `token_delta_pct` labeled on top of the `+cg` bar. Source: `aggregate.perModel[<target>].{totalOutputTokens, passRate}` × `caseCount`.
3. **Bar chart — cost per passed case in USD.** Same layout as (2), Y = `totalCostUsd / passCount`. Source: `aggregate.perModel[<target>].{totalCostUsd, passRate}`.
4. **Grouped bar — mean score by category.** Three groups (`build` / `find` / `ask`), one bar cluster per `(agent, model)` × `{baseline, +cg}` within each. Surfaces category-specific wins for the graph (usually `find` benefits most). Source: `perCategoryByTarget[]`.
5. **Scatter — quality vs latency tradeoff.** One point per `(agent, model, condition)`. X = `meanScore`, Y = `p50LatencyMs`. `+cg` points should sit right of their base (higher quality) but usually a bit above (added lookup time); the caption calls out whether the delta is worth the latency. Source: `aggregate.perModel[<target>].{meanScore, p50LatencyMs}`.
6. **Radar (optional) — judge dimensions.** Five axes = the LLM-judge dimensions for the dominant category (or a union — `problem_understanding / plan_quality / completeness / actionability / risk`), averaged across the run's cases per condition. One polygon per `(agent, model, condition)` triple. Source: `runs/<id>/cases.jsonl` → `scores.llmJudge.details.dimensions`.
7. **Header image** — hand off to `/devrel-skills:blog-header-image` with a prompt like `Postman context graph amplifying <model-name>` (2560×1355 PNG, no text).

Multi-provider runs (harness supports `+orbit` and additional providers alongside `+cg`) fan out charts 1–5 into one panel per provider so the delta view stays clean.

Chart script location: `skills/model-context-graph-comparison/references/make_charts.py` (matplotlib, uses the dataviz palette).

**Charts blocked on v2 of the pipeline** (see Stage 2.5 — need the four-suite / downstream-update shape to exist first):

- **Line chart — cumulative goal completion over tool-call budget** (autonomy suite). Requires per-case tool-call traces from Claude/Codex too, not just Devin/Cursor. The harness's `diagnostics.toolCallCount` is populated but zero for Claude/Codex until they get a tool set.
- **Scatter — consumer recall vs consumer precision** (downstream-update suite). Requires a `downstream-update-tasks` suite with ground-truth `consumers_identified` / `ground_truth_consumers` fields — planned, not shipped.
- **Stacked bar — migration cost split into `discovery` vs `patching`** — same v2 dependency.

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
<Model> ships today. Across build / find-issue / ask engineering tickets,
Postman's context graph lifts judge score by X%, changes pass rate by Y
percentage points, and shifts cost per passed task by Z% for
<agent + model triple with the strongest delta>. Full per-triple table below.

## Why it matters (qualitative)
- The model isn't the bottleneck; the *context* it's given is.
- The context graph replaces "here are 800 API docs, figure it out" with
  "here is the exact slice you need."
- For find-issue and blast-radius tasks, the graph is the difference between
  a plausible narrative and a correct one — those cases benefit most.
- Attribution matters: the same graph can help Claude Opus more than
  Claude Sonnet on the same task set. Every delta is per (agent, model, provider).

## The three prompt categories
### Build (5 cases)
<chart 1 embed for pass rate + chart 4 embed for score-by-category>
<paragraph with 1–2 concrete prompt examples and what changed>

### Find (3 cases)
<chart 4 embed for score-by-category>
<paragraph — this category usually benefits the most from the graph>

### Ask (4 cases)
<chart 4 embed>
<paragraph — OWASP review + endpoint drift tend to live here>

## Token economics
<chart 2 + 3 embed>
<table: raw numbers per (agent, model), baseline vs +cg>

## Latency cost
<chart 5 embed>
Every context-graph call adds a lookup step. Report the median added latency
per prompt and whether it was worth the quality delta.

## Judge dimensions (optional)
<chart 6 embed if generated>
Where does the graph help most: understanding, planning, completeness, risk,
or actionability? Call out the top-two dimensions per (agent, model).

## Reproducing this
<link to data.csv, the harness run URL, and the exact prompt file
`src/evals/agent-benchmark.ts` at the commit that ran>

## What we're shipping
<the on-model-release.yml commit that bumped the MODEL constant in the
relevant adapter, link to the diff>
```

### Stage 5 — Regenerate the harness (target: ≤ 5 min)

Emit `harness/YYYYMMDD-<slug>.json`:

```json
{
  "model": "<vendor/model-id>",
  "context_window": <int>,
  "pricing": {"input_per_1m": <float>, "output_per_1m": <float>},
  "tools": [
    {"name": "context_graph.query", "schema_ref": "postman.context_graph.v1.stub", "endpoint": "POST /graphs/{workspace_id}/query"},
    {"name": "context_graph.consumers", "schema_ref": "postman.context_graph.v1.stub", "endpoint": "GET /graphs/{workspace_id}/consumers"},
    {"name": "context_graph.diff", "schema_ref": "postman.context_graph.v1.stub", "endpoint": "GET /graphs/{workspace_id}/diff"},
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

1. **Twitter/X** — 5–7 tweet thread. Tweet 1: headline delta for the strongest (agent, model, provider) triple. Tweet 2: chart 1 (pass-rate per pair, baseline vs +cg). Tweet 3: chart 2 (output tokens per passed case, with `token_delta_pct` label). Tweet 4: chart 4 (score by category — call out the category with the biggest lift; usually `find`). Tweet 5: chart 5 (quality-vs-latency tradeoff — be honest about the added lookup time). Tweet 6: links to the study. Tweet 7 (optional): the workflow-run URL from `triggerContext.workflowRunUrl` so anyone can see the raw artifacts.
2. **LinkedIn** — long-form post, chart 1 as the cover image, chart 4 inline. CTA: read the study, try the harness config, click through to `buildwithtalia/ai-harness`.
3. **YouTube Short** — 30–60s script + b-roll callouts (charts, terminal, Postman UI). Written to `posts/*-youtube-short.md`; production hand-off is manual for now.
4. **Blog** — stage the study to WordPress via `/devrel-skills:blog-wordpress-stage` as a draft with the header image and SEO frontmatter.
5. **Discord** — post a short announcement in `#announcements` with the headline delta and a link to the blog.

Every posted URL is recorded in `run-log-YYYYMMDD-<slug>.md`.

## Guardrails

- **Never post an unfavorable result silently.** If any category (`build` / `find` / `ask`) shows the context graph making the model *worse* — negative `meanScoreDelta` or `passRateDelta` for that `(agent, model, +cg)` triple — halt at Stage 4 and require a human before Stage 6. Include the negative delta in the study body regardless; do not hide it.
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
