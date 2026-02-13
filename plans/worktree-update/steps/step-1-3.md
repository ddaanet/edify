# Step 1.3

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.3: Add precommit failure test

**Objective**: Add test for Phase 4 merge behavior when precommit fails after successful merge.

**Finding**: C4 from deliverable review — `tests/test_worktree_merge_parent.py` has no precommit failure test despite design requirement.

**Implementation**:

1. **Read existing precommit test** at `tests/test_worktree_merge_parent.py:89-159`:
   - Understand test structure (setup, merge, assertions)
   - Note docstring claims 6 behavioral conditions including failure path
   - Current test only exercises happy path

2. **Add new test function to existing file** (`test_worktree_merge_parent.py`):
   ```python
   def test_merge_precommit_failure(tmp_path, fixtures_worktree):
       """Test Phase 4: merge succeeds but precommit fails."""
       # Setup: create worktree with changes
       # Merge to Phase 3 (merged but not committed)
       # Mock or force precommit failure
       # Verify: exit code 1, error message, no commit created
   ```

3. **Mock precommit failure**:
   - Option A: Mock `subprocess.run` for `just precommit` call
   - Option B: Create actual precommit failure (invalid syntax in committed file)
   - **Recommended**: Option A (faster, more isolated)

4. **Assertions**:
   - Exit code: 1 (not 0 or 2)
   - Error message: "Precommit failed after merge"
   - Git state: merge completed, but no merge commit
   - Branch state: worktree branch still exists (merge incomplete)

**Expected Outcome**: Test verifies merge handles precommit failure gracefully with correct exit code and error message.

**Error Conditions**:
- If test hangs → check subprocess timeout settings
- If test flakes → verify fixtures create clean isolated state
- If precommit mock doesn't trigger → verify call pattern match

**Validation**:
```bash
pytest tests/test_worktree_merge_parent.py::test_merge_precommit_failure -v
```

---
