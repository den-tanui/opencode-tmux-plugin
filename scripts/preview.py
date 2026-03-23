#!/usr/bin/env python3
"""
preview.py — fzf preview pane for opencode-tmux-plugin.

Called by fzf as:  preview.py <directory> <session-id>

Renders the session details and conversation messages with colored
role badges and wrapped text, fitting within the preview panel.
"""

import json
import os
import sys
import textwrap
from pathlib import Path

# ── config ───────────────────────────────────────────────────────────────────

OPENCODE_SESSIONS_DIR = os.environ.get(
    "OPENCODE_SESSIONS_DIR", "/home/.local/share/opencode/storage/session"
)

# ── ANSI colors ───────────────────────────────────────────────────────────────

CYAN = "\033[38;5;45m"
MAGENTA = "\033[38;5;201m"
GRAY = "\033[38;5;242m"
GREEN = "\033[38;5;84m"
WHITE = "\033[38;5;252m"
YELLOW = "\033[38;5;226m"
RESET = "\033[0m"
BOLD = "\033[1m"


def col(s: str, c: str) -> str:
    return f"{c}{s}{RESET}"


def find_session_file(directory: str, session_id: str) -> Path | None:
    """Find the session JSON file given directory and session ID."""
    sessions_dir = Path(OPENCODE_SESSIONS_DIR)

    if not sessions_dir.exists():
        return None

    # The directory structure is: SESSION_DIR/<project-id>/<session-id>.json
    for project_dir in sessions_dir.iterdir():
        if not project_dir.is_dir():
            continue

        candidate = project_dir / f"{session_id}.json"
        if candidate.exists():
            return candidate

    return None


def main() -> None:
    if len(sys.argv) < 3:
        print("No session selected.")
        return

    dir_path = sys.argv[1].strip()
    sid = sys.argv[2].strip()
    home = Path.home()

    # Find the session file
    session_file = find_session_file(dir_path, sid)

    if not session_file:
        print(col(f"Session file not found: {sid}", MAGENTA))
        return

    try:
        with open(session_file) as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading session: {e}")
        return

    # Display session metadata
    short_dir = str(dir_path).replace(str(home), "~")
    title = data.get("title", "(no title)")
    session_id = data.get("id", "")
    time_data = data.get("time", {})
    summary = data.get("summary", {})

    print(col(f" {short_dir}", CYAN))
    print(col(f" {title}", BOLD + WHITE))
    print(col(f" ID: {session_id[:16]}...", GRAY))

    if time_data:
        created = time_data.get("created", 0)
        if created:
            import datetime

            dt = datetime.datetime.fromtimestamp(created / 1000)
            print(col(f" Created: {dt.strftime('%Y-%m-%d %H:%M')}", GRAY))

    if summary:
        additions = summary.get("additions", 0)
        deletions = summary.get("deletions", 0)
        files = summary.get("files", 0)
        print(col(f" Changes: +{additions} -{deletions} ({files} files)", YELLOW))

    print()
    print(col("─" * 40, GRAY))
    print()


if __name__ == "__main__":
    main()
