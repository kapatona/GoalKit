# GOAL

Local contract for the active Codex `/goal`. Keep it short. The host `/goal`
objective and newest user instruction stay canonical.

```text
objective: <literal user objective or referenced plan/spec>
status: not_started
stopping_condition: <verifiable end state or explicit finite-report condition>
cost_ceiling: <advisory local note for tokens/time/cost, or n/a; Codex /goal token_budget owns enforcement>

scope_may_change:
- <project paths allowed>

scope_must_not_change:
- secrets, credentials, read-only evidence, unrelated user changes
- <project-specific protected paths>

held_out_tests: n/a

protected_paths:
- <paths that strict scope guard must not see changed, or n/a>

success_criteria:
- <observable outcome>
- <observable outcome>

verifiers:
- <command/check/artifact and expected result>
- <independent verifier, or n/a for small work>

verifier_independence: <why verifier signals fail differently, or n/a>
done_gate_anti_trivial: <why the gate fails on empty/no-op implementation>
next_task: <one exact project task>
```

Completion requires fresh verifier evidence for the success criteria and no
known executable next task in scope.
