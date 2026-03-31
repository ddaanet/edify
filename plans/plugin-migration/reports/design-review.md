# Design Review: Plugin Migration

**Design Document**: `plans/plugin-migration/design.md`
**Review Date**: 2026-02-07
**Reviewer**: design-vet-agent (opus)

## Summary

The design converts plugin from a symlink-based distribution model to a Claude Code plugin with auto-discovery. It covers 8 components spanning plugin manifest, hook migration, fragment versioning, init/update skills, justfile modularization, symlink cleanup, post-upgrade version check, and script path updates. The document is well-structured with clear rationale for each design decision and correctly identifies the critical `$CLAUDE_PROJECT_DIR` vs `$CLAUDE_PLUGIN_ROOT` distinction.

**Overall Assessment**: Needs Minor Changes

After applying fixes, the design is ready for planning. The remaining recommendations are non-blocking suggestions for the planner to consider during implementation.

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Symlink count discrepancy (skills)**
   - Problem: Design claimed "17 symlinks" in `.claude/skills/` (Component 6, step 1) but actual count is 16. Verified via `ls -la .claude/skills/ | grep '^l' | wc -l` = 16, matching the 16 skill directories in `plugin/skills/`.
   - Impact: Incorrect count could cause planner to expect an extra symlink or miss validation.
   - Fix Applied: Changed "17 symlinks" to "16 symlinks" in Component 6.

2. **Fragment count discrepancy**
   - Problem: Directory layout said "19 instruction fragments" but `plugin/fragments/` contains 20 files (including `workflows-terminology.md`).
   - Impact: Minor mismatch, but could cause confusion during validation.
   - Fix Applied: Changed "19" to "20" in directory layout.

3. **`/edify:update` skill underspecified**
   - Problem: Listed in Affected Files (Create) and referenced in FR-4 but had no dedicated behavioral description. Component 4 only said "a separate skill (or alias) for fragment re-sync" without defining its scope, behavior, or relationship to `/edify:init`.
   - Impact: Planner would lack guidance on what to implement for the update skill.
   - Fix Applied: Added full `/edify:update` specification after Component 4's idempotency guarantee: separate skill, re-copies fragments, updates version marker, skips scaffolding, no-op in dev mode.

4. **Missing fragment documentation updates from affected files**
   - Problem: Four fragment files reference `just sync-to-parent` (`claude-config-layout.md`, `sandbox-exemptions.md`, `project-tooling.md`, `delegation.md`) but were not listed in Affected Files (Modify). Component 6 mentions symlink cleanup steps but omits the documentation updates the outline (line 112) correctly identified.
   - Impact: Planner would miss updating these fragments, leaving stale references to a deleted recipe.
   - Fix Applied: Added all four fragment files to Affected Files (Modify) with specific change descriptions.

5. **Justfile `bash_prolog` variable scoping across `import` boundaries**
   - Problem: Design stated "Bash prolog stays in root justfile" but the `wt-*` recipes being extracted to `portable.just` depend on `bash_prolog` functions (`fail`, `visible`, color variables like `GREEN`, `NORMAL`, `COMMAND`). Just's `import` does NOT share variables across file boundaries.
   - Impact: Extracted recipes would fail at runtime — missing function definitions.
   - Fix Applied: Expanded the `import` documentation in Component 5 to clarify that `portable.just` must define its own minimal `bash_prolog` (or equivalent) with the subset of helpers needed by portable recipes.

6. **Cache file regeneration missing from affected files**
   - Problem: `.cache/just-help.txt` and `.cache/just-help-plugin.txt` are generated from justfile content and loaded via CLAUDE.md `@` references. Changes to both justfiles (root: import + recipe removal; plugin: sync-to-parent removal) invalidate these caches.
   - Impact: Stale cache would show incorrect recipe lists in CLAUDE.md context.
   - Fix Applied: Added both cache files to Affected Files (Modify).

### Minor Issues

1. **Temp file path conflict in Component 7**
   - Problem: Once-per-session gating suggested `/tmp/edify-version-checked-$SESSION_ID` as a possible path. The project's own `pretooluse-block-tmp.sh` hook blocks writes to system `/tmp/`.
   - Fix Applied: Removed the `/tmp/` option, kept only `$CLAUDE_PROJECT_DIR/tmp/.edify-version-checked`, and added a note about the system `/tmp/` conflict.

