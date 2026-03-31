# Runbook Review: Phase 4 — Justfile Modularization

**Artifact**: plans/plugin-migration/runbook-phase-4.md
**Date**: 2026-03-14T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (2 steps)

## Summary

Phase 4 covers justfile modularization: extracting portable recipes into plugin-distributed module(s) and updating the root justfile to import them. The phase structure is sound and covers the D-5 dependency correctly. Three issues were found and fixed: an architecturally incomplete bash prolog definition missing required functions, a recipe name mismatch (`red` vs actual `red-lint`), and a stale assumption about `.cache/just-help*.txt` existing before this phase runs.

**Overall Assessment**: Ready (all issues fixed)

## Findings

### Critical Issues

None.

### Major Issues

1. **Bash prolog definition architecturally incomplete**
   - Location: Step 4.1, Implementation item 5 (prolog block)
   - Problem: The prolog block showed just-level variable assignments (`fail := 'echo "FAIL:" && exit 1'`, `visible := 'echo'`) but the justfile uses `#!{{ bash_prolog }}` as the recipe shebang — which requires `bash_prolog` to be a string containing a full bash shebang line plus bash function definitions. The shown snippet would produce a prolog string that starts with the first function variable, not `#!/usr/bin/env bash`, causing syntax errors at runtime. Additionally, `safe` and `end-safe` (needed by `lint`/`check`) and the proper `visible`/`fail` function bodies (needed by `wt-*`) were absent.
   - Fix: Replaced the variable snippet with a proper `bash_prolog` string variable definition following the same pattern as the root justfile, including all required bash functions (`safe`, `end-safe`, `show`, `visible`, `fail`) and color variables. Added note that variable merging means root's `bash_prolog` overrides in the root project context (correct behavior).
   - **Status**: FIXED

### Minor Issues

1. **Recipe name mismatch: `red` vs `red-lint`**
   - Location: Step 4.1, Implementation item 3; Step 4.2, Implementation item 3
   - Problem: Both steps refer to a recipe named `red`. The actual recipe in `justfile` is `red-lint` (line 345). D-5 in the outline uses `red` as shorthand but the actual implementation name differs.
   - Fix: Updated both occurrences to `red-lint` with a parenthetical note explaining the D-5 shorthand vs actual name.
   - **Status**: FIXED

2. **`.cache/just-help*.txt` assumes files exist**
   - Location: Step 4.2, Implementation item 5; Validation last bullet
   - Problem: Step says "Regenerate cached help files" and validation says "Regenerated `.cache/just-help*.txt` files" — but `.cache/just-help.txt` does not currently exist in the repo. Using "regenerate" implies overwriting existing files; the executor may skip the step if they don't find the files or fail if the `.cache/` directory doesn't exist.
   - Fix: Changed to "Generate or regenerate" with an explicit `just --list > .cache/just-help.txt` command and a note to create `.cache/` first if needed. Scoped `just-help-edify-plugin.txt` to "generate only if referenced."
   - **Status**: FIXED

3. **Thematic module validation missing**
   - Location: Step 4.1, Validation section
   - Problem: Validation only specified the single-file case (`just --justfile plugin/portable.just --list`). The thematic module path (if D-5 redesign occurs) had no validation command.
   - Fix: Added thematic-case validation (`just --justfile plugin/<module>.just --list` for each module) and a prolog verification command.
   - **Status**: FIXED

## Fixes Applied

- Step 4.1, item 3: `red` → `red-lint` with parenthetical note on D-5 naming
- Step 4.1, item 5: Replaced incomplete variable snippet with proper `bash_prolog` string variable definition including all required bash functions; added variable-merging behavior note
- Step 4.1, Validation: Added thematic-module validation variant and prolog evaluation command
- Step 4.2, item 3: Updated recipe removal list to use `red-lint` and explicit `wt-*` recipe names
- Step 4.2, item 5: Changed "Regenerate" to "Generate or regenerate" with explicit command and `.cache/` directory creation note
- Step 4.2, Validation: Updated final bullet to remove "Regenerated" assumption

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
