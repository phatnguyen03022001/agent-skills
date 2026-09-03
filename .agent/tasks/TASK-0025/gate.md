# TASK-0025 GOV-G Gate Evidence

## Gate identity

- Role: `EXECUTOR`
- Task: `TASK-0025`, revision `1`, state `APPROVED`
- Phase: `EXECUTION`
- Repository: `phatnguyen03022001/agent-skills`
- Target branch: `dev` (`integration`)
- Exact handoff base: `1ccad2229198e82759fd263ebd71c48c2600280b`
- Canonical task: `.agent/tasks/TASK-0025/task.yaml@1ccad2229198e82759fd263ebd71c48c2600280b`
- Canonical task blob: `c3da6a4d52d48d54dd7b7e0029cc6dbdcc4a7011`
- Pinned skill-library authority: `16217bb78a578160efb68afc84acdeff9c36ed38`
- Stable main required before promotion: `76f2d3877d1698f91eb5a6117e2301ed49480379`

The candidate is the single implementation commit created from the exact handoff base containing this bounded gate artifact and the existing regression-companion additions. Its exact GitHub-resolved SHA is recorded by the canonical `report.yaml` after publication; the report child is never the promotion candidate.

## Authority and capability preflight

All authority below was resolved before mutation and rechecked against fresh GitHub refs immediately before candidate creation:

- Accepted TASK-0024 closure: `.agent/tasks/TASK-0024/review.yaml@16217bb78a578160efb68afc84acdeff9c36ed38`; reviewed report `2c2c72bb491b097f45c34ead8c429c2428b87b9b`; review blob `7983a8a26d721c66864953494bfaf567ec781884`.
- GOV-A through GOV-E accepted evidence: `.agent/tasks/TASK-0019/review.yaml` through `.agent/tasks/TASK-0023/review.yaml`, each resolved at `16217bb78a578160efb68afc84acdeff9c36ed38`.
- GOV-F accepted operator-profile authority: `phatnguyen03022001/architect-profile` review commit `71921cde6228c21b4d2e3e6509e685d82981dc9c`.
- Fresh IELTS pilot: `phatnguyen03022001/ilets` TASK-0045 accepted review commit `4b88bbde9558ae50de2c17941677c73fe7c504c8`.
- Fresh SF pilot: `phatnguyen03022001/SF` TASK-0008 accepted review commit `dd518fa0ae693f57befcedf341410d4cf28026d8`.
- Historical replay: `.agent/tasks/TASK-0023/replay.md@1ccad2229198e82759fd263ebd71c48c2600280b`.
- Existing candidate verifier: `.github/workflows/validate-skill-library.yml@1ccad2229198e82759fd263ebd71c48c2600280b`, blob `1f770bf9ddefe9ade8454e8be594e71fb96f42c0`.
- Required semantic capabilities were available: exact remote-ref read, repository content read/write, native repository execution, and GitHub Actions read. Review/promotion write authority is task-authorized for the later phases only.

## GitHub-first local binding

- Fresh GitHub refs before candidate creation were `dev=1ccad2229198e82759fd263ebd71c48c2600280b` and `main=76f2d3877d1698f91eb5a6117e2301ed49480379`.
- The designated local repository is `/Users/tienphat/Developer/agent-skills`, branch `dev`, with `origin` fetch/push URL `https://github.com/phatnguyen03022001/agent-skills.git`.
- The local copy was initially behind GitHub at `2c2c72bb491b097f45c34ead8c429c2428b87b9b`; `git fetch --no-tags origin dev main` followed by `git merge --ff-only origin/dev` reconciled it to the exact base without reset, stash, cleanup, overwrite, or adoption of local work.
- The fast-forward brought only the canonical TASK-0024 review and TASK-0025 task-authority files. Tracked local state was clean; operator-owned untracked `.DS_Store` and `.codex/` were preserved.
- Path names were not treated as authority. The local owner/repo binding and exact branch/base were proven from Git configuration, GitHub metadata, and the fresh refs.

## Adversarial evidence

