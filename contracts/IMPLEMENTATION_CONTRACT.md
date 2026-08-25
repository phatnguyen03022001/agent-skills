# Implementation Contract

The canonical Architect-owned task shape is [templates/task.yaml](../templates/task.yaml). Target repositories may copy that template into `.agent/tasks/TASK-NNNN/task.yaml`.

The task is the approved implementation authority. It binds one supported protocol version, task identity/revision, target repository/branch, pinned skill rules, structure authority, restrictive scope, gap policy, acceptance criteria, verification requirements, and explicit mutation authority.

## Execution authorization

The canonical [handoff template](../templates/handoff.yaml) identifies the exact task snapshot via `base_head`. Executor reads the task from that exact commit and fails closed if live state differs. The exact approved task plus handoff is sufficient prior authorization for the bounded Executor phase; redundant user approvals are not invented inside that authority.

`task.git_authority` applies to Executor Git mutations. `create_branch`, `commit`, `push`, and `promote_to_main` are independent capabilities. None implies force push, history rewrite, branch creation, `main` mutation, or any release action not explicitly authorized.

Optional `release_authority` is separate from Git authority. Its independent booleans are `create_version_tag`, `mutate_repository_metadata`, and `publish_release`. If the block is absent, all are false. Promotion to `main` never grants any of them.

Optional `continuation_policy` defaults to `MANUAL`. `AUTO_UNTIL_STOP` allows an orchestration environment to dispatch the next already-authorized independent role/phase, but cannot merge roles, manufacture review/verifier evidence, infer authority, or treat an absent human as approval.

Optional phase-specific `capability_requirements` describe required semantic execution capabilities. Authority and capability remain separate. Current-phase required capability unavailable means block before phase mutation; later-phase capability unavailable does not invalidate an earlier completed authorized phase.

Executor owns `report.yaml` content, but an execution-ready task relying on committed report evidence must grant commit capability explicitly. Architect review authority remains separate. Report transport must also be consumable by the intended independent review context.

## Structure and scope

`structure_authority.status` is `RESOLVED`, `NOT_APPLICABLE`, or `UNRESOLVED`; Architect owns that decision. Task approval never implies unrelated cleanup, speculative features, architecture/spec/public-contract drift, dependency changes, or structural reorganization.

Every new source file needs existing or explicitly authorized ownership. Protocol-owned unconditional boilerplate need not be copied into every task. Safety-significant task-specific choices remain explicit, and there is still exactly one canonical protocol-v3 task model.

## Revisions

Architect owns task revisions. Meaningful task changes increment `task_revision`; Executor never rewrites task authority, refreshes a stale handoff, or silently upgrades rules.

See the [Task Protocol](../protocols/TASK_PROTOCOL.md) and [continuation template](../templates/continuation.yaml).
