# GoalKit-Compact

Minimal project memory for long Codex `/goal` runs.

Codex owns the host goal, lifecycle, compaction, token budget, and final goal
status. GoalKit-Compact only adds the local contract Codex does not know:
the project done gate, current resume snapshot, durable decisions, and optional
verifier checks.

## Use

Copy `your-project/` into a target repo, or copy its contents into the repo
root:

```text
your-project/
  AGENTS.md
  GOAL.md
  PROGRESS.md
  DECISIONS.md
  checks/
    goalkit_audit.py
    holdout_guard.py
    verifier_lock.py
    scope_guard.py
```

If the target repo already has `AGENTS.md`, merge the rules instead of
overwriting project-specific instructions.

## Start

1. Fill `GOAL.md`.
2. Start Codex with one objective and one verifiable stopping condition.
3. Work on project files first.
4. Verify with tests, commands, diffs, or inspected artifacts.
5. Replace `PROGRESS.md` once with the latest state.
6. Append only durable, evidence-backed decisions to `DECISIONS.md`.

`PROGRESS.md` is a resume snapshot, not a transcript. Keep it under 60 lines.

## Rules

- One goal, one stopping condition.
- Raw project artifacts and verifier outputs are the evidence of record.
- No ledgers, route queues, JSON mirrors, or recurring memory rewrites.
- Completion requires fresh evidence and no executable in-scope next task.
- Blocking requires an exact external condition, not difficulty or uncertainty.
- Strict checks are executable guards, not a second workflow engine.