2. **Incomplete directory layout**
   - Problem: Directory layout omitted several existing directories: `.claude/` (plugin's own dev config), `docs/`, `scripts/`, `migrations/`, `Makefile`, `README.md`.
   - Fix Applied: Added all missing directories and files to the layout tree for completeness.

3. **Outline naming drift unacknowledged**
   - Problem: The outline still uses pre-decision naming (`/ac:init`, `.ac-version`) while the design uses `/edify:*`. A planner reading both documents could be confused.
   - Fix Applied: Added a "Naming note" in the Requirements section explicitly stating the design supersedes outline naming.

4. **`precommit-base` consumer mode ambiguity**
   - Problem: Recipe extraction rules mentioned both `$CLAUDE_PLUGIN_ROOT/bin/` and `plugin/bin/` paths without clarifying which applies to this migration.
   - Fix Applied: Clarified that `precommit-base` uses `plugin/bin/` paths for dev mode only, with consumer mode deferred per D-7.

5. **Root justfile cache rebuild note**
   - Problem: Root justfile changes section didn't mention that imported recipes affect `just --list` output, which feeds into the CLAUDE.md `@` cached reference.
   - Fix Applied: Added cache rebuild note to root justfile changes list.

## Requirements Alignment

**Requirements Source:** inline (design document Requirements section)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Components 1-2: plugin manifest + hook migration |
| FR-2 | Yes | Component 5: `claude`/`claude0` recipes in portable.just |
| FR-3 | Yes | Component 4: `/edify:init` skill with full behavioral spec |
| FR-4 | Yes | Components 3-4: versioning system + `/edify:update` skill (clarified in fix) |
| FR-5 | Yes | Component 7: UserPromptSubmit version-check hook |
| FR-6 | Yes | Component 5: `import` mechanism for portable recipes |
| FR-7 | Yes | Component 6: symlink cleanup with validation gates |
| FR-8 | Yes | Component 1: coexistence via separate discovery paths |
| FR-9 | Yes | Component 2: hooks.json + settings.json cleanup |
| NFR-1 | Yes | `--plugin-dir` live loading in dev mode |
| NFR-2 | Partial | "Validated post-migration" — no specific measurement method defined |

**Gaps:**
- NFR-2 lacks a concrete validation method. Consider: count tokens in CLAUDE.md context before/after migration, or compare Claude Code's reported context size.

## Positive Observations

- **D-2 (Hook Script Analysis)** is excellent. The `$CLAUDE_PROJECT_DIR` vs `$CLAUDE_PLUGIN_ROOT` distinction is the most common error in plugin migrations, and the design explicitly identifies and corrects the explore report's incorrect recommendation. This alone prevents a significant implementation bug.
- **Rollback strategy** is well-designed with Component 6 as the clear point of no return. The ability to fall back to `just sync-to-parent` during intermediate states is practical.
- **Consumer mode deferral (D-7)** is pragmatic. The design documents consumer mode behavior without implementing it, preventing scope creep while maintaining forward compatibility.
- **Component dependency ordering** is correct. The manifest foundation (1) enables hooks (2), versioning (3) enables init/update (4, 7), and symlink cleanup (6) is last.
- **hooks.json format** correctly uses the wrapper `{"hooks": {...}}` structure and includes appropriate `matcher` and `timeout` fields matching current settings.json behavior.
- **Testing strategy** covers all components with appropriate manual verification methods.

## Recommendations

1. **NFR-2 validation method**: Define a concrete approach for measuring token overhead. For example: capture Claude Code's `/context` output before and after migration to compare loaded context sizes.

2. **`.gitignore` updates**: Component 6 step 7 says "Update `.gitignore` if needed" but doesn't specify what changes. Since symlinks in `.claude/` are tracked in git, their removal means the directories may need `.gitkeep` files or `.gitignore` adjustments. Planner should audit `.gitignore` during implementation.

3. **`precommit-base` validator paths**: The `precommit-base` recipe will call `plugin/bin/validate-*.py` scripts. These validators may reference project-specific paths (e.g., `agents/session.md`, `agents/learnings.md`). Verify they work correctly when invoked from an imported recipe context where CWD is the project root.

4. **Hook testing sequence**: The testing strategy lists "Manual hook testing" but doesn't specify the test procedure. The existing `test-hooks.md` agent could be leveraged for systematic hook verification post-migration.

## Next Steps

1. All fixes applied directly to `plans/plugin-migration/design.md` -- no further design changes needed
2. Proceed to `/plan-adhoc plans/plugin-migration/design.md` for runbook creation
3. Load `plugin-dev:plugin-structure` and `plugin-dev:hook-development` skills before planning
