# ielts-agents

`ielts-agents` contains role definitions and shared handoff contracts for the IELTS Architect / Executor operating model.

This repository is intentionally small. It does not contain IELTS application code, tunnel code, an executor backend, a coordinator server, CI/CD, or runtime dependencies.

## Roles

### IELTS Architect

The Architect is the planning, architecture, review, and orchestration authority for IELTS engineering tasks. It turns user intent and authoritative project context into deterministic implementation contracts for an Executor.

The Architect decides whether an Executor report satisfies the approved contract. It can accept contract compliance, reject the result, or require revision. It must use verification backends when appropriate and must never declare implementation success from reasoning alone.

### IELTS Executor

The Executor implements an approved implementation contract exactly within its authorized scope. It confirms the target repository, branch, base HEAD, and working state before changing anything. It makes only the required changes, preserves listed invariants, runs the required checks, and reports the result.

The Executor does not reinterpret objectives, make undelegated architectural decisions, weaken acceptance criteria, silently expand scope, or claim authoritative project success.

## Why role separation exists

Role separation keeps planning authority separate from execution authority. This prevents silent scope expansion, architecture drift, and after-the-fact specification changes. It also gives every implementation a reviewable record: what was approved, what changed, how it was checked, and what still needs review.

## Contract-based handoff

The Architect hands work to the Executor through `contracts/IMPLEMENTATION_CONTRACT.md`. The contract records the objective, authority sources, required changes, preserved invariants, acceptance criteria, forbidden changes, verification requirements, unresolved decisions, stale-contract behavior, and whether execution is ready.

The Executor reports back through `contracts/IMPLEMENTATION_REPORT.md`. The report records the base and final HEADs, changed files, checks run, verification results, deviations, unresolved items, and a result value.

## Authority model

Executor completion means the Executor reports the state of its assigned contract only. `CONTRACT_SATISFIED` means the Executor believes the authorized work was completed against the exact approved base with required Executor checks run and no material unapproved deviations. It is not authoritative project PASS.

Architect review means the Architect decides whether the implementation matches the approved contract. The Architect may accept contract compliance, request revision, reject the result, or issue a revised contract. Architect review does not manufacture authoritative project PASS.

Authoritative verification belongs to the target IELTS project repository and its approved verification mechanisms. When `@ielts-tunnel` or another project-defined backend is required, that backend provides the authoritative verification signal.

## Relationship to the IELTS application repository

The IELTS application repository remains the authoritative home for application code, canonical project documents, specifications, design files, tests, and runtime behavior.

`ielts-agents` does not replace or modify that repository. Architect and Executor roles must inspect and respect the authoritative IELTS application repository when a task requires it, but this repository only defines role behavior and shared contracts.

## Relationship to `@ielts-tunnel`

`@ielts-tunnel` remains the sync and verification backend for the IELTS system. It is not part of this repository.

Architect and Executor roles must not duplicate tunnel functionality. They may rely on tunnel-backed sync or verification when appropriate, but tunnel behavior and implementation remain outside `ielts-agents`.

## Future orchestration direction

A future coordinator or MCP dispatcher may route user requests to Architect and Executor roles, pass contract/report artifacts between them, and invoke `@ielts-tunnel` for sync or verification.

That orchestration layer is future work and is not implemented in this repository.
