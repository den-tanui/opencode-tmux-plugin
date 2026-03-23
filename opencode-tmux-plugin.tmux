# opencode-tmux-plugin.tmux
# TPM-compatible tmux plugin for managing OpenCode sessions
#
# Binds a key (default: prefix+g) to open an fzf popup listing all
# OpenCode sessions grouped by project directory.

PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"

# Read user-configurable options (with defaults)
KEY=$(tmux show-option -gv @opencode_sessions_key 2>/dev/null); KEY=${KEY:-g}
WIDTH=$(tmux show-option -gv @opencode_sessions_popup_width 2>/dev/null); WIDTH=${WIDTH:-80%}
HEIGHT=$(tmux show-option -gv @opencode_sessions_popup_height 2>/dev/null); HEIGHT=${HEIGHT:-75%}
DIR=$(tmux show-option -gv @opencode_sessions_dir 2>/dev/null); DIR=${DIR:-/home/.local/share/opencode/storage/session}

# Set the key binding - opens popup with fzf session picker
tmux bind-key "$KEY" display-popup \
  -w "$WIDTH" \
  -h "$HEIGHT" \
  -d "#{pane_current_path}" \
  -e "OPENCODE_SESSIONS_DIR=$DIR" \
  -E "bash $PLUGIN_DIR/scripts/popup.sh"

# Alternative: Terminal mode (no popup) for older tmux versions
tmux bind-key "$KEY" run-shell "bash $PLUGIN_DIR/scripts/opencode-sessions --attach"
