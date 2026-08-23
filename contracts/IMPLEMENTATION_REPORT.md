# Implementation Report

This reusable report is the Executor-to-Architect return format for IELTS engineering work.

The report must distinguish what changed, what was verified, what deviated, and what still needs Architect review. Verification results must be factual and must not be fabricated.

## Template

```yaml
contract_id: ""
base_head: ""
final_head: ""
status: ""
pre_execution_checks:
  repository_confirmed: false
  branch_confirmed: false
  base_head_confirmed: false
  working_tree_clean: false
changed_files:
  - path: ""
    summary: ""
implementation_summary:
  - ""
tests/checks_run:
  - command_or_check: ""
    result: ""
verification_results:
  - ""
deviations_from_contract:
  - ""
unresolved_items:
  - ""
result: NEEDS_REVIEW
```

## Result values

- `CONTRACT_SATISFIED`: Executor believes the approved contract was satisfied against the exact approved base, with required Executor checks run and no material unapproved deviations. This is not authoritative project PASS.
- `NEEDS_REVIEW`: Work is complete enough to review, but deviations, ambiguity, skipped checks, stale-base concerns, or judgment calls require Architect attention.
- `BLOCKED`: Execution could not continue because required information, access, branch state, base HEAD, clean working state, dependencies, or decisions were unavailable.
- `FAILED`: Execution was attempted but did not satisfy the contract or verification requirements.

## Field rules

- `contract_id`: Must match the implementation contract.
- `base_head`: Base commit confirmed before changes.
- `final_head`: Final commit after changes, or empty if no commit was produced.
- `status`: Brief execution state, such as `implemented`, `blocked`, or `failed`.
- `pre_execution_checks`: Evidence that repository, branch, base HEAD, and working state matched the contract before editing.
- `changed_files`: Files changed by the Executor and why.
- `implementation_summary`: Concise description of completed work.
- `tests/checks_run`: Exact commands, checks, or verification calls performed and their outcomes.
- `verification_results`: Evidence from checks, tests, tunnel calls, or manual inspection.
- `deviations_from_contract`: Any difference from the approved contract, including unapproved extra changes or scope changes not made.
- `unresolved_items`: Remaining questions, blockers, risks, or follow-up needs.
- `result`: Must be one of `CONTRACT_SATISFIED`, `NEEDS_REVIEW`, `BLOCKED`, or `FAILED`.
- Material deviations, forbidden changes, skipped required checks, dirty working state, branch mismatch, or base HEAD mismatch prevent `CONTRACT_SATISFIED` unless the Architect explicitly approved the deviation in a revised contract.
