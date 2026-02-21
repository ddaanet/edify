# Step 3.1

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 3.1: Create Auto-Format Script

**Objective:** Create `agent-core/hooks/posttooluse-autoformat.sh` that runs ruff + docformatter on Python files after Write/Edit completes.

**Script Evaluation:** Medium — new Bash script with JSON parsing via python3 -c subprocess, conditional execution, tool availability checks.

**Execution Model:** Haiku

**Prerequisite:**
- Verify `which ruff` → ruff is available at known path
- Verify `which docformatter` → docformatter availability (script handles missing gracefully)
- Read `.claude/settings.json` hooks section to confirm Write|Edit PostToolUse hook structure expected

**Implementation:**

Script logic (ordered):
1. Read stdin JSON — use `python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null` to extract `file_path`
2. If `file_path` is empty → exit 0 (no file to format)
3. If file does not end in `.py` → exit 0 (skip non-Python files)
4. Run: `ruff check --fix-only --quiet "$file_path"` (auto-fix linting issues)
5. Run: `ruff format --quiet "$file_path"` (format)
6. If `command -v docformatter >/dev/null 2>&1`: run `docformatter --in-place "$file_path"` (optional)
7. Silent on success — no stdout output
8. Any errors go to stderr (non-fatal) — ruff calls run normally under `set -euo pipefail` (non-zero exit surfaces to stderr via shell exit); docformatter call uses `|| true` because it is optional and absence is non-fatal

Script header:
```
#!/usr/bin/env bash
set -euo pipefail
```

Note: `set -euo pipefail` combined with explicit `|| true` on optional docformatter prevents early exit on missing tool.

**Expected Outcome:** Script file created at `agent-core/hooks/posttooluse-autoformat.sh` with execute permissions. Script parses PostToolUse stdin JSON, formats `.py` files with ruff, optionally runs docformatter.

**Error Conditions:**
- python3 not available → STOP, report (python3 required by other hooks; this is a system issue)
- ruff not available → log to stderr, exit 0 (non-fatal — formatting is best-effort)
- docformatter not available → skip silently (optional tool)
- file_path extraction fails → exit 0 (non-fatal pass-through)

**Validation:**
```bash
# Set execute permissions
chmod +x agent-core/hooks/posttooluse-autoformat.sh

# Test 1: Python file formatting
echo '{"tool_name":"Write","tool_input":{"file_path":"agent-core/hooks/posttooluse-autoformat.sh"}}' \
  | bash agent-core/hooks/posttooluse-autoformat.sh
# Expected: silent (sh file, not .py — gets skipped)

# Test 2: Non-.py file skip
echo '{"tool_name":"Write","tool_input":{"file_path":"README.md"}}' \
  | bash agent-core/hooks/posttooluse-autoformat.sh
# Expected: silent, exit 0

# Test 3: Empty tool_input
echo '{"tool_name":"Write","tool_input":{}}' \
  | bash agent-core/hooks/posttooluse-autoformat.sh
# Expected: silent, exit 0

# Test 4: Python file (use a real .py file to verify ruff runs)
echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"agent-core/hooks/userpromptsubmit-shortcuts.py\"}}" \
  | bash agent-core/hooks/posttooluse-autoformat.sh
# Expected: silent (ruff runs, no output on already-formatted file)
```

---
