# Design Skill Grounding Report

**Grounding:** Strong

**Date:** 2026-02-25
**Method:** Parallel diverge-converge (codebase + git history mining / external research), opus convergence
**Branch artifacts:** `design-skill-internal-codebase.md`, `design-skill-external-research.md`
**Purpose:** Ground the /design skill against established methodology before redesign

---

## Research Foundation

Six framework clusters cover the design skill's functional scope:

| Framework | Origin | Authority | Covers |
|-----------|--------|-----------|--------|
| Cynefin | Snowden, IBM, 1999 | HBR-endorsed; SAFe/Scrum | Domain-based complexity classification + routing |
| Stacey Matrix | Stacey, 1990s | PMI/Agile curricula | Two-axis (certainty × agreement) triage |
| IEEE 29148:2018 | ISO/IEC/IEEE | International standard | Requirements completeness + validation criteria |
| Double Diamond | UK Design Council, 2005 | Government research body | Diverge-converge workflow arc |
| ADR process | Nygard 2011; AWS, Microsoft | Industry standard | Architectural decision documentation |
| NASA PDR/CDR | NPR 7123.1 | NASA standard | Staged design review gates |

Supporting: ATAM (CMU SEI) for utility tree / quality attribute prioritization; Y-statement format (Zdun et al.) for tradeoff acknowledgment.

---

## Framework Mapping

### Principle 1: Complexity classification is a routing signal, not a quality judgment

**General insight:** Cynefin and Stacey Matrix both frame complexity classification as determining *what workflow is appropriate*. Cynefin's Clear domain routes to best-practice application; Complicated routes to expert analysis; Complex routes to experimentation. Stacey operationalizes with two concrete axes: certainty about *how* to achieve the goal, and agreement about *what* is needed. Neither framework treats "Simple" as inferior — it means the workflow overhead of analysis is unjustified.

**Project validation:** The /design skill routes Simple → direct execution, Moderate → /runbook, Complex → Phases A-C. The current criteria map to Stacey axes: "architectural decisions, multiple valid approaches" = low certainty about how; "uncertain requirements" = low agreement about what. The Moderate category = Cynefin Complicated (known technique, expert analysis resolves); Simple = Clear.

**What grounding adds:** The current classification criteria describe *what tasks look like* at each tier, not *what axes are being assessed*. Stacey provides the principled anchor: explicitly assess (1) implementation certainty — "is the approach known?" and (2) requirement stability — "are FRs agreed and mechanism-specified?" Both high → Simple; either low → Moderate/Complex depending on degree.

---

### Principle 2: Complexity can shift mid-task; one-shot triage is insufficient

**General insight:** Cynefin explicitly warns that domain assignment can shift: complicated problems reveal hidden complexity; complex problems resolve to complicated once experimentation yields insight. The framework expects reassessment as an intrinsic part of the process, not as an exception.

**Project validation:** Failure pattern #3 (commit `41a4b163`): one-shot triage at entry with no re-assessment. Process continued at "Complex" for a two-file prose edit. Cost: ~112K tokens for outline-corrector + design.md + design-corrector on work executable inline. Fix: post-outline complexity re-check gate.

**What grounding adds:** The two current gates (entry triage + post-outline re-check) are Cynefin-grounded mid-task reassessment. The downgrade criteria (additive changes, no loops, no open questions, explicit scope, no cross-file sequencing) operationalize "domain has shifted to Clear." This is principled, not an ad-hoc patch.

---

### Principle 3: Requirements completeness is a prerequisite to design, not an assumption

**General insight:** IEEE 29148:2018 defines requirements validation as a distinct activity that must precede design. Requirements must be complete, consistent, unambiguous, and verifiable. The standard explicitly separates requirements from design — design begins when requirements are validated, not when they are stated. Validation produces an observable artifact, not a self-assessment.

**Project validation:** The requirements-clarity gate checks "each FR/NFR has concrete mechanism" — mapping to IEEE 29148's "verifiable" criterion. Late-addition failure (FR-18 incident): requirement added during design bypassed outline-level validation, producing a mechanism-free specification downstream planners couldn't implement.

