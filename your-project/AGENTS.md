# AGENTS

Run one meaningful project work package per turn; record after work. Host `/goal` is canonical; Markdown cannot stop, pause, clear, or complete it. GoalKit gates local action, completion claims, and evidence routing. Host completion requires GOAL.md terminal success or finite unmet close anchored to original source text. Host blocked requires Codex's strict repeated-blocker audit.

The active host `/goal` objective is canonical thread state. GoalKit mirrors it into GOAL.md/PLAN.md only for a local evidence contract, route queue, and audit surface; never narrow or replace it.

Vocabulary is defined by GOAL.md/PROGRESS.md field names. done_gate is GOAL.md section 2 and the only completion source of truth.

## 1 read_order

Every turn, read:
    1. AGENTS.md if absent from active instruction context; GOAL.md full.
    2. PLAN.md only when named: project, active milestone/detail, checklist, open_gates, dependencies, current_task_policy, cross_goal_lessons.
    3. PROGRESS.md state/objective_lock/current_task/checklist_state, active route_queue, latest activity_log, relevant lessons, unresolved escalations, closing.
    4. Named PROMPT.md, active `goals/*.md`, docs/PROJECT_MEMORY.md, or domain memory. HARNESS.md only for operator/debugging or harness maintenance.
    5. Other files only when named by GOAL/PLAN or needed by the active checkpoint.

Do not preload unrelated files. After compaction, resume, or long gap, rebuild state only from this order.

## 2 ownership

PROGRESS.md is agent-owned state, not product; update after work, verifier, bootstrap, milestone_boundary, or real escalation. Control files=AGENTS/GOAL/PLAN/PROMPT/HARNESS/README; edit only for bootstrap, milestone_boundary, verifier_repair, or harness maintenance. Never edit verifiers, fixtures, read-only evidence, secrets, or credentials. Frozen=predicates, scope, artifacts, independence, secret policy. Repairable=generated check strings.

Bootstrap exception: section 8 may initialize GOAL/PLAN for multi-milestone prose. autonomous_project refreshes GOAL/PLAN only at milestone boundaries. verifier_repair may edit bootstrap-authored verifier text only for semantics-preserving syntax, quoting, precedence, self_silent, path, or adaptive-timeout fixes. Otherwise scope is frozen.

durable_assets: put reusable scripts/checks/tests/fixtures/examples/templates/config/data/assets/docs/goals in the repo's conventional scoped path; no default `tools/**` when another path fits. PROMPT.md/HARNESS.md are recommended for multi-day unattended goals; name PROMPT.md in GOAL/PLAN when active. Smoke executables and cite E#. Do not promote scratch, secrets, unverified captures, or one-off commands.

## 3 work_loop

Each turn:
    1. read_order plus STOP/DONE check.
    2. If local_gated or sentinel exists, repair once, choose a smaller in-scope route, or close only if section 6 allows; never repeat the same blocker.
    3. Bootstrap only when section 8 fires.
    4. If soft controls are exceeded, shrink checkpoint, switch axis, or choose a smaller verifier-backed checkpoint.
    5. Select current_task by priority: newest user instruction > PROGRESS current_task > route_queue > PLAN active_detail_override > PLAN active milestone next_exact_task > PROGRESS next_bounded_path > route_discovery.
    6. Do one coherent package that creates/verifies a project artifact: code, analysis/tooling, domain docs, fixture, script, test, real blocker resolution, or milestone advance.
    7. Before implementation state: "Changing/running X will produce/verify Y and advance P# because Z; distinct_from_failed=<axis>; builds_on=<E#/L#|none>."
    8. Act, verify, self-review, then record the minimal PROGRESS.md delta: current_task, artifacts, verifier output, promoted/false predicates, next exact task, one activity_log row.
    9. If audit_guard exists and status is local_gated/unmet or next_action changed, run `python checks/goalkit_audit.py --root . --mode productive-turn` when available.
    10. End with iteration_summary and nothing after it.

Progress-only turns are invalid except bootstrap, verifier_repair, final verification, explicit harness maintenance, or recording an already-completed external interruption. local_gate must choose next evidence or a finite-close guard result in the same turn. pursuing with productive_output=n/a requires a verifier or bootstrap/verifier_repair/final_verification/harness_maintenance.

