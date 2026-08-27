# Architect Review

The canonical Architect-owned review shape is [templates/review.yaml](../templates/review.yaml). A target repository may commit `review.yaml` or keep Architect review external if policy permits.

This contract owns review-artifact obligations only. Reusable lifecycle, authority/capability, continuation, promotion-lineage, and release semantics—including `PROMOTED_NOT_RELEASED`—are owned by the [Task Protocol](../protocols/TASK_PROTOCOL.md).

## Review ownership and exact report identity

Exactly one current governing Architect owns final review judgment for the active repository binding. Architect reviews Executor evidence; it does not rewrite it.

`reviewed_report.commit` names the exact commit containing the exact `report.yaml` revision being judged. The review context must resolve that commit and content deterministically. Remote-only review requires remote reachability; local-only review requires an explicitly shared trusted checkout/object environment resolving the same object.

Independent reviewer, red-team, verifier, debugger, researcher, or similar work may run in a separate agent/session as Executor-specialized evidence. Advisory evidence remains advisory; a designated verifier owns authoritative exact-SHA PASS/FAIL only when target authority explicitly grants that role. Neither independently owns Architect product/governance acceptance.

## Review artifact obligations

The review checks protocol/task/report identity, execution base, skill rules, scope, structure policy, Git authority/actions, gaps, acceptance evidence, available advisory evidence, and designated-verifier evidence.

The canonical v3 serialized judgment remains `ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`. Acceptance does not rewrite Executor report state or itself manufacture verifier evidence, promotion/release authority, or later capability availability.

When continuation is appropriate, use the [continuation template](../templates/continuation.yaml) with exact accepted evidence and refs. Candidate-lineage, stale-state, phase/action, promotion, and release rules are referenced from the Task Protocol rather than duplicated here.
