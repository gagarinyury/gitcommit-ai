"""Hook script template for prepare-commit-msg."""


def get_hook_template() -> str:
    """Get the prepare-commit-msg hook script template.

    Returns:
        Bash script as string.
    """
    return """#!/usr/bin/env bash
# GitCommit AI - Auto-generated commit messages
# GITCOMMIT_AI_HOOK_VERSION=1.0.0

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2
COMMIT_SHA=$3

# Skip for special commit types (merge, squash, amend, etc.)
if [ -n "$COMMIT_SOURCE" ]; then
    exit 0
fi

# Find gitcommit-ai executable
GITCOMMIT_AI=$(command -v gitcommit-ai 2>/dev/null)
if [ -z "$GITCOMMIT_AI" ]; then
    echo "# GitCommit AI not found in PATH" >> "$COMMIT_MSG_FILE"
    exit 0
fi

# Generate message with timeout (macOS compatible)
TEMP_MSG=$(mktemp)
"$GITCOMMIT_AI" generate 2>/dev/null > "$TEMP_MSG" &
GENERATE_PID=$!

# Wait up to 10 seconds (20 iterations * 0.5s)
for i in {1..20}; do
    if ! kill -0 "$GENERATE_PID" 2>/dev/null; then
        # Process finished
        break
    fi
    sleep 0.5
done

# Kill if still running
if kill -0 "$GENERATE_PID" 2>/dev/null; then
    kill -9 "$GENERATE_PID" 2>/dev/null
    echo "# GitCommit AI generation timeout" >> "$COMMIT_MSG_FILE"
    rm -f "$TEMP_MSG"
    exit 0
fi

# Check if generation succeeded
if [ ! -s "$TEMP_MSG" ]; then
    echo "# GitCommit AI generation failed" >> "$COMMIT_MSG_FILE"
    rm -f "$TEMP_MSG"
    exit 0
fi

# Write generated message
cat "$TEMP_MSG" > "$COMMIT_MSG_FILE" 2>/dev/null || {
    echo "# GitCommit AI: Error writing message" >> "$COMMIT_MSG_FILE"
}

rm -f "$TEMP_MSG"
exit 0
"""
