# Outline Review: plugin-migration

**Artifact**: plans/plugin-migration/outline.md
**Date**: 2026-02-06
**Mode**: review + fix-all

## Summary

The outline covers the plugin migration comprehensively with a sound dual-mode approach (dev submodule + consumer marketplace). The original draft had a hook migration path inconsistency, missing consideration of project-specific vs plugin hooks, no rollback strategy, and no implementation ordering. All issues have been fixed. The outline is ready for user discussion with several open questions requiring decisions.

**Overall Assessment**: Needs Iteration (open questions require user input before planning can proceed)

## Requirements Traceability

Requirements extracted from design conversation context (no formal requirements.md exists).

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| R-1: Plugin replaces skills/agents/hooks distribution | Components 1, 2; Approach | Complete | Auto-discovery via plugin manifest eliminates symlinks |
| R-2: Fragments need migration command (not plugin-provided) | Components 3, 4; Key Decisions | Complete | `/ac:init` copies fragments, `@` references point to local copies |
| R-3: Dev mode (`--plugin-dir`) vs consumer mode (marketplace) | Approach; Component 5 | Complete | Two installation modes clearly defined |
| R-4: Justfile modularization (portable vs language-specific) | Component 5 | Complete | `portable.just` import pattern with project-specific additions |
| R-5: No native PostUpgrade hook; UserPromptSubmit workaround | Component 7 | Complete | Version check on first prompt with once-per-session state |
| R-6: Symlink removal (core migration goal) | Component 6 | Complete | Explicit cleanup with preservation of non-symlink agents |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Hook migration path inconsistency**
   - Location: Component 2 (original)
   - Problem: Outline said to create `plugin/hooks/hooks.json` as a separate file, but plugin hooks belong in `plugin.json` at the plugin root. Having a separate hooks.json contradicts the plugin architecture where `plugin.json` is the single manifest.
   - Fix: Rewrote Component 2 to define hooks inside `plugin.json`. Updated Component 1 to reference hook definitions in Component 2.
   - **Status**: FIXED

2. **No hook ownership distinction (project vs plugin)**
   - Location: Key Decisions, Component 2
   - Problem: Original outline said "Move from settings.json to plugin hooks.json" without distinguishing project-specific hooks (`pretooluse-block-tmp.sh` enforces project `/tmp/` policy) from plugin hooks (`submodule-safety.py`, `userpromptsubmit-shortcuts.py`). Moving all hooks to plugin would make project-local policy leak into the shared plugin.
   - Fix: Added explicit hook ownership split in Component 2 and Key Decisions. Three categories: plugin hooks (migrate), project hooks (stay), deleted hooks.
   - **Status**: FIXED

3. **No rollback/migration safety strategy**
   - Location: (missing section)
   - Problem: A migration of this scope needs a way to recover if plugin discovery doesn't work. No mention of what happens if it fails partway through.
   - Fix: Added "Rollback Strategy" section with per-component revertibility, symlink restoration path, and additive fragment strategy.
   - **Status**: FIXED

4. **Plan-specific agents not addressed**
   - Location: Component 6 (original)
   - Problem: `.claude/agents/` contains both symlinks (plugin-provided) and regular files (`*-task.md` from `prepare-runbook.py`). Symlink cleanup must not delete generated agents. No mention of how plugin-provided and file-based agents coexist.
   - Fix: Added preservation note to Component 6, coexistence decision to Key Decisions, namespace collision question to Open Questions.
   - **Status**: FIXED

### Minor Issues

1. **Section ordering: Open Questions before Scope**
   - Location: Document structure
   - Problem: Original had Scope after Open Questions. Scope should establish boundaries first, then questions refine within those boundaries.
   - Fix: Reordered to: Scope, Implementation Order, Rollback Strategy, Open Questions.
   - **Status**: FIXED

2. **No cross-references between versioning components**
   - Location: Components 3 and 7
   - Problem: Component 3 (versioning system) and Component 7 (post-upgrade check) define the same version files but didn't reference each other. Reader must mentally connect them.
   - Fix: Added cross-references: Component 3 notes the UserPromptSubmit hook is in Component 7; Component 7 notes the version file is defined in Component 3.
   - **Status**: FIXED

