# Implementation Report

The canonical Executor-owned evidence shape is [templates/report.yaml](../templates/report.yaml). Target repositories may store it as `.agent/tasks/TASK-NNNN/report.yaml`.

Executor owns report content. Architect reviews it but does not rewrite it.

## Commit identity

`execution.final_execution_head` is the last implementation HEAD before the report artifact is committed. It is distinct from the later commit that contains the report.

When canonical report evidence is committed, Executor must have commit authority under the exact task. The Architect review must identify that exact committed report as `reviewed_report.commit`; an uncommitted working copy or a different report revision is not review identity.

The report commit is still not automatically `promotion_candidate_head`. After Architect accepts `R = reviewed_report.commit`, only `R` itself or one direct child containing solely the expected Architect-owned review artifact can become the candidate without a new report/review cycle.

## Evidence

The report records exact base/observed/final execution heads, skill revision, pre-execution gates, changed files, commits and pushes, acceptance evidence, checks, authoritative verifier status when available, discovered gaps, structural observations, deviations, blockers, and final state.

Executor classifies discoveries as `LOCAL`, `FOLLOW_UP`, or `BLOCKING` under the [Task Protocol](../protocols/TASK_PROTOCOL.md). CI or Git success alone is not authoritative project PASS.
