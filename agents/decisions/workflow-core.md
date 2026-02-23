# Workflow Patterns

Workflow-related architectural decisions and patterns.

## When Using Oneshot Workflow

**Decision Date:** 2026-01-19

**Decision:** Implement and validate weak orchestrator pattern with runbook-specific agents for ad-hoc task execution.

**Status:** Complete - All phases delivered, pattern validated

**Key Components:**
- Baseline task agent (`agent-core/agents/artisan.md`)
- Runbook preparation script (`agent-core/bin/prepare-runbook.py`)
- 5 skills: `/design`, `/plan-adhoc`, `/orchestrate`, `/review`, `/codify`
- Complete documentation (documented in CLAUDE.md and agent-core)

**Weak orchestrator pattern:**

**Pattern Validation:**
- Haiku successfully executes runbook steps using runbook-specific agents
- Error escalation works (haiku → sonnet → opus)
- Quiet execution pattern maintains lean orchestrator context
- Context caching via runbook-specific agents reduces token costs

**Terminology Standardization:**
- Job = user's goal
- Design = architectural spec from opus
- Runbook = implementation steps (replaces "plan" in execution context)
- Step = individual unit of work
- Runbook prep = 4-point process (Evaluate, Metadata, Review, Split)

**Impact:**
- Production-ready workflow for ad-hoc tasks
- Reduced context overhead through specialized agents
- Standardized terminology across documentation
- Reusable components via agent-core submodule

## How to Integrate Tdd Workflow

**Decision Date:** 2026-01-19, Updated 2026-01-26

**Decision:** Extend weak orchestrator pattern to support TDD methodology for feature development.

**Status:** Complete - All 8 steps delivered, production-ready

**Key Components:**
- TDD workflow documentation (`agent-core/agents/tdd-workflow.md`)
- TDD baseline agent (`agent-core/agents/test-driver.md`)
- `/plan-tdd` skill with 5-phase execution (includes automated review)
- Cycle-based runbooks supporting RED/GREEN/REFACTOR progression
- TDD task agent pattern with cycle-aware instruction sets
- TDD runbook reviewer (`agent-core/agents/runbook-corrector.md`) for prescriptive code detection
- Review skill (`agent-core/skills/review-tdd-plan/`) for anti-pattern detection

**TDD workflow:**

**Architecture:**
- Unified design entry point (`/design` skill) supports both oneshot and TDD modes
- RED phase: Write failing tests, document intent
- GREEN phase: Describe behavior and provide hints (NOT prescriptive code)
- REFACTOR phase: Improve code quality while maintaining tests
- **Automated review**: runbook-corrector detects prescriptive code violations
- **Mandatory prepare-runbook.py**: Generates step files before /orchestrate
- Cycle-aware task delegation with scoped runbooks per cycle
- Quiet execution pattern preserves orchestrator context

**Key Decisions:**
- Cycle-based splitting: Each RED/GREEN/REFACTOR as separate runbook cycle
- Model assignment: Sonnet for TDD planning, haiku for implementation, opus for design
- Deduplication: Use 4-point prep to avoid overlap with oneshot workflow
- Testing focus: Behavioral verification with full test coverage
- Progressive discovery: Documentation read only when executing TDD workflow
- Anti-pattern detection: Automated review prevents prescriptive code in GREEN phases
- Mandatory artifact generation: prepare-runbook.py must run before /orchestrate

**Impact:**
- Production-ready TDD workflow for test-first development
- Enforced test-first methodology via /plan-tdd skill
- Prescriptive code detection prevents "copy-paste" implementations
- Reusable cycle patterns via agent-core documentation
- Consistent terminology across test and implementation phases
- Proper execution flow: design → plan → review → prepare → orchestrate

## .How to Store Learnings In Handoffs

**Handoff pattern:**

**Decision Date:** 2026-01-27

**Decision:** Store session learnings inline in `session.md` rather than separate file system.

**Rationale:**
- Separate file system (pending.md + individual learning files) requires script management
- Inline learnings are easier to edit, update, and refine during handoffs
- Simpler workflow without add-learning.py complexity
- Single source of truth for session state

**Implementation:**
- Removed `agents/learnings/` directory entirely
- All learnings now in `session.md` Recent Learnings section
- Handoff skill simplified (removed script dependencies)

