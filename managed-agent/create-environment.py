#!/usr/bin/env python3
"""
Create a cloud environment for the blog-pipeline managed agent.

Usage:
    python3 create-environment.py

Prints the environment ID — save it for use with run-session.py.
"""

import json
import os
import sys
import urllib.error
import urllib.request

API_BASE = "https://api.anthropic.com/v1"
BETA_HEADER = "managed-agents-2026-04-01"


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Error: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    return key


def make_request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{API_BASE}/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "x-api-key": get_api_key(),
            "anthropic-version": "2023-06-01",
            "anthropic-beta": BETA_HEADER,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    print("Creating cloud environment...")
    result = make_request("POST", "environments", {
        "name": "blog-pipeline-env",
        "config": {
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    })

    print(f"\nEnvironment created.")
    print(f"  ID:   {result['id']}")
    print(f"  Name: {result['name']}")
    print(f"\nSave this environment ID:")
    print(f"  BLOG_PIPELINE_ENV_ID={result['id']}")


if __name__ == "__main__":
    main()
