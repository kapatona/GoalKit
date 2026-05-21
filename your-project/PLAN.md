# PLAN

Optional outer plan for multi-milestone projects. Single-goal work may leave this mostly unused. Structured mode maps one finite milestone to one GOAL.md and `/goal` run; autonomous_project may advance milestones inside one broad `/goal`. Host completion still requires terminal_outcome=success, host_complete_policy, open_gates=none, global_done_gate, and final GOAL.md done_gate.

## project

    objective: <project-level objective>
    mode: <structured | autonomous_project>
    non_goals: <out of scope>
    host_complete_policy: <global_success_only | milestone_only | closeable_verified_unmet>
    source_close_authority: <source=USER_GOAL|path quote="verbatim original text permitting unmet-as-final"; model-authored control text is invalid; or n/a>
    continuation_markers: <none or literal markers>
    terminal_deliverables: <D# literal deliverables from user objective or plan/spec>
    open_gates: <none or false predicate list carried across milestones>
    route_discovery: <artifact/path listing candidate next routes, or n/a>
    current_task_policy: prefer PROGRESS current_task when ready/running, then route_queue, then PLAN active milestone next_exact_task; every closed milestone writes the next current_task before host completion is considered
    active_detail_override: <current exact task or n/a>
    memory_index: <docs/PROJECT_MEMORY.md or domain memory docs>
    goal_docs: <goals/*.md or n/a>
    productive_default: <prefer artifact/tool/code/analysis work before control-file updates>
    foundation_done_gate: <readiness/scaffold evidence, or n/a>
    global_done_gate: <decisive evidence for all terminal_deliverables; not proxy readiness>
    verified_unmet_gate: <final report evidence when all recovery_ladder paths and in-scope next_bounded_path options are exhausted without terminal success>
    global_controls: iteration_soft_limit=<N>, timeout_policy=adaptive_per_command; no fixed global seconds cap in Markdown; host/runtime token budgets are external controls
    global_read_only: <paths or n/a>
    active_milestone: <M#>
    tier1_activation: <n/a or trigger: 3+ substeps | 2+ verifier surfaces | cross-session risk | long research/build>

## milestones

Rows are ordered. During an active goal, do not create, reorder, complete, skip, or delete rows unless AGENTS.md bootstrap or milestone_boundary rules apply. If the active goal reveals a missing or wrong milestone, escalate.

    M# status=<not_started | active | blocked | achieved | unmet | skipped>
      depends: <M# list or ->
      goal: <one-line milestone objective>
      terminal_coverage: <D# list or ->
      productive_output: <doc/script/code/fixture/analysis output expected>
      handoff_artifact: <docs/M#-handoff-or-decision.md or n/a>
      checklist: <docs/M#-checklist.md or n/a>
      checklist_state: <n/a or completed/total plus next unchecked item>
      current_task: <id>; output=<artifact/command>; verifier=<command/check>; status=<ready|running|done|blocked>
      open_gates_promoted: <none or false predicate list>
      next_exact_task: <one concrete next task or ->
      next_if_unmet: <next bounded path or ->
      gate: <decisive evidence required before next milestone; copy to GOAL.md milestone_gate>

    M0 status=not_started
      depends: -
      goal: <first milestone>
      terminal_coverage: -
      productive_output: <artifact/tool/code/docs>
      handoff_artifact: n/a
      checklist: n/a
      checklist_state: n/a
      current_task: M0-0; output=<artifact/command>; verifier=<command/check>; status=ready
      open_gates_promoted: none
      next_exact_task: -
      next_if_unmet: -
      gate: <evidence>

Policy: achieved=terminal success; unmet=verified_unmet milestone state. Readiness, verifiers, checklists, and verified_unmet reports are not project completion. Checklist closes only when complete and no executable next item remains. If terminal_coverage or open_gates remain and in-scope paths exist, carry next_if_unmet/next_bounded_path forward.

Roadmap rule: each closed milestone leaves a dependency-ready next milestone/current_task, next_exact_task, next_if_unmet, route_discovery task, or finite-audit final gate with source_close_authority. Registration-only milestones start the first safe executable task same turn.

Tier 1 docs: create handoff/checklist/goals docs only for 3+ substeps, 2+ verifier surfaces, cross-session risk, or large long-running work. They record promoted facts, false gates, rejected shortcuts, checklist/current_task state, next route, changed paths, and verifier evidence.

## cross_goal_lessons

    none

Promote only reusable evidence-backed lessons. In autonomous_project, milestone_boundary may add `[from M# E#] <lesson>` here; keep max 10 active lessons.