**Impact:**
- Reduced handoff complexity
- Easier to discover and update learnings
- Self-contained session documentation

## When Optimizing Design Phase Output

**Decision Date:** 2026-01-27

**Decision:** Minimize designer (premium model) output tokens by writing for intelligent readers.

**Rationale:**
- Large tasks require planning step anyway - planner can infer details
- Dense design output aligns with planning needs
- Intelligent downstream agents don't need obvious details spelled out

**Pattern:**
- Designer produces concise, high-level architectural guidance
- Planner elaborates details during runbook creation
- Implementation agents work from detailed runbook steps

**Impact:**
- Reduced token cost in premium design phase
- No loss of implementation quality (detail added in planning)
- Faster design sessions

## How to Document Three Stream Planning

**Decision Date:** 2026-01-27

**Decision:** Document parallel work streams with `problem.md` (analysis) + `session.md` (design proposals).

**Rationale:**
- Enables async prioritization without re-discovering context
- User can select work stream based on documented analysis
- Scales well for complex sessions with multiple improvement areas

**Structure:**
```
plans/<stream-name>/
├── problem.md      # Analysis: what's broken, why it matters
└── session.md      # Design proposals and decisions
```

**Example:** During TDD session, documented handoff skill improvements, model awareness, and plan-tdd improvements as separate streams with complete analysis.

**Impact:**
- Better context preservation across sessions
- User can prioritize work streams easily
- Clear separation of analysis vs design

## .How to Squash Tdd Cycle Commits

**TDD commit squashing:**

**Decision Date:** 2026-01-27

**Decision:** Squash TDD cycle commits into single feature commit while preserving granular cycle progression in reports.

**Pattern:**
1. Create backup tag before squashing
2. `git reset --soft <base-commit>` to staging area
3. Create squashed commit with feature message
4. Cherry-pick subsequent commits (if any)
5. Test result before cleanup
6. Delete backup tag after verification

**Rationale:**
- Clean git history (one commit per feature)
- Complete cycle-by-cycle implementation preserved in runbook reports
- Avoids polluting history with WIP commits

**Impact:**
- Production-ready commit history
- Full audit trail in execution reports
- Easy to review feature implementation holistically

## When Setting Orchestrator Execution Mode

**Decision Date:** 2026-01-31

**Decision:** Execution mode metadata in orchestrator plan overrides system prompt parallelization directives.

**Problem:** System prompt parallelization directive (strong emphasis, 3x repetition) overrides orchestrate skill sequential requirement when tasks appear syntactically independent but are semantically state-dependent (TDD cycles, git commits).

**Solution:**
- Use `claude0` (`--system-prompt "Empty."`) to remove competing directives
- Execution mode metadata in orchestrator plan is authoritative
- ONE Task call per message when execution mode is sequential
- Plan must include rationale and explicit override instructions

**Pattern:**
```markdown
**Execution Mode:** STRICT SEQUENTIAL

**Rationale:** TDD cycles modify shared state. Parallel execution causes git commit race conditions and RED phase violations.

**Override:** Execute ONE Task call per message, regardless of syntactic independence.
```

**Rationale:**
- Syntactic independence (no parameter dependencies) != semantic independence (state dependencies)
- Strong directive language ("CRITICAL", "MUST", all-caps) matches system prompt emphasis level
- Explicit rationale prevents future misinterpretation

**Impact:**
- Prevents race conditions in TDD workflow execution
- Clear contract between planner and orchestrator
- Eliminates ambiguity in execution mode requirements

## When Assessing Orchestration Tier

**Three-tier assessment:**

**Decision Date:** 2026-01-31 (updated 2026-01-31)

**Decision:** Plan skills use three-tier assessment to route work appropriately. This supersedes the original binary (direct vs runbook) decision.

**Three Tiers:**

**Tier 1 (Direct Implementation):**
- Design complete (no open decisions)
- All edits straightforward (<100 lines each)
- Total scope: <6 files
- Single session, single model
- No parallelization benefit
- **Sequence:** Implement directly → vet agent → apply fixes → `/handoff --commit`

