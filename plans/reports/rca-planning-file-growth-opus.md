# RCA: Planning Pipeline File Growth Gap (Opus Analysis)

**Date:** 2026-02-13
**Model:** opus
**Prior RCA:** `plans/reports/rca-planning-file-growth.md` (sonnet, same date)
**Runbook:** worktree-update (37 TDD cycles, 7 phases, 18 refactor reports)

---

## 1. Root Cause

The planning pipeline has a **projection-action gap**: the outline phase projected file growth correctly but failed to translate that projection into structural runbook changes (split phases, helper patterns).

This is not a missing-data problem. The worktree-update outline (`plans/worktree-update/runbook-outline.md` lines 228-232) contains an explicit growth projection:

```
File size tracking:
- cli.py currently ~386 lines
- Phase 5 adds ~100-150 lines (new command refactor + task mode)
- Phase 7 adds ~150-200 lines (merge ceremony)
- Estimate: ~636-736 lines after Phase 7 -> split required in Phase 7 cleanup cycle
```

The projection exists. It correctly identifies that cli.py would exceed limits. But three failures follow:

**F1: Wrong threshold.** The outline plans a split at 700 lines, but the 400-line limit triggers at commit time. The projection should compare against 400, not some vague "too big" threshold. At 386 starting lines with a 400-line limit, the file had only 14 lines of headroom — the first non-trivial phase would exceed it.

**F2: Deferred split.** The split is planned for "Phase 7 cleanup cycle" — after all growth has occurred. A split deferred to the end is functionally equivalent to no split. Every phase between the first limit-exceeding cycle (4.2, which hit 477 lines) and the planned Phase 7 split required reactive refactoring.

**F3: No review gate checks the projection.** Neither `runbook-outline-review-agent` nor `plan-reviewer` validates that the growth projection is consistent with the project's line limit. The outline review agent checks phase imbalance (>40% of work) but not projected file size against enforcement thresholds. The review-plan skill has zero mentions of file growth, file size, or line limits.

---

## 2. Contributing Factors

### C1: Phase 1.4 is structurally misplaced and underenforced

`agent-core/skills/runbook/SKILL.md` Phase 1.4 ("File Size Awareness") was added before worktree-update planning and specifies:

> For each item adding content: Note `(current: ~N lines, adding ~M)`. If `N + M > 350`: include a split step in the same phase.

This is per-item tracking during phase expansion — after the outline is frozen. Three problems:

1. **Wrong granularity.** Per-item tracking during expansion places cognitive load on the expanding agent (sonnet). The outline already has the right abstraction level (per-phase growth). Expanding agents don't have cumulative state across items.
2. **Not enforced.** No review agent checks Phase 1.4 compliance. The plan-reviewer skill (`agent-core/skills/review-plan/SKILL.md`) contains no criteria related to file growth.
3. **Mid-phase splits break coherence.** Inserting a split step mid-phase interleaves refactoring with feature work. Phase boundaries are natural split points; mid-phase splits are disruptive.

### C2: Outline review agent lacks file growth validation

`agent-core/agents/runbook-outline-review-agent.md` checks:
- Requirements coverage
- Phase structure and balance
- Dependency ordering
- Checkpoint frequency

It does not check:
- Whether growth projections exist for files modified by >10 cycles
- Whether projected totals are compared against the enforcement threshold (400)
- Whether split phases are placed before (not after) the threshold is reached

### C3: Runbook review axes don't include file growth

`agents/decisions/runbook-review.md` defines 4 axes: vacuity, dependency ordering, cycle density, checkpoint spacing. None address file growth. Checkpoint spacing is the closest analog (checks quality gate gaps by cycle count), but file growth is an independent concern — a 3-cycle phase can blow the limit if each cycle adds 20+ lines to a near-capacity file.

### C4: Formatter expansion not factored into projections

The outline projected raw line counts but did not account for formatter expansion. Black/ruff expands subprocess calls vertically (1 line to 7-8 lines per call). The worktree-update cli.py used 24 subprocess calls; formatter expansion accounts for approximately 100-150 lines of the final file size.

The `_git()` helper (introduced at Cycle 7.1) reduced this by 30%, but it was introduced as a reactive fix, not as a design-time pattern. The design document specified repeated `subprocess.run()` calls without recommending a helper.

### C5: Precommit is the only enforcement point

