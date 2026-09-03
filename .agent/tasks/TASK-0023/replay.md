# GOV-E1 Historical Governance Replay

Status: Executor evidence for TASK-0023 revision 1. This artifact is historical evaluation evidence only. It does not change reusable governance semantics or target-repository authority.

## Evidence boundary

Execution authority:

- `phatnguyen03022001/agent-skills@5167e6b0d30c254cce01f03b727569a18528429e` (`dev`) — exact TASK-0023 revision-1 handoff base.
- `phatnguyen03022001/agent-skills@7107bb6786bd0e9c6663bf22efe9c76ffb8b8875` — pinned Executor, verification, simplicity, report-contract, accepted GOV-D, and paired-eval authority.
- `.agent/tasks/TASK-0022/review.yaml@7107bb6786bd0e9c6663bf22efe9c76ffb8b8875` — `ACCEPTED` GOV-D review; reviewed report commit `a38d51f6c5b62797a7cab78f5ee0d2d6f447d6b1`.
- `.agent/tasks/TASK-0019/baseline.md@5167e6b0d30c254cce01f03b727569a18528429e` — accepted GOV-A metric definitions and five-family evidence corpus.

External repositories were resolved read-only immediately before replay:

- IELTS: `phatnguyen03022001/ilets` `dev@1a33e0466a2416a7d1afcf71d604de9fdbb3f9a0`, `main@e707aeee43411cc8f99448b63220eb8beff552b6`, topology `{dev, main}`.
- SF: `phatnguyen03022001/SF` `main@3ace885f84c9c88df87ab3a0d7888b5030920f23`, topology `{main}`.

No chat history is used as historical authority.

## Accepted replay semantics

The replay applies the accepted GOV-B/C/D model without inventing a classifier:

- Architect closes WHAT, material BOUNDARY, and PROOF; Executor chooses the smallest sufficient repository-native HOW inside positive authority.
- Materiality is consequence-based. Public compatibility, trust/security, persisted-data semantics, cross-component ownership, materially new dependencies/cost/topology, and evidence-integrity consequences remain Architect-owned.
- Exact local files, internal helpers/modules, owner-local selector aids, and local companion verification surfaces are Executor-local when they stay inside the authorized material/component boundary and change no governing consequence.
- Review is evidence-first and expands only on contradiction, unexplained surfaces, weak/missing proof, deviations, material risk, regression signals, or explicit stronger assurance.
- The GOV-D paired corpus is regression evidence, not live authority. Local/generated/helper variants remain local only while their material consequences are unchanged.

## Replay A — IELTS TASK-0044 revision family

### Immutable lineage

| Historical identity | Canonical evidence | Replay significance |
| --- | --- | --- |
| Revision 1 | task at `c792761e14c7c34a5f033e1ceb0b69c876f0807c` | Initial bounded executable Listening Core/API training slice. |
| Revision 2 | `7c857adf9a275b12f06d018791617daa54bc8c4d` | Corrected generated/public-contract surface authority. |
| Revision 3 | `f81ea09ec1935c348866769b623d15bf9a6ec916` | Authorized a PM-L03 owner-local materializer selector anchor. |
| Revision 4 | `ca3a07115f677054f770c790fa2dc7439d2e8f87` | Generalized owner-local selector-aid delegation for already-bound canonical identities. |
| Candidate | `13b2577e02050c1f354017389a106da66de0872d` | Sole Listening implementation candidate; direct child of revision-4 planning base. |
| Sentinel | `6c8bc9552a55a85c62b642e4ff40cdb7d4c080f3` | Sentinel-only direct child; changes only `.github/verification-boundary/candidate` to bind the candidate. |
| Authoritative proof | GitHub Actions run `33684727585`, attempt 1 | `success`; exact-candidate bind/checkout/assert steps and `./verify` all passed. |
| Revision-4 report defect | `.agent/tasks/TASK-0044/report.yaml@ac25dd2664103a24a30b0ccbd8e5e6468ba26729` | Historical report-ID mapping defect preserved by revision 5. |
| Revision 5 | `04cc4b29246b074f2a33e83d89a665660222e9c1` | Forward authority/report-lineage closure; no implementation replay. |
| Corrected report | `898f4360edf5523c355b98651b2c98dce6866886` | Report revision 2; report-only child of revision-5 base. |
| Accepted review | review resolved at `1a33e0466a2416a7d1afcf71d604de9fdbb3f9a0` | `ACCEPTED`; explicitly preserves restrictive-authority and report-mapping defects as historical facts. |

### Consequence classification

1. **Preventable Architect HOW leakage in revision 1.** The exact one-row FTR-010 materializer anchor, exact bootstrap fixture filename, and exact Go `//go:embed` primitive are implementation-local realizations. The accepted GOV-A baseline independently classifies these three decisions as leaks. Their product/evidence constraints remain, but those mechanisms do not need Architect prescription.

