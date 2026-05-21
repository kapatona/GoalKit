# GoalKit Operator Harness

Operator manual for multi-day GoalKit runs. It explains setup, inspection,
recovery, and closure without duplicating the canonical rules in `AGENTS.md`.

## 1 Purpose

GoalKit is a Markdown control layer for Codex `/goal`. It cannot own or stop the
host loop. It keeps the original objective stable, pushes the agent toward
project artifacts before bookkeeping, records evidence compactly, routes false
gates into next work, and resumes after compaction or long gaps.

Codex runtime note: the model can mark a goal `complete` or, after a strict
repeated-blocker audit, `blocked`. Pause, resume, clear, budget-limited, and
usage-limited are host/user/system controls.

## 2 File Set

Core:

```text
AGENTS.md
GOAL.md
PLAN.md
PROGRESS.md
goals/_template.md
docs/PROJECT_MEMORY.md
```

Optional operating layer:

```text
PROMPT.md
HARNESS.md
checks/goalkit_audit.py
```

Use the project repo's own conventions for assets such as `scripts/`, `checks/`,
`tests/`, `fixtures/`, `examples/`, `docs/`, and `goals/`.

## 3 Setup And Start

1. Create or open the project root.
2. Copy the GoalKit file set into that root.
3. Start `/goal` with a detailed objective, or against an existing durable
   plan/spec file.
4. Do not hand-fill GOAL/PLAN/PROGRESS for first launch; bootstrap initializes
   local control state.
5. Include `PROMPT.md` in GOAL.md `read_first` only when the active loop should
   read it.
6. Keep long domain facts out of generic GoalKit files; use project docs,
   artifacts, fixtures, tests, and memory files.

Examples:

```text
/goal Add <feature> with passing tests and documented verification.
/goal Execute <plan-file>.md in full detail.
```

Broad objectives should produce a light adaptive roadmap and first executable
current_task, then refine from evidence instead of pre-scripting the full
project.

## 4 Inspect

Read:

1. PROGRESS state/current_task/checklist_state
2. PLAN active milestone, open_gates, next_exact_task
3. newest activity_log/evidence/route_queue rows
4. PROJECT_MEMORY promoted facts and rejected paths
5. changed project artifacts

Healthy run: next_action names project work; current_task has output and
verifier; checklist_state advances when present; false gates create next routes;
milestone boundaries write handoffs; completion uses fresh independent signals.

Unhealthy run: next_action only rereads controls; current_task is missing/stale/
control-only; the same blocker repeats; verified_unmet is treated as success;
PROGRESS grows while project artifacts do not; verifier text changes without
repair evidence.

## 5 Local Signals And Budgets

`STOP` and `DONE` are workspace-root regular files. They are local signals, not
host loop brakes.

- `STOP`: request operator state and safe next route.
- `DONE`: request final verification.

If final verification cannot close the host goal, route the next evidence path.

Use host/runtime budget controls for real cost limits. Inside GoalKit, prefer
adaptive per-command hang guards, route changes after repeated failures, and
strict `update_goal blocked` only with an exact `blocked_external_required`
condition. Avoid fixed global time caps.

## 6 Recovery

When stalled:

1. Check status: local_gated, unmet, pursuing, achieved.
2. Verify current_task/next_action are not control-only.
3. Look for next_bounded_path, route_queue, or route_discovery.
4. If no route exists, create a route-discovery task.
5. If a verifier is broken, repair without changing predicates.
6. If terminal proof is missing, preserve false gates and create the next
   evidence milestone.
7. Use host `update_goal blocked` only after three repeated goal turns, no safe
   route or finite close, and exact external condition.

Never narrow the original objective, delete open gates, or treat a report as
completion to solve a stall.

## 7 Audit Guard

When `checks/goalkit_audit.py` exists, GoalKit instructions make Codex run the
relevant mode during suspicious local-gate, unmet-close, milestone-boundary, or
completion-adjacent states. This is an unattended guard, not a required manual
operator step. `--strict` is for post-bootstrap runs where git scope checks and
secret scan configuration are expected to be concrete.

The guard accepts Markdown evidence rows and optional `PROGRESS.md`
`evidence_jsonl` final/audit mirrors.

## 8 Verifier Registry

Register important verifiers in `docs/PROJECT_MEMORY.md`:

```text
[V1] name; signal=a; path=checks/example.py; sha256=<hex>; command=<exact>; expected=<literal>; last_pass=E#
```

The audit guard detects hash drift when a registry hash exists.

## 9 Completion Review

Before accepting completion, confirm:

- terminal_outcome success, or finite source-authorized unmet close
- done_gate maps to terminal deliverables
- no executable current_task, route_queue item, or checklist item remains
- signal_a and signal_b are independent
- objective_fidelity passes
- open_gates are none
- secret scan is clean
- unresolved escalations do not affect completion
- final evidence rows are fresh
- changed files are inside scope

For broad build, research, analysis, and continuation projects, `verified_unmet`
is a milestone report, not final host completion.

## 10 Maintenance

Edit GoalKit control files intentionally:

- `AGENTS.md`: core rules
- `GOAL.md`: active objective and done_gate
- `PLAN.md`: roadmap and milestone state
- `PROGRESS.md`: current state and evidence index
- `PROMPT.md`: active per-turn protocol
- `HARNESS.md`: operator manual

Keep project-specific detail out of generic GoalKit files.
