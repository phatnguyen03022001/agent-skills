# Architect Deferred Observations Design

Date: 2026-08-26
Status: APPROVED DESIGN

## Problem

Two governance gaps were reproduced during current Architect work:

1. While work is bound to repository A, the Architect may discover a material issue in repository B. Switching immediately creates context noise and risks carrying authority across repository boundaries, but relying on chat memory risks losing the finding.
2. Reusable source-structure and naming defaults already exist in `simplicity`, but a fresh Architect may not load that skill when structural planning is material, so the defaults can be missed before `structure_authority` is resolved.

The solution must preserve the existing one-active-target model, repository-local authority, GitHub as canonical target truth, and the closed skill taxonomy.

## Design principles

- Deferred observations are memory aids only. They are not tasks, findings with current validity, execution authority, review evidence, lifecycle state, or cross-repository authority.
- Target-repository truth remains authoritative only after the Architect explicitly binds that repository and refreshes current GitHub state.
- The observation mechanism must not become a queue, workflow engine, shared task registry, database, scheduler, or automatic repo switcher.
- Reusable source-structure rules remain owned by `simplicity`; Architect only owns routing and judgment.
- No source-depth or naming rule is duplicated into `architect`.

## Deferred observation lifecycle

When the Architect is actively bound to repository A and notices a potentially material issue concerning repository B:

1. Do not switch the active target merely to investigate or fix it.
2. If an explicitly configured operator-profile observation store is writable, record a minimal non-authoritative deferred observation there.
3. Continue and close the current repository-A phase normally.
4. Later, when the observation is selected for action, explicitly bind repository B using the normal repository-switch rules.
5. Refresh canonical GitHub truth for B before relying on the observation.
6. Revalidate the observation against current truth.
7. If stale, immaterial, already fixed, or intentionally accepted, discard it without creating a task.
8. If still material, create or revise normal repository-local authority and execute through the existing protocol.
9. When no unresolved observations remain for B, delete the operator-profile observation file rather than keeping an empty file. Git history retains historical trace.

Observation recording does not grant mutation authority in repository B and does not make the operator-profile repository the active target. It is a narrowly scoped write to optional operator context, distinct from target-repository authority. If no writable observation store exists, the Architect must not invent one or mutate another target repository as a substitute.

## Operator-profile storage contract

Reusable governance does not hard-code a profile repository or path. An operator profile may opt into an observation store.

For the current operator profile, the intended presentation is:

```text
debt/
  <owner>__<repo>.md
```

Each file contains only unresolved observations for that exact repository. Keep entries minimal and human-readable. Recommended fields are:

```text
## <short observation>
Observed: <date or exact source context>
Target: owner/repo
Evidence: <bounded pointer or concise reproduced symptom>
Revisit: <what must be checked when the repo is explicitly bound>
```

Do not add priority scores, assignees, workflow status, percentages, dependency graphs, automatic ordering, or lifecycle state. The file is deleted when its final unresolved observation is closed or discarded.

## Structural routing trigger

`architect` gains one explicit routing rule:

When planning materially introduces, moves, splits, nests, or renames source directories/modules/packages, or when source naming conventions are material to `structure_authority`, load `simplicity` before resolving `structure_authority` unless target-repository authority has already fully resolved the structural question.

Responsibilities remain separated:

- `simplicity`: owns reusable source-depth and language naming defaults.
- Architect: recognizes structural relevance, loads `simplicity`, resolves `structure_authority`, encodes task-specific constraints, and owns final review judgment.
- Executor: applies the exact task/skills/structure authority, reports any necessary justified deviation, and does not redefine reusable policy.

This trigger must not cause `simplicity` to be loaded for unrelated work and must not turn preferred depth guidance into mechanical lint or a mandatory refactor of existing deeper structures.

## Repository integration

Implementation is sequential and repository-local:

1. `phatnguyen03022001/agent-skills`
   - update `architect/SKILL.md` with the deferred-observation semantics and structural routing trigger;
   - update protocol text only if needed to make the operator-profile observation write explicitly non-authoritative without weakening repository-binding rules;
   - do not duplicate `simplicity` depth/naming values.

2. `phatnguyen03022001/architect-profile`
   - document the operator-specific `debt/<owner>__<repo>.md` convention;
   - create no empty debt file merely to materialize the directory;
   - actual debt files exist only while unresolved observations exist.

`agent-runtime`, `agent-documents`, and `agent-standards` require no change for this design.

## Non-goals

- No new skill.
- No new organizational role.
- No cross-repository task object.
- No automatic repository switching.
- No automatic debt execution.
- No GitHub issue mirroring.
- No database, queue, scheduler, dashboard, or orchestration layer.
- No duplication of source-depth or language naming values outside `simplicity`.
- No requirement to refactor existing repositories solely because they exceed preferred source depth.

## Acceptance criteria

The implementation is acceptable when:

1. A fresh Architect encountering a material structural change has an explicit route to load `simplicity` before `structure_authority` is finalized.
2. A deferred observation about repository B can be recorded without granting authority over B or interrupting active work on repository A.
3. Reopening B requires normal explicit binding and fresh GitHub truth before the observation can influence action.
4. Resolved/stale observations are removed; no empty debt files are retained.
5. The `simplicity` skill remains the single reusable owner of source-depth and naming defaults.
6. No new task framework, queue, role, skill, or cross-repository authority is introduced.
