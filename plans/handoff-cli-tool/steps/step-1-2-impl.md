# Cycle 1.2

**Plan**: `plans/handoff-cli-tool/runbook-rework.md`
**Execution Model**: sonnet
**Phase**: 1

---

**GREEN Phase:**

**Implementation:** Reorder pipeline: validation before irrevocable commits

**Behavior:**
- New order: validate_files → stage parent → validate (precommit/vet) → commit submodules → commit parent
- If validation fails, no submodule commits made — clean recovery possible
- Staging parent files before validation lets precommit see the staged state

**Changes:**
- File: `commit_pipeline.py`
  Action: Move parent staging and `_validate` call before submodule commit loop
  Location: `commit_pipeline` function — reorder the four blocks

**Verify GREEN:** `just green`
