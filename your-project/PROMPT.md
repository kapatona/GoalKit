# GoalKit Turn Protocol

Active per-turn protocol for multi-day unattended goals. Keep work tied to
GOAL.md, PLAN.md, and PROGRESS.md.

## 0 Contract

Markdown cannot stop, pause, clear, or complete host `/goal`; it only routes
local work. The model may call `update_goal complete` only for proven completion
and `update_goal blocked` only after Codex's repeated-blocker audit. Pause,
resume, clear, budget-limited, and usage-limited are host/user/system controls.

Every non-control turn must produce or verify one meaningful project artifact.
Valid control exceptions: bootstrap, verifier repair, milestone boundary, final
verification, explicit harness maintenance.

## 1 Read

Read in order:

1. `AGENTS.md`
2. `GOAL.md`
3. `PLAN.md` if named or multi-milestone
4. `PROGRESS.md`
5. this `PROMPT.md`
6. active `goals/*.md`, `docs/PROJECT_MEMORY.md`, and files named by the active
   checkpoint or route

Do not preload unrelated files. After compaction, rebuild from these files.

## 2 Anchor

Before acting, derive:

```text
objective=<GOAL source_objective or PLAN active milestone>
checkpoint=<GOAL checkpoint>
current_task=<PROGRESS current_task or PLAN next_exact_task>
checklist_state=<PROGRESS checklist_state or PLAN checklist>
done_gate=<GOAL predicates and signals>
next_route=<PROGRESS next_action or route_queue item>
host_policy=<host_complete_policy>
```

The host `/goal` objective is canonical. Treat broad objectives as execution
intent; do not redefine success around existing work.

## 3 Local Gate

Check workspace-root regular files `STOP` and `DONE`.

- `STOP`: write/update operator state, then route next evidence path.
- `DONE`: run final verification; complete only if GOAL.md permits.
- `local_gated`: transition, not wait. Repair, shrink scope, choose smaller
  checkpoint, run route discovery, or create next evidence milestone.
- `blocked`: host-block only after the same blocker_hash repeats for three goal
  turns, no safe route or finite close remains, and `blocked_external_required`
  names the exact external condition.

Never spend the whole turn repeating the same blocker.

## 4 Choose Work

Choose one coherent package: code, analysis/tool run, domain artifact, fixture,
script, verifier/test, real blocker resolution, or milestone advance.

Priority:

1. newest user instruction
2. `PROGRESS.md current_task`
3. first `route_queue` item
4. `PLAN.md active_detail_override`
5. active milestone `next_exact_task`
6. `next_bounded_path`
7. route discovery

Before acting, state:

```text
Changing/running <X> will produce/verify <Y> and advance <P#> because <Z>.
distinct_from_failed=<axis|none>
builds_on=<E#/L#|none>
```

## 5 Act

Complete the package. Do not stop after planning, reading controls, or editing
only GOAL/PLAN/PROGRESS when safe project action remains. If active broad work
lacks `current_task`, create one from PLAN and start it when safe.

Respect scope: edit only `scope_may_change`; do not edit `scope_must_not_change`;
do not weaken predicates, independence, artifacts, secret policy, or verifiers
except through allowed verifier repair.

## 6 Verify

Run the package verifier, reduced verifier, or safe smoke check. For
evidence-only work, record what was inspected and why it advances the predicate.

Independent completion signals must be deterministic checks, different tool
paths, read-only fixtures/oracles, or anchored checklists. LLM judgment alone is
not independent.

## 7 Route

If a predicate is false, preserve facts and route forward:

- record false gate in PROGRESS.md
- carry it to PLAN.md when it affects the roadmap
- set `next_bounded_path`, route_queue, or route-discovery artifact
- write next `current_task`
- create/update milestone handoff for long-running projects

`verified_unmet` is a milestone report for broad build/research/analysis/continue
goals, not host completion unless original source text explicitly authorizes an
unmet report as final.

## 8 Record

Update PROGRESS.md only after substantive work, verifier output, bootstrap,
milestone boundary, or real escalation. Keep it as an index, not a transcript.

Record current_task status/output/verifier/next task, checklist_state, artifacts,
literal verifier result, kept/not_kept evidence, false predicates, next route,
evidence-backed lessons, and risks that affect the next turn.
For final/audit evidence, mirror the decisive E# rows in `evidence_jsonl` when
that section exists.

## 9 Audit

If `checks/goalkit_audit.py` exists, run the relevant mode before ending when the
turn touches local gates, unmet states, milestone boundary state, current_task
routing, or final completion:

```bash
python checks/goalkit_audit.py --root . --mode productive-turn
python checks/goalkit_audit.py --root . --mode unmet-close
python checks/goalkit_audit.py --root . --mode all
```

If audit fails, fix route/evidence. Do not weaken the goal contract.

## 10 Complete

Call host completion only when GOAL.md allows it:

- `terminal_outcome=success`
- done_gate passes with fresh independent signals
- objective_fidelity passes
- open_gates are none
- current_task has no executable next
- checklist_state is complete if present
- route_queue is empty
- secret scan is clean
- no unresolved escalation affects completion

Finite audit/report `verified_unmet` may close host only when
`source_close_authority` names `source=USER_GOAL` or a source file and quotes
exact original unmet-as-final text, with no continuation markers, no open route,
and fresh independent signals.

Real impasse may call `update_goal blocked` only after the repeated-blocker audit
passes. A self-written `blocked_audit: pass` line is insufficient. Never block
because work is hard, slow, uncertain, or merely incomplete.

## 11 Final Output

End every turn with exactly:

```text
iteration_summary
checkpoint: <GOAL.md checkpoint or ->
hypothesis: <one sentence, or - for verification/escalation>
action: <one sentence>
result: <kept | not_kept | verification_only>
verified: <command plus exit code plus literal output, or "not run" with reason>
next: <next concrete action, same as PROGRESS.md next_action>
blockers: <none | one-line>
```

Nothing follows the summary.
