# Cycle 4.2 Refactoring Report

## Summary

**Status:** Escalated — architectural refactoring needed

## Issue

Line limit violations in both files after Cycle 4.2 section filtering implementation:
- `src/claudeutils/worktree/cli.py`: 477 lines (77 over 400-line limit)
- `tests/test_worktree_cli.py`: 445 lines (45 over 400-line limit)

## Attempted Refactoring

Applied deslop principles and code consolidation:

### cli.py reductions (477 → 412 lines formatted):
- Inline chained `.stdout.strip()` calls instead of intermediate variables
- Consolidated conditional logic in `wt_path()`, `clean_tree()`, `focus_session()`
- Extracted `_build_tree_with_session()` helper from `_create_session_commit()`
- Merged nested if statements (SIM102 fix)
- Simplified `derive_slug()` to single-expression chain
- Reduced verbosity in subprocess calls

### test_worktree_cli.py reductions (445 → 376 lines):
- Merged `test_derive_slug()` and `test_derive_slug_edge_cases()` (duplicate consolidation)
- Removed redundant assertions (isinstance checks, intermediate variables)
- Consolidated deduplication test assertions
- Streamlined focus_session test assertions

## Root Cause: Formatter Expansion

Black formatter consistently re-expands subprocess command lists:

**Before formatting (397 lines):**
```python
subprocess.run(["git", "hash-object", "-w", "--stdin"], input=content, capture_output=True, text=True, check=True)
```

**After formatting (412 lines):**
```python
subprocess.run(
    ["git", "hash-object", "-w", "--stdin"],
    input=content,
    capture_output=True,
    text=True,
    check=True,
)
```

15-line expansion across 6-8 subprocess calls.

## Escalation Reason

**Architectural change required:** Extract git operations to separate module.

Current structure:
- All git worktree logic in single 400+ line CLI module
- 10+ subprocess calls with long argument lists
- Formatter enforces vertical expansion for readability

Solutions require module extraction:
1. Extract git tree operations to `worktree/git_ops.py`
2. Extract session filtering to `worktree/session.py`
3. Create `worktree/porcelain.py` for git porcelain parsing

This is beyond "refactor within module" — requires architectural restructuring with new module boundaries.

## Current State

- Functionality: All 765/766 tests passing (1 xfail)
- Quality: No mypy/ruff errors
- Line limits: cli.py at 412 lines (12 over), test at 376 lines (within limit)
- Deslop applied: Removed 65 lines via consolidation
- Formatter conflict: Adds back 15 lines

## Recommendation

Escalate to Opus for module extraction design:
- Define module boundaries for worktree package
- Design clean interfaces between CLI, git ops, and session filtering
- Maintain all functionality and test coverage
- Target: Each module ≤400 lines after formatting

