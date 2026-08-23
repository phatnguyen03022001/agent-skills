---
name: cloud-run-basics
description: Use when a task involves deploying, configuring, troubleshooting, securing, scaling, or cost-optimizing Google Cloud Run services, jobs, or worker pools.
---

# Cloud Run Basics

## Core invariant

Treat Google Cloud account, project ID, region, resource type, service identity, current revision, exposure, and billing impact as explicit live state. Read before write; do not trust old conversation or local defaults.

## Pre-write gate

Before a consequential change, confirm the active account/project, region, target service/job/worker pool, current resource state, IAM/network/secrets/traffic effects, and authorization.

Do not silently enable APIs, broaden IAM, make a service public, create infrastructure, trigger builds, or enable paid/unknown-cost features merely to make deployment easier.

## Runtime and identity

HTTP containers must listen on `0.0.0.0:$PORT`. Use services for request/event workloads, jobs for run-to-completion work, and worker pools for continuous pull-based processing.

Prefer dedicated least-privilege service accounts and approved secret storage. Never place credentials in source-controlled files or command history. Public invocation must be explicit.

## Cost and infrastructure

Prefer scale-to-zero for bursty workloads when requirements allow it. Keep `min-instances=0` unless availability/latency justifies always-on capacity, and bound `max-instances` when fan-out can create cost or downstream pressure.

Do not add VPC connectors, NAT, load balancers, CDN, static IPs, Cloud SQL, GPUs, larger instances, or CI/CD as generic best practice. Verify current Google Cloud pricing when cost matters; do not assume a short operation is free.

`gcloud run deploy --source` may invoke Cloud Build and create artifacts. Treat it as cloud execution with IAM and billing effects.

## Deployment and verification

Prefer deterministic image inputs; immutable digests are useful for controlled releases. Run repository-designated checks before deployment when available.

Flow:

`inspect -> verify app -> review config/cost -> deploy -> inspect revision -> verify health/auth -> verify traffic`

Do not equate API/CLI success with application correctness. Keep local tests, image correctness, deploy success, revision health, traffic behavior, application acceptance, security, and cost review separate.

Stop on unresolved project/account identity, region/resource, write authority, exposure intent, destructive replacement, IAM expansion, paid/unknown-cost operation without approval, or required verification failure.

Before unfamiliar flags or Preview behavior, inspect current CLI help and official documentation.

## Upstream

Adapted from Google Cloud Run skill guidance, with additional fail-closed identity, IAM, cost, and verification rules for agent-driven workflows.
