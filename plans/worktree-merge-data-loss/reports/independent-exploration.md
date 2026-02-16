# Independent Runbook Quality Analysis

## Summary

Analyzed runbook phases 1-2 for the worktree-merge-data-loss plan against source files, design specification, and test patterns. Found 13 findings: 1 critical, 3 major, 5 minor, 4 observations. All critical/major issues affect design fidelity and must be addressed before orchestration.

---

## Critical Findings

### 1. Line number reference misalignment in Cycle 1.4

**Severity:** CRITICAL

**Location:** Runbook Phase 1, Cycle 1.4, line 187

**Issue:** Location hint states "before line 351" but `cli.py` line 351 is inside the function, not before. The rm() function **starts at line 349**, not 347.

**Details:**
```
cli.py line 347: @worktree.command()
cli.py line 348: @click.argument("slug")
cli.py line 349: def rm(slug: str) -> None:
cli.py line 350:     """Remove worktree and its branch."""
cli.py line 351:     worktree_path = wt_path(slug)
```

The runbook says "before line 351" (which is `worktree_path = wt_path(slug)`), but the guard should run **after the function definition, before line 351** (i.e., after line 350, before worktree_path is computed).

**Impact:** Haiku executor will misplace the guard logic, breaking the design requirement that guard runs BEFORE any operations touch the worktree path.

**Fix:** Update location hint to "After line 350 (docstring), before line 351 (worktree_path assignment)" or provide exact line count. Prerequisite says "lines 347-382" which is correct, but the insertion point hint is ambiguous.

---

## Major Findings

### 2. Cycle 1.4-1.6 branch deletion implementation unclear

**Severity:** MAJOR

**Location:** Runbook Phase 1, Cycles 1.4-1.6, lines 217-230 (Cycle 1.5)

**Issue:** The runbook states "Modify existing branch deletion code (lines 369-373) to use `-d` for merged, differentiate messages" but current cli.py lines 369-373 show:

```python
r = subprocess.run(
    ["git", "branch", "-d", slug], capture_output=True, text=True, check=False
)
if r.returncode != 0 and "not found" not in r.stderr.lower():
    click.echo(f"Branch {slug} has unmerged changes — use: git branch -D {slug}")
```

This is a single block with **no conditional for merged vs unmerged**. The runbook expects the implementation to track merge status from the guard (Cycle 1.4) and use it here, but the runbook doesn't specify **how** to thread that merge-status flag through the function or where to store it.

**Details:**
- Cycle 1.4 (line 186) says "Track removal type: merged vs focused-session-only" but doesn't say whether this is a local variable, parameter to a helper, or return value from guard
- Cycles 1.5-1.6 assume this tracking exists but provide no implementation guidance
- Current code has no guard at all, so there's nothing to track

**Impact:** Haiku executor must invent the threading mechanism (likely local variable before line 351). The design is sound but the runbook skips a key implementation detail.

**Fix:** Add clarification after Cycle 1.4: "Track removal type by setting a local variable: `removal_type = 'merged' | 'focused-session' | None` based on guard logic. Use this variable in branch deletion (Cycles 1.5-1.6) to choose `-d` vs `-D` flags."

### 3. Cycle 1.7 test references undefined behavior

**Severity:** MAJOR

**Location:** Runbook Phase 1, Cycle 1.7, lines 300-304

**Issue:** The test asserts `_probe_registrations` NOT called via "mock or side effect absence." No fixtures in `fixtures_worktree.py` provide a mock for `_probe_registrations`. The existing test file `test_worktree_rm.py` doesn't mock this function.

**Details:**
```python
# From Cycle 1.7, lines 303-304:
- `_probe_registrations` NOT called (verify via mock or side effect absence)
```

The test must verify that when guard exits 1, `_probe_registrations` is never executed. But the test-writing guidance is vague: "via mock or side effect absence" suggests either:
- A mock that tracks calls (not in fixtures)
- Observing no side effects (worktree registrations not removed), but that's implicit in the directory/branch still existing