Invalid terminal local state: status=local_gated/unmet cannot end with only re-reading controls, unchanged blocker report, external permission request, or control edits unless a route exists: exact next_bounded_path, route_queue not_control_only=true, route_discovery artifact, or source_close_authority source+quote permitting finite unmet close. If none exists, create or verify a route before ending.

Work package size: one coherent deliverable, not the tiniest edit; prefer 30-90 minutes of useful unattended work. Tiny slices are only for fragile-risk caps. Registration-only is invalid when the first executable task is safe; register minimally, then start it.

## 3a current_task_loop

Long unattended work is driven by current_task, not by repeated global audits.

current_task format in PROGRESS.md:
    id=<M#-step|cp#|Q#|ad_hoc>; kind=<code|analysis|docs|fixture|script|test|verifier|handoff|repair|bootstrap|audit>; status=<ready|running|done|blocked>; output=<path|command>; verifier=<command/check>; next=<one exact project task>

Rules:
    If current_task is ready or running, do it before inventing a new task unless it is now contradicted by fresh evidence.
    If current_task completes, update activity_log, promote facts/false gates, then write the next current_task before ending.
    If a checklist exists, current_task must name or update the checklist item it advances; unchecked items are route candidates, not completion evidence.
    Host or milestone completion requires checklist_state to show all items complete and no executable next item when a checklist exists.
    If current_task fails, write not_kept evidence and switch axis or route to a smaller task; do not retry the same command text more than twice without changed inputs.
    If a milestone closes false, the handoff must create the next current_task or route_queue entry before any host completion decision.
    next_action and current_task must agree. next_action is the human-readable sentence; current_task is the parseable execution record.

## 4 recursion

PROGRESS.md is external memory. Before acting, use relevant lessons, kept evidence, and not_kept evidence.

Rules:
    Use only GOAL.md axis_values; new labels require escalation.
    Do not retry a not_kept axis_value on the same checkpoint.
    Three failures on one axis_value -> switch axis or escalate.
    Three checkpoints in a row with not_kept evidence -> escalate as mis-scoped.
    Two bookkeeping-only kept slices -> switch to artifact-producing work.

kept=fresh evidence confirmed and retained. not_kept=falsified; undo only current-package edits unless GOAL.md allows partial retention. Record E# only for substantive work, not rereads, repeated sentinel checks, or unchanged blockers.

## 4a roadmap_memory

