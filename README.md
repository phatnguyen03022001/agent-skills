# agent-skills

A deliberately curated library of **exactly 15** reusable agent skills for software engineering across repositories.

This repository is not a target project's source of truth. Target repositories own product intent, code, specifications, architecture decisions, verification rules, deployment policy, and project-specific authority. Shared skills provide reusable decision methods; target-project authority wins on project-specific facts.

## Operating model

```text
User
  ↓
Architect
  ↓
exact repository → project authority → branch → fresh HEAD
  ↓
inspect skill names/descriptions
  ↓
shortlist and load only relevant skill bodies
  ↓
required/recommended skills → deterministic contract
  ↓
fresh Executor chat
  ↓
implementation + evidence report
  ↓
Architect review
```

`architect` is the central router/governance layer. `executor` performs one approved contract. Other skills are selected only when their decision domain is relevant. A project-designated verifier, when one exists, owns authoritative project PASS.

A fresh Executor chat must not mutate until exact `repository.full_name`, target branch, and `base_head` are explicit and verified.

## The 15 skills

| Skill | Type | Decision domain / trigger |
| --- | --- | --- |
| `architect` | core | repository-aware routing, authority, branch/HEAD resolution, skill selection, contracts, handoffs, report review |
| `executor` | core | controlled execution of one approved contract against exact repository state |
| `research` | reasoning | unknown/current/disputed/version-sensitive facts that materially affect an engineering decision |
| `reuse-first` | reasoning | build-vs-reuse decisions involving repository capabilities, standards, platform features, libraries, or upstream implementations |
| `simplicity` | reasoning | proposed abstractions, services, layers, state, configuration, dependencies, automation, or speculative generality |
| `design-review` | review | architecture, interfaces, major refactors, structural boundaries, product-direction alignment, and consequential trade-offs |
| `gap-analysis` | review | missing requirements, states, failure paths, ownership, migration, verification, or other unspecified decisions |
| `adversarial-audit` | review | stale state, retries, concurrency, partial failure, process death, dependency faults, and governance rationalizations |
| `security-review` | specialist | authentication, authorization, secrets, sensitive data, trust boundaries, untrusted input, and security-critical integrations |
| `verification` | engineering | testing/evidence strategy, regression proof, contract/invariant testing, acceptance evidence, confidence before completion |
| `debugging` | engineering | reproducible root-cause analysis for bugs, failing tests, CI failures, regressions, and unexpected behavior |
| `reliability` | engineering | operability through load/failure/retry/recovery, rollout/rollback, observability, and production incidents |
| `optimization` | engineering | measured performance, resource, developer-loop, automation, or cost constraints |
| `github-dev-main-workflow` | workflow | Git/GitHub governance under `dev` integration + `main` stable, including promotion and Actions risk |
| `cloud-run-basics` | domain | Google Cloud Run deployment, configuration, security, scaling, troubleshooting, and platform-specific cost behavior |

These are decision domains, not a checklist that must all run. The library is intentionally flat: `skill-name/SKILL.md`. At 15 skills, a registry, database, deep category tree, coordinator, or package-management layer would add more machinery than discovery value.

## Architect routing

Use progressive disclosure:

```text
task
→ inspect target repository
→ read target authority and intended direction
→ resolve branch + fresh HEAD
→ inspect the 15 names/descriptions only
→ shortlist concrete trigger matches
→ load candidate bodies
→ remove overlap
→ classify required vs recommended
→ contract
→ self-contained handoff
```

Normally activate **2–5 skills** for a task. More than about seven is a decomposition/review signal. Do not select a skill because its name sounds adjacent, because it is popular, or because “it might help.”

`required_skills` are necessary for safe/correct execution and block when unavailable. `recommended_skills` are useful non-blocking guidance. Recommended skills do not silently become required after execution begins.

Architect owns routing and authority, not all engineering judgment. For example, it may route a design to `design-review`, an unknown external behavior to `research`, or a test strategy to `verification`; those domains remain outside Architect.

## Boundary rules

The taxonomy stays coherent by keeping these distinctions explicit:

- `research` resolves unknown facts; `reuse-first` decides whether existing capabilities should replace custom construction.
- `reuse-first` asks **build or adopt**; `simplicity` asks **how little machinery is sufficient**.
- `design-review` judges specified architecture and trade-offs; `gap-analysis` finds what is not specified.
- `design-review` includes relevant product/structure/multi-perspective lenses so those are not fragmented into separate always-on skills.
- `adversarial-audit` pressure-tests faults and policy assumptions; `security-review` models malicious actors and trust boundaries.
- `reliability` designs/operates production failure and recovery behavior; `debugging` finds causes of observed failures.
- `verification` designs evidence; `executor` runs the checks and implementation authorized by the contract.
- `optimization` starts from measured constraints; it does not authorize speculative caching, concurrency, hardware, or infrastructure.
- `cloud-run-basics` owns platform-specific Cloud Run semantics; generic reliability/security/optimization skills are loaded only when those additional lenses are material.

A new skill should replace, merge, or clearly extend this set only when it establishes an independently triggered reusable decision domain. Do not bypass the 15-skill invariant by splitting mechanical subtopics.

## Engineering defaults

### Reuse before build

Inspect the repository first, then native/runtime capabilities, existing frameworks/platforms, standards/protocols, mature libraries, and upstream reference implementations. Reuse must still earn its place on maintenance, security, licensing, complexity, lock-in, runtime/bundle cost, and project constraints.

