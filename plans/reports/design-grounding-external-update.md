# Design Skill Grounding: External Research Update

**Date:** 2026-02-26
**Purpose:** External grounding for three gap areas identified from empirical session analysis not addressed by prior framework research (Cynefin, Stacey, IEEE 29148, Double Diamond, ADR, NASA PDR/CDR)
**Input:** `design-grounding-internal-update.md` — Finding A (research step rationalization), Pattern 3 (Phase 0 50% intervention rate), Pattern 8 (classification timing vs accuracy), Gap 7 (no triage accuracy feedback loop)

---

## Gap Area 1: Research Phase Enforcement

### Problem Statement

Empirical finding (pushback session, commit `2e376b75`): designer rationalized away the external research phase (A.3-A.5) with "framework was obvious," proceeding without WebSearch or Context7 calls. User intervention 47 minutes later. The research step is prose-only in `references/research-protocol.md` — same failure class as all other prose-only gates.

**Research question:** What established methodologies enforce investigation/research phases structurally — not just as instructions — and prevent rationalization?

### Frameworks Found

**1. Stage-Gate Process (Cooper, 1988–present)**

The Stage-Gate® model structures innovation as sequential stages separated by gate reviews. Stage 0 (Discovery) and Stage 1 (Scoping) are mandatory pre-design phases. Gates function as "tough decision meetings where critical go/kill decisions are made" — not project status updates. Stage 1 requires market research, Voice of Customer (VoC), technical feasibility studies, and risk assessment before Gate 1 review can proceed.

Gate enforcement mechanism: Each gate requires **specific deliverables from the prior stage**. Gatekeepers confirm deliverables exist before authorizing the next stage. If discovery work was not done, the gate review reveals this through missing artifacts, not through reasoning about whether discovery was needed.

Limitation: Cooper acknowledges that in practice "phase gates are often not enforced properly as evidence can be ignored or overridden." Structural enforcement (required artifacts) is necessary but not sufficient — organizational incentives can override gate decisions. For an LLM agent context, the artifact requirement is the exploitable mechanism.

Recent development (2024): Research re-examined the model by "advocating for the recognition of the Discovery Phase as Stage 1, emphasizing its essential role in aligning initial ideation with strategic goals." Formalization of discovery improves "early-stage decision-making and mitigates risks."

**Applicability:** High. The gate's mechanism — require a specific deliverable before routing continues — is exactly the D+B anchor pattern used elsewhere in the design skill. A research report file (not a prose gate) would enforce the research phase structurally.

**2. DMAIC Tollgates (Six Sigma)**

DMAIC (Define-Measure-Analyze-Improve-Control) uses tollgate reviews at each phase boundary. The Define phase requires a Project Charter, problem statement with baseline metrics, high-level process maps, and financial measures before a Sponsor can authorize the Measure phase.

Enforcement mechanism: The tollgate is a "traffic light" requiring a Champion review. If critical activities were omitted, Sponsors may recommend "discontinuing the Six Sigma project" or require additional Define phase work. The gate enables management to either halt projects or redirect resources.

The Define phase specifically enforces that "enough activities occurred during this DMAIC phase" — not a judgment call but a checklist of required outputs. Evidence you could use to convince your Sponsor must be prepared as a presentation including "metrics and data showing you achieved designated deliverables."

**Applicability:** High. The tollgate's structure (checklist of required outputs, evidential standard for advancement) maps directly to what a research step anchor needs: a structured output file that proves investigation happened. The key mechanism is that deliverables are output artifacts, not internal reasoning steps.

**3. NASA Systems Engineering Technical Reviews (NPR 7123.1D)**

NASA's System Requirements Review (SRR) and System Definition Review (SDR) enforce investigation completeness through entrance criteria. SRR requires:
- Risk assessment for all significant technical areas with mitigation strategies
- Identification of lessons learned from prior programs
- Technology readiness evaluation (gaps, development needs)
- Compliance verification documentation

SDR (subsequent gate) requires **baselined** versions of artifacts that were only preliminary at SRR — enforcing incremental maturity rather than one-pass completion.

Cascading requirement: "The program has successfully completed the previous planned life-cycle reviews and all RFAs and RIDs have been addressed and resolved." This prevents skipping reviews by making later reviews impossible without prior review evidence.

