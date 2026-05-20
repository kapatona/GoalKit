# GoalKit Milestone Template

Use this when a broad `/goal` needs a reusable finite milestone objective. Keep the objective concrete enough that Codex can verify it without redefining success.

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
- Do not treat compile success, file existence, checklist presence, or LLM/web opinion as terminal proof.
- Do not request external input inside host `/goal`; record non-waiting escalation and choose a fallback or next evidence path.
- update_goal complete only for allowed terminal_outcome=success, or finite audit/report verified_unmet authorized by source_close_authority source+quote.
- update_goal blocked only after the same blocker repeats for three goal turns, no safe route or finite close remains, and blocked_external_required names the exact condition.
- Do not close host on verified_unmet for build/research/continue objectives.
- If a GoalKit audit guard exists, local_gated/unmet next_action must pass it before the turn ends.
- Do not spend a turn only editing PROGRESS/GOAL/PLAN unless this milestone is bootstrap, verifier_repair, milestone_boundary, final verification, or explicit harness maintenance.
- Keep current_task, checklist_state, and next_action aligned; checklist closure needs all items complete and no executable next; false readiness writes the next concrete current_task.

Verification:
- signal_a: <exact command/check and expected output>
- signal_b: <independent command/check and expected output>
- independence_justification: <why signal_a and signal_b fail differently; include smallest A-pass/B-fail adversary>
- secret_redaction_scan: <exact command/check and expected 0 matches>
- final audit: <requirement-to-evidence mapping>

Completion policy:
- terminal_success: close only if P1/P2, objective_fidelity, open_gates=none, and two independent signals pass.
- verified_unmet: milestone report for build/research/continue; finite host close needs source_close_authority source+quote, no continuation markers/open path, and two independent signals.
```

## After Milestone

- Update PLAN.md active milestone, open_gates, next_exact_task, next_if_unmet.
- Update PROGRESS.md current_task, checklist_state, activity_log, evidence, route_queue, memory_index, lessons, closing.
- Promote durable facts to docs/PROJECT_MEMORY.md or the domain memory doc.
- Create/update the next `goals/*.md` when the next task should be reusable.
- If the host loop continues and the next step is safe, start the next artifact/tool/code work before ending the turn.
