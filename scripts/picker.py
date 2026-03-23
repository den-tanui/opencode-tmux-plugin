#!/usr/bin/env python3
"""
picker.py — lists all OpenCode sessions for fzf consumption.

Reads OPENCODE_SESSIONS_DIR (env) or default path, groups sessions by
project directory, and emits tab-delimited lines.

Two modes:
- collapsed (default): Only directory headers, preview shows session list
- expanded: All sessions listed under each directory

Usage: picker.py [--expanded]
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from collections import defaultdict

# ── config ───────────────────────────────────────────────────────────────────

OPENCODE_SESSIONS_DIR = os.environ.get(
    "OPENCODE_SESSIONS_DIR", "/home/.local/share/opencode/storage/session"
)

# ── helpers ───────────────────────────────────────────────────────────────────


def Age(mtime: float) -> str:
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

    return sessions_by_dir


# ── ANSI colors ───────────────────────────────────────────────────────────────

CYAN = "\033[38;5;45m"
MAGENTA = "\033[38;5;201m"
GRAY = "\033[38;5;242m"
WHITE = "\033[38;5;252m"
RESET = "\033[0m"


def col(s: str, c: str) -> str:
    return f"{c}{s}{RESET}"


def format_directory_header(
    dir_path: str, session_count: int, mtime: float, home: Path
) -> str:
    """Format a directory header line."""
    short_path = str(dir_path).replace(str(home), "~")
    a = Age(mtime)
    return f"▸ {col(short_path, CYAN)}  {col(f'({session_count} sessions, {a})', GRAY)}"


def format_session_line(session: dict, home: Path) -> str:
    """Format a session line."""
    dir_path = session.get("directory", "")
    sid = session.get("id", "")
    title = session.get("title", "")
    mtime = session.get("_mtime", 0)
    summary = session.get("summary", {})

    a = Age(mtime)
    additions = summary.get("additions", 0)
    deletions = summary.get("deletions", 0)

    # Truncate title
    label = (title[:50] + "…") if len(title) > 50 else (title or col("(empty)", GRAY))
    age_s = col(f"[{a:>4}]", MAGENTA)
    changes = col(f"+{additions} -{deletions}", GRAY)

    # Format: <display>\t<dir>\t<session-id>
    return f"    {age_s}  {label} {changes}\t{dir_path}\t{sid}"


def format_directory_preview(dir_sessions: list[dict], home: Path) -> str:
    """Format preview for a directory (shows all sessions)."""
    lines = []
    for session in dir_sessions:
        sid = session.get("id", "")
        title = session.get("title", "")
        mtime = session.get("_mtime", 0)
        summary = session.get("summary", {})

        a = Age(mtime)
        additions = summary.get("additions", 0)
        deletions = summary.get("deletions", 0)
        label = (title[:40] + "…") if len(title) > 40 else (title or "(empty)")

        lines.append(f"  [{a:>4}]  {label}  +{additions} -{deletions}  ({sid[:12]}...)")

    return "\n".join(lines)


# ── main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expanded", action="store_true", help="Show all sessions expanded"
    )
    args = parser.parse_args()

    home = Path.home()
    sessions_by_dir = get_sessions()

    if not sessions_by_dir:
        print("No opencode sessions found.", file=sys.stderr)
        sys.exit(1)

    # Sort directories by most recent session (newest first)
    sorted_dirs = sorted(
        sessions_by_dir.keys(),
        key=lambda d: sessions_by_dir[d][0].get("_mtime", 0),
        reverse=True,
    )

    for dir_path in sorted_dirs:
        sessions = sessions_by_dir[dir_path]

        if args.expanded:
            # Expanded mode: show directory header + all sessions
            header = format_directory_header(
                dir_path, len(sessions), sessions[0].get("_mtime", 0), home
            )
            # Display text | Directory | SessionID (empty for directories)
            print(f"{header}\t{dir_path}\t")

            for session in sessions:
                print(format_session_line(session, home))
        else:
            # Collapsed mode: show only directory header
            header = format_directory_header(
                dir_path, len(sessions), sessions[0].get("_mtime", 0), home
            )
            # Display text | Directory | SessionID (empty for directories)
            print(f"{header}\t{dir_path}\t")


if __name__ == "__main__":
    main()
