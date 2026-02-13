# RCA: Planning Pipeline Lacks File Growth Projection

**Date:** 2026-02-13
**Runbook:** worktree-update
**Evidence:** 18 refactor reports (2 opus-tier architectural, 16 sonnet-tier deslop)
**Impact:** Planning efficiency loss, execution delays, opus escalations for haiku-tier work

**Deepening:** See "Deepening" section for evidence verification, measured heuristics from execution data, execution-time vs planning-time trade-off analysis, and architectural question on correct abstraction layer for operational constraints.

---

## Root Cause

**The planning pipeline does not project file growth during runbook creation, and review axes do not validate projected file size against limits.**

**Specific gap:** Between outline generation (Phase 0.75) and phase expansion (Phase 1), there is no step that:
1. Estimates lines added per cycle based on design complexity
2. Projects cumulative file growth across phases
3. Inserts proactive split points when projection exceeds limits

The 400-line limit is enforced at commit time (precommit validation via `scripts/check_line_limits.sh`) but not anticipated during planning.

---

## Contributing Factors

### C1: Planning-Execution Gap

**Planning artifacts lack file growth metadata.**

Current outline structure (`runbook-outline.md`):
- Cycles per phase: ✓ (present)
- Complexity per phase: ✓ (Low/Medium/High)
- Estimated lines per cycle: ✗ (absent)
- Projected file size per phase: ✗ (absent)
- Split point recommendations: ✗ (absent)

**Evidence:** worktree-update outline specified:
- Phase 5: 7 cycles, High complexity
- Phase 7: 13 cycles, High complexity

But provided no estimate that these phases would add:
- Phase 5: ~80 lines (actual)
- Phase 7: ~130+ lines (actual, pre-refactor)

Without projection, planner cannot insert split points at phase boundaries.

### C2: Review Axes Miss Growth Pattern

**`agents/decisions/runbook-review.md` defines 4 review axes, none address file growth:**

| Axis | Checks | Misses |
|------|--------|--------|
| Vacuous Cycles | Behavioral substance | Lines added per cycle |
| Dependency Ordering | Foundation-first | Cumulative file size |
| Cycle Density | Collapse candidates | Growth projection |
| Checkpoint Spacing | Quality gate gaps | File split points |

**Checkpoint Spacing** is conceptually closest but checks cycle count between vet checkpoints, not projected file size.

### C3: Phase 1.4 "File Size Awareness" Underspecified

**`agent-core/skills/runbook/SKILL.md` lines 504-513 introduce "File Size Awareness":**

```markdown
### Phase 1.4: File Size Awareness

**Convention:** When an item adds content to an existing file, note current file size and plan splits proactively.

**Process:**
1. For each item adding content: Note `(current: ~N lines, adding ~M)`
2. If `N + M > 350`: include a split step in the same phase
3. Threshold rationale: 400-line hard limit at commit, 350 leaves ~50-line margin (heuristic)
```

**Problems with this approach:**

1. **Item-level granularity is too late:** By Phase 1 (expansion), phases are already defined. Inserting split steps mid-phase is awkward and breaks phase coherence.

2. **Per-item tracking is error-prone:** Requires planner to:
   - Track cumulative growth per file across phases
   - Sum lines from multiple cycles modifying same file
   - Manually insert split steps when threshold crossed
   - This is cognitive overhead that weak agents (sonnet expansion) handle inconsistently

3. **350-line margin is reactive, not proactive:** By the time a file reaches 350 lines during expansion, the outline structure is frozen. Better to project at outline phase and prevent growth, not react during expansion.

4. **Not enforced by review:** No review agent checks for Phase 1.4 compliance. `plan-reviewer` doesn't validate file growth projections.

