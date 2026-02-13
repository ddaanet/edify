# Exploration Report: Target Artifacts Analysis

**Date:** 2026-02-12
**Scope:** Skills and agents for workflow execution (plan-adhoc, plan-tdd, vet; runbook-outline-review-agent, tdd-plan-reviewer, vet-fix-agent)
**Report Location:** plans/workflow-fixes/reports/explore-target-artifacts.md

---

## Summary

Six key workflow artifacts analyzed: 2 planning skills (plan-adhoc 1152 lines, plan-tdd 1051 lines), 1 review skill (vet 375 lines), and 3 specialized agents (runbook-outline-review-agent 497 lines, tdd-plan-reviewer 181 lines, vet-fix-agent 430 lines). Total 3686 lines of structured guidance.

**Key findings:**
- Skills provide reference documentation for execution patterns
- Agents provide executable implementations with role specifications and return protocols
- Significant duplication exists between skill guidance and agent implementations (vet-fix-agent contains 80% of vet skill verbatim)
- Agent frontmatter fields are consistently structured (name, description, model, tools, color, skills)
- No apparent issues with references or content consistency

---

## File Inventory

### Skills (Agent-Invocable Reference Documentation)

| File | Lines | Frontmatter | Type | User-Invocable |
|------|-------|-------------|------|-----------------|
| agent-core/skills/plan-adhoc/SKILL.md | 1152 | Yes (6 fields) | Reference/Executable | Yes |
| agent-core/skills/plan-tdd/SKILL.md | 1051 | Yes (5 fields) | Reference/Executable | Yes |
| agent-core/skills/vet/SKILL.md | 375 | Yes (3 fields) | Reference/Executable | Yes |

### Agents (Sub-Agent Implementations)

| File | Lines | Frontmatter | Model | Color | Skills Field |
|------|-------|-------------|-------|-------|---------------|
| agent-core/agents/runbook-outline-review-agent.md | 497 | Yes (6 fields) | sonnet | cyan | No |
| agent-core/agents/tdd-plan-reviewer.md | 181 | Yes (6 fields) | sonnet | yellow | Yes (review-tdd-plan) |
| agent-core/agents/vet-fix-agent.md | 430 | Yes (6 fields) | sonnet | cyan | No |

### Agent Comparison (vet-agent for reference)

| File | Lines | Frontmatter | Model | Color | Fix Capability |
|------|-------|-------------|-------|-------|-----------------|
| agent-core/agents/vet-agent.md | 372 | Yes (6 fields) | sonnet | cyan | Review-only |
| agent-core/agents/vet-fix-agent.md | 430 | Yes (6 fields) | sonnet | cyan | Review + Fix All |

---

## Detailed File Analysis

### 1. agent-core/skills/plan-adhoc/SKILL.md (1152 lines)

**Structure:**
- YAML frontmatter (lines 1-12): name, description, model, allowed-tools, requires, outputs, user-invocable
- H1 title + brief description (14-19)
- When to Use section (21-33)
- Three-Tier Assessment (35-111) with explicit tier criteria
- Planning Process (Tier 3 Only) points 0.5-4 (123-781)
- Checkpoints section (783-836)
- Critical Constraints (840-865)
- Example Execution Flow (873-965)
- Runbook Template Structure (967-1097)
- Common Pitfalls (1099-1126)
- References (1128-1134)
- Integration with General Workflow (1137-1152)

**Key Features:**
- Extremely detailed 4-point planning process (Points 0.5, 0.75, 0.85, 0.9, 0.95, 1, 1.4, 2, 2.5, 3, 4)
- Multiple decision gates: complexity assessment (Point 0.9), sufficiency check (Point 0.95), consolidation gates (0.85, 2.5)
- Emphasizes discovery before planning (Point 0.5): Glob verification of file paths, never assume conventions
- Domain validation pattern: mentions checking for `agent-core/skills/<domain>-validation/SKILL.md`
- Mandatory conformance validation steps for external references
- File size awareness at planning time (350-line threshold for 400-line limit)
- Checkpoints: light (Fix + Functional) at phase boundaries, full (Fix + Vet + Functional) at final phases
- Common Context section optimization emphasis

