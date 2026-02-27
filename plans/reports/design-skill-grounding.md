# Design Skill Grounding Report

**Grounding:** Strong

**Date:** 2026-02-26 (v2 — empirical refresh)
**Method:** Parallel diverge-converge (session scraper empirical data + targeted external research), opus convergence
**Prior version:** 2026-02-25 (6 frameworks, 8 principles, 7 gaps)
**v2 update:** 2026-02-27 — extraction fixes (interrupt + classification detection), Gap 9 merged into Gap 7
**Branch artifacts:** `design-skill-internal-codebase.md`, `design-skill-external-research.md`, `design-session-empirical-data.md`, `design-grounding-internal-update.md`, `design-grounding-external-update.md`
**Purpose:** Validate and extend /design skill grounding with empirical session behavior data

---

## Research Foundation

Nine framework clusters cover the design skill's functional scope (6 original + 3 new from empirical gap research):

| Framework | Origin | Authority | Covers |
|-----------|--------|-----------|--------|
| Cynefin | Snowden, IBM, 1999 | HBR-endorsed; SAFe/Scrum | Domain-based complexity classification + routing |
| Stacey Matrix | Stacey, 1990s | PMI/Agile curricula | Two-axis (certainty × agreement) triage |
| IEEE 29148:2018 | ISO/IEC/IEEE | International standard | Requirements completeness + validation criteria |
| Double Diamond | UK Design Council, 2005 | Government research body | Diverge-converge workflow arc |
| ADR process | Nygard 2011; AWS, Microsoft | Industry standard | Architectural decision documentation |
| NASA PDR/CDR + SRR/SDR | NPR 7123.1 | NASA standard | Staged design review gates; investigation entrance criteria |
| **Stage-Gate** | Cooper, 1988 | Industry standard | Gate enforcement through required deliverables |
| **Kahneman dual-process + ESI** | Kahneman 2011; ESI systematic reviews | Peer-reviewed | Triage accuracy mechanisms; deliberation vs heuristic assessment |
| **GJP/AAR** | Tetlock 2015; U.S. Army | Peer-reviewed; military doctrine | Classification calibration through structured outcome feedback |

Supporting: ATAM (CMU SEI) for quality attribute prioritization; Y-statement format (Zdun et al.) for tradeoff acknowledgment; Premature closure literature for structured reflection; A3 (Toyota) for format-as-enforcement; DMAIC tollgates for phase deliverable checklists.

---

## Framework Mapping

### Principle 1: Complexity classification is a routing signal, not a quality judgment

**General insight:** Cynefin and Stacey Matrix both frame complexity classification as determining *what workflow is appropriate*. Cynefin's Clear domain routes to best-practice application; Complicated routes to expert analysis; Complex routes to experimentation. Stacey operationalizes with two concrete axes: certainty about *how* to achieve the goal, and agreement about *what* is needed. Neither framework treats "Simple" as inferior — it means the workflow overhead of analysis is unjustified.

**Project validation:** The /design skill routes Simple → direct execution, Moderate → /runbook, Complex → Phases A-C. The current criteria map to Stacey axes: "architectural decisions, multiple valid approaches" = low certainty about how; "uncertain requirements" = low agreement about what. The Moderate category = Cynefin Complicated (known technique, expert analysis resolves); Simple = Clear.

**Empirical validation (v2):** 3 complete design sessions confirm routing accuracy when classification is deliberate. The error-handling session correctly shortcircuited (existing design.md). The pushback and requirements-skill sessions correctly followed full Complex pipeline. Pattern 8 shows classification timing inversely correlates with accuracy — fast classifications (<30 sec) correlate with downstream issues, deliberate classifications (~2 min) with better outcomes.

**What grounding adds:** The current classification criteria describe *what tasks look like* at each tier, not *what axes are being assessed*. Stacey provides the principled anchor: explicitly assess (1) implementation certainty — "is the approach known?" and (2) requirement stability — "are FRs agreed and mechanism-specified?" Both high → Simple; either low → Moderate/Complex depending on degree.

