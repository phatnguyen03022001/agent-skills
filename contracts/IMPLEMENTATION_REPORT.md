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

## Backward-compatible operational timing evidence

Protocol-v3 timing schema is backward-compatible: historical and existing reports without `operational_timing` remain valid and require no backfill. For newly produced reports governed by the forward collection semantics, include `operational_timing` whenever both required boundary timestamps were truthfully captured from a trustworthy current UTC clock. Omission is valid only when trustworthy current timing was unavailable at either required boundary. Never partially populate the block or invent, approximate, reconstruct, or derive either timestamp from Git commit times.

When present, `operational_timing` contains exactly `started_at_utc` and `terminal_decision_at_utc`, both as RFC 3339 UTC timestamps. `started_at_utc` is captured after the exact task/repository/base binding is resolved and immediately before capability preflight. Approval-to-start or queue latency remains separate repository lifecycle evidence and MUST NOT be represented as Executor processing time. `terminal_decision_at_utc` is captured when the Executor reaches its terminal task result, before report publication. Elapsed processing duration is derived from those two timestamps and MUST NOT be stored as another canonical duration field.

This timing is non-authoritative operational telemetry only. It cannot prove or affect PASS, quality, acceptance, authority, capability, identity, independence, lifecycle, promotion, release, or performance compliance.

The existing report shape also represents truthful terminal failure. A report may record authoritative verifier FAIL, blockers, and an existing terminal/blocking `result` while remaining Executor-owned evidence; successful verification is not required for report validity or publication when the exact task grants report commit/push authority. Persisting such a report never converts FAIL to PASS and never creates Architect review, continuation, promotion, or release authority.

If report commit/push authority or required publication capability is unavailable, the Executor returns the exact non-durable terminal result and must not claim that canonical report evidence exists.

A report may remain `state: REPORTED` and `result: NEEDS_REVIEW` after later Architect acceptance because report evidence and review judgment are separate artifacts under the Task Protocol.

Executor classifies discoveries according to the Task Protocol and does not treat CI/Git success as authoritative project PASS unless target authority explicitly designates that evidence.