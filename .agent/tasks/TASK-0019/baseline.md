# GOV-A Decision-Surface Baseline

Status: Executor baseline evidence for TASK-0019 revision 1. This document is audit evidence only; it defines no reusable governance semantics.

## Resolved evidence boundary

Audit target: `phatnguyen03022001/agent-skills@79d556edfd6f9d33828e5caf675d95976e98eede` on `dev`.
Pinned agent-skills authority: `phatnguyen03022001/agent-skills@76f2d3877d1698f91eb5a6117e2301ed49480379`.
Read-only external refs resolved for this audit:

- `phatnguyen03022001/ilets` `dev@1a33e0466a2416a7d1afcf71d604de9fdbb3f9a0`.
- `phatnguyen03022001/SF` `main@a4695c9ad3a994a1e7e9ae76cc7c1c0954bb35cd`.

The corpus contains exactly five task families across three repositories. No external repository was mutated.

| Specimen | Exact task / report / review evidence | Required coverage supplied |
| --- | --- | --- |
| `ilets/TASK-0044` | revision 4 task `ca3a07115f677054f770c790fa2dc7439d2e8f87`; revision 5 task `04cc4b29246b074f2a33e83d89a665660222e9c1`; candidate `13b2577e02050c1f354017389a106da66de0872d`; sentinel `6c8bc9552a55a85c62b642e4ff40cdb7d4c080f3`; authoritative Actions run `33684727585`; report revision 2 commit `898f4360edf5523c355b98651b2c98dce6866886`; accepted review resolved at `1a33e0466a2416a7d1afcf71d604de9fdbb3f9a0` | bounded success; generated-contract/generated-companion work; data/migration work; security/ownership trust boundary; authoritative remote verification; authority and revision regression specimen |
| `SF/TASK-0001` | revision 1 task `7bb5ec1cfcea50f528887c98ce20450ac0a8663e`; revision 2 task `d11533417bd25bbc7e4d017add25e84c0baaf8f3`; revision 3 task resolved at `a4695c9ad3a994a1e7e9ae76cc7c1c0954bb35cd`; report revision 2 commit `1cf11bb2b9b2f7a0cd44b1fa379d06729b41f12d`; accepted review resolved at `a4695c9ad3a994a1e7e9ae76cc7c1c0954bb35cd` | equivalent missing-authority stop; Git-authority regression; no authoritative remote CI |
| `SF/TASK-0002` | revision 1 task resolved at `a4695c9ad3a994a1e7e9ae76cc7c1c0954bb35cd`; candidate `a185917b5ce51157c8229936f2d2550aa145e058`; report commit `b2d07bc5c30d148eca9045126f2f2428e34738cd`; accepted review resolved at `a4695c9ad3a994a1e7e9ae76cc7c1c0954bb35cd` | normal bounded documentation-only success; no authoritative remote CI |
| `SF/TASK-0003` | revision 1 task resolved at `a4695c9ad3a994a1e7e9ae76cc7c1c0954bb35cd`; candidate `710cc8303a15f23aa679ec3dba367b901c5800e3`; report commit `ee50218b8294291b124bb5fb96683f16c7235677`; accepted review resolved at `a4695c9ad3a994a1e7e9ae76cc7c1c0954bb35cd` | normal bounded documentation-only success; no authoritative remote CI |
| `agent-skills/TASK-0015` | revision 3 task/report/review resolved at `76f2d3877d1698f91eb5a6117e2301ed49480379`; candidate `a9be7b8e08ae2a83f6d01d38d811f6a0698f0d64`; report commit `72cf828ec7fd35e5b21af96a51b1b8c4c45fdc6f`; historical revision-1 review `017bf822708c4fff813478c6dffdc5c8e26821d6` | reusable-governance success; revision caused by material governance semantics rather than local mechanics; no authoritative remote CI |

`SF/TASK-0001` revision 1 is the missing-authority stop specimen: it was `DRAFT`, had `structure_authority.status: UNRESOLVED`, required explicit persisted-design approval, and had `execution_ready: false`. That stop itself is correct behavior and is not counted as an authority miss.

## Counting rule

A distinct Architect task decision is counted here only when an approved task mandates a concrete implementation mechanism or representation beyond the required externally observable outcome. Outcome/product semantics, artifact-owner naming alone, capability/Git gates, negative scope boundaries, acceptance criteria, verification commands, and repeated invariants are excluded. If one scope item contains independent concrete mechanisms, they are counted separately.

Each counted decision is classified as:

- **JUSTIFIED** when the mechanism itself has a consequence-backed authority reason involving public compatibility, data ownership/compatibility, security or trust boundary, evidence reproducibility/integrity, or reusable governance semantics.
- **LEAK** when the task hard-codes an implementation-local mechanism although the same material outcome could remain authority-correct with an Executor-local choice.

### Counted Architect HOW decisions

