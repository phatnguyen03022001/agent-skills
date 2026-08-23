# Implementation Contract

This reusable contract is the Architect-to-Executor handoff format for IELTS engineering work.

The contract must be concise, deterministic, and explicit. Avoid prose that allows silent reinterpretation. The Executor must not execute unless `execution_ready` is exactly `true`.

## Template

```yaml
contract_id: ""
repository:
  full_name: ""
  url: ""
  branch: ""
base_head: ""
objective: ""
authority_sources:
  - path_or_source: ""
    authority_role: ""
problem_statement: ""
required_changes:
  - ""
expected_files/components:
  - ""
must_preserve:
  - ""
acceptance_criteria:
  - ""
forbidden_changes:
  - ""
verification_requirements:
  executor_checks:
    - ""
  authoritative_verification:
    required: false
    mechanism: ""
    expected_signal: ""
unresolved_decisions:
  - decision: ""
    blocking: true
pre_execution_checks:
  require_branch_match: true
  require_base_head_match: true
  require_clean_worktree: true
stale_contract_behavior: BLOCKED
execution_ready: false
```

## Field rules

- `contract_id`: Stable identifier for the delegated task.
- `repository`: Exact repository full name, URL, and branch authorized for execution.
- `base_head`: Commit SHA the Executor must match before work.
- `objective`: Single outcome the contract authorizes.
- `authority_sources`: Canonical documents, specs, designs, issue links, or user instructions that govern the work.
- `problem_statement`: The concrete problem being solved.
- `required_changes`: Changes the Executor must make.
- `expected_files/components`: Files or components expected to change or be inspected.
- `must_preserve`: Invariants that must remain true.
- `acceptance_criteria`: Conditions required for the implementation to be considered contract-complete by Architect review.
- `forbidden_changes`: Changes outside the authorized scope.
- `verification_requirements.executor_checks`: Checks the Executor must run before reporting.
- `verification_requirements.authoritative_verification`: Project-defined verification mechanism, if required. Executor checks do not replace this signal.
- `unresolved_decisions`: Decisions not delegated to the Executor. If any item has `blocking: true`, set `execution_ready: false`.
- `pre_execution_checks`: Required fail-closed checks before any edit. Branch and HEAD must match the contract, and the working tree must be clean when using a checkout.
- `stale_contract_behavior`: Must be `BLOCKED` or `NEEDS_REVIEW`. If branch, HEAD, or working state differs from the contract, the Executor must stop instead of rebasing or reinterpreting the contract.
- `execution_ready`: Must be explicit `true` or `false`. The Executor must not execute when `false`.
