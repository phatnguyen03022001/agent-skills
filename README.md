# agent-skills

A deliberately curated library of **exactly 15** reusable agent skills plus deterministic contracts, templates, and protocols for software engineering across repositories.

`agent-skills` defines **HOW WE WORK**. A target repository defines **WHAT THE PRODUCT IS** and stores live tasks/evidence.

Supported protocol version is **3**. Sequential repository binding, proportional execution, lifecycle/continuation, and local-hygiene hardening are additive and backward-compatible; existing valid expanded v3 artifacts remain valid.

## Main flow

```text
bounded user authorization
→ Architect task + exact handoff
→ Executor implementation + REPORTED evidence
→ Architect review of exact report + advisory/designated-verifier evidence
→ exact-SHA verification when required
→ explicit promotion
→ PROMOTED_NOT_RELEASED
→ separately authorized release
→ RELEASED + final identity verification
```

There are only two organizational roles: Architect and Executor. Reviewer, verifier, red-team, debugger, researcher, coder, and similar execution modes are Executor specializations. Exactly one current governing Architect owns final acceptance judgment; a designated verifier may own exact PASS/FAIL evidence only when target authority says so.

`MANUAL` continuation returns control after a bounded phase. `AUTO_UNTIL_STOP` may let an orchestration environment dispatch the next already-authorized independent phase without asking the user again. It never merges roles, creates authority, manufactures Architect judgment/verifier evidence, or treats the absence of a human as approval. No orchestrator is implemented here.

## Risk-proportional execution

The same canonical v3 task/protocol supports three lanes: `DIRECT` for small reversible low-risk changes with cheap verification, `BOUNDED` for the normal task flow, and `HIGH_ASSURANCE` for materially consequential security/protocol/migration/irreversible/release-critical work with explicitly stronger evidence. DIRECT never bypasses authority, safety, target truth, or required verification. HIGH_ASSURANCE must not become default ceremony.

## Sequential repository binding

Architect and Executor contexts may be reused across repositories sequentially, but only one active target repository is bound at a time. A repository switch closes the current repository-specific phase, explicitly selects the next `owner/repo`, refreshes canonical GitHub truth, discards old repository-specific assumptions, and establishes fresh repository-local task/handoff/base authority before mutation.

Executor rebinding additionally requires the previous execution to be terminal with evidence finalized and no outstanding mutation authority carried forward. Authority, evidence, review, verification, promotion, and release lineage never carry from one repository to another.

## Cross-repository PROGRAM

`PROGRAM` is presentation only for ordered repository-local tasks. It may show operator-visible sequencing such as repo A → task A → report A, then repo B → task B → report B, but it is not a universal multi-repository task authority and never creates shared mutable cross-repository authority. Canonical authority remains repository-local and execution is sequential by default. No program template, registry, queue, database, workflow engine, or transaction layer is introduced.

## Compact execution handoff

`PROMPT TO COPY` is an authority locator, not duplicated authority. Normal content is target owner/repo, branch, exact task ID/revision/path, exact base HEAD, current phase when needed, and a concise instruction to resolve canonical authority, preflight, execute, verify, report, and stop. Do not duplicate canonical scope, invariants, forbidden changes, acceptance criteria, capability detail, Git/release authority, verification detail, or protocol boilerplate unless canonical authority is genuinely inaccessible.

## Identity / ownership cheat sheet

| Identity or result | Meaning | Owner / authority source |
| --- | --- | --- |
| `base_head` | Exact pre-execution task snapshot from the handoff | Architect handoff |
| `final_execution_head` | Last implementation HEAD before the Executor report commit | Executor evidence |
| `reviewed_report.commit` | Exact commit containing the report actually reviewed | Current governing Architect review identity |
| `promotion_candidate_head` | Exact accepted-lineage candidate SHA eligible for verifier/promotion checks | Derived from accepted review lineage |
| authoritative verifier identity/result | Verifier-owned evidence for the exact candidate SHA when designated | Project-designated verifier |
| lifecycle state | Derived conclusion from authoritative artifacts, refs, and evidence | Derived, never a shared role-writable state file |

A report may remain `REPORTED` / `NEEDS_REVIEW` after Architect accepts that exact report. Review state is separate evidence.

## Authority, capability, external authority, and release

