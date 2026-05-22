#!/usr/bin/env python3
"""Opt-in held-out fixture tamper check for GoalKit-Compact."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import tempfile
from pathlib import Path

BASELINE = Path(".goalkit/holdout.sha256")
EMPTY = {"", "none", "n/a", "na", "-", "unset", "pending"}


def useful(text: str) -> bool:
    raw = text.strip()
    return bool(raw) and raw.lower() not in EMPTY and not re.fullmatch(r"<[^>\n]+>", raw)


def field(text: str, key: str) -> str:
    match = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", text, re.M)
    return match.group(1).strip() if match else ""


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def holdout_path(root: Path) -> Path | None:
    goal = root / "GOAL.md"
    raw = field(goal.read_text(encoding="utf-8") if goal.exists() else "", "held_out_tests")
    if not useful(raw):
        return None
    path = Path(raw.strip().strip('"'))
    return path if path.is_absolute() else root / path


def manifest(path: Path) -> list[str]:
    rows: list[str] = []
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = file.relative_to(path).as_posix()
        rows.append(f"{digest(file)}  {rel}")
    return rows


def init_baseline(root: Path) -> int:
    path = holdout_path(root)
    if path is None:
        print("holdout_guard: fail held_out_tests_not_configured")
        return 1
    if not path.is_dir():
        print(f"holdout_guard: fail missing_held_out_path {path}")
        return 1
    target = root / BASELINE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(manifest(path)) + "\n", encoding="utf-8")
    print(f"holdout_guard: initialized files={len(manifest(path))}")
    return 0


def check(root: Path, require: bool = False) -> int:
    path = holdout_path(root)
    if path is None:
        print("holdout_guard: " + ("fail not_configured" if require else "pass not_configured"))
        return 1 if require else 0
    if not path.is_dir():
        print(f"holdout_guard: fail missing_held_out_path {path}")
        return 1
    target = root / BASELINE
    if not target.exists():
        print("holdout_guard: fail missing_baseline")
        return 1
    expected = target.read_text(encoding="utf-8").splitlines()
    actual = manifest(path)
    if expected != actual:
        print("holdout_guard: fail drift")
        return 1
    print(f"holdout_guard: pass files={len(actual)}")
    return 0


def selftest() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        holdout = root / "tests" / "heldout"
        holdout.mkdir(parents=True)
        (root / "GOAL.md").write_text("held_out_tests: tests/heldout\n", encoding="utf-8")
        (holdout / "case.txt").write_text("expected\n", encoding="utf-8")
        if init_baseline(root) != 0 or check(root) != 0:
            return 1
        (holdout / "case.txt").write_text("changed\n", encoding="utf-8")
        if check(root) == 0:
            print("holdout_guard_selftest: fail drift_not_detected")
            return 1
    print("holdout_guard_selftest: pass")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--require", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.selftest:
        return selftest()
    if args.init:
        return init_baseline(root)
    return check(root, args.require)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
