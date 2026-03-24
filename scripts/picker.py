#!/usr/bin/env python3
"""
picker.py — lists all OpenCode sessions for fzf consumption.

Reads OPENCODE_SESSIONS_DIR (env) or default path, groups sessions by
project directory, and emits tab-delimited lines:

    <display-text>\t<directory>\t<session-id>

fzf is invoked with --with-nth=1 so only display text is shown;
columns 2 and 3 are passed to preview.py and open.sh as hidden payload.
"""

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

# ── config ───────────────────────────────────────────────────────────────────

OPENCODE_SESSIONS_DIR = os.environ.get(
    "OPENCODE_SESSIONS_DIR", "/home/.local/share/opencode/storage/session"
)

# ── Tokyo Night colors ───────────────────────────────────────────────────────

PURPLE = "\033[38;5;141m"  # #bb9af7 - lavender
BLUE = "\033[38;5;69m"  # #7aa2f7 - blue
WHITE = "\033[38;5;189m"  # #c0caf5 - light
GRAY = "\033[38;5;244m"  # #565f89 - muted
GREEN = "\033[38;5;107m"  # #9ece6a - green
YELLOW = "\033[38;5;179m"  # #e0af68 - yellow
RESET = "\033[0m"


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
                session["_mtime"] = session_file.stat().st_mtime
                sessions_by_dir[session["directory"]].append(session)

    for dir_key in sessions_by_dir:
        sessions_by_dir[dir_key].sort(key=lambda x: x.get("_mtime", 0), reverse=True)

    return sessions_by_dir


def col(s: str, c: str) -> str:
    return f"{c}{s}{RESET}"


def print_dirs_only(sessions_by_dir: dict, hide_single: bool):
    """Print only directories, no sessions."""
    sorted_dirs = sorted(
        sessions_by_dir.keys(),
        key=lambda d: sessions_by_dir[d][0].get("_mtime", 0),
        reverse=True,
    )

    for dir_path in sorted_dirs:
        sessions = sessions_by_dir[dir_path]

        if hide_single and len(sessions) == 1:
            continue

        count = len(sessions)
        # Use "dir" as a marker for directory-only mode
        print(
            f"  {col(str(dir_path), PURPLE)}  {col(f'({count} sessions)', GRAY)}\t{dir_path}\tdir"
        )


def print_all(sessions_by_dir: dict, hide_single: bool):
    """Print directories with all their sessions."""
    sorted_dirs = sorted(
        sessions_by_dir.keys(),
        key=lambda d: sessions_by_dir[d][0].get("_mtime", 0),
        reverse=True,
    )

    for dir_path in sorted_dirs:
        sessions = sessions_by_dir[dir_path]

        if hide_single and len(sessions) == 1:
            continue

        count = len(sessions)
        print(f"  {col(str(dir_path), PURPLE)}  {col(f'({count})', GRAY)}")

        for session in sessions:
            sid = session.get("id", "")
            title = session.get("title", "")
            mtime = session.get("_mtime", 0)
            a = age(mtime)

            label = (
                (title[:58] + "…")
                if len(title) > 58
                else (title or col("(empty)", GRAY))
            )
            age_s = col(f"[{a:>4}]", BLUE)

            print(f"    {age_s}  {col(label, WHITE)}\t{dir_path}\t{sid}")


def main() -> None:
    parser = argparse.ArgumentParser(description="List OpenCode sessions for fzf")
    parser.add_argument(
        "--hide-single",
        action="store_true",
        help="Hide directories with only one session",
    )
    parser.add_argument(
        "--dirs-only",
        action="store_true",
        help="Show only directories, sessions appear in preview",
    )
    args = parser.parse_args()

    sessions_by_dir = get_sessions()

    if not sessions_by_dir:
        print("No opencode sessions found.", file=sys.stderr)
        sys.exit(1)

    if args.dirs_only:
        print_dirs_only(sessions_by_dir, args.hide_single)
    else:
        print_all(sessions_by_dir, args.hide_single)


if __name__ == "__main__":
    main()