**Gap status (v2):** Gap 2 (named axes) — CLOSED. Current skill names both axes with visible output in classification block.

---

### Principle 2: Complexity can shift mid-task; one-shot triage is insufficient

**General insight:** Cynefin explicitly warns that domain assignment can shift: complicated problems reveal hidden complexity; complex problems resolve to complicated once experimentation yields insight. The framework expects reassessment as an intrinsic part of the process, not as an exception.

**Project validation:** Failure pattern #3 (commit `41a4b163`): one-shot triage at entry with no re-assessment. Process continued at "Complex" for a two-file prose edit. Cost: ~112K tokens for outline-corrector + design.md + design-corrector on work executable inline. Fix: post-outline complexity re-check gate.

**Empirical validation (v2):** No sessions in the 8-session sample show the downgrade gate firing. This is a data coverage gap (most sessions predate the gate, and complete sessions all remained at initial classification). The gate is implemented but empirically unvalidated.

**What grounding adds:** The two current gates (entry triage + post-outline re-check) are Cynefin-grounded mid-task reassessment. The downgrade criteria (additive changes, no loops, no open questions, explicit scope, no cross-file sequencing) operationalize "domain has shifted to Clear."

---

### Principle 3: Requirements completeness is a prerequisite to design, not an assumption

**General insight:** IEEE 29148:2018 defines requirements validation as a distinct activity that must precede design. Requirements must be complete, consistent, unambiguous, and verifiable. The standard explicitly separates requirements from design — design begins when requirements are validated, not when they are stated. Validation produces an observable artifact, not a self-assessment.

**Project validation:** The requirements-clarity gate checks "each FR/NFR has concrete mechanism" — mapping to IEEE 29148's "verifiable" criterion. Late-addition failure (FR-18 incident): requirement added during design bypassed outline-level validation, producing a mechanism-free specification downstream planners couldn't implement.

**Empirical validation (v2):** Session 065996f4 directly confirms Gap 1. Agent proceeded through classification and routing without understanding the task — "you are guessing what the task means." Requirements-clarity gate was prose-only and failed silently.

**Gap status (v2):** Gap 1 (D+B anchor) — MITIGATED. Current skill uses structured output block (source, completeness checklist, routing) rather than tool-call anchor. Deliberation trigger without full D+B cost.

---

### Principle 4: A problem must be defined before a solution can be designed

**General insight:** Double Diamond (Design Council, 2005) distinguishes problem space (Diamond 1: Discover → Define) from solution space (Diamond 2: Develop → Deliver). The routing rule: if the problem is already defined, skip Diamond 1. If ambiguous, run Diamond 1 first. The framework treats requirements as active discovery, not passive receipt.

**Project validation:** The `/requirements` skill is the Diamond 1 path. The requirements-clarity gate routes vague requirements to /requirements before /design proceeds — the project-specific implementation of "if problem not defined, run Diamond 1 first." The /design skill operates within Diamond 2.

**Empirical validation (v2):** No sessions exercised the /requirements reroute path. All 8 sessions either had sufficient problem definition or aborted before the decision point. The routing structure exists but is empirically untested.

---

### Principle 5: Design output should record context, decision, and consequences — not just conclusions

**General insight:** ADR format (Nygard 2011) requires each architectural decision to capture: context (forces at play), decision (the choice made), status (proposed/accepted/superseded), and consequences (what becomes easier *and harder*). The Y-statement variant (Zdun et al.) forces explicit tradeoff acknowledgment: "In the context of [situation], facing [concern], we decided for [option], to achieve [quality], accepting [downside]." The accepted downside is mandatory, not optional.

**Project validation:** The design.md output is the project's ADR equivalent. design-content-rules.md now requires "accepted tradeoffs — what the choice makes harder or more expensive" per major decision.