The document establishes that cascading dependencies are the structural mechanism: you cannot get through Gate N+1 if Gate N artifacts are missing. No explicit "investigation was insufficient" exception — the deliverables either exist or the review cannot proceed.

**Applicability:** Moderate-High. The cascading dependency mechanism is architecturally cleaner than optional gates. For agentic workflows, this suggests: if a research report file does not exist, the routing step cannot proceed — not as a prose instruction but as a conditional branch that reads the file.

**4. Toyota A3 Problem Solving**

A3 methodology requires mandatory current-state documentation before any countermeasure can be proposed. The A3 report structure: Background → Current State → Problem Statement → Root Cause Analysis → Target State → Countermeasures. Countermeasures cannot appear before Current State.

The structural constraint is the page format: A3 is a single sheet of A3 paper (11×17 in). The current state section must be populated — physically — before any solution-space content. The layout enforces sequence.

The investigation standard: "Toyota suggests that problem-solvers observe the work processes first hand and document observations. They quantify the magnitude of the problem." The emphasis is on **direct observation, not reasoning** — you cannot substitute "I know the current state" for actual measurement.

**Applicability:** Moderate. The physical format constraint (you must fill the current state section before writing countermeasures) is analogous to requiring a research output file before routing. The mechanism is blocking: you literally cannot complete the document without the required prior sections. For LLM agents, the analog is: produce the research report before the outline-generation step receives any input.

### Key Mechanisms Applicable to the Design Skill

Across these frameworks, three structural enforcement mechanisms recur:

| Mechanism | Frameworks | Adaptation for Design Skill |
|-----------|------------|------------------------------|
| **Required artifact** | Stage-Gate, DMAIC, NASA | Research report file must exist before routing continues — not "read research-protocol.md" but "write research report to `plans/<job>/reports/research-<topic>.md`" |
| **Cascading gate dependency** | NASA (SRR → SDR chain) | Research report file is read by subsequent step; absence is a branch condition, not a prose check |
| **Structured format as enforcement** | A3, DMAIC checklists | Output format (frameworks considered, findings per framework, gaps identified) forces completeness — you cannot fill the template without having done the work |

The existing D+B anchor pattern (principle 6 in the grounding report) captures all three: tool-call (file write), observable output (structured report), read by next step (cascading dependency). The gap is that Phase A.3-A.5 doesn't apply this pattern.

### What Was Excluded

- **IDEO Design Thinking empathy phase:** Principled but not structurally enforced. The empathy phase is required by process description, not by a gate with deliverable requirements. Rationalization is as possible here as in the current research protocol. Not applicable.
- **Lean Startup validated learning:** Concerned with product-market fit measurement, not design investigation phases. Different problem domain.
- **Design Sprint (GV):** Requires a research/understand day, but enforcement is social (team room, time-boxing) not structural. Not applicable to single-agent context.

---

## Gap Area 2: Triage Entry Friction

### Problem Statement

Empirical finding (Pattern 3): 50% of design sessions had user intervention at Phase 0 (4 of 8 sessions). Pattern 8: sessions with fast classification (<30 sec) correlated with downstream issues (confusing prompts, misaligned triage); deliberate classification (~2 min) correlated with better outcomes.

Two sub-problems:
1. What causes the high intervention rate at triage? Is 50% inherent to complexity assessment, or a failure of the current gates?
2. How do classification systems balance deliberation quality against speed? What mechanisms ensure appropriate depth at process entry?

**Research question:** What frameworks address rapid vs deliberate assessment at process entry points, and how do they prevent premature closure?

### Frameworks Found

**1. Kahneman's Dual-Process Theory Applied to Design (System 1 / System 2)**

Kahneman's System 1 (fast, intuitive, heuristic) vs System 2 (slow, deliberate, analytical) framework has been explicitly applied to design processes in published research: "Design thinking, fast and slow: A framework for Kahneman's dual-system theory in design" (Design Science, Cambridge Core).

System 1 provides pattern recognition that enables rapid routing in familiar domains. System 2 provides deliberate analysis for novel or complex situations. The critical finding: "System 1 also provides a tool for responding to uncertain or ambiguous situations where the use of analytical reasoning would be impossible or impractical by replacing complex problems by simpler ones." This substitution — replacing the actual complexity assessment question with a simpler pattern-match — is the failure mode behind fast misclassification.

