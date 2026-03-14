# Cycle 6.5

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Staging, submodule coordination, amend semantics, structured output.

---

---

## Cycle 6.5: Output formatting

**RED Phase:**

**Test:** `test_format_success_parent`, `test_format_success_submodule`, `test_format_warning`, `test_format_failure`
**File:** `tests/test_session_commit_pipeline.py`

**Assertions:**
- `format_commit_output(result)` with parent-only success:
  ```
  [session-cli-tool a7f38c2] ✨ Add commit CLI
   3 files changed, 142 insertions(+), 8 deletions(-)
  ```
  Raw git output, no prefix
- With submodule success:
  ```
  agent-core:
  [session-cli-tool 4b2c1a0] 🤖 Update fragment
   1 file changed, 5 insertions(+), 2 deletions(-)
  [session-cli-tool a7f38c2] ✨ Add commit CLI
   4 files changed, 142 insertions(+), 8 deletions(-)
  ```
  Submodule output labeled with `<path>:`, parent unlabeled
- Warning + success:
  ```
  **Warning:** Submodule message provided but no changes found for: agent-core. Ignored.

  [session-cli-tool a7f38c2] ✨ Add commit CLI
  ```
  Warning prepended to git output
- Failure: gate-specific diagnostic (vet, precommit, clean-files) — format varies by gate

**Expected failure:** No dedicated formatting function

**Why it fails:** Output formatting inline in pipeline, not testable in isolation

**Verify RED:** `pytest tests/test_session_commit_pipeline.py::test_format_success_parent -v`

---
