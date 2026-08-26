# Task Protocol

This protocol defines reusable Architect-to-Executor governance across repositories. `agent-skills` owns how work is governed; each target repository owns what its product is and stores its live tasks.

Supported protocol version: **3**. These additions are backward-compatible. Existing valid expanded v3 artifacts remain valid; optional controls that are absent default to manual, fail-closed, and non-permissive behavior. Unsupported versions fail closed and are never silently upgraded.

## Core bindings

Architect remains ChatGPT and GitHub remote truth is canonical. A single Architect conversation may govern multiple repositories sequentially, but it has one active target repository at a time. Repository-specific planning, review, task creation, continuation, or mutation requires an explicit `owner/repo` binding. Facts from another repository never silently become authority.

Before Architect switches repositories, it must close the current repository-specific phase cleanly, explicitly identify the next `owner/repo`, refresh canonical GitHub truth for that repository, discard previous repository-specific assumptions, and establish fresh repository-local task/review identity before any mutation. Any simultaneous ambiguous active target is forbidden.

A single Executor chat may also be reused sequentially. While work is active, the active task/repository binding remains immutable: one approved task revision, one repository, one branch, and one exact execution authorization. Rebinding requires the prior execution to reach an explicit terminal handoff/result, previous evidence finalized, no outstanding mutation authority carried forward, an explicit next repository, a fresh repository-local task, a fresh exact handoff, a fresh exact base HEAD and branch identity, refreshed canonical GitHub truth, and a newly verified binding before mutation.

The approved exact task plus handoff is prior authorization for bounded Executor actions inside the active binding; a role must not invent extra user approvals for phases already authorized by those artifacts.

## Optional operator profile

A host/session/operator may supply an optional operator profile location/content at bootstrap. It is durable preference/environment context, not target-repository factual or mutation authority. Explicit current user decisions, target-repository canonical facts, and exact task authority outrank profile preferences. Reusable governance does not hard-code operator identity, profile location, machine, secret, personal provider/model default, personal path, or branch preference. A missing profile is not a blocker.

An explicitly configured operator-profile observation write is non-authoritative continuity context only. It does not switch the active target, create repository-specific authority, or grant mutation authority over the observed repository; lack of a writable observation store does not block current repository work. Before a deferred observation influences later action, the repository must be explicitly bound through the normal rules, current canonical GitHub truth refreshed, and the observation revalidated.

## Organizational roles and acceptance ownership

There are two organizational roles: Architect and Executor. Architect is ChatGPT. Reviewer, verifier, red-team, debugger, researcher, coder, and similar execution modes are Executor specializations, not additional organizational roles. Other execution agents/sessions, including Codex, operate as Executors when used. Role specialization never changes artifact ownership or authority boundaries.

Exactly one current governing Architect owns final ACCEPT/REJECT/REVISE judgment for the active repository binding. Independent reviewer/red-team/verifier sessions are an Executor specialization and produce advisory evidence unless the target explicitly designates verifier-owned authoritative PASS/FAIL. They never become a second Architect or independently own product/governance acceptance. Existing v3 `review.yaml` values remain `ACCEPTED`, `REVISION_REQUIRED`, and `BLOCKED` for backward compatibility.

## Repository-local authority across sequential bindings

The authority for repository A never grants authority for repository B. Every binding independently preserves repository identity, branch identity, task ID/revision, base HEAD, Git authority, capability requirements, verification, report evidence, review evidence, and promotion/release authority. The report/review/verifier/promotion/release lineage remains repository-local.

Never create a shared mutable cross-repository authority object. Sequential reuse changes only which repository is currently bound; it does not merge tasks, evidence, lifecycle, or authority across repositories. A user who never switches repositories observes effectively the same single-repository v3 semantics.

## Cross-repository PROGRAM presentation

`PROGRAM` may present ordered repository-local tasks as one operator-visible sequence, for example repo A → task A → report A, then repo B → task B → report B. PROGRAM is presentation only and is not a universal multi-repository task authority. Canonical authority remains repository-local and execution is sequential by default.

This model creates no orchestrator, no registry, no queue, no database, no workflow engine, no distributed transaction, no cross-repository lock, and no shared mutable cross-repository authority. Program progress never substitutes for exact task/handoff identity.

## Architect judgment and material user decisions

