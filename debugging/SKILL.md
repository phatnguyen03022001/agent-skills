---
name: debugging
description: Use when a bug, failing test, broken CI job, incident symptom, regression, or unexpected behavior needs a reproducible root cause rather than speculative fixes.
---

# Debugging

Find the cause before changing the cure.

## Establish the failure

Capture expected versus actual behavior, environment/version, triggering input, and the smallest reliable reproduction available. For CI, identify the first causal failure rather than chasing downstream cancellations or cascades.

If the symptom cannot be reproduced, gather logs, traces, metrics, state snapshots, or history that can distinguish hypotheses. Do not “fix” an unobserved theory.

## Narrow systematically

1. Locate the boundary where correct state becomes incorrect.
2. Trace inputs/state backward from the symptom.
3. Compare working and failing cases.
4. Form one falsifiable hypothesis at a time.
5. Gather the smallest observation that can disprove it.
6. Repeat until the causal mechanism explains the evidence.

Instrument boundaries rather than flooding logs everywhere. Check recent changes, configuration, versions, concurrency, data shape, external dependencies, and environment only when evidence points there.

Prefer root-cause fixes over masking retries, sleeps, broad exception catches, or state resets. A timeout increase without understanding why latency changed is not debugging.

## Verify the fix

Create or strengthen a targeted regression check when practical. Demonstrate that the failure existed before the fix or that equivalent evidence isolates it, then show the corrected behavior and relevant surrounding tests.

If the investigation reveals an architectural or operational weakness beyond the authorized scope, report it separately; do not smuggle a redesign into a bug fix.

Keep a short hypothesis ledger when the problem is complex: observation, hypothesis, discriminating check, result. This prevents revisiting disproven theories and makes handoff possible. If a workaround restores behavior without explaining the causal mechanism, label it a mitigation rather than a root-cause fix.

## Incident mode

During a production incident, coordinate with `reliability`: safe mitigation and service restoration may precede complete root-cause analysis. Preserve enough evidence to continue investigation after stabilization.

Use `optimization` when behavior is correct but a measured resource/latency constraint regressed. Use `research` when the remaining hypothesis depends on undocumented or version-sensitive external behavior.
