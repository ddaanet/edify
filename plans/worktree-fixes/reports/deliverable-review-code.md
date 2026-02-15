# Deliverable Review: Worktree Fixes Code

**Date:** 2026-02-15
**Reviewer:** Opus (delegated review task)
**Baseline:** `plans/worktree-fixes/design.md`
**Scope:** 4 files, 1,301 lines

## Summary

Overall conformance is strong. All 5 FRs are satisfied. The implementation follows the design closely with minor deviations that are defensible. Found 2 Major and 5 Minor issues, no Critical.

---

## Findings

### session.py (NEW, 264 lines)

**1. `session.py:54-58` | Conformance | Major**
`extract_task_blocks()` treats blank lines as block boundaries, terminating continuation line collection. The design spec says: "Block boundary: next task line, next `## ` header, or EOF" -- blank lines are not listed as boundaries. If a task block has a blank line between the task line and a continuation line (e.g., a spaced-out sub-bullet), the continuation would be lost. In practice, the session.md format doesn't use blank-line-separated continuations, so this works. But it silently deviates from the spec.

**2. `session.py:152-153` | Robustness | Major**
`move_task_to_worktree()` locates the task block for removal using `if line in task_block.lines` which matches any line in the file that equals any line in the block (including continuation lines). If a continuation line like `  - Plan: foo` appears earlier in the file in a different context, the function would match that earlier occurrence, set `task_start_idx` to the wrong line, and delete the wrong block. Should match against `task_block.lines[0]` specifically (like `remove_worktree_task` does at line 259).

**3. `session.py:164-165` | Robustness | Minor**
`move_task_to_worktree()` does not guard against `task_start_idx` being `None` before `del lines[task_start_idx:task_end_idx]`. If the block was returned by `extract_task_blocks()` but the content was re-read or mutated between extraction and this lookup, `task_start_idx` stays `None` and the `del` raises `TypeError`. Low probability since content is read once and not mutated, but the guard is absent.

**4. `session.py:191` | Conformance | Minor**
`_find_git_root()` uses `.resolve()` before traversal, consistent with the learning about relative path bugs. This is correct -- noting it as a positive conformance point.

### cli.py (Modified, 383 lines)

**5. `cli.py:23-36` | Conformance | Pass**
`derive_slug()` removes `max_length`, calls `validate_task_name_format()` before transformation, applies correct regex transformation. Matches design exactly. FR-1 satisfied.

**6. `cli.py:36` | Vacuity | Minor**
`return slug.rstrip("-")` is redundant after `strip("-")` on line 35. The `re.sub(r"[^a-z0-9]+", "-", ...)` followed by `.strip("-")` already removes trailing hyphens. The extra `rstrip("-")` does no harm but is dead code.

**7. `cli.py:63-85` | Conformance | Pass**
`focus_session()` uses `extract_task_blocks()` from session.py, preserving multi-line blocks. Matches design: "Replace single-line regex with `extract_task_blocks()`." FR-1 acceptance criterion met (pattern matching on constrained names works).

**8. `cli.py:265-297` | Conformance | Pass**
`new` command calls `move_task_to_worktree()` after `_setup_worktree()` only when `--task` flag provided. Edits main repo's session.md (not worktree copy). Matches design exactly. FR-6 (new side) satisfied.

**9. `cli.py:348-383` | Conformance | Pass**
`rm` command reorders operations: probe registrations, then `remove_worktree_task()`, then remove worktrees, then `git branch -d`. Session check happens before branch deletion. Matches design: "Check worktree branch state BEFORE `git branch -d`." FR-6 (rm side) satisfied.

### merge.py (Modified, 307 lines)

**10. `merge.py:72-73` | Conformance | Minor**
`_resolve_session_md_conflict()` calls `extract_task_blocks()` without section filter (extracts from all sections), while the design shows `extract_task_blocks(ours_content, section="Pending Tasks")`. The comment explains this is for legacy compatibility. Insertion still targets Pending Tasks section (line 80), so practical behavior is correct. However, if theirs has tasks in Worktree Tasks that ours doesn't, those would be treated as "new" and inserted into Pending Tasks, which could produce incorrect results during a merge of a worktree that moved tasks between sections.

