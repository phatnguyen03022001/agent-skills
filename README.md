# agent-skills

A deliberately curated library of **exactly 15** reusable agent skills plus deterministic contracts, templates, and protocols for software engineering across repositories.

`agent-skills` defines **HOW WE WORK**. A target repository defines **WHAT THE PRODUCT IS** and stores live tasks/evidence. Supported protocol version is **3**; existing valid expanded v3 artifacts remain valid.

## Governance ownership

[Task Protocol](protocols/TASK_PROTOCOL.md) is the semantic owner for reusable cross-role task-governance semantics. Architect and Executor skills own role-local procedure and safety boundaries; contracts own artifact-specific obligations; templates are example/default shapes; the validator mechanically enforces supported structure and compatibility. This README is discovery and navigation, not a second normative protocol.

The normal flow is planning and exact handoff → restrictive execution and Executor report → Architect review → exact-SHA verification when required → explicit promotion → separately authorized release. Binding, lifecycle, authority/capability separation, continuation, promotion lineage, and release semantics are defined only by the Task Protocol.

`PROGRAM` remains presentation only for ordered repository-local tasks. It may be rendered from the optional machine-readable [generated program template](templates/program.generated.json), which is derived planning data with authority `NONE`: it records immutable synthesis identities, validated coverage/dependencies, and Architect judgment, but never replaces repository-local task authority or authorizes execution, lifecycle mutation, review, verification, promotion, or release. See the Task Protocol for the governing semantics.

## Operator-facing presentation

TASK LAUNCH is operator-facing presentation only. It is non-authoritative, is not persisted as task state, and remains separate from `PROMPT TO COPY`.

`PROMPT TO COPY` is a compact authority locator to the canonical repository/task/base/phase authority, not duplicated authority. Generic `agent-skills` does not prescribe TASK LAUNCH field names, ordering, language, executor menus, model/effort display, or other operator-profile presentation choices.

## Maintenance and frozen taxonomy

Mature governance may correctly return NO CHANGE REQUIRED when no material reproduced problem exists. Corrective maintenance uses the smallest safe change. The exact 15-skill taxonomy remains closed by default; admission reasoning is owned by [simplicity](simplicity/SKILL.md), while this README keeps the discovery catalog unchanged.

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
| `github-workflow` | workflow | target-authoritative Git/GitHub topology, promotion, and Actions risk without inventing branches |
| `cloud-run-basics` | domain | Google Cloud Run deployment, configuration, security, scaling, troubleshooting, and platform-specific cost behavior |
<!-- SKILL_CATALOG_END -->

The validator recursively discovers every `SKILL.md` and accepts only these exact fifteen top-level locations. A hidden or nested sixteenth skill is an error.

## Canonical v3 artifacts

There is one task model, not task-lite/task-compact variants. Navigation:

- [templates/task.yaml](templates/task.yaml): Architect-owned implementation-authority shape;
- [templates/handoff.yaml](templates/handoff.yaml): exact Architect-to-Executor locator/authorization shape;
- [templates/report.yaml](templates/report.yaml): Executor-owned evidence shape;
- [templates/review.yaml](templates/review.yaml): Architect-owned judgment shape;
- [templates/continuation.yaml](templates/continuation.yaml): post-review exact-identity continuation shape;
- [templates/program.generated.json](templates/program.generated.json): optional derived generated-planning snapshot with authority `NONE`, never task/lifecycle authority;
- [contracts/IMPLEMENTATION_CONTRACT.md](contracts/IMPLEMENTATION_CONTRACT.md): task artifact obligations;
- [contracts/IMPLEMENTATION_REPORT.md](contracts/IMPLEMENTATION_REPORT.md): report artifact obligations;
- [contracts/ARCHITECT_REVIEW.md](contracts/ARCHITECT_REVIEW.md): review artifact obligations;
- [protocols/TASK_PROTOCOL.md](protocols/TASK_PROTOCOL.md): reusable cross-role semantic authority.

## Validation

The stdlib-only validator checks the exact taxonomy, frontmatter/catalog, constrained YAML, canonical templates, generated-program JSON shape/graph/coverage invariants, protocol-v3 compatibility, required doctrine tokens, and internal links. The repository keeps one bounded validation workflow on relevant pushes to `dev`; workflow policy is owned by [github-workflow](github-workflow/SKILL.md).
