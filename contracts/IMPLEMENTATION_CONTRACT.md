# Implementation Contract

The canonical Architect-owned task shape is [templates/task.yaml](../templates/task.yaml). Target repositories may copy that template into `.agent/tasks/TASK-NNNN/task.yaml`.

The task is the approved implementation authority. It binds one supported protocol version, task identity/revision, target repository/branch, pinned skill rules, structure authority, restrictive scope, gap policy, acceptance criteria, verification requirements, and Git capabilities.

## Execution authorization

The canonical [handoff template](../templates/handoff.yaml) identifies the exact task snapshot via `base_head`. Executor must read the task from that exact commit and fail closed if live state differs.

`task.git_authority` applies to Executor Git mutations. Artifact content ownership does not grant Git authority by implication. Executor owns `report.yaml` content, but an execution-ready task that relies on canonical committed report evidence must set `git_authority.commit: true`. Architect review authority remains separate and does not expand Executor capabilities.

## Structure and scope

`structure_authority.status` is `RESOLVED`, `NOT_APPLICABLE`, or `UNRESOLVED`; Architect owns that decision. Task approval never implies unrelated cleanup, speculative features, architecture/spec/public-contract drift, dependency changes, or structural reorganization.

Every new source file needs existing or explicitly authorized ownership. Unlisted new-file flexibility must be bounded by count, location, and purpose.

## Revisions

Architect owns task revisions. Meaningful task changes increment `task_revision`; Executor never rewrites task authority, refreshes a stale handoff, or silently upgrades rules.

See the [Task Protocol](../protocols/TASK_PROTOCOL.md).
