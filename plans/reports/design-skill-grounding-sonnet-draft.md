# Design Skill Grounding Report

**Grounding:** Strong

**Date:** 2026-02-25
**Method:** Parallel diverge-converge (codebase + git history mining / external research)
**Branch artifacts:** `design-skill-internal-codebase.md`, `design-skill-external-research.md`
**Purpose:** Ground the /design skill against established methodology before redesign

---

## Research Foundation

Five primary framework clusters cover the design skill's functional scope:

- **Cynefin Framework** (Snowden, IBM, 1999) — domain-based complexity classification and routing
- **Stacey Matrix** (Stacey, 1990s) — two-axis (certainty × agreement) complexity triage
- **IEEE 29148:2018** — international standard for requirements engineering processes and quality criteria
- **Double Diamond** (UK Design Council, 2005) — diverge-converge workflow arc for problem → solution
- **ADR process** (Nygard 2011; formalized at adr.github.io; adopted by AWS, Microsoft) — architectural decision documentation
- **ATAM** (CMU SEI, ~2000) — architecture evaluation; utility tree for quality attribute prioritization
- **NASA PDR/CDR model** (NPR 7123.1) — staged design review gates (PDR → CDR) before implementation

---

## Adapted Methodology

### Principle 1: Complexity is a routing signal, not a quality judgment

**External grounding:** Cynefin and Stacey Matrix both frame complexity classification as determining *what workflow is appropriate*, not as a quality judgment about the task. Cynefin's "Complicated" domain routes to expert analysis + design; "Clear/Simple" routes directly to implementation; "Complex" routes to discovery spike before design. Stacey operationalizes this with two axes: certainty about *how* to achieve the goal, and agreement about *what* is needed.

**Project instance:** The /design skill routes Simple → direct execution, Moderate → /runbook, Complex → Phases A-C. The current classification criteria (architectural decisions, multiple valid approaches, uncertain requirements, behavioral code changes) map directly to the Cynefin/Stacey axes: Stacey's "certainty" axis is "do we know how to implement this?" and "agreement" axis is "are requirements stable and agreed upon?" The Moderate category corresponds to Cynefin's Complicated (expert analysis resolves it; good practice exists); Simple corresponds to Clear.

**Grounding contribution:** The current Simple/Moderate/Complex trichotomy is structurally sound — it matches the consensus triage structure from two independent frameworks. What it lacked was named criteria per axis. The Stacey axes provide the principled anchor: assess *certainty about how* (implementation approach known?) and *requirement stability* (FRs stable and unambiguous?). Both must be high for Simple; either being low routes to Moderate or Complex.

---

### Principle 2: Complexity can shift mid-task; one-shot triage is insufficient

**External grounding:** Cynefin explicitly warns that domain assignment is an assessment, not a measurement, and that domain shifts occur (complicated problems can reveal complexity; complex problems can resolve to complicated once experimentation yields insight). The model expects reassessment, not single-point classification.

**Project instance:** Failure pattern #3 (commit 41a4b163): one-shot triage at /design entry with no re-assessment. Process continued at "Complex" even when the outline revealed a two-file prose edit. Evidence: outline-corrector + design.md + design-corrector cost ~112K tokens for work that could have been done inline. Fix: post-outline complexity re-check gate — if all downgrade criteria met, collapse to direct execution.

**Grounding contribution:** The post-outline re-check is Cynefin-grounded: it implements mid-task domain reassessment. The two current gates (entry triage + post-outline re-check) are the correct structure. The downgrade criteria (additive changes, no loops, no open questions, explicit scope, no cross-file sequencing) are operationalizations of "domain has shifted to Clear."

---

### Principle 3: Requirements completeness is a prerequisite to design, not an assumption

**External grounding:** IEEE 29148:2018 defines a requirements validation process that must precede design: requirements must be complete (no TBDs in scope), consistent (no conflicts), unambiguous (single interpretation), and verifiable (each requirement has a measurable acceptance criterion). The standard explicitly separates the requirements phase from design — design begins when requirements are validated, not when they are stated.

**Project instance:** The /design skill's requirements-clarity gate checks "each FR/NFR has concrete mechanism." This maps to IEEE 29148's "verifiable" quality criterion — a requirement without a concrete mechanism cannot be verified. Late-addition failure (workflow-planning.md, FR-18 incident): FR added during design session bypassed outline-level validation, produced mechanism-free specification that downstream planners could not implement.

**Gap revealed:** The requirements-clarity gate is currently **prose-only** — "validate requirements are actionable" is a self-assessment. IEEE 29148's validation activity produces an observable artifact (SRS with explicit quality assessment). Per failure pattern #2 (prose gates rationalized away), a prose-only gate at the highest-stakes entry point is structurally weak. A D+B anchor — a tool call that produces observable output before routing — is the project-specific implementation of IEEE 29148's explicit validation activity requirement.

---

### Principle 4: Design output should record context, decision, and consequences — not just conclusions