Architect optimizes for the user's durable user objective and explicit current product/design authority. Canonical authority is governing, not infallible: derived architecture, implementation accident, reviewer preference, or even current canonical text may be challenged only with concrete evidence of staleness, contradiction, incompleteness, or objective regression. This does not authorize ignoring explicit authority. Within non-waivable safety and policy boundaries, an explicit informed override remains valid.

Classify material user decisions by impact. A compatible decision may proceed. A trade-off requires a warning and recommendation. A regression requires a strong warning. A decision that contradicts the durable objective stops for explicit informed override. Ambiguity or casual assent is not informed approval for material architecture, protocol, security, compatibility, destructive, or irreversible change.

## Material-design-readiness gate

Before consequential implementation, Architect identifies the applicable target product/design authority and resolves only material missing decisions that could change correctness, compatibility, security, ownership, irreversible behavior, or acceptance. Trivial, mechanical, reversible, or well-specified work is not forced through documentation ceremony. Gap analysis and design review remain proportional to material risk, and detailed documentation structure remains outside this protocol.

## Risk-proportional execution lanes

The one canonical v3 task/protocol supports three proportional lanes without another task schema, role, framework, or lifecycle:

- `DIRECT`: small reversible low-risk changes with clear authority and cheap deterministic verification.
- `BOUNDED`: normal task → Executor → verification → Architect review flow.
- `HIGH_ASSURANCE`: materially consequential security, protocol, migration, irreversible, or release-critical work requiring stronger evidence/independence as explicitly specified by task authority.

DIRECT never bypasses target truth, explicit write authority, safety, scope, or required verification. HIGH_ASSURANCE must not become the default ceremony. Lane choice affects evidence rigor only; it never manufactures Git/release authority or changes artifact ownership.

## Artifact ownership and authority

Canonical target-repository artifacts are:

- `task.yaml`: Architect-owned material authority;
- `report.yaml`: Executor-owned evidence;
- `review.yaml`: Architect-owned judgment when repository policy stores it;
- [templates/continuation.yaml](../templates/continuation.yaml): a small machine-readable continuation envelope, not shared mutable state.

Content ownership, authority, and capability availability are distinct. Capability availability never grants authority, and authority never proves capability availability. A known capability is not a currently available capability. No role manufactures another role's authority or evidence.

`task.git_authority` governs Executor Git mutations. `create_branch`, `commit`, `push`, and `promote_to_main` are independent. `commit: true` does not authorize branch creation, push, `main` mutation, or promotion. `push: true` does not authorize branch creation, force push, `main` mutation, or promotion. `promote_to_main: false` forbids `main` ref mutation and merge into `main`. If `create_branch: false`, Executor MUST NOT invoke branch-creation capability for testing, probing, staging, temporary work, backup, recovery, or cleanup. Negative tests use isolated fixtures or mocks, never the live repository.

`task.release_authority`, when present, is separately owned authority with three independent booleans: `create_version_tag`, `mutate_repository_metadata`, and `publish_release`. If absent, all three are false. Commit, push, and `promote_to_main` never imply any release authority.

## External normative authority

Any external repository used as normative authority must be resolved to an immutable revision before mutation and represented through existing authority-source/task mechanisms. Mutable branch tips, latest documentation, or unpinned external repository state cannot govern execution. Current documentation, libraries, upstream repositories, examples, and other material used only as research/reference evidence does not become normative authority. This rule does not require a universal dependency registry.

## Canonical handoffs and compact prompt locators

[templates/handoff.yaml](../templates/handoff.yaml) is the Architect-to-Executor envelope containing protocol/type, exact task identity/path, repository/branch, and exact `base_head`.

Before mutation Executor verifies supported protocol, `handoff_type == EXECUTOR`, repository/branch identity, live HEAD equality with `base_head`, exact task identity at that commit, task binding, `execution_ready`, pinned skills, structure authority, current-phase capability availability, and applicable mutation authority. Any mismatch is `BLOCKED`.

A handoff authorizes only its repository. Rebinding to another repository always requires a fresh exact handoff and fresh exact base HEAD; prior handoff, task, Git authority, capability evidence, or lifecycle state cannot be reused as authority.

Operator-facing `PROMPT TO COPY` is an authority locator, not another authority artifact. Normal content is target owner/repo, branch, exact task ID/revision/path, exact base HEAD, current phase when needed, and a concise instruction to resolve canonical authority, preflight, execute, verify, report, and stop. Do not duplicate scope, invariants, forbidden changes, acceptance criteria, capabilities, Git/release authority, verification detail, or unconditional protocol boilerplate already available from canonical artifacts unless access to canonical authority is genuinely unavailable.

