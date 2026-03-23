# opencode-tmux-plugin

A tmux plugin for managing [OpenCode](https://opencode.ai) sessions. Browse and resume all your OpenCode conversations directly from tmux with a beautiful floating popup.

[![MIT License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Features

- **Floating Popup** — Press `Prefix + g` to open a floating popup with all sessions
- **Grouped by Directory** — Sessions automatically organized by project directory
- **Live Preview** — See session details in the preview pane as you browse
- **Smart Deduplication** — Switching to an already-open session jumps to its window
- **Fuzzy Search** — Type to filter across all sessions and projects
- **Keyboard-Driven** — Vim-style navigation inside the picker
- **Configurable** — Key binding, popup size, and session directory are all overridable

## Installation

### Using Tmux Plugin Manager (TPM)

```bash
# Add to ~/.tmux.conf
set -g @plugin 'yourusername/opencode-tmux-plugin'

# Install plugins
prefix + I
```

### Manual Installation

```bash
# Clone or copy this repository to your tmux plugins directory
git clone https://github.com/yourusername/opencode-tmux-plugin.git ~/.tmux/plugins/opencode-tmux-plugin

# Add to ~/.tmux.conf
run-shell ~/.tmux/plugins/opencode-tmux-plugin/opencode-tmux-plugin.tmux
```

Reload tmux: `tmux source-file ~/.tmux.conf`

## Requirements

| Dependency | Version | Notes |
|------------|---------|-------|
| [tmux](https://github.com/tmux/tmux) | ≥ 3.2 | For `display-popup` support |
| [fzf](https://github.com/junegunn/fzf) | any | Fuzzy finder |
| Python | 3.x | For picker and preview scripts |
| [opencode](https://opencode.ai) | any | Must be in `$PATH` |

## Usage

### Key Bindings

| Binding | Action |
|---------|--------|
| `Prefix + g` | Open session picker (floating popup) |
| `Prefix + G` | Open session picker (terminal mode, no popup) |

> Note: `Prefix` is your tmux prefix (default: `Ctrl+b`)

### Inside the Picker

| Key | Action |
|-----|--------|
| `Enter` | Open selected session |
| `Esc` / `Ctrl+c` | Close popup |
| `↑` / `↓` or `Ctrl+k` / `Ctrl+j` | Move selection |
| `J` / `K` | Scroll preview down / up |
| `g` / `G` | Preview top / bottom |
| `/` | Toggle preview pane |
| Type anything | Fuzzy-filter sessions |

## Configuration

Add to `~/.tmux.conf` before the `run-shell` / TPM line:

```bash
# Key to trigger the session picker (default: g)
set -g @opencode_sessions_key 'g'

# Popup dimensions (default: 80% width, 75% height)
set -g @opencode_sessions_popup_width '80%'
set -g @opencode_sessions_popup_height '75%'

# Session directory (default: auto-detected)
set -g @opencode_sessions_dir '/home/.local/share/opencode/storage/session'
```

## Scripts

The plugin includes several scripts in the `scripts/` directory:

- **picker.py** — Lists all sessions grouped by directory for fzf consumption
- **preview.py** — Renders session details in the fzf preview pane
- **open.sh** — Creates a new tmux window or switches to existing one
- **opencode-sessions** — Legacy bash script for non-fzf mode

### Standalone Usage

```bash
# List all sessions by directory
./scripts/picker.py

# Preview a specific session
./scripts/preview.py "/home/projects/myproject" "ses_abc123..."

# Open a session
echo -e "/home/projects/myproject\tses_abc123..." | ./scripts/open.sh
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│  OpenCode Session Storage                          │
│  /home/.local/share/opencode/storage/session/      │
│  └── <project-id>/<session-id>.json                │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ picker.py parses JSON
                       ▼
┌─────────────────────────────────────────────────────┐
│  Group by Directory                                │
│  /home/projects/todo-gum          (27 sessions)   │
│  /home/projects/opencode-tmux     (12 sessions)    │
│  ~/.config/nvim                  (62 sessions)    │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ fzf --preview
                       ▼
┌─────────────────────────────────────────────────────┐
│  Floating Popup (tmux display-popup)                │
│  ┌────────────────────┬──────────────────────────┐  │
│  │ Session List       │ Preview Pane            │  │
│  │ ▼ todo-gum (27)    │ ~/projects/todo-gum     │  │
│  │   [29d] Ticket...  │ Ticket: Todo app...     │  │
│  │   [30d] Locate... │ ID: ses_abc123...       │  │
│  │ ▶ nvim (62)       │ Created: 2026-02-22     │  │
│  └────────────────────┴──────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ open.sh
                       ▼
┌─────────────────────────────────────────────────────┐
│  Create/Switch tmux window                          │
│  opencode-<session-id> → opencode --session <id>   │
└─────────────────────────────────────────────────────┘
```

## Troubleshooting

### "No opencode sessions found"

- Make sure you've used OpenCode at least once
- Check that the session directory exists:
  ```bash
  ls -la /home/.local/share/opencode/storage/session
  ```

### fzf not found

- Install fzf: `brew install fzf` (macOS) or `apt install fzf` (Linux)
- Or use `Prefix + G` for non-popup mode

### Popup not working

- Ensure tmux version is 3.2 or higher
- Or use `Prefix + G` for terminal mode

## License

MIT
