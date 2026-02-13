# Runbook Review: LLM Failure Mode Analysis

**Artifact**: plans/worktree-update/runbook-phase-*.md (7 phases, 40 cycles)
**Date**: 2026-02-12
**Reviewer**: Sonnet (manual application of runbook-review.md methodology)
**Context**: Post-generation review applying LLM failure mode detection (vacuous cycles, dependency ordering, cycle density, checkpoint spacing)

---

## Executive Summary

The tdd-plan-reviewer agent successfully caught file reference errors and validated TDD discipline (no prescriptive code, proper RED/GREEN sequencing). However, it did not detect **semantic issues** that lead to haiku execution failures.

This review applies the four-axis methodology from `agents/decisions/runbook-review.md`:
1. **Vacuous Cycles** — scaffolding-only tests haiku satisfies with degenerate code
2. **Dependency Ordering** — forward references causing execution against wrong assumptions
3. **Cycle Density** — unnecessary cycles that dilute quality and increase context pressure
4. **Checkpoint Spacing** — gaps where haiku drift accumulates without correction

---

## Findings Summary

| # | Axis | Severity | Finding | Action |
|---|------|----------|---------|--------|
| 1 | Vacuous | Medium | Cycle 1.1 — structural CLI registration | Merge into 1.2 |
| 2 | Vacuous | Medium | Cycle 1.4 — self-declared "should pass immediately" | Merge into 1.3 |
| 3 | Vacuous | Medium | Cycle 5.3 — self-declared "no additional code needed" | Merge into 5.2 |
| 4 | Dependency | **High** | Missing jobs.md auto-resolve (design line 159) | Add cycle or merge with 7.8 |
| 5 | Dependency | Medium | Test file consolidation drifted from design | Already fixed by tdd-plan-reviewer |
| 6 | Dependency | Low | Phase 4→3 dependency declaration is spurious | Correct to "None" |
| 7 | Density | Medium | Cycle 4.3 identical logic to 4.2 | Merge into 4.2 |
| 8 | Checkpoint | Low | 17 cycles between Phase 5 and Phase 7 checkpoints | Add checkpoint after Phase 6 |

**Net effect:** 40 → 36 cycles (4 eliminated via vacuity/density), 1 cycle added (jobs.md), 1 checkpoint added (Phase 6). **Final: 37 cycles, 4 checkpoints.**

---

## 1. Vacuous Cycles (3 found)

**Definition**: Cycles where RED tests don't constrain implementation. Haiku satisfies them with structurally correct but behaviorally meaningless code.

### Finding 1.1: Cycle 1.1 — CLI Group Registration

**Location**: Phase 1, Cycle 1.1
**Problem**: RED assertions are entirely structural:
- `import succeeds` — satisfiable by empty file
- `isinstance(worktree, click.Group)` — satisfiable by `worktree = click.Group()`
- `help output does NOT contain "_worktree"` — satisfiable by underscore prefix (convention, not behavior)
- `direct invocation works` — satisfiable by empty command

GREEN adds ≤3 lines: import + `cli.add_command(worktree)`. No branching, no state transformation.

