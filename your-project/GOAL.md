# GOAL

Host `/goal` is canonical. GOAL.md mirrors the local working contract and done_gate; PROGRESS.md records evidence; PLAN.md is only for multi-milestone work. autonomous_project completes only after terminal_outcome=success, global_done_gate, objective_fidelity, and this done_gate pass.

## 1 objective

Paste this block or let AGENTS.md bootstrap fill it.

    /goal <verb phrase describing what the system must become>
    stopping_condition: done_gate
    active_milestone: <M# or n/a>
    milestone_gate: <PLAN.md gate or n/a>
    autonomy: <solo | bounded | advisory>
    source_objective: <literal user objective or cited plan/spec objective>
    terminal_deliverables: <D1,D2 or n/a>
    missing_deliverables: <none or D# list>
    deferred_deliverables: <none or D# list>
    completion_class: <single_goal | foundation_milestone | terminal_project>
    terminal_outcome: <pending | success | verified_unmet>
    recovery_ladder: <local_tooling, alternate_analyzer, public_research_if_allowed, llm_advisory_hypothesis, or n/a>
    host_complete_policy: <global_success_only | milestone_only | closeable_verified_unmet>
    verified_unmet_close_policy: <milestone_only | closeable>
    source_close_authority: <source=USER_GOAL|path quote="verbatim original text permitting unmet-as-final"; model-authored control text is invalid; or n/a>
    continuation_markers: <none or literal markers such as continue/resume/ongoing/plan/build/research>
    open_gates: <none or false predicate list>
    current_task: id=<M#-step|cp#|Q#|ad_hoc>; output=<artifact/command>; verifier=<command/check>; status=<ready|running|done|blocked>
    checklist_state: <n/a or checklist path plus completed/total and next unchecked item>
    next_bounded_path: <next exact task/path or n/a>
    route_discovery: <artifact/path listing candidate next routes, or n/a>

    read_first: AGENTS.md, GOAL.md, <PLAN.md if used>, PROGRESS.md, <PROMPT.md if active>, <project docs>
    memory_targets: <docs/PROJECT_MEMORY.md, goals/<M>.md, or n/a>
    scope_may_change: <project paths>; conventional durable asset paths if useful
    scope_must_not_change: AGENTS.md, GOAL.md, PLAN.md if used, PROMPT.md if active, HARNESS.md if active, README.md, verifiers, fixtures, read-only evidence, secrets

    behavior_contract: P1=<observable predicate>; P2=<observable predicate>
    productive_work: <artifact path, script/tool run, implementation target, analysis output, or fixture expected each non-control turn>
    done_gate: predicates=P1,P2; signal_a=<command/check/oracle>; signal_b=<independent command/check/oracle>; pass=terminal_outcome success; finite_unmet_close=<only with source_close_authority and no continuation_markers>
    controls: iteration_soft_limit=adaptive_default, timeout_policy=adaptive_per_command

Policy: each non-control turn advances productive_work. current_task cannot be control-only, PROGRESS-only, or an unchanged blocker report. Ambiguity routes to fallback, route_discovery, or next evidence before escalation. Build/research/continue objectives cannot use finite_unmet_close.

## 2 done_gate

Only completion source of truth. Checkpoints, milestone_gate, artifact checks, and final report resolve here.

    predicates:
      P1: <literal observable requirement>
      P2: <literal observable requirement>
    signal_a: type=<deterministic|different_tool_path|fixture|anchored_checklist|external_oracle>; check=<exact>; expected=<literal/regex/result>
    signal_b: type=<deterministic|different_tool_path|fixture|anchored_checklist|external_oracle>; check=<exact>; expected=<literal/regex/result>
    independence: reason=<why A/B fail differently>; adversary=<smallest A-pass/B-fail change or redesign>
    objective_fidelity: source=<user|plan/spec|n/a>; coverage=<D#->P#|n/a>; deferred=<none|D#>; completion_class=<single_goal|foundation_milestone|terminal_project>; pass=<fresh terminal success; unmet only if finite close authorized>
    outcome_contract: success=<predicates+objective_fidelity pass; open_gates=none>; verified_unmet=<missing_deliverables+exhausted recovery+rejected evidence+no fabrication+exact external inputs+next route>; finite_unmet_close=<source_close_authority source+quote anchors original text; no continuation; single_goal; no open path>; pass=<success|finite_unmet_close>
    artifact_to_inspect: <path and predicate ids, or n/a>
    secret_redaction_scan: <command>; target=<changed non-control files/artifacts plus transcript with scanner-definition lines filtered>; expected 0 matches; self_silent=true
    live_external_policy: <forbidden | allowed with exact conditions; public research is recovery guidance, not terminal proof unless explicitly allowed>