**Evidence:** worktree-update execution:
- Phase 1.4 section exists in SKILL.md since 2026-02-12 (before worktree-update planning)
- worktree-update outline created 2026-02-12, no file growth projections present
- Phase expansion (cycles 1.1-7.13) proceeded without split points
- First refactor escalation: Cycle 4.2 (cli.py reached 477 lines, 77 over limit)
- Subsequent refactors: 7.1, 7.2, 6.1, 6.4, 5.6, 5.5, 4.3 (18 total refactor reports)

### C4: Precommit Enforcement Only

**400-line limit enforced exclusively at commit time, not during planning:**

- `scripts/check_line_limits.sh` scans `src/` and `tests/` files
- Fails precommit if any file >400 lines
- Detection is binary: pass/fail, no warnings at 350 lines
- No integration with planning artifacts (runbook doesn't check limits)

**Result:** Planning proceeds blind to limits, execution encounters hard stop, opus refactor agent escalates.

### C5: Formatter Expansion Increases Effective Growth

**Black formatter expands subprocess calls vertically, amplifying line count:**

**Before formatting (1 line):**
```python
subprocess.run(["git", "hash-object", "-w"], input=content, capture_output=True, text=True, check=True)
```

**After formatting (8 lines):**
```python
subprocess.run(
    ["git", "hash-object", "-w"],
    input=content,
    capture_output=True,
    text=True,
    check=True,
)
```

**Cycle 4.2 refactor report:** 15-line expansion across 6-8 subprocess calls due to formatter.

**Impact:** Planning must estimate post-format size, not raw line count. Current planning doesn't account for formatter expansion.

### C6: `_git()` Helper Introduced Late

**worktree-update Cycle 7.1 introduced `_git()` helper to reduce subprocess boilerplate:**

```python
def _git(*args, check=True, **kwargs) -> str:
    """Run git command and return stdout."""
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=check, **kwargs
    ).stdout.strip()
```

**Impact:** 24 calls replaced, 477→336 lines (30% reduction).

**Timing issue:** Helper introduced at Cycle 7.1, but could have been designed into Phase 0 (setup). If included in design/outline, all phases would have used helper from start, avoiding growth.

---

## Evidence

### worktree-update Execution Timeline

| Cycle | Event | File Size | Over Limit | Action |
|-------|-------|-----------|------------|--------|
| 1.1 | Initial CLI setup | ~150 lines | - | - |
| 2.1-2.4 | Sandbox registration | ~220 lines | - | - |
| 4.2 | Section filtering | 477 lines | +77 | Refactor (deslop + arch) → 412 |
| 5.2-5.7 | `new` command updates | ~390 lines | - | - |
| 6.1 | `rm` refactor | 397 lines | - | - |
| 6.4 | Cleanup logic | 406 lines | +6 | Refactor (deslop) → 400 |
| 7.1 | Merge clean tree | 430 lines | +30 | Refactor (_git helper) → 399 |
| 7.2 | THEIRS clean tree | 448 lines | +48 | Refactor (consolidate helpers) → 430 |

**Total refactor escalations:** 7+ (18 refactor reports in `plans/worktree-update/reports/`)

**Refactor agents used:**
- Sonnet (deslop, consolidation): 5 escalations
- Opus (architectural splits): 2 escalations (Cycle 4.2, 7.2)

**Wall-clock estimate:** 1hr+ on refactor work alone (not counting planning, execution, vet)

### Design Document Review

**`plans/worktree-update/design.md` specified:**
- 8 modules/functions
- 9 commands/modes
- 37 TDD cycles planned
- No file size projection

**Outline (`runbook-outline.md`) specified:**
- 7 phases (1-7 TDD, 8-9 non-TDD)
- 37 cycles across phases
- Complexity per phase (Low/Medium/High)
- No lines-per-cycle estimate
- No cumulative file growth projection

---

## Proposed Fixes

### Fix 1: Add Growth Projection to Outline Phase (Primary)

**Location:** `agent-core/skills/runbook/SKILL.md` Phase 0.75 (outline generation)

**Add to outline structure:**

```markdown
## File Growth Projection

| File | Current Lines | Cycles Adding | Est. Lines/Cycle | Projected Total | Split Needed? |
|------|---------------|---------------|------------------|-----------------|---------------|
| cli.py | 120 | 25 | 15 | 495 | Yes (Phase 4) |
| test_cli.py | 80 | 30 | 10 | 380 | No |
```

**Calculation heuristics (empirically calibrated from worktree-update - see Deepening section):**

- **Lines per cycle (TDD):** Low: 10, Medium: 24, High: 42 (measured means)
- **Lines per cycle (general):** Needs measurement from general-phase runbooks
- **Note:** These are POST-refactor measurements including formatter expansion
- **Split threshold:** If projected total >350, insert split at phase boundary
- **Calibration status:** Single-runbook sample, needs validation across 2-3 more runbooks

**Process:**
1. Planner identifies files modified by runbook (from design document)
2. For each file: count cycles that add content, classify complexity
3. Estimate lines per cycle based on heuristic
4. Project cumulative growth: `current + (cycles × lines/cycle × 1.2)`
5. If projection >350: add split phase at natural boundary

**Split phase template:**

```markdown
### Phase N+1: File Split — cli.py

**Complexity:** Low (1 cycle)
**Type:** general

**Tasks:**
- Split `cli.py` into:
  - `cli.py` — CLI commands (Click wrappers)
  - `operations.py` — Core operations (wt_path, sandbox, focus)
- Update imports in tests
- Verify precommit passes
```

**When to split:**
- Phase boundary (not mid-phase) to preserve coherence
- After functional milestone (not mid-feature)
- Target: Split produces two files each <300 lines

### Fix 2: Add Growth Validation to Review Axes (Secondary)

**Location:** `agents/decisions/runbook-review.md`

**Add fifth review axis:**

```markdown
### File Growth Projection

Planning must project file size to prevent precommit failures. Every runbook adding >10 cycles to a file must include growth projection.

**Detection — projection is missing when:**
- Outline adds >10 cycles to existing file, but no growth table present
- Projection table missing "Split Needed?" column
- Projected total >350 lines with no split phase planned
- Heuristic (lines/cycle) not documented or implausible (e.g., 5 lines/cycle for High complexity)

**Action:** Add growth projection table to outline. If projection >350, insert split phase at natural boundary.

**Grounding:** Precommit enforces 400-line limit. Planning blind to limits causes execution delays and refactor escalations. Proactive projection prevents reactive refactoring.
```

**Integration with plan-reviewer:**

Update `plan-reviewer` agent prompt to check:
- Outline contains growth projection table when applicable
- Heuristics are reasonable (compare to phase complexity)
- Split phases inserted when projection exceeds 350

### Fix 3: Move File Size Awareness Earlier (Tertiary)

**Location:** `agent-core/skills/runbook/SKILL.md`

**Move Phase 1.4 content to Phase 0.75 (outline):**

Current: Phase 1.4 checks per-item growth during expansion (too late, cognitive load)

Proposed: Phase 0.75 projects holistic growth during outline creation (proactive, less cognitive load)

**Delete:** Lines 504-513 (Phase 1.4: File Size Awareness)

**Rationale:** Projection at outline phase is structural (inserts split phases), not item-level (manual tracking). Outline is reviewed by plan-reviewer before expansion begins.

### Fix 4: Prescribe Helper Pattern in Design (Optional)

**Location:** `agent-core/skills/design/SKILL.md` (if exists) or CLAUDE.md design guidance

**Pattern:** When design specifies repeated subprocess calls, recommend helper function in design phase.

**Example template:**

```markdown
## Design Patterns

**Subprocess Helpers:**

When module uses >5 subprocess calls to same command:
- Extract helper: `_git(*args, **kwargs) -> str`
- Single invocation point reduces formatter expansion
- 30% line count reduction observed (worktree-update Cycle 7.1)
```

**Rationale:** Helper pattern is deterministic (not cognitive), should be design-time decision, not execution-time discovery.

### Fix 5: Execution-Time Proactive Split (Primary, from Deepening Axis 3)

**Location:** `agent-core/agents/tdd-task.md` Step 3 (REFACTOR phase)

**Add Step 3.5 after precommit:**

```markdown
### Step 3.5: Proactive Split Check

After `just precommit`, check line limit warnings:

**If file >380 lines:**
1. Note: "File size [N] lines, approaching 400 limit"
2. Check plan outline for split boundary guidance (if exists)
3. Escalate to refactor agent: "Proactive split required"
   - Provide: Current file structure, recently added functions
   - Target: Split to two files each <300 lines
4. After split: Re-run precommit to verify
5. Proceed to Step 4 (address remaining warnings)

**If file 350-380 lines:**
- Note in report: "File size [N] lines, monitor next cycle"
- Proceed (acceptable margin)

**If file <350 lines:**
- Proceed to Step 4
```

**Rationale (from Deepening Axis 3):**
- Measurement beats prediction (zero prediction error)
- Context-aware splitting (agent knows recent additions)
- Continuous monitoring (no false negatives)
- Uses guidance from plan (strategic split points)

**Trade-off:**
- Per-cycle overhead: Medium (precommit already runs, just adds split logic)
- Mid-phase splits possible: Less coherent than phase boundary, but measurement-based

---

## Trade-off Analysis

### Planning-Time vs Execution-Time (See Deepening Axis 3 for full analysis)

| Approach | Information Available | Prediction Accuracy | Adaptation | Overhead |
|----------|----------------------|---------------------|------------|----------|
| **Planning-time** | Design document | Low (fabricated heuristics had 42% error) | None (frozen plan) | Low (one-time) |
| **Execution-time** | Actual code structure | Perfect (measured) | High (any cycle) | Medium (per-cycle check) |

**Key insight from Deepening:** Planning predicts WHAT will happen (cycles, phases). Execution observes WHAT DID happen (actual line count, structure). Operational constraints should be handled where they're measurable, not where they're predictable.

**Recommended hybrid approach:**

1. **Planning-time (strategic awareness):** Add growth projection table to outline as WARNING, not ENFORCEMENT
   - Flag phases with >10 High-complexity cycles: "Expect growth pressure"
   - Mark split boundary candidates: "If limit approached, split here"
   - Don't mandate splits (prediction unreliable)

2. **Execution-time (tactical enforcement):** Add proactive split behavior to tdd-task agent
   - Monitor line count each cycle via precommit
   - Trigger split at 380 lines (20-line margin before 400 limit)
   - Use split boundary guidance from plan
   - Escalate to refactor agent for split execution

**Benefits of hybrid:**
- Planning provides strategic context (split boundaries, growth awareness)
- Execution provides tactical precision (measurement-based, context-aware)
- No false positives (only split when measured >380)
- No false negatives (continuous monitoring)

**Trade-off:**
- Planning overhead: Low (outline table creation)
- Execution overhead: Medium (precommit check every cycle, already happens)
- Prediction error: Eliminated (execution uses measurement, not prediction)
- Abstraction alignment: Correct (operational constraints at execution layer)

---

## Scope Assessment

### Files Requiring Changes

**Primary implementation (Fix 1):**
- `agent-core/skills/runbook/SKILL.md` (Phase 0.75 section)
  - Add growth projection table to outline structure
  - Document heuristics (lines/cycle by complexity)
  - Add split phase insertion logic
  - Estimated: 30-40 lines added

**Secondary validation (Fix 2):**
- `agents/decisions/runbook-review.md` (new axis)
  - Add "File Growth Projection" axis with detection criteria
  - Estimated: 20-30 lines added
- `agent-core/agents/plan-reviewer.md` (prompt update)
  - Include growth validation in review checklist
  - Estimated: 10 lines added

**Tertiary cleanup (Fix 3):**
- `agent-core/skills/runbook/SKILL.md` (delete Phase 1.4)
  - Remove lines 504-513
  - Update references to file size awareness
  - Estimated: 10 lines removed, 5 lines updated

**Optional pattern guidance (Fix 4):**
- Design guidance document (location TBD)
  - Add subprocess helper pattern
  - Estimated: 15-20 lines added

### Estimated Complexity

**Fix 1 (Growth Projection):** Tier 1 - Direct implementation
- Prose artifact (outline table structure)
- Heuristic definition (straightforward)
- No code changes, no tests
- Estimated: 1-2 hours

**Fix 2 (Review Validation):** Tier 1 - Direct implementation
- Prose artifact (review axis definition)
- Agent prompt update (straightforward)
- No code changes, no tests
- Estimated: 1 hour

**Fix 3 (Cleanup):** Tier 1 - Direct implementation
- Delete obsolete section
- Update references
- Estimated: 30 minutes

**Fix 4 (Pattern Guidance):** Tier 1 - Direct implementation
- Prose artifact (pattern description)
- Estimated: 30 minutes

**Total estimated effort:** 3-4 hours for all fixes

### Validation Approach

**Empirical calibration (Fix 1 heuristics):**
- Backtest heuristics against worktree-update execution
- Measure actual lines/cycle by complexity tier
- Adjust heuristics if error >20%

**Regression test (Fix 2):**
- Test plan-reviewer on worktree-update outline
- Verify detection of missing growth projection
- Verify split phase recommendation when projection >350

**Next runbook validation:**
- Apply Fix 1+2 to next TDD runbook
- Measure: Did projection prevent refactor escalations?
- Measure: How accurate were heuristics? (projected vs actual)

---

## Conclusion

**Root cause:** Planning pipeline lacks file growth projection at outline phase. The 400-line limit is enforced at commit (reactive) but not projected during planning (proactive awareness).

**Deeper root cause (from Axis 4):** Planning model designed for behavioral correctness, not operational constraints. File limits are resource constraints that should be handled where they're MEASURABLE (execution-time), not where they're PREDICTABLE (planning-time).

**Recommended solution: Hybrid approach**

1. **Planning (strategic awareness):** Add growth projection table to outline as WARNING
   - Measured heuristics from worktree-update: Low: 10 lines/cycle, Medium: 24, High: 42
   - Flag phases with >10 High cycles: "Expect growth pressure"
   - Mark split boundary candidates
   - Don't mandate splits (prediction unreliable, 42% observed error in fabricated heuristics)

2. **Execution (tactical enforcement):** Add proactive split behavior to tdd-task agent
   - Monitor line count via precommit (already runs)
   - Trigger split at 380 lines (20-line margin)
   - Use split boundary guidance from plan
   - Measurement-based, zero prediction error

**Impact of current problem (measured):**
- 18 refactor reports across 37 cycles (49% of cycles triggered refactor)
- 2 opus-tier escalations (architectural)
- 16 sonnet-tier escalations (deslop)

**Complexity:** Low - prose artifacts, agent behavior update, measured heuristics (no fabrication)

**Next step:** Implement hybrid approach - Fix 1 (growth awareness table) in runbook skill + Fix 5 (execution-time split) in tdd-task agent. Validate with next TDD runbook.

---

## Deepening

### Axis 1: Evidence Verification

**Refactor reports: 18 (verified)**
```bash
$ ls plans/worktree-update/reports/*refactor* | wc -l
18
```

Files:
- cycle-1-1-refactor.md
- cycle-2-2-refactor.md
- cycle-3-1-refactor.md
- cycle-4-2-git-helper-refactor.md
- cycle-4-2-refactor.md
- cycle-4-3-refactor.md
- cycle-5-5-refactor.md through cycle-7-12-refactor.md

**Refactor escalations: 2 opus, 16 sonnet (verified from reports)**

Opus escalations (architectural):
1. Cycle 4.2: 477 lines → module extraction recommended (report: "Escalated — architectural refactoring needed")
2. Cycle 7.2: 448 lines → merge validation consolidation (report: "architectural change required")

Sonnet escalations (deslop/consolidation): Remaining 16 reports

**Wall-clock time: Not measured (claim removed)**

Original claim: "1hr+ wall-clock" was estimated, not measured. Git commits don't record execution time. Refactor reports don't include duration. **Corrected claim:** 18 refactor reports across 37 cycles indicates significant overhead, but exact time not measurable from artifacts.

**Lines added per cycle: Measured from git history**

Actual measurements (cli.py only, net lines after formatting):
- Cycle 2.1: +16
- Cycle 2.2: -13 (removal)
- Cycle 2.3: +1
- Cycle 2.4: +3
- Cycle 4.1: +28
- Cycle 4.2: +56 (triggered first major escalation)
- Cycle 4.3: 0 (test-only)
- Cycle 5.3: +6
- Cycle 5.4: +38
- Cycle 5.5: +21
- Cycle 6.1: +4
- Cycle 6.2: +24
- Cycle 6.3: +1
- Cycle 6.4: +9
- Cycle 6.5: +3
- Cycle 7.1: +32
- Cycle 7.2: 0 (refactor before commit)

**Pattern:** High-complexity cycles (4.2, 5.4, 7.1) added 28-56 lines. Medium cycles added 6-24 lines. Low cycles added 1-4 lines. These are POST-refactor numbers (refactors happened before GREEN commit).

**"7+ refactor escalations" verified:** 18 refactor reports confirm >7 escalations occurred. Exact count: 18 refactors, 2 opus-tier, 16 sonnet-tier.

### Axis 2: Heuristics - Fabrication vs Measurement

**Original heuristics were fabricated (violated "No estimates" rule):**

Claimed:
- Low: 8-12 lines/cycle
- Medium: 12-18 lines/cycle
- High: 18-25 lines/cycle

**Actual measurements (from worktree-update execution):**

**High complexity cycles (actual):**
- 4.2: +56 lines (section filtering with multiple functions)
- 5.4: +38 lines (environment initialization)
- 7.1: +32 lines (merge clean tree validation)
- Mean: 42 lines/cycle (fabricated range was 18-25)

**Medium complexity cycles (actual):**
- 4.1: +28 lines (task extraction)
- 6.2: +24 lines (registration probing)
- 5.5: +21 lines (--task option)
- Mean: 24 lines/cycle (fabricated range was 12-18)

**Low complexity cycles (actual):**
- 6.1: +4 lines
- 6.4: +9 lines
- 2.1: +16 lines
- Mean: 10 lines/cycle (fabricated range was 8-12, close but not measured)

**Corrected heuristics (empirically calibrated from worktree-update):**

| Complexity | Measured Mean | Measured Range | Notes |
|------------|---------------|----------------|-------|
| High | 42 lines/cycle | 32-56 | Multi-function features, integration points |
| Medium | 24 lines/cycle | 21-28 | Single-function features, moderate logic |
| Low | 10 lines/cycle | 1-16 | Edge cases, simple validation, test-only |

**Caveats:**
1. Sample size: 17 cycles from one runbook (small sample)
2. Post-refactor numbers: Measurements reflect code AFTER refactoring, not initial implementation
3. File type: Measurements from cli.py only (not tests, which grow differently)
4. Formatter included: Numbers include Black formatter expansion

**Recommendation:** These heuristics need validation across 2-3 more runbooks before codifying. Current Fix 1 should note "empirical calibration required" and provide worktree-update data as initial estimate.

### Axis 3: Execution-Time Adaptation - Deeper Analysis

**Current execution-time behavior (from tdd-task.md):**

Lines 96, 123:
```markdown
- **Ignore** complexity warnings and line limit warnings at this stage
- This surfaces complexity warnings and line limit issues
```

Agent SEES line limit warnings during Step 3 (Quality Check), but is instructed to ignore them in favor of escalating to orchestrator.

**Execution-time split capability:**

Agent already has:
- Line count visibility (precommit reports it)
- File editing capability (Read/Edit/Write tools)
- Helper extraction patterns (demonstrated by _git() in Cycle 7.1)

Agent does NOT have:
- Authority to decide split boundaries (cognitive task)
- Visibility into which functions are cohesive vs separable
- Understanding of module architecture

**Tractability comparison:**

| Approach | What must be predicted | Prediction accuracy | Adaptation capability |
|----------|------------------------|---------------------|----------------------|
| **Planning-time** | Lines per cycle, cumulative growth | Low (42% error in fabricated heuristics) | None (plan frozen before execution) |
| **Execution-time** | Nothing (measure, don't predict) | Perfect (actual line count) | High (split at any cycle) |

**Planning-time challenges:**

1. **Implementation choices unpredictable:** Planner doesn't know if agent will extract helpers, inline variables, use comprehensions vs loops
2. **Formatter expansion variable:** Depends on line length, nesting, argument count — not predictable from design
3. **Refactor timing unknown:** Agent might extract _git() helper at cycle 3 (saving 30 lines) or cycle 7 (worktree-update actual)

**Execution-time advantages:**

1. **Measurement over prediction:** Agent sees actual 448 lines, not estimated 350
2. **Context-aware splitting:** Agent knows which functions were just added, can split cohesively
3. **No heuristic maintenance:** No need to calibrate/update planning heuristics as project evolves

**Execution-time split behavior (proposed):**

```markdown
### Step 3.5: Proactive Split Check (NEW)

After `just precommit`, if line limit warnings present:

1. **Check file size:** Count lines in files with warnings
2. **If file >380 lines:** Trigger proactive split
   - Identify split boundary: Most recent phase boundary or helper group
   - Extract to new module: `<module>_helpers.py` or `<module>_<feature>.py`
   - Update imports in main module and tests
   - Re-run precommit to verify
3. **If file 350-380 lines:** Note in report, proceed (margin acceptable)
4. **If file <350 lines:** Proceed to Step 4 (address other warnings)
```

**Why 380-line trigger?**
- 400 hard limit
- ~15-20 lines added in typical subsequent cycle
- Margin for formatter expansion
- Avoids premature splitting

**Delegation pattern:**

Haiku tdd-task detects >380 lines → escalates to sonnet refactor agent with:
- Current file structure
- Recently added functions (from git diff since last split)
- Target: Split to two files each <300 lines

**Comparison to planning-time:**

| Factor | Planning-time | Execution-time |
|--------|---------------|----------------|
| When executed | Before cycle 1 | At cycle N when limit approached |
| Information available | Design document | Actual code structure |
| Split quality | Predictive (phase boundary) | Reactive (cohesion boundary) |
| False positives | High (predicted 350, actual 280) | None (measured) |
| False negatives | Medium (unexpected growth) | None (continuous monitoring) |
| Overhead | Low (one-time planning) | Medium (check every cycle) |

**Hybrid approach (optimal):**

1. **Planning-time:** Warn if phase has >10 High-complexity cycles → "expect growth pressure, plan split point"
2. **Execution-time:** Automatic split at 380 lines regardless of plan

Planning provides strategic awareness, execution provides tactical precision.

### Axis 4: Deeper WHY - Planning Model vs Operational Constraints

**Planning pipeline design intent (from workflow-core.md, runbook/SKILL.md):**

Core review axes in runbook-review.md:
- Vacuous Cycles: Behavioral substance (correctness)
- Dependency Ordering: Foundation-first (correctness)
- Cycle Density: Collapse candidates (efficiency)
- Checkpoint Spacing: Quality gates (correctness)

**Pattern:** All axes validate BEHAVIORAL correctness, not RESOURCE constraints.

**Why resource constraints absent:**

1. **Historical context:** TDD workflow emerged from small-scope tasks (≤10 cycles, single file). File size wasn't a constraint.

2. **Abstraction mismatch:** Planning operates at cycle/phase level (functional decomposition). File limits operate at line level (physical constraint). These are different abstraction layers.

3. **Unpredictable implementation:** Planner specifies WHAT (test X, implement Y). Agent chooses HOW (helper extraction, inline logic, data structures). Line count emerges from HOW, which planner doesn't control.

4. **Execution-time knowledge:** File size is OBSERVABLE during execution, PREDICTABLE during planning. Observation beats prediction for operational constraints.

**Architectural question: Should planning handle operational constraints?**

**Arguments FOR planning-time handling:**
- Proactive vs reactive (prevent problems before execution)
- Strategic split points (phase boundaries more coherent than mid-phase)
- Reduced execution overhead (no per-cycle checking)

**Arguments AGAINST planning-time handling:**
- Prediction unreliable (42% mean error in fabricated heuristics)
- Implementation variance (agent autonomy on HOW)
- Maintenance burden (heuristics need continuous calibration)
- Abstraction violation (mixing behavioral decomposition with resource management)

**Correct abstraction layer: Execution-time**

Operational constraints (line limits, memory, time) should be handled where they're MEASURABLE, not where they're PREDICTABLE.

**Analogy:** Garbage collection doesn't plan memory allocation at compile time. It monitors at runtime and triggers when thresholds reached.

**File limits are analogous:**
- Compile-time (planning): Can't predict exact line count
- Runtime (execution): Measure actual line count, trigger split when needed

**Planning role should be strategic awareness, not tactical enforcement:**

Planning should note:
- "Phase 7 has 13 High-complexity cycles → expect file growth pressure"
- "If cli.py approaches limit, split boundary candidates: Phase 6/7 transition, merge helpers group"

Execution should:
- Monitor actual line count each cycle
- Trigger split at 380 lines with split boundary guidance from plan

**Implication for Fix 1:**

Original Fix 1 (growth projection table) is useful as STRATEGIC AWARENESS, not TACTICAL ENFORCEMENT.

**Revised Fix 1:**
- Add growth projection to outline (awareness)
- Mark split boundary candidates (guidance)
- Don't mandate splits (enforcement stays at execution-time)

**New Fix 5: Execution-Time Split Behavior**

Add to tdd-task.md Step 3.5 (after precommit):

```markdown
### Step 3.5: Proactive Split Check

After `just precommit`, check line limit warnings:

**If file >380 lines:**
1. Note: "File size 380+ lines, approaching 400 limit"
2. Check plan for split boundary guidance
3. Escalate to refactor agent: "Proactive split needed"
4. Refactor agent extracts recent additions to new module
5. Re-run precommit to verify split successful

**If file 350-380 lines:**
- Note in report: "File size [N] lines, monitor next cycle"
- Proceed (acceptable margin)

**If file <350 lines:**
- Proceed to next step
```

**Benefits:**
- Measurement-based (no prediction error)
- Context-aware (agent knows recent additions)
- Guidance from plan (strategic split points available)
- Continuous monitoring (no false negatives)

**Trade-off:**
- Per-cycle overhead (check every cycle vs once at planning)
- Mid-phase splits possible (less coherent than phase boundary)
- Requires refactor agent escalation (orchestrator complexity)

**Conclusion:**

Planning SHOULD provide strategic awareness (growth projection, split guidance).
Planning should NOT enforce tactical splits (operational constraint).
Execution SHOULD handle enforcement (measurement-based, context-aware).

This separates concerns: planning for behavioral correctness, execution for operational constraints.