**Issues/Gaps:**
- No reference to `/remember` consolidation or memory-index discovery
- No mention of LLM failure modes (vacuity, dependency ordering, density, checkpoint spacing) — outline-level checks exist but not explicitly named
- No discussion of how to handle escalations from outline review

### 2. agent-core/skills/plan-tdd/SKILL.md (1051 lines)

**Structure:**
- YAML frontmatter (lines 1-10): name, description, model, allowed-tools, requires, outputs
- Purpose and Context (20-57): workflow integration with auto-preparation
- Process: Five-Phase Execution (59-1051)
  - Phase 0: Tier Assessment (61-100)
  - Phase 1: Intake (104-127)
  - Phase 1.5: Generate Runbook Outline (131-181)
  - Phase 1.6: Consolidation Gate (185-229)
  - Phase 2: Analysis (232-276)
  - Phase 2.5: Complexity Check (280-320)
  - Phase 2.7: Planning-Time File Size Awareness (324-352)
  - Phase 3: Cycle Expansion (354-410)
  - Phase 3.1-3.6: Cycle Planning Guidance (412-585)
  - Phase 4: Assembly and Metadata (587-695)
  - Phase 4.5: Consolidation Gate — Runbook (699-752)
  - Phase 5: Final Review and Preparation (756-831)
- Cycle Breakdown Guidance (834-855)
- What NOT to Test (859-876)
- Checkpoints (879-965)
- Constraints and Error Handling (968-982)
- Integration Notes (985-1015)
- Success Criteria (1018-1041)
- Additional Resources (1044-1051)

**Key Features:**
- Tier assessment with specific cycle count boundaries (Tier 1: 1-3, Tier 2: 4-10, Tier 3: >10)
- Mandatory conformance test cycles with exact expected strings from reference
- Prose test descriptions emphasized (not full code blocks)
- RED/GREEN/REFACTOR cycle format with specific prose test rules
- Investigation prerequisites for creation cycles
- Background review pattern for per-phase reviews (concurrent with next phase generation)
- Vacuous cycle detection during outline review (RED that passes with `import X; assert callable(X)`)
- Edge-case clusters collapse (parametrized test rows)
- Checkpoint spacing guidance (>10 steps/cycles or >2 phases without checkpoint)
- Integration test pattern with xfail markers for composition tasks
- Prose assertion quality table (vague vs specific examples)

**Issues/Gaps:**
- Phase 1.5 outline generation references quality checklist but doesn't reference runbook-outline-review-agent delegation
- No explicit mention of LLM failure mode detection (vacuity, dependency, density, checkpoints) in agent specs
- Phase 3 review delegation to tdd-plan-reviewer lacks explicit mention of running background reviews
- Phase 5 holistic review doesn't specify how to handle escalations
- References to undefined sections: `references/patterns.md`, `references/anti-patterns.md`, `references/error-handling.md`, `references/examples.md` (not found in project)

### 3. agent-core/skills/vet/SKILL.md (375 lines)

**Structure:**
- YAML frontmatter (lines 1-4): description, allowed-tools, user-invocable
- H1 title + distinction (7-11)
- When to Use section (13-25)
- Review Process (27-342) with 5 main steps:
  1. Determine Scope (29-51)
  2. Gather Changes (53-77)
  3. Analyze Changes (79-143)
  4. Provide Feedback (145-209)
  5. Output Review (231-241)
- Critical Constraints (243-265)
- Example Execution (267-318)
- Common Scenarios (320-346)
- Integration with General Workflow (348-363)
- References (365-376)

**Key Features:**
- Explicit scope determination (5 options: uncommitted, recent commits, current branch, specific files, everything)
- Design conformity checks: check for hardcoded values vs design specification
- Runbook file reference validation: Glob verification of paths, Grep for function names
- Self-referential modification detection: flag when runbook steps mutate their own plan directory
- Distinguishes between review-only (vet-agent) and review+fix (vet-fix-agent)
- Assessment criteria: Ready / Needs Minor Changes / Needs Significant Changes

