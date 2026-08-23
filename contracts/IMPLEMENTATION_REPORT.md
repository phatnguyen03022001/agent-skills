# Implementation Report

Reusable Executor-to-Architect evidence format.

The report records what actually happened. It must distinguish implementation evidence, git state, Executor checks, Architect review, and authoritative project verification.

## Template

```yaml
contract_id: ""
contract_version: 1
repository:
  full_name: ""
  url: ""
branch: ""
branch_role: ""
base_head: ""
pre_execution_head: ""
final_head: ""
status: ""
pre_execution_checks:
  repository_confirmed: false
  branch_confirmed: false
  base_head_confirmed: false
  working_tree_clean: false
skills_used:
  - name: ""
    source: ""
    available: false
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
promoted_to_main: false
implementation_summary:
  - ""
acceptance_evidence:
  - criterion: ""
    status: NOT_PROVEN
    evidence: ""
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
deviations_from_contract:
  - deviation: ""
    architect_approved_in_revised_contract: false
unresolved_items:
  - item: ""
    blocking: true
result: NEEDS_REVIEW
```

## Result values

- `CONTRACT_SATISFIED`: Executor evidence says the exact approved contract was satisfied. It is not Architect acceptance and not authoritative project PASS.
- `NEEDS_REVIEW`: enough work/evidence exists to review, but ambiguity, deviation, missing proof, stale concerns, or judgment remains.
- `BLOCKED`: execution could not safely begin/continue because required identity, authority, state, skill, dependency, or decision was unavailable.
- `FAILED`: execution was attempted but did not satisfy the contract, mandatory checks, invariants, or required verification.

## Evidence rules

Every acceptance criterion must be `SATISFIED`, `UNSATISFIED`, or `NOT_PROVEN` with evidence. Any `UNSATISFIED` or `NOT_PROVEN` criterion prevents `CONTRACT_SATISFIED`.

A successful verifier run is necessary evidence when required, but never proves that required changes were implemented. If the contract required mutation but `final_head == pre_execution_head`, `CONTRACT_SATISFIED` requires proof that the required state already existed and the contract allowed verification-only completion.

Record every changed file, created commit, push, and main promotion. Git actions not explicitly authorized by the contract invalidate a clean result.

## Invalid clean-result conditions

`CONTRACT_SATISFIED` is invalid when any of these are true unless a revised Architect-approved contract supersedes the original:

- repository, branch, or base HEAD mismatch;
- stale or internally inconsistent contract;
- required skill unavailable/not used;
- required clean-state precondition failed;
- changed file/component outside scope;
- forbidden change or material unapproved deviation;
- mandatory check failed, skipped, or substituted without authority;
- required authoritative verification absent/failing;
- blocking unresolved item remains;
- acceptance criterion is not proven satisfied;
- unauthorized branch creation, commit, push, or main promotion;
- uncommitted final state violates the contract.

Never report authoritative project PASS. The target project's designated verifier owns that signal.