For design entry triage specifically: System 1 pattern-match ("this looks like a Simple task") activates before System 2 analysis ("is the approach actually known? are requirements actually stable?"). Once a plausible classification appears, System 1 commits and System 2 doesn't engage.

The debate between Kahneman (fast heuristics create systematic errors) and Gigerenzer (fast-and-frugal heuristics are ecologically rational) is directly relevant: "when faced with limited initial data, heuristic strategies actually outperform complex strategies." This means the design skill's D+B anchors that force System 2 engagement should be calibrated to the amount of data available at triage — forcing full analysis when pattern-match data is sufficient wastes cost; allowing pattern-match when data is insufficient produces the Pattern 8 failures.

**Applicability:** High. Pattern 8's speed-accuracy correlation is exactly what Kahneman's dual-process theory predicts. The D+B anchor pattern (Classification Gate with mandatory tool-call) is the structural mechanism for activating System 2 when System 1 would otherwise commit. This provides external grounding for the existing anchor pattern.

**2. Emergency Medical Triage (ESI/Manchester Triage System)**

Emergency Severity Index (ESI) is a 5-level triage system used in emergency departments. Key empirical data:
- Overall triage accuracy across multiple studies: 59–72%
- Inter-rater reliability (how often two nurses assign the same level): κ = 0.45–0.94
- Under-triage rate: ~25% of cases assigned lower acuity than actual

The speed-accuracy tradeoff in emergency triage is well-documented: "a prevalence of 'quick look' triage approaches that do not rely on physiologic data to make acuity decisions." Quick-look approaches (System 1) produce lower accuracy than vital-signs-integrated approaches (System 2).

The intervention that improved accuracy: introducing vital signs as a **mandatory parameter**. "When vital signs were introduced as a necessary parameter, researchers reported that the framework for decision making changed... with an increase in accuracy of acuity assignation." Mandatory data collection changed the cognitive process, not just the inputs.

**Applicability:** Moderate-High. The ESI research provides an empirical model for why Pattern 8 occurs and what fixes it. The analog to "vital signs" in design triage is the mandatory data collection that D+B anchors enforce:
- `when-resolve.py` = collecting project-history vital signs before classification
- `Glob`/`Grep` behavioral code check = collecting structural data before classification

Both anchors change the cognitive process from pattern-match to evidence-based assessment. The ESI research confirms this is the right mechanism.

Limitation: ESI accuracy (59–72%) shows triage is inherently difficult even with structured systems. A 50% intervention rate in design sessions may reflect genuine complexity assessment difficulty, not a solvable enforcement problem. The goal is calibrated accuracy, not elimination of all misclassifications.

**3. Clinical Diagnosis: Premature Closure**

Medical diagnostic research identifies "premature closure" as the dominant triage failure mode: "the failure to consider alternative diagnoses after the initial impression." Premature closure is mechanistically linked to anchoring bias — "the tendency to lock onto salient features... and cling to an initial diagnosis."

Prevention mechanisms that have empirical support:
- **Structured reflection checklists** that force systematic consideration before committing: "Are all the patient's findings accounted for by my diagnosis? What are the consequences of this diagnosis? What else could it be?"
- **Diagnostic timeouts**: a deliberate pause to consider alternatives before disposition
- **Checklist-style interventions**: peer-reviewed research (Design Science) validated that "checklist-style interventions for mitigation of availability bias in professional designers" reduced systematic errors

The key finding: "strategies such as structured reflection, use of diagnostic checklists... introduce a healthy dose of System 2 thinking into the diagnostic process, thereby counteracting the pitfalls of our heuristic-driven System 1."

**Applicability:** High. Premature closure is the exact mechanism behind Pattern 8 failures. Fast classification produces premature closure; deliberate classification involves structured reflection. The Classification Gate's visible output block requirement ("produce this classification block before routing") is the project-specific implementation of a structured reflection checklist. This provides external grounding for the current gate structure.

**4. Agile Definition of Ready (DoR)**

Definition of Ready establishes criteria a work item must meet before it can enter a sprint. DoR enforces entry validation — the item cannot proceed until prerequisites are met. Unlike prose instructions ("ensure requirements are clear"), DoR criteria are pass/fail per item.

