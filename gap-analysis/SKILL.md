---
name: gap-analysis
description: Use when a specification, design, plan, contract, migration, or implementation proposal may be incomplete and missing decisions could block safe execution or verification.
---

# Gap Analysis

Search the negative space: what must be true for this plan to work that has not been specified?

## Build the expected model

Identify actors, inputs, outputs, states, transitions, data ownership, external dependencies, lifecycle stages, invariants, and success criteria. Compare that model with what the artifact actually specifies.

Probe for missing:

- requirements and acceptance criteria;
- initial, terminal, invalid, and transitional states;
- error, timeout, cancellation, retry, and partial-success paths;
- authorization and trust-boundary decisions;
- validation and malformed-input behavior;
- concurrency and idempotency semantics;
- migrations, compatibility, rollout, rollback, and recovery;
- cleanup, retention, deletion, and resource ownership;
- observability, alerts, diagnostics, and operator actions;
- tests and authoritative verification;
- dependency assumptions and version constraints;
- ownership of schemas, configuration, secrets, and generated artifacts;
- invariants and forbidden changes.

Trace at least one normal path and relevant exceptional paths end-to-end. For stateful changes, ask what happens before, during, and after transition. For integrations, ask what happens when the dependency is slow, unavailable, duplicated, reordered, or returns unexpected data.

## Classify gaps

For every real gap, record:

- what is missing;
- why it matters;
- the decision owner or authority source;
- whether it blocks execution;
- what evidence would close it.

Do not fill an architectural gap by guessing. A blocking unknown should remain explicit until resolved or the Architect issues a revised contract.

Prioritize gaps by consequence and decision timing. A missing rollback path before an irreversible migration matters more than an undocumented cosmetic convention. Watch for requirements that exist only implicitly in tests, deployment scripts, schemas, or operational habits; surface them as candidate authority conflicts rather than silently treating implementation drift as intent.

## Boundaries

Gap analysis is about **completeness**, not preference. If a decision is specified but questionable, use `design-review`. If a specified design needs fault pressure, use `adversarial-audit`. If a missing fact requires external evidence, use `research`.

Do not manufacture exhaustive checklists for low-risk trivial changes. Search where missing information could change correctness, safety, compatibility, operations, or verification.