**External grounding:** The ADR format (Nygard 2011) requires each architectural decision to capture: (1) context — forces at play, constraints; (2) decision — the specific choice made; (3) status — proposed/accepted/superseded; (4) consequences — what becomes easier and harder. The Y-statement variant (Zdun et al.) forces explicit tradeoff acknowledgment: "accepting [downside]." ADRs are the output artifact of design; they bridge design to implementation by giving implementers architectural intent rather than inferred intent.

**Project instance:** The design.md output is the project's equivalent of an ADR or ADR collection. The design-content-rules.md does not currently require explicit consequences/tradeoffs per decision. Design documents record what was decided; they are weaker on what was accepted as a downside.

**Grounding contribution:** Design documents should require a "tradeoffs accepted" section per major decision, following the ADR pattern. This is a gap in current design-content-rules.md — it governs density, repetition, and agent validation, but not the decision documentation structure itself.

---

### Principle 5: Design review is a staged gate, not a single approval

**External grounding:** NASA's PDR/CDR model provides a two-gate staged review: Preliminary Design Review (direction validated against requirements; correct options selected; risk acceptable) is the exit criterion for proceeding to detailed design. Critical Design Review (build-to specifications complete; test plans defined) is the exit criterion for beginning implementation. These are distinct gates with distinct criteria — PDR does not authorize implementation.

**Project instance:** /design runs: outline-corrector (corresponds to PDR — validates direction, catches structural issues before detailed design) → design-corrector (corresponds to CDR — validates design.md readiness for implementation). This two-gate structure independently matches the NASA PDR/CDR model. The C.2 checkpoint commit between C.1 (write design) and C.3 (design-corrector review) isolates the review as a distinct phase with its own audit trail — consistent with the PDR/CDR model's intent.

**Grounding contribution:** The existing two-gate structure is principled. What the grounding adds: the *criteria* for each gate should differ. outline-corrector criteria = PDR criteria (does the approach meet requirements? are options selected? are risks identified?). design-corrector criteria = CDR criteria (are decisions fully specified? can planners implement without inference?). Currently both gates use similar "completeness" criteria — differentiation based on PDR/CDR would sharpen each reviewer's role.

---

### Principle 6: Validation requires observable evidence, not self-assessment

**External grounding:** IEEE 29148 defines "validation" as a distinct activity — not a self-assessment by the requirements author, but a process that produces an observable verification artifact. Cynefin similarly warns that domain assignment is contested judgment, not measurement. The Stacey Matrix notes that axes require judgment and "lack a formal assessment protocol" — this is framed as a known limitation, implying a formal protocol is the improvement target.

**Project instance:** This is the primary structural finding of the git history analysis. Failure pattern #2 (multiple commits): every prose gate eventually fails. The resolution pattern: D+B anchor — a tool call (Grep, Glob, when-resolve.py) that produces visible output before routing decision. The escape hatch IS the failure mode — "skip if already in context" fails because agents substitute adjacent activity for the specific required action.

**Project implementation:** The `when-resolve.py` call before classification (D+B anchor) is the project-specific implementation of IEEE 29148's explicit validation activity requirement. It produces observable output (resolution results) that proves the gate was executed — the LLM cannot rationalize around visible tool output the way it can rationalize around prose instructions.

---

### Principle 7: A problem must be defined before a solution can be designed

**External grounding:** Double Diamond (Design Council, 2005) distinguishes two diamonds: Diamond 1 (Discover → Define) establishes what problem to solve; Diamond 2 (Develop → Deliver) designs and builds the solution. The key routing rule: if the problem is already defined (requirements agreed upon, scope known), skip Diamond 1. If the problem is ambiguous, run Diamond 1 first. The Double Diamond treats requirements as active discovery rather than passive receipt.

**Project instance:** The /requirements skill is the Diamond 1 path. The requirements-clarity gate at Phase 0 of /design routes to /requirements if requirements are vague or mechanism-free — this is the project-specific implementation of "if problem is not yet defined, run Diamond 1 first." The /design skill itself operates entirely within Diamond 2 (solution space).

**Grounding contribution:** The current routing (vague requirements → /requirements → return to /design) is Double Diamond-grounded. The gap: the requirements-clarity gate that makes this routing decision is prose-only (see Principle 3). A D+B anchor on this gate would ground the routing decision in observable evidence rather than self-assessment.

---

## Gap Analysis: Grounding-Revealed Issues

The following gaps were identified by mapping internal failure patterns against external framework requirements:

### Gap 1: Requirements-clarity gate needs D+B anchor

**Evidence:** IEEE 29148 requires explicit validation activity (not self-assessment). Failure pattern #2: prose gates fail. Current gate is prose-only.
**Implication:** Add a tool call before routing to /requirements — e.g., check for presence of requirements.md + scan for "TBD", "unclear", "mechanism" keywords. Observable output anchors the routing decision.

### Gap 2: Complexity classification criteria need axis naming

