# Runbook Quality Gates — Design

## Problem

The runbook pipeline has validation gaps at two points: (1) between outline finalization and expansion, where redundant patterns inflate expansion cost and cycle count; and (2) between Phase 3 (holistic review) and Phase 4 (prepare-runbook.py), where expanded phase files may contain incorrect model assignments, file lifecycle violations, implausible RED states, and inaccurate test count checkpoints. These defects propagate to execution, wasting cycles on avoidable failures.

## Requirements

**Source:** `plans/runbook-quality-gates/requirements.md`

**Functional:**
- FR-1: Outline-level consolidation — addressed by simplification agent (Phase 0.86)
- FR-2: Model selection review — split: mechanical (validate-runbook.py `model-tags`) + semantic (review-plan skill enrichment)
- FR-3: File lifecycle validation — addressed by validate-runbook.py `lifecycle`
- FR-4: RED plausibility audit — addressed by validate-runbook.py `red-plausibility` (structural) + optional agent (semantic)
- FR-5: Test count reconciliation — addressed by validate-runbook.py `test-counts`
- FR-6: Scaling by runbook size — addressed by mandatory-for-all design (scripts are fast, agent cost bounded)

**Non-functional:**
- NFR-1: Workflow integration — new steps slot into existing pipeline without breaking flow
- NFR-2: Incremental adoption — each capability independently deployable, graceful degradation

**Out of scope:**
- Execution-time monitoring (orchestrator)
- Design-level quality (design-vet-agent)
- Per-phase TDD discipline review (plan-reviewer handles in Phase 1)
- Modifying orchestrate skill or prepare-runbook.py internals

## Delivery Phases

**Two-phase delivery, split by artifact type and review needs:**

### Delivery Phase A: Prose Edits

Architectural artifacts — agent definitions, skill updates, pipeline contracts, memory index. All require opus. Can merge to main quickly after vet review.

**Deliverables:**
- `agent-core/agents/runbook-simplification-agent.md` — new agent (FR-1)
- `agent-core/skills/runbook/SKILL.md` — add Phase 0.86 + Phase 3.5 (NFR-1)
- `agent-core/skills/review-plan/SKILL.md` — add model assignment criteria (FR-2 semantic)
- `agent-core/agents/plan-reviewer.md` — add model assignment mention in Review Criteria (FR-2 semantic)
- `agents/decisions/pipeline-contracts.md` — add T2.5, T4.5 transformations (NFR-1)
- `agents/memory-index.md` — add entries for new decisions

### Delivery Phase B: Scripts (TDD)

Python validation script with unit tests and fixture runbooks. Requires TDD discipline and careful review. Separate merge after Phase A lands.

**Deliverables:**
- `agent-core/bin/validate-runbook.py` — 4 subcommands (FR-2 mechanical, FR-3, FR-4 structural, FR-5)
- `tests/test_validate_runbook.py` — unit tests with fixture runbooks
- `tests/fixtures/runbooks/` — test fixture runbooks (valid + violation cases)

**Dependency:** Phase B's SKILL.md references (`validate-runbook.py`) already exist from Phase A edits. Phase A writes the invocation pattern; Phase B implements the script. If Phase A merges first, SKILL.md will reference a script that doesn't exist yet — this is fine because NFR-2 requires graceful degradation (skill checks existence before invoking).

---

## Architecture

### Pipeline Position

```
0.85 → [0.86: Simplification agent (FR-1)] → 0.9 → 0.95 → Phase 1 (plan-reviewer enriched: FR-2 semantic) → Phase 2 → 2.5 → Phase 3 → [3.5: Pre-execution validation (FR-2 mechanical, FR-3, FR-4, FR-5)] → Phase 4
```

### Simplification Agent (FR-1) — Phase A

**File:** `agent-core/agents/runbook-simplification-agent.md`

**Trigger:** After Phase 0.85 trivial merging, before Phase 0.9 complexity check. Mandatory for all Tier 3 runbooks.

**Agent structure:**

