# Review: Phase 4 — Hook registration and permissions

**Scope**: `.claude/settings.json` (hook registration + recall-*.sh permission), `agent-core/hooks/pretooluse-recall-check.py`
**Date**: 2026-02-24
**Mode**: review + fix

## Summary

Phase 4 adds the PreToolUse hook and permission grant that constitute Layer 3 of the recall-tool-anchoring design. The hook script is clean and follows the pretooluse-recipe-redirect.py pattern. Settings.json changes are valid JSON with correct structure. One minor issue found: settings.json uses `python3` invocation for the new hook, inconsistent with the design intent (direct executable invocation preferred, as used for existing hooks in other matchers). However, looking at other Task hooks in the file, `python3` is consistent with all existing python hook invocations in this settings.json. No critical or major issues found.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Hook invocation style: `python3` prefix vs executable path**
   - Location: `.claude/settings.json:94`
   - Note: The new Task hook uses `python3 $CLAUDE_PROJECT_DIR/agent-core/hooks/pretooluse-recall-check.py`. Other Python hooks in the same file (submodule-safety.py:82, pretooluse-recipe-redirect.py:85, userpromptsubmit-shortcuts.py:124) all use the `python3` prefix form. `agent-core/bin/*.py` scripts are executable and invoked directly per CLAUDE.md, but hooks in `agent-core/hooks/` consistently use `python3` invocation. The new hook matches the hooks/ convention.
   - **Status**: OUT-OF-SCOPE — The hooks/ pattern uses `python3` prefix consistently; CLAUDE.md direct-invocation rule applies to `agent-core/bin/*.py` scripts only. No deviation exists.

## Fixes Applied

No fixes required. All items resolved as OUT-OF-SCOPE or found not to be issues.

## Design Anchoring (D-3 / Layer 3)

| Design requirement | Status | Evidence |
|---|---|---|
| PreToolUse hook on Task matcher | Satisfied | settings.json:91–96 |
| Detects `plans/<job>` path in prompt | Satisfied | pretooluse-recall-check.py:30 (`re.search(r"plans/([^/]+)/", prompt)`) |
| Checks recall-artifact.md existence | Satisfied | pretooluse-recall-check.py:35–37 |
| Missing → injects additionalContext warning | Satisfied | pretooluse-recall-check.py:19–26 (`additionalContext` key) |
| Warning, not block (soft enforcement) | Satisfied | `sys.exit(0)` on all paths — no blocking exit code |
| Hooks fire in main session only | Satisfied | Hook registered in project settings.json (not agent settings) |
| Pattern matches pretooluse-recipe-redirect.py | Satisfied | Same stdin JSON parse, same additionalContext output structure, same exit-0-always pattern |
| `Bash(agent-core/bin/recall-*:*)` permission | Satisfied | settings.json:20 |
| Hook registration | Satisfied | settings.json:91–96, matcher "Task" |

## Lifecycle Audit

Hook reads `sys.stdin` (JSON), writes `sys.stdout` (JSON). No file handles opened. No temp files created. No lock files. Both success path (artifact exists: `sys.exit(0)`) and warning path (artifact missing: print JSON + `sys.exit(0)`) close cleanly. The `try/except Exception: sys.exit(0)` guard at line 13 ensures malformed stdin never leaks an exception.

Defensive error handling note: `_check_recall` uses `os.path.exists()` not `os.path.isfile()`. If `recall-artifact.md` is a directory (unlikely but possible), hook silently passes. This is acceptable for a soft-enforcement warning hook — the recall scripts themselves enforce stricter validation.

## Positive Observations

- Error guard (`try/except Exception: sys.exit(0)`) ensures hook never blocks Claude on unexpected input — correct for a soft-enforcement hook
- Job extraction regex `r"plans/([^/]+)/"` correctly handles nested paths in prompts, extracting only the job name segment
- `os.path.join` used instead of string concatenation for path construction
- `sys.exit(0)` on all paths: hook is purely advisory, never blocks tool use
- Permission glob `Bash(agent-core/bin/recall-*:*)` covers all three recall-*.sh scripts with a single pattern
- Hook invocation style matches existing python hooks in settings.json (consistent pattern)
- `hookEventName: "PreToolUse"` correctly set in output (required by protocol)
