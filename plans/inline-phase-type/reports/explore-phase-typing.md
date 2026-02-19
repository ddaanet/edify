# Exploration: Phase Type Handling Across the Pipeline

**Date**: 2026-02-19
**Scope**: How `type: tdd` vs `type: general` flows through prepare-runbook.py, plan-reviewer, runbook skill, and orchestrate skill

---

## Summary

Phase typing is a planner-facing concept that flows through two channels: (1) header syntax (`## Cycle X.Y:` vs `## Step N.M:`) which prepare-runbook.py auto-detects, and (2) prose type tags in outline headings (`type: tdd`) which runbook/SKILL.md and plan-reviewer consume. The orchestrate skill is type-blind at runtime — it reads the `Phase:` field from step file headers and uses `type: tdd` only for post-execution routing (TDD process review). A third type would require changes in three places: prepare-runbook.py validation gates, the runbook skill expansion logic, and plan-reviewer's detection and criteria application.

---

## Component Analysis

### 1. prepare-runbook.py

**File**: `/Users/david/code/claudeutils-wt/error-handling-design/agent-core/bin/prepare-runbook.py`

#### How phase type is consumed

Type is handled at two levels:

**Frontmatter level** (`parse_frontmatter`, lines 63–100):
- Reads `type:` key from YAML frontmatter
- Valid values: `['tdd', 'general', 'mixed']` (line 95)
- Defaults to `'general'` if absent or unknown (with stderr warning)
- Unknown type: warn + fallback to `'general'`

**Content auto-detection** (`main`, lines 928–936):
- After parsing, auto-detects effective type from headers:
  - Has `## Cycle X.Y:` → `tdd`
  - Has both cycles and steps → `mixed`
  - Has neither → keeps frontmatter type
- **Content overrides frontmatter** — the `metadata['type']` is overwritten based on what headers are found

#### What it generates per type

**Agent selection** (`read_baseline_agent`, lines 504–524):
```python
if runbook_type == 'tdd':
    baseline_path = Path('agent-core/agents/tdd-task.md')
else:
    baseline_path = Path('agent-core/agents/quiet-task.md')
```
- `tdd` → tdd-task.md baseline (RED/GREEN/REFACTOR protocol)
- `general` or `mixed` → quiet-task.md baseline (generic execution)

**Step file generation** (`validate_and_create`, lines 760–876):
- `tdd` type: requires cycles, rejects if none; generates `step-{major}-{minor}.md` files via `generate_cycle_file()`
- `general` type: requires steps, rejects if none; generates `step-{N}-{M}.md` files via `generate_step_file()`
- `mixed` type: requires BOTH cycles AND steps; uses quiet-task.md; generates both cycle and step files

**Cycle validation** (TDD-only, lines 939–970):
- `validate_cycle_numbering()` — checks for duplicates, gaps, minor-starts-at-1
- `validate_cycle_structure()` — requires RED/GREEN sections, Stop/Error Conditions
- These validations only run when cycles are present (`has_cycles`)

**Phase boundary tagging** (`generate_step_file`, line 674):
```python
f"**Phase**: {phase}",
```
Phase number written to each step file header. Used by orchestrate to detect phase boundaries.

#### Hardcoded two-type assumptions

- `read_baseline_agent()` has a binary branch: `if runbook_type == 'tdd': ... else: ...` (line 513). Mixed maps to `'general'` baseline via the caller: `'general' if runbook_type == 'mixed' else runbook_type` (line 812).
- `validate_and_create()` has explicit `if/elif/else` for `tdd`, `mixed`, `general` — a third type would fall to `else` (general), silently validated as general.
- Cycle structure validation (`validate_cycle_structure`) is TDD-specific with spike/regression subtypes — no equivalent for a hypothetical third type.
- Phase file assembly (`assemble_phase_files`): detects type from headers (Cycle vs Step), no other type markers understood.

#### What would need to change for a third type

- Add to `valid_types` list (line 95)
- Add explicit validation gate in `validate_and_create()` for the new type's required content
- Add agent baseline selection branch in `read_baseline_agent()`
- Add structure validation function analogous to `validate_cycle_structure()`
- Add content detection in `assemble_phase_files()` if the new type has distinct header syntax

