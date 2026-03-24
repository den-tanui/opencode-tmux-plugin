#!/usr/bin/env bash
# popup.sh — launched inside the tmux popup
# Runs picker.py piped through fzf, then calls open.sh with the selection.
# Press TAB to toggle between all sessions and directory-only mode.

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

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

if [ ! -x "$PLUGIN_DIR/scripts/picker.py" ]; then
	echo "Error: picker.py not found or not executable" >&2
	read -p "Press Enter to continue..."
	exit 1
fi

# Default mode: show all sessions
MODE="all"

while true; do
	# Build picker command based on mode
	if [ "$MODE" = "dirs" ]; then
		PICKER_CMD="python3 $PLUGIN_DIR/scripts/picker.py --dirs-only 2>/dev/null"
		HEADER="  enter: open   esc: cancel   tab: switch to all sessions"
		BORDER_LABEL=" 󱜚 OpenCode Sessions (dirs) "
		OTHER_CMD="python3 $PLUGIN_DIR/scripts/picker.py 2>/dev/null"
	else
		PICKER_CMD="python3 $PLUGIN_DIR/scripts/picker.py 2>/dev/null"
		HEADER="  enter: open   esc: cancel   tab: switch to dirs-only"
		BORDER_LABEL=" 󱜚 OpenCode Sessions "
		OTHER_CMD="python3 $PLUGIN_DIR/scripts/picker.py --dirs-only 2>/dev/null"
	fi

	# Run fzf with reload on TAB
	selection=$(eval "$PICKER_CMD" |
		fzf \
			--ansi \
			--delimiter='\t' \
			--with-nth=1 \
			--nth=1 \
			--no-sort \
			--layout=reverse \
			--border=rounded \
			--border-label="$BORDER_LABEL" \
			--border-label-pos=2 \
			--color="border:#7aa2f7,label:#bb9af7,header:#7aa2f7" \
			--color="bg+:#1a1b26,fg+:#c0caf5,hl+:#bb9af7,hl:#7aa2f7" \
			--color="pointer:#bb9af7,marker:#7aa2f7,spinner:#7aa2f7" \
			--prompt="  " \
			--pointer="▶" \
			--header="$HEADER" \
			--preview="python3 $PLUGIN_DIR/scripts/preview.py {2} {3} 2>/dev/null" \
			--preview-window="right:45%:wrap" \
			--bind="ctrl-j:down,ctrl-k:up" \
			--bind="J:preview-down,K:preview-up" \
			--bind="ctrl-d:preview-half-page-down,ctrl-u:preview-half-page-up" \
			--bind="ctrl-f:preview-page-down,ctrl-b:preview-page-up" \
			--bind="g:preview-top,G:preview-bottom" \
			--bind="/:toggle-preview" \
			--bind="tab:reload($OTHER_CMD)" \
			2>/dev/null)

	# Exit on cancel or empty selection (reload returns empty when cancelled)
	[ -z "$selection" ] && exit 0

	dir=$(printf '%s' "$selection" | cut -f1)
	sid=$(printf '%s' "$selection" | cut -f2)

	[ -z "$dir" ] && exit 0
	[ -z "$sid" ] && exit 0

	# Call open.sh with the selection
	bash "$PLUGIN_DIR/scripts/open.sh" "$selection"
	exit $?
done
