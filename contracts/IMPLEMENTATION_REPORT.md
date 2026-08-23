# Implementation Report

Reusable Executor-to-Architect evidence format. It records what actually happened and keeps implementation evidence, Git state, Executor checks, Architect review, and authoritative project verification distinct.

## Template

```yaml
contract_id: ""
contract_version: 2

repository:
  full_name: ""
  url: ""
  branch:
    name: ""
    role: ""
  base_head: ""
  pre_execution_head: ""
  final_head: ""

status: ""

pre_execution_checks:
  repository_confirmed: false
  branch_confirmed: false
  base_head_confirmed: false
  working_tree_clean: false
  required_skills_available: false

skills_used:
  - name: ""
    source: ""

changed_files:
  - path: ""
    summary: ""
    in_contract_scope: false

commits_created:
  - sha: ""
    message: ""

pushed: false
promoted_to_main: false

acceptance_evidence:
  - criterion_id: AC-1
    status: NOT_PROVEN
    evidence: ""

executor_checks:
  - check_id: CHECK-1
    result: ""
    evidence: ""

authoritative_verification:
  required: false
  performed: false
  result: ""
  evidence: ""

deviations_from_contract: []
unresolved_items: []

working_tree_after:
  clean: false
  summary: ""

result: NEEDS_REVIEW
```

## Result values

- `CONTRACT_SATISFIED`: Executor evidence proves the exact approved contract was satisfied. It is not Architect acceptance and not authoritative project PASS.
- `NEEDS_REVIEW`: evidence exists, but ambiguity, deviation, missing proof, stale concerns, or judgment remains.
- `BLOCKED`: execution could not safely begin/continue because required identity, authority, state, skill, dependency, or decision was unavailable.
- `FAILED`: execution was attempted but did not satisfy scope, invariants, acceptance criteria, mandatory checks, or required verification.

## Evidence rules

Every acceptance criterion from the contract must appear by `criterion_id` with `SATISFIED`, `UNSATISFIED`, or `NOT_PROVEN` plus evidence. Any `UNSATISFIED` or `NOT_PROVEN` criterion prevents `CONTRACT_SATISFIED`.

Record every changed file, created commit, push, and main promotion. Git actions not authorized by the contract prevent a clean result.

`CONTRACT_SATISFIED` is invalid when any of these apply without a revised Architect-approved contract:

- repository, branch, or base HEAD mismatch;
- stale or internally inconsistent contract;
- required skill unavailable or not used;
- required precondition failed;
- out-of-scope or forbidden change;
- unapproved architectural reinterpretation or material deviation;
- mandatory check failed, skipped, or substituted;
- required authoritative verification absent or failing;
- blocking unresolved item remains;
- acceptance criterion is not proven satisfied;
- unauthorized branch creation, commit, push, or main promotion;
- final working-tree state violates the contract.

Git/CI success alone is not authoritative project PASS. The target project's designated verifier owns that signal.
