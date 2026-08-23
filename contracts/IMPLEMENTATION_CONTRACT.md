# Implementation Contract

This reusable contract is the Architect-to-Executor handoff format for IELTS engineering work.

The contract must be concise, deterministic, and explicit. Avoid prose that allows silent reinterpretation. The Executor must not execute unless `execution_ready` is exactly `true`.

## Template

```yaml
contract_id: ""
repository:
  name: ""
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
  - ""
unresolved_decisions:
  - ""
execution_ready: false
```

## Field rules

- `contract_id`: Stable identifier for the delegated task.
- `repository`: Exact repository, URL, and branch authorized for execution.
- `base_head`: Commit SHA the Executor must confirm before work.
- `objective`: Single outcome the contract authorizes.
- `authority_sources`: Canonical documents, specs, designs, issue links, or user instructions that govern the work.
- `problem_statement`: The concrete problem being solved.
- `required_changes`: Changes the Executor must make.
- `expected_files/components`: Files or components expected to change or be inspected.
- `must_preserve`: Invariants that must remain true.
- `acceptance_criteria`: Conditions required for the implementation to be considered contract-complete.
- `forbidden_changes`: Changes outside the authorized scope.
- `verification_requirements`: Tests, checks, tunnel calls, or manual inspections required before reporting.
- `unresolved_decisions`: Decisions not delegated to the Executor. If any item blocks implementation, set `execution_ready: false`.
- `execution_ready`: Must be explicit `true` or `false`. The Executor must not execute when `false`.
