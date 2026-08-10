# Planning Workflow Patterns

Planning expansion, TDD, model selection, and validation patterns.

## .Planning Workflow Patterns

### How to Expand Outlines Into Phases

**Decision Date:** 2026-02-05

**Decision:** Generate holistic outline first, then expand phase-by-phase with review after each.

**Anti-pattern:** Generate full runbook monolithically, review at end (late feedback).

**Rationale:** Outline provides cross-phase coherence; per-phase expansion provides earlier feedback. Quality preserved: outline catches structure issues before expensive full generation.

**Impact:** Earlier feedback, better cross-phase coherence, reduced rework.

### .How to Review Phases Iteratively

**Decision Date:** 2026-02-05

**Decision:** For each phase: generate → delegate to reviewer (fix-all) → check for escalation → proceed.

**Anti-pattern:** Generate all phase files, then review/fix at end (batch optimization).

**Root cause:** Agent rationalized "saving time" by batching file generation.

**Key insight:** "For each phase" means iterative loop, not parallel generation.

**Impact:** Prevents drift accumulation, enables early course correction.

### When Assembling Runbooks Manually

**Decision Date:** 2026-02-11

**Decision:** Leave phase files separate during planning, holistic review reads multiple files, prepare-runbook.py handles assembly.

**Anti-pattern:** Using `cat` + `Write` to assemble phase files into runbook.md during planning.

**Rationale:** Assembly logic (metadata calc, cycle numbering validation) belongs in prepare-runbook.py, not manual process. Manual assembly error-prone: wrong cycle count, missing metadata, inconsistent formatting.

**Key insight:** Review agent can read multiple phase files — doesn't need pre-assembled input. Updated plan-tdd Phase 4/5 accordingly.

### How to Use Review Agent Fix All Pattern

**Decision Date:** 2026-02-05

**Decision:** Review agents autofix everything, escalate unfixable issues.

**Three functions:**
1. Write review as audit trail (enables deviation monitoring)
2. Fix ALL issues directly (critical, major, minor)
3. Escalate unfixable to caller

**Escalation format:** Return filepath + "ESCALATION: N unfixable issues require attention"

**Applies to:** runbook-corrector, outline-corrector, runbook-outline-corrector, design-corrector

**Rationale:** Document fixes are low-risk; implementation fixes remain review-only due to higher risk.

**Impact:** Caller handles escalation only, not routine fixes. Audit trail preserved for process improvement.

### How to Transmit Recommendations Inline

**Decision Date:** 2026-02-05

**Decision:** Append "Expansion Guidance" section to artifact being consumed (inline), not separate report.

**Anti-pattern:** Review agent writes recommendations to report file that gets ignored.

**Rationale:** Phase expansion reads outline; guidance co-located ensures consumption.

**Example:** runbook-outline-corrector appends guidance to outline.md directly.

**Impact:** Guidance reaches executor, not lost in separate report file.

### How to Name Review Reports

**Decision Date:** 2026-02-12

**Decision:** Review reports use descriptive base names that indicate artifact type and review focus. Iteration suffix (-2, -3) for subsequent reviews of same artifact.

**Pattern:**
- `outline-review.md` — first design outline review
- `outline-review-2.md` — second iteration after amendments
- `runbook-outline-review.md` — runbook outline review (different artifact type)
- `phase-N-review.md` — per-phase review during expansion
- `runbook-review.md` — final holistic runbook review
- `design-review.md` — design document review

**Iteration suffix vs descriptive suffix:**
- Use iteration number (-2, -3) when reviewing same artifact in same mode after fixes
- Use descriptive suffix when review has different focus (e.g., `-llm-failure-modes` for specialized analysis)

**Rationale:** Base name conveys artifact type and review stage. Iteration number tracks review cycles. Descriptive suffix reserved for specialized analyses.

**Impact:** Reports directory organization is predictable. Consumers can find latest review by pattern matching.

### When Writing Test Descriptions In Prose

**Decision Date:** 2026-02-05

**Decision:** Use prose descriptions with specific assertions in TDD RED phases, not full test code.

**Anti-pattern:** Full test code in runbook RED phases (copy-paste pattern).

