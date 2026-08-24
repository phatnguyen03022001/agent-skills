# agent-skills

A deliberately curated library of **exactly 15** reusable agent skills plus deterministic contracts, templates, and protocols for software engineering across repositories.

`agent-skills` defines **HOW WE WORK**. A target repository defines **WHAT THAT PRODUCT IS**: product intent, roadmap, specifications, design, structure, source code, deployment policy, and project-specific verification authority.

## Operating protocol

```text
USER
  ↓
ARCHITECT (one session = one target repository)
  ↓
project authority + vision + structure
  ↓
progressive skill discovery
  ↓
planning/specification when required and authorized
  ↓
Architect-owned task
  ↓
post-planning fresh HEAD + canonical handoff
  ↓
EXECUTOR (one session = one task = one repository)
  ↓
scoped implementation
  ↓
Executor-owned report + discovered gaps
  ↓
ARCHITECT
  ↓
Architect-owned review / revised task / follow-up task
  ↓
separate exact-SHA verification + promotion decision
```

The complete reusable semantics are in [protocols/TASK_PROTOCOL.md](protocols/TASK_PROTOCOL.md). The protocol works manually through copy/paste; it does not depend on a coordinator, service, database, queue, registry, or automatic cross-chat messaging.

Supported protocol version is **3**. Unsupported versions fail closed and are never silently upgraded.

## Core session invariants

An Architect session binds once to exactly one immutable target repository. It may inspect other repositories only as read-only references. Asking that session to govern a second execution target requires `NEW_ARCHITECT_SESSION_REQUIRED`.

An Executor session binds to exactly one approved task revision, one target repository, and one authorized execution base. It does not switch projects, execute unrelated tasks, reinterpret architecture, or expand scope because neighboring work is visible.

Target-repository authority always wins on project-specific facts.

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

The validator treats this exact set as the curated taxonomy. Removing one skill and substituting an unrelated skill while keeping the count at 15 must fail validation.

## Progressive disclosure and skill determinism

Architect discovers skills by metadata first:

`task → target authority → names/descriptions → shortlist → candidate bodies → remove overlap → planning provenance + execution skill set`

Normally activate **2–5 skills**. More than about seven is a decomposition/review signal. Never preload all 15 bodies.

Planning and execution skills are separate:

- `architect_analysis_skills` record methods used to research/design/specify the task;
- required `execution_skills` must be resolved by Executor;
- recommended execution skills are non-blocking and cannot expand scope.

Tasks pin the shared library once:

```yaml
skill_library:
  repository: phatnguyen03022001/agent-skills
  revision: "<exact immutable commit SHA>"
```

External skills must carry their own immutable source/revision. Executor must not silently use a newer ruleset.

## Target-repository task storage

Live tasks are project state and belong in each target repository:

```text
.agent/tasks/
  TASK-0001/
    task.yaml
    report.yaml
    review.yaml
```

At current scale, that directory is the task list. Do not add task databases, registries, search services, or generated indexes without observed scale evidence.

Reusable shapes in this repository:

- [templates/task.yaml](templates/task.yaml): Architect-owned task/contract;
- [templates/handoff.yaml](templates/handoff.yaml): small Architect-to-Executor execution authorization/locator;
- [templates/report.yaml](templates/report.yaml): Executor-owned evidence;
- [templates/review.yaml](templates/review.yaml): Architect-owned review;
- [contracts/IMPLEMENTATION_CONTRACT.md](contracts/IMPLEMENTATION_CONTRACT.md): task semantics;
- [contracts/IMPLEMENTATION_REPORT.md](contracts/IMPLEMENTATION_REPORT.md): report semantics;
- [contracts/ARCHITECT_REVIEW.md](contracts/ARCHITECT_REVIEW.md): review semantics.

One role must not silently rewrite another role's authority/evidence.

## Base HEAD and authority deduplication

A committed `task.yaml` does **not** write the SHA of the commit containing itself.

`commit final planning/task state → refresh target branch → capture exact HEAD H → emit canonical handoff with base_head=H`

The handoff contains only protocol/type, task identity/path, repository/branch, and exact base. Executor verifies live HEAD equals `H` and reads the task from `H`. Scope, skill rules, structure policy, authority sources, and acceptance criteria are not duplicated into the handoff.

Likewise, `report.yaml.final_execution_head` means the implementation HEAD before the report artifact commit. Architect identifies the exact report commit externally when reviewing it.

## Structure authority

Architect classifies structure applicability in the task:

- `RESOLVED`: a canonical source is required;
- `NOT_APPLICABLE`: a rationale is required and the task cannot materially affect repository/module/file structure;
- `UNRESOLVED`: execution is not ready.

A README typo may legitimately be `NOT_APPLICABLE`. Adding source files, moving modules, changing dependency boundaries, or reorganizing structure may not.

