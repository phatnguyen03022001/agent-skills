# Architect Review

The canonical Architect-owned review shape is [templates/review.yaml](../templates/review.yaml). A target repository may commit `review.yaml` or keep Architect review external if policy permits.

Architect reviews Executor evidence; it does not rewrite it. Review authority is separate from Executor Git authority. Independent review may be performed by a separate agent/session; it is not inherently human-only. Independence requires Architect role/session separation from the Executor plus exact-evidence separation.

## Exact report identity

`reviewed_report.commit` names the exact commit containing the exact `report.yaml` revision being judged, and the review context must resolve that commit and content deterministically. Remote-only review requires remote reachability. Local-only review is valid only through an explicitly shared trusted checkout/object environment resolving the same object.

The canonical review template records independence evidence separately from the Executor report. Architect acceptance never changes the Executor-owned report state merely to mirror review outcome.

Review checks protocol/task/report identity, execution base, skill rules, scope, structure policy, Git authority/actions, gaps, acceptance evidence, and verifier evidence.

Architect chooses `ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`. `ACCEPTED` is contract acceptance, not authoritative verifier PASS, promotion authority, release authority, or proof of later capability availability.

## Promotion lineage

Let `R = reviewed_report.commit` for an accepted review. A valid `promotion_candidate_head` is only:

- `R`; or
- the single-parent direct child of `R`, whose only parent is `R`, where that single commit contains only the expected Architect-owned review artifact.

A merge commit or empty child is invalid. Any other post-`R` mutation requires a new Executor report and Architect review. Authoritative verification applies to the exact candidate SHA. If `dev` changes after verification, use `REVERIFY / REVIEW_REQUIRED`.

## Continuation and release

A valid [continuation template](../templates/continuation.yaml) may carry exact accepted evidence into the next already-authorized phase. It does not create authority. `AUTO_UNTIL_STOP` may dispatch the next independent role/session only while exact authority, identity, and current-phase capability preflight remain valid.

Promotion and release are separate. After an explicit exact-candidate promotion, unavailable or unauthorized release work yields a valid derived `PROMOTED_NOT_RELEASED` state rather than retroactively invalidating promotion. Version tag creation, repository metadata mutation, and release publication each require their own explicit release authority and available capability.
