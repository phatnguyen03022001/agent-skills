# Implementation Contract

The canonical Architect-owned task shape is [templates/task.yaml](../templates/task.yaml). Target repositories should copy that reusable shape into `.agent/tasks/TASK-NNNN/task.yaml` when this protocol is adopted.

The task is the approved implementation contract. It belongs to the target repository; `agent-skills` contains only the reusable protocol and template.

## Contract identity

A valid task binds:

- one `task_id` and explicit `task_revision`;
- one Architect session target repository;
- one target repository and branch role;
- one immutable shared `skill_library.revision` for internal skills;
- separate `architect_analysis_skills` and `execution_skills`;
- immutable revisions for any external skills;
- authority sources and structure authority;
- restrictive scope, invariants, forbidden changes, gap policy, structure policy, acceptance criteria, verification, and Git capabilities.

`execution_ready` must be false while any required identity, authority, scope, structure, skill, verification, or blocking decision is unresolved.

## Execution base

The task uses `execution_base.mode: handoff_snapshot`. Do **not** write the target branch HEAD that contains `task.yaml` back into that same task file.

After the final planning/task commit, Architect refreshes the target branch and places that exact SHA in the external `EXECUTOR_HANDOFF.base_head`. Executor must match live HEAD to the handoff and read the task from that exact base before mutation. See the [Task Protocol](../protocols/TASK_PROTOCOL.md).

## Skill semantics

Analysis skills record how Architect reached the task; they do not automatically enter Executor context.

Required execution skills must resolve at the task-pinned library revision. Recommended execution skills are non-blocking and cannot broaden scope or reinterpret the task. External skills require their own exact source/revision.

## Scope and structure

No unrelated cleanup, adjacent fixes, speculative features, architecture/spec/public-contract changes, unauthorized dependencies, or structural reorganization are implied by task approval.

Every new source file needs an existing or explicitly authorized ownership boundary. Unlisted new-file flexibility must be bounded by count, location, and purpose in `structure_policy`.

A dependency, public-contract, canonical-spec, architecture, or unauthorized structure change requires revised Architect authority.

## Revisions

Architect owns task revisions. Increment `task_revision` and preserve lineage/history when meaning changes. Executor must never rewrite `task.yaml` to authorize work it discovered during execution.