---

### 2. plan-reviewer agent

**File**: `/Users/david/code/claudeutils-wt/error-handling-design/agent-core/agents/plan-reviewer.md`

#### How phase type is consumed

Detection logic (Document Validation section):
- **TDD**: `type: tdd` in phase metadata OR `## Cycle` / `### Cycle` headers
- **General**: `## Step` / `### Step` headers OR no type marker (default)
- **Mixed**: Both header types across phases — applies per-type criteria per phase

The agent applies **type-specific review criteria**:

**TDD phases:**
- Prescriptive code detection in GREEN phases
- Prose test quality validation in RED phases
- RED/GREEN sequencing checks
- Consolidation quality for merged cycles

**General phases:**
- Prerequisite validation for creation steps
- Script evaluation (size classification)
- Step clarity (Objective/Implementation/Expected Outcome)
- Conformance validation

**All phases (type-agnostic):**
- LLM failure modes: vacuity, dependency ordering, density, checkpoint spacing
- Metadata accuracy
- File reference validation
- Model assignment review (advisory)

The report header includes `**Phase types**: [TDD | General | Mixed (N TDD, M general)]`.

#### What would need to change for a third type

- Add detection heuristic (what header or marker identifies the new type)
- Add review criteria section for the new type's specific quality checks
- Update Document Validation section to name the new type
- Update report header format
- `review-plan/SKILL.md` has the same structure — changes needed in both

---

### 3. runbook skill

**File**: `/Users/david/code/claudeutils-wt/error-handling-design/agent-core/skills/runbook/SKILL.md`

#### How phase type is consumed

Phase type is a planning-time concept in this skill. It appears in:

**Outline phase tags** (Phase 0.75 section):
```markdown
### Phase 1: Core behavior (type: tdd)
### Phase 2: Skill definition updates (type: general)
```
These tags are prose in outline headings — consumed by the planner and plan-reviewer, not by prepare-runbook.py (which auto-detects from headers).

**Expansion branching** (Phase 1, lines 427–443):
```
Check phase type tag from outline phase heading
Expand based on phase type:
  [TDD phases] — Cycle Planning: ...
  [General phases] — Script Evaluation: ...
```
The skill has two named expansion paths. Each has distinct content requirements:
- TDD: RED/GREEN/REFACTOR cycle structure, prose test descriptions, stop conditions
- General: Objective/Implementation/Expected Outcome structure, script evaluation, prerequisites

**Per-phase type model** (lines 28–47):
- Type determines: expansion format, review criteria
- Type does NOT affect: tier assessment, outline generation, consolidation gates, assembly, orchestration, checkpoints

**TDD Cycle Planning Guidance section** (lines 472–553): Dedicated 80-line subsection for TDD expansion only. No equivalent for general phases (general guidance is inline in Phase 1).

**Outline sufficiency check** (Phase 0.95, lines 384–408):
- TDD threshold: also skip expansion when `<3 phases AND <10 cycles total`
- This threshold is TDD-specific hardcoding

**Runbook template** (lines 836–887): Shows `## Cycle 1.1:` and `## Step 2.1:` as the two structural patterns.

**Weak Orchestrator Metadata** (lines 594–619):
```markdown
**Execution Model** (general phases only — TDD cycles use phase-level model):
```
Model assignment is differentiated by type in the metadata format.

#### What would need to change for a third type

- Add expansion format section analogous to "TDD Cycle Planning Guidance"
- Update Phase 1 expansion branching to handle the new type tag
- Update Phase 0.95 sufficiency thresholds
- Update the runbook template to show the new type's structural header pattern
- Update the Weak Orchestrator Metadata format note
- Update outline phase tagging format examples
- Update review delegation in Phase 1 step 4 (plan-reviewer receives type-aware criteria)

---

### 4. orchestrate skill

**File**: `/Users/david/code/claudeutils-wt/error-handling-design/agent-core/skills/orchestrate/SKILL.md`

