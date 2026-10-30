#!/usr/bin/env python3
"""Convert a blog markdown file to WordPress-ready HTML. Saves to /tmp/wp-post-content.html."""
import subprocess, sys, re

INPUT_FILE = "INPUT_FILE"  # Replace with actual markdown path

subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown", "pymdown-extensions", "-q"])
import markdown

with open(INPUT_FILE, "r") as f:
    content = f.read()

parts = content.split("---", 2)
body = parts[2].strip() if len(parts) >= 3 else content.strip()

# Strip the leading H1 — it goes into the WordPress title field, not the body
body = re.sub(r'^#\s+.+\n*', '', body, count=1).strip()

# superfences (not fenced_code) so ``` blocks nested in list items convert too.
# The highlight config keeps the <pre class="codehilite"><code class="language-x"> markup.
html = markdown.markdown(
    body,
    extensions=["pymdownx.superfences", "pymdownx.highlight", "tables", "toc"],
    extension_configs={"pymdownx.highlight": {"css_class": "codehilite", "use_pygments": False}},
)

with open("/tmp/wp-post-content.html", "w") as f:
    f.write(html)

print(f"HTML saved to /tmp/wp-post-content.html ({len(html)} chars)")