Executor cannot change this status to unblock itself. No-orphan-file, ownership/naming, unauthorized-structure, and no-speculative-scale rules remain in force whenever relevant.

## Always-on scope and structure governance

Noise control is protocol, not an optional skill. Tasks forbid unrelated cleanup, adjacent fixes, speculative features, undocumented scope expansion, architecture/spec/public-contract changes, unauthorized dependency changes, structural reorganization, and “while I'm here” refactors.

Each target repository should have one canonical structure authority when structure matters, whether an existing design/instructions document or an explicitly authorized project-specific structure artifact. Do not force a universal filename or layout.

Feature/domain/component ownership is the default principle when compatible with the target project. Go, Python, TypeScript, and other ecosystems may express that ownership differently.

Every new source file must belong to an existing or explicitly authorized feature/domain/component/layer/infrastructure responsibility. Generic `utils`, `helpers`, `common`, `misc`, or `shared` areas require real cross-domain ownership and project-authority justification.

Do not add new layers, factories, registries, plugin systems, extension points, services, queues, caches, shared modules, top-level directories, or scaling infrastructure for hypothetical future needs.

Prefer:

`existing solution → localized change → small local abstraction → larger abstraction → subsystem`

## Gap policy

Executor classifies discoveries as:

- `LOCAL`: necessary for current acceptance criteria and entirely within approved authority; may be fixed when task policy permits;
- `FOLLOW_UP`: real but unnecessary/outside current authorization; report, do not fix;
- `BLOCKING`: safe/correct continuation requires an Architect decision; stop.

A discovery never grants scope. Follow-up tasks preserve originating `task_id` and `gap_id`.

## Project product/spec/design authority

Canonical project artifacts use whatever names and locations the target repository recognizes. Shared skills teach reusable reasoning; they do not contain arbitrary project vision.

Architect may author product, roadmap, specification, design, structure, task, and review artifacts when explicitly authorized. Executor owns authorized implementation, implementation-scoped tests/migrations/configuration, and execution evidence. The project-designated verifier owns authoritative PASS/FAIL.

The curated 15 stays unchanged. Separate `product-planning`, `spec-writing`, or generic `documentation` skills would substantially overlap Architect planning authority plus `research`, `gap-analysis`, and `design-review`.

## Git and promotion identity model

For repositories adopting the shared two-branch model:

- `dev` = integration and normal mutation;
- `main` = stable authority;
- delegated/normal implementation defaults to `dev`;
- direct implementation on `main` is forbidden by default;
- no force push, history rewrite, unnecessary branch/PR ritual.

Promotion identities are deliberately distinct:

```text
planning commit
→ handoff base_head
→ implementation commit(s)
→ report final_execution_head
→ report commit
→ Architect review
→ review commit if required
→ refresh dev
→ promotion_candidate_head
→ authoritative verification of EXACT promotion_candidate_head
→ no further dev mutation
→ separate promotion of EXACT verified SHA
```

If `dev` changes after candidate verification, prior verification is stale: `REVERIFY / REVIEW_REQUIRED`. Architect `ACCEPTED`, CI green, and verifier PASS remain separate signals.

Branch protection is a separate GitHub-enforced governance decision. Written protocol is procedural enforcement; GitHub branch protection/rulesets are platform enforcement. This repository does not silently change branch-protection settings as part of protocol edits.

## GitHub Actions

The repository keeps one bounded `dev` validation workflow:

- relevant `push` to `dev` only;
- one standard Linux job;
- read-only contents permission;
- no matrix, PR duplicate, schedule, artifacts, cache, external paid service, or automatic rerun;
- concurrency cancellation and a short timeout;
- `actions/checkout` pinned to an immutable full commit SHA.

This private repository consumes the owner's included GitHub Actions quota for standard hosted runners when available and can become billable after that quota is exhausted. A short run is not proof of `$0`.

## Skill and protocol validation

The local validator enforces the curated set, unique folder/name identity, lowercase/hyphen naming, Agent Skills `name <= 64`, `Use when` descriptions, description length, internal Markdown links, README catalog sync, supported protocol version, and structure-aware paths/types for the canonical task/handoff/report/review templates.

The YAML validation is intentionally constrained and stdlib-only. It rejects duplicate mapping keys and invalid indentation for this protocol subset; it is not a general YAML implementation.

Core/frequently loaded skills should stay concise. Move heavy reference material outside `SKILL.md` rather than building god skills.

## Deliberately absent

No coordinator, shared runner/tunnel, task database, automatic Architect→Executor messaging, automatic main promotion, paid/larger CI infrastructure, feature skill, noise-control skill, file-naming skill, or task-management skill is added here. Those are either protocol invariants, target-project authority, or deferred infrastructure requiring evidence.