**Gap status (v2):** Gap 3 (explicit tradeoffs) — CLOSED. design-content-rules.md includes Decision Tradeoff Documentation section as binding requirement.

---

### Principle 6: Validation requires observable evidence, not self-assessment

**General insight:** IEEE 29148 defines validation as a distinct activity producing observable artifacts — not a self-assessment by the requirements author. Cynefin warns that domain assignment is contested judgment, not measurement. Stacey acknowledges its axes "lack a formal assessment protocol" — framing this as a known limitation.

**Extended grounding (v2):** Stage-Gate (Cooper), DMAIC tollgates, NASA SRR entrance criteria, and Toyota A3 all enforce investigation phases through **required deliverable artifacts**, not instructions. Cooper: "Gatekeepers confirm deliverables exist before authorizing the next stage." DMAIC: "evidence you could use to convince your Sponsor must be prepared." NASA: cascading gate dependencies where Gate N+1 is impossible without Gate N artifacts. A3: format-enforced sequencing where current-state section must be populated before countermeasures.

Kahneman's dual-process theory provides the causal mechanism: mandatory data collection (vital signs in ESI, tool calls in D+B anchors) changes the cognitive process from System 1 pattern-match to System 2 deliberate analysis. ESI triage research: "When vital signs were introduced as a necessary parameter, the framework for decision making changed... with an increase in accuracy." The data collection itself is the intervention — not what the data says, but the act of collecting it.

**Empirical validation (v2):** This is the dominant convergence point between all three evidence layers:

- **Session scraper (Pattern 2, pushback):** Research phase (A.3-A.5) is prose-only. Designer rationalized skipping external research — "framework was obvious." User caught it 47 minutes later. Same failure class as all other prose-only gates.
- **Session scraper (Pattern 8):** Classification timing inversely correlates with accuracy. D+B anchors that force tool calls enforce deliberation, which manifests as longer but more accurate classification.
- **Git history (Pattern 2):** Every prose-only gate eventually fails. Resolution: D+B anchor — tool call producing visible output.
- **External frameworks:** Stage-Gate, DMAIC, NASA, A3 all converge on the same mechanism: required artifacts enforce phase completion. Prose instructions do not.

**What grounding adds (v2):** The D+B anchor pattern is now grounded in 4 additional external frameworks (Stage-Gate, DMAIC, NASA SRR, A3) beyond IEEE 29148. The causal mechanism is grounded in Kahneman dual-process theory and ESI empirical research. The research step (A.3-A.5) is identified as the remaining prose-only gate — same failure class, same fix needed.

**New gap identified (v2):** Gap 8 — Research step anchor. See gap analysis section.

---

### Principle 7: Design review should be staged with differentiated criteria per stage

**General insight:** NASA's PDR/CDR model uses two review gates with distinct criteria. Preliminary Design Review validates *direction*: does the approach meet requirements? Are correct options selected? Are risks identified? Critical Design Review validates *readiness*: are specifications build-to complete? Can implementers proceed without inference? Test plans defined?

**Empirical validation (v2):** Both complete design sessions show design-corrector (CDR) catching real issues:
- Pushback: 2 major fixes (wrong path reference, overly prescriptive detail), 18 tool calls
- Requirements-skill: 3 major fixes (missing traceability, clarity gaps), 22 tool calls

Design-corrector is the most tool-intensive agent in the pipeline. The CDR-style review adds measurable value — corrector catches issues that would propagate to planning/execution. Outline-corrector (PDR) data is undersampled — only pushback shows a complete run.

**Gap status (v2):** Gap 4 (differentiated criteria) — CLOSED. outline-corrector uses PDR criteria (traceability, option rationale, risk identification). design-corrector uses CDR criteria (specification completeness, interfaces, agent-name verification, test strategy).

---

### Principle 8: Assessment must be separated from action