2. **Legitimate material boundary remains.** The exact Listening semantic binding, attributable Ogg source and integrity evidence, authenticated learner-owned media behavior, public route/compatibility semantics, generated public-contract consistency, persisted Academic/General Training variant semantics, deterministic completion scoring, TRAINING-only Observation consequence, and no-EvidenceFact boundary remain material. They are not reclassified as local to reduce revision count.

3. **Revision 2 remains.** Its historical cause is a generated/public-contract authority correction. Generated consumer and contract derivation are materially tied to the new public interface and reproducible contract evidence. Under TASK-0023's deletion rule, this is not a local-HOW-only revision and therefore remains in the counterfactual lineage.

4. **Revision 3 disappears.** Its sole new authority permits an owner-local PM-L03 selector anchor because the existing materializer could not uniquely select an already-canonical identity. The revision itself states the change affects machine resolvability only, not product meaning or semantic ownership. Under GOV-B/D this is local implementation/companion work inside the already-authorized canonical owner.

5. **Revision 4 disappears.** It generalizes the same owner-local selector-aid discretion to other already-bound identities and explicitly calls machine resolvability implementation design. No material product, trust, data, public-contract, or ownership consequence is added.

6. **Revision 4 restrictive-file noncompliance becomes preventable, not retroactively compliant.** The candidate changed `tools/canonical/test_materialize.py`, `tools/contracts/test_generate.py`, and `tools/contracts/validate.go` outside the old restrictive allowlist. Canonical revision-5 review confirms they are bounded existing verification companions: canonical-ID expectation, generated public-operation expectation, and exact public-route audit. GOV-B would allow these local companions under the already-positive material boundaries and require them to be reported; it does not rewrite the historical revision-4 violation.

7. **Revision 5 disappears as a task revision, while evidence correction remains.** Its two causes are the old exact-file authority coupling above and a reconstructable report-ID mapping defect. GOV-B removes the former as a revision trigger; GOV-C permits the latter to be corrected as evidence without inventing new material task authority. A corrected report and review check still remain required. The historical revision-5 closure remains valid history and is not rewritten.

8. **Material review depth remains.** TASK-0044 has real triggers: public API, learner ownership/trust, persisted data semantics, external-source integrity, a historical authority contradiction, and authoritative remote verification. GOV-C does not justify a shallow preference-only review here. Candidate/sentinel/run reconstruction remains legitimate when needed to prove those triggers.

9. **No verifier/stale/new-truth deletion claim.** The authoritative run passed. The replay found no TASK-0044 revision whose canonical sole cause was verifier failure, stale execution state, or newly discovered target truth. Those categories remain material gates if encountered; absence here is not generalized into a rule.

### Smallest sufficient counterfactual material boundary

A single initial implementation task should have fixed only: the canonical Listening identities and learner-visible semantics; attributable/integrity-bound media content; authenticated learner-owned media public contract; Academic/General Training persisted applicability; deterministic completion scoring; TRAINING Observation-only consequence; generated public-contract consistency; preservation of Reading; forbidden Assessment/Progression/Planner/provider/storage expansion; and exact acceptance/proof requirements. Executor would resolve owner-local selectors, internal filenames/modules, byte-embedding primitive, and same-boundary verification companions from repository truth.

Under the historical deletion rule, the counterfactual lineage retains **revision 1 and revision 2**, removes **revision 3 and revision 4**, and removes **revision 5 as a task revision** while retaining the corrected report/review evidence. This reduction does not classify any public/trust/data/ownership consequence as local.

## Replay B — SF TASK-0002 clean bounded lineage

### Immutable lineage

- Current canonical target: `phatnguyen03022001/SF@3ace885f84c9c88df87ab3a0d7888b5030920f23`, topology `{main}`.
- Authorized base: `6ff17cd216b89f95e224aa5957426ec61536d7b4`.
- TASK-0002 revision 1 candidate: `a185917b5ce51157c8229936f2d2550aa145e058`.
- Report-only child: `b2d07bc5c30d148eca9045126f2f2428e34738cd`.
- Current accepted review resolves that exact report and candidate lineage with no gaps, deviations, runtime, CI, taxonomy expansion, or unrelated product path.

### Consequence classification

The material objective is one canonical learning/tutoring owner plus README routing while preserving the existing authority order, decision/policy/outcomes owners, zero-runtime posture, main-only Git consequence, and no taxonomy/runtime expansion. The sole-owner and universal-entrypoint boundaries are real ownership consequences, not local formatting preference.

The historical implementation is one revision and two product paths with no discovered authority miss. There is no canonical evidence of a preventable revision event. Under GOV-B, local prose layout and internal document composition remain Executor HOW, but no historical task revision disappears because none was caused by those choices.

GOV-C would keep review compact: exact task/base/candidate/report identity, two-path diff, semantic-owner/routing acceptance, protected-owner preservation, and final topology are sufficient. The accepted review already behaves this way; no deep implementation reconstruction is required or removed.

