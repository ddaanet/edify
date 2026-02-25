# External Research: Software Design Process Methodology Frameworks

**Date:** 2026-02-25
**Scope:** Established frameworks for task complexity triage, requirements-to-design workflows, architectural decision-making, design review, and task routing by complexity.

---

## Framework 1: Cynefin Framework (Complexity Domain Classification)

**Origin:** Dave Snowden, IBM Global Services, 1999. Published academically; adopted widely in management, software engineering, and agile communities.

**Authority:** Peer-reviewed publications; embedded in Scrum and SAFe guidance; endorsed by Harvard Business Review.

### Core Domains and Routing Logic

Cynefin classifies problems into five domains based on the relationship between cause and effect:

| Domain | Cause-Effect Relationship | Recommended Response |
|--------|--------------------------|----------------------|
| Clear (Simple) | Obvious, predictable | Sense → Categorize → Respond (apply best practice) |
| Complicated | Analyzable by experts | Sense → Analyze → Respond (apply good practice) |
| Complex | Emergent, requires experimentation | Probe → Sense → Respond (experiment) |
| Chaotic | No visible cause-effect link | Act → Sense → Respond (stabilize first) |
| Disorder/Confusion | Unknown which domain applies | Break into parts, assign each to a domain |

### Complexity Classification Criteria

A task maps to a domain based on:
- **Requirement clarity:** Can requirements be fully specified upfront? (Clear → yes; Complex → no)
- **Solution knowability:** Is there a known best practice or does it require discovery? (Complicated → expert analysis sufficient; Complex → experimentation required)
- **Causal transparency:** Can you predict outcomes from decisions? (Clear → yes; Chaotic → no)
- **Novelty:** Is this task of a type the team has done before? (Clear/Complicated → familiar; Complex → novel enough that outcomes are emergent)

### Routing Implications

- **Clear:** Execute directly without analysis. Assign to any competent team member. No design phase needed.
- **Complicated:** Requires expert analysis before execution. Engage specialists. A design or planning phase is appropriate.
- **Complex:** Cannot fully design upfront. Run a discovery spike or prototype. Incremental delivery with feedback loops.
- **Chaotic:** Immediate action to stabilize; design deferred until order restored.

### Limitations

- Domains are assessments, not measurements — classification requires judgment and can be contested.
- Does not provide explicit step counts, file counts, or other quantifiable classification criteria.
- Domain assignment can shift mid-task (complicated problems can reveal complexity).
- Designed for general management; software adaptations are informal.

### Relationship to Requirements → Design → Implementation

Cynefin determines which workflow tier is appropriate: Clear tasks skip design and go straight to implementation; Complicated tasks get a full design pass; Complex tasks get a discovery-then-incremental-design approach rather than upfront specification.

