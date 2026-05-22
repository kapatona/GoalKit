#!/usr/bin/env python3
"""Optional anti-stall and anti-drift check for GoalKit-Compact."""
from __future__ import annotations
import argparse, re, sys, tempfile
from pathlib import Path
MAX_PROGRESS_LINES = 60
MAX_PROGRESS_CHARS = 5000

DONE = {"achieved", "done", "complete", "completed"}
ACTIVE = {"pursuing", "active", "in_progress", "working"}
EMPTY = {"", "none", "n/a", "na", "-", "unset", "pending"}
PHASES = {"review", "repair", "validate"}
CONTROL = r"(?:agents|goal|progress|decisions|readme)\.md"
CONTROL_PHRASES = ("read control", "update progress", "edit progress", "write progress", "progress only", "fill goal", "expand checklist", "report blocker")
TRIVIAL_HINTS = ("fail", "empty", "no-op", "noop", "nop", "placeholder", "not implemented", "unimplemented", "missing", "absent")
NEGATION_PATTERNS = ("not fail", "never fail", "does not fail", "doesn't fail")
PROGRESS_SHAPE = ("current", "hypotheses", "progress", "failure_modes", "next", "blockers")
def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
def field(text: str, key: str) -> str:
    match = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", text, re.M)
    return match.group(1).strip() if match else ""
def useful(text: str) -> bool:
    raw = text.strip()
    return bool(raw) and raw.lower() not in EMPTY and not re.fullmatch(r"<[^>\n]+>", raw)
def present(text: str) -> bool:
    raw = text.strip()
    return bool(raw) and not re.fullmatch(r"<[^>\n]+>", raw)
