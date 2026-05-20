# GoalKit Operator Harness

This file is the operator manual for multi-day GoalKit runs. It explains how to
set up, start, inspect, recover, and close an unattended `/goal` project.

## 1 Purpose

GoalKit provides a Markdown control layer for Codex `/goal`. It does not own the
host loop or the canonical host objective. It helps the agent:

- keep the original objective stable
- produce project artifacts before bookkeeping
- record evidence compactly
- route false gates into next work
- avoid broad false completion
- resume after compaction or long gaps

Use this harness when the run is expected to last hours or days.

Codex runtime note: the model can mark a goal `complete` or, after a strict
repeated-blocker audit, `blocked`. Pause, resume, clear, budget-limited, and
usage-limited status changes are host/user or system controls.

## 2 File Set

Minimal core:

```text
AGENTS.md
GOAL.md
PLAN.md
PROGRESS.md
goals/_template.md
docs/PROJECT_MEMORY.md
```

Recommended multi-day operating layer:

```text
PROMPT.md
HARNESS.md
checks/goalkit_audit.py
```

Project-specific assets should use the repository's own conventions, such as
`scripts/`, `checks/`, `tests/`, `fixtures/`, `examples/`, `docs/`, and
`goals/`.

## 3 Setup

1. Create or open the project root.
2. Copy the GoalKit file set into that root.
3. For first-run setup, either start a detailed direct `/goal`, or use the
   GoalKit README Plan prompt to create a durable plan file for broad projects.
4. Keep `PROMPT.md` short enough to read every turn.
5. Put long operator instructions in this file, not in `PROMPT.md`.
6. Do not pre-fill `GOAL.md`, `PLAN.md`, or `PROGRESS.md` by hand for first
   launch. Start `/goal` against the user objective or plan file; bootstrap
   will initialize local control state.
7. In `GOAL.md`, include `PROMPT.md` in `read_first` when it should be active.
8. If the project is multi-day, use `PLAN.md` and `docs/PROJECT_MEMORY.md`.
9. If strict machine checks are desired, keep `checks/goalkit_audit.py`.

## 4 Starting A Run

For a finite task:

```text
/goal Add <feature> with passing tests and documented verification.
```

For a broad project with a plan file:

```text
/goal Execute <plan-file>.md in full detail.
```

If the objective is already detailed, a direct `/goal` may skip a plan file. For
broad or ambiguous work, use the GoalKit README Plan prompt first. Plan mode
produces the proposed launch document; Default mode should write only that plan
file. Do not start a plan-based `/goal` from an unwritten plan.

The goal should be concrete enough to extract terminal deliverables. If the
source is broad, GoalKit should start with a light adaptive roadmap and first
executable current_task, then refine milestones from evidence rather than
pre-scripting the full project.

## 5 Daily Inspection

Inspect these files first:

1. `PROGRESS.md` state
2. `PROGRESS.md current_task`
3. `PROGRESS.md checklist_state`
4. `PLAN.md` active milestone and open gates
5. newest `activity_log` and `evidence` rows
6. newest `route_queue` item
7. `docs/PROJECT_MEMORY.md` promoted facts and rejected paths
8. changed project artifacts

Healthy run shape:

```text
next_action names project work
current_task has output and verifier
checklist_state advances when a checklist exists
productive_output is an artifact, command, test, fixture, script, or analysis
false gates create next routes
milestone boundaries write handoffs
completion requires fresh independent signals
```

Unhealthy run shape:

```text
next_action only re-reads controls
current_task is missing, stale, or control-only
checklist exists but state never changes
same blocker repeats
verified_unmet is treated as success
PROGRESS.md grows but project artifacts do not
verifier text changes without repair evidence
```

## 6 STOP And DONE

`STOP` and `DONE` are workspace-root regular files. They are local signals, not
host loop brakes.

- `STOP`: request an operator state report and a safe next route.
- `DONE`: request final verification.

If final verification cannot close the host goal, the agent must route the next
evidence path instead of repeating the report.

## 7 Budgets

GoalKit control files do not stop the host loop. Use host/runtime budget
controls for real cost limits.

Inside GoalKit:

- `iteration_soft_limit` steers strategy
- command hang guards prevent stuck commands
- repeated failures switch axis or route discovery
- local gates route work; they do not wait
- strict repeated blockers may use host `update_goal blocked` only with an exact
  `blocked_external_required` condition

Avoid fixed global time caps. Per-command limits should come from expected
runtime, prior evidence, and command-native progress signals.

## 8 Recovery

If the run stalls:

1. Check whether `PROGRESS.md status` is `local_gated` or `unmet`.
2. Confirm `current_task` and `next_action` are not control-only.
3. Look for `next_bounded_path`, `route_queue`, or `route_discovery`.
4. If no route exists, create a route-discovery task.
5. If a verifier is broken, use verifier repair without changing predicates.
6. If terminal proof is missing, preserve false gates and create the next
   evidence milestone.
7. If the same blocker recurs for at least three consecutive goal turns, no safe
   route or finite close remains, and `blocked_external_required` names the
   exact external input or state change required, use host `update_goal blocked`.

Do not solve a stall by narrowing the original objective, deleting open gates,
or treating a report as completion.

## 9 Audit Guard

When `checks/goalkit_audit.py` exists, GoalKit instructions make Codex run the
relevant mode during suspicious local-gate, unmet-close, milestone-boundary, or
completion-adjacent states. This is an unattended guard, not a required manual
operator step. Use it for debugging only when inspecting or maintaining the
harness itself.

## 10 Verifier Registry

For important verifier scripts or artifacts, register them in
`docs/PROJECT_MEMORY.md`:

```text
[V1] name; signal=a; path=checks/example.py; sha256=<hex>; command=<exact>; expected=<literal>; last_pass=E#
```

The audit guard can detect hash drift when a registry hash exists.

## 11 Completion Review

Before accepting completion, verify:

- `terminal_outcome=success`, or a finite source-authorized unmet close
- done_gate predicates map to terminal deliverables
- no executable current_task or route_queue item remains
- checklist_state is complete when a checklist exists
- signal_a and signal_b are independent
- objective_fidelity passes
- open_gates are none
- secret scan is clean
- no unresolved escalation affects completion
- final evidence rows are fresh
- changed files are inside scope

For broad build, research, analysis, and continuation projects,
`verified_unmet` is a milestone report, not final host completion.

## 12 Maintenance

Edit GoalKit control files intentionally:

- `AGENTS.md`: core rules
- `GOAL.md`: active objective and done_gate
- `PLAN.md`: roadmap and milestone state
- `PROGRESS.md`: current state and evidence index
- `PROMPT.md`: active per-turn protocol
- `HARNESS.md`: operator manual

Keep project-specific detail out of generic GoalKit files. Store domain facts in
project docs, artifacts, fixtures, tests, or memory files.