```yaml
---
name: runbook-simplification-agent
description: |
  Consolidates redundant patterns in runbook outlines after Phase 0.85.
  Detects identical-pattern items, independent same-module functions,
  and sequential additions. Rewrites outline with consolidations applied.
model: opus
color: cyan
tools: ["Read", "Write", "Edit", "Grep", "Glob"]
skills: ["project-conventions"]
---
```

**Process:**
- Read `runbook-outline.md` (post-0.85 state) and design.md (for requirements context)
- Detect consolidation patterns (3 categories below)
- Rewrite outline with consolidations applied
- Update item numbering and requirements mapping table
- Write report to `plans/<job>/reports/simplification-report.md`
- Return filepath

**Pattern detection categories:**

1. **Identical-pattern items:** Same function modified, same test structure, only fixture data varies. Indicator: N items with titles like "add X detection for status A/B/C/D". Consolidation: single parametrized item with table of inputs.

2. **Independent same-module functions:** Multiple items each creating a small function in the same module, no inter-dependencies. Indicator: items share a `File:` target, each adding a standalone function. Consolidation: batch into single item listing all functions.

3. **Sequential additions:** Items each adding one element to the same output/data structure. Indicator: items modify same loop body or dict constructor. Consolidation: single item adding all elements.

**Post-simplification:** Outline re-enters pipeline at Phase 0.9. No re-review by outline-review-agent needed — simplification agent validates its own output against outline structure rules (requirements mapping completeness, phase structure, item numbering).

**Output format:** Report documenting what was consolidated, before/after item counts, and any patterns left unconsolidated (with rationale).

### Review-Plan Skill Enrichment (FR-2 Semantic) — Phase A

**File:** `agent-core/skills/review-plan/SKILL.md`

**Change:** Add Section 12 to Review Criteria: "Model Assignment Review."

**New criteria:**

```markdown
### 12. Model Assignment Review — all phases

**Check:** Model tag matches task complexity and artifact type.

**Artifact-type override violations (advisory):**
- Steps editing skills (`agent-core/skills/`), fragments (`agent-core/fragments/`),
  agents (`agent-core/agents/`), or workflow decisions (`agents/decisions/workflow-*.md`)
  assigned below opus → flag
- Pattern: Check `File:` references in Changes section against override paths

**Complexity-model mismatch (advisory):**
- Synthesis tasks (combining multiple source files into new artifact) assigned below sonnet → flag
- Mechanical grep-and-delete or single-line changes assigned above haiku → flag

**Advisory only.** Model assignment involves judgment — findings inform but don't block.
Do NOT mark as UNFIXABLE or CRITICAL. Report as Minor with suggested correction.
```

**Integration:** plan-reviewer.md Review Criteria section gets one line: "Model assignment review: artifact-type overrides, complexity-model mismatches (advisory, see review-plan skill Section 12)"

### Plan-Reviewer Update (FR-2 Semantic) — Phase A

**File:** `agent-core/agents/plan-reviewer.md`

**Change:** Add to Review Criteria section, under "All phases (LLM failure modes)":

```markdown
- Model assignment: Artifact-type override violations, complexity-model mismatches (advisory — see review-plan skill)
```

Single line addition. Criteria detail lives in review-plan skill (already preloaded via `skills: ["review-plan"]`).

### SKILL.md Updates (NFR-1) — Phase A

**File:** `agent-core/skills/runbook/SKILL.md`

**Changes (3 locations):**

**1. Process overview (line ~181):** Add Phase 0.86 and Phase 3.5 to the list.

```markdown
- Phase 0.85: Consolidation gate (outline)
- Phase 0.86: Simplification pass (pattern consolidation)
- Phase 0.9: Complexity check before expansion
...
- Phase 3: Final holistic review
- Phase 3.5: Pre-execution validation
- Phase 4: Prepare artifacts and handoff
```

**2. New section after Phase 0.85 (after line ~308):** Add Phase 0.86.

