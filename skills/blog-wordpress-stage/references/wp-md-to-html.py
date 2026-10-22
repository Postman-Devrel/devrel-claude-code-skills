#!/usr/bin/env python3
"""Convert a blog markdown file to WordPress-ready HTML. Saves to /tmp/wp-post-content.html."""
import subprocess, sys, re

INPUT_FILE = "INPUT_FILE"  # Replace with actual markdown path

subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown", "-q"])
import markdown

with open(INPUT_FILE, "r") as f:
    content = f.read()

parts = content.split("---", 2)
body = parts[2].strip() if len(parts) >= 3 else content.strip()

# Strip the leading H1 — it goes into the WordPress title field, not the body
body = re.sub(r'^#\s+.+\n*', '', body, count=1).strip()

html = markdown.markdown(body, extensions=["fenced_code", "codehilite", "tables", "toc"])

# The blog theme styles plain <blockquote> as a 24px pull quote with no border or background,
# so prompts and agent replies read like body text. Turn each blockquote into a styled box:
# a blockquote starting with <p><strong> is an agent reply, anything else is a prompt.
# Inline styles (not a stylesheet) because we can't ship CSS to the theme from here.
BOX = "margin:24px 0;padding:16px 20px;border-radius:6px;font-size:16px;line-height:1.6;"
LABEL = "margin:0 0 8px;font-size:12px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;"
CHAT_STYLES = {
    "prompt": (BOX + "background:#FFF1EB;border-left:4px solid #FF6C37;", LABEL + "color:#A13D12;", "Prompt"),
    "agent": (BOX + "background:#F7F7F7;border:1px solid #E6E6E6;border-left:4px solid #212121;", LABEL + "color:#6B6B6B;", "Agent"),
}
chat_counts = {"prompt": 0, "agent": 0}


def chat_box(m):
    inner = m.group(1).strip()
    kind = "agent" if inner.startswith("<p><strong>") else "prompt"
    paras = re.findall(r"<p>(.*?)</p>", inner, flags=re.S)
    # Agent replies legitimately mix a bold heading with plain paragraphs; a *prompt* that
    # later has a bold-led paragraph is the merged case.
    if kind == "prompt" and any(p.startswith("<strong>") for p in paras):
        # Consecutive blockquotes separated by a blank line merge into one in Python-Markdown.
        print("WARNING: a blockquote mixes plain and bold-led paragraphs (a prompt and an agent reply "
              "merged?). Add a lead-in sentence between them in the markdown: "
              f"{re.sub(r'<[^>]+>', '', paras[0])[:60]!r}")
    chat_counts[kind] += 1
    box_style, label_style, label = CHAT_STYLES[kind]
    return (f'<div class="pm-chat pm-chat-{kind}" style="{box_style}">'
            f'<p style="{label_style}">{label}</p>{inner}</div>')


html = re.sub(r"<blockquote>(.*?)</blockquote>", chat_box, html, flags=re.S)
print(f"Styled {chat_counts['prompt']} prompts and {chat_counts['agent']} agent replies "
      f"({html.count('<blockquote')} blockquotes remaining)")

with open("/tmp/wp-post-content.html", "w") as f:
    f.write(html)

print(f"HTML saved to /tmp/wp-post-content.html ({len(html)} chars)")
