# Implementation Contract

Reusable Architect-to-Executor handoff format.

The contract must be concise, deterministic, and explicit. The Executor must not execute unless `execution_ready` is exactly `true` and all required identity/precondition fields are consistent.

## Template

```yaml
contract_id: ""
contract_version: 1
repository:
  full_name: ""
  url: ""
  branch: ""
  branch_role: integration
base_head: ""
objective: ""
authority_sources:
  - path_or_source: ""
    authority_role: ""
    precedence: 1
required_skills:
  - name: ""
    source: ""
    required: true
problem_statement: ""
required_changes:
  - ""
expected_files/components:
  - ""
scope_control:
  expected_files_are_restrictive: true
  out_of_scope_change_authorization: revised_contract_required
must_preserve:
  - ""
acceptance_criteria:
  - ""
forbidden_changes:
  - ""
verification_requirements:
  executor_checks:
    - command_or_check: ""
      required: true
  authoritative_verification:
    required: false
    mechanism: ""
    expected_signal: ""
unresolved_decisions:
  - decision: ""
    blocking: true
pre_execution_checks:
  require_repository_match: true
  require_branch_match: true
  require_base_head_match: true
  require_clean_worktree: true
git_actions:
  create_branch: false
  commit: false
  push: false
  promote_to_main: false
stale_contract_behavior: BLOCKED
execution_ready: false
```

## Required semantics

- `repository.full_name`, `repository.branch`, and `base_head` identify the exact execution target. A new chat must not mutate without all three.
- `repository.branch_role` records intent. Under the shared dev/main model, implementation uses `dev` / `integration`; `main` / `stable` is promotion-only unless explicitly overridden by target governance.
- `authority_sources` are ordered by precedence. Lower numbers have higher authority. Unresolved conflicts are blocking.
- `required_skills` lists only skills whose trigger conditions match the task. A required unavailable skill blocks execution; the Executor must not approximate it from memory.
- `required_changes` authorize the requested implementation only, not cleanup or adjacent fixes.
- `expected_files/components` are restrictive by default.
- `must_preserve` are invariants, not preferences.
- `acceptance_criteria` must be individually provable in the report.
- mandatory `executor_checks` may not be skipped or substituted without a revised contract.
- `authoritative_verification` remains separate from Executor checks and Architect review.
- `git_actions` are explicit capabilities. Omitted/false/ambiguous means forbidden. `promote_to_main` is separate from normal push.
- `stale_contract_behavior` must be `BLOCKED` or `NEEDS_REVIEW`.
- any blocking unresolved decision requires `execution_ready=false`.

## Contract integrity

Treat the contract as not executable when:

- repository, branch, or base HEAD is blank/ambiguous;
- actual repository/branch/HEAD differs from the contract;
- `execution_ready=true` conflicts with a blocking decision;
- authority sources conflict without resolution;
- required skill selection is unresolved;
- code-changing scope is not deterministic;
- required verification is undefined;
- a needed git action is not explicitly granted.

Do not silently refresh, rebase, retarget, or reinterpret a stale contract. The Architect must issue or approve a revised contract.
