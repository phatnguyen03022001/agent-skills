# TASK-0025 GOV-G Revision-2 Gate Evidence

## Identity and evidence boundary

- Role: `EXECUTOR`; task: `TASK-0025`, revision `2`; phase: `EXECUTION`.
- Repository: `phatnguyen03022001/agent-skills`; integration ref: `dev`.
- Exact handoff base and fresh GitHub `dev`: `6f36dbc5ccaa480c1aca28d1d77587999e302744`.
- Required unchanged stable ref before a future promotion: `main=76f2d3877d1698f91eb5a6117e2301ed49480379`.
- Revision authority: `.agent/tasks/TASK-0025/review.yaml@bf8d8e613e3c1af466fb45c433a472cc28b99cb4`; revision-1 report: `03f6f69794a1791c14bbcdfa916a67a537e699a0`.
- Frozen reusable-governance authority: `phatnguyen03022001/agent-skills@16217bb78a578160efb68afc84acdeff9c36ed38`.

This artifact records only evidence. It adds no classifier, Architect automation, synchronization primitive, registry, or policy semantics. Every executable result below uses an existing validator/model/corpus surface or a test-local Git fixture. Every historical result is reconstructed from immutable GitHub commit, tree, diff, task, report, review, or Actions evidence; it is not inferred from a replay sentence alone.

## Executable compatibility and consequence evidence

| Gate | Result | Actual proof mechanism |
| --- | --- | --- |
| Expanded-v3 and sparse-v3 are one model | PASS | `Task0025StableAdoptionGateTests.test_expanded_and_sparse_v3_use_one_normalized_semantic_model` copies the accepted TASK-0001 fixture, removes optional controls, runs `normalize_task_document`, checks `TASK_NORMALIZATION_DEFAULTS`, and runs the validator. It then validates the expanded restrictive form and its `unlisted_new_files` consequences. |
| Missing authority fails closed; absent local-HOW prescription remains discretionary | PASS | `test_missing_authority_fails_closed_but_missing_how_preserves_discretion` mutates the positive scope authority field and requires validator rejection, then validates the sparse normalized form. No alternate task dialect or validator change is introduced. |
| All governance-eval consequence pairs retain their outcomes | PASS | `test_governance_corpus_pairs_preserve_hand_checked_consequence_outcomes` executes `eval_corpus_errors` and independently checks all eight literal pairs: route/contract, persistence, ownership, dependency, generated/public contract, trust, preference/material HOW, and local/cross-component companion work. Every pair has exactly its literal `ALLOW_LOCAL` over-governance case and `ESCALATE_TO_ARCHITECT` under-governance case. Existing corpus-integrity mutations still reject duplicate IDs, incomplete pairs, unsupported outcomes, malformed fields, pair-count drift, and target-specific leakage. The corpus remains a regression expectation only, never task authority. |
| Existing material-boundary and report/review rules remain frozen | PASS | Existing `test_materiality_scope_structure_gap_and_report_ownership_remain_closed` and the protocol/contract validator suite continue to exercise the current closed fields and report/review schema. This gate does not claim documentary role instructions have become a runtime decision engine. |

## Real Git-state facts, then the frozen consequence contract

`Task0025StableAdoptionGateTests.test_git_state_facts_distinguish_safe_fast_forward_from_local_authority_risks` creates only a temporary bare remote and disposable clones. It executes real Git commands and proves these facts:

| Observed Git fact | Executed fixture evidence | Consequence under the already-frozen Executor contract |
| --- | --- | --- |
| Absent and safely empty are distinct | An absent path has no `.git`; an initialized empty repository has no remote and clean porcelain. | Neither fact supplies repository identity or mutation authority by itself. |
| Cached remote can be stale | A writer advances the bare remote; local `refs/remotes/origin/main` differs from `git ls-remote origin refs/heads/main` before fetch. | Fresh remote resolution is required before use. |
| Clean/behind has an actual fast-forward path | After fetch, porcelain is empty, `HEAD` is an ancestor of `origin/main`, and `git merge --ff-only origin/main` reaches the advertised commit. | This establishes a Git fact only; it is the sole fixture state with safe fast-forward mechanics. |
| Dirty/untracked state is observable before reconciliation | After a further remote advance, the local clone contains `?? operator-owned.txt` while still behind. | Preserve it and fail closed rather than treating the existence of a possible fast-forward as permission. |
| Ahead/diverged state is observable | A local commit after the remote advance makes neither `HEAD` nor `origin/main` an ancestor of the other. | Preserve and do not auto-reconcile. |
| Remote identity mismatch is observable | Changing `origin` to a different bare remote makes its URL differ from the expected remote. | Fail closed; path names cannot repair identity. |
| A temporary checkout is not the designated copy merely because its remote matches | A separate clone has the same remote URL but a different real path. | Designation remains an authority fact, not an inference from remote URL alone. |

The fixture deliberately contains no synchronization implementation. It proves Git facts; the mapping above is the existing Executor contract at `executor/SKILL.md@16217bb78a578160efb68afc84acdeff9c36ed38` and accepted TASK-0024 review, not a new policy surface.

## Architect remote-write and later local reconciliation

This sequence was independently reconstructed from the canonical agent-skills graph and the actual execution preflight, not chat history:

1. `03f6f69794a1791c14bbcdfa916a67a537e699a0` is the revision-1 Executor report. Its direct child `bf8d8e613e3c1af466fb45c433a472cc28b99cb4` is the Architect review authority, and that review's direct child `6f36dbc5ccaa480c1aca28d1d77587999e302744` is the Architect revision-2 task authority.
2. Before this execution's first mutation, the designated local branch was clean in tracked content at `03f6…`, while fresh GitHub resolution returned `dev=6f36…`. `git merge-base --is-ancestor 03f6… 6f36…` succeeded; the reverse check failed.
3. A fresh `git fetch --no-tags origin` followed by `git merge --ff-only origin/dev` reached exactly `6f36…`. The only local differences retained afterward were pre-existing untracked operator state; no reset, stash, clean, deletion, move, overwrite, or adoption occurred.

Therefore an Architect remote review/task-authority write can temporarily put GitHub ahead of a local copy, while the later local preflight must resolve GitHub and establish safe fast-forward/equivalence before local mutation. This is evidence for the existing sequence, not an instant-mirror requirement or sync subsystem.

## Independently reconstructed historical replay

The replay conclusion is checked against the following immutable GitHub facts for `phatnguyen03022001/ilets`, rather than treated as self-proving prose:

- TASK-0044 revision chain is direct: revision 1 `c792761e14c7c34a5f033e1ceb0b69c876f0807c`; revision 2 `7c857adf9a275b12f06d018791617daa54bc8c4d`; revision 3 `f81ea09ec1935c348866769b623d15bf9a6ec916`; revision 4 `ca3a07115f677054f770c790fa2dc7439d2e8f87`.
- GitHub commit diffs show revisions 3 and 4 changed only `.agent/tasks/TASK-0044/task.yaml`. Revision 3's immutable task permits a smallest PM-L03 anchor solely when needed for machine resolvability inside its existing owner, explicitly without semantic ownership or product-meaning change. Revision 4 generalizes that same owner-local non-semantic selector aid for already-bound identities.
- Candidate `13b2577e02050c1f354017389a106da66de0872d` is the direct child of revision-4 authority. Sentinel `6c8bc9552a55a85c62b642e4ff40cdb7d4c080f3` is its direct child and changes only `.github/verification-boundary/candidate`. GitHub Actions run `33684727585` is `completed/success` at that sentinel SHA.
- Revision 5 `04cc4b29246b074f2a33e83d89a665660222e9c1` is a task-only child of the revision-4 report `ac25dd2664103a24a30b0ccbd8e5e6468ba26729`. Its own immutable authority identifies the restrictive allowlist defect and report-ID mapping defect, preserves candidate bytes, and authorizes report correction only. Corrected report `898f4360edf5523c355b98651b2c98dce6866886` is a report-only child. The accepted review resolves at `1a33e0466a2416a7d1afcf71d604de9fdbb3f9a0`.

