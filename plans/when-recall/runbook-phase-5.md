# Phase 5: Bin Script Wrapper

**Type:** General
**Model:** haiku
**Dependencies:** Phase 4 (CLI must be registered in claudeutils)
**Files:** `agent-core/bin/when-resolve.py`

**Design reference:** Component Architecture (agent-core/bin/when-resolve.py)

---

## Step 5.1: Create bin script with shebang

**Objective:** Create `agent-core/bin/when-resolve.py` as a thin wrapper that invokes the claudeutils when command.

**Implementation:**
- Create file with `#!/usr/bin/env python3` shebang
- Import and call `claudeutils.when.cli.when_cmd()`
- Pass through sys.argv arguments
- Make file executable (`chmod +x`)

**Expected Outcome:** `agent-core/bin/when-resolve.py when "writing mock tests"` invokes the resolver and outputs content.

**Error Conditions:**
- Import error → claudeutils not installed in environment (run `uv sync`)
- Permission denied → file not executable

**Validation:** `agent-core/bin/when-resolve.py --help` shows usage text

---

## Step 5.2: Verify end-to-end invocation

**Objective:** Confirm the bin script works as a standalone entry point.

**Implementation:**
- Run `agent-core/bin/when-resolve.py when .` to test section mode
- Run `agent-core/bin/when-resolve.py how .` to test how operator
- Verify output matches `claudeutils when` command output

**Expected Outcome:** Bin script produces identical output to `claudeutils when` CLI command.

**Error Conditions:**
- Shebang not finding python3 → verify `#!/usr/bin/env python3`
- Module not found → verify PYTHONPATH or editable install

**Validation:** Output of bin script matches `claudeutils when` output for same arguments
