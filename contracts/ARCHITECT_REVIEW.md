# Architect Review

The canonical Architect-owned review shape is [templates/review.yaml](../templates/review.yaml). For canonical task reviews governed by the current forward-looking durable-review semantics, the final governing Architect judgment is persisted in the target repository as `.agent/tasks/<TASK-ID>/review.yaml`. Legacy protocol-v3 history may legitimately lack this artifact; absence in such history is ambiguous and does not prove acceptance, rejection, or lack of review.

This contract owns review-artifact obligations only. Reusable lifecycle, authority/capability, continuation, promotion-lineage, and release semantics—including `PROMOTED_NOT_RELEASED`—are owned by the [Task Protocol](../protocols/TASK_PROTOCOL.md).

## Review ownership and exact report identity

Exactly one current governing Architect owns final review judgment for the active repository binding. Architect reviews Executor evidence; it does not rewrite it.

`reviewed_report.commit` names the exact commit containing the exact `report.yaml` revision being judged. The review context must resolve that commit and content deterministically. Remote-only review requires remote reachability; local-only review requires an explicitly shared trusted checkout/object environment resolving the same object.

Independent reviewer, red-team, verifier, debugger, researcher, or similar work may run in a separate agent/session as Executor-specialized evidence. Advisory evidence remains advisory; a designated verifier owns authoritative exact-SHA PASS/FAIL only when target authority explicitly grants that role. Neither independently owns Architect product/governance acceptance.

Review metadata such as `independence.reviewer_role` or `separate_session_from_executor` records review context but is not independent proof of session identity, tool access, or independent execution. Evidence strength comes from exact report/commit/ref binding and independently resolvable evidence where the task requires it; this contract creates no reviewer authentication or signature mechanism.

## Review artifact obligations

The review checks protocol/task/report identity, execution base, skill rules, scope, structure policy, Git authority/actions, gaps, acceptance evidence, available advisory evidence, and designated-verifier evidence.

The canonical v3 serialized judgment remains `ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`. Before a final canonical judgment governed by the durable-review rule is relied on across sessions or for continuation, promotion, release, or successor reconstruction, Architect publishes the existing `review.yaml` bound to the exact reviewed report commit and report revision. Reasoning may occur before persistence, but it is not durable repository-reconstructible lifecycle evidence until publication.

When repository write capability is materially required to persist that final review, preflight it for the REVIEW phase. If unavailable, fail closed with `CURRENT_PHASE_CAPABILITY_UNAVAILABLE` rather than claiming a durable final review state. This requirement does not retroactively block earlier Executor phases whose required capabilities were available.

## Optional review operational timing

After resolving the exact repository/task/report binding, Architect captures `started_at_utc` from a trustworthy current UTC clock immediately before the first review-specific capability preflight or acceptance-evidence inspection, whichever occurs first, when the current review surface provides such a clock. This boundary measures Architect review processing only; task completion-to-review-start or queue latency is separate lifecycle evidence and must not be represented as review processing time.

When Architect reaches a final canonical judgment (`ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`), it captures `terminal_decision_at_utc` from a trustworthy current UTC clock before publishing `review.yaml`. If trustworthy current UTC was unavailable at either required boundary, timing is unavailable for that review attempt and the entire `operational_timing` block is omitted. Timestamps must not be invented, approximated, reconstructed, partially populated, or derived from Git commit metadata.

When present, `operational_timing` contains exactly `started_at_utc` and `terminal_decision_at_utc`, both captured RFC 3339 UTC timestamps. Elapsed review duration is derived and must not be stored as `elapsed_seconds` or another canonical duration field.

Review timing is non-authoritative operational telemetry. It cannot affect `ACCEPTED`/`REVISION_REQUIRED`/`BLOCKED`, PASS/FAIL, authority, capability, identity, independence, acceptance evidence, promotion readiness, release readiness, or any performance-compliance claim. Reviews without trustworthy timing remain valid, and historical/current protocol-v3 review artifacts require no backfill.

Acceptance does not rewrite Executor report state or itself manufacture verifier evidence, promotion/release authority, or later capability availability.

Tasks governed before the durable-review rule may have only `task.yaml`/`report.yaml` or historical external Architect review. Do not infer a historical judgment from missing `review.yaml` and do not require bulk backfill. A historical report may receive a persisted review later only after the current Architect actually re-resolves and reviews that exact report; the new artifact records current re-review evidence rather than fabricating historical persistence.

When continuation is appropriate, use the [continuation template](../templates/continuation.yaml) with exact accepted evidence and refs. Candidate-lineage, stale-state, phase/action, promotion, and release rules are referenced from the Task Protocol rather than duplicated here.