### Smallest sufficient counterfactual material boundary

Create one focused learning/tutoring authority that implements the approved learning semantics and is discoverable from the universal entrypoint; preserve all existing higher-precedence case/decision/policy/outcome authority, taxonomy non-ownership for this task, zero-runtime operation, and main-only repository consequence. Proof needs exact candidate lineage, semantic inspection, protected-owner preservation, and topology. No implementation-format prescription is needed.

Historical revision 1 remains. No revision disappears.

## GOV-A metric replay

Only accepted GOV-A formulas with defensible canonical numerator and denominator are emitted. No percentage is estimated from incomplete evidence.

| Metric | Numerator / denominator | Result | Evidence status |
| --- | --- | --- | --- |
| Architect HOW leakage rate | 3 unjustified implementation-local decisions / 15 counted Architect HOW decisions | **20.0%** | Defensible: all 15 baseline decisions are classified; the three leaks are the TASK-0044 anchor-row, fixture-filename, and Go-embed prescriptions. |
| Authority miss rate | 2 confirmed miss families / 5 assessed families, with 1 family still canonically UNKNOWN | **UNKNOWN** | Full numerator is not defensible because `agent-skills/TASK-0015` lacks sufficient pre-execution operator-intent evidence. No floor percentage is promoted to a rate here. |
| Unnecessary revision rate | 2 canonical local-mechanics-only revision events / 5 assessed executed families | **40.0%** | Defensible under the accepted GOV-A baseline: the two counted events are TASK-0044 revision 2→3 and revision 3→4. This metric is not silently expanded to include evidence-ceremony corrections. |
| Review replay rate | 0 untriggered deep-reconstruction reviews / 5 accepted reviews | **0.0%** | Defensible: all five accepted baseline reviews are classified; deep TASK-0044/SF-TASK-0001 replay had material triggers. |

No new counterfactual percentage is created from the two replayed lineages because TASK-0023 does not have a canonical denominator for such a new metric.

## GOV-E2 pilot candidates from fresh target truth

These are pilot selections only. They create no task and prescribe no implementation HOW.

### IELTS pilot — one bounded PM-L02 Gist Sprint TRAINING slice

**Objective:** Materialize one executable instance of the already-canonical `PM-L02` Gist Sprint behavior so GOV-E2 can observe whether Executor chooses local realization without Architect HOW leakage.

**Material boundary:** Preserve the current canonical Listening ownership and shared Academic/General Training meaning; preserve existing learner authentication/ownership, data semantics, TRAINING-versus-evidence separation, and existing public-contract consequences. Do not introduce or change a public API contract, storage/provider boundary, persistence model, Assessment/Evidence admission, Planner/Progression consequence, or cross-component ownership. Any such consequence requires Architect escalation.

**Proof intent:** Prove the exact canonical identity and owner are used, the bounded learner behavior is executable for its authorized target variants, TRAINING produces only its authorized observation consequence, existing PM-L03 and Reading behavior remain unchanged, and the exact candidate/report evidence exposes any local companion surfaces without treating them as automatic revision triggers.

Fresh-target basis: at IELTS `dev@1a33e0466a2416a7d1afcf71d604de9fdbb3f9a0`, canonical practice authority lists `PM-L01` through `PM-L06`; the current canonical source map materializes `PM-L03` but not `PM-L02`.

### SF pilot — one contextual lesson for existing L3 `05.03.03 Change Authorization`

**Objective:** Exercise the existing Learn → Apply → Decide → Defend learning model on one contextual lesson for the already-canonical L3 topic `05.03.03 Change Authorization`.

**Material boundary:** Keep L1–L3 taxonomy identity unchanged; keep L4+ detail contextual rather than a new durable taxonomy owner; preserve README authority precedence, decision-engine rules, case-state/policy/outcomes ownership, zero-runtime posture, and main-only Git consequence. Do not add learner state, runtime, a new canonical owner, or a new taxonomy level/identity.

**Proof intent:** Prove the lesson remains subordinate to current case facts and decision authority, uses the existing L3 identity without mutating taxonomy semantics, introduces no persistent learning machinery or ownership split, and leaves protected canonical owners unchanged except where the final authorized task boundary explicitly requires a material change.

Fresh-target basis: SF `main@3ace885f84c9c88df87ab3a0d7888b5030920f23` defines `docs/learning-model.md` as the learning owner, `docs/taxonomy.md` as the durable L1–L3 owner, and explicitly keeps L4+ dynamic/contextual.

## Replay conclusion

The historical evidence supports the accepted redesign without weakening material governance: TASK-0044 contains three confirmed Architect HOW leaks and two selector-authority revisions that GOV-B removes; its public/trust/data/integrity consequences and remote verifier proof remain governed; its old restrictive companion-file defect would be reportable local work rather than a revision trigger; and its report-mapping correction need not become a new material task. SF TASK-0002 remains a one-revision control showing that sparse material boundaries still govern a simple main-only repository.
