# agent-skills

Reusable agent skills and handoff contracts for software work across repositories.

This repository is a shared skill library, not a target project's source of truth. Target repositories own their code, specifications, design, verification rules, deployment policy, and branch-specific authority. Skills provide reusable operating behavior; target-project authority wins on project-specific facts.

## Operating model

```text
User
  ↓
Architect
  ↓
inspect target repository
  ↓
read project authority
  ↓
resolve exact branch
  ↓
refresh exact HEAD
  ↓
discover candidate skills
  ↓
select minimal required skills
  ↓
create self-contained execution handoff
  ↓
Executor chat
  ↓
implementation + evidence report
  ↓
Architect review
```

- **Architect** is the routing/governance layer. It resolves repository authority and execution identity, discovers relevant skills, creates the deterministic contract/handoff, and reviews Executor evidence. It does not implement target application code.
- **Executor** performs exactly one approved contract. It fails closed on stale repository/branch/HEAD state and never reinterprets architecture.
- **Domain skills** add reusable decision guidance only when their trigger matches the task.
- **Project-designated verifier** owns authoritative project PASS when the target repository defines one. Git success, CI success, contract compliance, Architect review, and project PASS are separate signals.

A fresh Executor chat must not mutate anything until `repository.full_name`, exact target `branch`, and exact `base_head` are explicit and verified.

## Current catalog

| Skill | Type | Trigger |
| --- | --- | --- |
| `architect` | core orchestration | architecture/routing/governance, repo/branch/HEAD resolution, skill selection, contract creation, Executor review |
| `executor` | core execution | execution of one approved, execution-ready contract against exact repository state |
| `github-dev-main-workflow` | cross-project workflow | Git/GitHub work under a `dev` integration + `main` stable model, including promotion and Actions risk |
| `cloud-run-basics` | domain | Google Cloud Run deployment, configuration, troubleshooting, security, scaling, or cost work |

For this size, this README catalog is sufficient. Do not add a registry, database, package manager, category tree, or discovery service merely to prepare for hypothetical scale.

## Library size and discovery

There is no evidence-backed universal "best number" of skills. Library size and active-set size are different problems.

Practical scaling bands:

| Total library size | Default organization |
| --- | --- |
| 1–10 | flat skill folders + README catalog |
| 10–20 | flat folders remain sufficient; keep descriptions precise |
| 20–40 | flat folders can still work; a generated index becomes useful if churn/search cost rises |
| 40–80 | add lightweight tags/categories in an index and machine-assisted search; keep physical layout shallow unless domains are clearly stable |
| 80+ | use generated registry/index, search/ranking, overlap checks, and selective installation/loading |

These are transition bands, not quotas. Add a skill only when it owns a reusable, coherent decision domain.

For one task, the Architect should normally activate **2–5 skills**. A narrow task often needs **1–3**; a genuinely cross-domain task may need **4–7**. More than about seven active skills is a review signal: remove advisory overlap or decompose the task unless the skills are small, sequential governance steps.

## Skill granularity

Prefer **one skill = one coherent decision domain**.

Merge material that shares the same trigger and is normally needed together. For example, branch choice, commit/push authority, promotion safety, and GitHub Actions trigger/cost review belong together in `github-dev-main-workflow`; splitting them into `github-push`, `github-commit`, `github-actions`, and similar fragments would increase routing noise without creating useful independence.

Split a skill when both are true:

1. it contains independently useful decision domains with different trigger conditions; and
2. tasks commonly need one domain without loading the other.

Do not create a god skill that mixes unrelated technologies or operating responsibilities.

## Skill size

The Agent Skills specification recommends progressive disclosure: all skill metadata is cheap to discover, the full `SKILL.md` loads only when activated, and supporting resources load only when needed.

Local guidance:

- frequently loaded/core skills: aim for roughly **150–400 words**;
- normal domain/workflow skills: aim for roughly **300–800 words**;
- treat **~800+ words or ~100+ lines of heavy reference** as a prompt to move details into `references/`, scripts, or templates;
- keep `SKILL.md` well below the Agent Skills recommendation of 500 lines / roughly 5,000 tokens whenever practical.

Descriptions must begin with `Use when` and describe trigger conditions rather than summarizing the workflow.

## Architect discovery strategy

Use progressive disclosure:

```text
task
→ inspect target repository
→ read target authority
→ resolve branch + fresh HEAD
→ inspect skill names/descriptions only
→ shortlist candidates
→ load required candidate bodies
→ classify required vs recommended
→ contract
→ self-contained handoff
```

Do not load the full skill library into every task. Do not select a skill because its name merely sounds related. Descriptions are discovery metadata; the skill body is authoritative for how the selected skill works.

`required_skills` are necessary to execute the contract safely/correctly. An unavailable required skill blocks execution. `recommended_skills` are useful but non-blocking and must never be smuggled into required scope after execution begins.

## Execution handoff

The Architect's handoff to a fresh chat should be copy/paste-ready and self-contained:

```yaml
EXECUTION_HANDOFF:
  target:
    repository: owner/repo
    branch: dev
    base_head: exact-40-character-sha
  required_skills:
    - executor
    - github-dev-main-workflow
  recommended_skills: []
  contract:
    # complete approved contract from contracts/IMPLEMENTATION_CONTRACT.md
```

Never assume another conversation inherited repository identity, branch, HEAD, project authority, skill bodies, or approvals.

## Two-branch Git model

For repositories that adopt this shared model:

- `dev` = integration and normal mutation branch.
- `main` = stable, authoritative branch.
- normal implementation defaults to `dev`;
- delegated/third-party agents default to `dev` write authority only;
- direct implementation on `main` is forbidden by default;
- promotion `dev -> main` is a separate operation requiring refreshed `dev` and `main` HEADs, no unexpected divergence, required verification, and explicit promotion authority;
- prefer fast-forward promotion semantics when repository history permits;
- no force-push, history rewrite, unnecessary long-lived feature branches, or PR by default.

Target-repository governance may be stricter and always takes precedence.

## Contracts

`contracts/IMPLEMENTATION_CONTRACT.md` is the Architect-to-Executor protocol. It binds execution to exact target identity, authority, selected skills, restrictive scope, invariants, acceptance criteria, verification, and explicit Git capabilities.

`contracts/IMPLEMENTATION_REPORT.md` is the Executor-to-Architect evidence protocol. `CONTRACT_SATISFIED` means the Executor supplied evidence that the approved contract was satisfied. It is not authoritative project PASS.

## GitHub Actions and cost discipline

A small validation workflow on `dev` is appropriate for this library because agent-driven pushes can otherwise publish malformed frontmatter or drift the handoff contracts.

The repository's validation workflow is intentionally bounded:

- trigger: relevant pushes to `dev` only;
- one standard Linux job;
- no matrix, schedule, PR duplicate, artifacts, cache, external paid service, or automatic rerun;
- concurrency cancellation prevents superseded `dev` runs from continuing;
- a short timeout bounds runaway execution.

This repository is private. Standard GitHub-hosted runner usage consumes the owner's included Actions quota and can become billable after that quota is exhausted. A short run is therefore not automatically "$0". Local validation remains the first check; the `dev` workflow is a lightweight integration guard, not a project PASS authority.

`main` intentionally has no automatic validation trigger here. Promotion should receive already reviewed, verified `dev` state unless a target repository's governance requires otherwise.

## Future scaling

Intentionally not implemented:

- shared runner/tunnel;
- automatic Architect → Executor messaging;
- coordinator service;
- database-backed or large machine-readable registry;
- automatic main promotion.

Add those only when observed scale or workflow friction justifies them.