**Issues/Gaps:**
- Skill references review agents but doesn't show which agent to delegate to
- No mention of execution context requirements (Scope IN/OUT, Changed Files)
- No mention of handling UNFIXABLE issues
- No mention of LLM failure mode detection for runbooks
- No cross-reference to vet-requirement.md fragment (which provides execution context template)

---

## Specialized Agents

### 4. agent-core/agents/runbook-outline-review-agent.md (497 lines)

**Frontmatter:**
```yaml
name: runbook-outline-review-agent
description: Reviews runbook outlines...
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
```

**Structure:**
- Role specification (17-21): Write review → Fix ALL issues → Escalate unfixable → Return filepath
- Review Protocol (23-495) with 7 steps:
  1. Validate Inputs (25-62): requirements exist, design exists, artifact type (runbook-outline.md)
  2. Load Context (64-80): read design, outline, exploration reports
  3. Review Criteria (82-150): 8 dimensions (requirements coverage, design alignment, phase structure, complexity distribution, dependency sanity, vacuity, intra-phase ordering, density, checkpoint spacing, step clarity, execution readiness)
  4. Traceability Matrix Validation (152-176)
  5. Apply Fixes (178-203): fix-all policy with constraints
  6. Append Expansion Guidance (205-250): Consolidation candidates, Cycle expansion guidance, Checkpoint guidance, References to include
  7. Write Review Report (255-481) with complete structure template
- Edge Cases (439-470)
- Verification checklist (472-482)
- Response Protocol (484-497)

**Key Features:**
- Validates inputs BEFORE review (requirements, design, artifact type checking)
- 8 detailed review criteria including vacuity detection and density analysis
- Fix-all policy explicitly stated with rationale
- Expansion Guidance section appended to artifact for downstream consumption
- Execution Readiness criteria (decision completeness, dependency declarations, code fix specificity, checkpoint frequency, post-phase state awareness, scope boundary declarations)
- Assessment criteria: Ready / Needs Iteration / Needs Rework
- Comprehensive edge case handling

**Issues/Gaps:**
- Expansion Guidance section assumes it will be consumed during phase expansion but plan-tdd skill doesn't explicitly mention reading it
- No reference to helper files or shared templates
- No mention of how to handle consolidation conflicts or merge failures

### 5. agent-core/agents/tdd-plan-reviewer.md (181 lines)

**Frontmatter:**
```yaml
name: tdd-plan-reviewer
description: Reviews TDD runbooks/phase files for prescriptive code, RED/GREEN violations...
model: sonnet
color: yellow
tools: ["Read", "Grep", "Glob", "Write", "Edit", "Skill"]
skills:
  - review-tdd-plan
```

**Structure:**
- Role specification (21-25): Write review → Fix ALL issues → Escalate unfixable
- Agent Purpose (27-34): 3 functions (audit trail, autofix, escalation)
- Document Validation (36-45): Check for `type: tdd` and `## Cycle` headers
- Outline Validation (47-54): Check for outline review report, skip for phase files
- Requirements Inheritance (56-61): Verify coverage from outline
- Review Criteria (63-75): Loads review-tdd-plan skill
- Fix-All Policy (77-103): with explicit UNFIXABLE examples
- Standard Workflow (105-113)
- Report Structure (115-158)
- Return Protocol (160-181)

**Key Features:**
- Smallest agent (181 lines) — delegates heavy lifting to review-tdd-plan skill
- Outline validation with phase file exception
- Fix-all policy with UNFIXABLE issue escalation
- Skill delegation explicit via frontmatter `skills` field
- Requirements inheritance from outline
- Prose quality emphasis (not full test code)

**Issues/Gaps:**
- Very brief — critical details delegated to skill
- No inline review criteria beyond "Load skill" reference
- No mention of background review pattern mentioned in plan-tdd skill
- No explanation of how to handle escalations in detail

