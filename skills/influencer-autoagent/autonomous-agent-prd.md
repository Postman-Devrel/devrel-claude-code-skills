Our big audacious goal is to launch an autonomous API engineer on June 1. Building this engineer means that we have to build some new capabilities and enhance all existing capabilities. The layers of thinking that we need to achieve this means thinking about the product across these layers and we need to execute on all of them:

AI Agents - Build internal and support external agents

Search - Help agents search and discover any relevant private, partner, or public API

Execution - Execute API calls, workflows, or tests

Simulation - Create simulated realities for agents to be trained in

API Infrastructure - Core infrastructure on which APIs and Agents can be run

In this doc, I wanted to lay out the components of the agent itself:

Agentic Loop

Invoke agent and hand over a task to it

Agent is invoked and starts running operations in the cloud

Agent can execute API calls, run collections, lint specs, do deep research - essentially anything that is possible through Postman, through the LLM, or through tools made available to it through an MCP Catalog built for the agent.

Agent can also execute a browser based front-end application to run API tests using Playwright to test the UI-API layer

Agent can execute database calls for SQL and No-SQL type databases to test the API-DB layer if provided a database schema to test with.

Agent can use “simulations” to re-create the “outer” world for the API or the application being built or tested

Agent progress is reported within the Postman platform in the existing Chat UI

Agent completes work and reports results. Results are associated with “proof-of-work” as collections, specs, flows etc as other artifacts

Agent can create a temporary cloud workspace for the human to review the work manually if needed (for example to verify API calls or run tests that the agent said it did)

Agent can write code and submit PRs. The agent can do this by invoking other coding agents.

Agent reports completion of the task through Postman notifications.

 

Agent Design

The agent needs to run in the cloud and should be able to take up tasks from anywhere - from the Postman app, the CLI, an API call, or through Slack. Invoking the agent should be as simple as typing @Postman with a prompt.

The agent should be able to run for long durations and should work towards finishing the task allocated to it.

The agent should have complete information about the customer’s API world through the API catalog

The agent should run in a fully sandboxed environment. Internet access should be off by default and only allowed APIs from the Postman platform as well as APIs that the agent is allowed to access should be run through the environment. The environment should capture API calls that the agent tries to make.

The agent should be able to operate Postman capabilities through the Postman CLI.

The agent should be given access to an API key through an explicit step in a shared vault.

The system’s execution layer for API calls should be separate from the agent. The system execution layer should enforce checks.

The agent should never have access to production keys. Any keys that the agent accesses is through the vault. Existing environment variables won’t work.

The agent should be able to call additional APIs from the Postman environment using MCP - for searching APIs or dependencies, or calling on API catalog data.

The agent should be able to invoke an organization’s existing coding agent and plug into existing rules around which they write code.

Agent can be triggered through events that happen through Postman Monitors or through CI pipelines or through recurring automations built through Agent Mode itself.

 

Use Cases

API Testing & Quality Assurance — An engineer pushes a PR and triggers the agent via CLI or Slack. It spins up a sandbox, pulls the workspace context, grabs API keys from the vault, runs the full test suite against captured API calls, and posts results back to the PR. No manual setup needed.

API Exploration & Documentation — Point the agent at an undocumented or unfamiliar API. It explores endpoints, runs calls across environments, captures the request/response pairs, and generates collections and markdown documentation in a Postman workspace for the team to review.

Web App API Discovery — The agent launches an embedded browser via Playwright, navigates a web application, and captures all underlying API calls. It then organizes these into collections, creates tests for them, and produces a map of how the frontend interacts with backend services.

End-to-End Acceptance Testing — Product or QA defines acceptance criteria in human-readable form. The agent translates these into Playwright browser tests combined with API-level assertions, runs them, captures screenshots and video, and delivers a proof-of-work report.

Mock Server Generation — When a dependency API isn't available, the agent simulates it by spinning up mock servers based on captured or documented endpoints. This unblocks frontend or integration work without waiting on other teams.

Database Validation — After running API calls, the agent uses the embedded SQL client to verify that the expected data was written, updated, or deleted in the database, closing the loop between API behavior and persistence.

CI/CD Integration & PR Generation — The agent runs as part of a pipeline: executes tests, validates behavior, captures evidence (screenshots, video, logs), writes results to markdown, and generates a PR with the finished work — collections, flows, test results, and proof of work all included.

Environment Parity Checking — The agent takes a workspace and runs the same API calls across staging, QA, and production environments, flagging discrepancies in responses, schemas, or performance.

Regression Detection — On every code change, the agent re-runs captured API interactions and Playwright flows, compares against baselines, and surfaces any regressions.

 

Capabilities needed in the core Postman platform (improvements or net new)

SQL Client support [New] - Postman needs to support SQL through the UI as well as the CLI. This is a popular request for human developers too who need to tie together API testing and Database testing.

Playwright support [New] - Playwright has upended the UI testing market and is the preferred solution over other providers. Postman needs to leverage Playwright as a plugin inside the CLI and help test the UI/API boundary. We won’t be replicating what Playwright does but instead augmenting testing of the APIs that are used in UIs.

Background Agents [New] - Core infra primitive for Agent Mode to run in the cloud.

Simulations [New] - Simulators are built on top of the existing mock servers framework. We also need cloud based simulations that are automatically kept up to date with an organization’s APIs. A default simulation needs to be the current state of a company’s services.

Search [Improvement] - Postman’s search needs to be flawless and should bring up relevant APIs

MCP Gateway [New] - The MCP Gateway needs to connect to Postman’s MCP Catalog which itself needs to be improved to assimilate all MCP servers easily - not just the ones generated through Postman

Code Mode for Agents [New] - Ability for the autonomous engineer to search and find the right APIs or services to get a job done is going to be a core capability.

Official Postman MCP and Official Postman API [Improvements] - Need to be treated as first-class artifacts to integrate with other agents.

Postman UI [Improve] - Show long running agents

Postman Skill/Plugin/Extensions for other Coding Agents [New] - Embed the ability to call Postman from anywhere.