Key finding from Agile research: "A DoR can lead to delays as teams chase down the completion of a checklist before starting their work." This is the explicit speed-accuracy tradeoff: DoR improves accuracy but introduces friction.

The calibration recommendation: "creating different criteria for different types of work, where urgent bug fixes might have simpler criteria than new feature development." This is the graduated friction principle — complexity of entry validation should match complexity of work, not be uniform.

**Applicability:** Moderate. DoR provides the principle that entry validation should be calibrated to work type, not uniform. This aligns with the design skill's classification-first approach: Simple tasks get lighter downstream process; Complex tasks get full A-B-C pipeline. The implication for triage friction: Phase 0 gates can be simpler for clearly Simple tasks and more elaborate for borderline cases. However, the challenge is that triage happens before work type is established — this is the bootstrapping problem.

### Key Mechanisms Applicable to the Design Skill

| Mechanism | Frameworks | Current design skill status | Gap |
|-----------|------------|------------------------------|-----|
| Mandatory data collection before assessment | ESI (vital signs), D+B anchors | Implemented: `when-resolve.py` + behavioral code check | None — mechanism correct |
| Structured reflection checklist | Premature closure literature, DoR | Implemented: Classification Gate visible output block | None — mechanism correct |
| Cognitive process change (not just input change) | ESI, Kahneman | Partially: D+B anchors change the process, but anchors are sequential (do tool calls → look at output) | Gap: require reasoning about the output before routing, not just producing it |
| Graduated validation depth by complexity | DoR calibration | Not implemented: same Phase 0 gates regardless of apparent complexity | Potential optimization: but creates circularity (complexity unknown until after triage) |

**Key insight from the research:** The 50% intervention rate at Phase 0 may not be fully solvable. ESI — the best-validated structured triage system in medicine — achieves 59–72% accuracy under ideal conditions. The design skill's Phase 0 intervention rate reflects both genuine complexity assessment difficulty and process friction. The D+B anchors already implement the highest-evidence mechanisms (mandatory data collection, structured reflection). Further gains require either better data inputs or higher-quality reasoning about the data, not additional gate structure.

### What Was Excluded

- **Machine learning triage approaches:** Multiple papers on AI-assisted ESI triage exist. Not applicable — the design skill's triage is performed by the same LLM executing the work; a separate classification model would require delegation overhead.
- **Fast-and-frugal tree heuristics (Gigerenzer):** Ecological rationality arguments for heuristic accuracy are valid but don't provide structural enforcement mechanisms. Theoretical support for allowing heuristic triage in stable domains, but no actionable process improvement.

---

## Gap Area 3: Triage Accuracy Feedback Loops

### Problem Statement

Empirical finding (Gap 7 from grounding report): No mechanism to verify whether complexity classification was correct post-execution. All corrections came from explicit user intervention, not systematic measurement. The grounding report scoped this as "a monitoring enhancement — downstream of /design skill itself."

**Research question:** What frameworks implement classification accuracy feedback? How do iterative systems self-correct their initial assessments?

### Frameworks Found

**1. Tetlock's Good Judgment Project (Superforecasting)**

Philip Tetlock and the Good Judgment Project (GJP) established the empirical basis for forecasting accuracy improvement through systematic feedback. Key mechanisms:

- **Scoring predictions against outcomes**: "You need to actually score your predictions so that you know how wrong you were." Calibration requires comparing predicted probabilities to actual outcome frequencies.
- **Brier scores**: A proper scoring rule measuring probabilistic forecast accuracy. Superforecasters demonstrated "the average difference between a probability they use and the true frequency of occurrence is 0.01" — very high calibration.
- **Year-over-year tracking**: Correlation between forecaster accuracy across seasons = 0.65. Accuracy is a persistent skill, improvable over time with feedback.
- **Randomized training trials**: Short training programs (40 min) covering reference-class forecasting, biases, and Bayesian reasoning showed persistent accuracy improvements (effects lasted ≥1 year).

Mechanism: "Reading news and generating probabilities is insufficient without outcome verification." The feedback loop requires three components: (1) explicit prediction, (2) observable outcome, (3) scoring/comparison.

**Applicability:** High for mechanism design; moderate for direct application. The design skill's triage produces a classification (Simple/Moderate/Complex) that can be scored retrospectively against execution evidence (how many files changed? was behavioral code involved? how many agents needed?). The prediction is explicit; the outcome is observable; the comparison mechanism is the gap.

