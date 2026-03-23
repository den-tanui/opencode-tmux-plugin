#!/usr/bin/env python3
"""
picker.py — lists all OpenCode sessions for fzf consumption.

Reads OPENCODE_SESSIONS_DIR (env) or default path, groups sessions by
project directory, and emits tab-delimited lines:

    <display-text>\t<directory>\t<session-id>

fzf is invoked with --with-nth=1 so only display text is shown;
columns 2 and 3 are passed to preview.py and open.sh as hidden payload.
"""

import json
import os
import sys
import time
from pathlib import Path
from collections import defaultdict

# ── config ───────────────────────────────────────────────────────────────────

OPENCODE_SESSIONS_DIR = os.environ.get(
    "OPENCODE_SESSIONS_DIR", "/home/.local/share/opencode/storage/session"
)

# ── helpers ───────────────────────────────────────────────────────────────────


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


def parse_session(json_path: Path) -> dict | None:
    """Parse session JSON file and return relevant fields."""
    try:
        with open(json_path) as f:
            data = json.load(f)
        return {
            "id": data.get("id", ""),
            "title": data.get("title", ""),
            "directory": data.get("directory", ""),
            "time": data.get("time", {}),
            "summary": data.get("summary", {}),
        }
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return None


def get_sessions() -> dict[str, list[dict]]:
    """Group sessions by directory."""
    sessions_by_dir = defaultdict(list)
    sessions_dir = Path(OPENCODE_SESSIONS_DIR)

    if not sessions_dir.exists():
        return sessions_by_dir

    for project_dir in sessions_dir.iterdir():
        if not project_dir.is_dir():
            continue

        for session_file in project_dir.glob("*.json"):
            session = parse_session(session_file)
            if session and session.get("directory"):
                mtime = session_file.stat().st_mtime
                session["_mtime"] = mtime
                sessions_by_dir[session["directory"]].append(session)

    # Sort sessions by time (newest first)
    for dir_key in sessions_by_dir:
        sessions_by_dir[dir_key].sort(key=lambda x: x.get("_mtime", 0), reverse=True)

    return sessions_by_dir


# ── ANSI colors ───────────────────────────────────────────────────────────────

CYAN = "\033[38;5;45m"
MAGENTA = "\033[38;5;201m"
GRAY = "\033[38;5;242m"
WHITE = "\033[38;5;252m"
RESET = "\033[0m"


def col(s: str, c: str) -> str:
    return f"{c}{s}{RESET}"


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    home = Path.home()
    sessions_by_dir = get_sessions()

    if not sessions_by_dir:
        print("No opencode sessions found.", file=sys.stderr)
        sys.exit(1)

    # Sort directories by most recent session
    sorted_dirs = sorted(
        sessions_by_dir.keys(),
        key=lambda d: sessions_by_dir[d][0].get("_mtime", 0),
        reverse=True,
    )

    for dir_path in sorted_dirs:
        sessions = sessions_by_dir[dir_path]
        short_path = str(dir_path).replace(str(home), "~")

        # Directory header with session count
        count = len(sessions)
        print(f"  {col(short_path, CYAN)}  {col(f'({count})', GRAY)}")

        for session in sessions:
            sid = session.get("id", "")
            title = session.get("title", "")
            mtime = session.get("_mtime", 0)
            a = age(mtime)

            # Truncate title
            label = (
                (title[:58] + "…")
                if len(title) > 58
                else (title or col("(empty)", GRAY))
            )
            age_s = col(f"[{a:>4}]", MAGENTA)

            # Format: <display>\t<dir>\t<session-id>
            print(f"    {age_s}  {col(label, WHITE)}\t{dir_path}\t{sid}")


if __name__ == "__main__":
    main()