**Impact:** Haiku executor must invent the verification mechanism. The intent (regression test for call ordering) is clear, but the implementation is undefined.

**Fix:** Clarify in Cycle 1.7 RED phase: "Verify integration: Call `_probe_registrations` is not invoked when guard refuses. Test by: (1) inspect git status to confirm worktree still registered before guard exit, (2) after rm returns exit 1, verify registration unchanged via `git worktree list --porcelain`."

### 4. Cycle 1.9 import source ambiguous

**Severity:** MAJOR

**Location:** Runbook Phase 1, Cycle 1.9, line 425

**Issue:** Line 425 says "Add import for `_is_branch_merged`" but **the function hasn't been created yet** — Cycle 1.1 is in the same phase (Phase 1), but Cycle 1.9 runs after Cycle 1.1. However, the cycles are independent if reading sequentially.

**Details:**
- Cycle 1.1 creates `_is_branch_merged` in utils.py
- Cycle 1.9 (line 425) says to import it in merge.py: "from claudeutils.worktree.utils import _is_branch_merged"
- But the cycles are TDD (RED-GREEN order), and 1.9 RED phase runs before 1.1 GREEN phase if executed in order

**Current code check:**
- merge.py line 1-20: Existing imports do NOT include _is_branch_merged ✓
- utils.py lines 1-39: Function exists but only after Cycle 1.1 implementation

**Impact:** If Cycle 1.9 is executed before Cycle 1.1 GREEN completes, the import will fail. Runbook doesn't specify execution order constraints.

**Fix:** Add dependency note after Cycle 1.1: "Cycle 1.9 (MERGE_HEAD checkpoint) depends on Cycle 1.1 GREEN (function exists in utils.py before import in merge.py)." OR reorder Cycle 1.9 to run after Cycle 1.1.

---

## Minor Findings

### 5. Cycle 1.8 references "old branch delete fallback block" that doesn't exist

**Severity:** MINOR

**Location:** Runbook Phase 1, Cycle 1.8, lines 355-366

**Issue:** Line 355-357 describes the fallback block:
```python
# From Cycle 1.8, line 355-357:
subprocess.run(["git", "branch", "-d", slug])  # with error message suggesting -D
```

But the **current cli.py already has this block** (lines 369-373). The runbook treats it as "obsolete" code that "should be removed in GREEN phase" (line 366).

However, the current code is:
```python
r = subprocess.run(
    ["git", "branch", "-d", slug], capture_output=True, text=True, check=False
)
if r.returncode != 0 and "not found" not in r.stderr.lower():
    click.echo(f"Branch {slug} has unmerged changes — use: git branch -D {slug}")
```

This is **exactly the code** the runbook describes as "obsolete." The runbook expects the RED phase to fail against current code (i.e., the fallback exists and outputs the suggestion). But the runbook calls this a "regression guard" (line 340), not a cleanup step.

**Details:**
- Cycle 1.8 is TYPE: Transformation (Regression guard)
- RED phase should fail when run against current code
- Current code ALREADY emits the suggestion
- So RED phase should PASS, not fail
- But runbook says RED phase "expected failure: output contains git branch -D string"

**Clarification issue:** Is this cycle meant to:
1. Test that destructive suggestions DON'T exist (in which case RED fails and code needs new guard from 1.4-1.6)?
2. Or test that after Cycles 1.4-1.7 are done, the old fallback is removed?

The runbook says "After Cycles 1.4-1.7 restructure rm(), this old fallback code is obsolete" (line 342), but Cycles 1.4-1.7 haven't been implemented yet, so the fallback still exists. This ordering is correct.

**Impact:** LOW — the cycle is conceptually sound but the explanation is confusing. Executor might misunderstand whether this is a cleanup step or a test that verifies absence.

**Fix:** Clarify line 340: "Cycle 1.8 is a CLEANUP step, not a test cycle. After Cycles 1.4-1.7 complete and add the guard, the old fallback block (lines 369-373) becomes obsolete and must be deleted. This cycle removes it."