Authority never proves capability availability; capability availability never grants authority. A known capability is not a currently available capability. Before the first action of a phase, preflight that phase's required semantic capabilities; when mandatory native verification is known to be required for the current execution, prove it before the first mutation. Missing current-phase capability blocks before mutation. Missing later-phase capability does not invalidate an earlier completed phase.

Use the least-powerful currently available execution surface sufficient for the phase, with bounded escalation only when an authorized requirement needs it. Operator/environment supplies or establishes model, effort, and execution surfaces rather than reusable governance hard-coding a particular provider or machine.

Any external repository used as normative execution authority must be bound to an immutable revision before mutation. Research/reference evidence may use current external material without turning it into normative authority.

Git topology is target-authoritative: the workflow owner supports `MAIN_ONLY`, `DEV_MAIN`, and explicitly activated `DEV_STAGING_MAIN`; staging is never inferred or created just because support exists. `create_branch`, `commit`, `push`, and promotion are independent Git authorities. Release authority is independent again: version tag creation, repository metadata mutation, and release publication must each be explicitly authorized.

After exact promotion, incomplete or unavailable release work yields the valid derived state `PROMOTED_NOT_RELEASED`. `RELEASED` requires separately authorized release actions plus final verification.

## Resource discipline

Use bounded inspection and the smallest sufficient execution surface. GitHub Actions should not be used as an iterative debugger when cheaper/native verification exists. Avoid repeated identical external/plugin/API calls. Tool availability is not permission to consume quota; paid or quota-limited resources require material justification. No billing subsystem is introduced.

Treat operator attention/manual labor as a constrained resource. Available authorized tools should perform safe actions directly rather than turning the operator into a manual command/RPC bridge; exceptions remain unavailable capability, physical/local-only action, unresolved product intent, destructive/irreversible authority, material paid-cost approval, or major informed trade-offs.

## Remote truth and local hygiene

Authorized remote Git state is canonical repository truth; local state is an execution copy. Local ahead or dirty work is divergence, not disposable state or implicit authority. Remote drift invalidates stale execution authority.

Temporary local execution uses one isolated run-owned root. Recursive cleanup is fail-closed and limited to proven current-run or explicitly disposable runtime-owned roots. Missing ownership, identity, realpath, containment, or non-symlink proof retains/blocks instead of deleting. Executor reports optional local-hygiene result `PASS`, `RETAINED_FOR_EVIDENCE`, or `BLOCKED`; legacy v3 reports without that optional evidence remain valid.

## TASK LAUNCH

TASK LAUNCH is Architect-only operator UX and presentation only. It is not persisted per task and is not execution authority. It contains only Chat, Executor, operator/environment-supplied Model, operator/environment-supplied Effort, Progress, and Giải thích / short explanation, followed separately by the compact `PROMPT TO COPY` authority locator.

For a program, Progress may be concrete, for example `Program 2/4 · agent-standards · execution`; do not invent fake percentages. Executor does not own TASK LAUNCH and no launcher/template subsystem is introduced.

## Maintenance and frozen taxonomy

Mature governance may correctly return NO CHANGE REQUIRED when no material reproduced problem exists. Admit change only for an evidence-backed defect, stale external reality/rule, recurring missing capability, security issue, compatibility failure, material cost/usability/maintainability regression, or explicit durable maintainer objective change. Preference, novelty, elegance, architectural fashion, and hypothetical future scale are insufficient authority. Corrective maintenance uses the smallest safe correction.

The 15-skill taxonomy is closed by default. A new skill requires repeated real evidence of a materially distinct recurring responsibility that cannot fit an existing owner cleanly, or exceptional correctness/security justification. There is no arbitrary numeric threshold that by itself authorizes taxonomy growth.

## Accepted promotion lineage

Let `R = reviewed_report.commit` after Architect acceptance. A valid `promotion_candidate_head` is only:

- `R`; or
- the single-parent direct child of `R`, whose only parent is `R`, where that one child contains only the expected Architect-owned review artifact.

A merge commit, empty child, or any other post-`R` mutation requires a new Executor report and Architect review. Authoritative verification applies to the exact candidate SHA. If the candidate changes afterward: `REVERIFY / REVIEW_REQUIRED`.

## Curated skill catalog