**Gap revealed:** The requirements-clarity gate is **prose-only**. Per the D+B pattern (Principle 6), prose-only gates at high-stakes decision points fail. IEEE 29148's validation activity produces an observable artifact. The gate needs a structural anchor: either enumerate FRs with mechanism status (structured visible output) or run a targeted check on `requirements.md` content, producing output the designer must respond to before routing.

---

### Principle 4: A problem must be defined before a solution can be designed

**General insight:** Double Diamond (Design Council, 2005) distinguishes problem space (Diamond 1: Discover → Define) from solution space (Diamond 2: Develop → Deliver). The routing rule: if the problem is already defined, skip Diamond 1. If ambiguous, run Diamond 1 first. The framework treats requirements as active discovery, not passive receipt.

**Project validation:** The `/requirements` skill is the Diamond 1 path. The requirements-clarity gate routes vague requirements to /requirements before /design proceeds — the project-specific implementation of "if problem not defined, run Diamond 1 first." The /design skill operates within Diamond 2.

**What grounding adds:** The current routing structure is Double Diamond-grounded. The gap is the same as Principle 3: the gate making this routing decision is prose-only. The general principle (problem must precede solution) is sound; the mechanism for verifying problem-definition completeness needs the same D+B anchor pattern.

---

### Principle 5: Design output should record context, decision, and consequences — not just conclusions

**General insight:** ADR format (Nygard 2011) requires each architectural decision to capture: context (forces at play), decision (the choice made), status (proposed/accepted/superseded), and consequences (what becomes easier *and harder*). The Y-statement variant (Zdun et al.) forces explicit tradeoff acknowledgment: "In the context of [situation], facing [concern], we decided for [option], to achieve [quality], accepting [downside]." The accepted downside is mandatory, not optional.

**Project validation:** The design.md output is the project's ADR equivalent. design-content-rules.md requires "decisions with rationale, not just conclusions" — this captures context and decision but not consequences. No current rule requires explicit tradeoff acknowledgment per decision.

**Gap revealed:** design-content-rules.md should require a consequences/tradeoffs element per major architectural decision, following the ADR pattern. Format: each decision section includes what the choice makes *harder* or *more expensive*, not just what it achieves. This is a content rule addition to the existing file.

---

### Principle 6: Validation requires observable evidence, not self-assessment

**General insight:** IEEE 29148 defines validation as a distinct activity producing observable artifacts — not a self-assessment by the requirements author. Cynefin warns that domain assignment is contested judgment, not measurement. Stacey acknowledges its axes "lack a formal assessment protocol" — framing this as a known limitation, implying a formal protocol is the improvement target.

**Project validation:** This is the dominant structural finding from git history mining. Failure pattern #2 (multiple commits culminating `59904514`): every prose-only gate eventually fails. The resolution pattern: D+B anchor — a tool call (Grep, Glob, `when-resolve.py`) producing visible output before routing. The escape hatch IS the failure mode: "skip if already in context" fails because agents substitute adjacent activity for the specific required action.

The `when-resolve.py` call before classification is the project-specific implementation of IEEE 29148's explicit validation activity. It produces observable output that proves the gate was executed — an LLM cannot rationalize around visible tool output the way it can around prose instructions.

**What grounding adds:** This principle is the strongest convergence point between external frameworks and internal failure evidence. The D+B anchor pattern is the project's instantiation of a general requirement: validation gates must produce observable evidence. Any current prose-only gate is a structural weakness by this principle.

---

### Principle 7: Design review should be staged with differentiated criteria per stage

**General insight:** NASA's PDR/CDR model uses two review gates with distinct criteria. Preliminary Design Review validates *direction*: does the approach meet requirements? Are correct options selected? Are risks identified? Critical Design Review validates *readiness*: are specifications build-to complete? Can implementers proceed without inference? Test plans defined? PDR does not authorize implementation; CDR does. The criteria are deliberately different because the questions being answered are different.

**Project validation:** /design runs outline-corrector (validates direction → PDR) then design-corrector (validates implementability → CDR). The C.2 checkpoint commit between writing and review isolates the review as a distinct phase with its own audit trail.

