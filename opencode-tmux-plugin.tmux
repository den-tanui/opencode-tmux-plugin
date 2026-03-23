# Run the session picker with fzf popup
bind g run -b "bash -c '\
    SCRIPT_DIR=#{plugin_dir}/scripts; \
    PICKER=\"$SCRIPT_DIR/picker.py\"; \
    PREVIEW=\"$SCRIPT_DIR/preview.py\"; \
    OPEN=\"$SCRIPT_DIR/open.sh\"; \
    if [ -x \"$PICKER\" ] && command -v fzf >/dev/null 2>&1; then \
        # Check tmux version for popup support (3.2+)
        TMUX_VERSION=$(tmux -V | sed 's/tmux //' | cut -d. -f1); \
        if [ \"$TMUX_VERSION\" -ge 3 ]; then \
            tmux display-popup -w '80%' -h '75%' -E \
                \"fzf --with-nth=2.. \
                --bind='enter:execute(echo {} | cut -f2,3 | \"$OPEN\")' \
                --bind='esc:close,ctrl-c:close' \
                --preview='$PREVIEW \$(echo {} | cut -f2) \$(echo {} | cut -f3)' \
                --preview-window='right:45%' \
                --layout=reverse-list \
                < \"$PICKER\"\"; \
        else \
            fzf --with-nth=2.. \
                --bind='enter:execute(echo {} | cut -f2,3 | \"$OPEN\")' \
                --bind='esc:close,ctrl-c:close' \
                --preview='$PREVIEW \$(echo {} | cut -f2) \$(echo {} | cut -f3)' \
                --preview-window='right:45%' \
                --layout=reverse-list \
                < \"$PICKER\"; \
        fi; \
    else \
        bash \"$SCRIPT_DIR/opencode-sessions\" --attach; \
    fi \
'"
# Tmux plugin for managing opencode sessions
# 
# Usage: Source this file in your .tmux.conf
#   source-file /path/to/opencode-tmux-plugin.tmux
#
# Key binding: Prefix + g (configurable)
#   Opens a floating popup with all opencode sessions grouped by directory

# Get the plugin directory path
_plugin_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration options (set before sourcing)
# These must be set with set -g BEFORE sourcing this file

# Key to trigger the session picker (default: g)
if -g @opencode_sessions_key '' &> /dev/null; then
    set -g @opencode_sessions_key 'g'
fi

# Popup dimensions
set -g @opencode_sessions_popup_width '80%'
set -g @opencode_sessions_popup_height '75%'

# Session directory (default: auto-detected)
# set -g @opencode_sessions_dir '/home/.local/share/opencode/storage/session'

# ── Key binding ──────────────────────────────────────────────────────────────

# Run the session picker with fzf popup
bind g run -b "bash -c '\
    SCRIPT_DIR=#{plugin_dir}/scripts; \
    PICKER=\"$SCRIPT_DIR/picker.py\"; \
    PREVIEW=\"$SCRIPT_DIR/preview.py\"; \
    OPEN=\"$SCRIPT_DIR/open.sh\"; \
    WIDTH=#{@opencode_sessions_popup_width}; \
    HEIGHT=#{@opencode_sessions_popup_height}; \
    if [ -x \"$PICKER\" ] && command -v fzf >/dev/null 2>&1; then \
        SELECTED=$(fzf --with-nth=2.. \
            --bind='enter:execute(echo {} | cut -f2,3 | \"$OPEN\")' \
            --bind='esc:close,ctrl-c:close' \
            --preview='$PREVIEW $(echo {} | cut -f2) $(echo {} | cut -f3)' \
            --preview-window='right:45%' \
            --height=\"$HEIGHT\" --width=\"$WIDTH\" \
            --layout=reverse-list \
            < \"$PICKER\"); \
    else \
        bash \"$SCRIPT_DIR/opencode-sessions\" --attach; \
    fi \
'"

# Alternative: run without popup (for older tmux versions or non-fzf mode)
bind G run -b "bash -c '\
    SCRIPT_DIR=#{plugin_dir}/scripts; \
    bash \"$SCRIPT_DIR/opencode-sessions\" --attach \
'"
