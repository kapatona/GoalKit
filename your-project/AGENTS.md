# AGENTS

GoalKit-Compact is a work-first local layer for Codex `/goal`. The host `/goal`
objective is canonical. These files only record the local done gate and latest
resume state.

## Read Order

Read only what is needed:

1. newest user instruction
2. `PROGRESS.md` snapshot and next task
3. `GOAL.md` objective, stopping condition, and done gate
4. project files for the current work slice

Do not read `checks/` during normal work unless the user names it or it directly
reduces current project risk.

## Work Loop

- Do project work before editing state files.
- Pick the largest safe coherent slice.
- For long `/goal` runs, set `phase: review|repair|validate` in `PROGRESS.md`.
- Keep those phases separate: review reads and reports; repair edits; validate
  runs or inspects verifiers and records evidence.
- For code, prefer implementation plus the closest useful test in the same turn.
- Verify with a meaningful command, test, static check, fixture, or artifact.
- Update `PROGRESS.md` once after verification.
- Keep final user summaries concise.

State-file-only turns are invalid except bootstrap, final verification, exact
blocker reporting, or explicit harness maintenance.

## State Budget

- Keep GoalKit bookkeeping under 10% of the turn.
- Keep `PROGRESS.md` under 60 lines by replacing the snapshot, not appending a
  transcript.
- Keep the snapshot shaped around hypotheses, verified progress, failure modes,
  next action, and blockers.
- Do not maintain ledgers, activity logs, JSON mirrors, route queues, checklist
  counters, or handoff files unless they directly reduce future project work.
- Treat raw tool output, tests, changed files, and inspected artifacts as the
  evidence of record.
- Promote durable lessons only after repeated evidence or explicit user
  correction. Put those lessons in `DECISIONS.md`, append-only.

## Completion

Complete only when:

- the user objective is satisfied, or the objective explicitly allowed a finite
  unmet report;
- the done gate has fresh evidence;
- the done gate is non-trivial: it fails on an empty or no-op implementation;
- no known executable next task remains inside scope;
- no unresolved blocker affects the result.

Do not narrow the original objective to fit current artifacts. Do not make host
completion depend on a perfect ledger.

`update_goal blocked` is allowed only after the same exact external blocker
repeats across the required host audit and no safe in-scope project route
remains. Hard, slow, uncertain, or incomplete work is not a blocker.

## Safety

- Respect user changes; do not revert unrelated edits.
- Keep secrets, credentials, read-only fixtures, and protected evidence out of
  edits and summaries.
- Treat tests or verifiers written or edited by the agent as insufficient final
  proof unless cross-checked by a held-out path, independent verifier, or user
  supplied evidence.
- If `held_out_tests`, `protected_paths`, or verifier hash locks are configured
  in `GOAL.md`, do not modify them during ordinary repair work.
- If uncertain, create or run a small verifier-backed project artifact rather
  than spending the turn on more control text.