### 6. Cycle 1.13 admits reproduction uncertainty

**Severity:** MINOR

**Location:** Runbook Phase 1, Cycle 1.13, line 585

**Issue:** Line 585 says the test "may pass even without fixes if the original bug was environment-specific." This is accurate but creates test validity ambiguity.

**Details:**
```
# Line 585:
The test may pass even without fixes if the original bug was environment-specific (design.md line 204).
```

The test could have a false-pass rate (passes despite incomplete implementation). This is acknowledged in design.md but makes the test less useful for verification.

**Impact:** MINIMAL — the test has value as a regression guard even if it doesn't reproduce the bug. But executor might skip this test thinking "it's inconclusive."

**Fix:** Change line 585 tone: "This test serves as a regression guard even if it doesn't reproduce the original bug. If it passes without code changes, the original incident was environment-specific. If it fails, the fix addresses it."

### 7. Cycle 1.10 assumes Cycle 1.9 implementation before testing

**Severity:** MINOR

**Location:** Runbook Phase 1, Cycle 1.10, lines 434-452

**Issue:** Cycle 1.10 is marked "expected result: test PASSES against Cycle 1.9 implementation" (line 452). But the test file `test_worktree_merge_correctness.py` doesn't exist yet.

**Details:**
- Cycles 1.1-1.8 reference test file `test_worktree_rm_guard.py` (doesn't exist)
- Cycles 1.9-1.13 reference test file `test_worktree_merge_correctness.py` (doesn't exist)
- Cycle 1.10 line 456 says "Verify RED: pytest tests/test_worktree_merge_correctness.py::test_phase4_allows_already_merged -v (expected: PASS)"

This is a forward reference to a test that will be created in a later cycle. The expected result is "PASS" because Cycle 1.9's implementation already handles it.

**Impact:** MINIMAL — this is correct (regression test format). But the line 456 reference path is forward-looking. Executor must ensure this test exists before running Cycle 1.10's verification step.

**Fix:** Add note after line 456: "Note: This test file is created during Cycle 1.9 GREEN phase (test setup). Verify the file exists before running this command."

### 8. Phase 2 prerequisites don't reference Phase 1 completion

**Severity:** MINOR

**Location:** Runbook Phase 2, Step 2.1, line 12

**Issue:** Phase 2 depends on Phase 1 implementation but doesn't state it explicitly as a prerequisite.

**Details:**
Line 12: "**Prerequisite:** Read `agent-core/skills/worktree/SKILL.md` (lines 84-115)"

But the actual prerequisite is: Phase 1 Track 1 (removal guard) must be complete so the `rm` exit 1 behavior exists. The skill update documents this behavior.

**Impact:** LOW — Phase 2 can't execute until Phase 1 is done (runbook order enforces this), but the prerequisite section doesn't make this dependency explicit.

**Fix:** Add to prerequisites: "Phase 1 Track 1 (removal guard) must be implemented first — this step documents the new `rm` exit 1 behavior."

---

## Observations (Non-Blocking)

### 9. Test file naming convention

**Observation:** Runbook references `test_worktree_rm_guard.py` and `test_worktree_merge_correctness.py` but existing test files use pattern `test_worktree_*.py`. These new test files should follow convention.

**Existing pattern:**
- `test_worktree_rm.py`
- `test_worktree_merge_merge_head.py`
- `test_worktree_merge_merge_parent.py`

**Suggested naming:** `test_worktree_rm_guard.py` and `test_worktree_merge_correctness.py` are descriptive and fit the pattern.

---

### 10. Fixture availability confirmed

**Observation:** All fixtures referenced in runbook exist in `fixtures_worktree.py`:
- `repo_with_submodule` ✓ (lines 72-154)
- `commit_file` ✓ (lines 158-171)
- `mock_precommit` ✓ (lines 12-36)
- `init_repo` ✓ (lines 40-68)

Test patterns in existing `test_worktree_*.py` files show correct usage of these fixtures.

---

### 11. Import paths verified

**Observation:** All import paths in runbook are correct:
- `from claudeutils.worktree.utils import _git, wt_path` ✓ (cli.py line 20)
- `from claudeutils.worktree.merge import merge as merge_impl` ✓ (cli.py line 14)
- `_is_branch_merged` will be created in utils.py (import-ready) ✓

---

### 12. Git command syntax verified

**Observation:** All git commands referenced in runbook syntax is correct:
- `git merge-base --is-ancestor <slug> HEAD` ✓ (design.md line 41)
- `git rev-list --count <merge_base>..<slug>` ✓ (design.md line 48)
- `git log -1 --format=%s <slug>` ✓ (design.md line 50)
- `git branch -d` / `git branch -D` ✓ (design.md lines 77-78)

---

### 13. Design alignment spot checks

**Observation:** Sample spots checked against design.md:
- Cycle 1.1 `_is_branch_merged` implementation matches design.md line 41-42 ✓
- Cycle 1.4 guard flow matches design.md lines 60-74 ✓
- Cycle 1.9 MERGE_HEAD checkpoint matches design.md lines 105-109 ✓
- Phase 2 Mode C update matches design.md lines 158-163 ✓

---

## Summary Table

| Finding | Severity | Category | Status |
|---------|----------|----------|--------|
| 1. Line number misalignment (Cycle 1.4) | CRITICAL | Implementation | Must fix |
| 2. Branch deletion threading unclear (Cycles 1.4-1.6) | MAJOR | Design detail | Must clarify |
| 3. Cycle 1.7 mock strategy undefined | MAJOR | Testing | Must clarify |
| 4. Cycle 1.9 import order ambiguous | MAJOR | Dependency | Must resolve |
| 5. Cycle 1.8 description confusing (regression vs cleanup) | MINOR | Documentation | Should clarify |
| 6. Cycle 1.13 reproduction uncertainty acknowledged | MINOR | Testing | Could improve tone |
| 7. Cycle 1.10 forward reference to test file | MINOR | Documentation | Should clarify |
| 8. Phase 2 prerequisites missing Phase 1 dependency | MINOR | Documentation | Should add |
| 9. Test file naming | Observation | Convention | Compliant |
| 10. Fixture availability | Observation | Testing | Verified |
| 11. Import paths | Observation | Implementation | Verified |
| 12. Git command syntax | Observation | Implementation | Verified |
| 13. Design alignment spots | Observation | Quality | Verified |

---

## Recommendations

**Before orchestration:**

1. **CRITICAL:** Fix line number reference in Cycle 1.4 (Finding 1)
   - Clarify insertion point: "After line 350 (function docstring), before line 351 (worktree_path assignment)"

2. **MAJOR:** Clarify branch deletion threading (Finding 2)
   - Add to Cycle 1.4 GREEN phase: "Track removal type with local variable before guard block"
   - Show variable assignment examples for merged vs focused-session

3. **MAJOR:** Specify Cycle 1.7 mock strategy (Finding 3)
   - Clarify how to verify `_probe_registrations` not called
   - Suggest git worktree list verification approach

4. **MAJOR:** Resolve Cycle 1.9 import order (Finding 4)
   - Add explicit dependency: "Requires Cycle 1.1 GREEN complete before Cycle 1.9 RED starts"
   - OR reorder cycles if sequential execution

5. **MINOR:** Clarify Cycle 1.8 as cleanup step (Finding 5)

6. **MINOR:** Improve Cycle 1.13 test documentation (Finding 6)

7. **MINOR:** Add forward reference note to Cycle 1.10 (Finding 7)

8. **MINOR:** Add Phase 1 dependency to Phase 2 prerequisites (Finding 8)

---

## Confidence Assessment

- **Line number accuracy:** HIGH — cross-referenced against source file
- **Function existence:** HIGH — design specifies all functions with exact names
- **Test patterns:** HIGH — existing test files provide clear precedent
- **Import paths:** HIGH — verified in current source files
- **Design fidelity:** MEDIUM-HIGH — spot checks pass, but threading details (Finding 2) need clarification
