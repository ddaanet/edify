## Runbook Review: worktree-update (Phases 1–7)

Applying the four review axes from `agents/decisions/runbook-review.md`.

---

### 1. Vacuous Cycles

**Cycle 1.1 — CLI group registration** (Phase 1)
- RED assertions: import succeeds, `isinstance(worktree, click.Group)`, help output string check, exit 0
- All structural: satisfiable by `import X; assert callable(X)` — no behavioral constraint
- **Action:** Merge into 1.2. The registration is a prerequisite for testing `wt_path()` — make it setup within 1.2's RED phase (import + first behavioral assertion together).

**Cycle 1.4 — Sibling path, multiple slugs** (Phase 1)
- Runbook self-declares: "Test should pass immediately (logic from 1.3 already handles this)"
- GREEN says "likely no changes needed"
- GREEN adds 0 lines. Test verifies statelesness already guaranteed by pure-function design.
- **Action:** Add as parametrized assertions within Cycle 1.3 (`wt_path("a")` vs `wt_path("b")` same parent).

**Cycle 5.3 — Existing submodule branch reuse** (Phase 5)
- Runbook self-declares: "Logic from 5.2 already checks submodule branch existence... No additional code needed if 5.2 implemented correctly"
- GREEN says "Verify submodule branch detection logic from 5.2 is correct (likely no changes needed)"
- GREEN adds 0 lines. Tests a non-branch already covered by 5.2's conditional.
- **Action:** Add as assertion in Cycle 5.2 (test both fresh-branch and existing-branch paths for submodule).

**Impact:** 3 vacuous cycles eliminated → 40 → 37 effective cycles.

---

### 2. Dependency Ordering

**Phase 4 → Phase 3 dependency is spurious.**
- Outline declares "Depends on: Phase 3 (slug derivation used internally)"
- But `focus_session(task_name, session_md_path)` does not call `derive_slug()`. Both are called independently by Phase 5's task mode.
- Phase 4 has no actual dependency on Phase 3. It only needs session.md parsing.
- **Impact:** Low (Phase 3 is 1 cycle, reordering gains nothing). But incorrect dependency declarations mislead the orchestrator.
- **Action:** Correct dependency declaration to "Phase 1 (file structure only)" or "None."

**Missing jobs.md auto-resolve — design/runbook gap.**
- Design line 159 explicitly specifies: `agents/jobs.md conflict: Keep ours with warning: git checkout --ours agents/jobs.md && git add agents/jobs.md`
- Phase 7 cycles cover: agent-core (7.8), session.md (7.9), learnings.md (7.10), source file abort (7.11)
- No cycle handles jobs.md. During execution, a jobs.md conflict falls through to 7.11 (source file abort), aborting the merge for a case the design says should auto-resolve.
- **Action:** Add jobs.md auto-resolve cycle between 7.10 and 7.11 (simple: checkout --ours, git add, same pattern as 7.8). Or merge into 7.8 as a parametrized "known-file auto-resolve" cycle covering both agent-core and jobs.md.
- **Severity: High** — this will cause merge failures in production for a case the design explicitly handles.

**Test file organization drift from design.**
- Design specifies: `test_worktree_path.py`, `test_sandbox_registration.py`, `test_focus_session.py`, `test_worktree_rm.py`, `test_worktree_merge.py`
- Outline preserves these file names
- All expanded phase files consolidate to `test_worktree_cli.py` (Phases 1-4, 6-7) without documented rationale
- Only Phase 5 preserves design intent (`test_worktree_new.py`)
- Haiku will create one large test file (~40 test functions) instead of focused modules
- **Impact:** Medium — contradicts design decision, creates maintenance burden, but functionally equivalent
- **Action:** Either update phase files to match design file names, or document rationale for consolidation. Recommend matching design (separate files per concern).

---

### 3. Cycle Density

**Cycle 4.3 — Reference files filtering** (Phase 4)
- Structurally identical to Cycle 4.2 (Blockers filtering): parse section, check relevance per entry, conditionally include
- <1 branch point difference (same filtering logic, different section header)
- **Action:** Merge into 4.2 as a single "section filtering" cycle that tests both Blockers and References. The RED phase uses parametrized test data with both section types.
- **Impact:** 37 → 36 effective cycles after prior vacuity fixes.

**Cycle 7.8 — agent-core auto-resolve** (Phase 7)
- GREEN adds ~3 lines: `if "agent-core" in conflicts: checkout --ours, git add`
- Borderline thin. However, it represents a distinct auto-resolution strategy with clear rationale (Phase 2 already resolved submodule).
- **Keep** — but see jobs.md gap above. If jobs.md auto-resolve is added, merge 7.8 and jobs.md into single "known-file auto-resolve" cycle (both use identical `checkout --ours && git add` pattern).

---

### 4. Checkpoint Spacing

**Gap: Phase 5 checkpoint (cycle ~23) → Phase 7 checkpoint (cycle ~40) = 17 cycles across 2 phases.**

Exceeds the >10 cycle threshold. Phase 6 (`rm` command, 5 cycles, Medium complexity) has no checkpoint. Phase 7 is High complexity (12 cycles).

Phase 6 involves:
- Worktree registration probing (subprocess output parsing)
- Submodule-first removal ordering (critical correctness constraint — FR-5)
- Filesystem cleanup (orphaned directories, empty containers)

These are exactly the conditions that warrant a checkpoint: complex data manipulation and an integration point (removal ordering composes probing + cleanup).

- **Action:** Add light checkpoint after Phase 6 (Fix + Functional). Validates removal ordering correctness before the large Phase 7 merge implementation.
- **Rationale:** Haiku drift across 17 uncheckpointed cycles risks pretraining-biased removal ordering (parent-first is the intuitive/common pattern, submodule-first is the correct but counterintuitive one).

---

### Summary

| # | Axis | Severity | Finding | Action |
|---|------|----------|---------|--------|
| 1 | Vacuous | Medium | Cycle 1.1 — structural CLI registration | Merge into 1.2 |
| 2 | Vacuous | Medium | Cycle 1.4 — self-declared "should pass immediately" | Merge into 1.3 |
| 3 | Vacuous | Medium | Cycle 5.3 — self-declared "no additional code needed" | Merge into 5.2 |
| 4 | Dependency | **High** | Missing jobs.md auto-resolve (design line 159) | Add cycle or merge with 7.8 |
| 5 | Dependency | Medium | Test file consolidation drifted from design | Match design file names or document rationale |
| 6 | Dependency | Low | Phase 4→3 dependency declaration is spurious | Correct to "None" |
| 7 | Density | Medium | Cycle 4.3 identical logic to 4.2 | Merge into 4.2 |
| 8 | Checkpoint | Low | 17 cycles between Phase 5 and Phase 7 checkpoints | Add checkpoint after Phase 6 |

**Net effect:** 40 → 36 cycles (4 eliminated via vacuity/density), 1 cycle added (jobs.md), 1 checkpoint added (Phase 6). Final: **37 cycles, 4 checkpoints.**