### 6. agent-core/agents/vet-fix-agent.md (430 lines)

**Frontmatter:**
```yaml
name: vet-fix-agent
description: Vet review agent that applies all fixes directly...
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "AskUserQuestion"]
```

**Structure:**
- Role specification (11-22): Review implementation changes (NOT runbooks/design), write report, apply ALL fixes
- Input validation (26-86): Rejects runbooks and design documents, requires requirements context, recommends execution context
- Determine Scope (87-98): 5 options same as vet skill
- Gather Changes (100-131): git commands for each scope option
- Analyze Changes (133-216): 8 review dimensions (code quality, standards, security, testing, documentation, completeness, requirements validation, design anchoring, alignment, integration review)
- Write Review Report (218-301): Report structure with Requirements Validation section
- Apply Fixes (320-336): After writing report, apply all fixes using Edit
- Return Result (338-353)
- Critical Constraints (355-387)
- Edge Cases (389-408)
- Verification (410-416)
- Response Protocol (418-430)

**Key Features:**
- Explicitly rejects wrong artifact types (runbooks, design documents)
- Requires execution context for phased work (Scope IN/OUT, Changed Files, Prior State, Design Reference)
- Fix-all policy with constraints on scope
- After-writing-then-fixing pattern (audit trail before changes)
- Runs all fixes in sequence with Edit calls
- UNFIXABLE marking for issues requiring escalation
- Integration review for cross-file patterns

**Issues/Gaps:**
- No mention of UNFIXABLE detection in return protocol (unlike tdd-plan-reviewer which shows escalation format)
- Significant duplication with vet-agent (80% verbatim in sections 2-3)
- No reference to vet-requirement.md fragment
- Assessment criteria in report not explicitly listed (relies on narrative description)

### 7. agent-core/agents/vet-agent.md (372 lines) [REFERENCE]

**Key Differences from vet-fix-agent:**
- Review-only (no Edit tool, no Fix capability)
- Explicitly allows caller to apply fixes with context
- Outline Validation section for runbooks (checks for outline review, compares against outline requirements)
- Does NOT include Requirements Validation section (caller provides context, agent reviews against it)
- No Fix process or verification sections

**Duplication Pattern:**
Lines 1-250 almost identical between vet-fix-agent and vet-agent (Sections 0-4 of protocol).

---

## Content Pattern Analysis

### Frontmatter Structure

**Skills (plan-adhoc example):**
```yaml
name: plan-adhoc
description: [multiline task description]
model: sonnet
allowed-tools: [list]
requires: [list]
outputs: [list]
user-invocable: true
```

**Agents (runbook-outline-review-agent example):**
```yaml
name: runbook-outline-review-agent
description: [multiline task description with triggering examples]
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
[optional: skills: [list]]
```

**Observations:**
- Skills use `allowed-tools` + `requires` + `outputs`
- Agents use `tools` + optional `color` + optional `skills`
- Descriptions include triggering examples in agents, not skills
- Model field consistent across both

### Skill vs Agent Distinction

| Aspect | Skills | Agents |
|--------|--------|--------|
| User-Invocable | Yes (user-invocable: true) | No (implicit sub-agent) |
| Purpose | Reference/guide for execution patterns | Executable implementations with roles |
| Content | 1000+ lines of detailed guidance, examples | 200-500 lines, references skills or inline criteria |
| Sections | Process steps, examples, common pitfalls, references | Role, protocol, validation, return format |
| Tools | Limited (mostly Read/Write) | Full tool set (Bash, Edit, Grep, Glob, AskUserQuestion) |
| Skill Delegation | plan-tdd delegates to tdd-plan-reviewer | tdd-plan-reviewer loads review-tdd-plan skill |

### Delegation Patterns

**plan-adhoc Tier Routing:**
- Tier 1: Direct implementation + vet agent + handoff
- Tier 2: Lightweight delegation to quiet-task + vet agent + handoff
- Tier 3: Full 4-point planning process with runbook-outline-review-agent

