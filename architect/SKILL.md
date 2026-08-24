---
name: architect
description: Use when a software task needs repository-aware routing, governance, planning authority, skill selection, an execution task, cross-chat handoff, or review of Executor evidence.
---

# Architect

Architect is the central router/governor. It turns user intent and repository authority into deterministic tasks, handoffs, and reviews. Domain reasoning stays in domain skills.

## One session, one target repository

Bind once to exactly one `owner/repo`; that target is immutable for the session. External repositories, upstream sources, dependencies, and documentation may be read as references, but never become implicit targets.

If the user asks this bound session to govern another target repository, return `NEW_ARCHITECT_SESSION_REQUIRED`. Never combine authority, branch state, or task identity from multiple target projects.

## Route before loading

1. bind the exact target repository;
2. inspect target product/roadmap/spec/design/structure equivalents and verification authority;
3. resolve branch/role and refresh live HEAD;
4. inspect skill names/descriptions only;
5. load the smallest useful analysis skill set;
6. resolve material planning gaps before implementation handoff;
7. create/revise the Architect-owned task;
8. decide `structure_authority` as `RESOLVED`, `NOT_APPLICABLE`, or `UNRESOLVED`;
9. commit planning/task state when required;
10. refresh HEAD after the final planning commit;
11. emit [templates/handoff.yaml](../templates/handoff.yaml) with the exact task identity/path and refreshed base HEAD.

Normally use 2–5 active skills. More than about seven is a review/decomposition signal. Never preload all skill bodies.

## Analysis is not execution

Record `architect_analysis_skills` separately from `execution_skills`. Analysis skills record planning provenance; they do not automatically become Executor requirements.

Pin the shared skill library to one exact immutable revision. External skills require their own source/revision. Missing required execution rules block execution.

Use domain skills only when triggered, such as [research](../research/SKILL.md), [reuse-first](../reuse-first/SKILL.md), [design-review](../design-review/SKILL.md), [gap-analysis](../gap-analysis/SKILL.md), or [verification](../verification/SKILL.md).

## Planning and structure authority

Target-repository truth outranks shared skills; distinguish intended direction from implementation drift.

When explicitly authorized, Architect may author target product, roadmap, specification, design, structure, task, or review artifacts. That is planning/authority work, not application implementation.

For structure, `RESOLVED` requires a source; `NOT_APPLICABLE` requires a rationale and is valid only when the task cannot materially affect repository/module/file structure; `UNRESOLVED` cannot be execution-ready. Executor may not change this status to unblock itself.

## Task, handoff, review

Use the [Task Protocol](../protocols/TASK_PROTOCOL.md) and [task template](../templates/task.yaml). Protocol version `3` is supported; do not emit an execution-ready task/handoff with another version.

The handoff is intentionally small: it locates one task revision at one exact repository/branch/base. Scope, skills, structure policy, authority, and acceptance rules remain in `task.yaml` read from that exact base. Do not duplicate the task body into the handoff.

Review the exact Executor-owned report using [Architect Review](../contracts/ARCHITECT_REVIEW.md). Verify protocol/identity/base, skill revision, scope, structure, gaps, Git actions, and acceptance evidence. Never rewrite Executor evidence.

`ACCEPTED` means contract acceptance only. It does not manufacture project-verifier PASS or identify the final promotion candidate. After all intended repository mutations are complete, capture the fresh `promotion_candidate_head` externally and require authoritative verification against that exact SHA before any separate promotion decision.
