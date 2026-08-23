---
name: design-review
description: Use when reviewing architecture, interfaces, major refactors, system structure, product-direction alignment, or consequential design choices before implementation.
---

# Design Review

Judge whether a proposed design advances the target project’s intended system, not whether it looks architecturally impressive.

## Establish authority and drivers

Start from user intent plus the target repository’s canonical specifications, architecture decisions, design documents, roadmap constraints, and explicit invariants. Distinguish intended architecture from accidental properties of the current implementation.

Identify the quality attributes that actually matter for this decision: correctness, maintainability, reliability, security, performance, cost, compatibility, operability, or delivery speed. Do not mechanically apply every lens.

## Review the design

Examine relevant areas:

- conceptual integrity and fit with existing architecture;
- component/module boundaries, cohesion, coupling, and dependency direction;
- data ownership, source of truth, schemas, and state transitions;
- interface/API contracts and compatibility;
- failure handling and recovery boundaries;
- migration, rollout, rollback, and reversibility;
- observability and operability requirements;
- security/trust boundaries;
- scalability and resource/cost implications;
- testability and deterministic verification;
- repository structure, ownership, and placement when these affect architecture.

For each concern, state the affected requirement or quality attribute, evidence, consequence, and a simpler or safer alternative when one exists.

## Multiple perspectives

Choose only relevant perspectives: product/user, architecture, implementation, operations, security, performance, cost, maintainability, testing, and migration/backward compatibility. A design that is locally elegant but violates product direction, operational reality, or migration constraints is not a good design.

Prefer explicit trade-offs over universal rules. Record irreversible decisions more carefully than reversible ones. Do not reward extra services, layers, patterns, or abstractions without evidence.

When reviewing repository structure, focus on architectural effects: dependency direction, ownership, change boundaries, generated/source separation, and discoverability of authoritative contracts. Naming or folder movement alone is not an architectural improvement. For each major recommendation, state what would become easier to change, test, operate, secure, or reason about.

## Boundaries

This skill critiques specified design choices. Use `gap-analysis` to find missing decisions and states. Use `security-review` for deep threat modeling, `reliability` for production-operability detail, and `simplicity` for concentrated accidental-complexity review.

Do not implement the reviewed change or rewrite project vision because current code drifted from it.
