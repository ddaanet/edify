# Runbook Review: plugin-migration Phase 2

**Artifact**: `plans/plugin-migration/runbook-phase-2.md`
**Date**: 2026-03-14T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (4 steps)

## Summary

Phase 2 covers hook script audit, env var fixes, creation of `edify-setup.sh`, and wiring into `hooks.json`. Steps have clear objectives, prerequisites, expected outcomes, and error conditions. Three minor issues fixed: incorrect `uv pip install` flag syntax (passing venv directory to `--python` which expects an interpreter path), missing wrapper-format context in the Step 2.4 JSON snippet, and bare relative path in Step 2.3 validation without an execution context note. No unfixable issues.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`uv pip install --python` receives venv directory instead of interpreter path**
   - Location: Step 2.3, Implementation step 2b
   - Problem: `uv pip install --python "$CLAUDE_PLUGIN_ROOT/.venv"` passes a venv directory path to `--python`, which expects a Python interpreter path (e.g., `.venv/bin/python`). This would fail at runtime. The outline specifies intent (install into plugin-local venv) without prescribing the exact invocation.
   - Fix: Replaced with two-step approach — create venv with `uv venv` if not already present, then install via `uv pip install --python "$CLAUDE_PLUGIN_ROOT/.venv/bin/python"`. Corrected pip fallback to use `--target` for install isolation.
   - **Status**: FIXED

2. **Step 2.4 JSON snippet lacks wrapper-format context**
   - Location: Step 2.4, Implementation steps 1-2
   - Problem: The JSON snippet shows only the `"SessionStart"` array value. After Phase 1 rewrites `hooks.json` to wrapper format (`{"hooks": {"SessionStart": [...], ...}}`), an executor needs to know this is an edit within the existing `"hooks"` key — not a full file replacement. Missing context could cause the executor to replace the entire file with only the SessionStart fragment.
   - Fix: Added clarifying note to step 1 ("file is in wrapper format after Phase 1 rewrites it") and a parenthetical after the snippet noting it shows the `"SessionStart"` key value within `"hooks"`, not a standalone JSON document.
   - **Status**: FIXED

3. **Step 2.3 validation uses bare relative path without execution context note**
   - Location: Step 2.3, Validation
   - Problem: `bash plugin/hooks/edify-setup.sh` is a relative path that resolves correctly only when run from the project root. No note indicates this constraint.
   - Fix: Added "from project root" qualifier to the validation command.
   - **Status**: FIXED

## Fixes Applied

- Step 2.3, Implementation 2b — Corrected `uv pip install` invocation: added venv creation step (`uv venv`), fixed `--python` flag to point to interpreter path (`/bin/python`), corrected pip fallback to use `--target`
- Step 2.4, Implementation 1+2 — Added wrapper-format context note to step 1; added parenthetical after JSON snippet clarifying it shows the `"SessionStart"` key value within `"hooks"`, not a standalone document
- Step 2.3, Validation — Added "from project root" qualifier to `bash plugin/hooks/edify-setup.sh`

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
