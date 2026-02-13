# Workflow Pipeline Unification: Design

## Problem

Two parallel planning skills (/plan-tdd, /plan-adhoc) share 75% structure but force a binary choice. Real work is mixed — behavioral code needs TDD, infrastructure doesn't. The bifurcation causes duplicate maintenance, inconsistent review gates, and 6 of 7 identified architectural gaps (G1-G7).

## Requirements

**Source:** `plans/workflow-fixes/outline.md` (implicit requirements extracted from problem analysis)

**Functional:**
- FR-1: Support mixed TDD + general phases in one runbook — per-phase type tagging
- FR-2: Eliminate duplicate maintenance — single /plan skill, ~1200 lines vs 2205
- FR-3: Unify review gates — single plan-reviewer agent, unified criteria
- FR-4: Resolve G1-G7 gaps — dissolved by unified architecture (G6 requires explicit fix)
- FR-5: Centralize pipeline contracts — `agents/decisions/pipeline-contracts.md`
- FR-6: Unified orchestrate completion — vet-fix-agent for both types

**Non-functional:**
- NFR-1: Preserve specialized TDD cycle guidance and general script evaluation
- NFR-2: No changes to prepare-runbook.py (already handles both types)
- NFR-3: Orchestrate compatibility maintained

**Out of scope:**
- prepare-runbook.py modifications
- Skills prolog restructuring
- Plugin-dev upstream
- Vet agent deduplication
- In-flight plan migration (prepare-runbook.py detection handles backward compat)

## Architecture: Unified /plan with Per-Phase Typing

### Per-Phase Type Model

Each phase in a runbook is tagged `type: tdd` or `type: general` (default: general).

**Type determines:**
- Expansion content format (TDD cycles with RED/GREEN vs general steps with script evaluation)
- Review criteria applied (TDD discipline for TDD phases, step quality for general phases)
- LLM failure mode checks apply universally (vacuity, ordering, density, checkpoints)

**Type does NOT affect:**
- Tier assessment (shared)
- Outline generation and review (shared)
- Consolidation gates (shared)
- Assembly and prepare-runbook.py (auto-detects from headers)
- Orchestrate execution (phase boundary detection already type-agnostic)
- Checkpoints (shared)

### Unified /plan Skill Structure

Target: ~1200 lines. Source: plan-tdd (1052 lines) + plan-adhoc (1153 lines).

**Section map (with source mapping):**

| Section | Source | Lines (approx) | Branching |
|---------|--------|-----------------|-----------|
| Frontmatter | Both | 15 | None |
| When to Use | Both | 20 | None |
| Tier Assessment | Both (identical) | 80 | None |
| Phase 0.5: Codebase Discovery | adhoc 138-170 | 35 | None |
| Phase 0.75: Outline Generation | Both (identical) | 50 | None |
| Phase 0.85: Consolidation Gate (outline) | Both (identical) | 45 | None |
| Phase 0.9: Complexity Check | Both (identical) | 45 | None |
| Phase 0.95: Outline Sufficiency | adhoc 312-335 | 25 | None (NEW for TDD: <3 phases AND <10 cycles) |
| Phase 1: Expansion | Both | 200 | **Per-phase-type** |
| — TDD: Cycle Planning | tdd 412-583 | 170 | TDD phases only |
| — General: Script Evaluation | adhoc 380-451 | 70 | General phases only |
| — Shared: Domain Validation | Both | 15 | None |
| Phase 1.4: File Size | Both (identical) | 20 | None |
| Phase 2: Assembly + Metadata | Both (identical) | 80 | None |
| Phase 2.5: Consolidation Gate (runbook) | Both (identical) | 60 | None |
| Phase 3: Final Review | Both | 60 | **Delegation target** |
| Phase 4: Artifacts + Handoff | Both (identical) | 40 | None |
| Checkpoints | Both (identical) | 85 | None |
| Constraints + Pitfalls | Both (shared) | 40 | None |
| References | Both | 10 | None |

**Total estimated: ~1165 lines** (47% reduction from 2205)

### Conditional Logic Points

Only two sections require per-phase-type branching:

**1. Phase 1 Expansion (largest divergence)**

Structure within Phase 1:

```markdown
### Phase 1: Phase-by-Phase Expansion

For each phase in the outline:

1. Check phase type tag (from outline: `type: tdd` or `type: general`)
2. Generate phase content using appropriate format:

**[TDD phases] — Cycle Planning Guidance:**
[Content from plan-tdd 3.1-3.6: numbering, RED specs, GREEN hints,
 investigation prereqs, stop conditions, dependencies]

**[General phases] — Script Evaluation:**
[Content from plan-adhoc 1.1-1.3: size classification, step types,
 conformance validation]

3. Review phase content:
   - Delegate to **plan-reviewer** (fix-all mode)
   - Agent applies type-aware criteria (TDD discipline for TDD phases,
     step quality for general phases, LLM failure modes for ALL phases)
```

**2. Phase 3 Final Review (delegation target differs)**

```markdown
### Phase 3: Final Holistic Review

Delegate to **plan-reviewer** (fix-all mode) for cross-phase consistency.

Review scope includes:
- Cross-phase dependency ordering
- Step/cycle numbering consistency
- Metadata accuracy
- File path validation
- Requirements satisfaction
- [TDD phases]: Cross-phase RED/GREEN sequencing, prescriptive code
- [General phases]: Step clarity, script evaluation completeness
- [All phases]: LLM failure modes (vacuity, ordering, density, checkpoints)
```

### Phase Type Tagging Format

In runbook outlines, phases declare their type:

```markdown
### Phase 1: Core behavior (type: tdd)
- Cycle 1.1: Load configuration
- Cycle 1.2: Parse entries
- Cycle 1.3: Validate schema

### Phase 2: Skill definition updates (type: general)
- Step 2.1: Update SKILL.md frontmatter
- Step 2.2: Add new section
- Step 2.3: Update references
```

prepare-runbook.py already distinguishes via header detection (`## Cycle X.Y:` vs `## Step N.M:`). The type tag is consumed by the planner and reviewer — not by prepare-runbook.py.

## Artifact Changes

### New: `agent-core/skills/plan/SKILL.md`

**Unified planning skill.** Merge shared sections from plan-tdd and plan-adhoc. Two conditional sections for per-phase-type content.

**Frontmatter:**
```yaml
---
name: plan
description: |
  Create execution runbooks with per-phase typing (TDD cycles or general steps).
  Supports mixed runbooks: behavioral phases use TDD discipline, infrastructure
  phases use general steps. Routes based on design context and phase requirements.
model: sonnet
allowed-tools: Task, Read, Write, Edit, Skill, Bash(mkdir:*, agent-core/bin/prepare-runbook.py, echo:*|pbcopy)
requires:
  - Design document from /design
  - CLAUDE.md for project conventions (if exists)
outputs:
  - Execution runbook at plans/<job-name>/runbook.md
  - Ready for prepare-runbook.py processing
user-invocable: true
---
```

**Content construction approach:**
- Start from plan-adhoc (more generic structure, Points 0.5-4)
- Replace Point numbering with Phase numbering (consistent with plan-tdd)
- Insert TDD cycle planning guidance from plan-tdd Phase 3.1-3.6 as conditional section
- Insert outline sufficiency check (from adhoc Point 0.95) with TDD threshold (<3 phases AND <10 cycles)
- Replace all review delegations with plan-reviewer
- Remove mode-specific language ("TDD runbook" / "general runbook" → "runbook")
- Add per-phase type model explanation at top
- Migrate `plan-tdd/references/` directory to `plan/references/` (patterns.md, anti-patterns.md, error-handling.md, examples.md — TDD cycle planning guidance references these)

**Key differences from either source:**
- Phase 1 expansion reads phase type tag, applies appropriate format
- Review delegations go to plan-reviewer (not tdd-plan-reviewer or vet-fix-agent)
- Outline sufficiency applies to both types
- No "When to Use" section that distinguishes from the other skill — this IS the planning skill

### New: `agent-core/agents/plan-reviewer.md`

**Replaces tdd-plan-reviewer.** Loads review-plan skill. Accepts both TDD and general artifacts.

