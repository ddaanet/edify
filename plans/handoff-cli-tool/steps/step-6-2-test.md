# Cycle 6.2

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

## Cycle 6.2: Submodule coordination (C-2)

**RED Phase:**

**Test:** `test_commit_with_submodule`, `test_commit_submodule_no_message`, `test_commit_submodule_orphan_message`, `test_commit_no_submodule_changes`
**File:** `tests/test_session_commit_pipeline.py`

Tests use real git repos with submodules via `tmp_path` (shared fixture).

**Assertions — four-cell matrix from C-2:**

| Submodule files in Files | `## Submodule` present | Expected |
|---|---|---|
| Yes | Yes | Submodule committed first, pointer staged, parent committed. Output has `<path>:` prefix for submodule |
| Yes | No | `CommitResult(success=False)`, output contains `**Error:**` about missing submodule message. Exit 1 |
| No | Yes | `CommitResult(success=True)`, output contains `**Warning:**` about orphaned submodule message. Warning prepended to git output |
| No | No | Parent-only commit (same as 6.1) |

**Submodule commit sequence:**
- Files partitioned by submodule path prefix
- Per-submodule: `git -C <path> add <files>` → `git -C <path> commit -m <submodule_message>`
- Stage submodule pointer: `git add <path>`
- Parent commit includes pointer change

**Expected failure:** Pipeline doesn't handle submodule files

**Why it fails:** No submodule partitioning or coordination logic

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_commit_with_submodule -v`

---
