# Step 1.4

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.4: Add merge idempotency test

**Objective**: Add test verifying merge can be safely re-run after manual fixes (idempotency).

**Finding**: C5 from deliverable review — No merge idempotency test across all merge test files. Design specifies "Idempotency: re-running after manual fix resumes correctly."

**Implementation**:

1. **Test file location**: `tests/test_worktree_merge_validation.py` (validation-focused tests — idempotency is a validation concern)

2. **Add test function to existing file**:
   ```python
   def test_merge_idempotency(tmp_path, fixtures_worktree):
       """Test merge can be re-run after manual intervention."""
       # Setup: create worktree with changes
       # Run merge — let it fail (e.g., dirty tree)
       # Fix the issue (e.g., commit changes)
       # Re-run merge — should succeed
       # Verify: merge completes, no duplicate commits, clean state
   ```

3. **Test scenarios** (choose 1-2):
   - Dirty tree → clean → merge succeeds
   - Precommit fail → fix code → merge succeeds
   - Conflict → resolve → merge succeeds
   - **Recommended**: Dirty tree scenario (simpler, tests core idempotency)

4. **Assertions**:
   - First run: fails with appropriate error
   - Second run: succeeds after fix
   - No duplicate work (no double-merge commits)
   - Final state matches single successful merge

**Expected Outcome**: Test verifies merge is safe to retry, critical for recovery workflow reliability.

**Error Conditions**:
- If test doesn't detect non-idempotency → verify assertions check for duplicate work
- If cleanup between runs incomplete → verify fixtures reset state

**Validation**:
```bash
pytest tests/test_worktree_merge_validation.py::test_merge_idempotency -v
```

---