#### How phase type is consumed

The orchestrate skill is largely **type-blind at runtime**. Phase type surfaces in two specific places:

**Phase boundary detection** (Section 3.3):
```
Read the next step file header (first 10 lines of `plans/<name>/steps/step-{N+1}.md`).
Compare its `Phase:` field with the current step's phase.
```
This uses the numeric `Phase:` field written by `prepare-runbook.py`, not the type. Type is irrelevant to phase transition logic.

**Post-execution routing** (Section 6, Completion):
```
If runbook frontmatter has `type: tdd`:
  Delegate to review-tdd-process for process analysis
  Write report to `plans/<name>/reports/tdd-process-review.md`
```
This is the only type-conditional behavior in orchestrate. It reads `type: tdd` from the runbook frontmatter (not step files) to decide whether to run TDD process review after all steps complete.

**Step execution** (Section 3.1):
The model for each step comes from the step file's `**Execution Model**` field (placed there by prepare-runbook.py). The orchestrator reads this per-step — no type inference.

**Error escalation** (Section 4):
- Level 1: Haiku → Sonnet (Refactor Agent) — triggered by "quality check warnings from TDD cycles"
- This escalation description mentions TDD cycles but the trigger is output-based, not type-detected

#### What would need to change for a third type

- If a third type needs post-execution process review analogous to `review-tdd-process`, add a corresponding conditional in Section 6
- The `type: tdd` check in Section 6 is the only type-conditional branch — adding a third type requires an additional `elif`
- No changes needed to step execution loop, phase boundary detection, or error escalation (all type-agnostic)

---

## Cross-Cutting Patterns

### Type detection is dual-channel and redundant

Two independent mechanisms determine effective type:

| Channel | Where | How |
|---------|-------|-----|
| Frontmatter | `parse_frontmatter()` | Reads `type:` YAML key |
| Content | `main()` auto-detect | Presence of `## Cycle` vs `## Step` headers |

Content overrides frontmatter. This means a runbook with `type: general` in frontmatter but `## Cycle` headers will be treated as `tdd`. The redundancy provides resilience but makes the frontmatter advisory.

### The type tag in outline headings is planner-only

The `(type: tdd)` annotation in outline phase headings (e.g., `### Phase 1: Core behavior (type: tdd)`) is consumed by:
- The runbook skill (to choose expansion path)
- The plan-reviewer (to apply criteria)

It is NOT consumed by prepare-runbook.py. That script infers type from headers, not outline annotations.

### Mixed runbooks are structurally supported but lightly tested

prepare-runbook.py has explicit `mixed` handling throughout. However:
- It maps to `quiet-task.md` (general baseline), not a dedicated mixed baseline
- No dedicated cycle validation for mixed (cycles validated same as pure TDD)
- The runbook skill and plan-reviewer support mixed via "per-phase type tagging" — documented but no distinct expansion path

### Orchestration is type-agnostic for step execution

The orchestrator executes all steps identically regardless of phase type. The only type-driven behavior is post-completion routing. This means adding a third type would not require changes to the core execution loop.

---

## Gaps and Assumptions

**Assumption: exactly two expansion paths in /runbook skill.** The Phase 1 expansion section has two named branches (`[TDD phases]` and `[General phases]`). A third type would require a named branch.

**Assumption: two baseline agents.** `tdd-task.md` and `quiet-task.md`. A third type requiring different agent behavior needs a third baseline or parameterized selection.

**Assumption: binary post-execution routing in orchestrate.** `if type: tdd` → run tdd-process-review. No else-if for other types. Adding a third type needing its own process review requires extending this.

**Assumption: TDD cycle validation is the only structural validation.** `validate_cycle_structure()` enforces RED/GREEN/stop-conditions only for TDD cycles. General steps have no analogous structural validation in prepare-runbook.py. A third type with structural requirements would need new validation.

**Undocumented dependency:** The outline phase type tag (`type: tdd` in `### Phase N:` headings) is prose convention — not parsed by any tool. Its enforcement is entirely through planner discipline and plan-reviewer reading. There is no machine-readable schema for it.
