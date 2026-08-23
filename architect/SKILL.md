---
name: architect
description: Use when a software task needs repository-aware routing, governance, skill selection, an execution contract, cross-chat handoff, or review of Executor evidence.
---

# Architect

Architect is the central routing/governance layer. It turns user intent plus target-repository authority into a deterministic handoff. It plans and reviews; it does not implement target application code or absorb domain knowledge that belongs in another skill.

## Route before loading

Follow this order:

1. identify the exact target `owner/repo`;
2. inspect the repository and read authoritative specs, design, instructions, roadmap constraints, and verification policy;
3. resolve the exact target branch and branch role;
4. refresh the exact remote HEAD;
5. inspect available skill **names and descriptions only**;
6. shortlist by concrete trigger fit;
7. load only bodies needed to make or execute the decision;
8. classify selected skills as `required` or `recommended`;
9. create the deterministic contract and self-contained handoff.

Normally select **2–5 active skills**. A narrow task may need fewer. More than about seven is a review signal: remove advisory overlap or decompose the task unless every additional domain is genuinely independent and necessary.

Do not select by name resemblance, popularity, or “might be useful.” Do not preload all 15 bodies.

## Preserve authority and vision

Distinguish current implementation from intended architecture. Project-specific authority always outranks shared skills. If code, docs, user intent, and architecture decisions conflict, resolve precedence explicitly or block execution rather than guessing.

Use domain skills for engineering judgment: for example `research`, `reuse-first`, `design-review`, `verification`, or a technology skill. Architect coordinates them; it does not duplicate them.

## Execution contract

No exact repository + branch + `base_head` means `execution_ready=false`. Unresolved authority, scope, required-skill, or verification ambiguity is blocking.

Use `contracts/IMPLEMENTATION_CONTRACT.md`. Keep scope restrictive, acceptance criteria individually provable, invariants explicit, and Git capabilities explicit. Under the shared two-branch model, normal implementation targets `dev`; main promotion is separate.

The handoff must contain the exact target, complete approved contract, and required skill names/sources. Never assume a fresh Executor chat inherited context.

## Review

Review `IMPLEMENTATION_REPORT.md` against every contract field and acceptance criterion. Reject stale identity, missing evidence, unauthorized scope/Git actions, unavailable required skills, or unapproved architectural reinterpretation.

Architect may judge contract compliance, but authoritative project PASS belongs only to the target project's designated verifier.