**Tier 2 (Lightweight Delegation):**
- Design complete, scope moderate (6-15 files or 2-4 logical components)
- Work benefits from agent isolation but not full orchestration
- Components are sequential (no parallelization benefit)
- No model switching needed
- **Sequence:** Delegate via Task tool (artisan/test-driver) with context in prompts → vet agent → `/handoff --commit`
- **Repetitive pattern variant:** ~15-20 cycles with same pattern qualifies as Tier 2 — plan cycle descriptions, delegate individually, checkpoint every 3-5 cycles. Full runbook overhead not justified for simple repetitive work

**Tier 3 (Full Runbook):**
- Multiple independent steps (parallelizable)
- Steps need different models
- Long-running / multi-session execution
- Complex error recovery
- >15 files or complex coordination
- **Sequence:** 4-point process → prepare-runbook.py → handoff → restart → orchestrate

**Rationale:** Matches orchestration overhead to task complexity. Tier 1 avoids unnecessary process for simple tasks. Tier 2 provides middle ground with context isolation but minimal overhead. Tier 3 preserves full pipeline for complex work.

**Impact:** Prevents unnecessary runbook creation for straightforward tasks while surfacing lightweight delegation as middle ground.

## How to Checkpoint Runbook Execution

**Checkpoint process:**

**Decision Date:** 2026-01-31

**Decision:** Two-step checkpoints at natural boundaries in runbook execution.

**Pattern:**
1. **Fix checkpoint:** `just dev` (lint, tests, build verification)
2. **Vet checkpoint:** Quality review (code review, architecture validation)

**Rationale:** Balances early issue detection with cost efficiency. Avoids both extremes: all-at-once review/correction (late detection) and per-step review/correction (excessive overhead).

**Impact:** Optimal cost-benefit for runbook quality assurance.

## How to Structure Phase Grouped Runbooks

**Decision Date:** 2026-01-31

**Decision:** Support both flat (H2) and phase-grouped (H2 + H3) cycle headers in runbooks.

**Patterns:**
- Flat: `## Cycle X.Y`
- Phase-grouped: `## Phase N` / `### Cycle X.Y`

**Implementation:** `prepare-runbook.py` regex changed from `^## Cycle` to `^###? Cycle`

**Rationale:** Phase grouping improves readability for large runbooks with logical phases.

**Impact:** Flexible runbook structure for different complexity levels.

## When Cycle Numbering Has Gaps

**Decision Date:** 2026-02-04

**Decision:** Gaps in cycle numbering are warnings, not errors. Duplicates and invalid start numbers remain errors.

**Rationale:** Document order defines execution sequence — numbers are stable identifiers, not sequence indicators. Treating gaps as fatal errors caused excessive editing churn (10+ edits per gap).

**Implementation:** `prepare-runbook.py` validation downgraded gap detection from ERROR to WARNING.

**Impact:** Reduced editing friction during runbook creation while maintaining validation for actual errors.

## When Refactoring Needs Escalation

**Decision Date:** 2026-01-31

**Decision:** Design decisions are made during `/design` phase. Opus handles architectural refactoring within design bounds. Human escalation only for execution blockers.

**Rationale:** Blocking pipeline for human input during refactoring is expensive.

**Impact:** Faster execution, clear separation between design (user input) and implementation (automated).

## How to Verify Commits Defense In Depth

**Commit verification:**

**Decision Date:** 2026-01-31

**Decision:** Multiple layers of commit verification at different execution levels.

**Layers:**
- **test-driver agent:** Post-commit sanity check (verify commit contains expected files)
- **orchestrate skill:** Post-step tree check (escalate if working tree dirty)

**Rationale:** Catches different failure modes at different levels (commit content vs working tree state).

**Impact:** Robust commit verification without single point of failure.

## .Delegation Patterns

### When Delegating Without Plan

**Decision Date:** 2026-02-11

**Decision:** Opus provides runbook OR acceptance criteria when delegating implementation.

**Anti-pattern:** Opus specifies "do X | haiku" without runbook/acceptance criteria.

**Consequence:** Without criteria, executing agent cannot verify alignment, vet cannot check drift.

**Haiku-specific:** Handoff uses `/handoff-haiku` not `/handoff` (no learnings judgment).

**Root cause:** Task had model spec but no execution spec.

**Fix:** Handoff skill now requires haiku tasks to include acceptance criteria (table + examples).

**Impact:** Delegated implementations maintain alignment through explicit criteria.

