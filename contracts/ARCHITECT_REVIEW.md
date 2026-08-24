# Architect Review

The canonical Architect-owned review shape is [templates/review.yaml](../templates/review.yaml). A target repository may commit `review.yaml` or keep Architect review external if its policy permits.

Architect reviews Executor evidence; it does not rewrite it. Review authority is separate from Executor Git authority.

## Exact report identity

`reviewed_report.commit` must name the exact commit containing the exact `report.yaml` revision being judged, and the Architect review context must resolve that commit and report content deterministically. Remote-only review requires the commit to be reachable from the authorized remote Git state. Local-only review is valid only through an explicitly shared trusted checkout/object environment that resolves the same object.

Review checks protocol/task/report identity, execution base, skill rules, scope, structure policy, Git authority/actions, gaps, acceptance evidence, and verifier evidence.

Architect chooses `ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`. `ACCEPTED` is contract acceptance, not authoritative verifier PASS.

## Promotion lineage

Let `R = reviewed_report.commit` for an accepted review. A valid `promotion_candidate_head` is only:

- `R`; or
- the single-parent direct child of `R`, whose only parent is `R`, where that single commit contains only the expected Architect-owned review artifact.

A merge commit or empty child is invalid. Any other post-`R` mutation requires a new Executor report and Architect review. There is no allowance for vague “other intended release mutations.”

Authoritative verification must apply to the exact candidate SHA. If `dev` changes after verification, use `REVERIFY / REVIEW_REQUIRED`. Actual promotion is separate under [github-dev-main-workflow](../github-dev-main-workflow/SKILL.md).
