---
name: reliability
description: Use when a service, job, deployment, migration, or integration must remain operable through failures, load, retries, recovery, rollout, or production incidents.
---

# Reliability

Design and operate for the failures that matter to users, without buying reliability with unnecessary machinery.

## Define the objective

Identify the user-visible service objective, critical dependencies, state that must survive, and tolerated degradation. Use explicit SLO/error-budget concepts when the project needs them; do not invent formal SLOs for a trivial internal script.

## Failure and recovery design

Review relevant concerns:

- timeouts and bounded waiting;
- retry policy, backoff, jitter, and retry budgets;
- idempotency and duplicate effects;
- concurrency, backpressure, queue growth, and load shedding;
- dependency failure and degraded modes;
- capacity/resource bounds;
- durable versus rebuildable state;
- health/readiness semantics;
- observability that drives an operator or automation action;
- rollout, feature flags, canary/staged delivery, and fast rollback;
- backup/restore, disaster recovery, and migration recovery where required.

Prefer simple bounded behavior over elaborate self-healing that hides faults. Every retry, queue, cache, replica, and fallback introduces states that must be understood.

Make failure visible at the right boundary. Silent fallback can protect users briefly while hiding a growing data or capacity problem; noisy alerts without an action create toil. Tie important signals to a response, owner, or documented recovery path. For stateful systems, identify the recovery point and recovery time actually required before designing backup/failover machinery.

## Incident response

When production is impaired:

1. establish impact and current state;
2. mitigate safely and restore service;
3. preserve evidence;
4. communicate material changes/risks;
5. identify root cause with `debugging`;
6. record follow-up actions that prevent recurrence or improve detection/recovery.

Do not let a postmortem become blame or a list of vague intentions. Follow-up actions need owners/mechanisms appropriate to the target repository.

## Verification

Exercise recovery paths when feasible. A backup never restored, failover never tried, or retry path never tested provides weaker confidence than its existence suggests.

Use `adversarial-audit` to pressure-test assumptions, `verification` to design deterministic evidence, and `optimization` when reliability choices are constrained by measured resource or cost budgets.
