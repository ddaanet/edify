# Recall Artifact Lifecycle: Grounding Report

**Grounding:** Moderate — HL7 CRMI (knowledge artifact lifecycle) + LangGraph (accumulator) + OpenLineage (per-stage facets). No single framework covers the full combination; synthesis adapts three.

**Research question:** What established frameworks exist for managing shared artifacts progressively refined across pipeline stages?

**Branch artifacts:**
- Internal: `plans/reports/recall-lifecycle-internal-codebase.md`
- External: `plans/reports/recall-lifecycle-external-research.md`

---

## Framework Mapping

| Internal Pattern | External Framework | Mapping |
|---|---|---|
| Progressive augmentation (A.1→C.1→0.5→0.75) | LangGraph reducer (non-destructive append) | Tight — both append-only shared state |
| Consumer-specific curation (/inline Phase 3) | Google ADK scope tiering | Tight — plan-scoped primary, consumer-scoped subsets |
| D+B gate anchors (when-resolve.py null) | HL7 CRMI forward-only state machine | Moderate — both prevent regression |
| recall-diff.sh (mtime comparison) | PROV-DM + SLSA provenance attestation | Moderate — temporal staleness detection |
| **GAP:** No per-stage annotations | OpenLineage facets | Gap — no internal equivalent |
| **GAP:** Rejection-direction loss at C.1 | PROV-DM invalidation events | Gap — removals untracked |

---

## Grounded Patterns

### Pattern 1: Accumulator with Stage Provenance

**General principle (LangGraph + OpenLineage):** Shared state objects in multi-stage pipelines should accumulate non-destructively, with each stage's contribution tagged for auditability. The accumulator pattern prevents write conflicts between stages; stage tagging enables downstream consumers to understand provenance without querying the pipeline.

**Project instance:** recall-artifact.md entries tagged with originating stage (`[req]`, `[des:A.1]`, `[des:A.2.5]`, `[run:0.5]`). Tags are debugging metadata, not consumption filters — all entries batch-resolved regardless of source.

**Practical constraint:** Tags add ~5 chars per entry. Acceptable given the artifact is already sparse (trigger phrase + 1-line relevance note).

### Pattern 2: Forward-Only Refinement with Annotated Removal

**General principle (HL7 CRMI):** Knowledge artifacts in active use should not regress to earlier states. Modification creates a new version or annotated update, not silent mutation. Active → Draft transition is forbidden; refinement is additive or annotated.

**Project instance:** recall-diff at C.1 and 0.75 currently removes entries for rejected approaches silently. Grounded alternative: annotate rather than delete (`~~trigger phrase~~ — removed:C.1, approach rejected`). Downstream consumers skip struck entries; audit trail preserved.

**Adaptation from CRMI:** Full semantic versioning (major.minor.patch) exceeds what per-plan artifacts need. A generation timestamp in artifact header (`generated: 2026-02-28T14:30`) + last-modified stage marker (`last_modified_by: /runbook Phase 0.75`) is sufficient for staleness detection.

### Pattern 3: Lifecycle Role Contract

**General principle (RUP + TOGAF):** Each pipeline stage should have a defined role (CREATE / AUGMENT / CONSUME / CURATE) with respect to shared artifacts. The role contract is documented and enforceable — stages cannot exceed their role (a CONSUME-only stage cannot modify the artifact).

**Project instance:**

| Stage | Role | Behavior |
|---|---|---|
| /requirements | CREATE | Initial seed from /recall all. Optional — downstream creates if absent. |
| /design | CREATE or AUGMENT | A.1 creates if absent. A.2.5 appends post-explore. C.1 refines via recall-diff. |
| /runbook | AUGMENT or CREATE | Phase 0.5 adds planning entries. Phase 0.75 refines. Creates from scratch if absent. |
| /inline | CONSUME + CURATE | Phase 2.3 loads. Phase 3 creates consumer-specific variants. No primary artifact modification. |
| /orchestrate | PASS-THROUGH | Passes to checkpoint correctors. No creation or modification. |
| /deliverable-review | CONSUME (optional) | Lightweight fallback. No modification. |

**Enforcement note:** Role contract is a convention, not mechanically enforced. Enforcement would require a script that validates artifact modification against expected stage role — feasible but not prioritized.

---

## Adaptations

**Excluded from external frameworks:**
- CRMI's formal governance review gates — automated pipeline doesn't have human review between lifecycle states
- CRMI's semantic versioning — per-plan artifacts are ephemeral; version tracking adds overhead without value
- TOGAF's Architecture Repository — centralized store pattern doesn't apply; recall artifacts are plan-scoped files
- RTM bidirectional traceability — backward query ("which executions loaded this entry?") deferred; forward-only sufficient for current needs
- SLSA cryptographic provenance — supply chain integrity not a concern for internal knowledge artifacts

