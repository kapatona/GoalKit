#!/usr/bin/env python3
"""Opt-in protected-path change check for GoalKit-Compact."""

from __future__ import annotations

import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

EMPTY = {"", "none", "n/a", "na", "-", "unset", "pending"}


def useful(text: str) -> bool:
    raw = text.strip()
    return bool(raw) and raw.lower() not in EMPTY and not re.fullmatch(r"<[^>\n]+>", raw)


def list_block(text: str, key: str) -> list[str]:
    rows: list[str] = []
    active = False
    for line in text.splitlines():
        match = re.match(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", line)
        if match:
            if useful(match.group(1)):
                rows.append(match.group(1).strip())
            active = True
            continue
        if not active:
            continue
        if not line.strip():
            continue
        item = re.match(r"^\s*-\s*(.*?)\s*$", line)
        if item:
            value = item.group(1).strip()
            if useful(value):
                rows.append(value)
            continue
        break
    return rows


def protected_patterns(root: Path) -> list[str]:
    goal = root / "GOAL.md"
    if not goal.exists():
        return []
    return list_block(goal.read_text(encoding="utf-8"), "protected_paths")


def changed_paths(root: Path) -> list[str] | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    paths: list[str] = []
    for line in out.splitlines():
        raw = line[3:] if len(line) > 3 else ""
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        if raw:
            paths.append(raw.replace("\\", "/").strip('"'))
    return paths


def violations(changed: list[str], patterns: list[str]) -> list[str]:
    hits: list[str] = []
    for path in changed:
        for pattern in patterns:
            normalized = pattern.replace("\\", "/")
            if fnmatch.fnmatch(path, normalized) or fnmatch.fnmatch(path, normalized.rstrip("/") + "/*"):
                hits.append(path)
                break
    return hits


def check(root: Path, require_git: bool = False, require_config: bool = False) -> int:
    patterns = protected_patterns(root)
    if not patterns:
        print("scope_guard: " + ("fail not_configured" if require_config else "pass not_configured"))
        return 1 if require_config else 0
    changed = changed_paths(root)
    if changed is None:
        print("scope_guard: " + ("fail not_git_repo" if require_git else "pass not_git_repo"))
        return 1 if require_git else 0
    hits = violations(changed, patterns)
    print("scope_guard: " + ("fail " + " ".join(hits) if hits else f"pass changed={len(changed)}"))
    return 1 if hits else 0


def selftest() -> int:
    hits = violations(["secrets.env", "src/app.py", "protected/a.txt"], ["secrets*", "protected/**"])
    if hits != ["secrets.env", "protected/a.txt"]:
        print("scope_guard_selftest: fail")
        return 1
    print("scope_guard_selftest: pass")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--require-git", action="store_true")
    parser.add_argument("--require-config", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    return check(Path(args.root).resolve(), args.require_git, args.require_config)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
