#!/usr/bin/env python3
"""Post the Friday auto-publish notification (or failure/skip notice) to #devrel-staff."""
import os, json, urllib.request

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
CHANNEL = "#devrel-staff"

MESSAGE_TEXT = "MESSAGE_TEXT_HERE"  # Replace with the formatted message

req = urllib.request.Request(
    "https://slack.com/api/chat.postMessage",
    data=json.dumps({"channel": CHANNEL, "text": MESSAGE_TEXT, "unfurl_links": False}).encode(),
    headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}", "Content-Type": "application/json; charset=utf-8"},
    method="POST",
)
resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
if not resp.get("ok"):
    raise RuntimeError(f"Slack notification failed: {resp.get('error')}")
print(f"Slack notification sent to {CHANNEL}")