3. **Not all agents are symlinked**
   - Location: Problem section
   - Problem: "12 agent symlinks" is accurate but implies all plugin agents are symlinked. `remember-task.md` and `memory-refactor.md` exist in plugin but aren't symlinked, suggesting selective distribution.
   - Fix: Added clarifying note to Problem section.
   - **Status**: FIXED

4. **plugin/bin/ scripts not addressed**
   - Location: (missing component)
   - Problem: Scripts like `prepare-runbook.py` and `batch-edit.py` are referenced by path in skills, agents, and settings.json. In consumer mode (marketplace), these paths won't resolve the same way.
   - Fix: Added Component 8 (Script Path Updates) with dev vs consumer path considerations.
   - **Status**: FIXED

5. **No implementation ordering**
   - Location: (missing section)
   - Problem: 7 components (now 8) with implicit dependencies but no suggested order. Component 6 (symlink cleanup) depends on 1+2 being verified, but this wasn't stated.
   - Fix: Added "Implementation Order" section with dependency-aware sequencing.
   - **Status**: FIXED

6. **`$CLAUDE_PLUGIN_ROOT` unverified**
   - Location: Component 2
   - Problem: The outline assumed `$CLAUDE_PLUGIN_ROOT` exists as a Claude Code environment variable, but this is undocumented. If it doesn't exist, the entire hook migration strategy needs adjustment.
   - Fix: Added verification note in Component 2 and corresponding open question.
   - **Status**: FIXED

7. **Plugin manifest path inconsistency**
   - Location: Component 1
   - Problem: Original said `plugin/.claude-plugin/plugin.json` (nested subdirectory). Plugin manifests typically live at plugin root as `plugin.json`.
   - Fix: Corrected to `plugin/plugin.json` with clarifying note.
   - **Status**: FIXED

8. **Duplicate documentation reference**
   - Location: Component 6
   - Problem: During editing, `sandbox-exemptions.md` was listed twice.
   - Fix: Removed duplicate.
   - **Status**: FIXED

## Fixes Applied

- Problem section: Added note about not all agents being symlinked
- Key Decisions: Rewrote hook migration decision to distinguish plugin vs project hooks; added plan-specific agents coexistence decision
- Component 1: Fixed plugin.json path from nested `.claude-plugin/` to plugin root; added hook cross-reference
- Component 2: Complete rewrite -- hooks in plugin.json, ownership split, `$CLAUDE_PLUGIN_ROOT` verification note
- Component 3: Added cross-reference to Component 7, clarified `.ac-version` location
- Component 4: Added idempotency consideration with Open Questions cross-reference
- Component 6: Added preservation of non-symlink agents, fixed documentation reference
- Component 7: Added requirement tag (R-5), cross-reference to Component 3, clarified version file paths
- Added Component 8: Script Path Updates for `plugin/bin/` portability
- Reordered sections: Scope before Open Questions
- Added Implementation Order section with dependency graph
- Added Rollback Strategy section
- Added two new Open Questions (`$CLAUDE_PLUGIN_ROOT` verification, agent namespace collision)
- Added requirements source annotation at document top

## Positive Observations

- Dual-mode approach (dev submodule + consumer marketplace) is well-conceived and avoids forcing a single distribution model
- Component decomposition is clean -- each component has a clear responsibility
- The symlink count claim (16/12/4) is verified accurate against the actual filesystem
- Fragment versioning with UserPromptSubmit is a pragmatic workaround for the missing PostUpgrade hook
- Justfile modularization via `import` is idiomatic and avoids copy-paste

## Recommendations

- **Priority decision needed:** Verify `$CLAUDE_PLUGIN_ROOT` existence before committing to the hook migration approach. This is a blocking unknown.
- **Fragment directory name:** Recommend `agents/ac-fragments/` -- explicit origin, avoids collision with project-specific rules, clearly distinguishable in CLAUDE.md `@` references.
- **Idempotency:** Recommend `/ac:init` be idempotent (safe to re-run) with `/ac:update` as an alias. Fewer commands to remember, and re-running init after a failed attempt is the natural recovery action.
- **Spike first:** Before full planning, run a minimal spike: create plugin.json, test `--plugin-dir` with one skill and one agent, verify discovery works. This validates the entire approach with minimal investment.

---

**Ready for user presentation**: Yes -- all issues fixed, open questions clearly identified for discussion.
