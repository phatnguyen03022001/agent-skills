---
name: verification
description: Use when a change needs a testing and evidence strategy, regression proof, acceptance checks, contract tests, invariant tests, or confidence before completion or release.
---

# Verification

Design evidence that would fail when the required behavior is wrong.

## Start from risk and acceptance

Map each acceptance criterion and important invariant to the cheapest reliable evidence. Choose test level by the failure being prevented, not by habit.

Useful methods include:

- focused unit tests for local deterministic behavior;
- regression tests that reproduce a bug before the fix where practical;
- characterization tests before risky legacy changes;
- integration tests for boundaries that mocks cannot prove;
- contract tests for independently changing producers/consumers;
- property-based or fuzz tests for broad invariants and input spaces;
- end-to-end tests for critical user/system paths;
- static analysis, schema validation, reproducible build checks, or runtime probes when they test the actual requirement.

TDD is useful when behavior can be expressed before implementation and feedback is fast. It is a method inside verification, not a ritual required for every configuration, migration, generated artifact, or exploratory task.

## Bounded deterministic execution bundles

When several required checks are deterministic and independent, they may share one **EXECUTION BUNDLE**: one bounded runtime invocation containing multiple jobs and one compact attributable `JOIN` result. Parallelize only a subset proven to have no shared mutable state, no ordering dependency, no conflicting externally rate-limited dependency, no material resource contention, and independently attributable results. Otherwise serialize the affected jobs inside or outside the bundle. Publication/ref mutation, migrations, shared databases/ports/temp/cache writes, and final mutation gates are serial.

The JOIN must preserve per-job identity and result; one failed job cannot be hidden by aggregate success. Bundling changes synchronization cost, not the assurance predicate set.

## Focused versus full suites

When a mandatory full suite semantically subsumes a focused suite, run the mandatory full suite directly on the happy path. Do not spend an extra synchronization boundary on focused-before-full ceremony. The focused suite becomes a diagnostic after failure unless it has distinct acceptance authority or proves a predicate the full suite does not cover. Separately authoritative focused checks remain mandatory.

## Evidence quality

A check should have a clear failure meaning. Verify that new tests can fail for the defect they claim to detect; a permanently green test is decoration. Avoid assertions tied only to implementation details, mocks that prove their own setup, and broad suites used as a substitute for a targeted causal test.

For nondeterministic systems, control time/randomness/environment where possible and define tolerances or repeated measurement honestly.

Separate:

- implementation checks run by the Executor;
- integration/CI evidence;
- acceptance evidence;
- project-designated authoritative verification.

Passing Git or CI mechanics is not proof that the intended change exists.

## Completion

Before declaring contract satisfaction, require evidence for every criterion, record skipped/substituted checks, and surface residual uncertainty. Failed mandatory checks block a clean result unless the Architect revises the contract.

Use `debugging` to find the cause of a failing check. Use `reliability` when verification must cover production recovery or fault behavior. Use `security-review` for security-specific negative tests and threat validation.
