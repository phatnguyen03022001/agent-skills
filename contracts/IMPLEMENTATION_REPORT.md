# Implementation Report

This reusable report is the Executor-to-Architect return format for IELTS engineering work.

The report must distinguish what changed, what was verified, what deviated, and what still needs Architect review. Verification results must be factual and must not be fabricated.

## Template

```yaml
contract_id: ""
repository:
  full_name: ""
  url: ""
branch: ""
base_head: ""
pre_execution_head: ""
final_head: ""
status: ""
pre_execution_checks:
  repository_confirmed: false
  branch_confirmed: false
  base_head_confirmed: false
  working_tree_clean: false
working_tree_after:
  clean: false
  summary: ""
changed_files:
  - path: ""
    summary: ""
    in_contract_scope: false
commits_created:
  - sha: ""
    message: ""
pushed: false
implementation_summary:
  - ""
executor_checks:
  required:
    - command_or_check: ""
      result: ""
      evidence: ""
  skipped:
    - command_or_check: ""
      reason: ""
authoritative_verification:
  required: false
  performed: false
  result: ""
  evidence: ""
verification_results:
  - ""
deviations_from_contract:
  - deviation: ""
    architect_approved_in_revised_contract: false
unresolved_items:
  - item: ""
    blocking: true
result: NEEDS_REVIEW
```

## Result values

- `CONTRACT_SATISFIED`: Executor believes the approved contract was satisfied against the exact approved base, with required Executor checks run successfully, no skipped mandatory checks, no forbidden changes, no material unapproved deviations, and only explicitly authorized git actions. This is not authoritative project PASS.
- `NEEDS_REVIEW`: Work is complete enough to review, but deviations, ambiguity, skipped checks, stale-base concerns, partial verification, unexpected files, or judgment calls require Architect attention.
- `BLOCKED`: Execution could not continue because required information, access, repository state, branch state, base HEAD, clean working state, dependencies, git action authority, or decisions were unavailable.
- `FAILED`: Execution was attempted but did not satisfy the contract, mandatory checks, invariants, or verification requirements.

## Field rules

- `contract_id`: Must match the implementation contract.
- `repository`: Actual repository where execution occurred.
- `branch`: Actual branch where execution occurred.
- `base_head`: Base commit from the contract.
- `pre_execution_head`: Actual HEAD observed before changes.
- `final_head`: Final commit after changes, or empty if no commit was produced.
- `status`: Brief execution state, such as `implemented`, `blocked`, or `failed`.
- `pre_execution_checks`: Evidence that repository, branch, base HEAD, and working state matched the contract before editing.
- `working_tree_after`: Whether uncommitted changes remain after execution.
- `changed_files`: Every changed file and whether it was inside the contract scope.
- `commits_created`: Commits created by the Executor. Empty when commit authority was not granted or no commit was produced.
- `pushed`: Whether the Executor pushed to a remote.
- `implementation_summary`: Concise description of completed work.
- `executor_checks`: Mandatory checks performed and mandatory checks skipped. A skipped required check prevents `CONTRACT_SATISFIED`.
- `authoritative_verification`: Required project verification status. If required and not performed or not passing, `CONTRACT_SATISFIED` is invalid.
- `verification_results`: Evidence from checks, tests, tunnel calls, or manual inspection.
- `deviations_from_contract`: Any difference from the approved contract, including unapproved extra changes or scope changes not made.
- `unresolved_items`: Remaining questions, blockers, risks, or follow-up needs.
- `result`: Must be one of `CONTRACT_SATISFIED`, `NEEDS_REVIEW`, `BLOCKED`, or `FAILED`.

## Invalid clean-result conditions

`CONTRACT_SATISFIED` is invalid when any of the following are true unless a revised Architect-approved contract explicitly supersedes the original:

- repository, branch, or base HEAD did not match before execution;
- the contract was internally inconsistent or stale;
- the working tree was dirty before execution;
- uncommitted changes remain after execution without contract authorization;
- a mandatory Executor check failed or was skipped;
- required authoritative verification failed, was unavailable, or was not performed;
- a changed file or component was outside the authorized scope;
- a forbidden change occurred;
- a material deviation lacked revised-contract approval;
- a blocking unresolved item remains;
- commit or push occurred without explicit `git_actions` authorization.