**Project-specific additions (no external source):**
- Consumer-specific curation pattern: Parent does cognitive selection, child does mechanical resolution. No framework addresses delegation of knowledge artifacts to context-isolated autonomous agents.
- Null mode handling: `when-resolve.py null` as gate anchor for negative paths. No framework addresses "artifact deliberately empty" vs "artifact missing."
- D+B gate pattern: Tool-call anchoring prevents skip rationalization. Specific to LLM agent failure modes — no external coverage.

---

## Three-Tier Recall Model (Discussion Context)

The grounding validates the three-tier model proposed in the discussion:

| Tier | Recall Mode | Stage | Grounded Pattern |
|---|---|---|---|
| Pipeline skills | Broad (whole files) | /requirements, /design, /runbook, /inline | Accumulator — these stages CREATE/AUGMENT (Pattern 1 + 3) |
| Sub-agents | Artifact-scoped (curated subset) | test-driver, corrector, skill-reviewer | Consumer curation — ADK scope tiering (Pattern 3 CURATE role) |
| In-process reactions | Targeted (specific entries) | PostToolUse/PreToolUse hooks | Outside artifact lifecycle — structural injection bypasses recall |

The three tiers map onto the lifecycle role contract: Tier 1 stages have write access (CREATE/AUGMENT), Tier 2 consumers have read-only access to curated subsets, Tier 3 bypasses the artifact entirely.

---

## Remaining Gaps

1. **Stage provenance not implemented** — entries lack source-stage tags (Pattern 1 convention defined but not codified in any skill)
2. **Rejection tracking not implemented** — recall-diff silently removes entries (Pattern 2 annotated removal defined but not codified)
3. **Lifecycle role contract not documented** — implicit in skill code (Pattern 3 table derived from Branch A inventory but not in any production artifact)
4. **Staleness gate not implemented** — sentinel-based detection proposed in session.md but not built (mtime comparison mechanism grounded in PROV-DM)

---

## Sources