| Case | Result | Evidence |
| --- | --- | --- |
| Expanded v3 compatibility | PASS | Existing accepted TASK-0001 expanded controls remain restrictive after normalization; the new companion regression preserves `expected_files_are_restrictive=true`, `unlisted_new_files.allowed=false`, and `max=0`. |
| Sparse v3 normalization | PASS | The same TASK-0001 fixture with optional implementation controls omitted normalizes through `TASK_NORMALIZATION_DEFAULTS`; validator acceptance remains unchanged and no second dialect is introduced. |
| Authority versus HOW prescription | PASS | Removing positive `scope.allowed_existing_files_or_components` fails validation; omitting only implementation-prescription controls remains valid and grants bounded Executor discretion. |
| Consequence-based ownership | PASS | Protocol, contracts, Architect, and Executor evidence retains Executor-local HOW for unchanged consequences, while trust, public/shared contract, data, ownership, durability/persistence, dependency, irreversibility, and architecture consequences remain Architect-governed. |
| `LOCAL` / `FOLLOW_UP` / `BLOCKING` | PASS | Existing protocol and companion regressions retain the necessary-for-acceptance, boundary, determinism, and missing/conflicting-authority consequences; discovery never becomes authorization. |
| Scope and structure materiality | PASS | Semantic/component scope remains the default; internal files/modules are local only inside an authorized component; new top-level ownership, component/package/service boundaries, shared abstractions, cross-component moves, and public/shared contracts remain material. |
| Preference-only HOW | PASS | Architect evidence keeps preference-only revision out of authority and rejects local HOW only for material consequence or contract/risk violation. |
| Report/review ownership | PASS | Executor report content remains Executor-owned; Architect review remains separate and does not rewrite the report. |
| TASK-0044 historical replay | PASS | The pinned replay remains truthful: revisions 3 and 4 disappear, revision 5 disappears as a task revision, and there is no verifier/stale/new-truth deletion claim; public/trust/data/integrity consequences remain governed. |
| Fresh one-revision pilots | PASS | IELTS TASK-0045 and SF TASK-0008 resolve to the exact accepted external review commits above and remain revision-1 accepted pilot evidence, not retrospective redesign targets. |
| GitHub-first local matrix | PASS | Absent/empty, clean/behind, dirty/ahead/unknown, identity mismatch, stale remote, temporary/reference checkout, remote-only, and post-publication reconciliation retain the accepted fail-closed consequences. |
| Architect remote-only mutation | PASS | A remote-only review/task-authority write may leave a local copy temporarily behind; any later local mutation must fresh-resolve GitHub and safely reconcile before using it. No instant mirror, daemon, watcher, registry, state database, sync service, or lifecycle was added. |
| Ownership boundary | PASS | No external repository was mutated. Generic agent-skills remains free of operator-specific paths/presentation/runtime preferences; those remain architect-profile context, while Agent Runtime remains an optional execution capability. |

## Verification before publication

- Focused stable-adoption regressions: `python3 -m unittest scripts.test_validate_skill_library.Task0025StableAdoptionGateTests` — `7/7 PASS`.
- Full validator: `python3 scripts/validate_skill_library.py` — exit `0`; only the pre-existing word-count warnings remain.
- Full unittest suite: `python3 -m unittest scripts/test_validate_skill_library.py` — `97/97 PASS`.
- Whitespace check: `git diff --check` — exit `0`.
- The reusable governance files, validator semantics, workflow, README, templates, external repositories, and operator state were not modified for this gate.

## Decision

- Bounded local GOV-G evidence: `PASS`.
- Semantic correction required: `NO`.
- Unexpected authority gap: `NO`.
- Stable promotion: permitted only after the exact candidate is pushed to `dev`, the existing Validate workflow reports success for that exact candidate SHA, fresh refs still prove the required old `main`, and the non-force ancestry check passes.
- Report publication: separately authorized only after promotion; report-only child on `dev`, never `main`.
- Terminal result: `NEEDS_REVIEW` after the exact post-promotion report/local-reconciliation checks.
