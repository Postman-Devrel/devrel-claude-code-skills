# Claude Code Skills

A collection of Claude Code skills used by the Postman Developer Relations team.

## What are Claude Code Skills?

Skills are reusable prompts that extend Claude Code's capabilities for specific tasks. They provide domain expertise and consistent output for common workflows.

## Available Skills

| Skill | Description |
|-------|-------------|
| [devadvocate-blogger](devadvocate-blogger.md) | Write technical blog posts about Postman and APIs with an expert developer advocate voice. Produces content that balances deep technical expertise with approachable teaching, including proper syntax highlighting, links to official documentation, and hands-on examples. |
| [cfp-hunter](cfp-hunter.md) | Fetch links for open CFPs which match our developer profiles. |
[competitor-sentiment](competitor-sentiment.md) | Analyze Reddit comments about API developer tools (Postman, Apigee, Bruno, Insomnia, RapidAPI/Paw, Hopscotch) and generate sentiment rankings by category. Provides 0-100 scores for capabilities like pricing, collaboration, and security with summarized feedback. |

## Installation

To use these skills in your Claude Code setup, copy the skill files to your Claude Code skills directory.

## Configuration

### Reddit API Setup (for competitor-sentiment skill)

The `competitor-sentiment` skill requires Reddit API credentials.

1. **Create a Reddit App:**
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app..." at the bottom
   - Select **"script"** as the app type
   - Name: `competitor-sentiment-analyzer`
   - Redirect URI: `http://localhost:8080`
   - Click "create app"

2. **Get Your Credentials:**
   - `client_id`: The string under your app name
   - `client_secret`: The "secret" field

3. **Set Up Environment Variables:**

   Copy the example file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your credentials:
   ```
   REDDIT_CLIENT_ID=your_actual_client_id
   REDDIT_CLIENT_SECRET=your_actual_client_secret
   REDDIT_USER_AGENT=competitor-sentiment-analyzer/1.0
   ```

   Or export directly in your shell:
   ```bash
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   export REDDIT_USER_AGENT="competitor-sentiment-analyzer/1.0"
   ```


