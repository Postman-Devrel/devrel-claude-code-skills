#!/usr/bin/env python3
"""
Run a blog-pipeline session against the managed agent.

Usage:
    python3 run-session.py --agent <AGENT_ID> --env <ENV_ID> "Testing OAuth 2.0 in Postman"
    python3 run-session.py --agent <AGENT_ID> --env <ENV_ID> "blog-output/my-draft.md"

Required environment variables:
    ANTHROPIC_API_KEY
    WP_USERNAME          (passed into the agent session)
    WP_APP_PASSWORD      (passed into the agent session)
    GEMINI_API_KEY       (passed into the agent session)

The session streams agent output in real time.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_BASE = "https://api.anthropic.com/v1"
BETA_HEADER = "managed-agents-2026-04-01"


def get_env(key: str, required: bool = True) -> str | None:
    val = os.environ.get(key)
    if required and not val:
        print(f"Error: {key} environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return val


def make_request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"{API_BASE}/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "x-api-key": get_env("ANTHROPIC_API_KEY"),
            "anthropic-version": "2023-06-01",
            "anthropic-beta": BETA_HEADER,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def stream_session(session_id: str):
    """Stream events from a session using SSE."""
    url = f"{API_BASE}/sessions/{session_id}/stream"
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "x-api-key": get_env("ANTHROPIC_API_KEY"),
            "anthropic-version": "2023-06-01",
            "anthropic-beta": BETA_HEADER,
            "Accept": "text/event-stream",
        },
    )

    with urllib.request.urlopen(req, timeout=600) as resp:
        buffer = ""
        while True:
            chunk = resp.read(1024)
            if not chunk:
                break
            buffer += chunk.decode()
            while "\n\n" in buffer:
                event_str, buffer = buffer.split("\n\n", 1)
                lines = event_str.strip().split("\n")
                event_type = None
                event_data = None
                for line in lines:
                    if line.startswith("event:"):
                        event_type = line[6:].strip()
                    elif line.startswith("data:"):
                        event_data = line[5:].strip()

                if event_type and event_data:
                    yield event_type, event_data


def handle_events(session_id: str) -> str:
    """Stream and display session events, return stop_reason."""
    stop_reason = None

    for event_type, event_data in stream_session(session_id):
        try:
            data = json.loads(event_data)
        except json.JSONDecodeError:
            continue

        if event_type == "agent.message":
            for part in data.get("content", []):
                if part.get("type") == "text":
                    print(part["text"], end="", flush=True)

        elif event_type == "agent.tool_use":
            tool_name = data.get("name", "unknown")
            tool_input = data.get("input", {})
            print(f"\n[Tool: {tool_name}]", flush=True)
            if tool_name == "bash" and "command" in tool_input:
                cmd = tool_input["command"]
                print(f"  $ {cmd[:120]}{'...' if len(cmd) > 120 else ''}", flush=True)
            elif tool_name in ("read", "write", "edit") and "file_path" in tool_input:
                print(f"  {tool_input['file_path']}", flush=True)
            elif tool_name == "web_search" and "query" in tool_input:
                print(f"  Search: {tool_input['query']}", flush=True)

        elif event_type == "session.status_idle":
            stop_reason = data.get("stop_reason", "end_turn")
            print(f"\n\n[Session idle — {stop_reason}]", flush=True)
            break

        elif event_type == "session.status_terminated":
            print(f"\n\n[Session terminated]", flush=True)
            stop_reason = "terminated"
            break

        elif event_type == "session.error":
            print(f"\n[Error: {data}]", flush=True)

    return stop_reason


def send_user_message(session_id: str, text: str):
    make_request("POST", f"sessions/{session_id}/events", {
        "events": [
            {
                "type": "user.message",
                "content": [{"type": "text", "text": text}],
            }
        ]
    })


def main():
    parser = argparse.ArgumentParser(description="Run a blog-pipeline session")
    parser.add_argument("--agent", required=True, metavar="AGENT_ID", help="Agent ID from create-agent.py")
    parser.add_argument("--env", required=True, metavar="ENV_ID", help="Environment ID from create-environment.py")
    parser.add_argument("topic", help="Blog topic, file path, or Google Docs URL")
    args = parser.parse_args()

    # Validate required credentials
    wp_user = get_env("WP_USERNAME")
    wp_pass = get_env("WP_APP_PASSWORD")
    gemini_key = get_env("GEMINI_API_KEY")

    print(f"Creating session for agent {args.agent}...")
    session = make_request("POST", "sessions", {
        "agent": args.agent,
        "environment_id": args.env,
        "title": f"Blog pipeline: {args.topic[:60]}",
        "env": {
            "WP_USERNAME": wp_user,
            "WP_APP_PASSWORD": wp_pass,
            "GEMINI_API_KEY": gemini_key,
        },
    })

    session_id = session["id"]
    print(f"Session created: {session_id}")
    print(f"Topic: {args.topic}\n")
    print("=" * 60)

    # Send the user message and stream the response
    send_user_message(session_id, args.topic)
    stop_reason = handle_events(session_id)

    print("=" * 60)

    # Fetch final usage
    final = make_request("GET", f"sessions/{session_id}")
    usage = final.get("usage", {})
    if usage:
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cache_reads = usage.get("cache_read_input_tokens", 0)
        print(f"\nToken usage:")
        print(f"  Input:        {input_tokens:,}")
        print(f"  Output:       {output_tokens:,}")
        print(f"  Cache reads:  {cache_reads:,}")

    if stop_reason == "requires_action":
        print("\nSession paused — requires user input. The agent is waiting for a response.")
        print(f"Session ID: {session_id}")


if __name__ == "__main__":
    main()
