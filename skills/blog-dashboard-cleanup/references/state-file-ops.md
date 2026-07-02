# Dashboard State File Operations

## Path Resolution

```python
import os, json, fcntl

plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
state_path = os.path.join(plugin_root, "dashboard", "state.json")
```

## Read State (shared lock)

```python
if not os.path.exists(state_path):
    print("Dashboard state file not found — is the dashboard installed?")
    print(f"Expected: {state_path}")
    raise SystemExit(1)

with open(state_path, "r") as f:
    fcntl.flock(f, fcntl.LOCK_SH)
    try:
        data = json.load(f)
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)

cards = data.get("cards", [])
```

## Filter Cards

```python
arg = "ARGUMENT_HERE"  # None or "--all"
remove_all = arg and arg.strip().lower() == "--all"

PRE_STAGING_STAGES = {"ideas", "writing", "copyedit", "header_image", "creating"}

if remove_all:
    to_remove = cards
    to_keep = []
else:
    to_remove = [c for c in cards if c.get("stage") in PRE_STAGING_STAGES]
    to_keep = [c for c in cards if c.get("stage") not in PRE_STAGING_STAGES]
```

## Write State (exclusive lock)

```python
data["cards"] = to_keep

with open(state_path, "w") as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    try:
        json.dump(data, f, indent=2)
    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
```
