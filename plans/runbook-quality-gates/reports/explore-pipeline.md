# Runbook Pipeline Exploration

**Date:** 2026-02-16
**Purpose:** Understand current pipeline structure, review flow, and validation mechanisms for runbook quality gates project

---

## Summary

The implementation pipeline chains `/design` → `/runbook` skill → plan-reviewer agent → prepare-runbook.py → `/orchestrate`, with multi-phase runbook generation (phases 0.5-4). Quality gates occur at three levels: per-phase review (Phase 1), consolidation gates (phases 0.85, 2.5), and holistic review (Phase 3). The prepare-runbook.py script validates structure, numbering, cycle/step definitions, and file references before artifact generation.

---

## 1. Runbook Skill (`/runbook`)

**Location:** `/Users/david/code/claudeutils-wt/runbook-skill-fixes/agent-core/skills/runbook/SKILL.md`

### Phase Sequence

The skill defines a hierarchical planning process (Tier 3 full runbooks):

| Phase | Purpose | Gating | Output |
|-------|---------|--------|--------|
| **0.5** | Discover codebase structure, read documentation, verify file locations | REQUIRED | Preparation for outline |
| **0.75** | Generate runbook outline (requirements mapping, phase structure, type tags) | Per-outline review | `runbook-outline.md` |
| **0.85** | Consolidation Gate — Outline (merge trivial phases before expansion) | Judgment gate | Updated outline |
| **0.9** | Complexity Check (detect oversized outlines, callback mechanism) | Mechanical gate | Proceed/callback decision |
| **0.95** | Outline Sufficiency Check (skip expansion if outline detailed enough) | Mechanical gate | Fast-path to Phase 4 OR Phase 1 |
| **Phase 1** | Phase-by-phase expansion with per-phase review | Per-phase review | `runbook-phase-N.md` files |
| **Phase 2** | Assembly and metadata validation (pre-prepare-runbook checks) | No gate | Assembled `runbook.md` |
| **2.5** | Consolidation Gate — Runbook (merge isolated trivial items after assembly) | Judgment gate | Updated runbook |
| **Phase 3** | Final holistic review (cross-phase consistency) | Holistic review | `runbook.md` ready |
| **Phase 4** | Prepare artifacts (run prepare-runbook.py, copy command, `/handoff --commit`) | Script validation | Execution artifacts, handoff |

### Model Assignments per Phase

**Runbook skill model:** Sonnet (orchestrator/coordinator)

**Per-phase execution models** (in runbook metadata):
- **Haiku:** File operations, scripted tasks, mechanical edits
- **Sonnet:** Semantic analysis, judgment, standard implementation
- **Opus:** Architecture decisions, complex design reasoning, **artifact-type override** (skills, fragments, agents, workflow decisions regardless of task complexity)

**Artifact-type override rule:** Steps editing architectural artifacts require **opus** regardless of task complexity, because these artifacts are prose instructions consumed by LLMs — wording directly determines downstream agent behavior.

### Phase 1: Per-Phase Expansion

**For each phase (e.g., Phase 1, Phase 2):**

1. **Check phase type tag** from outline phase heading: `### Phase N: Title (type: tdd)` or `(type: general)` (default: general)

2. **Expand based on phase type:**
   - **TDD phases:** Generate `runbook-phase-N.md` with RED/GREEN cycles using TDD Cycle Planning Guidance
   - **General phases:** Generate `runbook-phase-N.md` with step tasks, prerequisites, implementations

3. **Commit phase file before review** (review agents operate on filesystem state)

4. **Delegate to plan-reviewer** for type-aware review:
   - TDD phases: Validate RED/GREEN discipline, prescriptive code detection, test quality
   - General phases: Validate prerequisite completeness, step clarity, script evaluation classification
   - All phases: LLM failure modes (vacuity, ordering, density, checkpoints)

5. **Background review pattern:** Launch review with `run_in_background=true`, proceed to next phase

### TDD Cycle Planning Requirements

Within TDD phases, each cycle must include:

**RED Phase (prose test descriptions):**
- Test function name
- Specific assertions (behavioral, not structural) — "returns string containing emoji" not "returns correct value"
- Expected failure type/pattern
- Why it fails (missing implementation)
- Verify command