The GJP finding that calibration improves through training with feedback suggests that a systematic feedback loop — even a lightweight one — would improve the designer's classification accuracy over time. No feedback = no learning signal.

**2. Military After-Action Review (AAR)**

The U.S. Army created AARs in the 1970s as structured post-execution retrospectives. AAR occurs "within a cycle of establishing the leader's intent, planning, preparation, action and review" and "begins with a clear comparison of intended versus actual results."

The four-step AAR process:
1. What was supposed to happen? (initial assessment/plan)
2. What actually happened? (observed outcome)
3. Why was there a difference? (root cause of deviation)
4. What should be sustained or improved? (corrective action)

The critical structural element: "without a clear understanding of the initial plan, it's difficult to accurately assess deviations or successes." AARs require the initial intent to be recorded — not reconstructed from memory — to enable accurate comparison.

**Applicability:** High. The AAR structure directly maps to triage accuracy feedback:
- Step 1: Classification at entry (Simple/Moderate/Complex, with explicit criteria that triggered the decision)
- Step 2: Execution evidence (actual complexity encountered: files changed, agents used, corrections made)
- Step 3: Deviation root cause (which classification criteria mislabeled the task)
- Step 4: Criteria refinement (update triage criteria based on systematic pattern)

The AAR requirement for a recorded initial plan maps to the design skill's visible Classification block (lines 106-113). This block already records the criteria that triggered the classification. The gap is that this block is not compared to execution evidence at task completion.

**3. Agile Sprint Retrospective**

Scrum retrospectives occur after each sprint to identify process improvements. The team assesses "if the iteration goals were met" and reflects on "one or two things they can do better in the next iteration."

Sprint retrospective limitation: "Agile methods do not prescribe how these improvement actions should be identified, managed or tracked in detail, with the approaches to detect and remove problems often based on intuition and prior experiences and perceptions of team members." The retrospective's improvement identification is unstructured — no systematic comparison of planned vs actual.

ESI triage calibration finding: triage accuracy can be measured against outcomes (hospitalization rate, disposition decisions) to calculate under/over-triage rates. Regular retrospective review of under/over-triage rates, coupled with "regular refresher triage training, collaboration between emergency departments, and continuous monitoring," improved accuracy over time.

**Applicability:** Moderate. Sprint retrospectives provide the mechanism (structured periodic review) but lack the systematic measurement component. The ESI triage accuracy measurement (comparing classification to actual outcome) is the more applicable mechanism — it's classification-specific and directly analogous.

**4. AI Feedback Loop (Active Learning / Human-in-the-Loop)**

Research on ML classification feedback loops shows:
- "Continuously evaluating the classifier against a curated golden set of labeled data" detects accuracy drift
- "Any statistically significant negative trend in F1-score serves as a definitive indicator that the model is no longer aligned with ground truth"
- Human-in-the-loop approaches: "incorporating human oversight into the learning process helps correct errors and reduce bias"

The feedback loop mechanism: collect outcomes → score against classification → detect systematic drift → retrain or recalibrate.

**Applicability:** Moderate. The mechanism is directly applicable (collect execution outcomes, compare to classifications, detect systematic patterns), but the "retrain" step doesn't apply to LLM agents. The applicable component is: collect a structured record of (classification, execution outcome, deviation) for each /design session, and periodically review for systematic misclassification patterns.

This is equivalent to what the GJP does: explicit prediction → observable outcome → comparison → calibration.

### Key Mechanisms Applicable to the Design Skill

| Mechanism | Frameworks | Adaptation for Design Skill |
|-----------|------------|------------------------------|
| **Explicit prediction recording** | GJP, AAR | Classification block already records explicit classification + criteria. Gap: this block is not preserved post-execution for comparison |
| **Outcome measurement** | GJP (Brier scores), ESI (under/over-triage rate), AAR (intended vs actual) | Execution evidence: file count, agent count, correction events. These are observable from git history |
| **Systematic deviation comparison** | AAR (planned vs actual), GJP (prediction vs outcome) | New mechanism: after /commit, compare classification block to execution evidence |
| **Calibration trigger** | ESI (refresher training when under/over-triage detected), GJP (training on detected biases) | For LLM agents: learning entry when systematic misclassification detected; criteria refinement for next design session |