**Primary (framework originators):**
- [HL7 CRMI Artifact Lifecycle](https://build.fhir.org/ig/HL7/crmi-ig/artifact-lifecycle.html) — knowledge artifact state machine (Draft/Active/Retired)
- [W3C PROV-DM](https://www.w3.org/TR/prov-dm/) — provenance vocabulary (generation, usage, derivation, invalidation)
- [OpenLineage](https://openlineage.io/docs/) — per-stage metadata facets
- [Google ADK Artifacts](https://google.github.io/adk-docs/artifacts/) — scope tiering, automatic versioning, handle pattern
- [LangGraph](https://blog.langchain.com/langgraph-multi-agent-workflows/) — reducer-based shared state accumulation

**Secondary (structural inspiration, limited applicability):**
- [TOGAF ADM](https://togaf.visual-paradigm.com/2023/10/10/architectural-artifacts-in-togaf-adm-a-comprehensive-overview/) — Architecture Repository pattern, continuous requirements
- [RUP](https://en.wikipedia.org/wiki/Rational_unified_process) — multi-phase artifact refinement, discipline ownership
- [SLSA](https://slsa.dev/) — provenance attestation structure
- [RTM](https://www.testrail.com/blog/requirements-traceability-matrix/) — bidirectional traceability concept
- [Harness DevOps](https://www.harness.io/harness-devops-academy/artifact-lifecycle-management-strategies) — CI/CD promotion model, retention policies

---

## Per-Point Retrieval Mode Assignment

**Decision criterion:** Does the recall point need connective tissue between entries (→ per-file), or specific decisions by trigger (→ per-key)? Equivalently: does the agent know its triggers upfront (per-key) or is it discovering what's relevant (per-file)?

**Mechanical note:** Both modes cost one tool call per pass. Per-key = one Bash (`when-resolve.py` batch). Per-file = one parallel Read batch. No tool-call-count advantage either way.

| Recall Point | Stage | Mode | Rationale |
|---|---|---|---|
| Triage recall | /design Phase 0 | per-key | Specific triggers known: "when behavioral code", "when complexity", domain keywords |
| Documentation checkpoint | /design A.1 | per-file | Open-ended discovery — designer doesn't yet know which entries matter. Inter-entry context reveals relevance. |
| Post-explore recall | /design A.2.5 | per-key | Exploration surfaced specific new domains. Agent can name triggers. |
| Recall diff | /design C.1, /runbook 0.75 | per-key | Diff identifies specific entries whose relevance changed. |
| Runbook recall (Tier 1/2) | /runbook entry | per-key | Lightweight — resolve domain-relevant entries from artifact or index scan. |
| Runbook recall (Tier 3) | /runbook Phase 0.5 | per-file | Planning discovery — implementation constraints cluster by file. Planner needs broad context. |
| Inline pre-work | /inline Phase 2.3 | per-key | Resolving entries from existing recall-artifact. Keys known. |
| Sub-agent priming | /inline Phase 3 dispatch | per-key | Consumer artifacts are key lists. Mechanical batch-resolve. |
| Checkpoint corrector | /orchestrate Phase 3.3 | per-key | Review-relevant entries from artifact. Targeted. |
| Deliverable review | /deliverable-review Phase 3 | per-key | Lightweight fallback — specific review failure mode entries. |

**Pattern:** Per-file at 2 of 10 points — both are open-ended discovery phases where the agent scopes the problem. The remaining 8 are per-key — the agent knows what it needs.

**Recall system simplification context:** `when-resolve.py` handles per-key (batch). Read tool handles per-file (parallel batch). No sibling expansion — index scanning is the discovery mechanism, resolver is pure lookup.

---

## Iteration Assignment

**Decision criterion:** Does loaded content at this point reveal new domains the agent couldn't anticipate from the index alone? If yes, iterate (re-scan index after loading, resolve newly-relevant entries, repeat until saturation).

| Recall Point | Mode | Iterate? | Rationale |
|---|---|---|---|
| /design Phase 0 (triage) | per-key | no | Fixed trigger set for classification |
| /design A.1 (docs checkpoint) | per-file | **yes** | Cross-file discovery — loaded files reference patterns in other files |
| /design A.2.5 (post-explore) | per-key | no | Surgical followup after saturated A.1 pass |
| /design C.1, /runbook 0.75 (recall-diff) | per-key | no | Delta evaluation, not discovery |
| /runbook Tier 1/2 (entry) | per-key | no | Lightweight, execution-bound |
| /runbook Tier 3 Phase 0.5 (planning) | per-file | **yes** | Planning discovery — implementation constraints cascade cross-file |
| /inline Phase 2.3 (pre-work) | per-key | no | Resolving curated artifact keys |
| /inline Phase 3 (sub-agent priming) | per-key | no | Mechanical batch-resolve from consumer artifact |
| /orchestrate Phase 3.3 (checkpoint) | per-key | no | Targeted review entries |
| /deliverable-review Phase 3 | per-key | no | Lightweight optional fallback |

**Result (superseded):** Original analysis found iteration at the same 2 per-file points. Revised after discussion: per-key-twice everywhere.

---

## Revised Mode Assignment

Per-key-twice replaces single-pass per-key at all 8 points. One confirmation pass is cheap insurance — one extra tool call catches entries whose relevance only appears after loading the first batch.

**Revised recall modes:**

| Mode | Definition | Pipeline usage |
|---|---|---|
| default | Per-key, two passes, scored selection | 8 of 10 recall points |
| all | Per-file, tail-recursive | /design A.1, /runbook Tier 3 Phase 0.5 |
| everything | Full corpus, no scan | Ad-hoc only (not in pipeline) |

`broad` (per-file single pass) and `deep` (per-key iterated) drop from the formal mode set. `default` absorbs the double-pass. Three modes total.

**Scoring at recall points:**

Two scoring moments serve different purposes:

- **Pre-resolve scoring** (during index scan): Forces explicit selection rationale. Agent scores each index entry for relevance before resolving. Makes selection auditable. Applies at points where the agent scans memory-index (5 of 8 per-key points). Does not apply where agent resolves from pre-curated artifact (sub-agent priming, checkpoint corrector, recall-diff — these resolve mechanically, no selection judgment).

- **Post-resolve scoring** (at skill transitions): Measures how useful loaded entries actually were. Placed at pipeline stage boundaries (/design exit, /runbook exit, /inline exit), not at every recall point. Answers: "of everything recalled during this skill's execution, what influenced the output?"

**Post-resolve scoring design:**

Placement: skill transition boundaries (same points that produce artifacts — commit, continuation).

Assessment per entry:
- **Referenced** — entry content appears in output artifact (mechanically detectable: grep output for decision headings/triggers)
- **Informed** — entry influenced a decision but isn't directly referenced (bounded judgment)
- **Unused** — loaded but not applied (remainder)

Output: section appended to recall-artifact.md at skill exit, or lightweight log (`plans/<job>/recall-usage.md`). Feeds triage-feedback-log pattern for threshold calibration.

**Relationship to triage-feedback.sh:** Structurally parallel. Triage feedback compares pre-execution classification against post-execution evidence. Recall feedback compares pre-execution selection (entries chosen) against post-execution usage (entries that mattered). Both accumulate calibration data.

**Scope note:** Post-resolve scoring is downstream infrastructure — not in recall-null scope. Noted as design input for recall calibration system.