**Grounding**: [Jiang et al., 2024](https://arxiv.org/html/2406.08731v1) — LLMs produce "syntactically correct but irrelevant" code at 13.6–31.7% rate when RED tests don't constrain behavior.

**Action**: Merge into Cycle 1.2 as setup. Registration is prerequisite for testing `wt_path()`, not standalone behavior.

**Impact**: 40 → 39 cycles

---

### Finding 1.2: Cycle 1.4 — Sibling Path Multiple Slugs

**Location**: Phase 1, Cycle 1.4
**Problem**: Runbook self-declares: "Test should pass immediately (logic from 1.3 already handles this)" and "likely no changes needed if 1.3 implemented correctly."

GREEN adds 0 lines. Tests statelesness already guaranteed by pure-function design.

**Grounding**: Vacuous cycles that add no implementation waste expansion budget and orchestrator overhead for zero behavioral progress.

**Action**: Add as parametrized assertions within Cycle 1.3 (`wt_path("a")` vs `wt_path("b")` same parent).

**Impact**: 39 → 38 cycles

---

### Finding 1.3: Cycle 5.3 — Existing Submodule Branch Reuse

**Location**: Phase 5, Cycle 5.3
**Problem**: Runbook self-declares: "Logic from 5.2 already checks submodule branch existence... No additional code needed if 5.2 implemented correctly."

GREEN says "Verify submodule branch detection logic from 5.2 is correct (likely no changes needed)."

GREEN adds 0 lines. Tests a non-branch already covered by 5.2's conditional.

**Grounding**: Same as Finding 1.2 — zero-implementation cycles waste budget.

**Action**: Add as assertion in Cycle 5.2 (test both fresh-branch and existing-branch paths for submodule).

**Impact**: 38 → 37 cycles

---

## 2. Dependency Ordering (3 found, 1 critical)

**Definition**: Cycles that reference structures not yet created. Executing model must either create them ad-hoc (scope creep) or mock them (implementation coupling). Both produce fragile GREEN implementations.

### Finding 2.1: Missing jobs.md Auto-Resolve (**Critical**)

**Location**: Phase 7 (conflict handling cycles)
**Problem**:
- Design line 159 explicitly specifies: `agents/jobs.md conflict: Keep ours with warning: git checkout --ours agents/jobs.md && git add agents/jobs.md`
- Phase 7 cycles cover: agent-core (7.8), session.md (7.9), learnings.md (7.10), source file abort (7.11)
- **No cycle handles jobs.md**

During execution, a jobs.md conflict falls through to Cycle 7.11 (source file abort), aborting the merge for a case the design says should auto-resolve.

**Grounding**: [Fan et al., 2025](https://arxiv.org/html/2505.09027v1) — "API Call Mismatch" (Type C) errors when executing against structures that don't match expected state. Missing jobs.md handler = wrong conflict resolution strategy.

**Action**: Add jobs.md auto-resolve cycle between 7.10 and 7.11:
- Simple: `git checkout --ours agents/jobs.md && git add agents/jobs.md`
- Same pattern as 7.8 (known-file auto-resolve)
- Or: merge into 7.8 as parametrized "known-file auto-resolve" covering both agent-core and jobs.md

**Impact**: 37 → 38 cycles (adds 1 cycle)

**Severity**: High — this will cause merge failures in production for a case the design explicitly handles.

---

### Finding 2.2: Test File Organization Drift from Design

**Location**: Phase files 1-7
**Problem**:
- Design specifies: `test_worktree_path.py`, `test_sandbox_registration.py`, `test_focus_session.py`, `test_worktree_rm.py`, `test_worktree_merge.py`
- Runbook outline preserved these file names
- All expanded phase files consolidated to `test_worktree_cli.py` without documented rationale
- Only Phase 5 preserves design intent (`test_worktree_new.py`)

**Status**: Already fixed by tdd-plan-reviewer (runbook-final-review.md lines 169-174)

**Impact**: Medium — contradicts design decision, but tdd-plan-reviewer applied pragmatic consolidation based on existing file discovery

---

### Finding 2.3: Phase 4 → Phase 3 Dependency is Spurious

**Location**: Runbook outline dependency declarations
**Problem**:
- Outline declares "Phase 4 depends on Phase 3 (slug derivation used internally)"
- But `focus_session(task_name, session_md_path)` does not call `derive_slug()`
- Both are called independently by Phase 5's task mode
- Phase 4 has no actual dependency on Phase 3

**Grounding**: Incorrect dependency declarations mislead the orchestrator about parallelization opportunities.

**Action**: Correct Phase 4 dependency declaration to "None" or "Phase 1 (file structure only)."

**Impact**: Low (Phase 3 is 1 cycle, reordering gains nothing). Correctness fix for documentation.

---

## 3. Cycle Density (1 found)

**Definition**: Unnecessary cycles that dilute expansion quality and increase execution context pressure. Every cycle adds prompt length during expansion and execution.

### Finding 3.1: Cycle 4.3 — Reference Files Filtering

**Location**: Phase 4, Cycle 4.3
**Problem**:
- Structurally identical to Cycle 4.2 (Blockers filtering)
- Parse section, check relevance per entry, conditionally include
- <1 branch point difference (same filtering logic, different section header)

**Grounding**: [Mathews & Nagappan, 2024](https://arxiv.org/abs/2402.13521); [Fan et al., 2025](https://arxiv.org/html/2505.09027v1) — "Instruction loss in long prompts" where fidelity degrades as prompt grows. Trivial tests don't contribute signal.

**Action**: Merge into Cycle 4.2 as a single "section filtering" cycle that tests both Blockers and References. The RED phase uses parametrized test data with both section types.

**Impact**: 38 → 37 cycles (after jobs.md addition)

---

## 4. Checkpoint Spacing (1 found)

**Definition**: Distance between quality gates. Without intermediate checkpoints, haiku drift accumulates — pretraining bias overrides spec, errors compound.

### Finding 4.1: Gap Between Phase 5 and Phase 7 Checkpoints

**Location**: Phase 5 checkpoint (cycle ~23) → Phase 7 checkpoint (cycle ~40)
**Problem**:
- 17 cycles across 2 phases, exceeding >10 cycle threshold
- Phase 6 (`rm` command, 5 cycles, Medium complexity) has no checkpoint
- Phase 6 involves:
  - Worktree registration probing (subprocess output parsing)
  - Submodule-first removal ordering (critical correctness constraint — FR-5)
  - Filesystem cleanup (orphaned directories, empty containers)

These are exactly the conditions that warrant a checkpoint: complex data manipulation and an integration point (removal ordering composes probing + cleanup).

**Grounding**: [Fan et al., 2025](https://arxiv.org/html/2505.09027v1) — "Non-reasoning models understand semantics and write functioning code, but fail expectations" (functional code that violates spec). Checkpoints are the remediation loop.

Haiku drift across 17 uncheckpointed cycles risks pretraining-biased removal ordering (parent-first is intuitive/common, submodule-first is correct but counterintuitive).

**Action**: Add light checkpoint after Phase 6 (Fix + Functional). Validates removal ordering correctness before the large Phase 7 merge implementation.

**Impact**: 3 → 4 checkpoints (Post-Phase 2, Post-Phase 5, **Post-Phase 6**, Post-Phase 7)

---

## Recommendations

### Immediate Actions

**Priority 1 (Critical — blocks execution):**
1. Add jobs.md auto-resolve cycle (new Cycle 7.11, renumber 7.11 → 7.12)
   - Pattern: `git checkout --ours agents/jobs.md && git add agents/jobs.md`
   - Or merge with Cycle 7.8 as parametrized known-file handler

**Priority 2 (High — execution quality):**
2. Merge Cycle 1.1 into 1.2 as setup (eliminates vacuous registration test)
3. Merge Cycle 1.4 into 1.3 as parametrized assertions (eliminates vacuous sibling test)
4. Merge Cycle 5.3 into 5.2 as additional assertions (eliminates vacuous branch reuse test)
5. Merge Cycle 4.3 into 4.2 as parametrized section filtering (eliminates duplicate logic)
6. Add checkpoint after Phase 6 (light: Fix + Functional)

**Priority 3 (Low — documentation):**
7. Correct Phase 4 dependency declaration from "Phase 3" to "None"

### Cycle Count Impact

- Starting: 40 cycles
- Remove vacuous (1.1, 1.4, 5.3): -3
- Remove density (4.3): -1
- Add missing (jobs.md): +1
- **Final: 37 cycles**

### Checkpoint Impact

- Starting: 3 checkpoints (Post-Phase 2, Post-Phase 5, Post-Phase 7)
- Add: Post-Phase 6
- **Final: 4 checkpoints**

---

## Process Gap Analysis

### What tdd-plan-reviewer Caught
✓ File reference accuracy (3 critical issues — fixed)
✓ Prescriptive code detection (0 violations)
✓ RED/GREEN sequencing (0 violations)
✓ Prose test quality (excellent)

### What tdd-plan-reviewer Missed
✗ Vacuous cycles (3 found)
✗ Missing requirements coverage (jobs.md gap)
✗ Dependency ordering issues (2 found)
✗ Cycle density opportunities (1 found)
✗ Checkpoint spacing analysis (1 gap found)

### Root Cause

The tdd-plan-reviewer agent focuses on **TDD discipline** (prescriptive code, RED/GREEN violations). It does **not** apply the **LLM failure mode analysis** from `agents/decisions/runbook-review.md`.

The four-axis methodology (vacuous cycles, dependency ordering, cycle density, checkpoint spacing) requires a **separate review pass** with different detection criteria, grounded in LLM failure mode research:
- [Jiang et al., 2024](https://arxiv.org/html/2406.08731v1) — Vacuous test failure modes
- [Fan et al., 2025](https://arxiv.org/html/2505.09027v1) — Dependency ordering errors, instruction loss
- [Mathews & Nagappan, 2024](https://arxiv.org/abs/2402.13521) — TDD effectiveness, remediation loops

### Recommendation

**Two-tier review process:**
1. **tdd-plan-reviewer** (existing) — TDD discipline validation
2. **runbook-outline-review-agent** (needs enhancement) — LLM failure mode analysis

The runbook-outline-review-agent currently validates outline structure. It should be enhanced to apply the four-axis methodology from runbook-review.md:
- Detect vacuous cycles (RED satisfiable by scaffolding)
- Detect dependency inversions (forward references)
- Detect density opportunities (edge-case clusters, trivial cycles)
- Validate checkpoint spacing (>10 cycle gaps)

This creates defense-in-depth:
- **Outline review** catches semantic issues early (before expensive expansion)
- **Phase review** catches TDD discipline issues during expansion
- **Final review** validates cross-phase consistency

---

## Conclusion

The sonnet-based generation and validation process caught **syntax and format issues** but **not semantic issues** that lead to haiku execution failures.

Applying the LLM failure mode methodology from `agents/decisions/runbook-review.md` identified:
- 3 vacuous cycles (haiku produces degenerate code)
- 1 critical missing requirement (jobs.md auto-resolve gap)
- 1 checkpoint spacing gap (17-cycle unvalidated stretch)
- 1 cycle density opportunity (duplicate filtering logic)

**Impact**: 40 → 37 cycles (3 vacuous + 1 density - 1 missing), 3 → 4 checkpoints

**Next step**: Apply Priority 1-2 fixes before execution. The runbook is structurally sound (TDD discipline validated), but needs semantic corrections to prevent haiku execution failures.
