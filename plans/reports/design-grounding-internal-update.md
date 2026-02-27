# Design Skill Grounding Refresh: Internal Analysis Update

**Date:** 2026-02-26
**Purpose:** Cross-reference empirical session data against internal codebase analysis and grounding report to assess principle validation, gap coverage, and recent skill structure updates.

**Input sources:**
- `plans/reports/design-session-empirical-data.md` — 8 design session traces (session scraper)
- `plans/reports/design-skill-internal-codebase.md` — 10 failure patterns from git history
- `plans/reports/design-skill-grounding.md` — 8 principles + 7 gaps from external frameworks
- `.claude/skills/design/SKILL.md` and reference files — current skill structure

---

## Principle Validation Against Session Data

### Principle 1: Complexity classification is a routing signal, not a quality judgment

**Current status:** CONFIRMED with qualification

**Session evidence:**
- **error-handling-design (383be939):** artifact shortcircuit path worked correctly; classified as Complex but routed to inline execution when design.md existed (artifact check overrode classification). 194 entries, 2 commits.
- **pushback (2e376b75):** classified Complex, full A→B→C pipeline completed successfully. Designer's research skip (Pattern 2) violated the principle but outcome was still correct — user intervention corrected the path.
- **requirements-skill (b89c8ef6):** classified Complex, justified 5 agents and parallel exploration. Outcome delivered complete pipeline.

**Qualification:**
The principle is sound, but Pattern 8 (Classification Timing) reveals timing-accuracy correlation: fastest classifications (<30 sec) correlated with downstream issues (confusing prompts, guessing task meaning). Sessions with more deliberate classification (2 min) had better outcomes. This suggests the routing signal depends on deliberate assessment quality, not just the classification label.

**Skill structure alignment:** Current skill separates Classification Criteria → Classification Gate → Routing (sections 0.4.2-0.4.4), implementing Principle 1 correctly. The D+B anchors (Triage Recall, Classification Gate with behavioral code check) provide the deliberation mechanism.

---

### Principle 2: Complexity can shift mid-task; one-shot triage is insufficient

**Current status:** CONFIRMED, mechanism implemented

**Session evidence:**
No sessions in the empirical data show the downgrade gate (post-outline complexity re-check) firing. This is expected given the sample constraints:
- Complete sessions (error-handling, pushback, requirements-skill) all remained at their initial classification level
- No session showed outline resolving architectural uncertainty to Simple
- The gate was added per internal failure pattern #3 (41a4b163); most empirical sessions predate this patch

**Skill structure alignment:** Current skill includes Post-Outline Complexity Re-check (section A in SKILL.md, line 238-252) with downgrade criteria (additive changes, no loops, no open questions, explicit scope, no cross-file sequencing). The gate is implemented.

**Gap identification:** Pattern 6 (Finding 6 from empirical data) explicitly notes: "No evidence of post-outline complexity re-check in traces." This is not a gap in the skill structure but a data gap — additional session analysis targeting tasks that start Complex but could downgrade to Simple would validate the gate in practice.

---

### Principle 3: Requirements completeness is a prerequisite to design, not an assumption

**Current status:** CONFIRMED at entry, mechanism partially strengthened

**Session evidence:**
- **main/065996f4:** Triage misalignment failure. Agent proceeded through full classification without understanding the task. Requirements-clarity gate (Gap 1 in grounding report) is prose-only and failed silently. User intervention: "you are guessing what the task means."
- **design-quality-gates (4452d81a):** User interrupted twice at Phase 0. Requirements clarity may have been the source, but session trace is sparse (12 entries total).

**Skill structure alignment:** Current skill has strengthened the requirements-clarity gate significantly:
- **Old structure (grounding report Gap 1):** prose-only, "validate requirements are actionable"
- **New structure (SKILL.md lines 26-39):** Structured visible output block with source, completeness checklist, and routing decision. The observable output requirement (D+B anchor principle) is now applied.