def list_block(text: str, key: str) -> list[str]:
    rows: list[str] = []
    active = False
    for line in text.splitlines():
        match = re.match(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", line)
        if match:
            rows += [match.group(1).strip()] if useful(match.group(1)) else []
            active = True
            continue
        if not active or not line.strip():
            continue
        item = re.match(r"^\s*-\s*(.*?)\s*$", line)
        if not item:
            break
        value = item.group(1).strip()
        rows += [value] if useful(value) else []
    return rows
def snapshot(root: Path) -> dict[str, str]:
    progress = read(root / "PROGRESS.md")
    goal = read(root / "GOAL.md")
    return {
        "status": field(progress, "status").lower(),
        "phase": field(progress, "phase").lower(),
        "current": field(progress, "current_task"),
        "hypotheses": field(progress, "hypotheses"),
        "progress": field(progress, "progress"),
        "failure_modes": field(progress, "failure_modes"),
        "evidence": field(progress, "evidence"),
        "next": field(progress, "next") or field(progress, "next_task"),
        "blockers": field(progress, "blockers"),
        "anti_trivial": field(goal, "done_gate_anti_trivial"),
        "held_out": field(goal, "held_out_tests"),
        "verifier_independence": field(goal, "verifier_independence"),
        "verifiers": "\n".join(list_block(goal, "verifiers")),
        "protected_paths": "\n".join(list_block(goal, "protected_paths")),
        "_progress_text": progress,
    }
def control_only(text: str) -> bool:
    low = text.lower()
    if re.search(CONTROL, low):
        rest = re.sub(CONTROL, "", low)
        if not re.sub(r"[\s,.;:/\\+&|()_-]+", "", rest):
            return True
    return any(phrase in low for phrase in CONTROL_PHRASES)
def path_exists(root: Path, raw: str) -> bool:
    if not useful(raw):
        return True
    path = Path(raw.strip().strip('"'))
    return (path if path.is_absolute() else root / path).exists()
def anti_trivial_meaningful(text: str) -> bool:
    low = text.lower()
    return useful(text) and not any(k in low for k in NEGATION_PATTERNS) and any(k in low for k in TRIVIAL_HINTS)
def route_check(s: dict[str, str]) -> tuple[bool, str]:
    status = s["status"]
    if status in {"", "not_started"}:
        return True, "inactive"
    if status in DONE:
        return True, "completion_route_closed"
    if status == "blocked":
        return True, "blocked_route_closed"
    if not (useful(s["current"]) or useful(s["next"])):
        return False, "missing_current_task_or_next"
    if control_only(s["current"]) and control_only(s["next"]):
        return False, "control_only_route"
    if "bootstrap" in s["current"].lower():
        return False, "bootstrap_still_active"
    return True, "productive_route"
def checks(root: Path, strict: bool = False) -> list[tuple[bool, str]]:
    s = snapshot(root)
    status = s["status"]
    results = [route_check(s)]

    if status in ACTIVE:
        results += [
            (s["phase"] in PHASES, "phase_tag_present"),
            (all(present(s[key]) for key in PROGRESS_SHAPE), "progress_shape"),
            (useful(s["evidence"]) or useful(s["verifiers"]), "verifier_reference_present"),
        ]
    else:
        results.append((True, "phase_shape_not_active"))

    if status in DONE:
        results += [
            (useful(s["evidence"]), "completion_evidence"),
            (anti_trivial_meaningful(s["anti_trivial"]), "completion_anti_trivial_gate"),
            (not useful(s["next"]), "completion_no_next_task"),
            (not useful(s["blockers"]), "completion_no_blocker"),
        ]
    else:
        results.append((True, "not_completion_state"))

    if status == "blocked":
        blocker = s["blockers"].strip().lower()
        vague = blocker in {"user input", "clarification", "approval", "permission", "unknown"}
        results += [
            (useful(blocker) and not vague, "blocked_exact_external_condition"),
            (not useful(s["next"]), "blocked_no_next_task"),
        ]
    else:
        results.append((True, "not_blocked_state"))

    results.append((path_exists(root, s["held_out"]), "held_out_path_exists"))
    if strict:
        results.append((useful(s["protected_paths"]), "strict_protected_paths_declared"))
        verifiers = [v for v in s["verifiers"].splitlines() if useful(v)]
        if len(verifiers) > 1:
            results.append((useful(s["verifier_independence"]), "strict_verifier_independence"))

    text = s["_progress_text"]
    if status in {"", "not_started"}:
        results.append((True, "progress_size_inactive"))
    else:
        results += [
            (len(text.splitlines()) <= MAX_PROGRESS_LINES, "progress_line_budget"),
            (len(text) <= MAX_PROGRESS_CHARS, "progress_char_budget"),
        ]
    return results
GOAL = """held_out_tests: n/a
protected_paths:
- n/a
verifiers:
- pytest
verifier_independence: n/a
done_gate_anti_trivial: pytest fails on an empty implementation
"""
MISSING_HELDOUT_GOAL = GOAL.replace("held_out_tests: n/a", "held_out_tests: tests/missing")
TRIVIAL_ANTI_GOAL = GOAL.replace("pytest fails on an empty implementation", "ok")
NEGATED_ANTI_GOAL = GOAL.replace("pytest fails on an empty implementation", "gate does not fail on empty implementation")
BASE = "phase: repair\ncurrent_task: implement\nhypotheses: fix is in source\nprogress: source changed\nfailure_modes: none yet\nevidence: pending\nnext: run tests\nblockers: none\n"
DONE_OK = "status: achieved\nevidence: tests passed\nnext: n/a\nblockers: none\n"
def write_case(root: Path, progress: str, goal: str = GOAL) -> None:
    (root / "PROGRESS.md").write_text(progress, encoding="utf-8")
    (root / "GOAL.md").write_text(goal, encoding="utf-8")
def selftest() -> int:
    cases: list[tuple] = [
        ("inactive", "status: not_started\nnext: fill GOAL.md\n", True),
        ("productive", "status: pursuing\n" + BASE, True),
        ("control_loop", "status: pursuing\n" + BASE.replace("implement", "update PROGRESS.md").replace("run tests", "read control files"), False),
        ("done", DONE_OK, True),
        ("done_no_evidence", DONE_OK.replace("tests passed", "none"), False),
        ("done_with_next", DONE_OK.replace("next: n/a", "next: run more tests"), False),
        ("blocked_vague", "status: blocked\nevidence: n/a\nnext: n/a\nblockers: clarification\n", False),
        ("missing_phase", "status: pursuing\n" + BASE.replace("phase: repair\n", ""), False),
        ("missing_shape", "status: pursuing\nphase: review\ncurrent_task: inspect\nnext: test\nblockers: none\n", False),
        ("progress_too_long", "status: pursuing\n" + BASE + "filler line\n" * 70, False),
        ("strict_missing_protected_paths", "status: pursuing\n" + BASE, False, {"strict": True}),
        ("held_out_path_missing", "status: pursuing\n" + BASE, False, {"goal": MISSING_HELDOUT_GOAL}),
        ("done_with_trivial_gate", DONE_OK, False, {"goal": TRIVIAL_ANTI_GOAL}),
        ("done_with_negated_anti_trivial", DONE_OK, False, {"goal": NEGATED_ANTI_GOAL}),
    ]
    failed: list[str] = []
    for case in cases:
        name, progress, should_pass = case[0], case[1], case[2]
        opts = case[3] if len(case) > 3 else {}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_case(root, progress, opts.get("goal", GOAL))
            passed = all(ok for ok, _ in checks(root, strict=opts.get("strict", False)))
            failed += [name] if passed != should_pass else []
    print("goalkit_audit_selftest: " + ("fail " + ",".join(failed) if failed else f"pass cases={len(cases)}"))
    return 1 if failed else 0
def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    failed = [reason for ok, reason in checks(Path(args.root).resolve(), args.strict) if not ok]
    print("goalkit_audit: " + ("fail " + " ".join(failed) if failed else "pass"))
    return 1 if failed else 0
if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