**Token math:** Prose saves ~80% planning output tokens; haiku generates test code during execution anyway.

**Quality gate:** Prose must be behaviorally specific — "contains 🥈 emoji" not "returns correct value". runbook-corrector validates prose quality.

**Impact:** Significant token savings in planning phase without quality loss.

**Conformance exception:**

For conformance-type work (implementation with external reference: shell prototype, API spec, visual mockup, exact output format), prose descriptions MUST include the exact expected strings from the reference.

This is not full test code — it is precise prose that preserves the specification.

**Example contrast:**

| Standard prose | Conformance prose |
|----------------|-------------------|
| "Assert output contains formatted model with emoji and color" | "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator" |

**Rationale:** Standard prose is efficient for behavioral tests. For conformance work, the specification IS the exact string — abstracting it introduces translation loss. Precise prose preserves spec fidelity while maintaining token efficiency (still more compact than full test code).

### When Checking Complexity Before Expansion

**Decision Date:** 2026-02-05

**Decision:** Check complexity BEFORE expansion; callback to previous level if too large.

**Anti-pattern:** Expand all cycles regardless of complexity, discover problems late.

**Callback levels:** step → outline → design → design outline → requirements (human input)

**Fast paths:** Pattern cycles get template+variations; trivial phases get inline instructions.

**Key insight:** Complexity assessment is planning concern (sonnet/opus), not executor concern (haiku). Haiku optimizes for completion, not scope management.

**Impact:** Catch structure problems early, prevent executor overload.

### When Merging Trivial Cycles With Adjacent Work

**Decision Date:** 2026-02-05

**Decision:** Merge trivial work with adjacent complexity at two gates.

**Anti-pattern:** Trivial cycles left as standalone steps (config change, single constant).

**Gates:**
- **Gate 1 (Phase 1.6):** After outline — merge trivial phases with adjacent phases
- **Gate 2 (Phase 4.5):** After assembly — merge isolated cycles with related features

**Constraints:** Never cross phases, keep merged cycles ≤5 assertions, preserve test isolation.

**Rationale:** Haiku can handle "update constant X then implement feature Y" in one delegation.

**Impact:** Reduced orchestrator overhead for trivial work without losing test granularity.

### .When Applying Feedback Loop Insights

**Decision Date:** 2026-02-05

**Decision:** Apply feedback loop principles to planning workflows.

