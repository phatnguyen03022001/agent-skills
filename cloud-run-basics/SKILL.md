---
name: cloud-run-basics
description: Use when a task involves deploying, configuring, troubleshooting, securing, scaling, or cost-optimizing Google Cloud Run services, jobs, or worker pools.
---

# Cloud Run Basics

## Core invariant

Treat Google Cloud project, region, resource type, service identity, current revision, exposure, and billing impact as explicit state. Read current state before changing it; do not guess from local config or old conversation context.

## Pre-write checks

Before a consequential Cloud Run write:

1. Confirm the active Google Cloud account and exact project ID.
2. Confirm region and resource type: service, job, or worker pool.
3. Read the existing resource and current revision/configuration when it exists.
4. Identify IAM, networking, secret, build, traffic, and billing effects.
5. Confirm the operation is authorized. Treat public exposure, IAM expansion, cloud build/workflow execution, new always-on resources, and paid or unknown-cost features as consequential.

Do not silently enable APIs, grant broad IAM roles, make a service public, create infrastructure, or trigger builds merely because deployment would otherwise be easier.

## Runtime contract

For HTTP services, the ingress container must listen on `0.0.0.0` and the port supplied by `PORT` (8080 by default). Do not bind only to `127.0.0.1`.

Use:

- **services** for HTTP, request-driven, function, or event workloads;
- **jobs** for run-to-completion work such as migrations and batch processing;
- **worker pools** for continuous pull-based background processing.

Prefer Artifact Registry for production images. Prefer immutable image digests for deterministic releases when practical.

## Identity and secrets

Prefer a dedicated user-managed service account with least privilege. Do not rely on broad default service-account permissions when a narrower identity is practical.

Use Secret Manager or another approved secret mechanism. Do not place credentials, API keys, database passwords, or private tokens directly in source-controlled files or command history.

Public access must be intentional. Do not add `allUsers`, disable invoker checks, or weaken ingress controls unless the task explicitly requires public invocation.

## Networking and cost guard

For small or bursty web workloads, prefer scale-to-zero behavior where requirements allow it. Keep `min-instances` at `0` unless latency or availability requirements justify always-on capacity, and set a bounded `max-instances` when uncontrolled fan-out could create cost or downstream pressure.

Co-locate Cloud Run with databases and storage when practical. Do not introduce VPC connectors, Cloud NAT, load balancers, CDN, static IPs, Cloud SQL, GPUs, larger instances, or other billable infrastructure merely as generic "best practice".

When cost matters, verify current Google Cloud pricing rather than relying on remembered prices or assuming a short job is free. If an operation may create paid usage and approval is unclear, stop before executing it.

## Deployment safety

Prefer deterministic, inspectable deployment inputs. Before deployment, verify the application locally with the repository's designated checks when available.

Normal flow:

`inspect project/resource -> verify application -> review config/cost -> deploy revision -> inspect result -> verify health -> verify traffic`

Do not equate a successful CLI/API response with application correctness. After deployment, inspect the resulting resource and revision. For HTTP services, verify the intended endpoint and authentication behavior. Check logs when startup or health verification fails.

Do not change traffic splitting, delete old revisions, or perform rollback unless required by the task or necessary to recover from the deployment being performed.

## Source deployments and builds

`gcloud run deploy --source` can invoke Cloud Build and create build artifacts. Treat it as cloud execution with possible cost and IAM effects, not as a purely local command.

When the task only requires deploying a prebuilt image, do not add Cloud Build, GitHub Actions, Terraform, or another CI/CD layer for convenience.

## Verification separation

Keep these distinct:

- local build/test success;
- container startup correctness;
- Cloud Run deployment success;
- revision health;
- traffic/invocation correctness;
- application-level acceptance tests;
- cost/security review.

If required verification was not run or failed, say so. Do not manufacture a higher-level PASS from a successful deploy alone.

## Fail closed

Stop before writing when any of these is unresolved:

- project/account identity;
- region or target resource;
- required write authority;
- current resource state needed for a safe update;
- public/private exposure intent;
- destructive delete/replace intent;
- IAM expansion;
- potentially paid operation without approval;
- required verification that completion depends on.

## Quick reference

```bash
# Inspect
gcloud config get-value project
gcloud auth list
gcloud run services describe SERVICE --region REGION

# Deploy an existing image
gcloud run deploy SERVICE --image IMAGE --region REGION

# Read recent logs
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="SERVICE"' --limit=20

# Jobs
gcloud run jobs describe JOB --region REGION
gcloud run jobs execute JOB --region REGION --wait
```

Before using unfamiliar flags, inspect the installed CLI's `--help` and current Google Cloud documentation. Do not invent flags or assume Preview behavior is stable.

## Upstream reference

This local skill is adapted from the official Google `google/skills` Cloud Run guidance at `skills/cloud/cloud-run-basics`, observed at upstream commit `40d70a4187ced7d0f81a85568ccf10ff79af5bb1`. It is intentionally not a byte-for-byte mirror; it adds fail-closed identity, IAM, cost, and verification guards for agent-driven workflows.