**Agent definition:**
```yaml
---
name: plan-reviewer
description: |
  Reviews runbook phase files for quality, TDD discipline (if TDD), step quality (if general),
  and LLM failure modes (always).

  **Behavior:** Write review (audit trail) → Fix all issues → Escalate unfixable.

  Triggering examples:
  - "Review runbook-phase-1.md for quality"
  - "Check TDD runbook for prescriptive code and LLM failure modes"
  - "Validate general runbook steps for clarity and completeness"
  - /plan Phase 1 and Phase 3 delegate to this agent
model: sonnet
color: yellow
tools: ["Read", "Grep", "Glob", "Write", "Edit", "Skill"]
skills:
  - review-plan
---
```

**System prompt content (body of .md file):**

Adapt from tdd-plan-reviewer.md with these changes:

- **Document Validation:** Accept both TDD and general artifacts
  - TDD: `type: tdd` frontmatter or `## Cycle` headers
  - General: `## Step` headers or no type marker
  - Mixed: both header types across phases — valid
  - Remove: "If given wrong document type" error for general runbooks (they're now valid input)

- **Review Criteria:** "Load and follow the review-plan skill (preloaded via skills field). Key focus areas:" then list type-aware criteria:
  - TDD phases: prescriptive code detection, RED/GREEN validation, prose quality
  - General phases: step clarity, script evaluation, prerequisite validation
  - All phases: LLM failure modes (vacuity, ordering, density, checkpoints), file reference validation, metadata accuracy

- **Fix-All Policy:** Unchanged (fix all issues, escalate UNFIXABLE)
- **Report Structure:** Unchanged
- **Return Protocol:** Unchanged

### New: `agents/decisions/pipeline-contracts.md`

**Centralized I/O contracts for the design-to-deliverable pipeline.**

Content: Transformation table from outline (T1-T6) expanded with:

| # | Transformation | Input | Output | Defect Types | Review Gate | Review Criteria |
|---|---------------|-------|--------|-------------|-------------|----------------|
| T1 | Requirements → Design | requirements.md or inline | design.md | Incomplete, infeasible | design-vet-agent (opus) | Architecture, feasibility, completeness |
| T2 | Design → Outline | design.md | runbook-outline.md | Missing reqs, wrong decomposition | runbook-outline-review-agent | Requirements coverage, phase structure, LLM failure modes |
| T3 | Outline → Phase files | runbook-outline.md | runbook-phase-N.md | Vacuity, prescriptive code, density | **plan-reviewer** | Type-aware: TDD discipline + general quality + LLM failure modes |
| T4 | Phase files → Runbook | runbook-phase-*.md | runbook.md | Cross-phase inconsistency | **plan-reviewer** (holistic) | Cross-phase consistency, numbering, metadata |
| T5 | Runbook → Step artifacts | runbook.md | steps/step-*.md, agent | Generation errors | prepare-runbook.py | Automated validation |
| T6 | Steps → Implementation | step-*.md | Code/artifacts | Wrong behavior, stubs, drift | vet-fix-agent (checkpoints) | Scope IN/OUT, design alignment |

Plus:
- Scope IN/OUT template for review delegations (addresses G6)
- UNFIXABLE escalation protocol reference

### Modified: `agent-core/skills/review-tdd-plan/SKILL.md` → `agent-core/skills/review-plan/SKILL.md`

**Rename and expand.** Add general-phase criteria and LLM failure modes.

**Changes:**

1. **Rename** directory: `review-tdd-plan/` → `review-plan/`

2. **Frontmatter update:**
   - `name: review-plan`
   - Description: expand to cover both TDD and general artifacts, plus LLM failure modes

3. **Add section: General Phase Criteria** (after existing TDD criteria)

   New section between current section 9 (File Reference Validation) and Review Process:

   ```markdown
   ### 10. General Phase Step Quality

   **Applies to:** Phases with `## Step` headers (general type)

   **10.1 Prerequisite Validation**
   - Creation steps (new code touching existing paths) MUST have investigation prerequisites
   - Format: `**Prerequisite:** Read [file:lines] — understand [behavior/flow]`
   - Transformation steps (delete, move, rename) are exempt

   **10.2 Script Evaluation**
   - Steps classify size: small (≤25 lines inline), medium (25-100 prose), large (>100 separate planning)
   - Verify classification matches actual step complexity
   - Flag steps claiming "small" with >25 lines of inline content

   **10.3 Step Clarity**
   - Each step has: Objective, Implementation, Expected Outcome
   - No "determine"/"evaluate options"/"choose between" language (decisions resolved at planning)
   - Error conditions and validation criteria specified

   **10.4 Conformance Validation**
   - When design references external spec: validation steps verify conformance
   - Exact expected strings from reference, not abstracted descriptions
   ```

4. **Add section: LLM Failure Modes** (applies to ALL phase types)

   New section after General Phase Criteria:

   ```markdown
   ### 11. LLM Failure Modes (ALL phases)

   These checks apply regardless of phase type (TDD or general).
   Criteria from agents/decisions/runbook-review.md (four axes).

   **11.1 Vacuity**
   - TDD: Cycles where RED can pass with `assert callable(X)` or `import X`
   - General: Steps that only create scaffolding without functional outcome
   - Integration wiring steps where called function already tested
   - Fix: Merge into nearest behavioral cycle/step

   **11.2 Dependency Ordering**
   - Foundation-first within phases: existence → structure → behavior → refinement
   - Step N tests behavior depending on structure from step N+k (k>0)
   - Fix: Reorder within phase. If cross-phase: UNFIXABLE (outline revision needed)

   **11.3 Density**
   - Adjacent steps/cycles testing same function with <1 branch point difference
   - Single edge cases expressible as parametrized row in prior step
   - Entire phases with ≤3 items, all Low complexity
   - Fix: Merge adjacent, parametrize edge cases, collapse trivial phases

   **11.4 Checkpoint Spacing**
   - Gaps >10 steps/cycles or >2 phases without checkpoint
   - Complex data manipulation phases without checkpoint
   - Fix: Insert checkpoint recommendation
   ```

5. **Update Review Process phases** to cover both types:
   - Phase 1 (Scan): Add general step quality checks
   - Phase 3 (Analyze): Add general step analysis alongside cycle analysis
   - Phase 4 (Fix): Unchanged (fix-all applies to all issue types)
   - Phase 5 (Report): Template unchanged (works for both)

6. **Update references** from "TDD runbook" to "runbook" where generic

### Modified: `agent-core/skills/orchestrate/SKILL.md`

**Changes:**

1. **Prerequisites and routing** (lines 14, 25): Change "prepared with `/plan-adhoc` skill" and "use `/plan-adhoc` first" → "prepared with `/plan` skill" and "use `/plan` first"

2. **Section 6: Completion** (lines 248-271): Unify completion behavior

   Replace the TDD/general split with:

   ```markdown
   ### 6. Completion

   **When all steps successful:**

   1. Delegate to vet-fix-agent for quality review
      - Write report to `plans/<name>/reports/vet-review.md`
   2. If runbook frontmatter has `type: tdd`:
      - Delegate to review-tdd-process for process analysis
      - Write report to `plans/<name>/reports/tdd-process-review.md`
   3. Report overall success with report links
   4. Default-exit: `/handoff --commit` → `/commit`
   ```

   Key change: general completion now DOES the vet-fix-agent review (was only "suggest"). This resolves G7.

3. **Integration with Workflows** (lines 405-426): Update references from `/plan-adhoc` and `/plan-tdd` to `/plan`

4. **Weak Orchestrator Pattern** (line 285): Update "All decisions made during planning (/plan-adhoc)" → "All decisions made during planning (/plan)"

### Modified: `agent-core/skills/design/SKILL.md`

**Changes:**

1. **Mode Detection section** (lines 12-16): Remove TDD/General mode split

   Replace:
   ```markdown
   **TDD Mode:** Test-first culture, user mentions TDD/tests...
   **General Mode:** Infrastructure, refactoring...
   Mode determines downstream consumer: TDD → `/plan-tdd`, General → `/plan-adhoc`.
   ```

   With:
   ```markdown
   Downstream consumer: `/plan` (unified — handles both TDD and general phases).
   Design should note which phases are behavioral (TDD) vs infrastructure (general)
   to guide per-phase type tagging during planning.
   ```

2. **Moderate routing** (line 30): Change `/plan-adhoc` (or `/plan-tdd`) → `/plan`

3. **Documentation Perimeter template** (C.1): Add `agents/decisions/pipeline-contracts.md` for tasks producing runbooks

4. **Skill-loading directives**: Remove TDD-specific routing. Planning always goes to `/plan`.

5. **C.5 tail-call**: No change (already generic)

### Modified: `agent-core/fragments/workflows-terminology.md`

**Replace dual workflow description with unified:**

```markdown
## Workflow Selection

**Entry point:**
- **Questions/research/discussion** → Handle directly (no workflow needed)
- **Implementation tasks** → Use `/design` skill (triages complexity, routes to appropriate workflow)
- **Workflow in progress** (check session.md) → Continue from current state

The `/design` skill includes complexity triage: simple tasks execute directly, moderate tasks skip design and route to planning, complex tasks get full design treatment.

**Implementation workflow** — unified planning for all implementation work:
- **Route:** `/design` → `/plan` → [plan-reviewer] → prepare-runbook.py (auto) → tail: `/handoff --commit` → tail: `/commit` → restart → `/orchestrate` → [vet agent]
- **Per-phase typing:** Each phase tagged TDD or general. TDD phases get RED/GREEN cycles, general phases get task steps. Mixed runbooks supported.
- **Review:** plan-reviewer agent checks TDD discipline, step quality, and LLM failure modes (type-aware per phase)
- **Post-planning:** Automated via tail-call chain: prepare-runbook.py runs, orchestrate command copied to clipboard, then `/handoff --commit` → `/commit` → displays next pending task
- **Tier assessment:** Plan skill includes tier assessment — small tasks (Tier 1/2) bypass runbook creation
- **TDD process review:** After orchestration of TDD runbooks, review-tdd-process analyzes execution quality
```

Remove separate TDD workflow and General workflow sections.

Update Terminology table: add **Phase type** — `tdd` or `general`, determines expansion format and review criteria for that phase.

### Modified: `agent-core/agents/tdd-plan-reviewer.md` → DELETE

Replaced by `agent-core/agents/plan-reviewer.md`. Delete the old file.

### Modified: `agent-core/skills/vet/SKILL.md`

Add execution context guidance section referencing `vet-requirement.md`:

```markdown
## Execution Context for Review Delegations

When delegating to vet-fix-agent, include scope context per vet-requirement.md:

**Required:** Scope IN, Scope OUT, Changed files, Requirements summary
**Optional:** Prior state, Design reference

See `agent-core/fragments/vet-requirement.md` for full template and rationale.
```

### Deprecated: DELETE after validation

- `agent-core/skills/plan-tdd/SKILL.md` (and directory)
- `agent-core/skills/plan-adhoc/SKILL.md` (and directory)
- `agent-core/agents/tdd-plan-reviewer.md`

### Unchanged

- `agent-core/bin/prepare-runbook.py` — already handles both types via header detection
- `agent-core/agents/vet-fix-agent.md` — no changes
- `agent-core/agents/vet-agent.md` — no changes
- `agent-core/agents/runbook-outline-review-agent.md` — already handles both types (description references updated)
- `agent-core/agents/review-tdd-process.md` — still used for TDD orchestration completion

### Reference Updates

All references to `/plan-tdd`, `/plan-adhoc`, or `tdd-plan-reviewer` must be updated:

| File | Change |
|------|--------|
| `CLAUDE.md` | @-reference to workflows-terminology.md (auto-updated) |
| `agent-core/fragments/workflows-terminology.md` | Rewritten (see above) |
| `agent-core/fragments/execute-rule.md` | Task metadata example uses `/plan-adhoc` |
| `agent-core/fragments/continuation-passing.md` | Examples and continuation table reference both skills |
| `agent-core/skills/design/SKILL.md` | Mode detection, routing |
| `agent-core/skills/orchestrate/SKILL.md` | Prerequisites, completion, workflow refs |
| `agent-core/skills/vet/SKILL.md` | Workflow reference to `/plan-adhoc` |
| `agent-core/agents/runbook-outline-review-agent.md` | Description mentions plan-adhoc/plan-tdd (line 4, line 60, line 144) |
| `agent-core/agents/review-tdd-process.md` | Workflow reference to `/plan-tdd` |
| `agent-core/skills/review-plan/SKILL.md` | Internal references to /plan-tdd |
| `agent-core/skills/handoff-haiku/SKILL.md` | Task example uses `/plan-adhoc` |
| `agent-core/docs/tdd-workflow.md` | Multiple references to `/plan-tdd` throughout |
| `agent-core/docs/general-workflow.md` | Multiple references to `/plan-adhoc` throughout |
| `agent-core/README.md` | Directory listing references plan-adhoc/ and plan-tdd/ |
| `agent-core/bin/prepare-runbook.py` | Baseline detection references (if any agent name refs) |
| Symlinks in `.claude/` | `just sync-to-parent` after skill/agent directory changes |

## Design Decisions

### DD-1: Per-phase type granularity (not runbook or step level)
Per-runbook forces binary choice. Per-step is over-granular. Per-phase matches natural work grouping. Prepare-runbook.py detects per-file anyway.

### DD-2: Clean rename, no aliases (v0.0)
tdd-plan-reviewer → plan-reviewer (delete old, create new). review-tdd-plan → review-plan (rename directory). No backward compatibility aliases. Reference churn is mechanical and bounded.

### DD-3: Fix-all pattern eliminates recommendation propagation
Reviewers fix directly or escalate UNFIXABLE. No "Recommendations" dead-ends. Expansion Guidance (inline in outline) remains for outline → expansion transmission.

### DD-4: Centralized pipeline contracts
`agents/decisions/pipeline-contracts.md` as single source. Skills reference with brief I/O section. Transformation table is the authoritative spec.

### DD-5: LLM failure mode criteria in review-plan skill
Four axes (vacuity, ordering, density, checkpoints) coupled with review — no separate skill. Applied to all phase types. TDD-specific checks (prescriptive code, RED/GREEN) conditional. runbook-outline-review-agent keeps its own copy (different application stage, acceptable duplication).

### DD-6: Outline sufficiency for TDD
Threshold: <3 phases AND <10 cycles. Skip expansion when outline is execution-ready. Reduces overhead for small TDD work.

### DD-7: Orchestrate completion unified
Both TDD and general paths delegate to vet-fix-agent. TDD additionally runs review-tdd-process. General no longer merely "suggests" — it does the review. Resolves G7.

## Implementation Notes

**Execution model:** Opus for skill/agent definition edits (architectural artifacts). Sonnet for reference updates and mechanical changes.

**Build order:**
1. Create pipeline-contracts.md (no dependencies)
2. Create review-plan skill (rename + extend review-tdd-plan)
3. Create plan-reviewer agent (depends on review-plan skill)
4. Create unified /plan skill (depends on plan-reviewer agent existing for references)
5. Update design skill routing
6. Update orchestrate completion
7. Update workflows-terminology
8. Update reference strings across remaining files
9. Run `just sync-to-parent` for symlink sync
10. Delete deprecated artifacts (plan-tdd, plan-adhoc, tdd-plan-reviewer)
11. Validate: `just precommit`

**Testing strategy:** No automated tests (skill/agent definitions are prose artifacts). Validation via:
- `just precommit` passes (line limits, formatting)
- `just sync-to-parent` succeeds (symlinks correct)
- Manual review of unified skill against both source skills

**Risk: Regression in planning quality.** Mitigation: Both source skills remain in git history. If unified skill produces worse runbooks, diff against originals.

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `plans/workflow-fixes/outline.md` — approach, decisions, scope
- `plans/workflow-fixes/reports/explore-plan-unification.md` — structural overlap data
- `agents/decisions/runbook-review.md` — LLM failure mode criteria (four axes)
- `agent-core/fragments/vet-requirement.md` — execution context template

**Source skills (reference for content):**
- `agent-core/skills/plan-tdd/SKILL.md` — TDD-specific content to preserve
- `agent-core/skills/plan-adhoc/SKILL.md` — general-specific content to preserve
- `agent-core/skills/review-tdd-plan/SKILL.md` — review criteria to extend
- `agent-core/skills/orchestrate/SKILL.md` — completion behavior to modify
- `agent-core/skills/design/SKILL.md` — routing to update

**Agent definitions:**
- `agent-core/agents/tdd-plan-reviewer.md` — agent to replace
- `agent-core/agents/runbook-outline-review-agent.md` — unchanged but verify references

**Plugin-dev skills:** Load `plugin-dev:skill-development` and `plugin-dev:agent-development` before creating skill/agent definitions.

## Next Steps

1. `/plan-adhoc plans/workflow-fixes/design.md` — create execution runbook (last adhoc invocation before unification)
2. Execute with opus for architectural artifacts (skill/agent definitions)
3. After execution: `just sync-to-parent`, `just precommit`, manual validation