**Principles:**
- **Alignment:** Review all agent output against requirements from clean context
- **Autofix:** Apply fixes immediately (don't rely on caller reading recommendations)
- **Outline:** Use staged expansion with alignment correction to prevent drift
- **Complexity gate:** Check before expansion, callback if too large

**Impact:** Self-correcting planning process prevents late-stage rework.

### .When Dogfooding Process Design

**Decision Date:** 2026-02-05

**Decision:** Apply new process to its own planning (self-referential validation).

**Pattern:** Use the process you're designing to plan its own implementation.

**Example:** workflow-feedback-loops runbook planned using the feedback loop process it describes.

**Benefit:** Catches design issues before formal implementation. Phase-by-phase expansion with delegated reviews worked smoothly.

**Impact:** Design validation through practical application.

### When Requirements Mention Agent Or Skill Creation

**Decision Date:** 2026-02-11

**Decision:** Scan requirements for skill dependency indicators during A.0, load immediately.

**Anti-pattern:** Deferring skill loading to A.1 judgment when requirements explicitly mention agent/skill creation.

**Indicators:** "sub-agent" → agent-development, "invoke skill" → skill-development, "hook configuration" → hook-development

**Impact:** Early skill loading provides correct context for design decisions.

### When Crossing Phase Boundaries

**Decision Date:** 2026-02-11

**Decision:** Phase boundary = hard stop requiring explicit checkpoint delegation per orchestrate skill 3.3.

**Anti-pattern:** Treat checkpoint as part of step execution, skip corrector delegation, proceed to next phase.

**Rationale:** Checkpoints catch bugs (e.g., logic error in format_context() found at Phase 2→3 boundary). D+B hybrid merged phase boundary into 3.3 with Read anchor for phase detection.

### When Bootstrapping Self-Referential Improvements

**Decision Date:** 2026-02-15

**Decision:** When improving tools/agents, apply each improvement before using that tool in subsequent steps.

**Pattern:** Phase ordering follows tool-usage dependency graph, not logical grouping. Collapses design→plan→execute into design→apply for prose-edit work.

**Rationale:** Unimproved agents reviewing their own improvements creates a bootstrapping problem.

### When Outlines Conflate Decomposition With Sequencing

**Decision Date:** 2026-03-06

**Anti-pattern:** Design outlines that use "phases" to mean both "logical sub-problems" and "execution order." Forces premature ordering and defers design-time activities (grounding, research) into execution phases.

**Correct pattern:** Decomposition (breaking into sub-problems with dependency graph) is separate from sequencing (ordering for implementation). Sub-problems get tagged with design readiness — some are ready for runbook, others need more design. Sequencing happens at runbook time, not decomposition time. Design inputs (grounding, research) belong in the design process, not as execution phases.

**Evidence:** Active recall outline placed grounding (Phase 5) after metadata model commitment (Phase 4).

### When Requirements Added After Review

**Decision Date:** 2026-02-15

**Decision:** Requirements added after outline review must trigger re-check for traceability and mechanism specification.

**Anti-pattern:** Adding FRs after outline review without re-validating completeness.

**Evidence:** FR-18 added during design session bypassed outline-level validation, resulting in mechanism-free specification.

### When Deleting Agent Artifacts

**Decision Date:** 2026-02-18

**Anti-pattern:** Treating all ceremony artifacts as equally disposable.

**Correct pattern:** Distinguish audit trails with real findings from redundant restates. Review reports that improved artifacts have value; documents that reformat existing artifacts don't.

**Application:** Outline review found real issues (FR-2a gap, FR-3c contradiction) → keep the review report. design.md restated the reviewed outline without adding new decisions → disposable.

## .TDD Workflow Patterns

### How to Write Green Phase Descriptions

**Decision Date:** 2026-02-05

**Decision:** Describe behavioral requirements with approach hints in GREEN phase, not complete implementation code.

**Anti-pattern:** Writing complete implementation code in GREEN phase that can be copied verbatim.

**Correct pattern:** Describe behavioral requirements, provide approach hints, specify file location.

**Structure:** Behavior (WHAT code must DO) / Approach (high-level HOW) / Hint (specific technique)

**Rationale:** TDD discipline requires executor to WRITE code satisfying tests, not transcribe prescribed code.

**Impact:** Enforces test-first methodology, prevents copy-paste implementations.

## .Model Selection Patterns

### When Verifying Model Analysis Results

**Decision Date:** 2026-02-05

**Decision:** Use haiku for execution tasks, delegate architectural analysis to sonnet/opus, verify results.

**Anti-pattern:** Accepting haiku/sonnet analysis for critical architectural decisions without review.

**Example:** Haiku structural header analysis was incorrect (marked semantic headers as structural); sonnet analysis was correct.

**Rationale:** Efficient models optimize for speed, may miss nuance in architectural distinctions.

**Impact:** Appropriate model selection for analysis vs execution tasks.

## .Validation Patterns

### How to Implement Domain Validation

**Decision Date:** 2026-02-08

**Decision:** Domain-specific validation via skill files read by corrector, with planning-time detection encoded in runbook review steps.

**Pattern:** Planner detects domain (via rules files, design mentions, path patterns) → writes review step referencing domain validation skill + artifact type → orchestrator copies instruction verbatim → corrector reads skill file and applies criteria.

**Architecture:**
- **Domain validation skill:** `plugin/skills/<domain>-validation/SKILL.md` — structured review criteria (Critical/Major/Minor + examples)
- **Rules file:** `.claude/rules/<domain>-validation.md` — path-matched context injection for planner
- **Planner awareness:** plan-adhoc and plan-tdd include "Domain Validation" subsection in vet checkpoint guidance
- **No agent proliferation:** One corrector, enriched via skill files (not separate domain-specific review agents)

**First use case:** Plugin development validation (skills, agents, hooks, commands, plugin-structure)

**Rationale:**
- **Planning-time detection:** Intelligent planner (sonnet/opus) detects domain; weak orchestrator (haiku) executes mechanically
- **Dunning-Kruger avoidance:** Runtime self-assessment unreliable; planner encodes domain context explicitly
- **Sub-agents don't receive rules:** Rules files fire in main session only; domain context must be explicitly provided in task prompt
- **Cost management:** One agent with structured criteria cheaper than multiple specialist agents
- **Autofix trust:** Domain reviewer applies fixes directly (writer context may drift)

**Extensibility:** New domain = validation skill file + rules file + planner awareness (3-step template, no framework)

**Impact:** Domain-specific validation integrated into standard vet workflow without agent proliferation or orchestrator complexity.

### When Adding A New Variant To An Enumerated System

**Decision Date:** 2026-02-19

**Anti-pattern:** Updating only the authoritative definition section (type table, contract) but not downstream sections that enumerate existing variants.

**Correct pattern:** After updating the authoritative definition, grep all affected files for existing variant names (e.g., "tdd.*general", "both TDD and general") and update every enumeration site.

**Evidence:** Skill-reviewer found 1 critical (Phase 0.75 outline generation wouldn't produce inline phases), 3 major (description triggering, When to Use, Phase 1 expansion branch missing), 4 minor enumeration sites — all in runbook/SKILL.md alone.

### When TDD Cycles Grow Shared Test File

**Decision Date:** 2026-02-23

**Anti-pattern:** Each cycle agent adds tests to the designated test module without awareness of cumulative line count. The 400-line limit surfaces as precommit failure requiring refactor escalation.

**Correct pattern:** Step files for later cycles should include conditional split instructions: "If test file exceeds 380 lines, extract to separate module before adding tests." Alternatively, runbook planning should pre-assign test classes to separate files when cumulative growth is predictable.

**Evidence:** Test file grew from 382 → 478 lines across Phases 3-4. Each refactor escalation cost ~80-110K tokens.

### When Step File Inventory Misses Codebase References

**Decision Date:** 2026-02-23

**Anti-pattern:** Runbook step lists ~30 files for name propagation based on Phase 0.5 discovery. Actual codebase has ~45 files — discovery missed skills, decisions, fragments, agents, and script code paths.

**Correct pattern:** Discovery inventory must use `grep -r` across the full tree, not manual file listing. The verification step is the safety net, but discovery should cast a wider net initially.

**Evidence:** Step 1.6 agent modified 30 listed files. Second agent fixed 17 additional files. Orchestrator fixed 3 more.

### When Triaging Behavioral Code Changes As Simple

**Decision Date:** 2026-02-21

**Anti-pattern:** Assessing complexity from conceptual simplicity ("just read a config file") rather than structural criteria. Resolving ambiguity downward due to implementation eagerness.

**Correct pattern:** Simple criteria include "no behavioral code changes." Behavioral code (new functions, changed logic paths, conditional branches) routes to Moderate → `/runbook` → TDD phase-type assessment. Test discipline gated at triage, not emergent from routing.

**Root cause chain:** Motivated reasoning → resolved ambiguity downward → Simple path had no test gate → behavioral code shipped untested.

### When Design Proposes Removing Functions

**Decision Date:** 2026-03-02

**Rule:** When a design proposes removing a function, the corrector must read the function's implementation and all callers to verify the removal justification covers every purpose the function serves.

**Anti-pattern:** Accepting removal claims at face value. A function may serve multiple purposes. If the design identifies purpose (1) and justifies removing it, purpose (2) survives undetected. Every downstream stage trusts the claim.

**Correct pattern:** Corrector reads the function body and uses Grep to find all call sites. For each caller, verify the design accounts for how that caller's needs are met post-removal. Removal justification must cover all purposes, not just the one the design identified.

**Evidence:** task-classification plan D-4 conflated move semantics with post-merge hygiene. `_update_session_and_amend` served two purposes: (1) move-related session changes, (2) post-merge rm cleanup. Design only identified purpose (1), removed function. Outline review caught incomplete failure mode analysis (Major #1) but accepted "eliminated" as sufficient. Regression required restoring the function.

**Placement:** Design-corrector agent, not /design skill. Corrector independently verifies — avoids coupling verification to the same agent that proposed the removal.