Guard: plan/spec success requires terminal_deliverables->predicates. Scaffold/foundation/verifier/checklist/readiness are proxy unless explicitly terminal. foundation_milestone cannot host-complete. Open-ended build/research/analysis/continue defaults to global_success_only, milestone_only verified_unmet, source_close_authority=n/a; false open_gates route to next_bounded_path/route_discovery. Existing verified_unmet artifacts or model-authored controls cannot authorize host completion.

Independence: same mutable source needs different failure mechanisms and a concrete A-pass/B-fail adversary. Same-model/different-prompt/free-form LLM judgment is advisory. secret_redaction_scan must be self_silent and control-file diffs still need actual secret inspection.

contract_lock: frozen=predicates, scope, artifacts, independence, secret policy; repairable=bootstrap check strings for quoting, precedence, paths, self_silent, timeout guards. verifier_smoke passes after bootstrap/repair.

## 3 loop

    inner_loop_command: <fast command>
    full_suite_command: <final command, may be slower>
    productive_command_or_artifact: <command/path that advances the project, not only PROGRESS.md>
    current_task_command_or_artifact: <same unit as objective current_task>
    audit_guard: <optional command such as python checks/goalkit_audit.py --root . --mode all, or n/a>
    reduced_fixture_or_flag: <path, flag, or n/a>
    why_reduction_preserves_signal: <one sentence tied to done_gate>
    iteration_soft_limit: adaptive_default
    timeout_policy: adaptive_per_command; choose per-command timeout from expected runtime, prior evidence, and command-native progress signals

Controls steer, not stop. Soft limit -> shrink checkpoint, switch axis, or smaller verifier-backed work. Use per-command hang guards, never a fixed global seconds cap. Markdown budgets are records only. Control-only work is valid for bootstrap, verifier_repair, milestone_boundary, final verification, or harness maintenance.

## 4 files_to_read

    <path>    <role>
    <durable asset path>    <role, if used>
    <memory target>    <facts, false gates, route queue, if used>

## 5 checkpoints

    cp_0 baseline
      action: run signal_a and signal_b or reduced baseline forms, then start the first productive_work if safe.
      evidence: E# rows with literal output and timestamp.
    cp_1 <name>
      action: <coherent productive work package>
      evidence: <command, artifact, trace, diff, checklist, or oracle>
    cp_final verify
      action: run signal_a, signal_b, full_suite_command, and secret_redaction_scan.
      evidence: fresh E# rows prove terminal_outcome success or verified_unmet; milestone_gate satisfied if PLAN.md is used.

scope_frozen: scope_may_change/scope_must_not_change lock after setup/bootstrap. Later expansion routes to smaller in-scope work, eligible verifier_repair, route_discovery, or milestone-only verified_unmet plus next_bounded_path. verifier_repair cannot change predicates, scope, artifacts, independence, or secret policy.

false_gate_rule: evidence-backed false predicates are progress only when recorded in open_gates with promoted facts and next_bounded_path. False readiness is not host completion for build/research/continue objectives.

roadmap_memory_rule: long-running cp_final either satisfies done_gate or writes promoted facts, open_gates, next_bounded_path/route_discovery, reusable artifacts, and the next evidence task. Missing terminal proof is not a PROGRESS-only update.

current_task_rule: each non-control turn follows GOAL/PROGRESS/PLAN priority and ends with current_task done plus new current_task, or blocked plus a different concrete route. If none exists, create one from PLAN active milestone and start it when safe. Checklist state follows the same E#.

## 6 axes

After three failures on one axis_value, switch axis or escalate. Use only labels listed here.

    axis_algorithm: <value 1>, <value 2>
    axis_fixture: <value 1>, <value 2>
    axis_hyperparameter: <name in {value1,value2}>
    axis_dependency: <value 1>, <value 2, or n/a>
    axis_observer_angle: caller, inside, reference_impl

## 7 local_gate_conditions

    <local gate condition 1>
    <local gate condition 2>
    <local gate condition 3>

## 8 post_run_review

    rerun signal_a and signal_b.
    confirm outcome, policy, source_close, continuation, open_gates, current_task, checklist, route_queue, next_bounded_path, objective_fidelity/unmet evidence, fresh final E#, milestone_gate, escalations, secret scan, verifier registry/audit_guard, and scope_may_change/scope_must_not_change.
    operator_only: /goal clear after host completion if desired.