**Evidence:** Stacey Matrix provides two concrete axes (certainty about how, agreement about what). Current criteria (architectural decisions, multiple valid approaches, behavioral code) describe what complex/moderate tasks look like, but don't name the axes being assessed.
**Implication:** The classification section should name the axes: (1) implementation certainty — "do we know how to build this?"; (2) requirement stability — "are FRs agreed and mechanism-specified?" Classification outcome should cite which axes triggered it (produces visible output).

### Gap 3: Design output format lacks explicit tradeoffs

**Evidence:** ADR format requires "consequences" — what becomes easier and harder. Y-statement requires explicitly naming the accepted downside. Current design-content-rules.md doesn't require this.
**Implication:** design-content-rules.md should require a tradeoffs/consequences section per major architectural decision. This is a content rule addition, not a structural change.

### Gap 4: Outline-corrector and design-corrector criteria are not differentiated

**Evidence:** NASA PDR/CDR model uses different criteria at each stage. Preliminary = direction + options; Critical = specifications + implementability.
**Implication:** outline-corrector prompt/criteria = PDR (approach valid? requirements traceable? risks named?). design-corrector prompt/criteria = CDR (decisions fully specified? planner can implement without inference? agent names verified?). Currently both are "completeness" reviews — differentiation sharpens each gate's role.

### Gap 5: Companion task rule is prose-only

**Evidence:** Failure pattern #1 (e1a35cd1): companion tasks treated as exempt from Phase 0. Rule added as prose; learning entry says agents bypass it.
**Implication:** Structural enforcement is needed. The rule cannot be prose. One approach: before processing any bundled work, require explicit enumeration of all tasks with their Phase 0 classification output before proceeding to any of them.

### Gap 6: No structured-bugfix triage path

**Evidence:** workflow-grounding-audit.md notes "structured-bugfix process as routing outcome" — a known triage extension not yet incorporated.
**Implication:** Bugfix tasks have a distinct profile (Cynefin: often Complicated domain — cause analyzable, fix knowable). They warrant a fourth triage path: defect-triage → structured-bugfix workflow. This is a scope extension noted for the redesign.

---

## Grounding Assessment

**Quality label:** Strong

**Evidence basis:**
- 6 named frameworks with citations and authority assessments
- 5 core principles each grounded in ≥2 external frameworks
- 10 internal failure patterns with specific commit hashes mapped to external principles
- 6 gaps identified through framework → internal pattern comparison, each with implication for redesign
- Both branch artifacts retained as audit evidence

**Searches performed:**
- "software task complexity classification framework methodology"
- "requirements to design workflow simple moderate complex"
- "architectural decision record ADR process framework"
- "design thinking double diamond software engineering adaptation"
- "architecture tradeoff analysis method ATAM CMU"
- "ISO IEEE 29148 requirements engineering process"
- "software design review methodology criteria 2024 2025"

**Remaining gaps:**
- No widely adopted framework provides quantitative thresholds for complexity triage (Cynefin and Stacey both require judgment). The project's classification criteria are a defensible adaptation; they are not derivable from external literature.
- Option-generation methodology (how to reason through design alternatives, not just document them) is not covered by ADR or ATAM — both cover documentation/evaluation, not generation. This remains ungrounded.

---

## Sources

| Source | Authority | Used for |
|--------|-----------|----------|
| [Cynefin Framework](https://en.wikipedia.org/wiki/Cynefin_framework) | HBR-endorsed; embedded in SAFe/Scrum | Complexity domain classification, routing logic |
| [Stacey Matrix](https://www.praxisframework.org/en/library/stacey-matrix) | PMI/Agile curricula | Two-axis (certainty × agreement) triage operationalization |
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | International standard (ISO/IEEE) | Requirements completeness and validation criteria |
| [ADR — adr.github.io](https://adr.github.io/) | AWS, Microsoft adopted | Design output format; context/decision/consequences structure |
| [ADR Process — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html) | AWS | ADR lifecycle and review steps |
| [ATAM — CMU SEI](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/) | Academic/CMU | Utility tree; staged evaluation before implementation |
| [Double Diamond](https://en.wikipedia.org/wiki/Double_Diamond_(design_process_model)) | UK Design Council (government research) | Workflow arc; problem-definition vs solution-design phases |
| [Double Diamond — Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/double-diamond) | Industry practitioner | Software engineering adaptation of Double Diamond |
| [NASA PDR/CDR — NPR 7123.1](https://nodis3.gsfc.nasa.gov/displayCA.cfm?Internal_ID=N_PR_7123_001A_&page_name=AppendixG) | NASA standard | Staged design review gate structure |
| [Documenting Architecture Decisions — Nygard](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | Industry origin of ADR format | ADR motivation and Y-statement format |

**Internal evidence:** `design-skill-internal-codebase.md` — 10 failure patterns with commit hashes, 8 gap types, 5 structural patterns extracted from git history + current skill analysis.