<!-- SKILL_CATALOG_START -->
| Skill | Type | Decision domain / trigger |
| --- | --- | --- |
| `architect` | core | repository-bound routing/governance, planning authority, skill selection, tasks, handoffs, report review |
| `executor` | core | controlled execution of one approved task revision against one exact repository/base |
| `research` | reasoning | unknown/current/disputed/version-sensitive facts that materially affect an engineering decision |
| `reuse-first` | reasoning | build-vs-reuse decisions involving repository capabilities, standards, platforms, libraries, or upstream implementations |
| `simplicity` | reasoning | proposed abstractions, services, layers, state, configuration, dependencies, automation, or speculative generality |
| `design-review` | review | proposed or implemented consequential architecture, interfaces, structural integrity, and product-direction alignment |
| `gap-analysis` | review | missing requirements, states, failure paths, ownership, migration, verification, or unspecified decisions |
| `adversarial-audit` | review | stale state, retries, concurrency, partial failure, process death, dependency faults, and governance rationalizations |
| `security-review` | specialist | authentication, authorization, secrets, sensitive data, trust boundaries, untrusted input, and security-critical integrations |
| `verification` | engineering | testing/evidence strategy, regression proof, contract/invariant testing, acceptance evidence, confidence before completion |
| `debugging` | engineering | reproducible root-cause analysis for bugs, failing tests, CI failures, regressions, and unexpected behavior |
| `reliability` | engineering | operability through load/failure/retry/recovery, rollout/rollback, observability, and production incidents |
| `optimization` | engineering | measured performance, resource, developer-loop, automation, or cost constraints |
| `github-dev-main-workflow` | workflow | target-authoritative Git/GitHub topology, promotion, and Actions risk without inventing branches |
| `cloud-run-basics` | domain | Google Cloud Run deployment, configuration, security, scaling, troubleshooting, and platform-specific cost behavior |
<!-- SKILL_CATALOG_END -->

The validator recursively discovers every `SKILL.md` and accepts only these exact fifteen top-level locations. A hidden or nested sixteenth skill is an error.

## Canonical v3 artifacts and evidence dedup

There is one task model, not task-lite/task-compact variants. Reusable shapes are:

- [templates/task.yaml](templates/task.yaml): Architect-owned implementation authority;
- [templates/handoff.yaml](templates/handoff.yaml): exact Architect-to-Executor locator/authorization;
- [templates/report.yaml](templates/report.yaml): Executor-owned evidence;
- [templates/review.yaml](templates/review.yaml): Architect-owned judgment;
- [templates/continuation.yaml](templates/continuation.yaml): small post-review exact-identity continuation envelope;
- [contracts/IMPLEMENTATION_CONTRACT.md](contracts/IMPLEMENTATION_CONTRACT.md);
- [contracts/IMPLEMENTATION_REPORT.md](contracts/IMPLEMENTATION_REPORT.md);
- [contracts/ARCHITECT_REVIEW.md](contracts/ARCHITECT_REVIEW.md);
- [protocols/TASK_PROTOCOL.md](protocols/TASK_PROTOCOL.md).

Keep unconditional protocol boilerplate in the protocol, task-specific material authority in `task.yaml`, and record evidence once where practical. Existing legacy inline evidence remains valid v3 evidence; no parallel compact schema or new protocol version is introduced merely to reduce prose duplication.

## Gap and structure policy

`LOCAL` is necessary, in-scope work permitted by current authority. `FOLLOW_UP` is real but unnecessary or unauthorized now. `BLOCKING` requires new/conflicting authority before safe continuation. Discovery never grants authority.

Consequential implementation receives a material-design-readiness check against applicable target product/design authority; trivial, mechanical, reversible, or well-specified work is not forced through documentation ceremony.

No orphan source files. No speculative scale structure. `structure_authority.status` remains `RESOLVED`, `NOT_APPLICABLE`, or `UNRESOLVED`, owned by Architect.

## Validation and GitHub Actions

The stdlib-only validator checks the exact 15-skill taxonomy, frontmatter/catalog, constrained YAML, canonical task/handoff/report/review/continuation templates, lifecycle/continuation/capability/release semantics, sequential repository-binding doctrine, optional local-hygiene outcomes, identity consistency, and internal links.

The repository keeps one bounded validation workflow on relevant pushes to `dev`: one standard Linux job, read-only contents permission, short timeout, concurrency cancellation, immutable action pins, validator execution, and stdlib unittests. No extra workflow is required for this protocol hardening.