| ID | Specimen / exact evidence | Counted mechanism decision | Classification | Consequence-based rationale |
| --- | --- | --- | --- | --- |
| H01 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Require a dedicated FTR-010 materializer anchor containing exactly one L-F04 Markdown-table row | **LEAK** | The same task's structure rationale states machine-resolvability is implementation design and permits an owner-local anchor or equivalent non-semantic selector aid. Exact Markdown-row construction is therefore local HOW, not semantic authority. |
| H02 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Use a bounded slice descriptor and generated trace for the Listening canonical binding | **JUSTIFIED** | The repository already uses the accepted multi-slice canonical materialization/trace mechanism; deterministic canonical-source evidence is the consequence, not style preference. |
| H03 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Hard-code the bootstrap fixture file path `services/core-api/internal/bootstrap/listening-training-001.json` | **LEAK** | Content/revision identity is material; this exact repository-local filename is not shown to change product, compatibility, ownership, security, or verification meaning. |
| H04 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Vendor the exact Wikimedia/VOA Ogg source rather than substitute generated or unrelated audio | **JUSTIFIED** | Source identity, rights basis, and attributable assessment content are material supply/evidence facts. |
| H05 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Bind byte length and SHA-256 and verify embedded bytes deterministically | **JUSTIFIED** | Integrity and reproducible external-source evidence are material assurance properties. |
| H06 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Require Go `//go:embed` as the exact byte-delivery mechanism | **LEAK** | Exact owned bytes and absence of external media infrastructure are material; the language-level embedding primitive is implementation-local once those boundaries hold. |
| H07 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Fix the authenticated public media GET route, opaque reference semantics, and 401/404 behavior | **JUSTIFIED** | This is a public compatibility and learner-ownership trust boundary. |
| H08 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Regenerate repository-native public Go and TypeScript bindings from the OpenAPI | **JUSTIFIED** | Generated consumers are repository-owned companions of the public machine contract; divergence would break exact contract evidence. |
| H09 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Widen persisted `practice_activities.test_variant` only to existing Academic/General Training values and store the resolved variant | **JUSTIFIED** | Persisted variant ownership and compatibility are material data semantics; inventing `SHARED` would change the model. |
| H10 | `ilets/TASK-0044` rev4 task @ `ca3a071...` | Use trim plus case-insensitive exact completion scoring and forbid fuzzy/generalized marking | **JUSTIFIED** | Scoring behavior is learner-visible product semantics and affects assessment/training correctness. |
| H11 | `SF/TASK-0003` rev1 task @ `a4695c9...` | Require exactly three durable L3 topics under each fixed L2 | **JUSTIFIED** | The approved taxonomy contract intentionally fixes the durable 12/48/144 knowledge-map shape; changing this changes canonical content structure. |
| H12 | `SF/TASK-0003` rev1 task @ `a4695c9...` | Use stable complete IDs `01.01.01` through `12.04.03` | **JUSTIFIED** | Stable referential identity is material to a durable canonical taxonomy used by agents and later references. |
| H13 | `SF/TASK-0003` rev1 task @ `a4695c9...` | Render every L3 as `ID — Name — one-line scope` | **JUSTIFIED** | The bounded representation is part of the approved durable content contract and constrains L4 leakage; no alternative representation authority was delegated in this task. |
| H14 | `agent-skills/TASK-0015` rev3 task @ `76f2d387...` | Capture start after exact binding and immediately before capability preflight, then terminal time before report publication | **JUSTIFIED** | These boundaries define what Executor processing time means and prevent queue/approval latency from contaminating reusable telemetry semantics. |
| H15 | `agent-skills/TASK-0015` rev3 task @ `76f2d387...` | Keep `operational_timing` exactly two RFC-3339 UTC fields and derive, rather than store, elapsed duration | **JUSTIFIED** | This is reusable protocol/report compatibility and non-authoritative-telemetry semantics, not target implementation detail. |

`SF/TASK-0001` revision 3 and `SF/TASK-0002` contain no decision meeting this HOW-count rule; their concrete path ownership is the authorized output structure rather than an implementation mechanism beneath it.

## Primary metrics

### 1. Architect HOW leakage rate

Formula: unjustified implementation-local Architect decisions / total counted Architect task decisions.

Result: **3 / 15 = 20.0%**. Evidence coverage: **15/15 classified, 0 UNKNOWN**.

All three confirmed leaks are in `ilets/TASK-0044` revision 4 and concern repository-local realization beneath already-fixed semantics: exact Markdown selector construction, exact fixture filename, and exact Go embedding primitive. The same task correctly keeps public route, data variant, scoring, provenance, and generated-contract mechanisms Architect-owned because their consequences are material.

### 2. Authority miss rate

Formula: executed task families with at least one preventable unclosed material-authority discovery / executed task families assessed.

Confirmed numerator families:

1. **`ilets/TASK-0044`: YES.** Revision 4's restrictive allowlist omitted `tools/canonical/test_materialize.py`, `tools/contracts/test_generate.py`, and `tools/contracts/validate.go`, although its candidate changed all three. The revision-4 base already contained these repository-native authority/verification companions: `test_materialize.py@ca3a071...` owns the exact global registry expectation; `test_generate.py@ca3a071...` owns the exact generated public operation set; `validate.go@ca3a071...` owns the exact public route audit. Revision 5 and its accepted review preserve this as historical non-compliance. This was therefore discoverable before execution rather than newly created target truth.
2. **`SF/TASK-0001`: YES.** Revision 2 was executable with `promote_to_main: false` while the implementation nevertheless moved canonical `main`; report/review revision 2 preserve `GAP-GIT-AUTHORITY`. The task's own pre-execution Git authority was sufficient to close the decision.

Other families:

- `SF/TASK-0002`: **NO confirmed miss**; report/review show bounded execution with no discovered gaps.
- `SF/TASK-0003`: **NO confirmed miss**; report/review show bounded execution with no discovered gaps.
- `agent-skills/TASK-0015`: **UNKNOWN** for this metric. Revision-1 review proves the forward timing-capture behavior was missing, but the pre-execution canonical repository evidence does not independently prove the full operator intent later cited by revision 3. It is not silently converted to a miss or zero.

Result: **2 / 5 = 40.0% confirmed floor**, with evidence coverage **4/5 classification-known** and **1 UNKNOWN**. If the UNKNOWN family were later proven to be a preventable authority miss, the bounded rate would be **3/5 = 60.0%**.

### 3. Unnecessary revision rate

Formula: task revision events caused only by local implementation mechanics / executed task families assessed.

Confirmed local-mechanics revision events: **2**, both in `ilets/TASK-0044`.

- Revision 2 -> 3 (`f81ea09...`) added permission for an owner-local PM-L03 selector anchor because the current materializer's broad parsed section could not uniquely select the already-canonical identity.
- Revision 3 -> 4 (`ca3a071...`) generalized the same delegation to any already-bound identity and explicitly states that machine-resolvability is implementation design, permitting the smallest owner-local anchor or equivalent non-semantic selector aid.

These events changed no product identity, ownership, public contract, scoring, security, or data semantics; they existed to authorize local selector mechanics. Revision 1 -> 2 generated-surface correction is not counted because generated companion authority is part of reproducible public-contract evidence. `SF/TASK-0001` revisions are authority corrections, and `agent-skills/TASK-0015` revisions change reusable governance semantics, so neither is local-mechanics-only.

Result: **2 / 5 = 40.0% revision events per assessed executed family**. Evidence coverage: **5/5 families, 0 UNKNOWN**.

### 4. Review replay rate

Formula: reviews requiring deep implementation reconstruction without a material evidence/risk trigger / reviews assessed.

Review set: the accepted terminal review for each of the five corpus families.

- `ilets/TASK-0044`: deep candidate/sentinel/Actions reconstruction occurred, but a material trigger existed: historical restrictive-authority non-compliance plus generated-contract, data, security/ownership, and immutable remote-proof obligations.
- `SF/TASK-0001`: historical implementation reconstruction occurred, but a material Git-authority defect required it.
- `SF/TASK-0002`: bounded two-file documentation diff; no deep implementation reconstruction.
- `SF/TASK-0003`: direct canonical-content/structure acceptance review; no implementation reconstruction beyond the accepted taxonomy evidence.
- `agent-skills/TASK-0015`: bounded three-surface reusable-semantics review; no deep target-implementation reconstruction.

Result: **0 / 5 = 0.0%**. Evidence coverage: **5/5 reviews, 0 UNKNOWN**.

This zero does not justify removing review evidence. The sample instead shows that deep replay is useful when a material authority/risk trigger exists and avoidable when the report already exposes sufficient bounded evidence.

## Observed GOV-B pressure points

1. **Restrictive scope should not require the Architect to predict every repository-local companion mutation.** `TASK-0044` shows that exact-file allowlists can miss pre-existing generated/canonical verification companions even when product/public/data semantics are already closed. GOV-B needs to preserve material semantic boundaries while reducing authority coupling to implementation-local companion discovery.
2. **Non-semantic implementation mechanics need a safer default delegation path.** Two `TASK-0044` revisions existed only to authorize selector aids that revision 4 itself calls implementation design. GOV-B should avoid forcing task revision when a local mechanism preserves already-fixed owners, semantics, contracts, risks, and verification obligations.
3. **Material authority gates must remain explicit and fail closed.** `SF/TASK-0001` revision 1 correctly stopped with unresolved structure authority; revision 2's `promote_to_main: false` violation demonstrates that Git consequence authority is not ceremony and must not be weakened by sparsification.
4. **Review depth should remain trigger-driven.** The corpus shows no confirmed untriggered deep replay. GOV-B should retain deep reconstruction for material authority/security/data/generated-proof defects while allowing evidence-complete low-risk work to stay shallow.

These are observed pressure points only. This baseline does not design sparse task semantics, change report/review schemas, create a new role or lifecycle, or alter any reusable governance surface.