### The Feedback Loop Design

Combining the GJP, AAR, and ESI mechanisms, a minimal feedback loop for design triage:

**At classification (already done):** Record visible Classification block: `Classification: [Simple/Moderate/Complex] | Axes: implementation certainty [H/M/L] | requirement stability [H/M/L] | Evidence: [what was examined]`

**At execution completion (new):** Surface execution evidence: files changed, agent count, correction count, behavioral code involvement (yes/no). This can be derived from git log + worktree history.

**At retrospective (new):** Compare classification to execution evidence. If `Complex` classification and ≤2 files changed, no agents used → over-classification. If `Simple` classification and multi-file behavioral changes occurred → under-classification. Both are candidates for learning entries.

**Detection vs correction:** The frameworks distinguish detection (finding when classification was wrong) from correction (fixing the criteria). Detection is automatable (compare classification to execution evidence). Correction requires human judgment (update triage criteria). The feedback loop should automate detection and prompt human correction.

**Scope confirmation:** This feedback loop belongs downstream of the /design skill (at /orchestrate or /commit), not inside /design itself. The grounding report's scope note (lines 221-229) is confirmed by this research: the detection mechanism requires execution evidence that doesn't exist at design time.

### What Was Excluded

- **Deep learning model calibration (Platt scaling, temperature scaling):** Numerical probability calibration for statistical classifiers. Not applicable — design triage produces categorical classifications, not probability distributions.
- **Retrospective assessment scales (medical):** Clinical audit tools for retrospective case review. Methodologically sound but operationally heavy — designed for human teams reviewing 50+ cases, not for per-session automated comparison.

---

## Sources