**Gap revealed:** Both current gates use generic "completeness" criteria. PDR/CDR differentiation yields concrete criteria:

**outline-corrector (PDR):**
- Approach meets requirements (traceability check)
- Options selected with rationale (not "explore options")
- Risks and open questions identified
- Scope boundaries explicit

**design-corrector (CDR):**
- Decisions fully specified (implementer needs no inference)
- Interfaces and integration points defined
- Agent/tool names verified against disk (existing rule)
- Test strategy or verification approach specified
- Late-added requirements re-validated (existing rule)

---

### Principle 8: Assessment must be separated from action

**General insight:** Decision science and clinical triage separate the evaluation step from the disposition step. In emergency triage: assess severity (evaluation) → assign treatment pathway (disposition). Interleaving assessment with disposition creates premature commitment — the assessor skips intermediate evaluation steps once a plausible pathway appears. Structured decision-making literature (Klein's Recognition-Primed Decision Model) documents this as "premature closure" — the decision-maker recognizes a pattern and commits before completing assessment.

**Project validation:** Internal Pattern 2 (commit `e1a35cd1`): initial /design skill interleaved classification criteria with routing logic in a single section. Agents classified and routed simultaneously, skipping intermediate steps (recall, behavioral-code check). Fix: explicit separate sections for Criteria / Gate / Routing, each producing visible output before the next proceeds.

**What grounding adds:** The current separated structure (Classification Criteria → Classification Gate → Routing) is grounded in the general principle of separating assessment from disposition. The visible output requirement at each stage is the structural mechanism preventing premature closure. This same principle applies to any future gate additions: the assessment step must produce observable output before the routing step executes.

---

## Adaptations

### Adapted from external frameworks

| External element | Adapted as | Rationale |
|-----------------|------------|-----------|
| Cynefin Clear/Complicated/Complex | Simple/Moderate/Complex triage | Three-tier routing; Chaotic and Disorder domains excluded (no LLM equivalent) |
| Stacey Matrix certainty × agreement | Implementation certainty × requirement stability | Named axes for classification criteria; assessed per-task |
| IEEE 29148 validation activity | D+B anchors (tool calls before gates) | Observable evidence requirement adapted from document-based to tool-call-based |
| Double Diamond problem/solution split | /requirements → /design routing | Diamond 1 = /requirements; Diamond 2 = /design |
| ADR context/decision/consequences | Design.md decision sections | Adapted to add explicit consequences/tradeoffs per decision |
| NASA PDR/CDR | outline-corrector / design-corrector | Two review gates with differentiated criteria |
| Cynefin Complicated domain | Structured-bugfix triage path | Bug-fix tasks: cause analyzable, fix knowable → expert analysis routing |

### Project-specific additions (not in any external framework)

| Addition | Rationale |
|----------|-----------|
| D+B anchor pattern | Project-discovered mechanism for enforcing gate execution in LLM agents; no external equivalent exists for LLM-specific gate enforcement |
| Companion task Phase 0 enforcement | Multi-task /design invocations must process each task through the full triage pipeline; derived from failure pattern #1 |
| Recall artifact persistence | Context window findings don't survive pipeline stages; materialized as file for downstream consumption |
| Post-outline complexity re-check | Mid-task reassessment gate specific to the outline → design boundary; Cynefin-motivated but operationalization is project-specific |
| Classification visible output block | Structured output format forcing explicit assessment before routing; combines Principle 6 + 8 |

### Deliberately excluded from external frameworks

| Excluded element | Rationale |
|-----------------|-----------|
| Cynefin Chaotic domain | No operational equivalent in software design workflow; tasks in genuine disorder should be stabilized outside the design process |
| Cynefin Disorder/Confusion domain | Assessment of "which domain?" is the triage step itself; adding a meta-assessment is circular |
| ATAM utility tree | Full ATAM evaluation is resource-intensive (1-2 day team exercise); disproportionate for single-agent design workflow. Quality attribute assessment is embedded in requirements validation instead |
| IEEE 29148 three-document output (BRS, StRS, SRS) | Heavyweight for single-agent context; requirements.md + design.md covers the essential content without formal document tiers |
| Stacey Matrix quantitative zone boundaries | Stacey itself acknowledges boundaries require judgment; imposing quantitative thresholds would be ungrounded confabulation |

---

## Gap Analysis: Grounding-Revealed Issues

### Gap 1: Requirements-clarity gate needs D+B anchor

**Principles:** 3 (requirements completeness), 6 (observable evidence), 8 (assessment/action separation)

**Evidence:** IEEE 29148 requires explicit validation activity. Failure pattern #2: prose-only gates fail. The requirements-clarity gate is the highest-stakes entry point and the only remaining prose-only gate in Phase 0.

**Proposed fix:** Structured output before routing, matching the classification gate pattern:
- **Requirements source:** [requirements.md / user request / problem.md]
- **Completeness check:** [Each FR has mechanism: Y/N] [Each NFR has measurable criterion: Y/N]
- **Routing:** [Proceed to triage / Route to /requirements]

The key is observable output — not "validate that requirements are actionable" (prose judgment) but an explicit checklist the designer must populate with visible evidence.

### Gap 2: Classification criteria need named axes

**Principle:** 1 (complexity as routing signal)

**Evidence:** Stacey Matrix provides two concrete axes. Current criteria describe task *appearance* at each tier without naming the axes being assessed.

**Proposed fix:** Classification criteria section names two axes:
1. **Implementation certainty** — is the approach known? Prior art exists? Known technique?
2. **Requirement stability** — FRs agreed and mechanism-specified? Scope bounded?

Classification output cites which axes triggered the result. Simple requires both axes high; either axis low triggers Moderate or Complex.

### Gap 3: Design output format lacks explicit tradeoffs

**Principle:** 5 (context/decision/consequences)

**Evidence:** ADR requires consequences; Y-statement requires naming the accepted downside. design-content-rules.md governs density, repetition, and validation but not decision documentation structure.

**Proposed fix:** Add to design-content-rules.md: each major decision section must include "accepted tradeoffs" — what the choice makes harder or more expensive. Not a separate section per se; embedded in each decision's rationale block.

### Gap 4: Review gate criteria are not differentiated

**Principle:** 7 (staged review with differentiated criteria)

**Evidence:** NASA PDR/CDR uses different criteria per stage. outline-corrector and design-corrector currently both assess "completeness."

**Proposed fix:** Differentiate criteria as specified under Principle 7. Update outline-corrector prompt template (PDR criteria: direction, traceability, risk identification) and design-corrector prompt template (CDR criteria: specification completeness, implementability, verification approach).

### Gap 5: Companion task enforcement is prose-only

**Principle:** 6 (observable evidence), 8 (assessment/action separation)

**Evidence:** Failure pattern #1 (commit `e1a35cd1`): companion tasks treated as exempt. Rule added as prose; learning entry says agents bypass it.

**Proposed fix:** Before processing any companion task, require enumeration of all bundled tasks with individual Phase 0 output blocks (Classification: / Evidence: / Routing:) before proceeding to any of them. The enumeration is the structural anchor — it forces the agent to explicitly acknowledge and process each task rather than silently merging them.

### Gap 6: No structured-bugfix triage path

**Principles:** 1 (routing signal), 2 (complexity shifts)

**Evidence:** Cynefin's Complicated domain maps naturally to bug-fixing: cause is analyzable through investigation, fix is knowable by expert analysis. The grounding audit notes "structured-bugfix process as routing outcome" as a known extension. Behavioral code misclassification (failure pattern #6) often involves defect-type tasks where "conceptual simplicity" masks structural complexity.

**Proposed fix:** Add a fourth triage path: if the task is a defect (observed behavior ≠ expected behavior), route to a structured-bugfix workflow that enforces: (1) reproduce, (2) root-cause, (3) fix, (4) verify. This is Cynefin Complicated domain practice: expert analysis yields the answer, but the analysis must be structured to prevent premature-closure bias.

### Gap 7: No triage accuracy feedback loop

**Principle:** 2 (complexity shifts mid-task)

**Evidence:** Cynefin expects domain reassessment as intrinsic. Internal Gap 8: no post-execution mechanism to verify triage was correct. All structural patches in git history came from explicit failure discoveries, not systematic measurement. If a "Simple" task turns out to require behavioral code changes, there's no signal feeding back to improve triage criteria.

**Proposed fix:** This is a monitoring gap, not a process gap. The fix is detection, not prevention: when /orchestrate or /commit encounters evidence of triage mis-classification (e.g., task classified Simple but required multi-file behavioral changes), surface this as a learning entry. The existing learnings workflow captures this; the gap is triggering it automatically rather than depending on manual /reflect.

**Scope note:** This is a monitoring enhancement — downstream of the /design skill itself. Noted here for completeness; implementation belongs in orchestration or commit workflows, not in /design.

---

## Grounding Assessment

**Quality label:** Strong

**Evidence basis:**
- 6 primary framework clusters with citations and authority assessments
- 8 principles each grounded in ≥1 external framework with named citations
- 10 internal failure patterns with specific commit hashes mapped to external principles
- 7 gaps identified through framework → internal pattern comparison, each with concrete proposed fix
- Both branch artifacts retained as audit evidence

**What was searched:**
- "software task complexity classification framework methodology"
- "requirements to design workflow simple moderate complex"
- "architectural decision record ADR process framework"
- "design thinking double diamond software engineering adaptation"
- "architecture tradeoff analysis method ATAM CMU"
- "ISO IEEE 29148 requirements engineering process"
- "software design review methodology criteria 2024 2025"
- Git history: `git log --oneline --grep="reflect\|RCA\|deviat\|correct"`, `/reflect` artifacts, learnings.md, decision files

**Remaining ungrounded elements:**
- **Classification thresholds:** Neither Cynefin nor Stacey provides quantitative boundaries (both frameworks explicitly acknowledge this as a limitation). The project's criteria are a defensible operationalization; they are not derivable from external literature.
- **Option-generation methodology:** ADR and ATAM cover documentation and evaluation of decisions, not the reasoning process for generating options. How the designer generates alternatives before evaluating them remains ungrounded.
- **D+B anchor mechanism:** The specific technique of using tool calls to enforce gate execution is project-invented. No external framework addresses LLM-specific gate enforcement. The *principle* (observable evidence) is grounded; the *mechanism* (tool calls as proof-of-work) is project-specific.

---

## Sources

| Source | Type | Used for |
|--------|------|----------|
| [Cynefin Framework — Wikipedia](https://en.wikipedia.org/wiki/Cynefin_framework) | Primary (Snowden/IBM) | Complexity domain classification, routing, domain-shift warning |
| [Stacey Matrix — Praxis Framework](https://www.praxisframework.org/en/library/stacey-matrix) | Primary (Stacey) | Two-axis triage operationalization, named axes |
| [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) | International standard | Requirements completeness criteria, validation as distinct activity |
| [ADR — adr.github.io](https://adr.github.io/) | Primary (Nygard) | Decision documentation format, context/consequences structure |
| [ADR Process — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html) | Secondary (AWS adoption) | ADR lifecycle, review steps, "architecturally significant" criteria |
| [Double Diamond — Wikipedia](https://en.wikipedia.org/wiki/Double_Diamond_(design_process_model)) | Primary (Design Council) | Problem/solution space separation, Diamond 1/2 routing |
| [Double Diamond — Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/double-diamond) | Secondary (practitioner) | Software engineering adaptation |
| [NASA PDR/CDR — NPR 7123.1](https://nodis3.gsfc.nasa.gov/displayCA.cfm?Internal_ID=N_PR_7123_001A_&page_name=AppendixG) | Standard (NASA) | Staged design review gates, differentiated criteria |
| [ATAM — CMU SEI](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/) | Academic (SEI) | Quality attribute utility tree (referenced, not directly adapted) |
| [Documenting Architecture Decisions — Nygard](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) | Primary (origin) | ADR motivation, Y-statement format |

**Internal evidence:** `design-skill-internal-codebase.md` — 10 failure patterns with commit hashes, 8 gap types, 5 structural patterns extracted from git history + current skill analysis.