Result: revision 3 disappears, revision 4 disappears, and revision 5 disappears as a task-revision trigger under the accepted replay. The revision-5 report-lineage correction remains necessary evidence work; public, trust, persisted-data, generated-contract, ownership, and integrity consequences in the candidate remain material and governed. No verifier/stale/new-truth deletion is claimed.

## Independently reconstructed fresh pilots

| Pilot | Exact lineage and changed-boundary reconstruction | Result |
| --- | --- | --- |
| IELTS TASK-0045 | Task/review are revision 1 at accepted review `4b88bbde9558ae50de2c17941677c73fe7c504c8`; review resolves report `439877fcf6874ff11c6e2da8daeaa63bb688bd79`. Candidate `1e5d60003b91367e128a8c5d6cccfd0943b4ea06` is a direct child of base `c6f8f91c8d8b12e4a46f17916ea476e71fce4c5e`. GitHub's exact candidate diff lists 18 existing component/native surfaces, including one Listening fixture and its local verification companions; the immutable task forbids public-contract, persistence-meaning, trust, provider/storage, Assessment/Evidence, Progression/Planner, dependency, and cross-component changes. | Revision-1 accepted evidence: local selectors, SQL/sqlc, fixture placement, generated traces, and companions did not require task revision; material boundaries remained closed. |
| SF TASK-0008 | Task/review are revision 1 at accepted review `dd518fa0ae693f57befcedf341410d4cf28026d8`; review resolves report `fb67f45f59834b7848a7a76acaa44084541b960f`. Candidate `df595fbbb61fa01016b7fe965b4f22ebb430f978` is a direct child of base `83bcf6ae33abf8740ce66077f92fd523706354b5`; GitHub's exact candidate diff contains only `docs/change-authorization-lesson.md`. The task and report preserve the existing durable taxonomy, decision authority, main-only, zero-runtime, dependency-free boundary. | Revision-1 accepted control: one contextual lesson stayed local without a new owner, taxonomy, runtime, registry, workflow, or live decision-semantic change. |

Neither pilot is retroactively reinterpreted: each conclusion comes from its accepted review, report-bound candidate parent, and exact GitHub diff.

## Ownership boundary reconstruction

- The exact candidate diff is restricted to this task-local evidence artifact and the existing regression companion; neither is a reusable operator-path or presentation rule.
- Accepted architect-profile TASK-0015 review `71921cde6228c21b4d2e3e6509e685d82981dc9c` resolves an operator-profile candidate changing only `ARCHITECT_PROFILE.md` and `ARCHITECT_CALIBRATION.md`. Its task makes operator working-copy conventions and presentation/language preferences profile-owned, explicitly prohibiting leakage into agent-skills.
- Read-only `phatnguyen03022001/agent-runtime@9d5320d5afbc9aff20834801bfd6695b27cf2a0e` describes a local execution/tunnel surface with no registry, sync primitive, state engine, scheduler, daemon, or workflow authority. It is capability only.

No external repository was mutated. Generic agent-skills semantic owners remain frozen.

## Candidate gate

The executable and independent-evidence rows above are PASS for the exact base. A future implementation candidate may be created only from this base and only after the focused regressions, full validator, full unittest suite, and whitespace check are fresh PASS. Promotion remains prohibited until the exact candidate is on `dev`, the existing workflow completes successfully with matching `head_sha`, fresh refs still show the required old `main`, and ancestry proves a non-force fast-forward. The report-only child is a later, separate action and is never the promotion candidate.
