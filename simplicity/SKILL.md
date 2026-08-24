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

## Source structure defaults

Prefer the shallowest source structure that preserves real ownership and keeps navigation obvious. These are preferred review defaults, not absolute maximums. Apply them primarily to new directories, new modules, proposed structural expansion, and review of newly introduced nesting.

Source depth is the number of directory segments from the language or project source root to the directory containing the file. The file itself does not count. Do not count repository wrappers above the actual source root merely because they exist. Source roots may include `internal/`, `pkg/`, `src/`, or `app/`, according to target-repository authority.

- **Go:** prefer source directory depth `<= 2`; depth `>= 3` requires a concrete structural justification.
- **Python:** prefer source directory depth `<= 3`; depth `>= 4` requires a concrete structural justification.
- **TypeScript:** prefer source directory depth `<= 3`; depth `>= 4` requires a concrete structural justification.

For example, `internal/runtime/verify/worker.go` is depth 2 from `internal/`, and `src/features/auth/oauth/client.ts` is depth 3 from `src/`.

Deeper structure is valid when it represents a real boundary, such as distinct domain ownership, an independently understandable component, a stable subdomain, a meaningful implementation boundary, or multiple cohesive files that benefit from isolation.

A deeper directory is not justified merely because it groups one file, mirrors class or type names, adds technical ceremony, follows a generic “clean architecture” convention, or may theoretically scale later. When no concrete boundary exists, prefer flattening.

Do not apply the depth preference mechanically to infrastructure or generated trees such as generated code, vendored dependencies, build or distribution output, migrations, fixtures, or testdata.

Prefer ownership-, domain-, or feature-oriented organization over generic technical-layer hierarchies when those layers merely scatter one feature across unrelated directories. For example, prefer focused areas such as `src/billing/`, `src/identity/`, and `src/notifications/` over default global `controllers/`, `services/`, `repositories/`, `managers/`, or `helpers/` buckets. Technical-layer directories remain valid when the target architecture uses them as meaningful boundaries.

Treat names such as `common`, `shared`, `utils`, `helpers`, `misc`, `base`, and `core` skeptically unless ownership and purpose are concrete; do not prohibit them mechanically. Before extracting to `shared`, prefer evidence of at least two real independent consumers.

Keep language naming guidance minimal:
- **Go:** package and directory names should be lowercase, short, and idiomatic; avoid unnecessary nesting and redundant package names.
- **Python:** package and module names should use `snake_case`.
- **TypeScript:** follow the target repository's established source file and directory convention; if none exists, prefer `kebab-case`.

Existing repository naming conventions take precedence; do not introduce naming-lint enforcement from this guidance.

Apply precedence in this order:
1. target repository authoritative specification, design, and conventions;
2. existing coherent target-repository structure;
3. these reusable simplicity defaults.

Existing deeper structure is not itself a reason for unrelated refactoring. Do not reorganize an existing codebase merely because current depth exceeds the preferred default.

Do not optimize for minimum directory count at the cost of giant files, unrelated code in one package, or broken domain boundaries. Do not optimize for architecture aesthetics at the cost of needless nesting, indirection, generic layer directories, or speculative abstractions.

## Review output

Identify complexity with its claimed benefit. Classify it as:

- **required now**;
- **justified boundary**;
- **premature/speculative**;
- **duplicate/indirect**.

Recommend deletion or simplification only when behavior and invariants remain provable.

Common rationalizations to challenge include “we may need multiple implementations later,” “a service is cleaner than a module,” “configuration makes it flexible,” and “automation is always better.” Future possibilities count only when project authority or repeated evidence makes them credible. Prefer direct data/control flow that a new maintainer can trace without reconstructing hidden conventions.

Use `reuse-first` when the simplification question is build-versus-adopt. Use `design-review` when trade-offs concern system boundaries or quality attributes rather than accidental complexity alone.
