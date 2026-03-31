# Review: Phase 1 Checkpoint — Plugin Manifest and Structure

**Scope**: plugin submodule (plugin manifest + hooks.json), plans/plugin-migration/reports/step-1-3-report.md, plans/prototypes/validate-hooks-json.py
**Date**: 2026-03-20
**Mode**: review + fix

## Summary

Phase 1 delivers two artifacts inside the plugin submodule: `.claude-plugin/plugin.json` (plugin manifest) and `hooks/hooks.json` (plugin hook configuration in wrapper format). Both artifacts are structurally correct and consistent with the design and outline specs. The validation prototype and step report were added to document verification. `just dev` passes. One minor fix applied.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **validate-hooks-json.py uses relative path**
   - Location: `plans/prototypes/validate-hooks-json.py:4`
   - Note: `open("plugin/hooks/hooks.json")` only resolves correctly when the script is run from the project root. No documentation of the required working directory. Running from any other directory silently opens wrong path or raises FileNotFoundError.
   - **Status**: FIXED — added comment documenting run-from-project-root requirement

2. **Hook validation evidence conflates hook and sandbox**
   - Location: `plans/plugin-migration/reports/step-1-3-report.md` — Check 4 section
   - Note: The output `"The sandbox is blocking writes to both /tmp and the fallback temp directory"` is ambiguous. The Claude Code sandbox permissions deny rule (`Write(.claude/*)` and environment sandbox) also blocks `/tmp` writes independently of the hook. The report claims "Hook successfully prevented the `/tmp` write" but the evidence doesn't isolate the hook from the sandbox. The hook likely did fire (it's loaded alongside other hooks that verifiably fired in checks 1-3), but the validation output is not definitive proof.
   - **Status**: FIXED — updated Check 4 note to accurately reflect the ambiguity and that hook loading is inferred from checks 1-3, not directly proven by this output

## Fixes Applied

- `plans/prototypes/validate-hooks-json.py:4` — Added comment `# Run from project root` before the open() call to document the required working directory
- `plans/plugin-migration/reports/step-1-3-report.md` — Corrected Check 4 narrative to accurately describe what the output demonstrates (hook loaded alongside other hooks per checks 1-3; direct isolation from sandbox not possible from this output alone)

## Positive Observations

- `plugin.json` version `0.0.2` matches `pyproject.toml` version exactly — FR-12 satisfied
- hooks.json wrapper format (`{"hooks": {...}}`) is correct per the outline's D-4 correction (direct format was the design.md error; wrapper format is the outline-authoritative spec)
- All 9 hook entries present across 5 event types — matches runbook Step 1.2 spec exactly
- Command prefixes (`python3`, `bash`, implicit via shebang) match the source bindings in `.claude/settings.json` — runbook step 5 "Preserve existing command prefixes" satisfied
- `$CLAUDE_PLUGIN_ROOT` used throughout hooks.json (not `$CLAUDE_PROJECT_DIR`) — correct per D-2 hook configuration vs hook script distinction
- `pretooluse-symlink-redirect.sh` correctly NOT included in hooks.json (deferred to Phase 6 deletion per outline Component 6)
- Check 1-3 automated validations in step-1-3-report.md provide concrete evidence of plugin auto-discovery working
- NFR-1 check correctly deferred to human with clear procedure documented
