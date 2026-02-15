# Vet Review: Phase 2 — Session automation (FR-6)

**Scope**: Phase 2 implementation — FR-6 (Automate session.md task movement on worktree create and remove)
**Date**: 2026-02-15T15:30:00
**Mode**: review + fix

## Summary

Phase 2 implements session.md task automation for worktree lifecycle operations. Implementation satisfies all FR-6 requirements and matches design decisions. Code quality is high with comprehensive E2E tests. Found 3 major issues and 6 minor issues, all fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None found.

### Major Issues

1. **Task block removal uses fragile line matching**
   - Location: session.py:250
   - Problem: `if line in task_block.lines` matches by content, fails if multiple identical lines exist in file
   - Fix: Match by line index from original search (session.py:145-151 already does this correctly)
   - **Status**: FIXED

2. **Missing newline after task block insertion**
   - Location: session.py:176-178
   - Problem: Task blocks inserted without trailing blank line, may run into next section header
   - Fix: Add blank line after task block insertion in move_task_to_worktree
   - **Status**: FIXED

3. **Idempotency gap in move_task_to_worktree**
   - Location: session.py:118-181
   - Problem: Re-running move_task_to_worktree when task already in Worktree Tasks will find it in Pending (ValueError), but it's already moved
   - Fix: Check both sections before raising ValueError
   - **Status**: FIXED

### Minor Issues

1. **Inconsistent blank line handling in section creation**
   - Location: session.py:168
   - Note: Creates blank line before section header, but doesn't add blank after (insertion point handles it implicitly)
   - **Status**: FIXED

2. **No validation that session.md exists in cli.py:290**
   - Location: cli.py:290
   - Note: move_task_to_worktree will raise if session.md doesn't exist, but error is generic FileNotFoundError
   - **Status**: FIXED

3. **Git root detection could fail in edge cases**
   - Location: session.py:184-190
   - Note: Returns start_path if no .git found, caller gets confusing subprocess errors later
   - **Status**: FIXED

4. **Test uses raw string for escaped backticks**
   - Location: test_worktree_session_automation.py:29
   - Note: `r"""...\`/runbook\`..."""` — raw strings don't need backslash escaping, just use regular strings
   - **Status**: FIXED

5. **Test assertion could be clearer**
   - Location: test_worktree_session_automation.py:106
   - Note: `"## Worktree Tasks" not in final_session or "Feature A" not in final_session` — ambiguous if section exists but task removed vs section removed
   - **Status**: FIXED

6. **Variable naming inconsistency**
   - Location: session.py:196-209
   - Note: Function name is `_task_is_pending_in_branch` but checks extracted blocks for any match — could be clearer as `_task_is_in_pending_section`
   - **Status**: FIXED

## Fixes Applied

- session.py:250-254 — Changed task block removal to use original line index from search, not content matching
- session.py:178 — Added blank line insertion after task block in move_task_to_worktree
- session.py:133-143 — Added check for task in Worktree Tasks before raising ValueError in move_task_to_worktree
- session.py:168 — Removed redundant blank line before section header (insertion adds one)
- cli.py:289-290 — Added session.md existence check before move_task_to_worktree call
- session.py:190 — Changed _find_git_root to raise ValueError instead of returning start_path when no .git found
- test_worktree_session_automation.py:25,36,64,120,144 — Changed raw strings to regular strings (no escaping needed)
- test_worktree_session_automation.py:106,169 — Split assertion into two checks (section exists, task removed)
- session.py:193 — Renamed function to _task_is_in_pending_section for clarity

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| `new --task` edits main repo session.md | Satisfied | cli.py:290 calls move_task_to_worktree(session_md_path, task_name, slug) where session_md_path is main repo path |
| `rm` removes worktree task when completed | Satisfied | cli.py:359 calls remove_worktree_task, session.py:244-246 checks branch state and removes if not pending |
| `rm` preserves worktree task when still pending | Satisfied | session.py:245-246 returns early if task still in branch Pending Tasks |
| Skill Mode A/B/C steps become no-ops | Deferred | Phase 3 SKILL.md edits (out of Phase 2 scope) |
| Idempotent operations | Satisfied | remove_worktree_task returns early if slug not found (line 234-235), move_task_to_worktree now checks both sections |

**Gaps:** None for Phase 2 implementation scope.

---

## Positive Observations

- E2E testing approach with real git repos provides high confidence (test_worktree_session_automation.py)
- Clean separation of concerns: session.py handles parsing/editing, cli.py handles orchestration
- Task block extraction reused from Phase 1 (extract_task_blocks, find_section_bounds)
- Git show command usage avoids coupling to merge resolution internals (design decision #3)
- Proper sequencing in rm command: check branch state before deletion (design constraint satisfied)
- Helper functions well-factored (_find_git_root, _task_is_in_pending_section)
- Comprehensive test coverage for both unit (test_worktree_session_remove.py) and E2E (test_worktree_session_automation.py)

## Recommendations

None — Phase 2 implementation is complete and correct. Phase 3 SKILL.md prose edits can proceed inline.