The rule is **reuse before build**, not **dependency before thinking**.

### Simplicity before machinery

Prefer:

```text
existing solution
→ small change
→ small abstraction
→ larger abstraction
→ new subsystem
```

Move right only when a concrete requirement, invariant, or quality attribute proves the simpler option insufficient. Extra services, layers, state, configuration, dependencies, CI, or automation are costs to justify, not architectural achievements.

### Preserve intended direction

Current implementation is evidence, not automatically the product/system vision. User intent, canonical specs, architecture decisions, design documents, roadmap constraints, and explicit invariants must be considered before local optimization or refactoring. Do not normalize implementation drift into new authority.

### Evidence before confidence

Research distinguishes FACT, INFERENCE, ASSUMPTION, and UNKNOWN. Verification maps acceptance criteria to evidence. Debugging reproduces and narrows before fixing. Optimization measures before changing. Security findings require plausible attack paths. Reliability mechanisms should have exercised recovery paths when feasible.

## Illustrative routing, not fixed bundles

| Scenario | Likely selected skills |
| --- | --- |
| Simple bug fix | `architect`, `debugging`, `verification`, `executor` |
| New feature | `architect`, `reuse-first`, `simplicity`, `verification`, `executor` |
| Major architecture change | `architect`, `research`, `design-review`, `gap-analysis`, `adversarial-audit` |
| Unknown technical problem | `architect`, `research`, `reuse-first` |
| Performance regression | `architect`, `debugging`, `optimization`, `verification`, `executor` |
| Security-sensitive change | `architect`, `security-review`, `adversarial-audit`, `verification`, `executor` |
| Database migration | `architect`, `design-review`, `gap-analysis`, `reliability`, `executor` |
| Cloud deployment | `architect`, `cloud-run-basics`, `reliability`, `github-dev-main-workflow`, `executor` |
| Broken CI | `architect`, `debugging`, `github-dev-main-workflow`, `verification`, `executor` |
| Legacy cleanup | `architect`, `simplicity`, `design-review`, `verification`, `executor` |
| API redesign | `architect`, `design-review`, `gap-analysis`, `verification`, `executor` |
| Third-party integration | `architect`, `research`, `reuse-first`, `security-review`, `executor` |
| Production incident | `architect`, `debugging`, `reliability`, `adversarial-audit`, `executor` |
| Cost optimization | `architect`, `optimization`, `simplicity`, `reliability`, `executor` |
| Pre-implementation design review | `architect`, `design-review`, `gap-analysis`, `adversarial-audit` |

These examples demonstrate selection pressure only. Architect must derive the active set from the actual repository and task rather than hardcoding bundles.

## Skill size and discovery metadata

Descriptions begin with `Use when` and contain trigger conditions, not workflow summaries. The skill body remains authoritative after activation.

Local guidance:

- frequently loaded/core skills: roughly **150–400 words**;
- normal domain/workflow skills: roughly **300–800 words**;
- move heavy examples, reference tables, reusable scripts, or protocol detail outside `SKILL.md` when they materially improve readability;
- keep skill bodies well below the Agent Skills 500-line guidance whenever practical.

## Contracts

`contracts/IMPLEMENTATION_CONTRACT.md` is the Architect-to-Executor protocol. It binds execution to exact target identity, authority, required/recommended skills, restrictive scope, invariants, acceptance criteria, verification, stale-state behavior, and explicit Git capabilities.

`contracts/IMPLEMENTATION_REPORT.md` is the Executor-to-Architect evidence protocol. `CONTRACT_SATISFIED` is evidence of contract compliance, not authoritative project PASS.

The current contract already represents the 15-skill taxonomy without enumerating it: skill selection remains dynamic and contract-specific.

## Two-branch Git model

For repositories adopting this shared model:

- `dev` = integration and normal mutation branch;
- `main` = stable, authoritative branch;
- implementation and delegated agents default to `dev`;
- direct implementation on `main` is forbidden by default;
- promotion `dev -> main` is separate, explicit, verification-gated, and based on refreshed heads;
- stop on unexpected divergence;
- prefer fast-forward semantics when history permits;
- no force-push, history rewrite, unnecessary long-lived branches, or PR ritual by default.

Target-repository governance may be stricter and takes precedence.

## GitHub Actions

This repository keeps one bounded `dev` validation workflow because malformed skill metadata or taxonomy drift would break discovery.

It intentionally uses:

- relevant `push` events to `dev` only;
- one standard Linux job;
- read-only contents permission;
- no matrix, schedule, duplicate PR run, artifacts, cache, external paid service, or automatic rerun;
- concurrency cancellation;
- a short timeout.

The validator enforces exactly 15 discoverable top-level skills, unique names, folder/name equality, `Use when` descriptions, contract structure, internal references, and size warnings.

Because this repository is private, standard GitHub-hosted execution uses included Actions quota when available and may become billable after quota is exhausted. A short run is not proof of `$0`.

## Intentionally outside the 15

Not every good engineering practice deserves another skill. Standalone skills for TDD, property testing, contract testing, observability, incident response, cost review, structural review, vision alignment, multi-perspective review, API design, migration safety, dependency management, naming, cleanup, commits, pushes, or YAML checking are intentionally merged into broader domains or left to target-project/domain tooling.

Also intentionally absent: coordinator service, shared runner/tunnel, automatic Architect → Executor messaging, database-backed registry, automatic main promotion, and paid/larger CI infrastructure.
