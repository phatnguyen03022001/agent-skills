# Implementation Contract

The canonical Architect-owned task shape is [templates/task.yaml](../templates/task.yaml). Target repositories may copy that template into `.agent/tasks/TASK-NNNN/task.yaml`.

This contract owns task-artifact obligations only. Reusable binding, authority/capability, lifecycle, continuation, promotion, and release semantics are owned by the [Task Protocol](../protocols/TASK_PROTOCOL.md).

## Task authority and execution binding

A task records the supported protocol version, task identity/revision, target repository/branch, pinned skill rules, structure authority, restrictive scope, gap policy, acceptance criteria, verification requirements, and explicit mutation authority.

The canonical [handoff template](../templates/handoff.yaml) binds execution to the exact task snapshot through `base_head`. Executor reads the task from that snapshot and fails closed on identity/state mismatch.

Task fields remain explicit where they carry artifact-specific obligations:

- `git_authority` records the independently authorized Git mutations for this task;
- optional `release_authority` records task-specific release permissions and defaults non-permissively when absent;
- optional phase-specific `capability_requirements` records semantic capabilities the task requires;
- optional `continuation_policy` records the task's continuation mode;
- `structure_authority`, restrictive scope, gap policy, acceptance criteria, and verification remain task-owned material authority.

The semantic meaning and interaction of those controls are defined once in the Task Protocol rather than repeated here.

## Structure, scope, and revisions

Architect owns `structure_authority` and task revisions. Task approval does not authorize unrelated cleanup, speculative features, architecture/spec/public-contract drift, dependency changes, or structural reorganization.

Every new source file needs existing or explicitly authorized ownership. Task-specific safety-significant choices remain explicit; unconditional protocol boilerplate need not be copied into each task.

Meaningful authority changes increment `task_revision`. Executor never rewrites task authority, refreshes a stale handoff, or silently upgrades rules.

See the [Task Protocol](../protocols/TASK_PROTOCOL.md) and [continuation template](../templates/continuation.yaml).