**GREEN Phase (behavior + hints, NO prescriptive code):**
- Brief description
- What the code must DO (not HOW)
- Approach hint (algorithm/strategy)
- Changes (file, action, location hint — describe, don't code)
- Verify GREEN and regression test commands

**Mandatory sections:**
- RED and GREEN (except spike cycles 0.x, regression cycles marked `[REGRESSION]`)
- Stop/Error Conditions (can be in cycle OR Common Context)
- Dependencies (optional, can be in cycle OR Common Context)

### Consolidation Gates

**Phase 0.85 (outline consolidation):**
- Merge trivial phases (≤2 items, Low complexity) with adjacent work
- Constraints: don't exceed 10 items after merge, maintain domain coherence

**Phase 2.5 (runbook consolidation):**
- Merge isolated trivial items (single-line changes, config-only)
- Merge same-file items with adjacent item
- Promote setup items to phase preamble, cleanup to postamble
- Update Total Steps count in metadata

### Checkpoints

**Light checkpoint** (Fix + Functional):
- Run `just dev`, fix, commit
- Review implementations: real behavior or stubs? Functional or constants?
- Place at every phase boundary

**Full checkpoint** (Fix + Vet + Functional):
- Run `just dev`, fix, commit
- Delegate to sonnet for review, apply all fixes, commit
- Same functional checks as light
- Place at final phase or phases marked `checkpoint: full`

**When to mark `checkpoint: full`:**
- Phase introduces new public API surface
- Phase crosses module boundaries (3+ packages)
- Runbook exceeds 20 items total

### Quality Criteria Summary

**Phase-aware review** (plan-reviewer handles):
- **TDD:** GREEN prescriptive code detection, RED prose quality (specific assertions)
- **General:** Prerequisite validation, script evaluation sizing, step clarity
- **All:** Vacuity (items that don't constrain implementation), dependency ordering, density (adjacent items with <1 branch difference), checkpoint spacing (gaps >10 items)

---

## 2. Plan-Reviewer Agent

**Location:** `/Users/david/code/claudeutils-wt/runbook-skill-fixes/agent-core/agents/plan-reviewer.md`

**Model:** Sonnet (balanced for most runbook review tasks)

### Role and Responsibilities

1. **Audit trail:** Document findings (even for fixed issues) for deviation monitoring
2. **Autofix:** Apply ALL fixes (critical, major, AND minor) using Edit tool
3. **Escalation:** Report UNFIXABLE issues requiring caller intervention

### Artifact Validation

**Accepts:**
- TDD runbooks (`type: tdd` or `## Cycle` headers)
- General runbooks (`## Step` headers or no type marker, default: general)
- Mixed runbooks (both header types across phases)

**Rejects:**
- Design documents → use design-vet-agent
- Code/implementation → use vet-agent

### Review Criteria

Load and follow the **review-plan skill** (preloaded via skills field). Key focus areas:

**TDD phases:**
- GREEN phases: Detect prescriptive code (behavior + hints, not exact code)
- RED phases: Validate prose test quality (specific assertions, not vague)
- RED/GREEN sequencing: Incremental cycle progression
- Consolidation quality: Merged cycles maintain test isolation

**General phases:**
- Prerequisite validation: Creation steps MUST have investigation prereqs
- Script evaluation: Size classification matches actual complexity
- Step clarity: Objective, Implementation, Expected Outcome present; no deferred decisions
- Conformance validation: Spec-based steps verify with exact expected strings

**All phases (LLM failure modes):**
- Vacuity: Items that don't constrain implementation (merge into behavioral items)
- Dependency ordering: Foundation-first within phases (reorder or UNFIXABLE if cross-phase)
- Density: Adjacent items with <1 branch difference (collapse)
- Checkpoint spacing: Gaps >10 items or >2 phases without checkpoint

**Prose quality rule:** If an executor could write different tests that all satisfy the prose, the prose is too vague.

### Outline Review Check

When reviewing a full runbook:
- Extract plan name from path (e.g., `plans/<plan-name>/runbook.md`)
- Check for outline review report: `plans/<plan-name>/reports/runbook-outline-review.md`
- Add warning if outline review missing

**Exception:** When reviewing phase files (`runbook-phase-N.md`), SKIP this check (phase files are intermediate, created after outline review).

### Report Structure

```markdown
# Runbook Review: [name]

**Artifact**: [path]
**Date**: [ISO timestamp]
**Mode**: review + fix-all
**Phase types**: [TDD | General | Mixed]

## Summary
[2-3 sentences]
**Overall Assessment**: [Ready / Needs Escalation]

## Findings

### Critical Issues
1. **[Issue]**
   - Location: [cycle/step, section]
   - Problem: [description]
   - Fix: [what was changed]
   - **Status**: FIXED | UNFIXABLE (reason)

### Major Issues
[same format]

### Minor Issues
[same format]

## Fixes Applied
- [location] — [change]

## Unfixable Issues (Escalation Required)
[List or "None"]

---

**Ready for next step**: [Yes / No]
```

### Return Protocol

**On success:** Return ONLY filepath
```
plans/<feature>/reports/runbook-review.md
```

**On success with unfixable issues:** Return filepath + escalation note
```
plans/<feature>/reports/runbook-review.md
ESCALATION: [count] unfixable issues require attention
```

---

## 3. Runbook Outline Review Agent

**Location:** `/Users/david/code/claudeutils-wt/runbook-skill-fixes/agent-core/agents/runbook-outline-review-agent.md`

**Model:** Opus (architectural complexity of outline evaluation)

### Purpose

Reviews `runbook-outline.md` after Phase 0.75 (outline generation), before full runbook expansion. Validates requirements coverage, phase structure, complexity distribution, design alignment.

### Validation Protocol

**Input validation:**
1. Verify requirements exist (design.md Requirements section, requirements.md, or task prompt)
2. Verify artifact is `runbook-outline.md` (not outline.md, not runbook.md)
3. Verify design.md exists at `plans/<job>/design.md`

### Review Criteria

1. **Requirements Coverage:** Every FR-* and NFR-* maps to phase/step
2. **Design Alignment:** Steps reference design decisions, architecture reflects design
3. **Phase Structure:** Balanced complexity, logical grouping, clean boundaries, logical progression
4. **Complexity Distribution:** No phase >40% of total, high-complexity phases well-decomposed
5. **Dependency Sanity:** No circular dependencies, prerequisites before dependents
6. **Vacuity:** Each step tests branch point or produces outcome; no scaffolding-only items
7. **Intra-Phase Ordering:** Foundation-first (existence → structure → behavior → refinement)
8. **Step/Cycle Density:** Flag adjacent items testing same function with <1 branch difference
9. **Checkpoint Spacing:** Flag gaps >10 items or >2 phases without checkpoint
10. **Growth Projection:** Estimate net new lines per file; flag when projected cumulative size exceeds 350 lines
11. **Semantic Propagation:** When design introduces new terminology, verify all producer and consumer files are in outline
12. **Deliverable-Level Traceability:** Cross-reference outline against design deliverables table (artifact × action pairs)
13. **Step Clarity:** Objective, title, scope, success criteria all present
14. **Execution Readiness:** No "choose/decide/determine" language, dependencies declared, code fix specificity, checkpoint frequency, post-phase state awareness, scope boundaries

### Expansion Guidance Section

After fixing, append `## Expansion Guidance` section to outline:

```markdown
## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- [Trivial phases to merge]
- [Setup cycles to inline]

**Cycle expansion:**
- [Test case suggestions]
- [Edge case reminders]

**Checkpoint guidance:**
- [Validation step suggestions]

**References to include:**
- [Shell line numbers]
- [Design sections to propagate]
```

### Report Structure

Similar to plan-reviewer: Critical/Major/Minor issues, Requirements Coverage table, Phase Structure Analysis, Phase Balance (steps/complexity/percentage), Complexity Distribution, Design Alignment, Positive Observations, Recommendations.

**Assessment Criteria:**
- **Ready:** All requirements traced, no critical/major issues, balanced phases, reasonable complexity, sane dependencies
- **Needs Iteration:** All issues fixed, outline needs elaboration, minor structural adjustments
- **Needs Rework:** Fundamental structure issues, major requirements gaps, phase structure doesn't support flow

---

## 4. prepare-runbook.py Script

**Location:** `/Users/david/code/claudeutils-wt/runbook-skill-fixes/agent-core/bin/prepare-runbook.py`

### Purpose

Transforms runbook markdown (or phase-grouped directory) into execution artifacts:
1. Plan-specific agent at `.claude/agents/<runbook-name>-task.md`
2. Step/Cycle files at `plans/<runbook-name>/steps/`
3. Orchestrator plan at `plans/<runbook-name>/orchestrator-plan.md`

### Input Modes

1. **Single file:** `prepare-runbook.py plans/foo/runbook.md`
2. **Phase directory:** `prepare-runbook.py plans/foo/` (detects `runbook-phase-*.md` files, assembles them)

### Validation Checks

**Phase file assembly (if directory input):**
- Detects `runbook-phase-*.md` files
- Validates sequential phase numbering (0-based or 1-based, no gaps)
- Injects default Common Context for TDD runbooks lacking one
- Auto-detects runbook type: cycles → TDD, steps → general, both → mixed

**Frontmatter parsing:**
- Extracts metadata: `type`, `model`, `name`
- Validates type field (tdd/general/mixed)
- Defaults: type='general', model='haiku'

**Cycle numbering validation** (TDD runbooks):
- **Fatal errors:** No cycles found, duplicate cycle numbers, minor doesn't start at 1
- **Warnings:** Gaps in major or minor numbering (gaps acceptable, document order is authoritative)

**Cycle structure validation** (TDD runbooks):
- **Spike cycles (0.x):** No RED/GREEN required
- **Regression cycles:** GREEN only, no RED expected
- **Standard cycles:** Both RED and GREEN required
- **All cycles:** Must include Stop/Error Conditions (in cycle OR Common Context)
- **Optional:** Dependencies section (in cycle OR Common Context)

**Phase numbering validation** (general runbooks):
- **Fatal errors:** Non-monotonic phases (decreasing order invalid)
- **Warnings:** Phase number gaps (acceptable)

**File reference validation:**
- Extracts backtick-wrapped file paths from step/cycle content
- Skips report paths (e.g., `plans/*/reports/*`)
- Skips creation-verb context ("Create|Write|mkdir")
- Checks existence for all other references
- **Warnings only:** Non-existent files (doesn't fail script)

**Step extraction validation:**
- Detects duplicate step numbers → error
- Extracts Common Context section once
- Extracts Orchestrator Instructions section
- Extracts all steps matching `## Step N.M:` pattern

### Artifact Generation

**Plan-specific agent:**
- Selects baseline: `tdd-task.md` (TDD) or `quiet-task.md` (general/mixed)
- Reads baseline body (without frontmatter)
- Generates frontmatter with runbook name, model, color=cyan
- Appends Common Context as "Runbook-Specific Context"
- Appends clean-tree requirement contract
- Writes to `.claude/agents/<runbook-name>-task.md`

**Step files:**
- Generates one file per step/cycle
- File naming: `step-{N}-{M}.md` or `step-{major}-{minor}.md` for cycles
- Includes header with:
  - Plan reference path
  - Execution Model (extracted from step metadata or default)
  - Phase number (from section context or cycle major number)
  - Report Path (if specified in step)
- Appends step body content

**Orchestrator plan:**
- Reads custom Orchestrator Instructions if present
- Otherwise generates default:
  - Executes steps sequentially
  - Marks phase boundaries with `— PHASE_BOUNDARY` comment
  - Suggests functional review checkpoint before next phase

### Common Context Injection (TDD)

When assembling phase files, if no Common Context section exists, injects:

```markdown
## Common Context

**TDD Protocol:**
Strict RED-GREEN-REFACTOR: ...

**Stop/Error Conditions (all cycles):**
STOP IMMEDIATELY if: RED passes (expected failure) • ...
```

This ensures every TDD runbook has mandatory protocol guidance.

### File Staging

After generating all artifacts:
- Runs `git add` for agent, steps directory, and orchestrator plan
- Reports git staging status
- Returns `[SUCCESS | FAILURE]` to caller

---

## 5. Implementation Pipeline Flow

**Full chain:**

```
User request
    ↓
/design skill
    ↓ (produces design.md)
    ↓
/runbook skill (Tier 3: full runbook)
    ├─ Phase 0.5: Discover codebase
    ├─ Phase 0.75: Generate outline → runbook-outline.md
    ├─ Phase 0.85: Consolidation gate (outline)
    ├─ Phase 0.9: Complexity check
    ├─ Phase 0.95: Sufficiency check (fast-path or proceed)
    ├─ Phase 1: Phase-by-phase expansion
    │   └─ For each phase:
    │       ├─ Generate runbook-phase-N.md
    │       ├─ Commit phase file
    │       └─ Delegate to plan-reviewer (background)
    ├─ Phase 2: Assembly validation
    ├─ Phase 2.5: Consolidation gate (runbook)
    ├─ Phase 3: Holistic review → delegate plan-reviewer
    └─ Phase 4: Prepare artifacts
        ├─ Run prepare-runbook.py
        ├─ Copy `/orchestrate {name}` to clipboard
        └─ Tail-call `/handoff --commit`
            ├─ Updates session.md
            └─ Tail-calls `/commit`
                ├─ Commits artifacts
                └─ Displays STATUS (orchestration pending)
    ↓
User restarts session
    ↓
/orchestrate {name}
    ├─ Loads plan-specific agent
    └─ Executes steps sequentially
```

---

## 6. Review Integration Points

### Per-Phase Review (Phase 1)

- **Trigger:** After each phase file committed
- **Agent:** plan-reviewer (sonnet)
- **Mode:** Background (`run_in_background=true`)
- **Input:** Committed phase file path
- **Output:** Report at `plans/<job>/reports/runbook-phase-N-review.md`
- **Criteria:** Type-aware (TDD vs general) + LLM failure modes
- **Fix scope:** ALL issues (critical, major, minor)

### Outline Review (Phase 0.75)

- **Trigger:** After outline created
- **Agent:** runbook-outline-review-agent (opus)
- **Mode:** Blocking (waits for completion)
- **Input:** `runbook-outline.md`
- **Output:** Report + Expansion Guidance appended to outline
- **Criteria:** Requirements coverage, phase structure, complexity distribution, design alignment
- **Fix scope:** ALL issues

### Holistic Review (Phase 3)

- **Trigger:** After assembly, before prepare-runbook.py
- **Agent:** plan-reviewer (sonnet)
- **Mode:** Blocking
- **Input:** Assembled `runbook.md`
- **Output:** Report at `plans/<job>/reports/runbook-review.md`
- **Criteria:** Cross-phase consistency, dependency ordering, metadata accuracy, file path validation, requirements satisfaction
- **Scope:** Checks consistency across phases only (individual phases already reviewed)

### Outline Review Check in Plan-Reviewer

When reviewing full runbook, plan-reviewer checks if outline review was performed:
- Expects report at `plans/<job>/reports/runbook-outline-review.md`
- Adds warning if missing
- SKIPPED when reviewing phase files (intermediate artifacts)

---

## 7. Model Assignment Rules

### Runbook Skill (orchestrator): Sonnet

### Per-Phase Execution Model (in runbook metadata)

**Default heuristic:**
- Haiku: File operations, scripted tasks, mechanical edits
- Sonnet: Semantic analysis, judgment, standard implementation
- Opus: Architecture, complex design decisions

**Artifact-type override** (applies regardless of task complexity):
- Skills (`agent-core/skills/`)
- Fragments (`agent-core/fragments/`)
- Agent definitions (`agent-core/agents/`)
- Workflow decisions (`agents/decisions/workflow-*.md`)

Override applies to:
- Tier 2 delegation (model parameter in Task call)
- Tier 3 step assignment (Execution Model field in runbook)
- Weak Orchestrator Metadata (Execution Model section)

**Rationale:** These artifacts are prose instructions consumed by LLMs. Wording directly determines downstream agent behavior. "Simple" edits require nuanced understanding that haiku/sonnet cannot reliably provide.

---

## 8. Current Validation Architecture

### Validation Layers

| Layer | Location | Trigger | Scope | Enforcer |
|-------|----------|---------|-------|----------|
| **Outline structure** | runbook-outline-review-agent | Phase 0.75 | Requirements coverage, phase structure, complexity, design alignment | Opus agent (fix-all) |
| **Phase content quality** | plan-reviewer | Phase 1 (per-phase) | Type-aware criteria, LLM failure modes | Sonnet agent (fix-all) |
| **Runbook assembly** | prepare-runbook.py | Phase 4 | Cycle/step numbering, structure requirements, file references | Script validation |
| **Holistic consistency** | plan-reviewer | Phase 3 | Cross-phase dependencies, metadata, path consistency | Sonnet agent (fix-all) |
| **Artifact generation** | prepare-runbook.py | Phase 4 | Agent creation, step file format, orchestrator plan | Script checks |

### Quality Gate Enforcement

**Proportional model:** Review severity matches artifact risk
- Low-risk document review (outline, runbook phases) → fix-all with agent
- Structural validation (numbering, references) → script checks
- Cross-cutting consistency → interactive review (holistic)

---

## 9. Key Architectural Insights

### Tier Assessment Before Planning

The runbook skill includes upfront Tier Assessment (1/2/3):
- **Tier 1:** Direct implementation (<6 files, single session, no parallelization)
- **Tier 2:** Lightweight delegation (6-15 files, sequential, single model)
- **Tier 3:** Full runbook (multiple independent steps, model switching, long-running, >15 files, >10 TDD cycles with cross-dependencies)

Only Tier 3 proceeds to the full pipeline described above. Tiers 1-2 skip runbook ceremony.

### Review Timing

- **Outline review:** Blocks expansion (must pass before Phase 1)
- **Per-phase reviews:** Background (don't block next phase generation)
- **Holistic review:** Blocks prepare-runbook (must pass before Phase 4)

### Phase Files vs Full Runbook

- **Phase files:** Intermediate artifacts (`runbook-phase-N.md`), reviewed individually
- **Full runbook:** Assembled from phases, reviewed holistically before prepare-runbook.py
- **prepare-runbook.py input:** Can accept either file or directory
  - If directory: assembles phase files automatically
  - If file: processes single runbook.md directly

### Consolidation Gates

Two consolidation opportunities:
1. **Phase 0.85 (outline):** Merge trivial phases before expensive expansion
2. **Phase 2.5 (runbook):** Merge isolated trivial items after assembly, update metadata

Both are judgment-based gates applied before next phase.

### Sufficiency Fast-Path

Phase 0.95 checks if outline is detailed enough to serve as runbook directly:
- All items specify target files/locations
- All items have concrete actions (no "determine"/"evaluate")
- All items have verification criteria
- No unresolved design decisions
- TDD threshold: <3 phases AND <10 cycles total

If sufficient: skip Phase 1 expansion, jump to Phase 4 preparation.

---

## 10. Gaps and Questions

1. **Design quality gates:** The current pipeline lacks pre-/post-design review integration. Design-vet-agent exists but not mentioned in pipeline chain. How does design quality affect runbook quality gates?

2. **Outline review escalation:** runbook-outline-review-agent can find "UNFIXABLE" issues but doesn't define escalation protocol (UNFIXABLE taxonomy). Does it use the same UNFIXABLE classification as plan-reviewer?

3. **Consolidation gate criteria:** Phase 0.85 and 2.5 describe "trivial" phases/items but don't specify exact criteria beyond item count and marked complexity. How are merge candidates identified programmatically vs. heuristically?

4. **Backward compatibility:** Phase files can use 0-based or 1-based numbering (script accepts both). How does this affect cross-phase numbering validation?

5. **TDD vs general mixing:** Mixed runbooks supported (both cycles and steps), but unclear what execution model is applied to general steps in a TDD runbook context.

6. **Background review fault handling:** Phase 1 uses background reviews. How are review failures detected/handled when they complete asynchronously?