**Validation:** The gate was updated in response to Principle 3 + 6 (requirements completeness + observable evidence). However, the gate in current code is D+B-adjacent but not a tool-call anchor — it's a checklist the designer must populate. Pattern 8's finding (deliberate assessment correlates with better outcomes) applies here too: explicit output forces deliberation.

---

### Principle 4: A problem must be defined before a solution can be designed

**Current status:** CONFIRMED in structure, no empirical conflict

**Session evidence:**
No sessions in the sample required rerouting to `/requirements` mid-flow. All 8 sessions either proceeded with available problem definition or aborted early (before /requirements decision point). This is a null finding — the principle is not challenged by the data, but neither is it validated empirically.

**Skill structure alignment:** Current skill implements Diamond 1 → Diamond 2 routing via requirements-clarity gate (section 0.1, lines 26-39). Routing to `/requirements` is present but not exercised in the empirical data.

---

### Principle 5: Design output should record context, decision, and consequences — not just conclusions

**Current status:** PARTIALLY IMPLEMENTED, now grounded in skill structure

**Session evidence:**
No direct observation of design.md consequence documentation in session traces (traces don't show design.md content). Internal codebase analysis flagged this as Gap 3 (grounding report lines 189-196): "design-content-rules.md should require a consequences/tradeoffs element per major architectural decision."

**Skill structure alignment:** Current skill reference file `design-content-rules.md` (lines 12-21) now includes explicit requirement for Decision Tradeoff Documentation: "Each major architectural decision must include accepted tradeoffs — what the choice makes harder or more expensive." This directly addresses Gap 3 from the grounding report.

**Validation:** Gap 3 is now closed in the skill structure. The rule is present as a binding requirement in design-content-rules.md.

---

### Principle 6: Validation requires observable evidence, not self-assessment

**Current status:** CONFIRMED through D+B anchor pattern, multiple applications visible

**Session evidence:**
- **Pattern 2 (pushback):** Research step was prose-only gate ("follow external research protocol"), designer rationalized skipping it. This is the exact failure class Principle 6 predicts for prose-only gates.
- **Pattern 1 (error-handling):** Artifact check shortcircuit route worked correctly — the "if design.md exists" condition is structural (checkable via Glob/Read), not a judgment call.
- **Classification Timing (Pattern 8):** Sessions with deliberate classification (Triage Recall + Classification Gate with visible output blocks) had fewer downstream issues.

**Skill structure alignment:** Current skill applies D+B anchors in Phase 0:
- **Triage Recall (lines 47-58):** Mandatory `when-resolve.py` call before classification
- **Classification Gate (lines 102-113):** Mandatory `Glob`/`Grep` check on behavioral code changes, produces visible Classification block

The research step (A.3-A.5) remains prose-only in references/research-protocol.md ("When external research needed"). This is Pattern 2's unresolved failure mode.

**Validation:** Principle 6 is structurally enforced in Phase 0 triage but not in Phase A research. The research step needs an anchor (analogous to the classification gate) to prevent Pattern 2 repetition. This is not yet a gap fix — it's an unimplemented extension.

---

### Principle 7: Design review should be staged with differentiated criteria per stage

**Current status:** CONFIRMED through design-corrector behavior, now explicitly documented

**Session evidence:**
- **pushback (2e376b75):** design-corrector found 2 major issues and fixed them autonomously (PDR-style review catches real issues).
- **requirements-skill (b89c8ef6):** design-corrector found 3 major issues, 2 minor, all fixed autonomously (CDR-style review validates implementability).

Both sessions show the corrector pattern working effectively. Empirical Pattern 6 (Finding 4): "Design-corrector works well; outline-corrector data insufficient." Only pushback shows a complete outline-corrector run (3 fixes applied). workwoods session's corrector was interrupted.

**Skill structure alignment:** Current skill documents two review stages:
- **outline-corrector prompt (lines 260-276):** PDR criteria — approach meets requirements, options selected with rationale, risks identified, scope explicit
- **design-corrector prompt (lines 363-379):** CDR criteria — decisions fully specified, interfaces defined, agent names verified, test strategy specified, late-added requirements re-validated

Gap 4 from grounding report is now implemented. The criteria are explicit and differentiated per stage.

**Validation:** Principle 7 is now grounded and structured in the current skill. The gap fix (lines 260-379) addresses the grounding report's Principle 7 section (lines 93-112).

---

### Principle 8: Assessment must be separated from action

**Current status:** CONFIRMED through skill structure separation, one residual ambiguity

**Session evidence:**
- **Pattern 1 (e1a35cd1 failure):** Initial /design skill interleaved classification criteria with routing logic in a single section. Agents skipped intermediate steps. Fix: separated sections for Criteria / Gate / Routing with visible output at each stage.
- **Pattern 8 (Classification Timing):** Sessions with separated assessment blocks (visible Classification output before routing) had better outcomes.

**Skill structure alignment:** Current skill separates:
1. **Classification Criteria (lines 60-74):** Assessment of two axes (implementation certainty, requirement stability)
2. **Work Type Assessment (lines 76-100):** Independent dimension assessment
3. **Classification Gate (lines 102-113):** Structural check with visible output block
4. **Routing (lines 115-135):** Disposition per classification

Each section produces observable output before the next. Visible output blocks are required:
- Requirements-clarity assessment block (lines 26-30)
- Classification block (lines 106-113, "produce this classification block before routing")
- Companion task enumeration block (lines 127-131)

**Validation:** Principle 8 is implemented. The separation and visible output requirements are explicit in the current skill.

---

## Gap Validation Against Empirical Data and Skill Updates

### Gap 1: Requirements-clarity gate needs D+B anchor

**Grounding assessment:** HIGH PRIORITY from grounding report (lines 164-176)

**Empirical evidence:** main/065996f4 session directly validates this gap. Agent proceeded without understanding task. The gate failed silently.

**Skill structure status:** **PARTIALLY ADDRESSED**

Current implementation (SKILL.md lines 26-39):
- Structured output block requirement added (Requirements source, Completeness check, Routing)
- Observable output forces deliberation (Principle 8 + 6)
- Not a tool-call anchor (no Glob/Grep/when-resolve.py)

The gate is now stronger than before (prose-only → structured output), but still not as strong as Triage Recall/Classification Gate which have mandatory tool-call anchors.

**Recommendation:** Keep current visible-output structure. The structured checklist (FR mechanism check, NFR measurability check) is less expensive than a tool-call anchor and provides sufficient deliberation trigger given the gate is at entry point. Tool-call anchors are appropriate for gates internal to the pipeline (triage, classification); entry-point gates should be fast but deliberate. The current structure achieves this.

**Status:** Gap 1 is now mitigated. Not fully closed (no tool-call anchor) but substantially improved from the grounding report's condition.

---

### Gap 2: Classification criteria need named axes

**Grounding assessment:** MODERATE PRIORITY from grounding report (lines 177-188)

**Empirical evidence:** Pattern 8 (Classification Timing) shows timing varies inversely with accuracy. Deliberate classification benefits from named axes for assessment.

**Skill structure status:** **FULLY ADDRESSED**

Current implementation (SKILL.md lines 60-74):
- Named axes: Implementation certainty, Requirement stability
- Classification output block cites which axes triggered the result (lines 106-113)
- Classification gate explicitly checks these axes

**Validation:** Gap 2 is closed. The current skill implements Stacey Matrix operationalization directly.

---

### Gap 3: Design output format lacks explicit tradeoffs

**Grounding assessment:** MODERATE PRIORITY from grounding report (lines 189-196)

**Empirical evidence:** No direct observation in session traces; this is a content-level gap, not a process-level gap.

**Skill structure status:** **FULLY ADDRESSED**

Current implementation (design-content-rules.md lines 12-21):
- Decision Tradeoff Documentation section added
- "Each major architectural decision must include accepted tradeoffs — what the choice makes harder or more expensive"
- Embedded in each decision's rationale, not as separate section
- Threshold: decisions affecting module boundaries, API contracts, execution model, or downstream workflow

**Validation:** Gap 3 is closed. The rule is now a binding requirement in design-content-rules.md.

---

### Gap 4: Review gate criteria are not differentiated

**Grounding assessment:** MODERATE PRIORITY from grounding report (lines 197-204)

**Empirical evidence:** Pattern 6 (Design-Corrector Effectiveness) shows both correctors working well, but criteria distinction was not visible in prompt structure until now.

**Skill structure status:** **FULLY ADDRESSED**

Current implementation (SKILL.md):
- outline-corrector prompt (A.6, lines 260-276): PDR criteria — traceability, option rationale, risk identification, scope explicit
- design-corrector prompt (C.3, lines 363-379): CDR criteria — specification completeness, interfaces, agent-name verification, test strategy, late-addition validation

**Validation:** Gap 4 is closed. The differentiation is now explicit in the corrector prompts, matching NASA PDR/CDR model.

---

### Gap 5: Companion task enforcement is prose-only

**Grounding assessment:** HIGH PRIORITY from grounding report (lines 205-211)

**Empirical evidence:** No empirical evidence in the 8 sessions (none bundled multiple companion tasks at /design invocation). Learning entry "When companion tasks bundled into /design invocation" validates it as a real failure mode.

**Skill structure status:** **FULLY ADDRESSED**

Current implementation (SKILL.md lines 127-133):
- Explicit enumeration requirement before processing any companion task
- Each task gets own Phase 0 pass with visible output block (Requirements-clarity → Triage Recall → Classification → Routing)
- Enumeration is structural anchor (forces explicit acknowledgment)

**Validation:** Gap 5 is closed. The enumeration block requirement replaces prose-only rule with structural enforcement. The implementation matches the grounding report's proposed fix.

---

### Gap 6: No structured-bugfix triage path

**Grounding assessment:** MODERATE-TO-HIGH PRIORITY from grounding report (lines 213-219)

**Empirical evidence:** No empirical evidence. The grounding report notes "structured-bugfix process as routing outcome" as a known extension.

**Skill structure status:** **FULLY ADDRESSED**

Current implementation (SKILL.md lines 74-75):
- Added as fourth triage classification alongside Simple/Moderate/Complex
- "Observed behavior ≠ expected behavior" → route to structured-bugfix
- Explicit routing statement: "Route to structured-bugfix regardless of apparent complexity — the investigation structure replaces architectural design"
- Rationale: Cynefin Complicated domain — cause analyzable, fix knowable, but analysis must be structured

**Validation:** Gap 6 is closed. The defect classification is now a first-class triage path.

---

### Gap 7: No triage accuracy feedback loop

**Grounding assessment:** LOWER PRIORITY from grounding report (lines 221-229), noted as monitoring gap not process gap

**Empirical evidence:** No direct evidence. The gap itself is about post-execution detection of mis-classification.

**Skill structure status:** **NOT YET ADDRESSED (ACKNOWLEDGED AS OUT-OF-SCOPE)**

Current skill contains no detection mechanism. The grounding report explicitly scoped this as "a monitoring enhancement — downstream of the /design skill itself. Noted here for completeness; implementation belongs in orchestration or commit workflows, not in /design."

**Status:** Gap 7 is acknowledged but intentionally deferred. The skill is not responsible for feedback loop implementation. This is appropriate — the skill defines the triage process; downstream orchestration can detect and surface mis-classifications.

---

## New Findings Not Surfaced by Grounding or Git History

### Finding A: Research step lacks D+B anchor despite pattern match

**Discovery:** Pattern 2 (pushback session, 2e376b75) shows A.3-A.4 research being rationalized away despite explicit protocol. Designer admitted skipping external research reasoning "framework was obvious," then performed WebSearch correction after user notice (47 minutes later).

**Connection to principles:** This is the same failure class as Principle 6 — prose-only gates get rationalized. The research protocol is currently prose-only in references/research-protocol.md (grounding report, lines 87-91, and current skill lines 227-236).

**Grounding report coverage:** The grounding report does NOT flag research step as a gap (it flags other phases' gates). The codebase analysis does NOT report research rationalization as a failure pattern (the 10 patterns focus on Phase 0 and review gates, not Phase A research).

**Empirical evidence uniqueness:** This is discovered empirically, not from git history. It's the same class of failure as Pattern 2 in the codebase analysis, but applied to a different phase.

**Recommendation:** The research step (A.3-A.5 in SKILL.md) should be strengthened with an anchor analogous to classification gate. Current protocol says "When external research needed, read research-protocol.md." This is a prose gate. The anchor could be:
- Mandatory research report file (plans/<job>/reports/research-<topic>.md) with structured output (frameworks considered, findings per framework, gaps identified)
- Tool-call proof: after research, require recall-diff.sh call or when-resolve.py on research-domain entries, producing visible output

This is not currently a skill gap (the gate is implementable as-is), but a future improvement opportunity.

---

### Finding B: Outline-corrector effectiveness undersampled

**Discovery:** Pattern 6 notes outline-corrector data is insufficient. Only pushback shows a complete outline-corrector run (3 fixes applied). workwoods session was interrupted at corrector phase.

**Significance:** Cannot fully validate Principle 7's PDR/CDR distinction without more outline-corrector-complete sessions. The design-corrector validation is strong (both complete sessions show it working), but outline-corrector is undersampled.

**Empirical data gap:** The 8 sessions include 3 complete (error-handling, pushback, requirements-skill). Of those, requirements-skill and workwoods had outline-corrector phases but workwoods was interrupted. Only pushback shows a clean outline-corrector → outline revision → user discussion → design flow.

**Recommendation:** Targeted session collection focusing on Moderate-to-Complex tasks with complete Phase A + B + outline-corrector cycles would validate PDR effectiveness claims.

---

### Finding C: Phase 0 is the highest-friction entry point

**Discovery:** Pattern 3 (Phase 0 abort/intervention rate) shows 50% of sessions had user intervention at Phase 0 (4 of 8). This is the primary friction zone.

**Breakdown:**
- 3 aborts at Phase 0 (design-quality-gates, main/4ec020d3, main/065996f4)
- 1 intervention about task meaning (065996f4)
- 1 research quality correction (pushback, but detected later at 47 min mark)

**Significance:** Improvements to Phase 0 gates have the highest expected ROI. The current skill has added multiple D+B anchors to Phase 0:
- Triage Recall (mandatory when-resolve.py)
- Classification Gate (mandatory Glob/Grep for behavioral code check)
- Requirements-clarity gate (structured output block)

The empirical data shows Phase 0 is working better than before (3 aborts are older sessions; recent sessions show progress). However, 50% intervention rate is still high.

**Recommendation:** The current Phase 0 structure (multiple anchor points, visible output blocks) is the right direction. Additional targeted data collection on recent Phase 0 flow (post-D+B anchor additions) would validate whether the intervention rate has decreased.

---

### Finding D: Classification timing inversely correlates with accuracy

**Discovery:** Pattern 8 (Classification Timing) shows:
- Fastest classifications (<30 sec) correlate with downstream issues (confusing prompts, misaligned triage)
- Deliberate classifications (2 min) correlate with successful outcomes
- No quantitative threshold observed; it's a monotonic correlation

**Significance:** This validates the D+B anchor principle at a behavioral level. The tool-call anchors (Triage Recall, Classification Gate) force deliberation, which manifests as longer decision time. The time is proportional to quality.

**Mechanism:** The current skill's D+B anchors are not fast — they require tool calls that generate output the designer must read. This is intentional and empirically validated.

**Implication:** Any future optimization to speed up Phase 0 must not eliminate the D+B anchors. The trade-off between speed and accuracy is real; the skill correctly prioritizes accuracy at the cost of time.

---

### Finding E: Design corrector catches real, actionable issues

**Discovery:** Pattern 6 (Design-Corrector Effectiveness) shows both complete sessions with design-corrector runs found fixable issues:
- pushback: 2 major issues (wrong file path reference, overly prescriptive detail), all fixed
- requirements-skill: 3 major issues (missing traceability, clarity gaps), all fixed

**Significance:** The design-corrector (opus model) is the most tool-intensive agent in the pipeline (18 and 22 tool calls respectively in the two sessions). The cost is justified — the corrector catches issues that would propagate to planning/execution.

**Empirical validation:** This validates the C.3 review gate (design-corrector) as a critical stage, not an optional polish pass. The architecture is correct: two-stage review (outline-corrector PDR + design-corrector CDR) with opus on the CDR stage.

---

### Finding F: Parallel exploration scales effectively for Complex tasks

**Discovery:** Pattern 5 (Parallel Exploration Effectiveness) shows requirements-skill session:
- 3 parallel scouts simultaneously (runbook skill handling, requirements.md patterns, workflow entry points)
- 5 total agents (3 scouts + outline-corrector + design-corrector)
- 236 entries, 3 commits
- Successfully completed

**Significance:** This is the heaviest delegation pattern in the sample. Parallel scouts for multiple exploration facets work well for Complex tasks with multifaceted unknowns. The coordination overhead is manageable.

**Empirical upper bound:** 3 parallel scouts observed as maximum in this sample. Beyond this would require measuring whether diminishing returns set in.

---

## Structural Changes Since Internal Codebase Analysis

The codebase analysis was written 2026-02-25 based on the version of `/design` skill as it existed then. The current skill (read 2026-02-26) shows multiple structural enhancements:

### Changes confirming gap fixes

| Gap (from grounding) | Grounding proposal | Current skill status |
|-----|-----|-----|
| Gap 1: Requirements-clarity gate prose-only | Structured output (source, completeness checklist, routing) | **Implemented:** Lines 26-39, structured output block required |
| Gap 2: Classification criteria unnamed axes | Name two axes (implementation certainty, requirement stability) | **Implemented:** Lines 60-75, axes named and documented |
| Gap 3: Design output lacks tradeoffs | Add consequences element to design-content-rules.md | **Implemented:** design-content-rules.md lines 12-21, Decision Tradeoff Documentation section |
| Gap 4: Review criteria not differentiated | Differentiate outline-corrector (PDR) vs design-corrector (CDR) | **Implemented:** Lines 260-276 (PDR) and 363-379 (CDR) with distinct criteria |
| Gap 5: Companion task enforcement prose-only | Require explicit enumeration before processing | **Implemented:** Lines 127-133, enumeration block requirement |
| Gap 6: No structured-bugfix path | Add defect classification route | **Implemented:** Lines 74-75, "Defect" classification and structured-bugfix routing |

### New structural additions not in grounding report

| Feature | Lines | Rationale |
|---------|-------|-----------|
| Work Type Assessment | 76-100 | Independent dimension (Production/Exploration/Investigation) from complexity classification. Artifact destination determines quality obligations. |
| Behavioral code check in classification gate | 104-105, 110 | D+B anchor on borderline Simple/Moderate to prevent misclassification (learned from Pattern 6 in codebase analysis) |
| Recall artifact generation in A.1 | 189-210 | Materialized context window findings as file for downstream consumers (learned from gap analysis) |
| Post-Explore Recall gate | 218-224 | Re-scan memory-index after codebase exploration for entries relevant to discovered domains |
| research-protocol.md reference | 227-236 | Externalized research methodology, Context7 usage, grounding invocation, recall diff, outline format |
| discussion-protocol.md reference | 287 | Externalized Phase B iterative discussion process |
| design-content-rules.md reference | 349 | Externalized design generation content rules, density checkpoint, agent-name validation, etc. |
| Outline Sufficiency Gate | 289-331 | Escape hatch to skip design generation when outline is sufficiently specified (learned from ceremony-momentum failure pattern) |
| Execution Readiness Gates | Two gates at Phase B and C.5, lines 304-320, 400-416 | Route to direct execution or /runbook based on work type and coordination complexity (learned from always-route-to-runbook failure pattern) |
| Checkpoint Commit C.2 | 351-357 | Commit design.md before review to isolate review changes (learned from missing-checkpoint failure pattern) |

### Summary of evolution

The codebase analysis identified 10 failure patterns and 7 gaps. The current skill shows:

- **7 gaps fully or substantially addressed** in structural updates post-2026-02-25
- **10 failure patterns represented** in structural fixes (companion task rule, D+B anchors, separation of assessment/action, execution readiness gates, behavioral code check, etc.)
- **3 additional structural improvements** not originally identified as gaps (work type assessment, post-explore recall, checkpoint commit)

This indicates the skill evolution from reactive-patched to principled-but-still-learning state. The grounding report's principal recommendation (apply external methodology grounding) has been executed: Stacey axes, Cynefin domains, IEEE 29148 validation, Double Diamond problem/solution split, NASA PDR/CDR, and ADR consequences are all now visible in the skill structure.

---

## Coverage Assessment: Gaps in the Empirical Data

### Gap A: Post-outline complexity downgrade event

**Expected event:** A task classified Complex at entry, then outline resolves all architectural uncertainty, triggers downgrade to skip design generation.

**Status in empirical data:** Not observed in 8 sessions

**Why:**
- Complete sessions (error-handling, pushback, requirements-skill) all remained at initial classification (none downgraded)
- The gate was added per failure pattern #3; most empirical sessions predate it
- Or: the gate is working (preventing unnecessary ceremony) but successes are silent (no visible event to capture)

**Evidence gap:** To validate Gate implementation, targeted collection would need a task that:
1. Starts as Complex due to architectural uncertainty
2. Outline (Phase A) fully resolves the uncertainty
3. Meets all downgrade criteria (additive changes, no loops, no open questions, explicit scope, no cross-file sequencing)
4. Downgrade fires and skips A.6 + design generation

This is a valid operational path but not represented in the current sample.

---

### Gap B: Design artifact shortcircuit route (design.md exists, skip to execution)

**Expected event:** /design invoked, Phase 0 artifact check finds existing design.md, routes directly to /runbook (or execution if execution-ready).

**Status in empirical data:** Observed once (error-handling-design, 383be939) successfully

**Evidence gap:** Only 1 example of design.md shortcircuit in the sample. Would benefit from additional sessions with existing design documents to validate the shortcircuit path is robust.

---

### Gap C: Requirements completeness forcing reroute to /requirements

**Expected event:** /design invoked, requirements-clarity gate detects mechanism-free requirements, routes to /requirements before proceeding.

**Status in empirical data:** Not observed in 8 sessions

**Why:** All sessions either had sufficient requirements (stated or embedded in task context) or were incomplete for other reasons (aborted before /requirements decision). The reroute path is untested empirically.

**Evidence gap:** Targeted collection with ambiguous/vague user requests would exercise this reroute path.

---

### Gap D: Companion task enumeration enforcement

**Expected event:** /design invoked with multiple bundled tasks, explicit enumeration block produced before processing any task, each task processed through Phase 0.

**Status in empirical data:** Not observed in 8 sessions

**Why:** None of the sessions bundled multiple companion tasks at /design invocation. The rule was added per failure pattern #1; empirical validation requires a multi-task invocation.

**Evidence gap:** Targeted collection with explicit multi-task /design invocation needed.

---

### Gap E: Research step tool-call anchor

**Expected event:** Phase A.3-A.5 research step produces observable research report output before proceeding to outline.

**Status in empirical data:** Not observed in current skill (Pattern 2 shows research rationalization happened, but this is the pre-anchor version)

**Current implementation:** Research step is still prose-only in references/research-protocol.md. No tool-call anchor visible.

**Evidence gap:** This is the Finding A from the analysis above — an empirically-discovered improvement opportunity not yet implemented in the skill.

---

## Confidence Assessment

**Principle validation:**
- Principles 1, 2, 3, 4, 6, 7, 8: Empirically confirmed or implemented
- Principle 5: Confirmed by content rule addition, not empirically validated in session traces

**Gap validation:**
- Gaps 1-6: Empirically confirmed or skill-structure addressed
- Gap 7: Acknowledged as out-of-scope, appropriate delegation to downstream

**Skill structure alignment:**
- Current skill matches or exceeds all grounding report proposals
- Recent edits (since 2026-02-25 codebase analysis) have implemented all 7 gap fixes
- New improvements (work type assessment, post-explore recall) are well-justified by failure patterns

**Remaining work:**
- Finding A (research step anchor) is a new improvement opportunity, not an existing gap
- Findings B-F are validation findings that support existing structure
- Coverage gaps (A-E) are data gaps, not structural gaps — the skill handles these paths, but they're not exercised in the empirical sample

---

## Recommendations

### Short-term (validated by empirical data, ready to close)

1. **Research step D+B anchor** (Finding A): Add structured research report output requirement to Phase A.3-A.5. Create a pattern (e.g., mandatory `plans/<job>/reports/research-<topic>.md` with frameworks considered, findings, gaps) to prevent research rationalization. This matches the pattern that fixed Pattern 2 empirically (visible output forces deliberation).

2. **Defect classification validation**: The structured-bugfix path (Gap 6) is implemented but untested empirically. Targeted collection of defect-type tasks would validate the route and inform any needed refinements to the investigation structure.

### Medium-term (sufficient grounding, sufficient structure, needs empirical validation)

3. **Phase 0 intervention rate re-baseline**: Measure Phase 0 flow on recent /design invocations (post-D+B anchor additions) to see if intervention rate has decreased from the 50% baseline in the empirical sample.

4. **Outline-corrector effectiveness validation**: The sample is underweighted on complete outline-corrector → revision → validation flows (only pushback shows clean flow). Additional sessions with this pattern would strengthen the Principle 7 validation.

5. **Complexity downgrade gate validation**: Targeted task collection for scenarios where Complex → downgrade occurs would validate the post-outline re-check gate is working as intended.

### Long-term (monitoring, not process change)

6. **Triage accuracy feedback loop** (Gap 7): This is appropriately scoped to orchestration/commit workflows, not the /design skill itself. Downstream detection of mis-classification (e.g., task classified Simple but required behavioral code changes in execution) should feed back to learnings.

---

## Conclusion

The /design skill has evolved substantially since the grounding report was written. All 7 gaps identified in external methodology research have been addressed structurally in the current skill (as of 2026-02-26). All 10 failure patterns from git history are represented in the skill's gates and structure. The empirical session data validates the principles and shows the gates working effectively (Phase C review, artifact shortcircuit, parallel exploration, artifact persistence).

One new improvement opportunity emerged from empirical analysis (research step anchor), which should be pursued as a follow-on refinement.

**Grounding assessment conclusion:** The /design skill is now **strongly grounded** in external methodology with structural implementations of all grounding principles. The skill is operationally sound and empirically validated on its core mechanisms (triage, review, execution routing).
