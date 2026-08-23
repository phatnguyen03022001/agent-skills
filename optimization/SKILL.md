---
name: optimization
description: Use when measured latency, throughput, memory, CPU, network, storage, build time, developer iteration time, cloud spend, or automation cost is materially outside a required budget.
---

# Optimization

Optimize from evidence: measure → identify constraint → change → re-measure.

## Define the target

State the workload, metric, baseline, required budget, and measurement environment. Distinguish user-visible performance from microbenchmarks and total cost from a single unit price.

Do not optimize a metric that has no project consequence.

## Find the constraint

Use profiling, tracing, query/build analysis, resource metrics, billing data, or controlled experiments appropriate to the system. Attribute the dominant cost before changing code or infrastructure.

Consider:

- algorithmic work and allocations;
- database/query behavior;
- serialization and payload size;
- network round trips;
- concurrency and queueing;
- cache effectiveness and invalidation cost;
- storage/read-write patterns;
- build/test/CI critical path;
- cloud resource sizing and idle capacity;
- developer feedback-loop latency;
- Actions or external-service fan-out.

Check whether `simplicity` or `reuse-first` can remove work entirely before making the remaining work faster.

## Change one meaningful variable

Prefer optimizations that preserve conceptual integrity and have a rollback path. Record expected benefit and trade-offs, including complexity, reliability, security, portability, and dollar cost.

Avoid speculative caches, parallelism, batching, denormalization, larger machines, or new services without evidence that they address the measured bottleneck.

Prefer removal of unnecessary work before clever acceleration. A deleted network hop, query, build step, dependency, or redundant transformation often improves both performance and maintainability. When parallelism is justified, include coordination, contention, ordering, retry, and failure overhead in the measurement rather than counting theoretical concurrency as throughput.

## Re-measure

Repeat the same representative measurement after the change. Report absolute and relative effect, variance, and any shifted bottleneck. If the result is noise or fails the target, do not declare success.

Cost optimization follows the same rule: verify current billing model and actual usage, reduce waste or right-size where evidence supports it, and do not weaken correctness or required reliability merely to lower a line item.

Use `debugging` when a regression may be caused by incorrect behavior rather than resource constraints. Use `reliability` when optimization changes failure behavior or capacity margins.
