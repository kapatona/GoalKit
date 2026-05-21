# GoalKit Milestone Template

Use when a broad `/goal` needs a reusable finite milestone objective. Keep it concrete enough to verify without redefining success.

## Goal Objective

```text
<Milestone name and one-sentence purpose. State whether this is terminal_success work, evidence-only work, or a false-gate reduction.>

Authoritative refs:
- AGENTS.md
- GOAL.md
- PLAN.md <section/milestone>
- PROGRESS.md current state
- <domain docs/artifacts>

Scope may change:
- <paths>

Scope must not change:
- AGENTS.md except explicit harness maintenance
- read-only evidence, secrets, credentials, external fixtures
- <project-specific paths>

Behavior contract:
- P1: <observable predicate>
- P2: <observable predicate>
- Productive output: <doc/script/code/fixture/analysis artifact or command result>
- Current task: id=<M#-step>; kind=<code|analysis|docs|fixture|script|test|verifier|handoff>; output=<artifact/command>; verifier=<command/check>; next=<task>
- Checklist state: <n/a or checklist path plus completed/total and next unchecked item>

Open gates carried in:
- <none or gate=false with evidence>

Next-if-unmet:
- <next bounded evidence path to write if this milestone closes false>

Rollback plan:
- <append-only | exact undo command for current-package edits | n/a>

Constraints:
- Follow AGENTS.md completion, blocked, local_gate, and audit_guard rules.
- Host complete/blocked only through AGENTS.md strict conditions; milestone close is not host close.
- verified_unmet is milestone-only unless original source text explicitly authorizes finite unmet close.
- Evidence must be concrete; compile success, file existence, checklist presence, or LLM/web opinion is not terminal proof.
- No waiting inside host `/goal`: choose fallback, route_discovery, verifier_repair, or next evidence path.
- Keep current_task, checklist_state, and next_action aligned; false readiness writes the next concrete current_task.

Verification:
- signal_a: <exact command/check and expected output>
- signal_b: <independent command/check and expected output>
- independence_justification: <why signal_a and signal_b fail differently; include smallest A-pass/B-fail adversary>
- secret_redaction_scan: <exact command/check and expected 0 matches>
- final audit: <requirement-to-evidence mapping>

Completion policy:
- terminal_success: P1/P2, objective_fidelity, open_gates=none, and independent signals pass.
- verified_unmet: milestone report unless finite host close has source_close_authority source+quote, no continuation markers, and no open route.
```

## After Milestone

- Update PLAN.md active milestone, open_gates, next_exact_task, next_if_unmet.
- Update PROGRESS.md current_task, checklist_state, activity_log, evidence, optional evidence_jsonl final/audit mirror, route_queue, memory_index, lessons, closing.
- Promote durable facts to docs/PROJECT_MEMORY.md or the domain memory doc.
- Create/update the next `goals/*.md` when the next task should be reusable.
- If the host loop continues and the next step is safe, start the next artifact/tool/code work before ending the turn.
