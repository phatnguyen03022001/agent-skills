# Implementation Report

The canonical Executor-owned evidence shape is [templates/report.yaml](../templates/report.yaml). Target repositories may store it as `.agent/tasks/TASK-NNNN/report.yaml`.

This contract owns report-artifact obligations only. Reusable lifecycle, authority/capability, continuation, promotion-lineage, and release semantics—including `PROMOTED_NOT_RELEASED`—are owned by the [Task Protocol](../protocols/TASK_PROTOCOL.md).

## Ownership and commit identity

Executor owns report content. Architect may review it but does not rewrite it.

`execution.final_execution_head` identifies the last implementation HEAD before the report artifact is committed. When canonical report evidence is committed, the exact task must authorize that commit. Architect review later identifies the exact committed report through `reviewed_report.commit`; an uncommitted copy or different report revision is not the same evidence artifact.

The report records only evidence available before its own commit plus immutable identities it can truthfully name. It must not encode a same-commit post-publication predicate about its own remote visibility as `PASS`, `PENDING_FINAL_REFRESH`, or equivalent ceremony. When present, `pushed` refers to publication of `execution.final_execution_head` before report authorship; it does not claim that the report commit containing itself is already remote. After push of the report commit, fresh remote publication proof belongs to the publication consequence boundary and later review boundary, not to a self-referential field in that report.

## Required evidence

The report is a compact evidence index. It preserves exact task/revision, authorized base, candidate identity, target binding, AC-to-evidence mapping, required verification identity/results, deviations/gaps/blockers, implementation push identity, and the final Executor result. Redundant successful-process attestations and changed-file enumeration may be omitted when exact Git/task/verifier evidence reconstructs the same fact; omission never means PASS, permission, or hidden success. When present, changed-file entries remain evidence, not authority.

Canonical new reports omit reconstructible transcript fields and empty optional sections. `execution.pre_execution_head`, `skill_library.observed_revision`, `execution_skills_used`, `pre_execution_checks`, `commits_created`, `promoted_to_main`, `working_tree_after`, `changed_files`, `discovered_gaps`, `structural_observations`, `deviations_from_task`, and `blockers` are serialized only when they carry material evidence not already reconstructible from exact task/Git/verifier identity. Expanded-v3 report fields remain valid compatibility input and retain their existing validation when present.

The canonical template includes `capability_preflight` for the Executor phase: phase, required semantic capabilities, observed available/missing capabilities, and pass/fail. This is evidence of the observed execution preflight, not authority.

`local_hygiene` is optional for protocol-v3 compatibility. When present, its result is `PASS`, `RETAINED_FOR_EVIDENCE`, or `BLOCKED`, with retained identity/reason when evidence must remain. Cleanup safety semantics are defined by the Task Protocol and Executor skill rather than recopied here. Local mirror closure is `LOCAL_MUTABLE` operational hygiene and is not canonical remote authority; fresh remote proof comes from the remote consequence/review boundary.

## Backward-compatible operational timing evidence

Protocol-v3 timing schema is backward-compatible: historical and existing reports without `operational_timing` remain valid and require no backfill. New reports omit operational timing by default; include it only when an operator, task, or performance audit explicitly requests timing and both required boundary timestamps were truthfully captured from a trustworthy current UTC clock. If either requested boundary is unavailable, omit the entire block. Never partially populate the block or invent, approximate, reconstruct, or derive either timestamp from Git commit times.

When present, `operational_timing` contains exactly `started_at_utc` and `terminal_decision_at_utc`, both as RFC 3339 UTC timestamps. When explicitly requested, `started_at_utc` is captured after the exact task/repository/base binding is resolved and immediately before capability preflight. Approval-to-start or queue latency remains separate repository lifecycle evidence and MUST NOT be represented as Executor processing time. `terminal_decision_at_utc` is captured when the Executor reaches its terminal task result, before report publication. Elapsed processing duration is derived from those two timestamps and MUST NOT be stored as another canonical duration field. No timing-enabled or telemetry-mode field is added.

This timing is non-authoritative operational telemetry only. It cannot prove or affect PASS, quality, acceptance, authority, capability, identity, independence, lifecycle, promotion, release, or performance compliance.

The existing report shape also represents truthful terminal failure. A report may record authoritative verifier FAIL, blockers, and an existing terminal/blocking `result` while remaining Executor-owned evidence; successful verification is not required for report validity or publication when the exact task grants report commit/push authority. Persisting such a report never converts FAIL to PASS and never creates Architect review, continuation, promotion, or release authority.

If report commit/push authority or required publication capability is unavailable, the Executor returns the exact non-durable terminal result and must not claim that canonical report evidence exists.

A report may remain `state: REPORTED` and `result: NEEDS_REVIEW` after later Architect acceptance because report evidence and review judgment are separate artifacts under the Task Protocol.

Executor classifies discoveries according to the Task Protocol and does not treat CI/Git success as authoritative project PASS unless target authority explicitly designates that evidence.
