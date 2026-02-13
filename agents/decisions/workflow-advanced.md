# Advanced Workflow Patterns

Requirements handling, knowledge management, and specialized workflow patterns.

## .Documentation and Knowledge Management

### When Seeding Indexes Before Generation

**Seeding before auto-generation:**

**Decision Date:** 2026-02-04

**Decision:** Seed indexes with entries pointing to existing permanent docs before expecting auto-generation to fill them.

**Anti-pattern:** Leaving knowledge indexes empty until consolidation runs.

**Rationale:** Non-empty index is immediately useful; seeding and consolidation are complementary bootstrap mechanisms.

**Impact:** Immediate value from indexes while consolidation builds them incrementally.

### When Adding Entries Without Documentation

**Index entries require backing documentation:**

**Decision Date:** 2026-02-04

**Decision:** Learnings → learnings.md → /remember → permanent doc → index entry.

**Anti-pattern:** Adding memory-index entries for concepts without permanent docs.

**Rationale:** Index entries are discovery surfaces for on-demand knowledge; they must point somewhere.

**Impact:** Index serves as reliable discovery mechanism, not aspirational wishlist.

### How to Merge Templates Safely

**Template merge semantics:**

**Decision Date:** 2026-02-04

**Decision:** Partial templates with explicit merge semantics — PRESERVE existing sections, ADD new items, REPLACE only specified content.

**Anti-pattern:** Generic templates that imply "replace structure with this form" (causes learnings deletion).

**Rationale:** "Template" implies blank slate; explicit semantics (preserve/add/replace) prevent unintended overwrites.

**Impact:** Safe template usage without data loss.

## .Requirements and Execution

### When Requirements Change During Execution

**Requirements immutable during execution:**

**Decision Date:** 2026-02-04

**Decision:** Requirements MUST NOT be updated if task execution made them outdated; updating requires explicit user confirmation.

**Anti-pattern:** Updating requirement files during task execution when implementation discovers they're outdated.

**Rationale:** Requirements document intent and decisions at planning time; execution discovering they're wrong means either (1) requirements need user review/approval before updating, or (2) implementation needs to match requirements despite being outdated.

**Impact:** Clear separation between planning (requirements) and execution (implementation).

## .Knowledge Discovery and Context

### When Embedding Knowledge In Context

**Ambient awareness beats invocation:**

**Decision Date:** 2026-02-04

**Research:** From Vercel study: Ambient context (100%) outperformed skill invocation (79%).

**Problem:** Skills not triggered 56% of cases — decision about "when to invoke" is failure point.

**Correct pattern:** Embed critical knowledge in loaded context (CLAUDE.md, memory-index).

**Directive:** "Prefer retrieval-led reasoning over pre-training knowledge" (memory-index.md header).

**Impact:** Always-available context beats sometimes-invoked skills.

### How to Name Tasks As Prose Keys

**Task prose keys pattern:**

**Decision Date:** 2026-02-04

**Pattern:** Task names serve as identifiers (no hash tokens needed).

**Implementation:** git log -S for on-demand history search, case-insensitive matching.

**Benefit:** Near-zero marginal cost, natural language keys, context recovery via task-context.sh.

**Impact:** Task names are both human-readable and machine-searchable identifiers.

## .Commit Workflow Patterns

### When Committing Rca Fixes

**Decision Date:** 2026-02-05

**Decision:** Three commit RCA fixes implemented and active in workflow.

**Fixes:**
1. **Submodule awareness:** Commit submodule first, then stage pointer in parent
2. **Artifact staging:** prepare-runbook.py stages its own artifacts via `git add`
3. **Orchestrator stop rule:** Absolute "no exceptions" language, deleted contradictory scenarios

**Status:** All fixes implemented and committed, active in current workflow.

**Impact:** Prevents submodule sync drift, missing artifacts in commits, and dirty-state rationalization.

### When Running Precommit Validation

**Decision Date:** 2026-02-05

**Decision:** `just precommit` must not modify source files (unlike `just dev` which autoformats).

**Exemption:** Volatile session state (`agents/session.md`) is exempt — `#PNDNG` token expansion runs in precommit.

**Rationale:** Precommit is validation, not transformation. Session state is ephemeral metadata, not source code.

**Impact:** Clear separation between validation (precommit) and transformation (dev) workflows.

## .Planning Workflow Patterns

### How to Expand Outlines Into Phases

**Decision Date:** 2026-02-05

**Decision:** Generate holistic outline first, then expand phase-by-phase with review after each.

**Anti-pattern:** Generate full runbook monolithically, review at end (late feedback).

**Rationale:** Outline provides cross-phase coherence; per-phase expansion provides earlier feedback. Quality preserved: outline catches structure issues before expensive full generation.

**Impact:** Earlier feedback, better cross-phase coherence, reduced rework.

### How to Review Phases Iteratively

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

**Key insight:** Review agent can read multiple phase files — doesn't need pre-assembled input.

**Fix:** Updated plan-tdd Phase 4/5 to clarify prepare-runbook.py handles assembly, planner provides phase files.

**Impact:** Consolidates assembly logic in one authoritative location, reduces manual errors.

### How to Use Review Agent Fix All Pattern

**Decision Date:** 2026-02-05

**Decision:** Review agents autofix everything, escalate unfixable issues.

