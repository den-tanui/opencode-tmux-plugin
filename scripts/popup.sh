#!/usr/bin/env bash
# opencode-sessions-popup.sh — launched inside the tmux popup
# Runs picker.py piped through fzf, then calls open.sh with the selection.

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Get session directory from environment or use default
SESSION_DIR="${OPENCODE_SESSIONS_DIR:-/home/.local/share/opencode/storage/session}"

# Check dependencies
if ! command -v python3 &>/dev/null; then
	echo "Error: python3 is required but not installed" >&2
	read -p "Press Enter to continue..."
	exit 1
fi

if ! command -v fzf &>/dev/null; then
	echo "Error: fzf is required but not installed" >&2
	read -p "Press Enter to continue..."
	exit 1
fi

# Check if picker.py exists
if [ ! -x "$PLUGIN_DIR/scripts/picker.py" ]; then
	echo "Error: picker.py not found or not executable" >&2
	read -p "Press Enter to continue..."
	exit 1
fi

# Run fzf with the picker and handle selection
selected=$(python3 "$PLUGIN_DIR/scripts/picker.py" 2>/dev/null |
	fzf \
		--ansi \
		--delimiter='\t' \
		--with-nth=1 \
		--nth=1 \
		--no-sort \
		--layout=reverse-list \
		--border=rounded \
		--border-label=" 󱜚 OpenCode Sessions " \
		--border-label-pos=2 \
		--color="border:#0ABDC6,label:#0ABDC6,header:#D300C4" \
		--color="bg+:#111133,fg+:#ffffff,hl+:#D300C4,hl:#0ABDC6" \
		--color="pointer:#D300C4,marker:#0ABDC6,spinner:#0ABDC6" \
		--prompt="  " \
		--pointer="▶" \
		--header="  enter: open   esc: cancel   tab: expand   J/K: scroll   g/G: top/bottom" \
		--preview="python3 $PLUGIN_DIR/scripts/picker.py --expanded 2>/dev/null | head -50" \
		--preview-window="right:45%:wrap" \
		--bind="ctrl-j:down,ctrl-k:up" \
		--bind="J:preview-down,K:preview-up" \
		--bind="ctrl-d:preview-half-page-down,ctrl-u:preview-half-page-up" \
		--bind="ctrl-f:preview-page-down,ctrl-b:preview-page-up" \
		--bind="g:preview-top,G:preview-bottom" \
		--bind="/:toggle-preview" \
		--bind="tab:execute-silent(echo expanded)+reload(python3 $PLUGIN_DIR/scripts/picker.py --expanded)" \
		2>/dev/null |
	awk -F'\t' '{print $2"\t"$3}') # extract path<TAB>session_id

# Exit on cancel or empty selection
[ -z "$selected" ] && exit 0
dir=$(printf '%s' "$selected" | cut -f1)
[ -z "$dir" ] && exit 0

# Call open.sh with the selection
bash "$PLUGIN_DIR/scripts/open.sh" "$selected"
