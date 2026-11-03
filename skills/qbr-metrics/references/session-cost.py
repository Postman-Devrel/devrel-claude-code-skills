#!/usr/bin/env python3
"""Estimate the tokens and API-list-price cost of the Claude Code session that produced a report.

Usage: session-cost.py OUT_DIR [--since ISO_TIMESTAMP] [--transcript PATH]
Writes OUT_DIR/cost.json. Standard library only.

Token counts are read from the session transcript (~/.claude/projects/<project>/<session>.jsonl),
one usage record per assistant message. The transcript is the main session only; sub-agent
sessions are not included. Without --since, the whole session is counted.

The dollar figure is an estimate at Claude API list prices (per million tokens), not an invoice:
a Claude subscription or enterprise agreement may bill differently. Prices below come from the
claude-api skill's model table (cached 2026-09-25) and its prompt-caching reference: cache reads
are listed per model, cache writes are 1.25x (5-minute) and 2x (1-hour) the base input price.
A model not in the table gets token counts and no dollar figure.
"""
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone

# model id -> (input, output, cache_read) in USD per million tokens
PRICES = {
    "claude-sonnet-5-5": (2.00, 10.00, 0.20),
    "claude-opus-5-5": (4.00, 20.00, 0.20),
    "claude-fable-5-1": (10.00, 50.00, 0.25),
    "claude-haiku-4-5": (1.00, 5.00, 0.10),
}
PRICE_SOURCE = "Claude API list prices from the claude-api skill (cached 2026-09-25)"


def find_transcript():
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
    files = glob.glob(os.path.expanduser(f"~/.claude/projects/{slug}/*.jsonl"))
    if not files:  # run from another directory: fall back to the most recently written transcript
        files = glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl"))
    return max(files, key=os.path.getmtime) if files else None


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    out_dir = args[0]
    since = parse_ts(args[args.index("--since") + 1]) if "--since" in args else None
    path = args[args.index("--transcript") + 1] if "--transcript" in args else find_transcript()
    if not path or not os.path.exists(path):
        result = {"available": False, "reason": "session transcript not found"}
    else:
        by_id = {}  # a message can be logged more than once while streaming; keep the last
        first = last = None
        with open(path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                m = r.get("message") or {}
                u = m.get("usage")
                if r.get("type") != "assistant" or not u or not r.get("timestamp"):
                    continue
                ts = parse_ts(r["timestamp"])
                if since and ts < since:
                    continue
                by_id[m.get("id") or r.get("uuid")] = (m.get("model"), u)
                first = first or ts
                last = ts
        totals, models = {"input": 0, "output": 0, "cache_read": 0, "cache_write_5m": 0, "cache_write_1h": 0}, {}
        cost, priced = 0.0, True
        for model, u in by_id.values():
            cc = u.get("cache_creation") or {}
            w5 = cc.get("ephemeral_5m_input_tokens", u.get("cache_creation_input_tokens", 0) if not cc else 0)
            w1 = cc.get("ephemeral_1h_input_tokens", 0)
            t = {"input": u.get("input_tokens", 0), "output": u.get("output_tokens", 0),
                 "cache_read": u.get("cache_read_input_tokens", 0), "cache_write_5m": w5, "cache_write_1h": w1}
            for k, v in t.items():
                totals[k] += v
            models[model] = models.get(model, 0) + 1
            if model in PRICES:
                pin, pout, pread = PRICES[model]
                cost += (t["input"] * pin + t["output"] * pout + t["cache_read"] * pread
                         + t["cache_write_5m"] * pin * 1.25 + t["cache_write_1h"] * pin * 2.0) / 1e6
            else:
                priced = False
        result = {
            "available": True, "messages": len(by_id), "models": models, "tokens": totals,
            "total_tokens": sum(totals.values()),
            "cost_usd": round(cost, 2) if priced and by_id else None,
            "price_source": PRICE_SOURCE,
            "scope": "since " + since.isoformat() if since else "whole session, including building the skill",
            "counted_through": last.isoformat() if last else None,
            "note": "Estimate at API list prices; main session only (no sub-agents); not an invoice.",
        }
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "cost.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
