# Project Memory

Durable, evidence-backed memory for long-running GoalKit projects. Keep this file short enough to read, and move domain detail into linked docs when needed.

## Current State

    objective: n/a
    active_milestone: n/a
    active_detail_override: n/a
    host_complete_policy: global_success_only
    verified_unmet_close_policy: milestone_only
    source_close_authority: n/a
    continuation_markers: n/a
    current_task: n/a
    checklist_state: n/a
    terminal_outcome: pending
    open_gates: none
    next_bounded_path: n/a
    route_discovery: n/a
    productive_output: n/a

## Promoted Facts

    none

Format: `[F# from=E# path=<artifact>] <fact that future work may rely on>`

## False Gates

    none

Format: `[G# from=E#] <predicate>=false; why; next_bounded_path=<path/task>; blocker_hash=<stable id if repeated>; blocked_external_required=<exact external condition or n/a>`

## Rejected Paths

    none

Format: `[R# from=E#] <path/axis>; rejected because <evidence>; do_not_retry_until=<condition>`

## Route Queue

    none

Format: `[Q# depends=<F#/G#>] <next exact project task>; verifier=<command/check>; output=<artifact>; not_control_only=true`

## Activity Log Index

    none

Format: `[I# from=E#] current_task=<id>; checklist_state=<n/a|completed/total>; output=<artifact/command>; verified=<literal>; next=<task>`

## Verifier Registry

    none

Format: `[V#] <name>; signal=<a|b|smoke|secret|audit>; path=<script/artifact|n/a>; sha256=<hex|unchecked>; command=<exact>; expected=<literal>; last_pass=<E#|none>`

## Artifact Index

    none

Format: `[A# from=E#] <path>; role=<source|derived|doc|script|fixture|report>; status=<candidate|promoted|stale>`

## Milestone Handoffs

    none

Format: `[H# from=E#] milestone=<M#>; handoff=<path|n/a>; checklist=<path|n/a>; checklist_state=<n/a|completed/total next=<item|n/a>>; current_task=<id>; next_exact_task=<task>; next_bounded_path=<path/task|n/a>`

## Stale Memory

    none

Format: `[S# contradicts=<F#/G#/R#> from=E#] <what changed and how future agents should treat it>`