**Sources:** [Wikipedia — Cynefin framework](https://en.wikipedia.org/wiki/Cynefin_framework), [Managing software complexity - DEV Community](https://dev.to/cagatayunal/managing-software-complexity-the-cynefin-framework-3j6g), [Cynefin - Consortium for Service Innovation](https://library.serviceinnovation.org/Intelligent_Swarming/Practices_Guide/80_Intelligent_Swarming_and_Other_Models/20_Cynefin)

---

## Framework 2: Stacey Matrix (Agreement × Certainty Complexity Model)

**Origin:** Ralph Stacey, British organizational theorist, 1990s. Adopted in agile and project management contexts, particularly for software scope assessment.

**Authority:** Widely cited in agile literature; used in Scrum training; appears in PMI and project management curricula.

### Core Structure

Two-axis grid:
- **X-axis:** Certainty about how to achieve the goal (high → low)
- **Y-axis:** Agreement among stakeholders about what is needed (high → low)

Four zones:
1. **Simple:** High certainty, high agreement → well-understood best practices apply
2. **Complicated:** High certainty, lower agreement → expert analysis resolves disagreement; good practices known
3. **Complex:** Lower certainty, lower agreement → experimentation, iterative discovery
4. **Chaotic:** Minimal certainty, minimal agreement → immediate action; no stable process

### Complexity Classification Criteria

A task is placed on the matrix by assessing:
- **Requirement agreement:** Do all stakeholders agree on what is needed? (Proxy: requirements are stable and signed off vs. disputed or evolving)
- **Method certainty:** Do implementers know how to build this? (Proxy: similar work done before vs. greenfield technical challenge)

### Routing Implications

- **Simple:** Assign directly. Standard procedures apply.
- **Complicated:** Convene experts. A structured design phase is warranted to resolve technical options.
- **Complex:** Use agile/iterative methods. Avoid upfront full design — design incrementally as knowledge develops.
- **Chaotic:** Stabilize with any working approach; refine once stable.

### Distinction from Cynefin

Stacey focuses on two concrete measurable axes (certainty, agreement) that are easier to assess at task intake than Cynefin's cause-effect relationship judgment. Stacey is more operational for software task triage; Cynefin is more conceptually rigorous.

### Limitations

- Same subjectivity risk as Cynefin — axes require judgment.
- Does not specify at what certainty/agreement level the boundary between zones lies.
- Lacks a formal assessment protocol.

### Relationship to Requirements → Design → Implementation

Stacey provides the triage gate: tasks in the Simple zone flow directly to implementation; Complicated tasks get a design phase; Complex tasks get a discovery spike before requirements are even finalized. This maps directly to a tiered design workflow.

**Sources:** [Stacey Matrix — Praxis Framework](https://www.praxisframework.org/en/library/stacey-matrix), [Understanding The Stacey Matrix — Agility Portal](https://agilityportal.io/blog/stacey-matrix), [What is the Stacey Matrix — OnlinePMCourses](https://onlinepmcourses.com/what-is-the-stacey-matrix-simple-complicated-complex-chaotic/)

---

## Framework 3: Architectural Decision Records (ADR) Process

**Origin:** Michael Nygard popularized the format in 2011 (blog post: "Documenting Architecture Decisions"). Formalized by the ADR community at adr.github.io. Multiple template variants; Y-statement format from Zdun et al. academic work. AWS, Microsoft, and UK Gov Digital Service have adopted it as a standard.

**Authority:** Industry standard; adopted by AWS (Prescriptive Guidance), Microsoft Azure Well-Architected Framework, UK Government Digital Service. Multiple peer-reviewed papers on ADR practices.

### Core Components

Each ADR captures:
1. **Context:** Forces at play, stakeholder needs, constraints (the "why now")
2. **Decision:** The chosen solution (the architectural choice made)
3. **Status:** Proposed → Accepted → Superseded / Deprecated / Rejected
4. **Consequences:** Good and bad — what this decision makes easier and harder

#### Y-Statement Template (Zdun et al.)

Structured single sentence format:
> "In the context of [situation], facing [concern], we decided for [option], to achieve [quality], accepting [downside]."

This forces explicit acknowledgment of tradeoffs — a key quality gate.

### ADR Process Steps (AWS formulation)

1. **Identify** — Recognize an architecturally significant decision needing documentation
2. **Propose** — Owner creates ADR in `Proposed` state using standard template
3. **Review** — Team dedicates 10–15 min; comments added; owner facilitates discussion
4. **Resolve** — ADR moves to `Accepted`, `Rejected`, or stays `Proposed` pending rework
5. **Apply** — ADRs consulted during code reviews to validate conformance
6. **Update** — New ADR created when change needed; original marked `Superseded`

### Three-Pillar Framework (InfoQ — Technology Radar + Standards + ADRs)

An extended framework separates decision formality by type:
- **Technology Radar:** Assess/Trial/Adopt/Hold — governs technology selection decisions
- **Technology Standards:** Documented guidelines for routine technical choices (API design, logging)
- **ADRs:** Required for architecturally significant individual decisions (cross-cutting, structural, irreversible)

The tiering itself is a routing mechanism: not every decision becomes an ADR. ADRs are for "architecturally significant" decisions — those with measurable effect on architecture and quality.

### Complexity Routing Signal

An ADR is warranted when the decision:
- Has structural impact (changes module boundaries, API contracts, data models)
- Involves non-functional requirements (performance, security, availability)
- Is difficult to reverse
- Affects multiple teams or components
- Could lead to "architecture drift" if undocumented

Routine implementation choices (variable names, algorithm selection within a known approach) do not require ADRs.

### Limitations

- Provides record-keeping structure, not a decision-making methodology — tells you what to capture, not how to reason through options.
- "Architecturally significant" is not precisely defined, requiring team calibration.
- ADR quality depends heavily on the reasoning captured — a weak ADR is worse than none (false confidence).

### Relationship to Requirements → Design → Implementation

ADRs are the output artifact of the design phase. They bridge design to implementation by recording what was decided and why, ensuring implementation teams have explicit architectural intent rather than inferred intent.

**Sources:** [Architectural Decision Records — adr.github.io](https://adr.github.io/), [ADR Process — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html), [Maintain an ADR — Microsoft Azure](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record), [A Simple Framework for Architectural Decisions — InfoQ](https://www.infoq.com/articles/framework-architectural-decisions/), [Documenting Architecture Decisions — Nygard/Cognitect](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

---

## Framework 4: ATAM — Architecture Tradeoff Analysis Method

**Origin:** Carnegie Mellon Software Engineering Institute (SEI), circa 2000. Authors: Rick Kazman, Mark Klein, Paul Clements. Peer-reviewed; published as SEI technical report.

**Authority:** SEI/CMU academic and industry origin. Widely cited in software architecture literature. Used in defense, finance, and enterprise software evaluation.

### Core Purpose

ATAM is a risk-mitigation evaluation process applied early in the development lifecycle. It does not make design decisions — it evaluates a proposed architecture against quality attribute requirements to surface risks, tradeoffs, and sensitivity points before implementation begins.

### The Nine Steps (Two Phases)

**Phase 1 (internal team, steps 1–6):**
1. **Present ATAM** — explain the method to evaluation participants
2. **Present business drivers** — define architectural goals and business context
3. **Present architecture** — architect presents with appropriate detail (module + component views minimum)
4. **Identify architectural approaches** — catalog primary tactics and patterns used
5. **Generate quality attribute utility tree** — map business requirements to measurable quality attributes (performance, security, modifiability, etc.) with specific scenarios and priorities
6. **Analyze architectural approaches** — evaluate each approach against scenarios; identify risks, non-risks, sensitivity points, tradeoff points

**Phase 2 (broader stakeholder group, steps 7–9):**
7. **Brainstorm and prioritize scenarios** — stakeholders vote to prioritize; reveals divergent assumptions
8. **Analyze architectural approaches (continued)** — run new high-priority scenarios against architecture
9. **Present results** — risks, non-risks, sensitivity points, tradeoffs, and mitigation strategies presented and written up

### Key Output Artifacts

- **Utility tree:** Hierarchical map from business drivers → quality attributes → specific architectural scenarios → priority/difficulty rating
- **Risk register:** Potentially problematic architectural decisions
- **Sensitivity points:** Architecture decisions that strongly affect quality attribute responses
- **Tradeoff points:** Decisions that simultaneously affect two or more quality attributes in opposing directions

### Complexity Classification Role

The utility tree is particularly relevant: it forces explicit prioritization of quality attributes with a 2×2 rating (importance to business × difficulty to achieve). This is a formal complexity assessment tool — it surfaces where an architecture's complexity lies and which risks are highest priority.

### Limitations

- Resource-intensive: Phase 1 takes 1–2 days with the full team.
- Requires a proposed architecture to exist — cannot evaluate from requirements alone.
- The SEI notes ATAM has been partially superseded by lighter-weight evaluation approaches in agile contexts.
- Does not prescribe how to make design decisions, only how to evaluate them.

### Relationship to Requirements → Design → Implementation

ATAM sits at the design → implementation boundary. It validates that a completed design adequately addresses requirements before committing to implementation. It can reveal that a design needs revision, routing back to the design phase.

**Sources:** [Architecture Tradeoff Analysis Method — Wikipedia](https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method), [ATAM — CMU SEI](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/), [ATAM — GeeksforGeeks](https://www.geeksforgeeks.org/software-engineering/architecture-tradeoff-analysis-method-atam/)

---

## Framework 5: ISO/IEC/IEEE 29148 — Requirements Engineering Process

**Origin:** ISO/IEC/IEEE 29148:2018 (revision of 2011 original). International standard for requirements engineering across system and software life cycles. Published jointly by ISO, IEC, and IEEE.

**Authority:** International standard — the authoritative requirements engineering reference. Adopted globally in safety-critical, defense, and enterprise software contexts.

### Three Core Processes

The standard defines requirements engineering as three sequential processes:

1. **Business or Mission Analysis**
   - Define the business problem or opportunity
   - Characterize the solution environment (operational context)
   - Determine potential solution classes (what kinds of solutions are feasible)
   - Output: Business Requirements Specification (BRS)

2. **Stakeholder Needs and Requirements Definition**
   - Identify stakeholders and their concerns
   - Elicit stakeholder needs
   - Transform needs into verifiable requirements
   - Resolve conflicts between stakeholder requirements
   - Output: Stakeholder Requirements Specification (StRS)

3. **System/Software Requirements Definition**
   - Transform stakeholder requirements into technical requirements
   - Define interfaces, constraints, quality attributes
   - Verify that requirements are complete, consistent, unambiguous, verifiable
   - Output: System Requirements Specification (SyRS) or Software Requirements Specification (SRS)

### Key Activities Within Each Process

The standard specifies these activities are required (not optional) across processes:
- **Elicitation:** Active gathering from stakeholders and context
- **Analysis:** Structure, classify, prioritize requirements; detect conflicts and gaps
- **Specification:** Document in verifiable, unambiguous form
- **Validation:** Confirm requirements represent stakeholder intent
- **Management:** Track changes, maintain traceability, version control requirements

### Complexity Signal in Requirements

The standard implicitly provides a complexity signal: the ratio of unknown/unstable requirements to total requirements scope indicates complexity class:
- All requirements known and stable → Clear/Complicated (Cynefin mapping)
- Significant requirements elicitation needed → Complicated
- Requirements cannot be fully specified without discovery → Complex

### Limitations

- Heavyweight for small projects — the full standard process produces multiple formal specification documents.
- Designed for systems engineering contexts; requires adaptation for agile/iterative software development.
- Does not directly prescribe complexity triage or routing — it provides the process for any requirements engineering task, regardless of scale.

### Relationship to Requirements → Design → Implementation

IEEE 29148 covers the requirements phase comprehensively. The handoff from requirements to design is: SyRS/SRS documents that are complete, consistent, and validated. Design begins when requirements are validated — the standard explicitly separates the requirements and design phases.

**Sources:** [ISO/IEC/IEEE 29148:2018 — ISO](https://www.iso.org/standard/72089.html), [IEEE 29148 Standard — IEEE SA](https://standards.ieee.org/standard/29148-2018.html), [Requirements Engineering Process — GeeksforGeeks](https://www.geeksforgeeks.org/software-engineering/software-engineering-requirements-engineering-process/)

---

## Framework 6: Double Diamond Design Process

**Origin:** British Design Council, 2005. Developed from observational research of design processes at 11 global companies. Originally for product design; widely adapted for software product development.

**Authority:** UK Design Council (government-backed research body). Adopted by Thoughtworks, Splunk, and numerous product teams; standard in UX/product curricula.

### Four Phases (Two Diamonds)

**Diamond 1 — Problem Space:**
1. **Discover (diverge):** Research broadly. Observe users, gather data, explore the problem landscape without constraining the solution space. Goal: surface the actual problem, which may differ from the stated problem.
2. **Define (converge):** Synthesize discovery findings into a precise problem statement. Scope and prioritize. Output: a defined problem that is worth solving.

**Diamond 2 — Solution Space:**
3. **Develop (diverge):** Generate multiple solution concepts. Prototype, experiment, ideate broadly. Defer judgment.
4. **Deliver (converge):** Test, refine, select and build the best solution. Iterate to production.

### Complexity Routing Signal

The Double Diamond provides a diagnostic for a key routing decision: **is the problem well-defined?**

- If the problem is already clearly defined (requirements are agreed upon, the scope is known), skip Diamond 1 — go straight to Develop.
- If the problem is ambiguous (stakeholder disagreement, unclear scope, novel domain), run Diamond 1 to define before designing.

This maps directly to complexity triage: a task with clear requirements is a one-diamond task (solution design + delivery); a task with ambiguous requirements is a two-diamond task (discovery first).

### Software Engineering Adaptation (Thoughtworks)

Thoughtworks adapted the Double Diamond for software:
- Software's malleability reduces the cost of starting — teams often deliver smaller "packages of value" rather than perfecting upfront.
- Strategy and execution are interleaved: software engineering defines strategy as it executes.
- Diamond 1 may produce lightweight artifacts (user story maps, problem briefs) rather than formal requirements documents.

### Limitations

- Originally developed for physical product design; software adaptation is informal (no ISO/IEEE equivalent).
- Does not specify criteria for when Diamond 1 is complete enough to start Diamond 2.
- The diverge-converge model is descriptive, not prescriptive — it names the phases without defining specific techniques within each.

### Relationship to Requirements → Design → Implementation

Double Diamond maps as: Discover + Define = requirements (Diamond 1); Develop + Deliver = design + implementation (Diamond 2). The model explicitly frames requirements as active discovery rather than passive receipt — a significant framing departure from waterfall requirements engineering.

**Sources:** [Double Diamond — Wikipedia](https://en.wikipedia.org/wiki/Double_Diamond_(design_process_model)), [Double Diamond — Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/double-diamond), [Double Diamond for Software — Mayven Studios](https://mayvenstudios.com/blog/double-diamond-method-software-development)

---

## Cross-Framework Synthesis

### Complexity Triage: Composite Decision Criteria

Drawing on Cynefin, Stacey Matrix, and software engineering research, a composite triage signal emerges:

| Signal | Simple/Clear | Complicated | Complex |
|--------|-------------|-------------|---------|
| Requirements stability | Stable, agreed | Stable but needs expert analysis | Unstable, evolving, or unknown |
| Novelty | Familiar pattern, done before | New application of known technique | Novel domain or approach |
| Solution knowability | Best practice exists | Expert analysis yields answer | Requires experimentation |
| Stakeholder agreement | High | Moderate | Low |
| Reversibility of decisions | High | Moderate | Low (high-stakes choices) |
| Cross-cutting scope | Self-contained | Limited cross-cutting | Significant cross-cutting |

### Requirements → Design → Implementation Handoffs

Each framework names a distinct handoff:
- **Requirements complete** (IEEE 29148): SRS validated — enter design
- **Problem defined** (Double Diamond): Define phase complete — enter Develop
- **Architecture proposed** (ATAM): Utility tree complete — begin ATAM evaluation
- **Decision resolved** (ADR): ADR moves to `Accepted` — implementation may proceed

### Design Review Staging

The NASA PDR/CDR model (from aerospace, NPR 7123.1 series) provides a staged design review structure relevant to software:
- **Preliminary Design Review (PDR):** Design meets all requirements with acceptable risk; correct options selected; interfaces identified; verification methods described. Exit criterion: basis for proceeding to detailed design.
- **Critical Design Review (CDR):** Design maturity sufficient to proceed with full implementation; build-to specifications complete; test plans defined. Exit criterion: authorization to begin implementation.

This two-gate model (PDR → CDR) maps to a natural design workflow: early design review validates direction; late design review validates readiness to implement.

**Sources:** [Design Review — Wikipedia](https://en.wikipedia.org/wiki/Design_review_(U.S._government)), [NASA NPR 7123.1 Appendix G](https://nodis3.gsfc.nasa.gov/displayCA.cfm?Internal_ID=N_PR_7123_001A_&page_name=AppendixG), [Triage in Software Engineering — arXiv 2511.08607](https://arxiv.org/abs/2511.08607)

---

## Framework Gaps and Limitations

No single framework fully addresses all five research questions:

1. **Task complexity triage:** Cynefin and Stacey Matrix provide qualitative routing criteria; no widely adopted framework provides quantitative thresholds (e.g., "tasks touching >N components require design").
2. **Requirements-to-design translation:** IEEE 29148 covers requirements; Double Diamond covers the full arc; but neither specifies the handoff protocol precisely.
3. **Architectural decision-making:** ADR covers documentation of decisions; ATAM covers evaluation; neither covers the reasoning process for generating options.
4. **Design review quality:** NASA PDR/CDR provides the strongest staged review model; ATAM provides the most rigorous evaluation methodology.
5. **Task routing by complexity:** Cynefin and Stacey Matrix are the primary frameworks; both require team calibration and cannot be automated without supplementary heuristics.

The most actionable combination for grounding a design skill: **Stacey Matrix** for triage routing (two measurable axes), **IEEE 29148** for requirements completeness criteria, **Double Diamond** for the overall workflow arc, and **ADR + ATAM** for design output artifacts and evaluation.
