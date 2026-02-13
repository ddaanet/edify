---
name: worktree-update-recovery
model: sonnet
---

# Worktree Update Recovery

**Context**: Fix critical findings and functional correctness bugs from deliverable review. Independent fixes only — C1 and R1 deferred to workwoods redesign.

**Requirements**: `plans/worktree-update/reports/deliverable-review.md`

**Design**: `plans/worktree-update/design.md`

**Status**: Ready

**Created**: 2026-02-13

---

## Weak Orchestrator Metadata

**Total Steps**: 6

**Execution Model**:
- Steps 1-6: Sonnet (code fixes, config updates, test additions with behavioral verification)

**Step Dependencies**: Independent (all can run in parallel, but execute sequentially for simplicity)

**Error Escalation**:
- Test failures → STOP, report issue to user
- Precommit failures → Fix and retry
- Unexpected behavior → STOP, escalate to user

**Report Locations**: `plans/worktree-update/reports/recovery-step-N.md`

**Success Criteria**: All 6 findings resolved, tests pass, precommit clean

**Prerequisites**:
- Repository in clean state (✓ verified via git status before execution)
- Test suite functional (✓ verify with `pytest tests/test_worktree_*.py -v` before starting)

---

## Common Context

**Recovery scope (from session.md):**

**FIX NOW:**
- C2: wt-merge THEIRS clean tree check (uncommitted worktree changes lost on merge)
- C3: agent-core setup recipe (env init fails for agent-core-only worktrees)
- C4: Precommit failure test (specified behavior path, zero coverage)
- C5: Merge idempotency test (recovery workflow untested)
- M1: `_filter_section` continuation line handling (non-bullet lines leak into filtered output)
- M2: `plan_dir` regex case-sensitive (won't match title case `Plan:`)

**DEFER:**
- C1: wt-ls native bash — workwoods FR-1 redesigns wt-ls
- R1: Auto-combine session.md/jobs.md on merge — workwoods FR-5/FR-6 supersede
- M3-M10: Test quality and prose improvements (evaluate post-workwoods)
- Minor findings (24): batch during post-merge cleanup or defer

**Strategy:** Fix independent findings → merge to main → workwoods designs against merged baseline

**Key Constraints:**
- Maintain design conformance (D1-D8 from design.md)
- No new features, only bug fixes
- Test additions must verify specified behavior, not just structure

**Project Paths:**
- Config: `justfile`, `agent-core/justfile`
- Code: `src/claudeutils/worktree/cli.py`
- Tests: `tests/test_worktree_merge_*.py`

---

## Step 1.1: Fix wt-merge THEIRS clean tree check

**Objective**: Add clean tree check for worktree side before merge to prevent uncommitted changes from being silently lost.

**Finding**: C2 from deliverable review — `justfile:209-222` missing THEIRS clean tree check.

**Implementation**:

1. **Read current wt-merge recipe** at `justfile:209-222`:
   - Identify where OURS clean tree check happens
   - Note the check pattern and error message format

2. **Add THEIRS clean tree check**:
   - After OURS check (around line 211-212)
   - Before fetch and merge operations
   - Check worktree directory for uncommitted changes
   - Pattern: `git -C "$WT_PATH" diff --quiet --exit-code && git -C "$WT_PATH" diff --cached --quiet --exit-code`
   - Error message: "Worktree has uncommitted changes. Commit or stash before merging."

3. **Verify placement**:
   - THEIRS check must run BEFORE `git fetch` (line 213)
   - Both clean checks (OURS and THEIRS) must complete before merge operations

**Expected Outcome**: wt-merge recipe includes clean tree check for both main and worktree sides. Uncommitted changes in worktree cause early exit with clear error message.

**Error Conditions**:
- If git commands fail → check WT_PATH is correctly computed
- If recipe syntax error → verify bash quoting and variable expansion

**Validation**:
```bash
# Manual test: create dirty worktree and verify early exit
# (Defer to Step 1.5 for automated test)
grep -A 3 "THEIRS clean tree" justfile
```

---

## Step 1.2: Add agent-core setup recipe

**Objective**: Add `setup` recipe to agent-core/justfile to support environment initialization in agent-core-only worktrees.

**Finding**: C3 from deliverable review — `agent-core/justfile` missing `setup` recipe required by design D5.

**Prerequisite**: Read `agent-core/justfile` (full file) — understand existing recipe structure and patterns.

**Implementation**:

1. **Read parent justfile setup recipe** at `justfile`:
   - Find the `setup` recipe (use `grep -A 20 "^setup:"`)
   - Understand what it does (venv, direnv, npm)

2. **Create agent-core setup recipe** in `agent-core/justfile`:
   - Add after existing recipes (around line 15-20)
   - Minimal version for agent-core context:
     ```just
     setup: # Set up agent-core development environment
         @echo "No setup required for agent-core (no venv or npm)"
         @echo "Run 'just sync-to-parent' to update parent .claude/ symlinks"
     ```
   - Rationale: agent-core is documentation/skills only, no Python package dependencies

3. **Alternative if agent-core needs real setup**:
   - Check if agent-core has its own pyproject.toml or package.json
   - If yes, implement actual setup steps
   - If no, use stub recipe above

**Expected Outcome**: `just setup` runs successfully in agent-core directory without errors. Recipe provides helpful guidance for agent-core-specific workflows.

**Error Conditions**:
- If justfile syntax error → verify recipe formatting (tabs vs spaces)
- If recipe conflicts with existing → check for duplicate recipe names

**Validation**:
```bash
cd agent-core
just setup
echo $?  # Should be 0
```

---

## Step 1.3: Fix _filter_section continuation line handling

**Objective**: Fix `_filter_section` to exclude non-bullet continuation lines that belong to filtered-out entries.

**Finding**: M1 from deliverable review — `cli.py:55-60` non-bullet continuation lines leak into filtered output.

**Implementation**:

1. **Read _filter_section function** at `src/claudeutils/worktree/cli.py:55-60`:
   - Understand current filtering logic
   - Identify where continuation lines are processed

2. **Add continuation line tracking**:
   - Track state: "in relevant section" vs "in filtered-out section"
   - When a bullet line is filtered out, set state = "skipping"
   - When next bullet line is relevant, set state = "including"
   - Only append lines when state = "including"

3. **Implementation approach**:
   - Track state: whether current section is relevant (should include) or filtered out (should skip)
   - When a bullet line matches filter: set state to "including"
   - When a bullet line doesn't match: set state to "skipping"
   - Only append lines (bullets + continuation) when state is "including"

4. **Handle edge cases**:
   - Empty lines between sections (preserve structure)
   - Nested bullets (indented with spaces)
   - Headers (always include)

**Expected Outcome**: Focused sessions exclude continuation lines from irrelevant tasks. Example: task "Implement X" with sub-items filtered out when focus is "Implement Y".

**Error Conditions**:
- If filtering too aggressive → verify bullet detection regex
- If continuation lines still leak → check state tracking logic
- If focused session empty → verify at least one task matches filter

**Validation**:
```bash
# Manual verification with session.md sample (test function may not exist yet)
# If test exists: pytest tests/test_worktree_commands.py -k filter_section -v
# Otherwise: manual test with sample session.md
```

---

## Step 1.4: Fix plan_dir regex case-sensitivity

**Objective**: Make `plan_dir` regex case-insensitive to match both `plan:` and `Plan:` in session.md.

**Finding**: M2 from deliverable review — `cli.py:73` regex `plan:\s*(\S+)` won't match title case `Plan:`.

**Implementation**:

1. **Read plan_dir extraction** at `src/claudeutils/worktree/cli.py:73`:
   - Current regex: `plan:\s*(\S+)`
   - Find where this is used in focus_session function

2. **Make regex case-insensitive**:
   - Option A: Change to `[Pp]lan:\s*(\S+)` (explicit both cases)
   - Option B: Add `re.IGNORECASE` flag if using re.search()
   - Option C: Use `(?i)plan:\s*(\S+)` (inline case-insensitive flag)
   - **Recommended**: Option A (explicit, no flag needed, clearer intent)

3. **Verify usage context**:
   - Check if other fields in session.md use title case
   - If yes, update those patterns too (Model:, Restart:, etc.)
   - For this finding, only `plan:` → `[Pp]lan:` required

**Expected Outcome**: `focus_session` extracts plan directory correctly from both `plan: foo` and `Plan: foo` metadata formats.

**Error Conditions**:
- If regex matches incorrectly → verify \S+ captures plan directory without whitespace
- If no match found → check session.md format matches expected pattern

**Validation**:
```bash
# Manual verification or unit test if exists
# If test exists: pytest tests/test_worktree_commands.py -k focus_session -v
# Otherwise: manual test with session.md containing both `plan:` and `Plan:`
```

---

## Step 1.5: Add precommit failure test

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

## Step 1.6: Add merge idempotency test

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

## Final Checkpoint

**After all steps complete:**

1. **Run full test suite**:
   ```bash
   pytest tests/test_worktree_*.py -v
   ```

2. **Run precommit checks**:
   ```bash
   just precommit
   ```

3. **Verify all findings resolved**:
   - C2: `grep "THEIRS clean tree" justfile` — check present
   - C3: `cd agent-core && just setup` — check succeeds
   - M1: Manual test with session.md sample (continuation lines filtered)
   - M2: Manual test with `Plan:` (title case) in session.md
   - C4: `pytest -k test_merge_precommit_failure` — check exists and passes
   - C5: `pytest -k test_merge_idempotency` — check exists and passes

4. **Commit all changes**:
   ```bash
   git add -A
   git commit -m "🐛 Fix worktree-update critical findings and correctness bugs

   - C2: Add THEIRS clean tree check to wt-merge
   - C3: Add setup recipe to agent-core justfile
   - C4: Add precommit failure test
   - C5: Add merge idempotency test
   - M1: Fix _filter_section continuation line handling
   - M2: Fix plan_dir regex case-sensitivity

   Resolves 6 findings from deliverable review. C1 and R1 deferred to workwoods.
   "
   ```

**Success criteria met when:**
- All 6 steps completed without errors
- Test suite passes (all new tests green)
- Precommit clean
- Changes committed
