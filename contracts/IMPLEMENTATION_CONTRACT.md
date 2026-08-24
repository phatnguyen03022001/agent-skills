# Implementation Contract

The canonical Architect-owned task shape is [templates/task.yaml](../templates/task.yaml). Target repositories should copy that reusable shape into `.agent/tasks/TASK-NNNN/task.yaml` when this protocol is adopted.

The task is the approved implementation contract. It belongs to the target repository; `agent-skills` contains only the reusable protocol and template.

## Contract identity

A valid task binds:

- one supported `protocol_version` (currently `3`);
- one `task_id` and explicit `task_revision`;
- one Architect session target repository;
- one target repository and branch role;
- one immutable shared `skill_library.revision` for internal skills;
- separate `architect_analysis_skills` and `execution_skills`;
- immutable revisions for any external skills;
- authority sources and explicit structure-authority applicability;
- restrictive scope, invariants, forbidden changes, gap policy, structure policy, acceptance criteria, verification, and Git capabilities.

`architect_binding.target_repository` and `target.repository` are intentionally duplicated identity claims and must be equal. They exist so Executor can verify the task belongs to the bound Architect target.

`execution_ready` must be false while any required identity, authority, scope, structure, skill, verification, or blocking decision is unresolved.

## Handoff and execution base

The canonical authorization envelope is [templates/handoff.yaml](../templates/handoff.yaml). It contains only protocol/type, task identity/path, target repository/branch, and exact `base_head`.

The task does not duplicate its own path or exact execution SHA. After the final planning/task commit, Architect refreshes the target branch and places that exact SHA in the external handoff. Executor reads `task.path` from **that exact commit**, verifies task ID/revision and repository binding, then applies the task rules.

Do not copy scope, skill rules, structure policy, authority sources, or acceptance criteria into the handoff. The exact task at the exact base is their single source of truth.

See the [Task Protocol](../protocols/TASK_PROTOCOL.md).

## Structure authority

`structure_authority.status` is one of:

- `RESOLVED`: non-empty `source` required;
- `NOT_APPLICABLE`: non-empty `rationale` required and valid only when the task cannot materially affect repository/module/file structure;
- `UNRESOLVED`: execution blocked.

Executor may not change this Architect-owned status to unblock itself. `NOT_APPLICABLE` cannot authorize source-file creation, module moves, dependency-boundary changes, or structural reorganization.

## Skill semantics

Analysis skills record how Architect reached the task; they do not automatically enter Executor context.

Required execution skills must resolve at the task-pinned library revision. Recommended execution skills are non-blocking and cannot broaden scope or reinterpret the task. External skills require their own exact source/revision.

## Scope and structure

No unrelated cleanup, adjacent fixes, speculative features, architecture/spec/public-contract changes, unauthorized dependencies, or structural reorganization are implied by task approval.

Every new source file needs an existing or explicitly authorized ownership boundary. Unlisted new-file flexibility must be bounded by count, location, and purpose in `structure_policy`.

A dependency, public-contract, canonical-spec, architecture, or unauthorized structure change requires revised Architect authority.

## Revisions

Architect owns task revisions. Increment `task_revision` and preserve lineage/history when meaning changes. Executor must never rewrite `task.yaml`, refresh a stale handoff, or silently upgrade protocol/skill rules to authorize work discovered during execution.
