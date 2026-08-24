---
name: design-review
description: Use when reviewing proposed or implemented architecture, interfaces, major refactors, system structure, product-direction alignment, or consequential design choices.
---

# Design Review

Judge whether a proposed or implemented consequential design advances the target project's intended system without introducing unjustified complexity or structural drift.

## Establish authority and drivers

Start from user intent plus the target repository's canonical specifications, architecture decisions, design documents, roadmap constraints, structure authority, and explicit invariants. Distinguish intended architecture from accidental properties of current implementation.

Identify only the quality attributes material to the decision: correctness, maintainability, reliability, security, performance, cost, compatibility, operability, delivery speed, or reversibility.

## Review design integrity

Examine relevant areas:

- conceptual integrity and fit with intended architecture;
- component/module/feature ownership, cohesion, coupling, and dependency direction;
- data ownership, source of truth, schemas, and state transitions;
- interface/API contracts and compatibility;
- failure/recovery boundaries;
- migration, rollout, rollback, and reversibility;
- observability and operability requirements;
- security/trust boundaries;
- scalability and resource/cost implications;
- testability and deterministic verification;
- source/generated/test placement and authorized structural boundaries.

For implemented changes, compare the actual diff/structure with the approved design and task. Look for dependency-direction violations, orphan files, generic dumping grounds, unauthorized top-level/shared areas, product/vision drift, or abstractions introduced beyond current evidence.

File naming and physical layout must follow target language/framework/project conventions. The invariant is intentional ownership, not one cross-language directory recipe.

For each concern, state affected authority/quality attribute, evidence, consequence, and a simpler/safer alternative when one exists.

## Multiple perspectives

Choose only relevant lenses: product/user, architecture, implementation, operations, security, performance, cost, maintainability, testing, migration/backward compatibility. Do not mechanically run every lens.

Prefer explicit trade-offs over universal rules. Record irreversible decisions more carefully than reversible ones. Do not reward services, layers, factories, registries, extension points, shared modules, or other scale structure without current evidence.

## Boundaries

This skill judges quality/integrity of specified or implemented design. Use [gap-analysis](../gap-analysis/SKILL.md) for missing decisions/states, [security-review](../security-review/SKILL.md) for malicious/trust-boundary analysis, [reliability](../reliability/SKILL.md) for production failure/recovery, and [simplicity](../simplicity/SKILL.md) for concentrated accidental-complexity review.

Do not implement the reviewed change or rewrite project vision because current code drifted from it.