`scripts/check_line_limits.sh` checks `src/` and `tests/` Python files and `agents/decisions/` markdown files against a 400-line hard limit. This is binary pass/fail at commit time. There is:
- No warning threshold (e.g., warn at 350)
- No integration with planning artifacts
- No line count reporting during development (only at commit)

The enforcement architecture is **commit-gated only**, with no forward-looking validation.

---

## 3. Evidence

### Refactor escalation timeline

| Cycle | File | Lines | Over Limit | Agent Tier | Strategy |
|-------|------|-------|-----------|------------|----------|
| 1.1 | cli.py | ~150 | - | - | - |
| 4.2 | cli.py | 477 | +77 | Opus | Module split analysis |
| 4.2 | test_worktree_cli.py | 445 | +45 | Sonnet | Consolidation |
| 5.5 | cli.py | 421 | +21 | Sonnet | Helper extraction + deslop |
| 5.5 | test_worktree_new.py | 457 | +57 | Sonnet | Consolidation (457->331) |
| 5.6 | cli.py | ~400 | - | Sonnet | Deslop pass |
| 5.7 | cli.py | ~400 | - | Sonnet | Deslop pass |
| 6.1 | cli.py | 397 | - | Sonnet | Preventive refactor |
| 6.2 | cli.py | 422 | +22 | Sonnet | Helper extraction + deslop |
| 6.3 | cli.py | 401 | +1 | Sonnet | Docstrings, exceptions |
| 6.4 | cli.py | 406 | +6 | Sonnet | Pathlib, inline checks |
| 6.5 | cli.py | 403 | +3 | Sonnet | Redundant guards |
| 7.1 | cli.py | 430 | +30 | Sonnet | `_git()` helper + consolidation |
| 7.2 | cli.py | 448 | +48 | Opus | Merge validation consolidation |
| 7.6 | cli.py | ~400 | - | Sonnet | Deslop pass |
| 7.12 | cli.py | ~400 | - | Sonnet | Deslop pass |

18 refactor reports total. 2 opus escalations (architectural decisions required). 16 sonnet refactors.

### What the outline knew vs what it did

The outline had sufficient information to prevent this:

| Information | Available at Outline | Used for Split Planning |
|-------------|---------------------|------------------------|
| Current cli.py size: 386 lines | Yes (line 229) | No |
| 400-line enforcement limit | Known (precommit exists) | Not compared |
| Phase 5 growth: +100-150 lines | Yes (line 230) | No (split deferred to Phase 7) |
| Phase 7 growth: +150-200 lines | Yes (line 231) | Yes (but split placed after growth) |
| Formatter expansion factor | No | No |
| Helper pattern opportunity | No (design didn't prescribe) | No |

The outline projected 636-736 total lines, noted "split required," but placed the split at the end. With a 400-line limit, the split needed to occur before Phase 5 — the first phase that would push cli.py over 400 lines (386 + 100 = 486).

### Pipeline stage analysis

| Pipeline Stage | Checks File Growth? | Could Check? |
|----------------|---------------------|-------------|
| T1: Requirements -> Design | No | No (too early) |
| T2: Design -> Outline | **Projection exists** but wrong threshold | Yes — compare against 400 |
| T3: Outline -> Phase files | Phase 1.4 exists but unenforced | Yes — per-phase cumulative check |
| T4: Phase files -> Runbook | No | Possible but late |
| T5: Runbook -> Step artifacts | No (prepare-runbook.py) | No (wrong abstraction) |
| T6: Steps -> Implementation | Precommit (reactive) | Already does (but too late) |

The right intervention point is **T2** (outline generation/review) with validation at **T3** (phase expansion review).

---

## 4. Proposed Fixes

### Fix 1: Outline growth validation gate (primary)

**Location:** `agent-core/agents/runbook-outline-review-agent.md`

Add a review criterion: when the outline contains a growth projection, validate:
- Projected totals compared against 400-line limit (not vague "too big")
- Split phases placed **before** the first phase that exceeds 350 lines cumulative
- Each post-split target file projected at <300 lines (50% margin for drift)

When the outline lacks a growth projection but has >10 cycles modifying the same file, flag as Major issue.

**Why outline review:** This is the earliest review gate with sufficient information (file sizes, cycle counts, complexity). The outline-review-agent already checks phase balance; growth projection is an analogous structural concern.

### Fix 2: Correct Phase 1.4 or replace it (secondary)

**Option A:** Move Phase 1.4 guidance to Phase 0.75 (outline generation). Replace per-item tracking with per-phase projection:

```
For each target file:
1. Current size from Glob/wc -l
2. Sum estimated growth across all phases modifying this file
3. If current + growth > 350: insert split phase at earliest boundary
4. Apply 1.2x formatter overhead factor
```

**Option B:** Delete Phase 1.4 entirely. If Fix 1 (outline review gate) catches growth issues, Phase 1.4 is redundant — it tries to catch the same problem later, with more cognitive load, and without enforcement.

Recommend Option B. The outline is the right abstraction level for growth planning. Phase expansion should not carry this concern.

### Fix 3: Add growth axis to runbook-review.md (tertiary)

**Location:** `agents/decisions/runbook-review.md`

Add a fifth review axis ("File Growth Projection") alongside the existing four. Detection criteria:
- Outline projects file growth beyond 350 lines with no split phase
- Split phase placed after the phase that first exceeds the limit
- Projection does not account for formatter expansion (no overhead factor)

This provides documented criteria for both human reviewers and automated review agents.

### Fix 4: Prescribe helper patterns in design (optional)

When design specifies >5 repeated subprocess calls to the same command, recommend a private helper in the design phase. The `_git()` helper reduced cli.py by 30% (477 to 336 lines). If prescribed at design time, the file would never have exceeded 400 lines.

This is a design-phase pattern, not a planning concern. But it eliminates a major contributor to formatter-driven growth.

---

## 5. Trade-off Analysis

### Planning-time projection vs execution-time adaptation

| Dimension | Planning-time (Fixes 1-3) | Execution-time (current) |
|-----------|---------------------------|--------------------------|
| **When** | Outline review (before expansion) | Precommit (after implementation) |
| **Cost of failure** | Revise outline (minutes) | Refactor code (hours, opus tier) |
| **Accuracy** | Heuristic (may be off by 20-30%) | Exact (measured at commit) |
| **Cognitive load** | Planner (once per outline) | Executor (every violating cycle) |
| **Split quality** | Phase boundary (natural) | Mid-cycle (disruptive) |
| **Review integration** | Outline-review-agent (existing gate) | None (precommit is pass/fail) |

Planning-time wins on all dimensions except accuracy. But 20-30% inaccuracy with a 50-line margin (split at 350, limit at 400) is acceptable — the consequence of a missed projection is a single refactor, not 18.

### Single-point vs multi-point enforcement

| Approach | Failure mode | Impact |
|----------|-------------|--------|
| Outline only (Fix 1) | Projection wrong or missing | Precommit catches at commit time (existing backstop) |
| Outline + review axis (Fixes 1+3) | Same, but documented criteria | Reviewers catch in review pass |
| Outline + Phase 1.4 + review (all) | Redundant, cognitive overhead | Higher compliance cost, diminishing returns |

Recommend Fixes 1+3 (outline review gate + review axis). Fix 2 Option B (delete Phase 1.4) simplifies by removing the redundant mid-pipeline check.

### Helper pattern prescription vs organic discovery

| Approach | Cost | Benefit |
|----------|------|---------|
| Prescribe in design (Fix 4) | Design phase overhead | Prevents 30% of formatter-driven growth |
| Discover during execution (current) | 18 refactor reports | None — pure waste |

Fix 4 has low cost (one design guideline) and high benefit (eliminates the largest contributor to growth). The `_git()` helper is a general pattern applicable to any module with repeated subprocess calls.

---

## 6. Scope Assessment

### Files requiring changes

**Fix 1 (outline review gate):**
- `agent-core/agents/runbook-outline-review-agent.md` — add growth projection validation criteria
- ~15-20 lines added to review criteria section
- Tier 1 (direct edit, prose artifact)

**Fix 2B (delete Phase 1.4):**
- `agent-core/skills/runbook/SKILL.md` — remove Phase 1.4 section (lines 504-513)
- Move growth projection guidance to Phase 0.75 (outline generation) or remove entirely if Fix 1 covers it
- ~10 lines removed, ~5-10 lines added to Phase 0.75
- Tier 1 (direct edit)

**Fix 3 (review axis):**
- `agents/decisions/runbook-review.md` — add File Growth Projection axis
- ~15-20 lines added
- Tier 1 (direct edit, follows existing axis structure)

**Fix 4 (helper pattern):**
- Design skill or design guidance document — add subprocess helper prescription
- ~10 lines added
- Tier 1 (direct edit, advisory guidance)

**Total scope:** 4 files, ~50-60 lines of changes, all Tier 1 direct edits. No code changes, no tests required (all prose artifacts).

### Relationship to prior RCA

The sonnet RCA (`plans/reports/rca-planning-file-growth.md`) identifies the same root cause but frames it as "missing projection." This opus analysis corrects that: the projection existed but had three failures (wrong threshold, deferred split, no review validation). The distinction matters because:

- "Missing projection" suggests adding a data-gathering step
- "Projection-action gap" suggests adding validation at the existing review gate

The fixes overlap substantially. This report's Fix 1 corresponds to the sonnet report's Fix 2 but targets the outline review agent (the right enforcement point) rather than a new review axis alone. Fix 2B (delete Phase 1.4) is stronger than the sonnet report's Fix 3 (move Phase 1.4) because it removes redundancy rather than relocating it.

---

## 8. Deepening

### 8.1: Measured Lines per Cycle

**Method:** Measured cli.py line count at each cycle commit from git history, computing raw lines added (before any refactoring) relative to the post-refactor baseline of the previous cycle.

#### Raw measurements (cli.py)

| Cycle | Pre-cycle | Post-cycle | Raw Delta | Notes |
|-------|-----------|------------|-----------|-------|
| 1.1 | 385 | 373 | -12 | Refactored existing code while adding wt_path() |
| 1.2 | 373 | 373 | 0 | Test-only changes |
| 1.3 | 373 | 376 | +3 | |
| 1.4 | 376 | 380 | +4 | |
| 2.1 | 380 | 396 | +16 | |
| 2.2 | 396 | 383 | -13 | Refactored while adding |
| 2.3 | 383 | 384 | +1 | |
| 2.4 | 384 | 387 | +3 | |
| 3.1 | 387 | 393 | +6 | |
| 4.1 | 393 | 421 | +28 | |
| 4.2 | 421 | 477 | +56 | **First limit breach** (+77 over 400) |
| *refactor* | 477 | 336 | -141 | _git() helper + deslop (412→336) |
| 4.3 | 336 | 336 | 0 | Error handling only |
| 5.1 | 336 | 345 | +9 | |
| 5.2 | 345 | 356 | +11 | |
| 5.3 | 356 | 362 | +6 | |
| 5.4 | 362 | 400 | +38 | At limit exactly |
| 5.5 | 400 | 421 | +21 | **Over limit** (+21), refactored to 393 |
| 5.6 | 393 | 401 | +8 | Refactored to 400 |
| 5.7 | 400 | 404 | +4 | Refactored to 400 |
| 6.1 | 400 | 414 | +14 | Refactored to 398 |
| 6.2 | 398 | 422 | +24 | Refactored to 400 |
| 6.3 | 400 | 401 | +1 | Refactored to 397 |
| 6.4 | 397 | 406 | +9 | Refactored to 400 |
| 6.5 | 400 | 403 | +3 | Refactored to 397 |
| 7.1 | 397 | 430 | +33 | Refactored to 399 |
| 7.2 | 399 | 448 | +49 | Module split → 365 |
| 7.3 | 365 | 386 | +21 | |

#### Aggregated by phase and complexity

| Phase | Complexity | Cycles | Total Raw Added | Mean/Cycle | Range |
|-------|-----------|--------|-----------------|------------|-------|
| 1 | Medium | 4 | 7* | 2 | -12 to +4 |
| 2 | Medium | 4 | 7* | 2 | -13 to +16 |
| 3 | Low | 1 | 6 | 6 | 6 |
| 4 | Medium | 3 | 84 | 28 | 0 to +56 |
| 5 | High | 7 | 97 | 14 | +4 to +38 |
| 6 | Medium | 5 | 51 | 10 | +1 to +24 |
| 7 | High | 3** | 103 | 34 | +21 to +49 |

*Phase 1 and 2 include cycles that refactored while adding, making deltas misleadingly low.
**Only 3 of 13 Phase 7 cycles measured (module split at 7.2 changed the target file).

#### Comparison with sonnet's heuristic estimates

The sonnet RCA proposed heuristics: High=42 lines/cycle (32-56), Medium=24 (21-28), Low=10 (1-16).

| Complexity | Sonnet Heuristic | Measured Mean | Measured Range | Assessment |
|-----------|-----------------|---------------|----------------|------------|
| High | 42 | 14 (Phase 5), 34 (Phase 7) | 4-49 | **Wildly variable.** Phase 5 is half the heuristic; Phase 7 is close. |
| Medium | 24 | 2 (P1), 2 (P2), 28 (P4), 10 (P6) | -13 to +56 | **4x range.** Phase 4 matches, Phases 1/2 are 12x below. |
| Low | 10 | 6 | 6 | Reasonable. |

**Key finding: Growth rate varies enormously by what the cycle does, not by complexity label.** Phases 1-2 add tiny amounts to cli.py because they add helper functions (compact). Phase 4 adds large amounts because `focus_session()` is a parsing function with string manipulation (verbose). Phase 7 adds large amounts because merge ceremony has many git operations (formatter-expanded).

The complexity label (Low/Medium/High) is a poor predictor of lines-per-cycle. The actual predictor is the **nature of the code being added**: parsing/string manipulation and subprocess-heavy code grows fast; helper functions and configuration logic grows slowly.

#### Prediction accuracy of the outline

The outline projected:
- Phase 5: +100-150 lines → Measured: +97 raw (before refactoring). **Accurate.**
- Phase 7: +150-200 lines → Measured: +103 in first 3 of 13 cycles. Extrapolating 103/3 * 13 = ~446 lines. **Substantially underestimated.**
- Total: 636-736 → If Phase 7 extrapolation holds: 386 + 97 + 51 + 446 = 980. **Outline underestimated by ~33%.**

The outline's projection was in the right order of magnitude but consistently underestimated — especially for Phase 7, which had the most subprocess-heavy code. The 700-line split threshold would itself have been breached.

### 8.2: Execution-Time Enforcement Analysis

The current execution-time flow:

```
tdd-task runs cycle → `just precommit` → line limit fails →
  tdd-task STOPs, reports "quality-check: warnings found" →
  orchestrator delegates to sonnet refactor agent →
  refactor agent reduces lines → commits → resume
```

This loop executed 18 times in worktree-update. Each iteration costs:
- Orchestrator context: ~2000 tokens (stop handling, delegation)
- Refactor agent: 5000-20000 tokens (read, analyze, edit, verify)
- Elapsed time: 3-8 minutes per refactor

**Could execution-time enforcement be proactive instead of reactive?**

#### Option A: tdd-task proactive split at 380 lines

Modify tdd-task agent to check file size before committing:
```
After GREEN, before REFACTOR:
  wc -l <modified files>
  If any file > 380: trigger proactive split
```

**Advantages:**
- Exact measurement (no heuristic error)
- Prevents the violation before it occurs
- No planning-phase changes needed
- Split decision made with full implementation context

**Problems:**
1. **tdd-task is haiku.** Haiku cannot make good split decisions — it doesn't know module boundaries, public API surfaces, or cohesion criteria. The 7.2 refactor report shows that even sonnet needed opus escalation for architectural splits. Mechanical file splitting (top half / bottom half) creates worse code than no split at all.

2. **Split mid-cycle is disruptive.** A cycle that adds 40 lines to a 370-line file triggers a split between RED and GREEN — or between GREEN and the next cycle. The split changes file paths, imports, and test references. Subsequent cycles in the same phase reference the old file path.

3. **No forward visibility.** Execution-time enforcement sees only the current state. It cannot say "this file will be 500 lines after 3 more cycles, so split now to create headroom." It reacts at 380 every time, potentially splitting files that were about to shrink via planned refactoring.

4. **Frequency.** If the file oscillates around 380-400 (as cli.py did through Phases 5-6), the agent triggers a split check nearly every cycle. This is the behavior observed: 11 of 18 refactors were for overages of 1-24 lines.

#### Option B: Orchestrator-level file size monitoring

The orchestrator checks file sizes between steps and inserts split phases dynamically.

**Advantages:**
- Sonnet-tier reasoning for split decisions
- Can plan ahead (3-4 cycles) based on remaining step files
- Natural breakpoint between cycles (not mid-cycle)

**Problems:**
1. **Orchestrator context bloat.** The orchestrator already manages step dispatch, error handling, checkpoint scheduling. Adding file size monitoring and dynamic split insertion increases cognitive load at the weakest point (long orchestration sessions lose fidelity).

2. **Weak orchestrator pattern violation.** The orchestrate skill is designed for mechanical dispatch, not dynamic plan modification. Inserting a split phase requires modifying the step execution order — a planning decision, not an execution decision.

3. **Still reactive.** Even with monitoring, the orchestrator discovers the problem after the code exists. The split still happens mid-runbook, disrupting subsequent cycles.

#### Option C: Hybrid — planning-time projection with execution-time backstop

Planning time (outline review): Project file growth, insert split phases at boundaries when projected total > 350.

Execution time (tdd-task enhancement): After GREEN, if any modified file > 380 lines, report `"file-size-warning: <file> at <N> lines"` alongside the normal cycle status. The orchestrator logs the warning but does NOT auto-split. The warning becomes input for the next checkpoint review.

**Advantages:**
- Planning prevents most violations (14-line headroom insufficient, but 50-line headroom with 350 threshold sufficient)
- Execution catches projection errors without disruptive mid-cycle splits
- Warning-only approach avoids haiku making split decisions
- Checkpoint review (sonnet) makes the split decision with full context

**Disadvantages:**
- Two systems to maintain
- Warning can be ignored (soft enforcement)

#### Assessment

| Approach | Prevents violations? | Split quality | Complexity | Tractability |
|----------|---------------------|--------------|------------|-------------|
| Planning-only (Fixes 1-3) | Most (heuristic error remains) | High (phase boundaries) | Low (prose edits) | High |
| Execution-proactive (Option A) | All (exact measurement) | Low (haiku splits mid-cycle) | Medium (agent changes) | Low — haiku can't split well |
| Orchestrator-monitoring (Option B) | All (exact measurement) | Medium (between cycles) | High (orchestrator redesign) | Low — violates weak orchestrator |
| Hybrid (Option C) | Most + catch residual | High (checkpoint review) | Medium (warning + prose) | **Highest** |

**Recommendation: Hybrid (Option C).** Planning-time projection handles the strategic problem (where to split). Execution-time warning handles the tactical residual (projection was wrong). Neither system needs to make split decisions alone — the checkpoint review agent (sonnet, with full context) makes the actual split decision when a warning accumulates.

The key insight is that **measurement is easy but splitting is hard.** The tdd-task agent can trivially measure file size (one `wc -l` call). But deciding *how* to split requires understanding module boundaries, public APIs, import graphs, and test dependencies — cognitive work that haiku cannot do and that mid-cycle execution cannot plan for. Planning-time projection places the split decision where the intelligence and context exist (outline review, sonnet/opus). Execution-time measurement catches the residual without attempting the cognitive work.

### 8.3: Deeper WHY — Threshold Error and Deferred Split

#### Why 700 instead of 400?

The outline (line 270) says: "Module split guidance (if cli.py >700 lines after Phase 7)." The 400-line limit has existed since 2025-12-18. The outline was created 2026-02-12. The planner had access to:
- `scripts/check_line_limits.sh` (400-line limit, in repository)
- `just line-limits` recipe (run as part of `just precommit`)
- Prior refactor history (worktree-skill had similar issues)

This is **not a knowledge gap.** The planner knew the 400-line limit exists — the outline's "File size tracking" section explicitly notes current size (386 lines) and projects growth. A planner unaware of the limit would not track file sizes at all.

This is an **attention gap with a specific mechanism: the outline conflated two different thresholds.**

The 400-line limit governs individual files at commit time. The 700-line threshold in the outline is a **module split** threshold — the point at which a single module should be decomposed into multiple modules. These are different concerns:

- 400 lines: precommit hard limit (enforced, per-file)
- 700 lines: architectural split point (judgment-based, per-module)

The planner was thinking about **when to split the module** (an architectural question) rather than **when individual files exceed the commit limit** (a mechanical constraint). The outline's "File size tracking" section is in the Expansion Guidance, next to "Module split guidance" — both are framed as architectural guidance for the expander, not as constraint satisfaction against the precommit limit.

**Evidence for conflation:** The outline projects 636-736 total lines and says "split required in Phase 7 cleanup cycle." If the planner were thinking about the 400-line limit, the split would be needed at Phase 4 (where 386+84=470 > 400), not Phase 7. The split timing only makes sense if the planner is thinking "when does the module become too big to maintain" (700), not "when does the file exceed the precommit limit" (400).

**Contributing factor:** The runbook skill (SKILL.md Phase 1.4) uses 350 as its threshold — the correct number for the precommit limit with margin. But the outline planner used 700. Phase 1.4 was not consulted or enforced during outline generation, and the outline review agent didn't cross-check the projection against either threshold.

#### Why was the split deferred to Phase 7?

The deferral was a **deliberate choice driven by a reasonable but incorrect heuristic: split after functionality is complete.**

The outline's Expansion Guidance (line 270) says: "Module split guidance (if cli.py >700 lines **after Phase 7**)." This places the split after the last feature phase (7) and before the artifact phase (8). The rationale is clear: don't split a module while you're still adding features to it, because each split changes file paths and imports that subsequent cycles reference.

This is a legitimate concern. An early split at Phase 4 would mean:
- Phase 5 cycles (7 cycles) would target the new module structure
- Phase 6 cycles (5 cycles) would target the new module structure
- Phase 7 cycles (13 cycles) would target the new module structure
- Each cycle's file references in the runbook would need updating

But the heuristic "split after all features" only works when the file can absorb all features without exceeding the hard limit. With a 400-line limit and 386 starting lines, this was impossible — the outline's own projection showed the file growing to 636-736 lines.

**The deferral is a planning anti-pattern: optimizing for executor convenience (stable file paths) while violating a hard constraint (400-line limit).** The convenience can be achieved differently — split early and update runbook references — but the constraint cannot be deferred.

**Root of the anti-pattern:** The planner treated the 400-line limit as a soft preference ("split when too big") rather than a hard constraint ("must not exceed at any commit"). This is the same conflation identified above: architectural judgment (700) vs mechanical constraint (400).

#### What does this mean for the fix?

The threshold error and the deferral share a single cause: **the planner did not treat the 400-line precommit limit as a hard constraint during outline construction.**

This means:
- "Communicate the limit better" is **necessary but insufficient.** The limit was already known; the problem is that it wasn't applied to the projection.
- "Enforce the limit mechanically" is **the correct fix** — the outline review agent should compare projected file sizes against the enforcement threshold and flag violations, regardless of whether the planner remembers the threshold.

The fix is structural (review gate validation), not informational (documenting the limit in more places). The limit is already documented in `scripts/check_line_limits.sh`, the justfile, and SKILL.md Phase 1.4. More documentation would not have prevented the conflation. A mechanical check at outline review — "projection exceeds 400 at Phase N, split must precede Phase N" — would have.

This also reinforces the hybrid approach from section 8.2. Planning-time projection catches the strategic error (wrong threshold, deferred split) through mechanical validation. Execution-time warning catches the tactical residual (projection underestimated by 33%). Neither alone is sufficient: planning without validation repeats the conflation; execution without planning makes every violation a surprise.

---

## 9. Conclusion

The root cause is a **projection-action gap** driven by **threshold conflation**: the planner confused the architectural split threshold (~700 lines, judgment-based) with the precommit enforcement threshold (400 lines, mechanical). The projection existed, projected accurately for Phase 5 and underestimated Phase 7 by ~33%, but compared against the wrong number and deferred the split to a point where 25 cycles of violations had already occurred.

**Measured growth rates** vary enormously by code nature (2-56 lines/cycle), not by complexity label. The complexity label is a poor predictor; subprocess-heavy and parsing code grows fast, helper functions grow slowly. Heuristic prediction at planning time will always have significant error bars.

**Recommended approach: Hybrid (planning + execution-time warning).**
- Planning-time: Outline review agent mechanically validates projected file sizes against the 400-line enforcement threshold. Split phases placed before the first phase exceeding 350 cumulative. This catches the strategic error (wrong threshold, deferred split).
- Execution-time: tdd-task reports file size warnings after GREEN phase when any modified file exceeds 380 lines. Checkpoint review (sonnet) decides whether and how to split. This catches projection errors without requiring haiku to make split decisions.
- Phase 1.4 deleted (redundant with outline-level enforcement).
- Helper patterns prescribed at design time to reduce formatter-driven growth.

**The fix is structural (mechanical validation), not informational (more documentation).** The limit was already known and documented in multiple places. The planner conflated two different thresholds because no review gate cross-checked the projection against the enforcement limit. Adding that mechanical check at outline review is the primary fix.
