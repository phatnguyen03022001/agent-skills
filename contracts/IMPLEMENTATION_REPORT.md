# Implementation Report

The canonical Executor-owned evidence shape is [templates/report.yaml](../templates/report.yaml). Target repositories may store it as `.agent/tasks/TASK-NNNN/report.yaml`.

Executor owns report content. Architect reviews it but does not rewrite it. A report may remain `state: REPORTED` and `result: NEEDS_REVIEW` after an external Architect accepts that exact report; later review state is separate evidence.

## Commit identity

`execution.final_execution_head` is the last implementation HEAD before the report artifact is committed. It is distinct from the later commit that contains the report.

When canonical report evidence is committed, Executor must have commit authority under the exact task. The Architect review identifies that exact committed report as `reviewed_report.commit`; an uncommitted copy or different report revision is not review identity.

The report commit is still not automatically `promotion_candidate_head`. After Architect accepts `R = reviewed_report.commit`, only `R` itself or one single-parent direct child whose only parent is `R` and that contains solely the expected Architect-owned review artifact can become the candidate without a new report/review cycle.

## Capability preflight evidence

The canonical template includes a small `capability_preflight` record for the Executor phase: phase, required semantic capabilities, observed available/missing capabilities, and pass/fail. It proves availability only for that phase at that time. It does not grant authority and does not claim later-phase capabilities are available.

Current-phase missing required capability blocks before mutation. A later unavailable release capability may leave an earlier accepted and promoted candidate valid as `PROMOTED_NOT_RELEASED`.

## Evidence

The report records exact base/final execution heads, pinned skill revision, pre-execution gates, changed files, commits/pushes, acceptance evidence, checks, authoritative verifier status when applicable, discovered gaps, structural observations, deviations, blockers, and final Executor result.

Executor classifies discoveries as `LOCAL`, `FOLLOW_UP`, or `BLOCKING` under the [Task Protocol](../protocols/TASK_PROTOCOL.md). CI or Git success alone is not authoritative project PASS.
