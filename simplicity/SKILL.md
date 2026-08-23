---
name: simplicity
description: Use when a proposed change introduces new abstractions, services, layers, state, configuration, dependencies, automation, or generality beyond the immediate proven requirements.
---

# Simplicity

Choose the least complex solution that satisfies current requirements and preserves known constraints.

## Solution ladder

Challenge proposals in this order:

`existing solution → small change → small abstraction → larger abstraction → new subsystem`

Move right only when the simpler option fails a concrete requirement, invariant, quality attribute, or expected near-term change that is already authoritative.

Ask of every new layer, service, state store, queue, configuration axis, dependency, generator, workflow, or framework:

- What present requirement makes this necessary?
- What failure or change does it handle that the simpler design cannot?
- What new states, interfaces, ownership, and operations does it create?
- Can the same result be obtained by deleting or adapting something?
- Is the abstraction based on repeated evidence or a speculative future?

## Keep complexity where it pays

Simplicity is not “fewest lines.” A small explicit state machine can be simpler than scattered conditionals; a maintained library can be simpler than custom code; an interface can be justified when it isolates a real volatile boundary.

Protect decisions that are expensive to retrofit, such as data integrity, security boundaries, compatibility contracts, and irreversible migrations. YAGNI does not authorize ignoring known constraints.

Prefer reversible, local changes. Keep abstractions narrow until repeated use demonstrates a stable concept. Remove duplicate representations and unnecessary indirection. Avoid configuration when a single project-wide choice is sufficient.

## Review output

Identify complexity with its claimed benefit. Classify it as:

- **required now**;
- **justified boundary**;
- **premature/speculative**;
- **duplicate/indirect**.

Recommend deletion or simplification only when behavior and invariants remain provable.

Common rationalizations to challenge include “we may need multiple implementations later,” “a service is cleaner than a module,” “configuration makes it flexible,” and “automation is always better.” Future possibilities count only when project authority or repeated evidence makes them credible. Prefer direct data/control flow that a new maintainer can trace without reconstructing hidden conventions.

Use `reuse-first` when the simplification question is build-versus-adopt. Use `design-review` when trade-offs concern system boundaries or quality attributes rather than accidental complexity alone.
