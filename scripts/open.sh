#!/usr/bin/env bash
# open.sh — receives "<directory>\t<session-id>" and opens a tmux window with opencode
# If a window for the session already exists, switches to it instead.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT="$1"
DIR=$(printf '%s' "$INPUT" | cut -f1)
SID=$(printf '%s' "$INPUT" | cut -f2)

[ -z "$DIR" ] && exit 0
[ -z "$SID" ] && exit 0
[ ! -d "$DIR" ] && {
	echo "opencode-tmux-plugin: directory not found: $DIR" >&2
	exit 1
}

# Window name derived from session id (first 8 chars)
WIN_NAME="opencode-${SID:0:8}"

# If a window for this session already exists anywhere, switch to it
existing=$(tmux list-windows -a -F "#{session_name}:#{window_name}" 2>/dev/null |
	grep ":${WIN_NAME}$" | head -1 || true)

if [ -n "$existing" ]; then
	echo "Switching to existing window: $existing"
	tmux switch-client -t "$existing"
	exit 0
fi

# Create a new window in the current session and run opencode
CURRENT_SESSION=$(tmux display-message -p '#S')
CURRENT_CLIENT=$(tmux display-message -p '#{client_name}')

# Use the directory basename for better readability
DIR_NAME=$(basename "$DIR")
DISPLAY_NAME="${DIR_NAME:0:20}-${SID:0:6}"

tmux new-window -n "$WIN_NAME" -c "$DIR" -t "${CURRENT_SESSION}:"
tmux send-keys -t "${CURRENT_SESSION}:${WIN_NAME}" "opencode --session $SID" Enter
tmux switch-client -c "$CURRENT_CLIENT" -t "${CURRENT_SESSION}:${WIN_NAME}"

echo "Created new window: $WIN_NAME for session $SID"
