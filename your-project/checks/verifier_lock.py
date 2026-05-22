#!/usr/bin/env python3
"""Opt-in verifier hash drift check for GoalKit-Compact."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

REGISTRY = Path(".goalkit/verifiers.json")


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def registry_path(root: Path) -> Path:
    return root / REGISTRY


def init_registry(root: Path, files: list[str]) -> int:
    entries = []
    for item in files:
        path = Path(item)
        full = path if path.is_absolute() else root / path
        if not full.is_file():
            print(f"verifier_lock: fail missing_file {item}")
            return 1
        entries.append({"name": path.stem, "path": str(path), "sha256": digest(full)})
    target = registry_path(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(f"verifier_lock: initialized entries={len(entries)}")
    return 0


def check(root: Path, require: bool = False) -> int:
    target = registry_path(root)
    if not target.exists():
        print("verifier_lock: " + ("fail missing_registry" if require else "pass not_configured"))
        return 1 if require else 0
    entries = json.loads(target.read_text(encoding="utf-8"))
    failures: list[str] = []
    for entry in entries:
        rel = Path(entry["path"])
        path = rel if rel.is_absolute() else root / rel
        if not path.is_file():
            failures.append(f"missing:{entry['path']}")
            continue
        actual = digest(path)
        if actual != entry.get("sha256"):
            failures.append(f"drift:{entry['path']}")
    print("verifier_lock: " + ("fail " + " ".join(failures) if failures else f"pass entries={len(entries)}"))
    return 1 if failures else 0


def selftest() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        script = root / "verify.ps1"
        script.write_text("Write-Output ok\n", encoding="utf-8")
        if init_registry(root, ["verify.ps1"]) != 0:
            return 1
        if check(root) != 0:
            return 1
        script.write_text("Write-Output changed\n", encoding="utf-8")
        if check(root) == 0:
            print("verifier_lock_selftest: fail drift_not_detected")
            return 1
    print("verifier_lock_selftest: pass")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--init", nargs="+", metavar="FILE")
    parser.add_argument("--require", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.selftest:
        return selftest()
    if args.init:
        return init_registry(root, args.init)
    return check(root, args.require)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