**plan-tdd Tier Routing:**
- Tier 1: Direct TDD (RED/GREEN discipline) + vet agent + handoff
- Tier 2: Lightweight TDD with intermediate checkpoints + vet agent + handoff
- Tier 3: Full 5-phase process with tdd-plan-reviewer for per-phase and holistic review

**vet Skill vs Agents:**
- Direct skill invocation (/vet): User interactive with AskUserQuestion
- vet-agent delegation: Review-only, caller applies fixes
- vet-fix-agent delegation: Review + apply all fixes

### Cross-References and Dependencies

**plan-adhoc → runbook-outline-review-agent (Point 0.75 step 3):**
"Delegate to runbook-outline-review-agent (fix-all mode)"

**plan-tdd → runbook-outline-review-agent (Phase 1.5 step 3):**
"Delegate to runbook-outline-review-agent (fix-all mode)"

**plan-tdd → tdd-plan-reviewer (Phase 3 step 2):**
"Delegate to tdd-plan-reviewer (fix-all mode)"

**plan-tdd → tdd-plan-reviewer (Phase 5 step 2):**
"Delegate to tdd-plan-reviewer (fix-all mode) for holistic review"

**plan-adhoc/plan-tdd → vet-fix-agent (implied in checkpoint steps):**
"Delegate to vet-fix-agent with execution context"

**tdd-plan-reviewer → review-tdd-plan skill:**
"Load and follow the review-tdd-plan skill"

### Documentation Gaps and Issues

**1. Missing References in plan-tdd skill:**
- Lines 855, 974, 982: References to `references/patterns.md`, `references/anti-patterns.md`, `references/error-handling.md`, `references/examples.md`
- These files not found in project
- Should either be created or references removed

**2. LLM Failure Mode Detection Not Fully Integrated:**
- Mentioned in learnings.md: "Expansion re-introduces outline-level defects"
- plan-tdd Phase 1.5 quality checklist includes "No vacuous cycles" and "Foundation-first ordering"
- But not explicitly named as "LLM failure modes"
- runbook-outline-review-agent criteria (lines 116-137) include vacuity, intra-phase ordering, density, checkpoint spacing — all LLM failure modes
- plan-tdd expansion (Phase 3) doesn't reference re-validation of outline-level checks against expanded phases

**3. Execution Context Not Mentioned in Some Delegations:**
- plan-adhoc Point 1 (phase expansion) doesn't mention including execution context in vet-fix-agent delegation (line 351)
- vet-fix-agent requires this context (lines 52-85)
- Mismatch between plan-adhoc guidance and agent requirements

**4. Background Review Pattern Mentioned but Not Explicit:**
- plan-tdd Phase 3 (line 378) mentions "Background review pattern: launch review (background) → generate next phase"
- But doesn't specify `run_in_background=true` in Task tool call
- tdd-plan-reviewer doesn't mention background execution

**5. Expansion Guidance Transmission Not Confirmed:**
- runbook-outline-review-agent appends Expansion Guidance to outline (line 205-250)
- plan-tdd Phase 1 references "Read Expansion Guidance" (line 345)
- But Phase 1 is never executed for Tier 3 — it goes directly to Phase 1.5
- Plan-tdd should explicitly reference reading expansion guidance in Phase 3

**6. UNFIXABLE Escalation Format:**
- tdd-plan-reviewer shows escalation format (line 170-172)
- vet-fix-agent doesn't show escalation format in return protocol
- Inconsistent with vet-requirement.md which specifies grep UNFIXABLE mechanical detection

### Duplication Analysis

**Significant duplication between vet skill and agents:**

**vet SKILL.md (375 lines) vs vet-agent (372 lines):**
- 250+ lines verbatim (Sections 0-4: Determine Scope, Gather Changes, Analyze Changes, Provide Feedback)
- Review criteria sections identical
- Example execution identical