[templates/continuation.yaml](../templates/continuation.yaml) carries exact identity for a later post-review phase: protocol/task identity, phase, `reviewed_report.commit`, report revision, `promotion_candidate_head`, expected refs, prior result/lifecycle state, and one next authorized action. It does not create authority and does not implement an orchestrator, scheduler, queue, daemon, registry, database, or cross-session messaging runtime.

## Execution base without self-reference

Use `handoff_snapshot`:

1. Architect completes final planning/task changes.
2. Commit planning state when required.
3. Refresh the target branch and capture exact HEAD `H`.
4. Emit the handoff with `target.base_head=H`.
5. Executor reads the task from `H` and requires live HEAD to equal `H` before mutation.

No artifact needs to contain the SHA of the commit containing itself.

## Identity and ownership

Keep these identities distinct within each repository binding:

- `base_head`: Architect handoff identity for the pre-execution task snapshot;
- `final_execution_head`: Executor implementation HEAD before committing `report.yaml`;
- `reviewed_report.commit`: exact commit containing the report the current governing Architect actually judged;
- `promotion_candidate_head`: accepted-lineage SHA used for authoritative verification and promotion;
- authoritative verifier identity/result: verifier-owned evidence applying to the exact candidate SHA when explicitly designated;
- lifecycle state: a derived conclusion from authoritative artifacts, refs, and evidence, never a shared role-writable state file.

`reviewed_report.commit` must resolve the exact committed report. Normal cross-session remote review requires remote Git reachability. A local-only report commit is valid only when review and Executor contexts use an explicitly **shared trusted** checkout or Git object database that deterministically resolves the same commit and report content.

`report.yaml` state belongs to Executor evidence. It may remain `REPORTED` / `NEEDS_REVIEW` after the Architect accepts that exact report. Architect acceptance is separate evidence and does not justify rewriting the Executor report merely to mirror later review state.

## Executor-binding terminal vs whole-task lifecycle

An Executor-binding terminal ends current mutation authority when required execution evidence is finalized. `NEEDS_REVIEW` / `REPORTED`, `BLOCKED`, `STALE_STATE`, `AUTHORITY_REQUIRED`, `CURRENT_PHASE_CAPABILITY_UNAVAILABLE`, failed terminal execution, or completed execution may all close an Executor binding when no mutation authority remains. This does not imply acceptance, promotion, or release and does not skip later lifecycle boundaries.

Only after that explicit terminal boundary may a reused Executor context establish another repository binding from fresh repository-local authority.

## Derived workflow lifecycle

Lifecycle is derived per repository, not assigned by a multi-writer state service:

- `PLANNED`: approved task and exact handoff exist.
- `REPORTED`: Executor has produced the exact report evidence.
- `ACCEPTED`: the current governing Architect accepted the exact `reviewed_report.commit`.
- `VERIFIED`: the designated authoritative verifier produced the required result for the exact `promotion_candidate_head`.
- `PROMOTED_NOT_RELEASED`: the stable target ref has been explicitly promoted to the exact accepted candidate, but one or more separately authorized release actions are not completed.
- `RELEASED`: separately authorized release actions are complete and final identity verification succeeds.

`BLOCKED`, `REVISION_REQUIRED`, and `REVERIFY / REVIEW_REQUIRED` are stop/results, not permission to skip a lifecycle boundary. A terminal result closes the current execution binding but does not authorize the next repository.

## Pre-authorized continuation

Optional `continuation_policy.mode` is one of:

- `MANUAL`: return control after the current bounded phase;
- `AUTO_UNTIL_STOP`: an orchestration environment MAY dispatch the next required independent phase without returning to the user when existing exact authority already covers it.

If `continuation_policy` is absent, behavior is `MANUAL`.

`AUTO_UNTIL_STOP` does not merge roles, let Executor self-accept, manufacture verifier PASS, infer promotion/release authority, or treat absence of a human as approval. It stops on `BLOCKED`, `STALE_STATE`, `AUTHORITY_REQUIRED`, `CURRENT_PHASE_CAPABILITY_UNAVAILABLE`, `REVIEW_REQUIRED`, `REVERIFY_REQUIRED`, or `USER_STOP`.

