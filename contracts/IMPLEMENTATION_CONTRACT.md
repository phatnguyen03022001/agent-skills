# Implementation Contract

This reusable contract is the Architect-to-Executor handoff format for IELTS engineering work.

The contract must be concise, deterministic, and explicit. Avoid prose that allows silent reinterpretation. The Executor must not execute unless `execution_ready` is exactly `true` and the contract is internally consistent.

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
    precedence: 1
problem_statement: ""
required_changes:
  - ""
expected_files/components:
  - ""
scope_control:
  expected_files_are_restrictive: true
  out_of_scope_change_authorization: "revised_contract_required"
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
  commit: false
  push: false
stale_contract_behavior: BLOCKED
execution_ready: false
```

## Field rules

- `contract_id`: Stable identifier for the delegated task.
- `repository`: Exact repository full name, URL, and branch authorized for execution.
- `base_head`: Exact commit SHA the Executor must match before work.
- `objective`: Single outcome the contract authorizes.
- `authority_sources`: Canonical documents, specs, designs, issue links, or user instructions that govern the work. Lower `precedence` numbers have higher authority. Unresolved conflicts must be recorded as blocking unresolved decisions.
- `problem_statement`: The concrete problem being solved.
- `required_changes`: Changes the Executor must make. These do not authorize extra cleanup or adjacent fixes.
- `expected_files/components`: Restrictive file/component scope by default. The Executor must not change files or components outside this list unless `required_changes` explicitly authorizes it or a revised contract is issued.
- `scope_control`: Must state whether file/component scope is restrictive and how out-of-scope changes can be authorized.
- `must_preserve`: Mandatory invariants. Violating any item prevents `CONTRACT_SATISFIED`.
- `acceptance_criteria`: Conditions required for the implementation to be considered contract-complete by Architect review. The Executor must not weaken or reinterpret them.
- `forbidden_changes`: Changes outside the authorized scope. Any forbidden change prevents `CONTRACT_SATISFIED`.
- `verification_requirements.executor_checks`: Executor checks. Items with `required: true` are mandatory and must not be skipped, substituted, or treated as informational without a revised contract.
- `verification_requirements.authoritative_verification`: Project-defined verification mechanism, if required. Executor checks do not replace this signal.
- `unresolved_decisions`: Decisions not delegated to the Executor. If any item has `blocking: true`, `execution_ready` must be `false`.
- `pre_execution_checks`: Required fail-closed checks before any edit. Repository, branch, HEAD, and working tree state must match the contract.
- `git_actions`: Explicit commit and push authority. If an action is `false`, omitted, or ambiguous, the Executor must not perform it.
- `stale_contract_behavior`: Must be `BLOCKED` or `NEEDS_REVIEW`. If repository, branch, HEAD, or working state differs from the contract, the Executor must stop instead of rebasing or reinterpreting the contract.
- `execution_ready`: Must be explicit `true` or `false`. The Executor must not execute when `false`.

## Contract integrity

The Executor must treat the contract as not executable and report `BLOCKED` or `NEEDS_REVIEW` when:

- required identity fields are blank or ambiguous;
- `execution_ready=true` conflicts with a blocking unresolved decision;
- authority sources conflict without an explicit resolution;
- expected file/component scope is missing for a code-changing task;
- required checks are undefined for a task that requires verification;
- git commit or push authority is needed but not explicitly granted.
