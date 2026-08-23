---
name: reuse-first
description: Use when a task may duplicate existing repository code, a standard protocol, platform capability, maintained library, framework feature, or upstream reference implementation.
---

# Reuse First

Prefer reuse before invention, but never dependency before thinking.

## Search from nearest to farthest

Before designing a new subsystem or utility, inspect:

1. the target repository for an existing implementation, abstraction, helper, or pattern;
2. the language/runtime standard library and native APIs;
3. the framework or platform already in use;
4. established protocols, formats, and ecosystem conventions;
5. mature maintained libraries;
6. upstream reference implementations or small adapters.

A new implementation needs a reason stronger than “we can write it.”

## Evaluate reuse, do not worship it

For a candidate dependency or platform feature, check:

- fitness for the actual requirement;
- maintenance activity and ownership;
- security and supply-chain implications;
- license compatibility;
- API stability and migration path;
- lock-in and portability;
- runtime, bundle, storage, and operational cost;
- transitive complexity and configuration burden;
- whether a thin adapter isolates the dependency cleanly.

Prefer the smallest adoption surface that solves the problem. Reuse an existing repository primitive when it is already the project convention. Prefer a standard protocol over a proprietary mechanism when project constraints permit.

## Decision outcomes

A good review can conclude:

- **REUSE**: existing capability already fits;
- **WRAP**: reuse behind a small project-owned adapter;
- **EXTEND**: modify an existing project abstraction;
- **BUILD**: no acceptable existing option satisfies the constraints.

Record why rejected options fail the project’s constraints so a later agent does not repeat the same search. If an existing capability solves 90% of the requirement, compare the cost of a small adapter with the long-term cost of owning the missing 10% yourself.

## Failure modes

Do not add a package for a trivial function. Do not create internal infrastructure because a mature platform feature feels “too easy.” Do not copy an upstream implementation and silently inherit its maintenance burden. Do not force a dependency whose abstraction is larger than the problem.

Use `simplicity` to reduce the shape of the chosen solution. Use `research` when candidate behavior, maturity, licensing, security, or current support must be verified externally.
