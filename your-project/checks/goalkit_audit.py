#!/usr/bin/env python3
"""Optional GoalKit audit guard.

This script is intentionally small and dependency-free. GoalKit core must still
work without checks/, but serious unattended runs can call this guard to catch
the failure modes that Markdown prose cannot enforce by itself.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path


CONTROL_FILES = ("AGENTS.md", "GOAL.md", "PLAN.md", "PROGRESS.md", "PROMPT.md", "HARNESS.md")
STATE_FILES = ("GOAL.md", "PLAN.md", "PROGRESS.md")


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def line_value(text: str, key: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def line_values(text: str, key: str) -> list[str]:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.*?)\s*$", re.MULTILINE)
    return [match.group(1).strip() for match in pattern.finditer(text)]


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end]


def field_value(line: str, key: str) -> str:
    match = re.search(rf"\b{re.escape(key)}=([^;\s]+)", line)
    return match.group(1).strip() if match else ""


def useful(value: str) -> bool:
    v = value.strip().lower()
    if "<" in v and ">" in v:
        return False
    return bool(v) and v not in {"n/a", "na", "none", "-", "<path/task|n/a>", "<next exact task/path or n/a>"}


def control_only_text(value: str) -> bool:
    lower = value.lower()
    return any(
        phrase in lower
        for phrase in (
            "re-read",
            "reread",
            "read controls",
            "report blocker",
            "unchanged blocker",
            "update progress",
            "edit progress",
            "write progress",
            "progress only",
            "wait",
            "approval",
        )
    )


def control_file_only_output(value: str) -> bool:
    raw = field_value(value, "output") or value
    if not useful(raw):
        return False
    lower = raw.strip().lower()
    if lower in {"control files", "control-files", "state files", "state-files"}:
        return True
    names = re.findall(r"\b(?:agents|goal|plan|progress|prompt|harness|readme)\.md\b", lower)
    if not names:
        return False
    remainder = re.sub(r"\b(?:agents|goal|plan|progress|prompt|harness|readme)\.md\b", "", lower)
    remainder = re.sub(r"[\s,;/+&|()_-]+", "", remainder)
    return remainder == ""


def current_task_is_open(value: str) -> bool:
    if not useful(value) or control_only_text(value):
        return False
    return not re.search(r"\bstatus=(done|blocked|n/a|none)\b", value, re.IGNORECASE)


def current_task_value(root: Path) -> str:
    return (
        line_value(read(root / "PROGRESS.md"), "current_task")
        or line_value(read(root / "PLAN.md"), "current_task")
        or line_value(read(root / "GOAL.md"), "current_task")
    )


def active_milestone_id(root: Path) -> str:
    for name in ("PROGRESS.md", "PLAN.md", "GOAL.md"):
        text = read(root / name)
        for key in ("active_milestone", "current_milestone"):
            value = line_value(text, key)
            if useful(value):
                match = re.search(r"\bM\d+\b", value, re.IGNORECASE)
                if match:
                    return match.group(0).upper()
    plan = read(root / "PLAN.md")
    match = re.search(r"^\s*(M\d+)\s+status=active\b", plan, re.IGNORECASE | re.MULTILINE)
    return match.group(1).upper() if match else ""


def milestone_block(plan: str, milestone: str) -> str:
    if not milestone:
        return ""
    pattern = re.compile(
        rf"(?ms)^\s*{re.escape(milestone)}\s+status=.*?(?=^\s*M\d+\s+status=|^##\s+|\Z)",
        re.IGNORECASE,
    )
    match = pattern.search(plan)
    return match.group(0) if match else ""


def useful_line_value(text: str, key: str) -> str:
    for value in line_values(text, key):
        if useful(value):
            return value
    return ""


def checklist_value(root: Path) -> str:
    plan = read(root / "PLAN.md")
    block = milestone_block(plan, active_milestone_id(root))
    return useful_line_value(block, "checklist") or useful_line_value(plan, "checklist")


def checklist_state_value(root: Path) -> str:
    progress_state = line_value(read(root / "PROGRESS.md"), "checklist_state")
    if useful(progress_state):
        return progress_state
    plan = read(root / "PLAN.md")
    block = milestone_block(plan, active_milestone_id(root))
    return useful_line_value(block, "checklist_state") or useful_line_value(plan, "checklist_state")


def checklist_counts(value: str) -> tuple[int, int] | None:
    match = re.search(r"\b(\d+)\s*/\s*(\d+)\b", value)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def checklist_next_open(value: str) -> bool:
    match = re.search(r"\bnext\s*=\s*([^;\n]+)", value, re.IGNORECASE)
    return bool(match and useful(match.group(1).strip()))


def checklist_complete(value: str) -> bool:
    if not useful(value):
        return False
    counts = checklist_counts(value)
    if counts:
        completed, total = counts
        return total > 0 and completed >= total and not checklist_next_open(value)
    lower = value.lower()
    return bool(re.search(r"\b(complete|completed|closed|done)\b", lower)) and not checklist_next_open(value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_changed_files(root: Path) -> list[str] | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip().strip('"')
        paths.append(path.replace("\\", "/"))
    return paths


def scope_patterns(root: Path) -> list[str]:
    raw = line_value(read(root / "GOAL.md"), "scope_must_not_change")
    patterns: list[str] = []
    for token in re.split(r"[,;]", raw):
        item = re.sub(r"\bif used\b", "", token, flags=re.IGNORECASE).strip().strip("`")
        item = item.replace("\\", "/")
        if not item or item.startswith("<"):
            continue
        if " " in item:
            continue
        if any(marker in item for marker in ("/", "*", ".")) or item.lower() in {"verifiers", "fixtures", "secrets"}:
            patterns.append(item)
    return patterns


def matches_scope(path: str, pattern: str) -> bool:
    p = pattern.rstrip("/")
    return path == p or path.startswith(p + "/") or fnmatch.fnmatch(path, p) or fnmatch.fnmatch(path, p.rstrip("/") + "/**")


def any_line_value(root: Path, key: str) -> str:
    for name in ("PROGRESS.md", "GOAL.md", "PLAN.md"):
        value = line_value(read(root / name), key)
        if value:
            return value
    return ""


def source_close_value(root: Path) -> str:
    return (
        line_value(read(root / "PROGRESS.md"), "source_close_authority")
        or line_value(read(root / "GOAL.md"), "source_close_authority")
        or line_value(read(root / "PLAN.md"), "source_close_authority")
    )


def parse_source_close_authority(value: str) -> tuple[str, str]:
    match = re.search(r'\bsource=([^;\s]+).*?\bquote="([^"]+)"', value)
    if not match:
        return "", ""
    return match.group(1).strip(), match.group(2).strip()


def source_close_is_original(root: Path, value: str) -> bool:
    if not useful(value):
        return False
    if re.search(r"\b(model-authored|GOAL\.md|PLAN\.md|PROGRESS\.md)\b", value, re.IGNORECASE):
        return False
    source, quote = parse_source_close_authority(value)
    if not useful(source) or not useful(quote):
        return False
    if source.upper() == "USER_GOAL":
        anchors = (
            line_value(read(root / "PROGRESS.md"), "active_goal"),
            line_value(read(root / "GOAL.md"), "source_objective"),
            line_value(read(root / "PROGRESS.md"), "source_objective"),
        )
        return any(quote in anchor for anchor in anchors if anchor)
    source_path = (root / source).resolve()
    try:
        source_path.relative_to(root.resolve())
    except ValueError:
        return False
    return source_path.is_file() and quote in read(source_path)


def close_policy_allows_unmet(root: Path) -> bool:
    goal = read(root / "GOAL.md")
    host_policy = line_value(goal, "host_complete_policy").lower()
    close_policy = line_value(goal, "verified_unmet_close_policy").lower()
    return host_policy == "closeable_verified_unmet" and close_policy == "closeable"


def finite_unmet_close_authorized(root: Path) -> tuple[bool, str]:
    if not close_policy_allows_unmet(root):
        return False, "unmet_close_policy_not_closeable"
    source_close = source_close_value(root)
    if not source_close_is_original(root, source_close):
        if not useful(source_close):
            return False, "closeable_without_source_close_authority"
        return False, "source_close_authority_not_anchored"
    plan_mode = line_value(read(root / "PLAN.md"), "mode").lower()
    if plan_mode == "autonomous_project":
        return False, "autonomous_project_unmet_close"
    completion_class = any_line_value(root, "completion_class").lower()
    if completion_class != "single_goal":
        return False, "completion_class_not_single_goal"
    continuation = any_line_value(root, "continuation_markers")
    if useful(continuation):
        return False, "continuation_markers_present"
    open_gates = any_line_value(root, "open_gates")
    if useful(open_gates):
        return False, "open_gates_present"
    next_bounded_path = (
        line_value(read(root / "PROGRESS.md"), "next_bounded_path")
        or line_value(read(root / "GOAL.md"), "next_bounded_path")
    )
    if useful(next_bounded_path):
        return False, "next_bounded_path_still_open"
    progress_done_gate = line_value(read(root / "PROGRESS.md"), "done_gate").lower()
    if "pass" not in progress_done_gate:
        return False, "done_gate_not_pass"
    return True, "unmet_close"


def has_route(root: Path) -> bool:
    progress = read(root / "PROGRESS.md")
    goal = read(root / "GOAL.md")
    current_task = current_task_value(root)
    if current_task_is_open(current_task):
        return True
    next_bounded_path = line_value(progress, "next_bounded_path") or line_value(goal, "next_bounded_path")
    if useful(next_bounded_path):
        return True
    route_discovery = line_value(progress, "route_discovery") or ("route_discovery" if "route_discovery output" in progress else "")
    if useful(route_discovery):
        return True
    route_queue = section(progress, "route_queue")
    if "[Q" in route_queue and "not_control_only=true" in route_queue:
        return True
    return finite_unmet_close_authorized(root)[0]


def route_without_blocked_close(root: Path) -> bool:
    progress = read(root / "PROGRESS.md")
    goal = read(root / "GOAL.md")
    next_bounded_path = line_value(progress, "next_bounded_path") or line_value(goal, "next_bounded_path")
    if useful(next_bounded_path):
        return True
    route_discovery = line_value(progress, "route_discovery") or ("route_discovery" if "route_discovery output" in progress else "")
    if useful(route_discovery):
        return True
    route_queue = section(progress, "route_queue")
    if "[Q" in route_queue and "not_control_only=true" in route_queue:
        return True
    return finite_unmet_close_authorized(root)[0]


def blocked_close_attempt(root: Path) -> bool:
    progress = read(root / "PROGRESS.md").lower()
    combined = "\n".join(
        (
            line_value(progress, "next_action"),
            section(progress, "closing"),
        )
    )
    return "update_goal blocked" in combined or "host goal blocked" in combined


def strict_blocked_audit_authorized(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    hashes = re.findall(r"\bblocker_hash=([A-Za-z0-9_.:-]+)", progress)
    repeated_three = len(hashes) >= 3 and len(set(hashes[-3:])) == 1
    if not repeated_three:
        return False, "blocked_without_three_turn_audit"
    if route_without_blocked_close(root):
        return False, "blocked_with_open_project_route"
    task = current_task_value(root)
    if re.search(r"\bstatus=(ready|running)\b", task, re.IGNORECASE):
        return False, "blocked_with_ready_task"
    external_required = line_value(progress, "blocked_external_required")
    if not useful(external_required):
        return False, "blocked_without_external_requirement"
    if re.fullmatch(r"(user input|external state|external input|clarification|approval|permission|help|unknown)", external_required.strip(), re.IGNORECASE):
        return False, "blocked_external_requirement_not_specific"
    return True, "blocked_audit"


def check_no_fixed_timeout(root: Path) -> tuple[bool, str]:
    pattern = re.compile(r"\b(?:command_)?timeout\s*=\s*300\b|\b300s\b", re.IGNORECASE)
    hits: list[str] = []
    for name in CONTROL_FILES:
        text = read(root / name)
        for idx, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{name}:{idx}")
    return (not hits, "no_fixed_timeout" if not hits else "fixed_timeout=" + ",".join(hits))


def check_no_human_wait(root: Path) -> tuple[bool, str]:
    terms = (
        "human " + "approval",
        "approval " + "needed",
        "await external " + "input",
        "wait for " + "approval",
    )
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(term) for term in terms) + r")\b", re.IGNORECASE)
    hits: list[str] = []
    for name in STATE_FILES:
        text = read(root / name)
        for idx, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{name}:{idx}")
    return (not hits, "no_human_wait" if not hits else "human_wait=" + ",".join(hits))


def check_productive_route(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    status = line_value(progress, "status").lower()
    if status not in {"local_gated", "unmet"}:
        return True, "productive_route=not_terminal_local_state"
    next_action = line_value(progress, "next_action").lower()
    control_only = control_only_text(next_action)
    if not control_only:
        return True, "productive_route=next_action_not_control_only"
    return (has_route(root), "productive_route" if has_route(root) else "missing_project_route")


def check_current_task_contract(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    status = line_value(progress, "status").lower()
    if status in {"", "not_started"}:
        return True, "current_task=inactive"
    if "explicit harness maintenance" in progress.lower():
        return True, "current_task=harness_maintenance"

    current_task = current_task_value(root)
    next_action = line_value(progress, "next_action")
    productive_output = line_value(progress, "productive_output")
    caps = line_value(progress, "caps").lower()
    task_lower = current_task.lower()
    verifier_or_control = any(
        marker in task_lower or marker in caps
        for marker in ("verifier", "bootstrap", "repair", "final_verification", "audit", "smoke")
    )

    if not useful(current_task) and not has_route(root):
        return False, "current_task_missing"
    if useful(current_task) and control_only_text(current_task):
        return False, "current_task_control_only"
    if status == "pursuing" and not verifier_or_control and control_file_only_output(current_task):
        return False, "current_task_control_output"
    if status == "pursuing" and control_file_only_output(productive_output):
        return False, "productive_output_control_file_only"
    if useful(next_action) and control_only_text(next_action) and not has_route(root):
        return False, "next_action_control_only"
    if status == "pursuing" and not useful(productive_output) and not verifier_or_control and not has_route(root):
        return False, "productive_output_missing"
    return True, "current_task_contract"


def check_checklist_state(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    status = line_value(progress, "status").lower()
    if status in {"", "not_started"}:
        return True, "checklist_state=inactive"
    checklist = checklist_value(root)
    if not useful(checklist):
        return True, "checklist_state=no_checklist"
    checklist_state = checklist_state_value(root)
    if not useful(checklist_state):
        return False, "checklist_state_missing"
    return True, "checklist_state"


def check_terminal_outcome_consistency(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    status = line_value(progress, "status").lower()
    outcome = line_value(progress, "terminal_outcome").lower()
    if status == "achieved" and "success" not in outcome:
        return False, "achieved_without_success"
    if status == "achieved" and "verified_unmet" in outcome:
        return False, "verified_unmet_marked_achieved"
    if status == "unmet" and "success" in outcome:
        return False, "success_marked_unmet"
    if "terminal_outcome=success" in progress and "status: unmet" in progress:
        return False, "success_closing_unmet"
    return True, "terminal_outcome_consistency"


def check_unmet_close(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    status = line_value(progress, "status").lower()
    outcome = line_value(progress, "terminal_outcome").lower()
    next_action = line_value(progress, "next_action").lower()
    closing = section(progress, "closing").lower()
    close_attempt = any(
        phrase in (next_action + "\n" + closing)
        for phrase in (
            "update_goal complete",
            "host goal complete",
            "host complete",
            "ready_for_update_goal_complete=true",
        )
    )
    unmet_state = status == "unmet" or "verified_unmet" in outcome
    if not close_policy_allows_unmet(root):
        if unmet_state and close_attempt:
            return False, "unmet_host_close_not_allowed"
        return True, "unmet_close"
    return finite_unmet_close_authorized(root)


def check_unmet_close_ready(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    status = line_value(progress, "status").lower()
    outcome = line_value(progress, "terminal_outcome").lower()
    if status != "unmet" and "verified_unmet" not in outcome:
        return False, "not_unmet_close_state"
    return finite_unmet_close_authorized(root)


def check_completion_no_pending_task(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    status = line_value(progress, "status").lower()
    next_action = line_value(progress, "next_action").lower()
    closing = section(progress, "closing").lower()
    close_attempt = status == "achieved" or any(
        phrase in (next_action + "\n" + closing)
        for phrase in (
            "update_goal complete",
            "host goal complete",
            "host complete",
            "ready_for_update_goal_complete=true",
        )
    )
    if not close_attempt:
        return True, "completion_pending_task=not_closing"
    task = current_task_value(root)
    if useful(task) and re.search(r"\bstatus=blocked\b", task, re.IGNORECASE) and not finite_unmet_close_authorized(root)[0]:
        return False, "completion_with_blocked_current_task"
    if useful(task) and not re.search(r"\bstatus=(done|blocked|n/a|none)\b", task, re.IGNORECASE):
        return False, "completion_with_pending_current_task"
    checklist = checklist_value(root)
    if useful(checklist):
        checklist_state = checklist_state_value(root)
        if not checklist_complete(checklist_state):
            return False, "completion_with_incomplete_checklist"
    route_queue = section(progress, "route_queue")
    if "[Q" in route_queue and "not_control_only=true" in route_queue:
        return False, "completion_with_route_queue"
    return True, "completion_pending_task"


def check_independence(root: Path) -> tuple[bool, str]:
    goal = read(root / "GOAL.md")
    if "signal_a:" not in goal or "signal_b:" not in goal:
        return True, "independence=no_signals"
    if "/goal <verb phrase" in goal or "<literal observable requirement>" in goal:
        return True, "independence=template"
    independence = line_value(goal, "independence")
    if "<" in independence or not independence:
        return False, "independence_placeholder"
    return True, "independence"


def check_secret_scan_shape(root: Path) -> tuple[bool, str]:
    goal = read(root / "GOAL.md")
    if "secret_redaction_scan:" not in goal:
        return True, "secret_scan=not_declared"
    line = line_value(goal, "secret_redaction_scan")
    if "<command>" in line:
        return True, "secret_scan=placeholder"
    if "expected 0" not in goal or "self_silent=true" not in goal:
        return False, "secret_scan_not_self_silent"
    return True, "secret_scan"


def check_repeated_blocker_hash(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    hashes = re.findall(r"\bblocker_hash=([A-Za-z0-9_.:-]+)", progress)
    if blocked_close_attempt(root):
        return strict_blocked_audit_authorized(root)
    if len(hashes) >= 2 and hashes[-1] == hashes[-2] and not has_route(root):
        return False, "repeated_blocker_hash_without_route"
    return True, "repeated_blocker_hash"


def check_blocked_close(root: Path) -> tuple[bool, str]:
    if not blocked_close_attempt(root):
        return True, "blocked_close=not_attempted"
    return strict_blocked_audit_authorized(root)


def check_scope_guard(root: Path) -> tuple[bool, str]:
    progress = read(root / "PROGRESS.md")
    status = line_value(progress, "status").lower()
    if status in {"", "not_started"}:
        return True, "scope_guard=inactive"
    if "explicit harness maintenance" in progress.lower():
        return True, "scope_guard=harness_maintenance"
    patterns = scope_patterns(root)
    if not patterns:
        return True, "scope_guard=no_patterns"
    changed = git_changed_files(root)
    if changed is None:
        return True, "scope_guard=git_unavailable"
    hits = sorted({path for path in changed for pattern in patterns if matches_scope(path, pattern)})
    return (not hits, "scope_guard" if not hits else "scope_violation=" + ",".join(hits))


def check_verifier_registry(root: Path) -> tuple[bool, str]:
    memory = read(root / "docs" / "PROJECT_MEMORY.md")
    registry = section(memory, "Verifier Registry")
    if not registry or re.search(r"^\s*none\s*$", registry, re.MULTILINE):
        return True, "verifier_registry=none"
    checked = 0
    for line in registry.splitlines():
        stripped = line.strip()
        if not stripped.startswith("[V#") and not re.match(r"^\[V\d+\b", stripped):
            continue
        path_value = field_value(stripped, "path")
        hash_value = field_value(stripped, "sha256").lower()
        if not path_value and not hash_value:
            continue
        if not path_value or hash_value in {"", "none", "unchecked"}:
            return False, "verifier_registry_missing_hash"
        target = root / path_value
        if not target.is_file():
            return False, "verifier_registry_missing_path=" + path_value
        checked += 1
        actual = sha256_file(target)
        if actual != hash_value:
            return False, "verifier_hash_drift=" + path_value
    return True, "verifier_registry=" + ("checked" if checked else "no_hash_entries")


def run_checks(root: Path, mode: str) -> list[tuple[bool, str]]:
    checks = [
        check_no_fixed_timeout,
        check_no_human_wait,
        check_productive_route,
        check_current_task_contract,
        check_checklist_state,
        check_terminal_outcome_consistency,
        check_unmet_close,
        check_completion_no_pending_task,
        check_independence,
        check_secret_scan_shape,
        check_repeated_blocker_hash,
        check_blocked_close,
        check_scope_guard,
        check_verifier_registry,
    ]
    if mode == "productive-turn":
        checks = [check_no_fixed_timeout, check_no_human_wait, check_productive_route, check_current_task_contract, check_checklist_state, check_repeated_blocker_hash, check_blocked_close, check_scope_guard]
    elif mode == "unmet-close":
        checks = [check_no_fixed_timeout, check_no_human_wait, check_checklist_state, check_terminal_outcome_consistency, check_unmet_close_ready, check_completion_no_pending_task, check_scope_guard, check_verifier_registry]
    return [check(root) for check in checks]


def write_minimal(root: Path, progress: str, goal: str = "", plan: str = "") -> None:
    (root / "PROGRESS.md").write_text(progress, encoding="utf-8")
    (root / "GOAL.md").write_text(goal or "# GOAL\n", encoding="utf-8")
    (root / "PLAN.md").write_text(plan or "# PLAN\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# AGENTS\n", encoding="utf-8")


def init_git(root: Path) -> None:
    subprocess.run(["git", "-C", str(root), "init"], check=True, capture_output=True, text=True)


def selftest() -> int:
    cases: list[tuple[str, bool, str]] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    next_action: re-read controls and report blocker\n    next_bounded_path: n/a\n\n## route_queue\n\n    none\n",
        )
        cases.append(("control_only_local_gate_fails", not all(ok for ok, _ in run_checks(root, "productive-turn")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    next_action: re-read controls and report blocker\n    next_bounded_path: docs/M1-handoff.md\n\n## route_queue\n\n    none\n",
        )
        cases.append(("local_gate_with_route_passes", all(ok for ok, _ in run_checks(root, "productive-turn")), "expected pass"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    current_task: id=M1-1; kind=docs; status=done; output=docs/x.md; verifier=inspect docs/x.md; next=n/a\n    next_action: re-read controls and report blocker\n    next_bounded_path: n/a\n\n## route_queue\n\n    none\n",
        )
        cases.append(("local_gate_done_task_is_not_route_fails", not all(ok for ok, _ in run_checks(root, "productive-turn")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: achieved\n    terminal_outcome: verified_unmet evidence=E1\n",
        )
        cases.append(("verified_unmet_achieved_fails", not all(ok for ok, _ in run_checks(root, "unmet-close")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: unmet\n    terminal_outcome: verified_unmet evidence=E1\n    next_action: update_goal complete\n",
            "# GOAL\n\n    host_complete_policy: global_success_only\n    verified_unmet_close_policy: milestone_only\n",
        )
        cases.append(("broad_unmet_host_close_fails", not all(ok for ok, _ in run_checks(root, "unmet-close")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    active_goal: Run a finite audit. This finite audit may end with an unmet report.\n    status: unmet\n    completion_class: single_goal\n    terminal_outcome: verified_unmet evidence=E1\n    open_gates: none\n    next_bounded_path: n/a\n    done_gate: pass evidence=E1,E2\n",
            "# GOAL\n\n    host_complete_policy: closeable_verified_unmet\n    verified_unmet_close_policy: closeable\n    source_close_authority: source=USER_GOAL quote=\"This finite audit may end with an unmet report.\"\n    continuation_markers: none\n",
        )
        cases.append(("finite_unmet_with_source_close_passes", all(ok for ok, _ in run_checks(root, "unmet-close")), "expected pass"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    active_goal: Run a finite audit.\n    status: unmet\n    completion_class: single_goal\n    terminal_outcome: verified_unmet evidence=E1\n    open_gates: none\n    next_bounded_path: n/a\n    done_gate: pass evidence=E1,E2\n",
            "# GOAL\n\n    host_complete_policy: closeable_verified_unmet\n    verified_unmet_close_policy: closeable\n    source_close_authority: source=USER_GOAL quote=\"This finite audit may end with an unmet report.\"\n    continuation_markers: none\n",
        )
        cases.append(("finite_unmet_unanchored_source_close_fails", not all(ok for ok, _ in run_checks(root, "unmet-close")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: unmet\n    completion_class: single_goal\n    terminal_outcome: verified_unmet evidence=E1\n    open_gates: none\n    next_bounded_path: n/a\n    done_gate: pass evidence=E1,E2\n",
            "# GOAL\n\n    host_complete_policy: closeable_verified_unmet\n    verified_unmet_close_policy: milestone_only\n    source_close_authority: source=USER_GOAL quote=\"This finite audit may end with an unmet report.\"\n    continuation_markers: none\n",
        )
        cases.append(("finite_unmet_requires_both_close_policies_fails", not all(ok for ok, _ in run_checks(root, "unmet-close")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: unmet\n    completion_class: single_goal\n    terminal_outcome: verified_unmet evidence=E1\n    open_gates: none\n    next_bounded_path: n/a\n    done_gate: pass evidence=E1,E2\n",
            "# GOAL\n\n    host_complete_policy: global_success_only\n    verified_unmet_close_policy: closeable\n    source_close_authority: source=USER_GOAL quote=\"This finite audit may end with an unmet report.\"\n    continuation_markers: none\n",
        )
        cases.append(("finite_unmet_close_policy_alone_fails", not all(ok for ok, _ in run_checks(root, "unmet-close")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: unmet\n    completion_class: single_goal\n    terminal_outcome: verified_unmet evidence=E1\n    open_gates: none\n    next_bounded_path: n/a\n    done_gate: pass evidence=E1,E2\n",
            "# GOAL\n\n    host_complete_policy: closeable_verified_unmet\n    verified_unmet_close_policy: closeable\n    source_close_authority: <source=USER_GOAL|path quote=\"verbatim original text permitting unmet-as-final\"; or n/a>\n",
        )
        cases.append(("finite_unmet_placeholder_source_close_fails", not all(ok for ok, _ in run_checks(root, "unmet-close")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: unmet\n    completion_class: terminal_project\n    terminal_outcome: verified_unmet evidence=E1\n    open_gates: none\n    next_bounded_path: n/a\n    done_gate: pass evidence=E1,E2\n",
            "# GOAL\n\n    host_complete_policy: closeable_verified_unmet\n    verified_unmet_close_policy: closeable\n    source_close_authority: source=USER_GOAL quote=\"This finite audit may end with an unmet report.\"\n    continuation_markers: none\n",
            "# PLAN\n\n## project\n\n    mode: autonomous_project\n",
        )
        cases.append(("autonomous_project_unmet_close_fails", not all(ok for ok, _ in run_checks(root, "unmet-close")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: unmet\n    completion_class: single_goal\n    terminal_outcome: verified_unmet evidence=E1\n    open_gates: none\n    next_bounded_path: docs/next-evidence.md\n    done_gate: pass evidence=E1,E2\n",
            "# GOAL\n\n    host_complete_policy: closeable_verified_unmet\n    verified_unmet_close_policy: closeable\n    source_close_authority: source=USER_GOAL quote=\"This finite audit may end with an unmet report.\"\n    continuation_markers: none\n",
        )
        cases.append(("unmet_close_with_open_route_fails", not all(ok for ok, _ in run_checks(root, "unmet-close")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: unmet\n    completion_class: single_goal\n    terminal_outcome: verified_unmet evidence=E1\n    open_gates: contract=false\n    next_bounded_path: n/a\n    done_gate: pass evidence=E1,E2\n",
            "# GOAL\n\n    host_complete_policy: closeable_verified_unmet\n    verified_unmet_close_policy: closeable\n    source_close_authority: source=USER_GOAL quote=\"This finite audit may end with an unmet report.\"\n    continuation_markers: none\n",
        )
        cases.append(("unmet_close_with_open_gate_fails", not all(ok for ok, _ in run_checks(root, "unmet-close")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    next_action: work\n",
            "# GOAL\n\n    controls: " + "timeout" + "=300\n",
        )
        cases.append(("fixed_timeout_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    next_action: " + "approval " + "needed before work\n",
        )
        cases.append(("approval_wait_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    current_task: id=M1-1; kind=docs; status=ready; output=docs/x.md; verifier=inspect docs/x.md; next=run check\n    next_action: write docs/x.md\n    productive_output: docs/x.md\n",
            "# GOAL\n\n    independence: reason=A checks artifact; adversary=B fails if report omitted\n",
        )
        cases.append(("normal_state_passes", all(ok for ok, _ in run_checks(root, "all")), "expected pass"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    next_action: update PROGRESS with blocker\n    productive_output: n/a\n\n## route_queue\n\n    none\n",
        )
        cases.append(("progress_bot_state_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    current_task: id=M1-1; kind=docs; status=ready; output=PROGRESS.md; verifier=inspect PROGRESS.md; next=work\n    next_action: update PROGRESS.md\n    productive_output: PROGRESS.md\n",
        )
        cases.append(("control_file_output_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    current_task: id=M2-1; kind=script; status=ready; output=checks/x.py; verifier=python -m py_compile checks/x.py; next=run x\n    next_action: create checks/x.py\n    productive_output: checks/x.py\n",
        )
        cases.append(("productive_current_task_passes", all(ok for ok, _ in run_checks(root, "all")), "expected pass"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    current_task: id=M2-1; kind=docs; status=ready; output=docs/x.md; verifier=inspect docs/x.md; next=work\n    next_action: write docs/x.md\n    productive_output: docs/x.md\n",
            plan="# PLAN\n\n## milestones\n\n    M2 status=active\n      checklist: docs/M2-checklist.md\n",
        )
        cases.append(("checklist_without_state_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    current_milestone: M2\n    current_task: id=M2-1; kind=docs; status=ready; output=docs/x.md; verifier=inspect docs/x.md; next=work\n    next_action: write docs/x.md\n    productive_output: docs/x.md\n",
            plan="# PLAN\n\n## project\n\n    active_milestone: M2\n\n## milestones\n\n    M0 status=achieved\n      checklist: n/a\n\n    M2 status=active\n      checklist: docs/M2-checklist.md\n",
        )
        cases.append(("active_milestone_checklist_without_state_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    current_milestone: M2\n    current_task: id=M2-1; kind=docs; status=ready; output=docs/x.md; verifier=inspect docs/x.md; next=work\n    checklist_state: docs/M2-checklist.md 1/4 next=M2-2\n    next_action: write docs/x.md\n    productive_output: docs/x.md\n",
            plan="# PLAN\n\n## project\n\n    active_milestone: M2\n\n## milestones\n\n    M0 status=achieved\n      checklist: n/a\n\n    M2 status=active\n      checklist: docs/M2-checklist.md\n",
        )
        cases.append(("active_milestone_checklist_with_state_passes", all(ok for ok, _ in run_checks(root, "all")), "expected pass"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    current_task: id=M2-1; kind=docs; status=ready; output=docs/x.md; verifier=inspect docs/x.md; next=work\n    checklist_state: docs/M2-checklist.md 1/4 next=M2-2\n    next_action: write docs/x.md\n    productive_output: docs/x.md\n",
            plan="# PLAN\n\n## milestones\n\n    M2 status=active\n      checklist: docs/M2-checklist.md\n",
        )
        cases.append(("checklist_with_state_passes", all(ok for ok, _ in run_checks(root, "all")), "expected pass"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: achieved\n    current_task: id=M3-1; kind=docs; status=ready; output=docs/x.md; verifier=inspect docs/x.md; next=write docs\n    next_action: update_goal complete\n    terminal_outcome: success evidence=E2\n",
        )
        cases.append(("completion_with_pending_current_task_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: achieved\n    current_task: id=M3-1; kind=docs; status=done; output=docs/x.md; verifier=inspect docs/x.md; next=n/a\n    next_action: update_goal complete\n    terminal_outcome: pending evidence=none\n",
        )
        cases.append(("achieved_without_success_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: achieved\n    current_task: id=M3-1; kind=docs; status=blocked; output=n/a; verifier=n/a; next=n/a\n    next_action: update_goal complete\n    terminal_outcome: success evidence=E2\n",
        )
        cases.append(("completion_with_blocked_current_task_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: achieved\n    current_task: id=M3-1; kind=docs; status=done; output=docs/x.md; verifier=inspect docs/x.md; next=n/a\n    checklist_state: docs/M3-checklist.md 1/4 next=M3-2\n    next_action: update_goal complete\n    terminal_outcome: success evidence=E2\n",
            plan="# PLAN\n\n## milestones\n\n    M3 status=active\n      checklist: docs/M3-checklist.md\n",
        )
        cases.append(("completion_with_incomplete_checklist_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: achieved\n    current_task: id=M3-4; kind=docs; status=done; output=docs/x.md; verifier=inspect docs/x.md; next=n/a\n    checklist_state: docs/M3-checklist.md 4/4 next=n/a\n    next_action: update_goal complete\n    terminal_outcome: success evidence=E2\n",
            plan="# PLAN\n\n## milestones\n\n    M3 status=active\n      checklist: docs/M3-checklist.md\n",
        )
        cases.append(("completion_with_complete_checklist_passes", all(ok for ok, _ in run_checks(root, "all")), "expected pass"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: unmet\n    terminal_outcome: success evidence=E2\n",
        )
        cases.append(("success_marked_unmet_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    next_action: re-read controls\n    next_bounded_path: n/a\n\n## escalations\n\n    blocker_hash=same1\n    blocker_hash=same1\n",
        )
        cases.append(("repeated_blocker_hash_fails", not all(ok for ok, _ in run_checks(root, "productive-turn")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    current_task: id=M4-1; kind=analysis; status=blocked; output=n/a; verifier=n/a; next=n/a\n    next_action: update_goal blocked\n    next_bounded_path: n/a\n\n## escalations\n\n    blocker_hash=same1\n    blocker_hash=same1\n",
        )
        cases.append(("blocked_without_three_turn_audit_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    current_task: id=M4-1; kind=analysis; status=blocked; output=n/a; verifier=n/a; next=n/a\n    next_action: update_goal blocked\n    next_bounded_path: n/a\n    blocked_external_required: dependency mirror is reachable\n    blocked_audit: pass\n\n## escalations\n\n    blocker_hash=same1\n    blocker_hash=same1\n",
        )
        cases.append(("blocked_audit_pass_without_three_turns_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    current_task: id=M4-1; kind=analysis; status=blocked; output=n/a; verifier=n/a; next=n/a\n    next_action: update_goal blocked\n    next_bounded_path: n/a\n\n## escalations\n\n    blocker_hash=same1\n    blocker_hash=same1\n    blocker_hash=same1\n",
        )
        cases.append(("blocked_without_external_requirement_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    current_task: id=M4-1; kind=analysis; status=blocked; output=n/a; verifier=n/a; next=n/a\n    next_action: update_goal blocked\n    next_bounded_path: n/a\n    blocked_external_required: dependency mirror is reachable\n\n## escalations\n\n    blocker_hash=same1\n    blocker_hash=same1\n    blocker_hash=same1\n",
        )
        cases.append(("blocked_after_three_turn_audit_passes", all(ok for ok, _ in run_checks(root, "all")), "expected pass"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    current_task: id=M4-1; kind=analysis; status=blocked; output=n/a; verifier=n/a; next=n/a\n    next_action: update_goal blocked\n    next_bounded_path: n/a\n    blocked_external_required: user input\n\n## escalations\n\n    blocker_hash=same1\n    blocker_hash=same1\n    blocker_hash=same1\n",
        )
        cases.append(("blocked_generic_external_requirement_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    current_task: id=M4-1; kind=docs; status=ready; output=docs/x.md; verifier=inspect docs/x.md; next=work\n    next_action: write docs/x.md\n    productive_output: docs/x.md\n\n## lessons\n\n    [L1 from=E1] Do not call update_goal blocked unless the strict audit passes.\n",
        )
        cases.append(("blocked_text_in_lesson_not_attempt_passes", all(ok for ok, _ in run_checks(root, "all")), "expected pass"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: local_gated\n    current_task: id=M4-1; kind=analysis; status=blocked; output=n/a; verifier=n/a; next=n/a\n    next_action: update_goal blocked\n    next_bounded_path: n/a\n    blocked_external_required: dependency mirror is reachable\n\n## route_queue\n\n    [Q1 not_control_only=true] output=docs/next.md; verifier=inspect docs/next.md\n\n## escalations\n\n    blocker_hash=same1\n    blocker_hash=same1\n    blocker_hash=same1\n",
        )
        cases.append(("blocked_with_open_route_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        init_git(root)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    next_action: work\n",
            "# GOAL\n\n    scope_must_not_change: protected.txt\n",
        )
        (root / "protected.txt").write_text("changed\n", encoding="utf-8")
        cases.append(("scope_guard_violation_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        init_git(root)
        write_minimal(
            root,
            "# PROGRESS\n\n## state\n\n    status: pursuing\n    next_action: work\n",
            "# GOAL\n\n    scope_must_not_change: secrets\n",
        )
        secret_dir = root / "secrets"
        secret_dir.mkdir()
        (secret_dir / "fixture.txt").write_text("changed\n", encoding="utf-8")
        cases.append(("scope_guard_bare_dir_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_minimal(root, "# PROGRESS\n\n## state\n\n    status: pursuing\n    current_task: id=M1-1; kind=script; status=ready; output=check.py; verifier=python check.py; next=work\n    next_action: work\n    productive_output: check.py\n")
        script = root / "check.py"
        script.write_text("print('ok')\n", encoding="utf-8")
        digest = sha256_file(script)
        docs = root / "docs"
        docs.mkdir()
        (docs / "PROJECT_MEMORY.md").write_text(
            "# Project Memory\n\n## Verifier Registry\n\n"
            f"[V1] check; signal=a; path=check.py; sha256={digest}; command=python check.py; expected=ok; last_pass=E1\n",
            encoding="utf-8",
        )
        cases.append(("verifier_registry_hash_passes", all(ok for ok, _ in run_checks(root, "all")), "expected pass"))
        script.write_text("print('changed')\n", encoding="utf-8")
        cases.append(("verifier_registry_drift_fails", not all(ok for ok, _ in run_checks(root, "all")), "expected fail"))
    failed = [name for name, ok, _ in cases if not ok]
    if failed:
        print("goalkit_audit_selftest: fail " + ",".join(failed))
        return 1
    print("goalkit_audit_selftest: pass cases=" + str(len(cases)))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run optional GoalKit audit checks.")
    parser.add_argument("--root", default=".", help="GoalKit/project root")
    parser.add_argument("--mode", choices=("all", "productive-turn", "unmet-close"), default="all")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    root = Path(args.root).resolve()
    results = run_checks(root, args.mode)
    failed = [reason for ok, reason in results if not ok]
    if failed:
        print("goalkit_audit: fail " + " ".join(failed))
        return 1
    print("goalkit_audit: pass " + " ".join(reason for _, reason in results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
