#!/bin/bash
# Hook script: triggers blog-copyeditor after blog-write skill completes
# This runs as a PostToolUse hook on the "Write" tool.
# It checks if the written file looks like a blog post and signals
# Claude to run the copy editor.

# Read the tool input from stdin (JSON with tool_input)
INPUT=$(cat)

# Extract the file path from the tool input
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data.get('tool_input',{}).get('file_path',''))" 2>/dev/null)

# Skip if no file path
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Get just the filename
FILENAME=$(basename "$FILE_PATH")

# Skip non-markdown files
if [[ "$FILENAME" != *.md ]]; then
  exit 0
fi

# Skip known non-blog files
SKIP_FILES=("README.md" "CLAUDE.md" "MEMORY.md" "current-cfps.md" "monthly-newsletters.md" "sentiment-analysis-"*)
for skip in "${SKIP_FILES[@]}"; do
  if [[ "$FILENAME" == $skip ]]; then
    exit 0
  fi
done

# Skip files in .claude/ directory (commands, settings, etc.)
if [[ "$FILE_PATH" == *"/.claude/"* ]]; then
  exit 0
fi

# Skip files in plugin directories
if [[ "$FILE_PATH" == *"/.claude-plugin/"* ]] || [[ "$FILE_PATH" == *"/skills/"* ]] || [[ "$FILE_PATH" == *"/hooks/"* ]]; then
  exit 0
fi

# Skip copyedit report files
if [[ "$FILENAME" == *"-copyedit.md" ]]; then
  exit 0
fi

# If we get here, a blog-like markdown file was written.
# Output a message that will be injected into the conversation.
echo "A blog post file was written: $FILENAME. Run /devrel-skills:blog-copyeditor $FILE_PATH to copy edit it for grammar, syntax, repetitive structures, and SEO optimization."