## Execution environment, operator attention, and surface selection

Model, effort, and execution surfaces are supplied or established by the operator/environment, not guessed by Architect. Choose the least-powerful currently available surface sufficient for the phase. Use bounded escalation only when an authorized requirement cannot be satisfied on the lesser surface. Capability availability and authority remain separate facts.

Treat operator attention/manual labor as a constrained resource. When an available authorized agent/tool can safely perform an action, do not use the operator as a manual command/RPC bridge. Human input remains valid for unavailable capability, physical/local-only action that cannot be automated, unresolved product intent, destructive/irreversible authority, material paid-cost approval, or a major informed trade-off.

Keep resource use bounded. GitHub Actions must not become an iterative debugger when cheaper/native verification exists. Avoid repeated identical external/plugin/API calls; prefer bounded, narrow inspection over unnecessary full scans. Tool availability is not permission to consume quota. Paid or quota-limited resources are used only when materially justified. This is execution doctrine, not a billing subsystem.

## Phase-specific capability preflight

Optional `capability_requirements` maps semantic phases such as `EXECUTION`, `REVIEW`, `VERIFICATION`, `PROMOTION`, and `RELEASE` to required semantic capabilities. Missing declarations grant nothing.

Immediately before the first mutation or authoritative action of the current phase, preflight that phase's required capabilities. If the approved task already knows that native verification or another mandatory current-execution capability is required to complete the current execution, prove that currently available capability before the first mutation. If a required current-phase capability is unavailable, return `CURRENT_PHASE_CAPABILITY_UNAVAILABLE` and block before mutation. Do not preflight later phases as a prerequisite to completing an earlier authorized phase.

Examples: repository content write/test execution for `EXECUTION`; exact commit/report resolution for `REVIEW`; exact-SHA verifier access for `VERIFICATION`; non-force target-ref update for `PROMOTION`; tag, repository-metadata, and release-publication APIs for `RELEASE`.

## Target-authoritative Git topologies

Repository-specific branch policy and exact live refs outrank generic defaults. The existing Git workflow owner supports:

- `MAIN_ONLY`: one stable/working `main`-style branch when target authority says so;
- `DEV_MAIN`: mutable `dev` integration plus stable `main`, preserving existing dev/main behavior;
- `DEV_STAGING_MAIN`: `dev` → `staging` → `main` only when explicitly activated by target authority.

Never infer or create staging merely because `DEV_STAGING_MAIN` is supported. Never create any branch without explicit branch-creation authority. Promotion semantics must be interpreted against the target-authoritative topology rather than hard-coded branch names.

## GitHub/local drift

Authorized remote Git state is canonical repository truth; local state is an execution copy. A local clean/behind copy may be synchronized when authority permits. Local ahead or local dirty state is divergence or unknown work: never auto-push, reset, delete, or adopt it as authority merely because remote state is canonical. Remote drift from the authorized ref invalidates stale execution authority and fails closed.

On every repository switch/rebind, refresh canonical GitHub truth for the new target before repository-specific authority is used. Previous repository refs or local state are not evidence for the new binding.

## Local Hygiene Contract

Any local execution surface isolates temporary work under one run-owned root. Cleanup is part of completion when the current execution created local temporary artifacts. Cleanup authority is narrower than ordinary filesystem mutation authority: clean only artifacts created by the current run or explicitly disposable runtime-owned state.

Recursive cleanup is legal only when all safety proof is present. The target must be the exact current-run run-owned root or explicitly disposable runtime-owned root; creation, ownership, and run identity must be proven; canonical realpath must be contained in the authorized temporary/runtime root; and the target must not be a symlink traversal. Reject an empty or unresolved target, filesystem root, home, workspace root, repository root, any ancestor of those roots, pre-existing user state, a sibling project, or arbitrary user-supplied cleanup input. Path names, cache-like appearance, proximity to another project, or task/config input alone never prove disposability.

Missing cleanup proof means retain or return `BLOCKED`; never guess and delete. Evidence still required for diagnosis is retained with bounded artifact identity and reason and reported as `RETAINED_FOR_EVIDENCE`. Later stale cleanup obeys the same ownership, identity, realpath, and containment rules. A safely cleaned/no-artifact execution reports `PASS`.

## Evidence deduplication and v3 compatibility

