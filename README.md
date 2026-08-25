# agent-skills

A deliberately curated library of **exactly 15** reusable agent skills plus deterministic contracts, templates, and protocols for software engineering across repositories.

`agent-skills` defines **HOW WE WORK**. A target repository defines **WHAT THE PRODUCT IS** and stores live tasks/evidence.

Supported protocol version is **3**. The lifecycle/continuation hardening is additive and backward-compatible; existing valid expanded v3 artifacts remain valid.

## Main flow

```text
bounded user authorization
→ Architect task + exact handoff
→ Executor implementation + REPORTED evidence
→ independent Architect/session review
→ exact-SHA verification when required
→ explicit promotion
→ PROMOTED_NOT_RELEASED
→ separately authorized release
→ RELEASED + final identity verification
```

`MANUAL` continuation returns control after a bounded phase. `AUTO_UNTIL_STOP` may let an orchestration environment dispatch the next already-authorized independent role/phase without asking the user again. It never merges roles, creates authority, manufactures review/verifier evidence, or treats the absence of a human as approval. No orchestrator is implemented here.

## Identity / ownership cheat sheet

| Identity or result | Meaning | Owner / authority source |
| --- | --- | --- |
| `base_head` | Exact pre-execution task snapshot from the handoff | Architect handoff |
| `final_execution_head` | Last implementation HEAD before the Executor report commit | Executor evidence |
| `reviewed_report.commit` | Exact commit containing the report actually reviewed | Independent Architect review identity |
| `promotion_candidate_head` | Exact accepted-lineage `dev` SHA eligible for verifier/promotion checks | Derived from accepted review lineage |
| authoritative verifier identity/result | Verifier-owned evidence for the exact candidate SHA | Project-designated verifier |
| lifecycle state | Derived conclusion from authoritative artifacts, refs, and evidence | Derived, never a shared role-writable state file |

A report may remain `REPORTED` / `NEEDS_REVIEW` after an external Architect accepts that exact report. Review state is separate evidence.

## Authority, capability, and release

Authority never proves capability availability; capability availability never grants authority. Before the first action of a phase, preflight only that phase's required semantic capabilities. Missing current-phase capability blocks before mutation. Missing later-phase capability does not invalidate an earlier completed phase.

`create_branch`, `commit`, `push`, and `promote_to_main` are independent Git authorities. Release authority is independent again: version tag creation, repository metadata mutation, and release publication must each be explicitly authorized. None is inferred from commit, push, or promotion.

After exact promotion, incomplete or unavailable release work yields the valid derived state `PROMOTED_NOT_RELEASED`. `RELEASED` requires the separately authorized release actions plus final verification.

## Accepted promotion lineage

Let `R = reviewed_report.commit` after independent Architect acceptance. A valid `promotion_candidate_head` is only:

- `R`; or
- the single-parent direct child of `R`, whose only parent is `R`, where that one child contains only the expected Architect-owned review artifact.

A merge commit, empty child, or any other post-`R` mutation requires a new Executor report and Architect review. Authoritative verification applies to the exact candidate SHA. If `dev` changes afterward: `REVERIFY / REVIEW_REQUIRED`.

## Curated skill catalog

<!-- SKILL_CATALOG_START -->
| Skill | Type | Decision domain / trigger |
| --- | --- | --- |
| `architect` | core | repository-bound routing/governance, planning authority, skill selection, tasks, handoffs, report review |
| `executor` | core | controlled execution of one approved task revision against one exact repository/base |
| `research` | reasoning | unknown/current/disputed/version-sensitive facts that materially affect an engineering decision |
| `reuse-first` | reasoning | build-vs-reuse decisions involving repository capabilities, standards, platforms, libraries, or upstream implementations |
| `simplicity` | reasoning | proposed abstractions, services, layers, state, configuration, dependencies, automation, or speculative generality |
| `design-review` | review | proposed or implemented consequential architecture, interfaces, structural integrity, and product-direction alignment |
| `gap-analysis` | review | missing requirements, states, failure paths, ownership, migration, verification, or unspecified decisions |
| `adversarial-audit` | review | stale state, retries, concurrency, partial failure, process death, dependency faults, and governance rationalizations |
| `security-review` | specialist | authentication, authorization, secrets, sensitive data, trust boundaries, untrusted input, and security-critical integrations |
| `verification` | engineering | testing/evidence strategy, regression proof, contract/invariant testing, acceptance evidence, confidence before completion |
| `debugging` | engineering | reproducible root-cause analysis for bugs, failing tests, CI failures, regressions, and unexpected behavior |
| `reliability` | engineering | operability through load/failure/retry/recovery, rollout/rollback, observability, and production incidents |
| `optimization` | engineering | measured performance, resource, developer-loop, automation, or cost constraints |
| `github-dev-main-workflow` | workflow | Git/GitHub governance under `dev` integration + `main` stable, including promotion and Actions risk |
| `cloud-run-basics` | domain | Google Cloud Run deployment, configuration, security, scaling, troubleshooting, and platform-specific cost behavior |
<!-- SKILL_CATALOG_END -->

The validator recursively discovers every `SKILL.md` and accepts only these exact fifteen top-level locations. A hidden or nested sixteenth skill is an error.

## Canonical v3 artifacts

There is one task model, not task-lite/task-compact variants. Reusable shapes are:

- [templates/task.yaml](templates/task.yaml): Architect-owned implementation authority;
- [templates/handoff.yaml](templates/handoff.yaml): exact Architect-to-Executor locator/authorization;
- [templates/report.yaml](templates/report.yaml): Executor-owned evidence;
- [templates/review.yaml](templates/review.yaml): Architect-owned judgment;
- [templates/continuation.yaml](templates/continuation.yaml): small post-review exact-identity continuation envelope;
- [contracts/IMPLEMENTATION_CONTRACT.md](contracts/IMPLEMENTATION_CONTRACT.md);
- [contracts/IMPLEMENTATION_REPORT.md](contracts/IMPLEMENTATION_REPORT.md);
- [contracts/ARCHITECT_REVIEW.md](contracts/ARCHITECT_REVIEW.md);
- [protocols/TASK_PROTOCOL.md](protocols/TASK_PROTOCOL.md).

Protocol-owned unconditional boilerplate can stay in the protocol instead of being recopied into every task. Safety-significant task-specific scope, authority, capabilities, release decisions, structure policy, acceptance criteria, and verification remain explicit.

## Gap and structure policy

`LOCAL` is necessary, in-scope work permitted by current authority. `FOLLOW_UP` is real but unnecessary or unauthorized now. `BLOCKING` requires new/conflicting authority before safe continuation. Discovery never grants authority.

No orphan source files. No speculative scale structure. `structure_authority.status` remains `RESOLVED`, `NOT_APPLICABLE`, or `UNRESOLVED`, owned by Architect.

## Validation and GitHub Actions

The stdlib-only validator checks the exact 15-skill taxonomy, frontmatter/catalog, constrained YAML, canonical task/handoff/report/review/continuation templates, lifecycle/continuation/capability/release semantics, identity consistency, and internal links.

The repository keeps one bounded validation workflow on relevant pushes to `dev`: one standard Linux job, read-only contents permission, short timeout, concurrency cancellation, immutable action pins, validator execution, and stdlib unittests. No extra workflow is required for this protocol hardening.
