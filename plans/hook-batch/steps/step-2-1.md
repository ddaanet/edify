# Cycle 2.1

**Plan**: `plans/hook-batch/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Cycle 2.1: Script Structure and Silent Pass-Through

**Objective:** Create script skeleton that reads stdin JSON, extracts `tool_input.command`, exits 0 silently for unmatched commands.

---

**RED Phase:**

**Test:** `test_script_loads`
**File:** `tests/test_pretooluse_recipe_redirect.py` — create new file with HOOK_PATH definition and `call_hook()` helper

**HOOK_PATH setup:**
```
HOOK_PATH = Path(__file__).parent.parent / "agent-core" / "hooks" / "pretooluse-recipe-redirect.py"
```

Load with importlib.util (same pattern as test_userpromptsubmit_shortcuts.py). Test that `HOOK_PATH.exists()` is True and module loads without error.

**Assertions for test_script_loads:**
- `HOOK_PATH.exists()` is `True`
- Module loads without ImportError

**Test:** `test_unknown_command_silent_passthrough`

**Assertions:**
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "echo hello"}})` returns `{}` (empty dict — exit 0, no output)
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "pytest tests/"}})` returns `{}`
- `call_hook({"tool_name": "Bash", "tool_input": {"command": "just test"}})` returns `{}`

**Test:** `test_missing_command_field_passthrough`

**Assertions:**
- `call_hook({"tool_name": "Bash", "tool_input": {}})` returns `{}` (no `command` key — graceful default, no crash)
- `call_hook({"tool_name": "Bash"})` returns `{}` (no `tool_input` key — graceful default)

**Test:** `test_output_format_when_match_exists`
(placeholder test to verify output format — will pass after Cycle 2.2 adds pattern logic, but structure is verified here)

**Assertions:**
- When a redirect fires (e.g., `"ln -sf ..."` command), result dict has key `"hookSpecificOutput"`
- `result["hookSpecificOutput"]["hookEventName"]` equals `"PreToolUse"`
- `result["hookSpecificOutput"]` has key `"additionalContext"` with a non-empty string
- Result does NOT have a `"systemMessage"` key (D-6: additionalContext only)

Note: `test_output_format_when_match_exists` will remain failing (RED) until Cycle 2.2 adds the redirect.

**call_hook() helper signature:**
```python
def call_hook(hook_input: dict) -> dict:
    # serialize hook_input to JSON → stdin
    # capture stdout → parse JSON or return {} on empty/exit-0
```

**Expected failure:**
- `test_script_loads`: `AssertionError` — `HOOK_PATH.exists()` is False (file doesn't exist yet)
- `test_unknown_command_silent_passthrough`: `ModuleNotFoundError` or `RuntimeError` loading missing file

**Why it fails:** `agent-core/hooks/pretooluse-recipe-redirect.py` does not exist.

**Verify RED:** `pytest tests/test_pretooluse_recipe_redirect.py::test_script_loads -v`

---

**GREEN Phase:**

**Implementation:** Create `agent-core/hooks/pretooluse-recipe-redirect.py` with stdin parsing and pass-through.

**Behavior:**
- Shebang: `#!/usr/bin/env python3`
- Read stdin as JSON — `json.load(sys.stdin)`
- Extract `tool_input.command` — `hook_input.get('tool_input', {}).get('command', '')`
- If no redirect matches: `sys.exit(0)` with no output (silent pass-through)
- `main()` function callable from tests; `if __name__ == '__main__': main()`

**Approach:** Minimal script — import json, sys; main() reads and exits. Redirect logic added in Cycle 2.2.

**Output format (for Cycle 2.2 reference):**
```python
output = {
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'additionalContext': '<redirect message>'
    }
    # NO 'systemMessage' key (D-6: informative only)
}
print(json.dumps(output))
```

**Changes:**
- File: `agent-core/hooks/pretooluse-recipe-redirect.py`
  Action: Create new file with main() function
  Location hint: new file in `agent-core/hooks/`
- File: `tests/test_pretooluse_recipe_redirect.py`
  Action: Create new test file with HOOK_PATH, call_hook() helper, and test classes

**Verify GREEN:** `pytest tests/test_pretooluse_recipe_redirect.py -v -k "not test_output_format_when_match_exists"`
(Note: `test_output_format_when_match_exists` stays failing until Cycle 2.2 — this is expected)
**Verify no regression:** `pytest tests/test_userpromptsubmit_shortcuts.py -v`

---
