# agent-skills

A deliberately curated library of **exactly 15** reusable agent skills plus deterministic contracts, templates, and protocols for software engineering across repositories.

`agent-skills` defines **HOW WE WORK**. A target repository defines **WHAT THE PRODUCT IS**: product intent, roadmap, specifications, design, structure, source code, deployment policy, and project-specific verification authority. Live project tasks belong to the target repository; reusable methods and protocol shapes belong here.

## Main flow

```text
User
→ Architect
→ Task + Handoff
→ Executor
→ Report
→ Architect Review
→ Exact-SHA Verification
→ Explicit Promotion
→ main
```

A discovered gap may return Executor → Architect. The reusable flow is intentionally manual-capable; it does not require a coordinator, queue, database, registry, shared service, or automatic cross-session messaging.

Supported protocol version is **3**. Unsupported versions fail closed and are never silently upgraded.

## Ownership and authority

Architect owns:

- `task.yaml` content and task revisions;
- Architect review judgment, normally represented by `review.yaml` when repository policy stores it.

Executor owns:

- the implementation authorized by the exact task and handoff;
- `report.yaml` content and the evidence it records.

The project-designated verifier owns authoritative PASS / FAIL for the exact candidate SHA. Architect acceptance, Executor evidence, CI status, verifier PASS, promotion authorization, and actual `main` mutation are separate signals.

Content ownership does not automatically grant Git commit authority. `task.git_authority` governs Executor Git mutations. Canonical committed report evidence therefore requires Executor commit capability when a task is execution-ready. Architect review authority is separate from Executor Git authority, and an Architect-owned `review.yaml` may remain external when target-repository policy permits.

`reviewed_report.commit` must be resolvable by the Architect review context; remote-only handoff requires that commit to be reachable from the authorized remote Git state, while an explicitly shared trusted checkout may support local-only review.

## Four distinct SHA identities

These values must not be collapsed into one convenient but incorrect “current SHA”:

1. `base_head`: the exact pre-execution task snapshot named by the handoff.
2. `final_execution_head`: implementation HEAD before the Executor-owned report artifact is committed.
3. `reviewed_report.commit`: the exact commit containing the report Architect actually reviewed.
4. `promotion_candidate_head`: the exact `dev` SHA eligible for authoritative verification and a later explicit promotion decision.

After Architect accepts `R = reviewed_report.commit`, valid promotion lineage is only:

- `promotion_candidate_head == R`; or
- `promotion_candidate_head` is the single-parent direct child of `R`, its only parent is `R`, and that one child commit contains only the expected Architect-owned review artifact.

Any other mutation after `R` invalidates the accepted lineage and requires a new report plus Architect review. That includes implementation, unrelated documentation, cleanup, dependencies, another task, or a second post-review commit.

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

The validator recursively discovers every `SKILL.md` and accepts only these exact fifteen top-level locations. A hidden or nested sixteenth skill is an error, not a cute loophole.

## Task artifacts

Target repositories adopting the protocol normally keep live artifacts under:

```text
.agent/tasks/TASK-0001/
  task.yaml
  report.yaml
  review.yaml
```

Reusable shapes live here:

- [templates/task.yaml](templates/task.yaml): Architect-owned implementation authority;
- [templates/handoff.yaml](templates/handoff.yaml): Architect-to-Executor locator/authorization;
- [templates/report.yaml](templates/report.yaml): Executor-owned evidence;
- [templates/review.yaml](templates/review.yaml): Architect-owned judgment;
- [contracts/IMPLEMENTATION_CONTRACT.md](contracts/IMPLEMENTATION_CONTRACT.md): task semantics;
- [contracts/IMPLEMENTATION_REPORT.md](contracts/IMPLEMENTATION_REPORT.md): report semantics;
- [contracts/ARCHITECT_REVIEW.md](contracts/ARCHITECT_REVIEW.md): review semantics.

The complete reusable protocol is [protocols/TASK_PROTOCOL.md](protocols/TASK_PROTOCOL.md).

## Gap policy

`LOCAL`: necessary for current acceptance criteria, fully inside authority, and allowed by task policy. Executor may fix it.

`FOLLOW_UP`: real but not needed or not authorized for the current task. Record it; do not fix it.

`BLOCKING`: safe continuation needs missing or conflicting Architect authority. Stop and return evidence.

Discovery never grants authority.

## Scope and structure discipline

Task approval never implies unrelated cleanup, adjacent fixes, speculative features, undocumented scope expansion, architecture/spec/public-contract drift, unauthorized dependencies, structural reorganization, or “while I'm here” refactors.

`structure_authority.status` is `RESOLVED`, `NOT_APPLICABLE`, or `UNRESOLVED`. Architect owns that decision; Executor may not change it to unblock execution. Every new source file needs a real existing or explicitly authorized ownership boundary. No orphan source files and no speculative scale structure are protocol invariants.

## Exact-SHA verification and promotion

For repositories using the two-branch model:

- `dev` is integration and normal mutation;
- `main` is stable authority;
- promotion is separate from implementation and review;
- direct implementation on `main`, force-push, and history rewrite are forbidden by default.

Authoritative verification applies to the exact `promotion_candidate_head`. If `dev` changes afterward, prior evidence is stale: `REVERIFY / REVIEW_REQUIRED`.

A promotion candidate is valid after Architect accepts `reviewed_report.commit = R` only when it is `R` itself or the single-parent direct child of `R`, with only parent `R`, containing only the expected Architect-owned review artifact. No vague “other intended release mutations” are allowed between accepted report lineage and candidate capture.

## Validation and GitHub Actions

The stdlib-only validator checks the curated skill locations and frontmatter, README catalog, constrained YAML structure, canonical templates, protocol semantics, and internal Markdown links. Its YAML parser supports only the structures used by these templates; it is intentionally not a general YAML parser.

The repository keeps one bounded validation workflow on relevant pushes to `dev`: one standard Linux job, read-only contents permission, short timeout, concurrency cancellation, immutable action pins, validator execution, and stdlib unittests. There is no manual dispatch, schedule, duplicate PR workflow, matrix, artifact upload, cache, automatic rerun, or paid external service.