```markdown
### Phase 0.86: Simplification Pass

**Objective:** Detect and consolidate redundant patterns before expensive expansion.

**Mandatory** for all Tier 3 runbooks.

**Actions:**

1. **Delegate to simplification agent:**
   - Agent: `runbook-simplification-agent`
   - Input: `plans/<job>/runbook-outline.md` (post-0.85 state)
   - Output: Consolidated outline + report at `plans/<job>/reports/simplification-report.md`

2. **Review simplification report:**
   - Read report filepath returned by agent
   - Check before/after item counts
   - Verify requirements mapping preserved

3. **Proceed to Phase 0.9** with simplified outline.

**Pattern categories detected:**
- Identical-pattern items (same function, varying data) → parametrized single item
- Independent same-module functions → batched single item
- Sequential additions to same structure → merged single item

**When to skip:** Outline has ≤10 items (consolidation unlikely to find patterns worth merging). Agent still runs but reports "no consolidation candidates" rather than skipping entirely — maintains mandatory gate (D-4) while avoiding wasted effort on small outlines.
```

**3. New section after Phase 3 (after line ~645):** Add Phase 3.5.

```markdown
### Phase 3.5: Pre-Execution Validation

**Objective:** Validate assembled runbook structurally before artifact generation.

**Mandatory** for all Tier 3 runbooks.

**Actions:**

1. **Run validation checks:**
   ```bash
   agent-core/bin/validate-runbook.py model-tags plans/<job>/
   agent-core/bin/validate-runbook.py lifecycle plans/<job>/
   agent-core/bin/validate-runbook.py test-counts plans/<job>/
   agent-core/bin/validate-runbook.py red-plausibility plans/<job>/
   ```

   Each subcommand writes a report to `plans/<job>/reports/validation-{subcommand}.md`.

   **Exit codes:** 0 = pass, 1 = violations (blocking), 2 = ambiguous (optional semantic analysis).

2. **Handle results:**
   - All exit 0: proceed to Phase 4
   - Any exit 1: STOP, report violations to user
   - Any exit 2 (red-plausibility only): optionally delegate semantic analysis to agent

3. **Graceful degradation:** If `validate-runbook.py` doesn't exist, skip Phase 3.5 and proceed to Phase 4 with warning. This supports incremental adoption (NFR-2).

**Validation checks:**
- `model-tags`: File path → model mapping. Artifact-type files (skills/, fragments/, agents/, workflow-*.md) must have opus tag.
- `lifecycle`: Create→modify dependency graph. Flags modify-before-create, duplicate creation, future-phase reads.
- `test-counts`: Checkpoint "All N tests pass" claims vs actual test function count.
- `red-plausibility`: Prior GREENs vs RED expectations. Flags already-passing states.
```

### Scaling (FR-6) — Addressed by Design

FR-6 originally specified delegated-per-phase agents for large runbooks vs single-agent for small. This design simplifies: all validation is mandatory for all Tier 3 runbooks (D-4). The scaling concern dissolves because:

- **Scripts (Phase 3.5):** Text parsing — O(n) in runbook size, fast regardless of scale. No agent delegation needed.
- **Simplification agent (Phase 0.86):** Operates on outline (not expanded phases), so input size bounded by outline item count. Cost scales linearly with outline size, not expanded cycle count.
- **Plan-reviewer enrichment (FR-2 semantic):** Already runs per-phase — no change to scaling model.

No separate small/large code paths needed. FR-6 acceptance criteria (equivalent quality for both sizes) satisfied by uniform mandatory execution.

### Pipeline Contracts Updates — Phase A

**File:** `agents/decisions/pipeline-contracts.md`

**Change:** Add two rows to the transformation table (between T2/T3 and T4/T5):

```markdown
| T2.5 | Outline → Simplified outline | runbook-outline.md (post-0.85) | runbook-outline.md (consolidated) | Missed patterns, broken numbering | runbook-simplification-agent (opus) | Pattern detection, requirements preservation |
| T4.5 | Runbook → Validated runbook | runbook-phase-*.md or runbook.md | Validation reports | Model mismatches, lifecycle violations, count errors, implausible REDs | validate-runbook.py (script) | Deterministic structural checks |
```

### Memory Index Updates — Phase A

**File:** `agents/memory-index.md`

**Add entries under `agents/decisions/pipeline-contracts.md` section:**

```markdown
/when simplifying runbook outlines | pattern consolidation identical-pattern batching
/when validating runbook pre-execution | model-tags lifecycle test-counts red-plausibility structural
```