**vet-agent (372 lines) vs vet-fix-agent (430 lines):**
- Sections 0-4 almost entirely duplicated (250+ lines)
- Only differences: Tools field (no Edit in vet-agent), additional sections in vet-fix-agent (Apply Fixes, Verification)
- Both could reference a shared base template

**Recommendation:**
- Extract common protocol sections to a shared file (e.g., `agent-core/fragments/vet-protocol.md`)
- Both agents and skill could reference it
- Reduces maintenance burden, improves consistency

### Missing Integration Points

**1. From learnings.md (Feb 12 session):**
- "Expansion re-introduces outline-level defects" — outline checks exist but expansion doesn't re-validate
- "vet-fix-agent context-blind validation" — vet-fix-agent doesn't receive execution context automatically
- "Vet agents over-escalate alignment issues" — pattern-matching tasks labeled as design escalations

**2. From session.md pending tasks:**
- "Integrate LLM failure mode checks into tdd-plan-reviewer" — Currently tdd-plan-reviewer only checks prescriptive code and RED/GREEN
- "Update design skill" — Two refinements mentioned but not reflected in current files

**3. Skill Interdependencies Not Documented:**
- No clear documentation of when to use plan-adhoc vs plan-tdd
- No guidance on model selection for different phases
- No mention of how /orchestrate integrates with runbook artifacts

---

## Issue Catalog

### Critical Issues

**Issue 1: Missing Reference Files in plan-tdd**
- Location: plan-tdd SKILL.md, lines 855, 974, 982
- References: `references/patterns.md`, `references/anti-patterns.md`, `references/error-handling.md`, `references/examples.md`
- Status: Files not found in project
- Impact: Incomplete documentation, references broken if agent follows them
- Recommendation: Either create the referenced files or remove references

**Issue 2: Execution Context Requirements Mismatch**
- Location: plan-adhoc Point 1 (line 351) vs vet-fix-agent validation (lines 52-85)
- Problem: plan-adhoc doesn't mention including execution context in vet delegations; vet-fix-agent requires it
- Impact: Vet reviews may confabulate issues if context missing
- Recommendation: Update plan-adhoc to include execution context in all vet-fix-agent delegations

**Issue 3: LLM Failure Mode Detection Not Cascaded**
- Location: plan-tdd Phase 3 expansion (lines 354-410)
- Problem: Outline review catches vacuity/density/checkpoint issues, but expanded phases don't re-validate
- Impact: Issues fixed at outline level re-introduced during expansion
- Recommendation: Add explicit re-validation step in Phase 5 holistic review

### Major Issues

**Issue 4: Duplication Between Agents**
- Location: vet-agent, vet-fix-agent, and vet skill (sections 0-4)
- Duplication: 250+ lines verbatim
- Impact: Maintenance burden, inconsistency risk
- Recommendation: Extract to shared `vet-protocol.md` fragment

**Issue 5: tdd-plan-reviewer Too Brief**
- Location: tdd-plan-reviewer.md (181 lines)
- Problem: Agent delegates all review criteria to skill but doesn't inline key checks
- Impact: Less context available at review time, harder to debug issues
- Recommendation: Inline key criteria sections from review-tdd-plan skill

**Issue 6: Background Review Pattern Undefined**
- Location: plan-tdd Phase 3 (line 378)
- Problem: Mentions "background review pattern" but doesn't specify `run_in_background=true` in Task call
- Impact: Unclear how to implement concurrent review
- Recommendation: Add explicit Task tool call format with `run_in_background=true`

**Issue 7: Escalation Format Inconsistency**
- Location: tdd-plan-reviewer (lines 170-172) shows format; vet-fix-agent (lines 338-353) doesn't
- Problem: No consistent format for UNFIXABLE issues across agents
- Impact: Orchestrator can't reliably detect escalations
- Recommendation: Add escalation format to all agents that support UNFIXABLE

### Minor Issues

