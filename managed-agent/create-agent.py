#!/usr/bin/env python3
"""
Create (or update) the blog-pipeline managed agent on the Anthropic API.

Usage:
    python3 create-agent.py              # create a new agent
    python3 create-agent.py --update <AGENT_ID>  # update an existing agent

Requirements:
    - ANTHROPIC_API_KEY set in your environment
    - Beta access to managed agents (https://claude.com/form/claude-managed-agents)

The agent ID is printed on success — save it, you'll need it to create sessions.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://api.anthropic.com/v1"
BETA_HEADER = "managed-agents-2026-04-01"
MODEL = "claude-opus-4-7"

SYSTEM_PROMPT_FILE = Path(__file__).parent / "blog-pipeline-system-prompt.md"


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return key


def make_request(method: str, path: str, body: dict | None = None) -> dict:
    api_key = get_api_key()
    url = f"{API_BASE}/{path}"
    data = json.dumps(body).encode() if body else None

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": BETA_HEADER,
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"HTTP {e.code} {e.reason}: {error_body}", file=sys.stderr)
        sys.exit(1)


def load_system_prompt() -> str:
    if not SYSTEM_PROMPT_FILE.exists():
        print(f"Error: {SYSTEM_PROMPT_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    return SYSTEM_PROMPT_FILE.read_text()


def create_agent(system_prompt: str) -> dict:
    payload = {
        "name": "blog-pipeline",
        "description": "Full blog creation pipeline for Postman DevRel — write, copyedit, generate header image, stage to WordPress, and optionally schedule.",
        "model": MODEL,
        "system": system_prompt,
        "tools": [
            {
                "type": "agent_toolset_20260401",
                # All tools enabled by default:
                # bash, read, write, edit, glob, grep, web_fetch, web_search
            }
        ],
    }
    return make_request("POST", "agents", payload)


def update_agent(agent_id: str, system_prompt: str, current_version: int) -> dict:
    payload = {
        "version": current_version,
        "system": system_prompt,
    }
    return make_request("PATCH", f"agents/{agent_id}", payload)


def get_agent(agent_id: str) -> dict:
    return make_request("GET", f"agents/{agent_id}")


def main():
    parser = argparse.ArgumentParser(description="Create or update the blog-pipeline managed agent")
    parser.add_argument("--update", metavar="AGENT_ID", help="Update an existing agent instead of creating a new one")
    args = parser.parse_args()

    system_prompt = load_system_prompt()
    print(f"System prompt loaded ({len(system_prompt):,} characters)")

    if args.update:
        agent_id = args.update
        print(f"Fetching current agent version for {agent_id}...")
        current = get_agent(agent_id)
        current_version = current["version"]
        print(f"Current version: {current_version}")

        print("Updating agent...")
        result = update_agent(agent_id, system_prompt, current_version)
        print(f"\nAgent updated successfully.")
        print(f"  ID:      {result['id']}")
        print(f"  Name:    {result['name']}")
        print(f"  Version: {result['version']}")
        print(f"  Model:   {result['model']}")
    else:
        print("Creating agent...")
        result = create_agent(system_prompt)
        print(f"\nAgent created successfully.")
        print(f"  ID:      {result['id']}")
        print(f"  Name:    {result['name']}")
        print(f"  Version: {result['version']}")
        print(f"  Model:   {result['model']}")
        print(f"\nSave this agent ID — you'll need it to create sessions:")
        print(f"  BLOG_PIPELINE_AGENT_ID={result['id']}")

    print(f"\nNext steps:")
    print(f"  1. Create an environment:  python3 create-environment.py")
    print(f"  2. Run a session:          python3 run-session.py --agent {result['id']} --env <ENV_ID> \"<topic>\"")


if __name__ == "__main__":
    main()
