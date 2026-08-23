# agent-skills

Reusable agent skills and handoff contracts for software work across repositories.

This repository is a skill library, not a project source-of-truth. Each target repository keeps its own code, specs, design, verification rules, and deployment authority. Skills provide reusable operating behavior; target-project authority always wins on project-specific facts.

## Operating model

- **Project Architect**: resolves target authority, repository, branch, exact base HEAD, relevant skills, scope, and verification; then creates/reviews implementation contracts.
- **Implementation Executor**: mutates only the exact contract target and returns evidence.
- **Shared skills**: add domain behavior such as GitHub dev/main safety or Google Cloud Run operations.
- **Project verifier/runner**: owns authoritative PASS only when the target project designates it.

A new execution chat must not mutate anything until the exact `repository.full_name`, target `branch`, and `base_head` are explicit.

## Default Git model

For repositories that adopt the shared two-branch model:

- `dev` is the integration and normal mutation branch.
- `main` is stable and authoritative.
- normal implementation targets `dev`;
- promotion `dev -> main` is separate, explicit, and verification-gated;
- no extra branches, PRs, force-pushes, or history rewrites unless the user or target repository explicitly requires them.

This repository is being bootstrapped into that model. After bootstrap, normal changes should land on `dev` first.

## Skill discovery

Architects should select skills by frontmatter `description`, not by name alone. Load only skills whose trigger conditions match the task.

Current catalog:

| Skill | Trigger |
| --- | --- |
| `project-architect` | architecture, scope, repository/branch targeting, skill selection, contracts, report review |
| `implementation-executor` | executing an approved contract against exact repo/branch/base HEAD |
| `github-dev-main-workflow` | Git/GitHub work under the shared dev/main model, including Actions/cost risk |
| `cloud-run-basics` | Google Cloud Run deploy/config/troubleshooting/security/scaling/cost work |

## Skill size guidance

Keep `SKILL.md` concise enough that agents actually read it. The working target is:

- frequently loaded skills: ideally under ~200 words;
- normal task-specific skills: ideally under ~500 words;
- move large schemas, references, and reusable templates into supporting files.

Descriptions should begin with `Use when` and describe trigger conditions only. They should not summarize the workflow, because agents may shortcut from the description instead of reading the skill body.

## Contract handoff

`contracts/IMPLEMENTATION_CONTRACT.md` is the Architect-to-Executor protocol.

It binds execution to:

- exact repository;
- exact branch and branch role;
- exact base HEAD;
- authority sources and precedence;
- required skills;
- restrictive scope;
- invariants and forbidden changes;
- acceptance criteria;
- Executor checks and authoritative verification;
- commit/push/promotion permissions;
- unresolved decisions;
- explicit `execution_ready`.

`contracts/IMPLEMENTATION_REPORT.md` is the Executor-to-Architect evidence protocol. `CONTRACT_SATISFIED` is never authoritative project PASS.

For a handoff to another ChatGPT conversation, the Architect must provide a self-contained envelope containing the contract plus required skill names/sources. Never assume another chat inherited repository, branch, HEAD, or skill context.

## GitHub and cost discipline

GitHub writes can trigger Actions or other infrastructure. Before consequential push/merge/rerun/dispatch operations, inspect applicable triggers and cost risk when available. Do not create or broaden CI, rerun workflows, use larger runners, or enable paid/unknown-cost features merely for convenience.

Prefer repository-native/local verification when it provides the required evidence and target-project governance allows it. Cost optimization must never weaken correctness.

## Cloud skills

`cloud-run-basics` is a reusable Cloud Run guardrail skill. It is intentionally concise and fail-closed around project identity, IAM, exposure, build/deploy side effects, billing risk, and verification.

Domain skills must not override a target repository's own deployment or security policy.

## Future shared runner

A future shared runner/tunnel may provide bounded sync and verification across projects. It should remain separate from this repository and use trusted project profiles rather than arbitrary shell commands.

The intended authority split is:

`Architect decides -> Contract authorizes -> Executor mutates -> Report evidences -> Architect reviews -> Project verifier declares PASS`

Do not collapse those roles merely because one environment happens to expose more tools.