Keep unconditional protocol boilerplate here, task-specific material authority in `task.yaml`, and record evidence once where practical instead of copying the same prose through task/report/review. Existing legacy inline evidence remains valid protocol-v3 input. Additive evidence references may be used only when existing validators/contracts support them; there is no parallel compact schema, task-lite variant, or new protocol version.

## TASK LAUNCH presentation

TASK LAUNCH is Architect-only operator UX and presentation only. It is not persisted per task, is not execution authority, and Executor does not own it. It contains only Chat, Executor, operator/environment-supplied Model, operator/environment-supplied Effort, Progress, and Giải thích / short explanation. Follow it separately with the compact `PROMPT TO COPY` authority locator defined above.

For a multi-repository program, Progress may use a concrete denominator such as `Program 2/4 · agent-standards · execution`. Do not invent fake percentages. No reusable launch artifact, launcher subsystem, or second authority source is created.

## Promotion lineage after review

Let `R = reviewed_report.commit` after Architect accepts that exact report.

Only two candidate lineages are valid:

1. `promotion_candidate_head == R`; or
2. `promotion_candidate_head` is the **single-parent direct child** of `R`, its only parent is `R`, and that one child commit contains only the expected Architect-owned review artifact.

A merge commit is never the permitted review-artifact child. An empty child is not the expected review artifact. Any other target-branch mutation after `R` invalidates the accepted lineage and requires a new Executor report plus Architect review. This exact accepted-lineage rule is unchanged.

Authoritative verification applies to the exact `promotion_candidate_head`. If the candidate branch changes afterward, prior evidence is stale: `REVERIFY / REVIEW_REQUIRED`. Actual promotion is a separate explicitly authorized operation. Release remains separate again.

## Structure authority applicability

Architect owns `structure_authority.status`:

- `RESOLVED`: non-empty source required;
- `NOT_APPLICABLE`: non-empty rationale required and valid only when structure cannot materially change;
- `UNRESOLVED`: execution cannot be ready.

Executor never changes this status to unblock itself.

## Gap policy

`LOCAL` is necessary for current acceptance criteria, completely inside authorized scope, and permitted by task policy. `FOLLOW_UP` is real but unnecessary or unauthorized for the current task; record it and do not fix it. `BLOCKING` means safe continuation requires missing or conflicting authority; stop with evidence. Discovery is never authorization.

## Stable maintenance and change admission

For mature governance, NO CHANGE REQUIRED is valid and preferred when no material problem is reproduced. Admit change only for an evidence-backed defect, stale rule/external reality, recurring missing capability, security issue, compatibility failure, material cost/usability/maintainability regression, or explicit durable maintainer objective change. Preference, novelty, elegance, architectural fashion, and hypothetical future scale are insufficient authority. Corrective maintenance remains permitted through the normal smallest safe correction path.

The 15-skill taxonomy is closed by default. New-skill admission requires repeated real evidence of a materially distinct recurring responsibility that cannot fit an existing owner cleanly, or exceptional correctness/security justification. No arbitrary numeric threshold is universal authority for admission.

## Global structure invariants

No orphan source files. Every new source file belongs to an existing or explicitly authorized responsibility. No speculative scale structure. Do not create layers, factories, registries, plugin systems, services, queues, caches, shared modules, top-level directories, or scaling infrastructure for hypothetical needs.

These unconditional protocol rules need not be recopied as prose into every task. The single canonical v3 task model remains authoritative; there is no task-lite, task-compact, second schema, universal program task, or second protocol.

## Executor flow

`receive exact handoff → verify base/task/rules → preflight EXECUTION capability → execute restrictive scope → resolve LOCAL only → record FOLLOW_UP → stop on BLOCKING → run checks → local hygiene gate → write REPORTED report → commit/publish report only when separately authorized → terminal handoff/result → stop`

Executor never self-accepts its report. Only after that terminal boundary may a reused Executor chat establish another repository binding from fresh authority.

## Architect review and continuation

The current governing Architect resolves the exact committed report identified by `reviewed_report.commit` and reviews protocol, identity, execution base, skills, scope, structure, gaps, Git actions, acceptance evidence, advisory evidence, and designated verifier evidence. Final serialized outcome is `ACCEPTED`, `REVISION_REQUIRED`, or `BLOCKED`.

`ACCEPTED` is contract acceptance. It is not authoritative verifier PASS, promotion authority, release authority, or proof that those later capabilities are available. When continuation is authorized, emit/use only exact evidence and refs; stale identity fails closed.
