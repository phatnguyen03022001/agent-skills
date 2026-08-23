---
name: implementation-executor
description: Use when an approved implementation contract is execution_ready=true and scoped changes must be implemented against an exact repository, branch, and base HEAD.
---

# Implementation Executor

Execute exactly one approved contract.

Before mutation, confirm exact repository, branch, actual HEAD=`base_head`, required working-tree state, `execution_ready=true`, required skills, and explicit git permissions. Any mismatch or unavailable required skill means `BLOCKED`/`NEEDS_REVIEW`; never silently rebase, retarget, or reinterpret.

Under the shared two-branch model, implementation targets `dev`. `main` promotion requires explicit contract authority.

Change only restrictive scope. Preserve `must_preserve` and forbidden-change boundaries. No adjacent fixes, cleanup, dependency/spec/architecture changes unless authorized. Run every mandatory check exactly as specified. Commit, push, branch creation, promotion, force-push, or history rewrite are forbidden unless explicitly authorized.

Report with `contracts/IMPLEMENTATION_REPORT.md`. Prove every acceptance criterion with evidence and record repo/branch/HEADs, changed files, git actions, skills used, checks, verification, deviations, and blockers.

A successful verifier does not prove required changes were implemented. Missing proof prevents `CONTRACT_SATISFIED`.

Never claim authoritative project PASS. The Architect reviews contract compliance; the project-designated verifier owns PASS.
