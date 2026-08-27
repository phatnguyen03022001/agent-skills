# Implementation Report

The canonical Executor-owned evidence shape is [templates/report.yaml](../templates/report.yaml). Target repositories may store it as `.agent/tasks/TASK-NNNN/report.yaml`.

This contract owns report-artifact obligations only. Reusable lifecycle, authority/capability, continuation, promotion-lineage, and release semantics—including `PROMOTED_NOT_RELEASED`—are owned by the [Task Protocol](../protocols/TASK_PROTOCOL.md).

## Ownership and commit identity

Executor owns report content. Architect may review it but does not rewrite it.

`execution.final_execution_head` identifies the last implementation HEAD before the report artifact is committed. When canonical report evidence is committed, the exact task must authorize that commit. Architect review later identifies the exact committed report through `reviewed_report.commit`; an uncommitted copy or different report revision is not the same evidence artifact.

## Required evidence

The report records task/base identity, pinned skill revision, pre-execution gates, changed files, implementation commits/pushes, acceptance evidence, required checks, gaps/deviations/blockers, and final Executor result.

The canonical template includes `capability_preflight` for the Executor phase: phase, required semantic capabilities, observed available/missing capabilities, and pass/fail. This is evidence of the observed execution preflight, not authority.

`local_hygiene` is optional for protocol-v3 compatibility. When present, its result is `PASS`, `RETAINED_FOR_EVIDENCE`, or `BLOCKED`, with retained identity/reason when evidence must remain. Cleanup safety semantics are defined by the Task Protocol and Executor skill rather than recopied here.

A report may remain `state: REPORTED` and `result: NEEDS_REVIEW` after later Architect acceptance because report evidence and review judgment are separate artifacts under the Task Protocol.

Executor classifies discoveries according to the Task Protocol and does not treat CI/Git success as authoritative project PASS unless target authority explicitly designates that evidence.
