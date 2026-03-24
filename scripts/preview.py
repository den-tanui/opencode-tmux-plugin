#!/usr/bin/env python3
"""
preview.py — fzf preview pane for opencode-tmux-plugin.

Called by fzf as:  preview.py <directory> <session-id>

Renders the session details and conversation messages with colored
role badges and wrapped text, fitting within the preview panel.

Also handles --dirs-only mode where it shows all sessions for a directory.
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ── config ───────────────────────────────────────────────────────────────────

OPENCODE_SESSIONS_DIR = os.environ.get(
    "OPENCODE_SESSIONS_DIR", "/home/.local/share/opencode/storage/session"
)
MESSAGE_DIR = os.environ.get(
    "OPENCODE_MESSAGE_DIR", "/home/.local/share/opencode/storage/message"
)

# ── Tokyo Night colors ───────────────────────────────────────────────────────

PURPLE = "\033[38;5;141m"  # #bb9af7 - lavender
BLUE = "\033[38;5;69m"  # #7aa2f7 - blue
GREEN = "\033[38;5;107m"  # #9ece6a - green
YELLOW = "\033[38;5;179m"  # #e0af68 - yellow
RED = "\033[38;5;203m"  # #f7768e - red/pink
ORANGE = "\033[38;5;208m"  # #ff9e64 - orange
WHITE = "\033[38;5;189m"  # #c0caf5 - light
GRAY = "\033[38;5;244m"  # #565f89 - muted
DIM = "\033[38;5;243m"  # #414868 - dim
RESET = "\033[0m"
BOLD = "\033[1m"


def col(s: str, c: str) -> str:
    return f"{c}{s}{RESET}"


def age(mtime: float) -> str:
    """Return human-readable age string."""
    s = int(time.time() - mtime)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m"
    if s < 86400:
        return f"{s // 3600}h"
    return f"{s // 86400}d"


def get_time_group(mtime: float) -> str:
    """Return time group for a session."""
    now = time.time()
    diff = now - mtime

    if diff < 86400:  # Less than 24 hours
        return "Today"
    elif diff < 172800:  # Less than 48 hours
        return "Yesterday"
    elif diff < 604800:  # Less than 7 days
        return "This Week"
    elif diff < 2592000:  # Less than 30 days
        return "This Month"
    else:
        return "Older"


def find_session_file(directory: str, session_id: str) -> Path | None:
    """Find the session JSON file given directory and session ID."""
    sessions_dir = Path(OPENCODE_SESSIONS_DIR)

    if not sessions_dir.exists():
        return None

    for project_dir in sessions_dir.iterdir():
        if not project_dir.is_dir():
            continue
        candidate = project_dir / f"{session_id}.json"
        if candidate.exists():
            return candidate

    return None


def parse_session(json_path: Path) -> dict | None:
    """Parse session JSON file."""
    try:
        with open(json_path) as f:
            data = json.load(f)
        return {
            "id": data.get("id", ""),
            "title": data.get("title", ""),
            "directory": data.get("directory", ""),
            "time": data.get("time", {}),
            "summary": data.get("summary", {}),
            "model": data.get("model", {}),
            "tokens": data.get("tokens", {}),
            "cost": data.get("cost", 0),
            "error": data.get("error"),
        }
    except Exception:
        return None


def get_sessions_for_dir(dir_path: str) -> list[dict]:
    """Get all sessions for a directory."""
    sessions_dir = Path(OPENCODE_SESSIONS_DIR)
    if not sessions_dir.exists():
        return []

    sessions = []
    for project_dir in sessions_dir.iterdir():
        if not project_dir.is_dir():
            continue
        for session_file in project_dir.glob("*.json"):
            session = parse_session(session_file)
            if session and session.get("directory") == dir_path:
                session["_mtime"] = session_file.stat().st_mtime
                sessions.append(session)

    sessions.sort(key=lambda x: x.get("_mtime", 0), reverse=True)
    return sessions


def show_session_details(dir_path: str, sid: str):
    """Show details for a single session."""
    session_file = find_session_file(dir_path, sid)

    if not session_file:
        print(col(f"Session file not found: {sid}", RED))
        return

    try:
        with open(session_file) as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading session: {e}")
        return

    # Display session metadata
    title = data.get("title", "(no title)")
    session_id = data.get("id", "")
    time_data = data.get("time", {})
    summary = data.get("summary", {})

    print(col(f" {dir_path}", PURPLE))
    print(col(f" {title}", BOLD + WHITE))
    print(col(f" ID: {session_id[:16]}...", GRAY))

    if time_data:
        created = time_data.get("created", 0)
        if created:
            dt = datetime.fromtimestamp(created / 1000)
            print(col(f" Created: {dt.strftime('%Y-%m-%d %H:%M')}", GRAY))

    if summary:
        additions = summary.get("additions", 0)
        deletions = summary.get("deletions", 0)
        files = summary.get("files", 0)
        print(col(f" Changes: +{additions} -{deletions} ({files} files)", YELLOW))

    print()
    print(col("─" * 40, DIM))
    print()

    # Model info
    model_data = data.get("model", {})
    if model_data:
        provider = model_data.get("providerID", "?")
        model_id = model_data.get("modelID", "?")
        print(col(f" Model: {provider}/{model_id}", BLUE))

    # Tokens & cost
    tokens_data = data.get("tokens", {})
    if tokens_data:
        input_tok = tokens_data.get("input", 0)
        output_tok = tokens_data.get("output", 0)
        total = input_tok + output_tok
        cost_val = data.get("cost", 0)
        cost_str = f"${cost_val:.2f}" if cost_val else "$0.00"
        print(col(f" Tokens: {total} ({cost_str})", ORANGE))

    # Error state
    error = data.get("error")
    if error:
        print()
        error_name = error.get("name", "Unknown error")
        print(col(f" ⚠ Error: {error_name}", RED + BOLD))


def show_directory_sessions(dir_path: str):
    """Show list of sessions for a directory (dirs-only mode), grouped by time."""
    print(col(f" Sessions in {dir_path}", BOLD + WHITE))
    print()

    sessions = get_sessions_for_dir(dir_path)

    if not sessions:
        print(col(" No sessions found", GRAY))
        return

    print(col(f" {len(sessions)} sessions:", BLUE))
    print()

    # Group sessions by time
    groups = {}
    for session in sessions:
        mtime = session.get("_mtime", 0)
        group = get_time_group(mtime)
        if group not in groups:
            groups[group] = []
        groups[group].append(session)

    # Define group order
    group_order = ["Today", "Yesterday", "This Week", "This Month", "Older"]

    for group_name in group_order:
        if group_name not in groups:
            continue

        group_sessions = groups[group_name]
        print(col(f" ▶ {group_name}", PURPLE))
        print()

        for session in group_sessions:
            sid = session.get("id", "")
            title = session.get("title", "")
            mtime = session.get("_mtime", 0)
            a = age(mtime)

            label = (title[:50] + "…") if len(title) > 50 else (title or "(empty)")
            age_s = col(f"[{a:>4}]", BLUE)

            print(f"   {age_s}  {col(label, WHITE)}")
            print(f"        {col(sid[:32], GRAY)}")

        print()


def main() -> None:
    if len(sys.argv) < 3:
        print("No session selected.")
        return

    dir_path = sys.argv[1].strip()
    sid = sys.argv[2].strip()

    # If sid is "dir", we're in directory-only mode - show session list
    if sid == "dir":
        show_directory_sessions(dir_path)
    else:
        show_session_details(dir_path, sid)


if __name__ == "__main__":
    main()
