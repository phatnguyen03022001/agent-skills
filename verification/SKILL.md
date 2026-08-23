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
