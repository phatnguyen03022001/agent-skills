# Architect Review

The canonical Architect-owned review shape is [templates/review.yaml](../templates/review.yaml). Target repositories should store it as `.agent/tasks/TASK-NNNN/review.yaml` when this protocol is adopted.

Architect reviews Executor evidence; it does not rewrite it.

## Review gate

Review the exact report commit/path and verify:

- supported protocol version and task/report identity;
- authorized execution base and exact task-at-base evidence;
- skill-library revision and required execution skills;
- changed/new files against task scope and structure policy;
- architecture/spec/product/vision drift;
- gap classification and any LOCAL actions;
- Git actions;
- acceptance/check/verifier evidence.

A protocol-version mismatch is not repaired during review; it requires a compatible Architect-owned revision/handoff.

## Outcomes

Architect chooses exactly one:

- `ACCEPTED`: the report proves the approved task is contract-compliant. This is still distinct from project-designated authoritative PASS.
- `REVISION_REQUIRED`: current work/task needs an Architect-owned revised task revision or another bounded action.
- `BLOCKED`: unresolved authority or safety issue prevents acceptance/progression.

Gap dispositions may close a finding as invalid, accept it as a known limitation, revise the current task, or create a follow-up task. Follow-up lineage records the originating `task_id` and `gap_id`.

## Promotion boundary

Review may mark the work eligible for **promotion-candidate capture**, but `review.yaml` does not contain or manufacture the final candidate SHA when the review commit itself may be part of the release.

After all intended `dev` mutations are complete, refresh `dev` and capture `promotion_candidate_head` externally. Required authoritative verification must identify that exact SHA. Architect must not manufacture verifier evidence.

If `dev` changes after verification, promotion requires `REVERIFY / REVIEW_REQUIRED`.

Actual `dev -> main` promotion remains a separate explicitly authorized operation under [github-dev-main-workflow](../github-dev-main-workflow/SKILL.md).
