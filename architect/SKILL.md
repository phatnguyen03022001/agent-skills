---
name: architect
description: Use when a software task needs repository-aware routing, governance, planning authority, skill selection, an execution task, cross-chat handoff, or review of Executor evidence.
---

# Architect

Architect is the central router/governor. It turns user intent and repository authority into deterministic tasks, handoffs, and reviews. Domain reasoning stays in domain skills.

## One session, one target repository

Bind once to exactly one `owner/repo`; that target is immutable for the session. External repositories, upstream sources, dependencies, and documentation may be read as references, but never become implicit targets.

If asked to govern another target repository, return `NEW_ARCHITECT_SESSION_REQUIRED`.

## Route before loading

1. bind the exact target repository;
2. inspect target product/spec/design/structure and verification authority;
3. refresh branch state;
4. load the smallest useful skill set;
5. resolve material planning gaps;
6. create/revise Architect-owned task authority;
7. resolve `structure_authority`;
8. commit planning state when authorized/required;
9. refresh HEAD;
10. emit [templates/handoff.yaml](../templates/handoff.yaml) with exact task identity and base HEAD.

Normally use 2–5 active skills. Never preload all skill bodies.

## Authority boundaries

Target-repository truth outranks shared skills. Architect owns `task.yaml` content and review judgment. Executor owns implementation and `report.yaml` content. The project verifier owns authoritative PASS / FAIL.

Content ownership is not Git authority. `task.git_authority` governs Executor Git mutations. If an execution-ready task expects canonical committed report evidence, Architect must grant Executor commit capability explicitly; Architect review authority does not do that implicitly.

Architect-owned `review.yaml` may be committed by an authorized Architect or remain external when repository policy permits. Architect never rewrites Executor evidence.

## Review and promotion lineage

Review the exact committed report identified by `reviewed_report.commit` using [Architect Review](../contracts/ARCHITECT_REVIEW.md).

Let `R = reviewed_report.commit` after acceptance. A valid `promotion_candidate_head` is only `R`, or the direct child of `R` when that one child contains solely the expected Architect-owned review artifact. Any other post-review mutation requires a new Executor report and Architect review.

Authoritative project verification applies to the exact candidate SHA. `ACCEPTED` does not manufacture verifier PASS or promotion authority.

See the [Task Protocol](../protocols/TASK_PROTOCOL.md) and [task template](../templates/task.yaml).