**11. `merge.py:268-283` | Conformance | Pass**
`_phase4_merge_commit_and_precommit()` detects MERGE_HEAD via `git rev-parse --verify MERGE_HEAD`, uses `--allow-empty` when merge in progress. Matches design exactly. FR-5 satisfied.

**12. `merge.py:86-88` | Functional completeness | Minor**
New blocks are sorted by task name before insertion (`sorted(new_blocks, key=lambda b: b.name)`). The design doesn't specify ordering. This is a reasonable addition (deterministic output) but is excess relative to spec. Not harmful.

### validation/tasks.py (Modified, 347 lines)

**13. `tasks.py:21-49` | Conformance | Pass**
`validate_task_name_format()` checks empty/whitespace, forbidden characters via `re.fullmatch(r"[a-zA-Z0-9 .\-]+", name)`, and length <= 25. Returns list of error strings. Matches design spec character-for-character. FR-1 validation satisfied.

**14. `tasks.py:311-316` | Conformance | Pass**
`validate()` integrates `validate_task_name_format()` for each extracted task name, with line number and offending character in error message. Matches design error format. FR-2 satisfied.

**15. `tasks.py:16` | Conformance | Pass**
`TASK_PATTERN` requires ` —` (em dash) after `**name**`. `validate_task_name_format()` correctly validates the name portion only. Shared between `derive_slug()` and precommit. Design decision 6 (shared function) satisfied.

---

## FR Satisfaction Matrix

| FR | Status | Evidence |
|----|--------|----------|
| FR-1 | Satisfied | `validate_task_name_format()` in tasks.py, `derive_slug()` lossless, no truncation |
| FR-2 | Satisfied | `validate()` calls `validate_task_name_format()` per task, format errors with line numbers |
| FR-4 | Satisfied | `extract_task_blocks()` returns multi-line blocks, merge uses full blocks |
| FR-5 | Satisfied | MERGE_HEAD detection, `--allow-empty` flag in _phase4 |
| FR-6 | Satisfied | `move_task_to_worktree()` in new, `remove_worktree_task()` in rm, correct ordering |

## Test Coverage Assessment

| Area | Tests | Coverage |
|------|-------|---------|
| `extract_task_blocks()` | 4 tests (single, multi-line, section filter, mixed) | Good |
| `find_section_bounds()` | 2 tests (found, not found) | Adequate |
| `move_task_to_worktree()` | 5 tests (single-line, slug marker, create section, multiline, CLI E2E) | Good |
| `remove_worktree_task()` | 3 unit + 2 E2E tests (completed, still pending, branch state, CLI) | Good |
| `validate_task_name_format()` | 3 tests (valid, invalid chars, length) + integration | Good |
| `derive_slug()` validation | 2 tests (transform + format rejection) | Good |
| MERGE_HEAD detection | 1 test (empty diff + MERGE_HEAD) | Adequate |
| Session merge multi-line | 3 E2E tests (basic, multiline blocks, insertion position) | Good |

**Gap:** No test verifies `git branch -d` succeeds after empty-diff merge (FR-5 acceptance criterion #2). The MERGE_HEAD test verifies the commit is created and MERGE_HEAD removed, but doesn't test branch deletion.

**Gap:** No idempotency test for `move_task_to_worktree()` (design specifies idempotent: "no-op if slug not found in Worktree Tasks" for remove, but move's idempotency when task already in Worktree Tasks is tested only implicitly).

---

## Issue Summary

| # | File:Line | Axis | Severity | Description |
|---|-----------|------|----------|-------------|
| 1 | session.py:54-58 | Conformance | Major | Blank lines terminate task blocks; design says only task lines, headers, or EOF are boundaries |
| 2 | session.py:152-153 | Robustness | Major | `line in task_block.lines` matches any block line, not just the first; could match wrong location |
| 3 | session.py:164-165 | Robustness | Minor | No guard for `task_start_idx is None` before deletion |
| 4 | cli.py:36 | Vacuity | Minor | Redundant `rstrip("-")` after `strip("-")` |
| 5 | merge.py:72-73 | Conformance | Minor | No section filter on `extract_task_blocks()` -- could insert Worktree Tasks as Pending Tasks |
| 6 | merge.py:86-88 | Excess | Minor | Alphabetical sort of new blocks not in design spec |
| 7 | — | Completeness | Minor | No test for `git branch -d` succeeding after empty-diff merge |

**Critical: 0 | Major: 2 | Minor: 5**
