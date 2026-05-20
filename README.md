# GoalKit

Markdown harness for long Codex CLI or Codex app `/goal` runs.

GoalKit is for multi-hour or multi-day Codex work where the agent needs local
state, evidence, project memory, milestones, and completion guards.

## Install

Copy the contents of `your-project/` into your project root.

```text
your-project/
  AGENTS.md
  GOAL.md
  PLAN.md
  PROGRESS.md
  PROMPT.md
  HARNESS.md
  checks/goalkit_audit.py
  docs/PROJECT_MEMORY.md
  goals/_template.md
```

Do not blindly overwrite an existing project's `AGENTS.md`, `GOAL.md`,
`PLAN.md`, `PROGRESS.md`, `PROMPT.md`, `HARNESS.md`, `checks/`, `docs/`, or
`goals/`. Inspect and merge first.

## Direct Start

Use a normal `/goal`:

```text
/goal <your detailed objective>
```

Examples:

```text
/goal Add JWT login to this app, including database migration, API endpoints, UI flow, tests, and documentation.
```

```text
/goal Execute <plan-file>.md in full detail.
```

Do not paste GoalKit's internal file list into the goal prompt. Once the files
are in the project root, the harness is loaded from the project files.

## Files

- `AGENTS.md`: core runtime rules
- `GOAL.md`: active local goal contract and done gate
- `PLAN.md`: multi-milestone roadmap
- `PROGRESS.md`: current task, state, evidence, activity, lessons
- `PROMPT.md`: short per-turn protocol
- `HARNESS.md`: operator/debugging manual
- `checks/goalkit_audit.py`: automatic guard used by the harness when present
- `docs/PROJECT_MEMORY.md`: durable facts, rejected paths, verifier registry
- `goals/_template.md`: reusable sub-goal template

## Notes

- Codex `/goal` remains the host runtime. GoalKit only provides local project
  control files.
- Markdown files cannot pause, resume, clear, or stop the host goal.
- Completion is expected to be evidence-based, not a checklist or readiness
  claim.
- For details, read `HARNESS.md` and `AGENTS.md`.
