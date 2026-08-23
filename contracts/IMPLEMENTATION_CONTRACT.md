# Implementation Contract

Reusable Architect-to-Executor handoff. Keep it concise and deterministic. The Executor must not mutate unless `execution_ready` is exactly `true` and the live target matches every required identity/precondition field.

## Template

```yaml
contract_id: ""
contract_version: 2

repository:
  full_name: ""
  url: ""
  branch:
    name: ""
    role: integration
  base_head: ""

objective: ""

authority_sources:
  - source: ""
    role: ""
    precedence: 1

required_skills:
  - name: ""
    source: ""

recommended_skills: []

scope:
  required_changes:
    - ""
  expected_files_or_components:
    - ""
  expected_files_are_restrictive: true
  out_of_scope_change_authorization: revised_contract_required

invariants:
  - ""

forbidden_changes:
  - ""

acceptance_criteria:
  - id: AC-1
    requirement: ""
    evidence_required: ""

verification:
  executor_checks:
    - id: CHECK-1
      command_or_check: ""
      required: true
  authoritative_verification:
    required: false
    mechanism: ""
    expected_signal: ""

pre_execution_checks:
  require_repository_match: true
  require_branch_match: true
  require_base_head_match: true
  require_clean_worktree: true
  require_required_skills: true

git_authority:
  create_branch: false
  commit: false
  push: false
  promote_to_main: false

blocking_decisions: []

stale_contract_behavior: BLOCKED
execution_ready: false
```

## Semantics

- `repository.full_name`, `repository.branch.name`, and `repository.base_head` bind the exact execution target. Missing any of them means no execution.
- `repository.branch.role` records intent. In the shared model, normal implementation is `dev` / `integration`; `main` / `stable` is promotion-only by default.
- `authority_sources` are ordered by `precedence`; lower numbers have higher authority. Unresolved conflicts block execution.
- `required_skills` contain only skills necessary for safe/correct execution. An unavailable required skill blocks execution.
- `recommended_skills` are non-blocking guidance. They do not silently expand scope or become required after execution starts.
- `scope.required_changes` authorizes only the requested work. `expected_files_or_components` is restrictive when the flag is true.
- `invariants` are conditions the implementation must preserve. `forbidden_changes` are explicit negative boundaries.
- each acceptance criterion has a stable ID and required evidence so the report can answer it one-for-one.
- mandatory `executor_checks` may not be skipped or substituted without a revised contract.
- `authoritative_verification` is separate from Executor checks and Architect review.
- `git_authority` is capability-based. False, omitted, or ambiguous means forbidden. Main promotion is separate from normal push.
- `stale_contract_behavior` must be `BLOCKED` or `NEEDS_REVIEW`.
- any blocking decision, identity ambiguity, required-skill ambiguity, scope ambiguity, or undefined required verification requires `execution_ready=false`.

Never silently refresh, rebase, retarget, or reinterpret a stale contract. The Architect must issue or approve a revised contract.
