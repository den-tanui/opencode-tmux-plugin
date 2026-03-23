#!/usr/bin/env bash
# Plugin setup script - run this to install dependencies and configure tmux

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== opencode-tmux-plugin Setup ==="
echo

# Check dependencies
log_info "Checking dependencies..."

# Check jq
if command -v jq &>/dev/null; then
	log_info "jq: installed"
else
	log_error "jq is required but not installed"
	log_info "Install with: brew install jq (macOS) or apt install jq (Linux)"
	exit 1
fi

# Check opencode
if command -v opencode &>/dev/null; then
	log_info "opencode: installed"
else
	log_warn "opencode not found in PATH - make sure it's installed"
fi

# Check fzf (optional)
if command -v fzf &>/dev/null; then
	log_info "fzf: installed (optional - for interactive selection)"
else
	log_warn "fzf not found - using simple selector (install fzf for better UX)"
fi

# Check tmux
if command -v tmux &>/dev/null; then
	log_info "tmux: installed"
else
	log_error "tmux is required but not installed"
	exit 1
fi

echo
log_info "Checking session directory..."

SESSION_DIR="${OPENCODE_SESSION_DIR:-/home/.local/share/opencode/storage/session}"
if [[ -d "$SESSION_DIR" ]]; then
	session_count=$(find "$SESSION_DIR" -name "*.json" -type f 2>/dev/null | wc -l)
	log_info "Found $session_count session files in $SESSION_DIR"
else
	log_warn "Session directory not found: $SESSION_DIR"
	log_info "This is normal if you haven't used opencode yet"
fi

echo
log_info "Configuring tmux..."

TMUX_CONF="$HOME/.tmux.conf"

# Check if plugin is already sourced
if [[ -f "$TMUX_CONF" ]]; then
	if grep -q "opencode-tmux-plugin" "$TMUX_CONF" 2>/dev/null; then
		log_info "Plugin already configured in ~/.tmux.conf"
	else
		echo "" >>"$TMUX_CONF"
		echo "# opencode-tmux-plugin" >>"$TMUX_CONF"
		echo "run-shell $PLUGIN_DIR/opencode-tmux-plugin.tmux" >>"$TMUX_CONF"
		log_info "Added plugin to ~/.tmux.conf"
	fi
else
	echo "# opencode-tmux-plugin" >"$TMUX_CONF"
	echo "run-shell $PLUGIN_DIR/opencode-tmux-plugin.tmux" >>"$TMUX_CONF"
	log_info "Created ~/.tmux.conf with plugin"
fi

echo
log_info "Making scripts executable..."
chmod +x "$PLUGIN_DIR/scripts/opencode-sessions"

echo
log_info "Setup complete!"
echo
echo "Reload tmux config with: tmux source-file ~/.tmux.conf"
echo "Then press Alt+o to list and attach to opencode sessions"