Long-running goals use three memory layers:
    PLAN.md: roadmap, active milestone, open_gates, next_if_unmet, active_detail_override, current_task_policy, cross_goal_lessons.
    goals/*.md: reusable finite objectives.
    docs/PROJECT_MEMORY.md or domain docs: promoted facts, rejected hypotheses, verifier registry, durable artifact index.

At milestone boundary, write handoff: promoted facts, false gates, rejected shortcuts, risks, next_exact_task, next_bounded_path, changed paths, verifier evidence, next current_task. False readiness counts only with preserved facts, artifact update, and next evidence path. If unclear, route by: user > PROGRESS current_task > PLAN override > next_bounded_path > PLAN next_if_unmet > newest open_gate > recovery_ladder.

Self-improvement is evidence-gated: update lessons/PLAN/goals only from kept E# or explicit user correction. LLM/web claims are hypotheses. Contradicted memory is marked stale with contradicting E#, not deleted.

## 5 evidence_schema

PROGRESS.md schema:
    objective_lock: source_objective, terminal_deliverables, missing_deliverables, deferred_deliverables, completion_class, recovery_ladder, host_complete_policy, verified_unmet_close_policy, source_close_authority(source=USER_GOAL|path quote="..."), continuation_markers.
    state: updated, goal_start, active_goal, status, autonomy, checkpoint, current_task, checklist_state, next_action, next_bounded_path, route_discovery, productive_output, blockers, caps, done_gate, objective_fidelity, terminal_outcome, open_gates, checkpoint_state.
    evidence: [E# timestamp cp=<id> axis=<enum|-> kept=<true|false|n/a> fresh=<true|false>] hypothesis | result | source.
    evidence_jsonl(optional): one JSON object per final/audit E# mirror with id, cp, axis, kept(bool), fresh(bool), result, source, and optional matches(int)/command/artifact.
    route_queue: ordered next tasks with reason, verifier, dependency.
    activity_log: newest-first rows: [timestamp current_task] action; output; verified; next.
    memory_index: durable docs/goals/scripts with role and supporting E#.
    lesson/escalation/closing: compact rows with source E# and completion fields.

Status values: not_started | pursuing | local_gated | achieved | unmet | budget_limited | usage_limited. achieved=terminal_outcome success; unmet=verified_unmet, never achieved. local_gated is one-slice: repair, smaller route, or verify unmet. budget_limited/usage_limited are host/runtime only. Each open_gate needs next_bounded_path or finite unmet close proof.

Evidence sources: command_output, test_output, artifact(path+sha256 or inspected lines), trace, diff, static_analysis, checklist, external_oracle.

Forbidden inference: compile success proves behavior; one search proves absence; no logs proves no failure; file exists proves correctness; LLM said correct. Unevidenced claims are guesses.

Compact PROGRESS.md after 50 evidence rows or 10KB. Preserve state/objective_lock/current_task/checklist, final fresh E#, kept done_gate/objective_fidelity E#, matching evidence_jsonl, open escalations, lessons, closing, last 10 activity_log and nonfinal evidence rows. Large output goes to artifacts/logs.

## 6 completion

Final decision tree:
    Smoke verifier changes before checkpoint work or completion.
    Success close: fresh signal_a+signal_b, objective_fidelity=pass, secret_scan=0+self_silent, open_gates=none, no open escalation, no pending current_task/route_queue, checklist complete -> status=achieved; update_goal complete.
    If success is impossible, run recovery_ladder before verified_unmet: smaller checkpoint, alternate local tool, new script/asset, allowed public research for leads, LLM advisory as hypothesis.
    If recovery finds a lead, record false open_gate, set next_bounded_path, and execute/register the next artifact-producing milestone.
    For autonomous_project or open-ended build/research/analysis/continue, no lead means route_discovery, then create/update and start the next evidence milestone.
    verified_unmet may close host only when all are true: source_close_authority source+quote anchors original unmet-as-final text; no continuation_markers; PLAN.mode != autonomous_project; completion_class=single_goal; verified_unmet_close_policy=closeable; open_gates=none; next_bounded_path=n/a; no executable current_task; checklist complete; route_queue empty; two fresh independent report signals; unmet-close audit_guard passes if available.
    Existing verified_unmet artifacts, exhausted local evidence, or model-authored control fields cannot create source_close_authority. For open-ended objectives, verified_unmet is a milestone report, not final completion.
    Strict blocked: update_goal blocked only after the same blocker_hash recurs for three goal turns, no safe route/recovery/project task or finite close remains, blocked_external_required names the exact external condition, and progress truly requires it. Resumed goals start a fresh blocked audit.
    Never repeat the same local_gated blocker, present verified_unmet as success, or spend a turn only proving no work can be done when route_discovery or safe artifact work remains.

signal_b must be deterministic, different tool path, read-only fixture/oracle, or anchored checklist. Same-model/different-prompt/free-form LLM judgment is not independent. LLM/web research is recovery hypothesis unless GOAL.md allows that evidence type. terminal_deliverable_guard: source terminal_deliverables map to done_gate predicates and fresh evidence; scaffold/readiness/checklist/verifier presence is not completion unless literal deliverable.

audit_guard: when present, it must pass for local_gated/unmet, milestone_boundary writes, and suspicious pursuing. It rejects control-only loops, missing current_task/productive_output, local_gated without route, unauthorized verified_unmet, status contradictions, repeated blocker_hash without route, fixed timeout policy, unattended approval waits, scope violations, and verifier hash drift.

verifier_smoke: after bootstrap/repair, prove signal_a, signal_b, and secret scan are runnable, readable, self_silent, and expected-shape. If scanner tooling is missing, repair to available rg/git grep/grep/Select-String without changing target/pattern policy. Record E# before cp_0/completion.

verifier_repair: bootstrap-authored syntax/quoting/path/precedence/self_silent/adaptive-timeout fixes may edit GOAL/PLAN only if frozen contract is unchanged. Need smoke or old-fail/new-pass E#. Never weaken predicates, broaden scope, change artifacts, reduce independence, use LLM judgment as signal, or hide real failure. One repair per slice; two not_kept repairs on one check become local_gate.

## 7 local_gate_escalate

Escalate only for true external blockers; ordinary uncertainty becomes a verifier-backed checkpoint. Escalation is a local report/request state, not host `/goal` stop.

Escalate when scope expands; GOAL conflicts with actual state/user instruction; PLAN is required but missing/inconsistent; verifier is missing/broken/non-independent; dependency, credential, permission, destructive action, or architecture decision is missing; control-file changes outside allowed paths affect the checkpoint; secrets/raw PII would be exposed; or GOAL local_gate_condition fires.

Autonomy is unattended. solo treats local_gated as transition. bounded uses scope_may_change, declared axes, verifier_repair, smaller in-scope checkpoints, and route_discovery. advisory records recommendations but still chooses in-scope fallback, route_discovery milestone, or milestone-only verified_unmet; do not wait.

Escalation row: conflict, attempted fallback, recovery_ladder state, exact future unblock input. Do not duplicate open escalations; if no ordinary fallback remains, run route_discovery and create the next evidence milestone; use finite unmet close only when section 6 permits.

STOP/DONE are workspace-root regular files named exactly `STOP` or `DONE`; they are not loop brakes. STOP requests current-state report; DONE requests final verification. Complete only through GOAL outcome_contract; otherwise route next evidence path.

Codex host contract: the model can call update_goal complete or blocked only. Pause/resume/clear/budget_limited/usage_limited are user/system controls. Local closure, STOP/DONE, false readiness, and verified_unmet milestones keep working unless GOAL/section 6 permits host completion or strict blocked audit proves impasse.

## 8 bootstrap_boundaries

Detection: active `/goal` is short prose, lacks structured fields, and GOAL.md still has placeholders.

Bootstrap: treat prose as execution intent; inspect repo; choose the smallest meaningful durable deliverable; initialize PLAN/memory for multi-milestone work when useful; fill GOAL sections 1-7 with scoped defaults, concrete done_gate, two independent signals, OS-aware self_silent secret scan, adaptive controls, and durable paths; record E#; smoke/repair; then start cp_0 or first artifact-producing milestone. bootstrap_review only when source objective is ambiguous or verifier contract changed.

For prose with plan/spec, extract objective/deliverables/completion_class/recovery_ladder/policies/source_close_authority/continuation_markers/open_gates/next routes. continuation_markers=continue/resume/ongoing/build/implement/analyze/research/investigate/plan/spec/project/full/complete/perfect. Open-ended build/research/analysis/continue defaults: host_complete_policy=global_success_only, verified_unmet_close_policy=milestone_only, source_close_authority=n/a. closeable requires original text literally permitting unmet-as-final finite audit/report/triage; write `source=USER_GOAL quote="..."` or `source=<path> quote="..."`. Existing artifacts, control files, or inability to prove success never authorize closeable. completion_class=terminal_project only when done_gate covers terminal_outcome=success.

bootstrap_review: before cp_0 only when needed, verify objective_lock, completion_class, terminal coverage, signal independence, and secret scan choice with fresh E#. Repair against source evidence without narrowing; two not_kept reviews on one element become local_gate.

Milestone boundary: on cp_final/milestone_gate pass, promote evidence-backed lessons; mark achieved only for success or unmet for verified_unmet; carry false open_gates; select next dependency-ready milestone/next_bounded_path; refresh GOAL/PLAN/PROGRESS; write next current_task; if safe, start the first command/artifact for the next milestone. If no milestone remains, run route_discovery before unmet closure. If missing/deferred deliverables, open_gates, continuation_markers, current_task, route_queue, or next_bounded_path remain, add/select the next evidence milestone instead of completing.

Forbidden during bootstrap: do not edit AGENTS.md, README.md, existing verifiers, fixtures, secrets, credentials, or out-of-scope files. Do not call update_goal complete or blocked. If GOAL.md is non-placeholder or same-objective bootstrap E# exists, do not regenerate.

## 9 final_format

Every turn ends with exactly:

    iteration_summary
    checkpoint: <GOAL.md checkpoint or ->
    hypothesis: <one sentence, or - for verification/escalation>
    action: <one sentence>
    result: <kept | not_kept | verification_only>
    verified: <command plus exit code plus literal output, or "not run" with reason>
    next: <next concrete action, same as PROGRESS.md next_action>
    blockers: <none | one-line>