**Issue 8: Expansion Guidance Consumption Not Explicit**
- Location: plan-tdd Phase 1.5 appends guidance; Phase 3 should read it
- Problem: Phase 3 references "Read Expansion Guidance" (line 345) but instruction comes after outline review, not before expansion
- Recommendation: Reorder Phase 1.5 step 1 to emphasize reading guidance BEFORE generating phases

**Issue 9: No Plan-Adhoc/Plan-TDD Selection Guidance**
- Location: Both skills user-invocable but no guidance on choosing between them
- Problem: Users might pick wrong skill, wrong tier assessment
- Recommendation: Add skill selection section to both (design determines path; if TDD in design → plan-tdd, else → plan-adhoc)

**Issue 10: Skill References Missing**
- Location: vet SKILL.md and plan-adhoc Point 1 reference agents by name without saying which agent to delegate to
- Problem: Implied assumptions about agent availability
- Recommendation: Explicit agent names in delegation examples

---

## Skills/Agents Directory Listing

**agent-core/skills/ (18 SKILL.md files):**
- commit
- design
- gitmoji
- handoff-haiku
- handoff
- next
- opus-design-question
- orchestrate
- plan-adhoc ✓ (analyzed)
- plugin-dev-validation
- plan-tdd ✓ (analyzed)
- reflect
- release-prep
- remember
- review-tdd-plan (referenced by tdd-plan-reviewer but not analyzed in detail)
- shelve
- token-efficient-bash
- vet ✓ (analyzed)
- worktree

**agent-core/agents/ (14 agents):**
- design-vet-agent
- memory-refactor
- outline-review-agent
- quiet-explore
- quiet-task
- refactor
- remember-task
- review-tdd-process
- runbook-outline-review-agent ✓ (analyzed)
- tdd-plan-reviewer ✓ (analyzed)
- tdd-task
- test-hooks
- vet-agent ✓ (reference)
- vet-fix-agent ✓ (analyzed)

**.claude/plugins/ (no files found)**
- plugin-dev:skill-development → Not found
- plugin-dev:agent-development → Not found
- Noted: plugin-dev-validation skill exists but not in plugins directory

---

## Recommendations for Workflow Fixes

### Priority 1: Resolve Missing References

1. Create or remove references to `references/*.md` files in plan-tdd skill
2. Verify all agent-to-skill delegation paths are correctly referenced

### Priority 2: Fix Context Mismatches

1. Update plan-adhoc Point 1 to include execution context in vet-fix-agent delegation (copy template from vet-requirement.md)
2. Update plan-tdd Phase 3 to explicitly include execution context
3. Add section to vet SKILL.md about execution context requirements

### Priority 3: Consolidate Duplication

1. Extract vet protocol sections to `agent-core/fragments/vet-protocol.md`
2. Update vet skill and vet-agent to reference shared protocol
3. Update vet-fix-agent to note extensions (Fix process, Verification)

### Priority 4: Clarify LLM Failure Modes

1. Add explicit "LLM Failure Mode Validation" step to plan-tdd Phase 5 holistic review
2. Reference runbook-outline-review-agent criteria in Phase 3 as re-validation pattern
3. Add to tdd-plan-reviewer skill loading to emphasize vacuity/density checks

### Priority 5: Fix Background Review Pattern

1. Specify Task tool call format with `run_in_background=true` in plan-tdd Phase 3
2. Update tdd-plan-reviewer to document concurrent execution expectations
3. Add post-phase result collection step

---

## Conclusion

The target artifacts form a coherent workflow system with clear roles:
- **Skills** provide reference implementation patterns and detailed guidance
- **Agents** provide executable implementations with built-in validation and fix capabilities
- **Delegation** follows consistent patterns (plan-skill → outline-review → phase-expansion → agent-review → fix → handoff)

Primary issues are:
1. Missing reference files (plan-tdd)
2. Execution context not uniformly required (plan-adhoc/plan-tdd vs vet-fix-agent)
3. Duplication between agents (vet-agent, vet-fix-agent, vet skill)
4. LLM failure modes detected at outline level but not re-validated after expansion

These are fixable with targeted updates to skill guidance and agent specifications.