**General insight:** Decision science and clinical triage separate the evaluation step from the disposition step. Structured decision-making literature (Klein's Recognition-Primed Decision Model) documents "premature closure" — the decision-maker recognizes a pattern and commits before completing assessment.

**Extended grounding (v2):** Premature closure is the dominant triage failure mode in medical diagnostic literature: "the failure to consider alternative diagnoses after the initial impression." Prevention mechanisms with empirical support include structured reflection checklists and diagnostic timeouts. Peer-reviewed research (Design Science, Cambridge Core) validated that "checklist-style interventions for mitigation of availability bias in professional designers" reduced systematic errors.

**Empirical validation (v2):** Pattern 8 (classification timing) directly demonstrates premature closure: fast classifications (<30 sec) commit to a pattern before evidence collection completes. The Classification Gate's visible output block requirement is the project-specific implementation of a structured reflection checklist — it prevents premature closure by requiring explicit evidence documentation before routing.

---

### Principle 9 (NEW): Triage accuracy has inherent bounds; structural improvements approach but do not eliminate misclassification

**General insight:** ESI (Emergency Severity Index) — the best-validated structured triage system in medicine — achieves 59–72% accuracy under ideal conditions with trained practitioners, structured algorithms, and mandatory vital signs. Inter-rater reliability ranges κ = 0.45–0.94. "Quick-look" approaches produce significantly lower accuracy than vital-signs-integrated approaches.

Kahneman/Gigerenzer debate: "when faced with limited initial data, heuristic strategies actually outperform complex strategies." Fast-and-frugal heuristics are ecologically rational in stable, familiar domains. The implication: D+B anchors should be calibrated to data availability, not uniformly imposed.

**Project validation:** The empirical 63% interrupt rate (24/38 sessions) partially reflects genuine assessment difficulty, not solely process failure. The D+B anchors implement the highest-evidence mechanisms (mandatory data collection, structured reflection). Further structural additions face diminishing returns — the ESI research suggests the remaining accuracy gap requires better reasoning about available data, not more gates.

**What this adds:** A ceiling on expectations for triage accuracy improvements. The design skill's current Phase 0 structure (multiple D+B anchors, visible output blocks) is at or near the structural optimum. Remaining accuracy gains require better inputs (richer context, better recall), not additional enforcement structure.

---

### Principle 10 (NEW): Classification accuracy improves through systematic outcome feedback

**General insight:** Tetlock's Good Judgment Project established that calibration improves through explicit prediction → observable outcome → scoring feedback loops. Brier scores measure probabilistic forecast accuracy. Superforecasters achieved calibration differences of 0.01 between predicted and actual frequencies. Key finding: "Reading news and generating probabilities is insufficient without outcome verification" — the feedback loop is the learning mechanism, not the classification act itself.

Military After-Action Reviews (AAR, U.S. Army) implement the same structure: (1) what was supposed to happen, (2) what actually happened, (3) why the difference, (4) what to sustain/improve. AARs require the initial intent to be *recorded* — not reconstructed from memory — enabling accurate comparison.

**Project validation:** The design skill's Classification block already records the explicit prediction (classification + axes + evidence). The gap is downstream: no mechanism compares classification to execution evidence (files changed, agents used, corrections made). All triage corrections in the project's history came from explicit user intervention, not systematic measurement.

**Scope note:** This feedback loop belongs downstream of /design (at /orchestrate or /commit), not inside /design. The prediction side is complete; the outcome-comparison side needs to be built in downstream workflows.

---

## Adaptations

### Adapted from external frameworks

| External element | Adapted as | Rationale |
|-----------------|------------|-----------|
| Cynefin Clear/Complicated/Complex | Simple/Moderate/Complex triage | Three-tier routing; Chaotic and Disorder excluded |
| Stacey Matrix certainty × agreement | Implementation certainty × requirement stability | Named axes for classification criteria |
| IEEE 29148 validation activity | D+B anchors (tool calls before gates) | Observable evidence adapted from document-based to tool-call-based |
| Double Diamond problem/solution split | /requirements → /design routing | Diamond 1 = /requirements; Diamond 2 = /design |
| ADR context/decision/consequences | Design.md decision sections with tradeoffs | Adapted with explicit consequences per decision |
| NASA PDR/CDR | outline-corrector / design-corrector | Two review gates with differentiated criteria |
| **Stage-Gate required deliverables** | **Research report file before outline generation** | Gate enforcement through artifact presence, not prose |
| **Kahneman System 1/2** | **D+B anchors as System 2 activation** | Mandatory data collection changes cognitive process |
| **ESI vital signs** | **when-resolve.py + Glob/Grep before classification** | Mandatory structured data before assessment |
| **GJP explicit prediction + scoring** | **Classification block + downstream comparison** | Recorded prediction at classification; scoring at execution completion |
| **AAR planned-vs-actual** | **Classification evidence vs execution evidence** | Deviation analysis for triage criteria refinement |

### Project-specific additions (not in any external framework)

| Addition | Rationale |
|----------|-----------|
| D+B anchor pattern | Project-discovered mechanism for enforcing gate execution in LLM agents; now grounded in 5 external frameworks (IEEE 29148, Stage-Gate, DMAIC, NASA, A3) as project instantiation of universal artifact-requirement principle |
| Companion task Phase 0 enforcement | Multi-task /design invocations must process each task through full triage pipeline |
| Recall artifact persistence | Context window findings don't survive pipeline stages; materialized as file |
| Post-outline complexity re-check | Mid-task reassessment gate at outline → design boundary; Cynefin-motivated |
| Classification visible output block | Structured output format forcing explicit assessment before routing; grounded in premature closure checklist literature |
| Work Type Assessment | Independent dimension (Production/Exploration/Investigation) from complexity classification; artifact destination determines quality obligations |

### Deliberately excluded from external frameworks

| Excluded element | Rationale |
|-----------------|-----------|
| Cynefin Chaotic domain | No operational equivalent in software design workflow |
| Cynefin Disorder/Confusion domain | Assessment of "which domain?" is the triage step itself; meta-assessment is circular |
| ATAM utility tree | Full ATAM is resource-intensive (1-2 day team exercise); disproportionate for single-agent workflow |
| IEEE 29148 three-document output | Heavyweight; requirements.md + design.md covers essential content |
| Stacey Matrix quantitative zone boundaries | Stacey itself acknowledges boundaries require judgment |
| IDEO Design Thinking empathy phase | Principled but not structurally enforced; rationalization is as possible as current prose gates |
| Design Sprint (GV) time-boxing | Enforcement is social (team room); not applicable to single-agent context |
| Fast-and-frugal tree heuristics | Valid theory but no structural enforcement mechanism |
| ML classification calibration (Platt/temperature scaling) | Numerical probability calibration not applicable to categorical triage |

---

## Gap Analysis: Current Status

### Previously identified gaps (v1)

| Gap | Status | Evidence |
|-----|--------|----------|
| **Gap 1:** Requirements-clarity gate needs D+B anchor | **Mitigated** | Structured output block implemented; not full tool-call anchor but sufficient deliberation trigger |
| **Gap 2:** Classification criteria need named axes | **Closed** | Stacey axes (implementation certainty, requirement stability) implemented with visible output |
| **Gap 3:** Design output format lacks explicit tradeoffs | **Closed** | design-content-rules.md includes Decision Tradeoff Documentation section |
| **Gap 4:** Review gate criteria not differentiated | **Closed** | outline-corrector (PDR) and design-corrector (CDR) use distinct criteria |
| **Gap 5:** Companion task enforcement prose-only | **Closed** | Enumeration block requirement replaces prose rule with structural enforcement |
| **Gap 6:** No structured-bugfix triage path | **Closed** | Defect classification is now a first-class triage path |
| **Gap 7:** No triage accuracy feedback loop | **Deferred** | Scoped to downstream orchestration/commit workflows; prediction side complete. v2 grounding: GJP calibration (Tetlock), AAR planned-vs-actual (U.S. Army), ESI retrospective under/over-triage review |

### New gaps identified (v2)

### Gap 8: Research step needs artifact-based enforcement

**Principles:** 6 (observable evidence), Stage-Gate (required deliverables), DMAIC (phase deliverable checklist)

**Empirical evidence:** Pushback session (2e376b75) — designer rationalized skipping A.3-A.5 external research. Research protocol is prose-only in `references/research-protocol.md`. Same failure class as all other prose-only gates. User caught it 47 minutes later.

**External grounding:** Stage-Gate requires specific deliverables from each stage before gate review. DMAIC requires evidence to convince Sponsor. NASA SRR requires risk assessment and lessons-learned documentation as entrance criteria. A3 uses format-enforced sequencing. All converge: artifact requirement, not prose instruction.

**Fix applied:** A.3-4 (research) and A.5 (outline) separated into distinct steps. Research produces `plans/<job>/reports/research-<topic>.md`; A.5 gates on file existence before outline generation. Cascading dependency — outline step reads the report, absence blocks the path. Matches D+B anchor pattern, grounded in 4 additional external frameworks.

**Status: Closed.**

### Gap 9: ~~Downstream triage feedback mechanism~~ — MERGED into Gap 7

Gap 9 described the same mechanism as Gap 7 with additional v2 grounding (GJP, AAR, ESI). Merged: v2 evidence folded into Gap 7's evidence column. Proposed mechanism:
- At classification: Classification block already records prediction (in place)
- At execution completion: Surface execution evidence (files changed, agent count, behavioral code, corrections)
- At retrospective: Compare classification to execution evidence; surface systematic misclassification as learning entry
- Detection is automatable; correction requires human judgment (criteria updates)
- Complex↔Moderate boundary accuracy is priority metric (26% of sessions are Moderate)
- Implementation belongs in orchestration or commit workflows, not in /design

---

## Empirical Validation Summary (v2)

**Source:** Session scraper + batch extraction across 38 design sessions (full population of /design Skill invocations)

### Full population (n=38, batch extraction — v2 with fixes)

| Metric | Value | Significance |
|--------|-------|-------------|
| Total sessions with /design | 38 | Full population across main + worktrees |
| Completion rate (commit proxy) | 33/38 (87%) | Most sessions produce work output |
| Sessions with interrupts | 24/38 (63%) | Majority of design sessions have user interrupts |
| Classification: Complex | 17/38 (45%) | Plurality of design invocations are Complex |
| Classification: Moderate | 10/38 (26%) | Significant portion — second most common |
| Classification: Simple/Shortcircuit | 4/38 (11%) | Low — most /design invocations are non-trivial |
| Classification: Unknown | 7/38 (18%) | Genuinely unclassifiable (aborted/mixed sessions) |
| Review gates present (OC+DC) | 8/38 (21%) | Only recent sessions (≥2026-02-23) have two-gate review |
| Agent count range | 0–10 | Median ~2 |

### Deep sample (n=8, session scraper tree)

| Metric | Value | Significance |
|--------|-------|-------------|
| Design-corrector fix rate | 100% self-resolved | CDR review adds measurable value |
| Research skip observed | 1/3 complete sessions | Prose-only research gate fails |
| Classification timing correlation | Fast (<30s) → worse outcomes | D+B anchors justified — deliberation improves accuracy |
| Average agents (complete sessions) | 3 | Delegation load for Complex tasks |
| Average entries (complete sessions) | 209 | Session complexity metric |

### Sampling bias corrections

The initial n=8 sample was cherry-picked for diversity, which overrepresented problematic sessions:
- **Pipeline completion rate:** n=8 showed 37.5%; n=38 shows 87%. The initial sample was biased toward aborted/partial sessions.
- **Phase 0 intervention rate:** n=8 showed 50% (4/8); n=38 shows 63% (24/38) sessions with at least one interrupt. The n=8 rate was directionally correct but the denominator was too small.
- **Classification coverage:** v1 extraction had 39% Unknown due to markdown bold breaking regexes. v2 fixes reduced Unknown to 18% (7/38 genuinely unclassifiable). Complex and Moderate are the dominant categories (45% + 26%).
- **Review gate coverage:** Two-gate review (outline-corrector + design-corrector) exists only in 8 most recent sessions. Older sessions predating this infrastructure cannot validate Principle 7.

**Coverage gaps in session data:**
- Post-outline complexity downgrade: not observed (0 events in n=38)
- /requirements reroute: not observed (0 events)
- Companion task enumeration: not observed (0 events)
- Defect classification path: not observed (0 events)
- Outline-corrector effectiveness: undersampled (1 complete run in n=8)

---

## Grounding Assessment

**Quality label:** Strong

**Evidence basis (v2):**
- 9 primary framework clusters with citations and authority assessments (6 original + 3 new)
- 10 principles each grounded in ≥1 external framework with named citations (8 original + 2 new)
- 10 internal failure patterns with specific commit hashes mapped to external principles
- 38 design sessions batch-extracted (full population); 8 deep-parsed with session scraper tree
- 8 gaps tracked (7 original + 1 new; Gap 9 merged into Gap 7), with 6 closed, 1 mitigated, 1 deferred
- 5 branch artifacts retained as audit evidence

**What was searched (v2 additions):**
- "design process mandatory investigation phase enforcement methodology"
- "triage assessment speed vs accuracy framework methodology"
- "rapid assessment cognitive bias triage decision making"
- "classification accuracy feedback loop process improvement"
- "design thinking fast and slow Kahneman"
- "ESI triage accuracy systematic review"
- "superforecasting calibration feedback loop"
- "after-action review structured retrospective"
- Session scraper: 38 sessions batch-extracted (full population), 8 deep-parsed across main repo + 7 worktrees

**Remaining ungrounded elements:**
- **Classification thresholds:** Neither Cynefin nor Stacey provides quantitative boundaries. ESI confirms triage requires judgment even with structured systems.
- **Option-generation methodology:** ADR and ATAM cover documentation and evaluation of decisions, not the reasoning process for generating options.
- **D+B anchor calibration:** When to require full tool-call anchor vs structured output block remains project-specific judgment. The ESI/Kahneman research suggests calibrating to data availability, but no framework provides operational thresholds.

---

## Sources

### Original sources (v1)

| Source | Type | Used for |
|--------|------|----------|
| [Cynefin Framework — Wikipedia](https://en.wikipedia.org/wiki/Cynefin_framework) | Primary (Snowden/IBM) | Complexity domain classification, routing, domain-shift warning |
| [Stacey Matrix — Praxis Framework](https://www.praxisframework.org/en/library/stacey-matrix) | Primary (Stacey) | Two-axis triage operationalization, named axes |
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | International standard | Requirements completeness criteria, validation as distinct activity |
| [ADR — adr.github.io](https://adr.github.io/) | Primary (Nygard) | Decision documentation format, context/consequences structure |
| [ADR Process — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html) | Secondary (AWS adoption) | ADR lifecycle, review steps |
| [Double Diamond — Wikipedia](https://en.wikipedia.org/wiki/Double_Diamond_(design_process_model)) | Primary (Design Council) | Problem/solution space separation |
| [Double Diamond — Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/double-diamond) | Secondary (practitioner) | Software engineering adaptation |
| [NASA PDR/CDR — NPR 7123.1](https://nodis3.gsfc.nasa.gov/displayCA.cfm?Internal_ID=N_PR_7123_001A_&page_name=AppendixG) | Standard (NASA) | Staged design review gates |
| [ATAM — CMU SEI](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/) | Academic (SEI) | Quality attribute utility tree |
| [Documenting Architecture Decisions — Nygard](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | Primary (origin) | ADR motivation, Y-statement format |

### New sources (v2)

| Source | Type | Used for |
|--------|------|----------|
| [Stage-Gate — stage-gate.com](https://www.stage-gate.com/blog/the-stage-gate-model-an-overview/) | Primary (Cooper) | Gate enforcement through required deliverables |
| [Stage-Gate Process — Toolshero](https://www.toolshero.com/innovation/stage-gate-process/) | Secondary (practitioner) | Discovery phase activities, gatekeeper role |
| [DMAIC Tollgate Reviews — Six Sigma Study Guide](https://sixsigmastudyguide.com/dmaic-tollgate-reviews/) | Secondary (practitioner) | Define phase deliverable checklist |
| [DMAIC Tollgate Define — Master of Project](https://blog.masterofproject.com/tollgate-review-check-list/) | Secondary (practitioner) | Evidence standard for phase advancement |
| [NASA NPR 7123.1D Appendix G](https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_7123_001D_&page_name=AppendixG) | Standard (NASA) | SRR/SDR entrance criteria; cascading gate dependencies |
| [A3 Problem Solving — Montana State](https://www.montana.edu/dsobek/a3/steps.html) | Academic (practitioner) | Format-enforced investigation sequencing |
| [Toyota A3 — Orca Lean](https://www.orcalean.com/article/toyota's-a3-thinking-and-root-cause-analysis:-a-reality-driven-approach-to-problem-solving) | Secondary (Lean practitioner) | Gemba observation requirement |
| [Design Thinking Fast and Slow — Design Science](https://www.cambridge.org/core/journals/design-science/article/design-thinking-fast-and-slow-a-framework-for-kahnemans-dualsystem-theory-in-design/A200DC637BBDC982D288FC4F8A112DE7) | Peer-reviewed journal | Dual-process theory applied to design triage |
| [ESI Triage Accuracy — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7211387/) | Peer-reviewed medical | Triage accuracy bounds (59-72%); vital signs as mandatory data |
| [Triage Performance Systematic Review — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0196064418312824) | Peer-reviewed medical | Cross-system triage accuracy; inter-rater reliability |
| [Triage Future Direction — BMC Emergency Medicine](https://bmcemergmed.biomedcentral.com/articles/10.1186/s12873-018-0215-0) | Peer-reviewed medical | Quick-look vs systematic assessment accuracy gap |
| [Premature Closure — FHEA](https://www.fhea.com/resource-center/cognitive-errors-in-clinical-diagnosis-availability-bias-and-premature-closure/) | Medical education | Premature closure mechanism; structured reflection |
| [Checklist for Availability Bias — Design Science](https://www.cambridge.org/core/journals/design-science/article/validation-of-a-checkliststyle-intervention-for-mitigation-of-availability-bias-in-professional-designers/06F89C9C009A5B744385EE643BB20012) | Peer-reviewed | Validated checklist reduces availability bias in designers |
| [GJP Evidence — AI Impacts](https://aiimpacts.org/evidence-on-good-forecasting-practices-from-the-good-judgment-project/) | Research synthesis | Brier score calibration; explicit prediction + outcome scoring |
| [Superforecasting — HBR](https://hbr.org/2016/05/superforecasting-how-to-upgrade-your-companys-judgment) | Tetlock/HBR | Systematic feedback + training improves calibration |
| [After-Action Review — Wikipedia](https://en.wikipedia.org/wiki/After-action_review) | Encyclopedic | Four-step AAR structure |
| [AAR — U.S. Army FM 7-0](https://www.first.army.mil/Portals/102/FM%207-0%20Appendix%20K.pdf) | Military doctrine | Formal AAR process; intent recording requirement |
| [Definition of Ready — Atlassian](https://www.atlassian.com/agile/project-management/definition-of-ready) | Industry practitioner | Entry validation criteria; graduated criteria by work type |

**Internal evidence:** `design-skill-internal-codebase.md` (10 failure patterns), `design-session-empirical-data.md` (8 session traces), `design-grounding-internal-update.md` (cross-reference analysis), `design-grounding-external-update.md` (targeted external research).
