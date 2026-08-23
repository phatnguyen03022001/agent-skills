---
name: adversarial-audit
description: Use when correctness or governance depends on assumptions about stale state, retries, concurrency, partial failure, process death, dependency behavior, or policy compliance under pressure.
---

# Adversarial Audit

Try to make the proposed system or workflow fail before reality does.

## Start from invariants

List the guarantees that must survive failure: data consistency, at-most/at-least-once effects, authorization, branch/HEAD identity, ordering, uniqueness, durability, rollback ability, or execution-policy boundaries.

Then challenge the mechanisms that protect them.

## Fault-oriented questions

Use only relevant faults, including:

- stale reads, stale contracts, clocks, caches, or configuration;
- duplicate, delayed, reordered, or lost requests/events;
- retry after an operation succeeded but acknowledgement failed;
- concurrent writers and races;
- process death between multi-step effects;
- partial success across service or storage boundaries;
- timeout, throttling, network partition, storage exhaustion, or unavailable dependency;
- malformed or surprising dependency responses;
- interrupted deployment or migration;
- cleanup that never runs;
- future maintainers misunderstanding an implicit invariant.

For agent-governed workflows, explicitly test rationalizations: “the branch is probably unchanged,” “CI passed so promotion is safe,” “this adjacent cleanup is harmless,” or “the missing skill can be approximated from memory.” Convert important rules into observable gates or deterministic validation where possible.

## Produce actionable findings

For each plausible failure, state:

1. precondition/fault;
2. resulting incorrect state or policy violation;
3. earliest detectable signal;
4. containment/recovery path;
5. prevention or invariant-strengthening change.

Prefer high-consequence or likely faults over theatrical edge cases. Fault injection or simulation is useful only when authorized, bounded, and safer than speculation.

Look especially for single observations being mistaken for guarantees: one successful deploy, one passing retry, one clean shutdown, or one agent obeying a rule. Where policy matters, ask how the next agent can verify the invariant mechanically instead of relying on memory, wording, or good intentions.

## Boundaries

This is a generic failure and governance-pressure audit, not a substitute for `security-review` threat modeling, `reliability` production operating design, `debugging` root-cause work on an observed failure, or `gap-analysis` completeness review.

Do not demand distributed-systems machinery for a local deterministic problem simply because exotic failures can be imagined.
