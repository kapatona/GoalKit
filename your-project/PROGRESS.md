# PROGRESS

Agent-owned state for one active `/goal`. Update after substantive work, verifier output, bootstrap, milestone boundary, or real escalation. Schema is in AGENTS.md.

## state

    updated: not_started
    goal_start: not_started
    active_goal: none
    status: not_started
    autonomy: solo
    checkpoint: -
    current_milestone: n/a
    current_task: id=bootstrap; kind=bootstrap; status=ready; output=GOAL.md/PLAN.md/PROGRESS.md; verifier=bootstrap smoke; next=first artifact-producing task
    checklist_state: n/a
    next_action: Fill GOAL.md then start structured `/goal`, or start prose `/goal` for autonomous bootstrap.
    next_bounded_path: n/a
    route_discovery: n/a
    productive_output: n/a
    active_detail_override: n/a
    blockers: none
    caps: iter=0/unset timeout_policy=adaptive_per_command last_command=n/a control_scope=whole_goal
    done_gate: pending evidence=none
    objective_fidelity: pending evidence=none
    terminal_outcome: pending evidence=none
    open_gates: none
    verifier_smoke: pending evidence=none
    checkpoint_state: cp_0=pending cp_final=pending

## objective_lock

    source_objective: n/a
    terminal_deliverables: none
    missing_deliverables: none
    deferred_deliverables: none
    completion_class: unset
    recovery_ladder: n/a
    host_complete_policy: global_success_only
    verified_unmet_close_policy: milestone_only
    source_close_authority: n/a
    continuation_markers: n/a

## route_queue

    none

Format: `[Q# depends=<E#/F#/G#>] <project action>; output=<artifact/path>; verifier=<command/check>; not_control_only=true`

## activity_log

    none

Format: `[timestamp current_task=<id>] action=<what changed or ran>; output=<artifact/command>; verified=<literal result>; next=<next exact project task>`

## memory_index

    none

Format: `[M# from=E#] <path>; role=<doc|script|fixture|analysis|code>; status=<candidate|promoted|stale>`

## evidence

    none

## evidence_jsonl

    none

Format: optional machine-readable mirror for final/audit evidence rows:
`{"id":"E#","cp":"cp_final","axis":"signal_a","kept":true,"fresh":true,"result":"pass","source":"command_output"}`

## lessons

    none

## escalations

    none

## closing

    none