| Source | Authority | Gap Area | Key Mechanism Extracted |
|--------|-----------|----------|------------------------|
| [Stage-Gate International: The Stage-Gate Model Overview](https://www.stage-gate.com/blog/the-stage-gate-model-an-overview/) | High — Robert Cooper's canonical source | Gap 1 | Deliverable requirements at gate; go/kill decisions based on artifact presence |
| [Stage-Gate Process — Toolshero explanation](https://www.toolshero.com/innovation/stage-gate-process/) | Medium — secondary practitioner | Gap 1 | Discovery phase activities, gatekeeper role |
| [DMAIC Tollgate Reviews — Six Sigma Study Guide](https://sixsigmastudyguide.com/dmaic-tollgate-reviews/) | Medium — practitioner standard | Gap 1 | Define phase deliverable checklist; traffic-light mechanism |
| [DMAIC Tollgate: 12 Questions for Define Stage — Master of Project](https://blog.masterofproject.com/tollgate-review-check-list/) | Medium — practitioner | Gap 1 | Specific Define phase questions; evidence standard for advancement |
| [NASA NPR 7123.1D Appendix G: Technical Review Entrance and Success Criteria](https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_7123_001D_&page_name=AppendixG) | High — NASA official standard | Gap 1 | SRR/SDR entrance criteria; cascading gate dependencies; lessons-learned requirement |
| [A3 Problem Solving — Montana State University](https://www.montana.edu/dsobek/a3/steps.html) | Medium — academic practitioner | Gap 1 | Mandatory current-state section before countermeasures; format-enforced sequencing |
| [Toyota A3 Problem Solving — Orca Lean](https://www.orcalean.com/article/toyota's-a3-thinking-and-root-cause-analysis:-a-reality-driven-approach-to-problem-solving) | Medium — Lean practitioner | Gap 1 | Gemba observation requirement; document structure as sequence enforcement |
| [Design Thinking, Fast and Slow — Design Science / Cambridge Core](https://www.cambridge.org/core/journals/design-science/article/design-thinking-fast-and-slow-a-framework-for-kahnemans-dualsystem-theory-in-design/A200DC637BBDC982D288FC4F8A112DE7) | High — peer-reviewed journal | Gap 2 | Dual-process theory applied to design; System 1 substitution mechanism |
| [System 1 and System 2 Thinking — The Decision Lab](https://thedecisionlab.com/reference-guide/philosophy/system-1-and-system-2-thinking) | Medium — educational | Gap 2 | System 1/2 characteristics; complexity-assessment substitution |
| [Triage Assessment Accuracy — ESI Systematic Review (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7211387/) | High — peer-reviewed medical | Gap 2, Gap 3 | ESI accuracy (67%), vital signs as mandatory data; under-triage mechanisms |
| [Triage Performance in Emergency Medicine: Systematic Review](https://www.sciencedirect.com/science/article/abs/pii/S0196064418312824) | High — peer-reviewed medical | Gap 2, Gap 3 | Cross-system triage accuracy comparison; inter-rater reliability data |
| [Triage Review: Future Direction — BMC Emergency Medicine](https://bmcemergmed.biomedcentral.com/articles/10.1186/s12873-018-0215-0) | High — peer-reviewed medical | Gap 2 | Quick-look vs systematic assessment accuracy gap |
| [Cognitive Errors in Clinical Diagnosis: Premature Closure — FHEA](https://www.fhea.com/resource-center/cognitive-errors-in-clinical-diagnosis-availability-bias-and-premature-closure/) | Medium — medical education | Gap 2 | Premature closure mechanism; anchoring bias; structured reflection checklist |
| [Checklist Intervention for Availability Bias in Designers — Design Science / Cambridge Core](https://www.cambridge.org/core/journals/design-science/article/validation-of-a-checkliststyle-intervention-for-mitigation-of-availability-bias-in-professional-designers/06F89C9C009A5B744385EE643BB20012) | High — peer-reviewed | Gap 2 | Validated checklist reduces availability bias in design triage |
| [Definition of Ready — Atlassian](https://www.atlassian.com/agile/project-management/definition-of-ready) | Medium — industry practitioner | Gap 2 | Entry validation criteria; speed-accuracy tradeoff; graduated criteria by work type |
| [Good Judgment Project Evidence — AI Impacts](https://aiimpacts.org/evidence-on-good-forecasting-practices-from-the-good-judgment-project/) | High — GJP research synthesis | Gap 3 | Brier score calibration; explicit prediction + outcome scoring; training effect |
| [Superforecasting — HBR](https://hbr.org/2016/05/superforecasting-how-to-upgrade-your-companys-judgment) | High — Tetlock/HBR | Gap 3 | Systematic feedback + training improves calibration; 0.65 year-over-year accuracy correlation |
| [After-Action Review — Wikipedia](https://en.wikipedia.org/wiki/After-action_review) | Medium — encyclopedic | Gap 3 | Four-step AAR structure; planned vs actual comparison; Army origin |
| [After-Action Review — U.S. Army FM 7-0 Appendix K](https://www.first.army.mil/Portals/102/FM%207-0%20Appendix%20K.pdf) | High — military doctrine | Gap 3 | Formal AAR process; intent recording requirement; deviation analysis |
| [Agile Retrospective — Scaled Agile Framework](https://framework.scaledagile.com/iteration-retrospective) | Medium — SAFe practitioner | Gap 3 | Iteration metrics review; improvement story tracking |
| [AI Feedback Loop — Clarifai](https://www.clarifai.com/blog/closing-the-loop-how-feedback-loops-help-to-maintain-quality-long-term-ai-results) | Medium — ML practitioner | Gap 3 | Classification accuracy monitoring; golden set comparison; drift detection |

---

## Cross-Gap Synthesis

Three findings apply across all three gap areas:

**1. Artifact requirement over prose instruction**
Stage-Gate, DMAIC, and NASA all enforce process phases through required output artifacts — not through instructions to perform activities. The research step's current prose gate ("when external research needed, read research-protocol.md") needs an artifact requirement: a research report file that must exist before outline generation proceeds. This is Gap Area 1's primary mechanism.

**2. Visible output forces deliberation**
ESI's vital signs requirement, the premature closure checklist literature, and Kahneman's dual-process theory all converge: mandatory data collection changes the cognitive process, not just the inputs. This provides external grounding for the D+B anchor pattern applied throughout Phase 0. Gap Area 2's finding is that this mechanism is already correctly implemented for classification gates; it needs application to the research step.

**3. Prediction recording enables feedback**
GJP and AAR both require explicit recording of the initial assessment/prediction before execution. The design skill's Classification block already records the prediction; the gap is downstream: no mechanism compares classification to execution evidence. Gap Area 3's feedback loop is architecturally ready — the prediction side exists; the outcome-comparison side needs to be built in orchestration or commit workflows.
