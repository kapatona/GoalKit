# GoalKit Turn Protocol

Active per-turn protocol for long unattended `/goal` runs. `AGENTS.md` and
`GOAL.md` remain canonical; this file keeps the loop short.

## 0 Constants

- Markdown cannot stop, pause, clear, or complete host `/goal`.
- `update_goal complete` only after GOAL.md completion policy passes.
- `update_goal blocked` only after Codex's repeated-blocker audit passes.
- Every non-control turn produces or verifies project work.
- Control-only exceptions: bootstrap, verifier repair, milestone boundary, final
  verification, explicit harness maintenance.

## 1 Read And Anchor

Read only what is needed, in order:

1. `AGENTS.md`
2. `GOAL.md`
3. `PLAN.md` if named or multi-milestone
4. `PROGRESS.md`
5. this file
6. active `goals/*.md`, memory docs, and files named by current task/route

Before acting, derive:

```text
objective=<GOAL objective or PLAN milestone>
checkpoint=<GOAL checkpoint>
current_task=<PROGRESS current_task or PLAN next_exact_task>
checklist_state=<PROGRESS/PLAN checklist state>
done_gate=<GOAL predicates/signals>
route=<PROGRESS next_action, route_queue, or next_bounded_path>
host_policy=<host_complete_policy>
```

Broad objectives are execution intent. Do not redefine success around existing
work.

## 2 Work Loop

Handle local signals first:

- `STOP`: write operator state and choose a safe next route.
- `DONE`: run final verification; close only if GOAL.md permits.
- `local_gated`: transition by repair, smaller in-scope route, route discovery,
  or finite close guard; never repeat the same blocker.
- `blocked`: host-block only after three repeated blocker hashes, no safe route,
  and exact `blocked_external_required`.

Choose one package by priority: newest user instruction, PROGRESS current_task,
route_queue, PLAN active_detail_override, active milestone next_exact_task,
next_bounded_path, route discovery.

Before work, state the local rationale:

```text
Changing/running <X> will produce/verify <Y> and advance <P#> because <Z>.
distinct_from_failed=<axis|none>
builds_on=<E#/L#|none>
```

Then act. Do not stop after reading controls, planning, or editing only control
files when safe project work remains. If broad work lacks `current_task`, create
one from PLAN and start it when safe. Respect scope and never weaken predicates,
independence, artifacts, secret policy, or verifiers except allowed repair.

## 3 Verify And Route

Run the package verifier, reduced verifier, or safe smoke check. Evidence-only
work must record inspected facts and the predicate it advances.

Completion signals must be deterministic, different tool paths, read-only
fixtures/oracles, or anchored checklists. LLM judgment alone is not independent.

If a predicate is false, preserve useful facts and write the next route:

- PROGRESS evidence and false gate
- PLAN carry-forward when roadmap-affecting
- next_bounded_path, route_queue, or route-discovery artifact
- next current_task
- milestone handoff for long-running work

`verified_unmet` is a milestone report for broad build/research/analysis/continue
goals, not host completion unless original source text authorizes final unmet.

## 4 Record And Audit

Update PROGRESS.md only after substantive work, verifier output, bootstrap,
milestone boundary, or real escalation. Keep it as an index, not a transcript.
Record current_task, checklist_state, artifacts, literal verifier result,
kept/not_kept evidence, false predicates, next route, lessons, and risks. Mirror
decisive final/audit E# rows in `evidence_jsonl` when present.

If `checks/goalkit_audit.py` exists, run the relevant mode before ending when the
turn touches local gates, unmet states, milestone boundary, current_task routing,
or final completion:

```bash
python checks/goalkit_audit.py --root . --mode productive-turn
python checks/goalkit_audit.py --root . --mode unmet-close
python checks/goalkit_audit.py --root . --mode all
```

If audit fails, fix route/evidence. Do not weaken the goal contract.

## 5 Complete Or Block

Host completion requires GOAL.md permission plus fresh evidence:

- terminal_outcome success, or finite source-authorized unmet close
- done_gate and objective_fidelity pass
- open_gates none
- no executable current_task, route_queue item, or checklist item remains
- secret scan clean
- no unresolved escalation affects completion

Finite audit/report `verified_unmet` may close host only with anchored
`source_close_authority`, no continuation markers, no open route, and fresh
independent signals.

Real impasse may call `update_goal blocked` only after strict repeated-blocker
audit. Never block because work is hard, slow, uncertain, or merely incomplete.

## 6 Final Output

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