**Three functions:**
1. Write review as audit trail (enables deviation monitoring)
2. Fix ALL issues directly (critical, major, minor)
3. Escalate unfixable to caller

**Escalation format:** Return filepath + "ESCALATION: N unfixable issues require attention"

**Applies to:** tdd-plan-reviewer, outline-review-agent, runbook-outline-review-agent, design-vet-agent

**Rationale:** Document fixes are low-risk; implementation fixes (vet-agent) remain review-only due to higher risk.

**Impact:** Caller handles escalation only, not routine fixes. Audit trail preserved for process improvement.

### How to Transmit Recommendations Inline

**Decision Date:** 2026-02-05

**Decision:** Append "Expansion Guidance" section to artifact being consumed (inline), not separate report.

**Anti-pattern:** Review agent writes recommendations to report file that gets ignored.

**Rationale:** Phase expansion reads outline; guidance co-located ensures consumption.

**Example:** runbook-outline-review-agent appends guidance to outline.md directly.

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

**Quality gate:** Prose must be behaviorally specific — "contains 🥈 emoji" not "returns correct value". tdd-plan-reviewer validates prose quality.

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

### When Using Consolidation Gates

**Decision Date:** 2026-02-05

**Decision:** Merge trivial work with adjacent complexity at two gates.

**Anti-pattern:** Trivial cycles left as standalone steps (config change, single constant).

**Gates:**
- **Gate 1 (Phase 1.6):** After outline — merge trivial phases with adjacent phases
- **Gate 2 (Phase 4.5):** After assembly — merge isolated cycles with related features

**Constraints:** Never cross phases, keep merged cycles ≤5 assertions, preserve test isolation.

**Rationale:** Haiku can handle "update constant X then implement feature Y" in one delegation.

**Impact:** Reduced orchestrator overhead for trivial work without losing test granularity.

### When Applying Feedback Loop Insights

**Decision Date:** 2026-02-05

**Decision:** Apply feedback loop principles to planning workflows.

**Principles:**
- **Alignment:** Review all agent output against requirements from clean context
- **Autofix:** Apply fixes immediately (don't rely on caller reading recommendations)
- **Outline:** Use staged expansion with alignment correction to prevent drift
- **Complexity gate:** Check before expansion, callback if too large

**Impact:** Self-correcting planning process prevents late-stage rework.

### When Dogfooding Process Design

**Decision Date:** 2026-02-05

**Decision:** Apply new process to its own planning (self-referential validation).

**Pattern:** Use the process you're designing to plan its own implementation.

**Example:** workflow-feedback-loops runbook planned using the feedback loop process it describes.

**Benefit:** Catches design issues before formal implementation. Phase-by-phase expansion with delegated reviews worked smoothly.

**Impact:** Design validation through practical application.

### When Scanning Requirements For Skills

**Decision Date:** 2026-02-11

**Decision:** Scan requirements for skill dependency indicators during A.0, load immediately.

**Anti-pattern:** Deferring skill loading to A.1 judgment when requirements explicitly mention agent/skill creation.

**Indicators:** "sub-agent" → agent-development, "invoke skill" → skill-development, "hook configuration" → hook-development

**Impact:** Early skill loading provides correct context for design decisions.

### When Crossing Phase Boundaries

**Decision Date:** 2026-02-11

**Decision:** Phase boundary = hard stop requiring explicit checkpoint delegation per orchestrate skill 3.3.

**Anti-pattern:** Treat checkpoint as part of step execution, skip vet-fix-agent delegation, proceed to next phase.

**Rationale:** Checkpoints catch bugs (e.g., logic error in format_context() found at Phase 2→3 boundary). D+B hybrid merged phase boundary into 3.3 with Read anchor for phase detection.

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

**Decision:** Domain-specific validation via skill files read by vet-fix-agent, with planning-time detection encoded in runbook vet steps.

**Pattern:** Planner detects domain (via rules files, design mentions, path patterns) → writes vet step referencing domain validation skill + artifact type → orchestrator copies instruction verbatim → vet-fix-agent reads skill file and applies criteria.

**Architecture:**
- **Domain validation skill:** `agent-core/skills/<domain>-validation/SKILL.md` — structured review criteria (Critical/Major/Minor + examples)
- **Rules file:** `.claude/rules/<domain>-validation.md` — path-matched context injection for planner
- **Planner awareness:** plan-adhoc and plan-tdd include "Domain Validation" subsection in vet checkpoint guidance
- **No agent proliferation:** One vet-fix-agent, enriched via skill files (not separate domain-specific review agents)

**First use case:** Plugin development validation (skills, agents, hooks, commands, plugin-structure)

**Rationale:**
- **Planning-time detection:** Intelligent planner (sonnet/opus) detects domain; weak orchestrator (haiku) executes mechanically
- **Dunning-Kruger avoidance:** Runtime self-assessment unreliable; planner encodes domain context explicitly
- **Sub-agents don't receive rules:** Rules files fire in main session only; domain context must be explicitly provided in task prompt
- **Cost management:** One agent with structured criteria cheaper than multiple specialist agents
- **Autofix trust:** Domain reviewer applies fixes directly (writer context may drift)

**Extensibility:** New domain = validation skill file + rules file + planner awareness (3-step template, no framework)

**Impact:** Domain-specific validation integrated into standard vet workflow without agent proliferation or orchestrator complexity.