### validate-runbook.py (FR-2 Mechanical, FR-3, FR-4 Structural, FR-5) — Phase B

**File:** `agent-core/bin/validate-runbook.py`

Single script, 4 subcommands. Orchestrator-invoked internal tooling — not user-facing CLI. Incremental adoption (NFR-2) achieved via subcommand granularity — orchestrator invokes each check independently and can omit any subset.

**Shared infrastructure:**
- Reuse parsing patterns from prepare-runbook.py: `extract_cycles()`, `extract_sections()`, `extract_file_references()`, `extract_step_metadata()`, `assemble_phase_files()`
- Import approach: either import from prepare-runbook.py directly (if it's importable) or duplicate the minimal regex patterns needed. Design decision for Phase B planner.
- Input: directory path (assembles phase files) or single runbook.md file
- Output: structured report at `plans/<job>/reports/validation-{subcommand}.md`
- Exit codes: 0 (pass), 1 (violations), 2 (ambiguous, red-plausibility only)

**Subcommand: `model-tags`**

Parse `**Execution Model**:` tags and `File:` references from all steps/cycles. Match file paths against artifact-type override rules:
- `agent-core/skills/` → opus required
- `agent-core/fragments/` → opus required
- `agent-core/agents/` → opus required
- `agents/decisions/workflow-*.md` → opus required

Flag: artifact-type file referenced with non-opus model tag. Report: file path, current model, expected model, step/cycle location.

**Subcommand: `lifecycle`**

Parse `File:` + `Action:` references from all phases. Build dependency graph:
- Track creation actions (Create, Write new) with phase:cycle/step location
- Track modification actions (Modify, Add, Update, Edit) with location
- Track read-only references

Flag:
- Modify-before-create: file modified in phase:cycle before creation phase:cycle
- Duplicate creation: file created in multiple cycles/steps
- Future-phase reads: step references file content that doesn't exist until a later phase creates it
- Missing creation: file marked "Existing file" but not found on disk and not created in prior cycles

**Subcommand: `test-counts`**

Extract `**Test:**` fields from TDD cycles. Parse checkpoint claims ("All N tests pass"). Reconcile:
- Count unique test function names per phase (cumulative across phases)
- Account for parametrized tests: `test_foo[param1]` counts as 1 function
- Account for deleted tests (explicit removal in cycle description)
- Compare against checkpoint claims

Flag: mismatch between claimed count and reconciled count. Report: checkpoint location, claimed N, actual N, test function list.

**Subcommand: `red-plausibility`**

For each RED phase, check if prior GREENs created the module/function the RED test expects to fail on:
- Parse RED `**Expected failure:**` for function/module names
- Check if prior GREEN `**Changes:**` sections created that function/module
- If function already exists from prior GREEN → flag as "already-passing" (RED won't fail)

Exit 2 for ambiguous cases (function exists but behavior might differ). Exit 1 for clear violations. Exit 0 if all REDs are plausible.

**Report format (all subcommands):**

```markdown
# Validation Report: {subcommand}

**Runbook:** {path}
**Date:** {ISO timestamp}
**Result:** PASS | FAIL | AMBIGUOUS

## Violations

### 1. {description}
- **Location:** Phase {N}, {Cycle/Step} {X.Y}
- **File:** {path}
- **Expected:** {what should be}
- **Found:** {what was found}

## Summary

- Checks run: {N}
- Passed: {N}
- Failed: {N}
- Ambiguous: {N} (red-plausibility only)
```

### Test Strategy — Phase B

**TDD approach.** Fixture-based testing with sample runbook content.

**Fixtures needed:**
- Valid TDD runbook (3 phases, correct lifecycle, correct counts, plausible REDs)
- Valid general runbook (2 phases, correct model tags)
- Violation cases per subcommand:
  - model-tags: skill file with haiku tag
  - lifecycle: modify-before-create, duplicate creation
  - test-counts: checkpoint claiming 5 when 3 tests exist
  - red-plausibility: RED testing function created in prior GREEN

**Fixture format:** Markdown strings in test file or separate `.md` files in `tests/fixtures/runbooks/`.

**Test structure:** One test module `tests/test_validate_runbook.py`. Parametrized tests per subcommand with valid/violation fixture pairs.

## Key Design Decisions

**D-1: FR-1 at outline level (from outline).** Consolidation operates on outline items, not expanded phases. Saves expansion cost. Workwoods evidence confirms patterns detectable from titles. Note: requirements.md FR-1 text says "After Phase 1 expansion completes" — this was superseded by the outline discussion (Phase B) which moved consolidation earlier to Phase 0.86. Requirements.md should be updated to reflect this decision.

**D-2: FR-2 split (from outline).** Mechanical (file path → model) is script. Semantic (task complexity → model) is plan-reviewer enrichment. Different enforcement layers for different failure modes.

**D-3: Dedicated simplification agent (from outline).** Every pipeline transformation has a dedicated enforcer. Simplification is optimization, not defect detection.

**D-4: Mandatory for all Tier 3 (from outline).** Both simplification and Phase 3.5 mandatory. Scripts are fast. Simplification agent cost bounded by outline size.

**D-5: Two-phase delivery.** Prose edits (Phase A) merge first — all architectural artifacts, opus review. Scripts (Phase B) follow with TDD — separate merge after careful review. Phase A establishes invocation patterns; Phase B implements the script. Graceful degradation (NFR-2) bridges the gap.

**D-6: Advisory model review.** FR-2 semantic findings are advisory (Minor severity), not blocking. Model assignment involves judgment — hard rules would produce false positives on edge cases.

**D-7: Reuse prepare-runbook.py patterns.** validate-runbook.py reuses parsing infrastructure (cycle extraction, file reference extraction, step metadata). Avoids duplicating 200+ lines of regex patterns. Implementation detail left to Phase B planner.

## Requirements Traceability

| Requirement | Design Element | Delivery Phase |
|-------------|---------------|----------------|
| FR-1 | Simplification Agent (Phase 0.86) | A |
| FR-2 (mechanical) | validate-runbook.py `model-tags` | B |
| FR-2 (semantic) | Review-Plan Skill Section 12 + plan-reviewer update | A |
| FR-3 | validate-runbook.py `lifecycle` | B |
| FR-4 (structural) | validate-runbook.py `red-plausibility` | B |
| FR-4 (semantic) | Optional agent on exit 2 (ambiguous) | B |
| FR-5 | validate-runbook.py `test-counts` | B |
| FR-6 | Scaling section — mandatory uniform execution | A (design) |
| NFR-1 | SKILL.md Phase 0.86 + Phase 3.5 + pipeline-contracts T2.5/T4.5 | A |
| NFR-2 | Graceful degradation (existence checks), `--skip-*` flags | A (skill) + B (script) |

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agent-core/skills/runbook/SKILL.md` — primary integration target, pipeline structure
- `agent-core/agents/plan-reviewer.md` — FR-2 semantic integration target
- `agent-core/skills/review-plan/SKILL.md` — review criteria detail
- `agent-core/agents/runbook-outline-review-agent.md` — template for simplification agent
- `agents/decisions/pipeline-contracts.md` — transformation table structure
- `agents/memory-index.md` — entry format and conventions

**Phase B additional reading:**
- `agent-core/bin/prepare-runbook.py` — parsing functions to reuse
- `tests/` — existing test patterns and conventions

**Skill-loading directives:**
- Load `plugin-dev:agent-development` before planning Phase A (simplification agent creation)

**Execution model directives:**
- Phase A: All deliverables are architectural artifacts → opus required
- Phase B: Script development → TDD, sonnet for test design, haiku for implementation

## References

- `plans/runbook-quality-gates/requirements.md` — source requirements
- `plans/runbook-quality-gates/outline.md` — approved outline (Phase B validated)
- `plans/runbook-quality-gates/reports/explore-pipeline.md` — pipeline exploration
- `plans/runbook-quality-gates/reports/explore-validation.md` — validation infrastructure
- `plans/runbook-quality-gates/reports/outline-review.md` — outline review report

## Next Steps

1. `/runbook plans/runbook-quality-gates/design.md` — Plan Phase A first (prose edits)
2. After Phase A merges: Plan and execute Phase B (validate-runbook.py TDD)
