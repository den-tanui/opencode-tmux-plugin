#!/usr/bin/env bash
# open.sh — receives "<directory>\t<session-id>" and opens a tmux window with opencode
# Logic:
# 1. Extract directory name (basename) as session name
# 2. If tmux session exists → switch to it, create new window
# 3. If not → create new tmux session (with default window)
# 4. Run opencode --session {session-id} OR opencode sessions list (if in dir mode)

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

# Use directory basename as session name
SESSION_NAME=$(basename "$DIR")

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
	# Session exists - switch to it and create a new window
	echo "Switching to existing tmux session: $SESSION_NAME"
	tmux switch-client -t "$SESSION_NAME"

	# Create a new window with the directory
	WINDOW_NAME="opencode"
	tmux new-window -n "$WINDOW_NAME" -c "$DIR" -t "$SESSION_NAME"
	tmux select-window -t "$SESSION_NAME:$WINDOW_NAME"

	# Run command in the new window
	if [ "$SID" = "dir" ]; then
		tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME" "opencode sessions list" Enter
	else
		tmux send-keys -t "$SESSION_NAME:$WINDOW_NAME" "opencode --session $SID" Enter
	fi
else
	# Session doesn't exist - create it (comes with default window)
	echo "Creating new tmux session: $SESSION_NAME"
	tmux new-session -d -s "$SESSION_NAME" -c "$DIR"
	tmux switch-client -t "$SESSION_NAME"

	# Run command in the default window
	if [ "$SID" = "dir" ]; then
		tmux send-keys -t "$SESSION_NAME" "opencode sessions list" Enter
	else
		tmux send-keys -t "$SESSION_NAME" "opencode --session $SID" Enter
	fi
fi
