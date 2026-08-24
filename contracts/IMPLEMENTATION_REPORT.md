# Implementation Report

The canonical Executor-owned evidence shape is [templates/report.yaml](../templates/report.yaml). Target repositories should store it as `.agent/tasks/TASK-NNNN/report.yaml` when the protocol is adopted.

Executor owns report evidence. Architect may review it but must not rewrite it to improve compliance or erase deviations.

## Identity and authority evidence

The handoff is the source of execution authorization; the task at that exact base is the source of execution rules. The report records what Executor observed.

Intentional comparisons use explicit authorized/observed values:

- `execution.authorized_base_head` vs `execution.pre_execution_head`;
- `skill_library.authorized_revision` vs `skill_library.observed_revision`.

The report does not duplicate the task repository/base under a second locator block. `task_source.path` plus execution repository/base identifies the exact task used.

## Required evidence

A report records:

- supported protocol/task/report identity and exact task path;
- authorized execution base, observed pre-execution HEAD, and final execution HEAD;
- authorized and observed skill-library revision;
- execution skills actually used;
- pre-execution gates, including exact task-at-base validation;
- every changed/new file and whether scope/structure authorized it;
- commits, pushes, and promotion status;
- evidence for every acceptance criterion and mandatory check;
- authoritative verifier status when available;
- discovered gaps and structural observations;
- deviations, blockers, and final working-tree state.

`final_execution_head` is the last implementation HEAD **before the report artifact itself is committed**. The commit containing `report.yaml` is identified externally during Architect review.

`final_execution_head` is not the promotion candidate when report/review or other intended repository mutations occur afterward.

## Gap evidence

Executor classifies discoveries only as `LOCAL`, `FOLLOW_UP`, or `BLOCKING` under the [Task Protocol](../protocols/TASK_PROTOCOL.md).

- LOCAL may be resolved only when task policy permits and the change remains fully in scope.
- FOLLOW_UP is recorded without implementation.
- BLOCKING stops execution.

A discovered issue never grants scope by itself.

## Result values

- `CONTRACT_SATISFIED`: evidence proves the approved task revision, including structure and Git policy, was satisfied.
- `NEEDS_REVIEW`: evidence exists but judgment, ambiguity, or residual uncertainty remains.
- `BLOCKED`: execution could not safely begin/continue.
- `FAILED`: execution was attempted but required scope/invariants/criteria/checks were not satisfied.

CI success or Git success alone is not authoritative project PASS.
