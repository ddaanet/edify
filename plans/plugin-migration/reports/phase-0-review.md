# Vet Review: Phase 0 Runbook - Directory Rename

**Scope**: Phase 0 runbook file at `plans/plugin-migration/runbook-phase-0.md`
**Date**: 2026-02-07T18:15:00Z

## Summary

Phase 0 runbook renames `plugin/` to `edify-plugin/` across the entire project. Review found **significant coverage gaps** in file identification, incomplete grep pattern, and missing validation for critical file types. The symlink auto-adjust explanation is correct but lacks testing guidance. Several categories of files were missed that will break after rename.

**Overall Assessment**: Needs Significant Changes

## Issues Found

### Critical Issues

1. **Missing .claude/rules/*.md path updates**
   - Location: runbook-phase-0.md:49-53 (grep command) + step 4-7 (affected files)
   - Problem: `.claude/rules/skill-development.md` contains `paths: ["plugin/skills/**/*"]` frontmatter that won't be caught by grep (excluded directory). Two other rules files also contain references.
   - Fix: Add explicit step to update `.claude/rules/` files:
     - `skill-development.md` line 4: `plugin/skills/**/*` → `edify-plugin/skills/**/*`
     - `commit-work.md`: contains `@plugin/fragments/commit-delegation.md` reference
     - `planning-work.md`: contains `@plugin/fragments/` references

2. **Missing plan-specific agent file updates**
   - Location: runbook-phase-0.md:99-107 (affected files)
   - Problem: 6 plan-specific agent files in `.claude/agents/` contain plugin references but are not listed as affected files. These are NOT symlinks (type f), so they need explicit path updates.
   - Files found:
     - `.claude/agents/plugin-migration-task.md` (ironically, the agent for THIS plan)
     - `.claude/agents/claude-tools-rewrite-task.md`
     - `.claude/agents/consolidation-task.md`
     - `.claude/agents/learnings-consolidation-task.md`
     - `.claude/agents/workflow-controls-task.md`
     - `.claude/agents/design-workflow-enhancement-task.md`
   - Fix: Add these to affected files list and update step to handle them

3. **Missing plans/ directory updates**
   - Location: runbook-phase-0.md:49-53 (grep coverage)
   - Problem: Found 41 references in `plans/` subdirectories (reflect-rca-prose-gates, validator-consolidation, commit-unification, workflow-skills-audit). These are design docs, outlines, and reports that contain plugin paths in examples and file references.
   - Impact: Historical plan documentation will contain stale paths (confusing but not breaking)
   - Fix: Decision needed - update historical docs vs accept staleness. If updating, add explicit step for `plans/*/` files. Grep found files at:
     - `plans/reflect-rca-prose-gates/outline.md` (2 refs)
     - `plans/reflect-rca-prose-gates/design.md` (10 refs)
     - `plans/reflect-rca-prose-gates/reports/vet-review.md` (1 ref)
     - `plans/validator-consolidation/requirements.md` (9 refs)
     - `plans/commit-unification/design.md` (9 refs)
     - `plans/commit-unification/reports/vet-review.md` (2 refs)
     - `plans/workflow-skills-audit/audit.md` (8 refs)

4. **plugin/Makefile contains plugin reference**
   - Location: plugin/Makefile:4, 10, 30
   - Problem: Makefile comment line 4 says "FUTURE: When justfiles are factored to use plugin includes", line 10 target name is `just-help-plugin.txt`, line 30 creates that file
   - Impact: Target name must change to match cache file rename
   - Fix: Update Makefile to rename target `just-help-plugin.txt` → `just-help-edify-plugin.txt` (line 10, 30)

5. **Incomplete grep pattern excludes critical directories**
   - Location: runbook-phase-0.md:49-53
   - Problem: `--exclude-dir=edify-plugin` prevents finding plugin references INSIDE the renamed directory (like Makefile, comments, documentation)
   - Rationale: After `git mv plugin edify-plugin`, the grep runs and excludes the NEW directory name, but self-references inside edify-plugin/ should be checked
   - Fix: Remove `--exclude-dir=edify-plugin` from grep, or run grep BEFORE git mv

### Major Issues

6. **Missing session.md update**
   - Location: runbook-phase-0.md (not mentioned anywhere)
   - Problem: session.md likely contains plugin references in "Reference Files" or "Completed This Session" sections
   - Evidence: Current session.md shows "Design updated (naming + format fixes)" referencing old paths
   - Fix: Add explicit step to update `agents/session.md` plugin → edify-plugin

7. **Symlink testing incomplete**
   - Location: runbook-phase-0.md:40-43, 84
   - Problem: Runbook tests only ONE symlink (`.claude/skills/commit`), but 31 symlinks exist (agents, skills, hooks). Any could break if git mv doesn't handle relative paths correctly.
   - Fix: Change validation from single symlink to comprehensive check:
     ```bash
     # Verify ALL symlinks resolve
     find .claude -type l | while read link; do
       readlink -f "$link" >/dev/null || echo "BROKEN: $link"
     done
     ```

8. **No validation of @ references loading**
   - Location: runbook-phase-0.md:72 (manual check on next session)
   - Problem: "Manual: check that fragments load without errors on next session" defers critical validation to AFTER the irreversible rename
   - Impact: If CLAUDE.md @ references break, discovery happens after rename is committed
   - Fix: Add script-based validation BEFORE commit:
     ```bash
     # Check that @ references resolve (basic existence check)
     grep '^@edify-plugin/' CLAUDE.md | sed 's/@//' | while read path; do
       [ -f "$path" ] || echo "MISSING: $path"
     done
     ```

9. **Worktree submodule reference unclear**
   - Location: justfile:65 (identified in grep)
   - Problem: `--reference "$main_dir/plugin"` in wt-new recipe must update to edify-plugin, but runbook doesn't explicitly call this out in step 3 (Update root justfile)
   - Impact: After rename, `just wt-new` will fail with "reference repository does not exist"
   - Fix: Add explicit note in step 3 that wt-new, wt-merge recipes contain plugin in submodule operations

10. **Cache filename change timing unclear**
    - Location: runbook-phase-0.md:45-47
    - Problem: "Update cache filenames" step 7 says "Rename .cache/just-help-plugin.txt" but doesn't clarify if this happens BEFORE or AFTER updating CLAUDE.md @ references (step 5)
    - Impact: If CLAUDE.md updated first but cache file not renamed, @ reference breaks immediately
    - Fix: Reorder steps - rename cache file BEFORE updating CLAUDE.md @ reference

### Minor Issues

11. **Git status validation insufficient**
   - Location: runbook-phase-0.md:82
   - Problem: "`git status` shows renamed files, no deleted/added files" is ambiguous - git mv shows as renamed (R) but also stages the change
   - Suggestion: Clarify expected output: "git status shows 'renamed: plugin/ -> edify-plugin/' and modified files (.gitmodules, justfile, etc.)"

12. **Unexpected reference handling vague**
   - Location: runbook-phase-0.md:76
   - Problem: "If grep finds additional references: update those files" provides no guidance on WHAT references are expected vs unexpected
   - Suggestion: Provide expected reference count or list of known files to set baseline

13. **Edify-plugin Makefile target name check missing**
   - Location: runbook-phase-0.md:106
   - Problem: "Possibly: `edify-plugin/Makefile` (target names)" is listed as uncertain, but target DEFINITELY needs update (see Critical Issue #4)
   - Fix: Change from "Possibly" to definite requirement with line numbers

## Requirements Validation

**Requirements context provided:** Design document at plans/plugin-migration/design.md

Phase 0 is preparatory - no direct requirement mapping. However, correct directory rename is prerequisite for all components:

| Component | Phase 0 Impact | Status |
|-----------|----------------|--------|
| C-1 Plugin Manifest | Must reference edify-plugin/ paths | Blocked by Critical #1-5 |
| C-2 Hook Migration | settings.json hooks reference plugin/ paths | Covered (step 4) |
| C-3 Version Marker | File created in edify-plugin/ | Unblocked |
| C-4 Init Skill | Will reference edify-plugin/ paths | Unblocked after rename |
| C-5 Justfile Recipes | Import from edify-plugin/ path | Covered (step 3) |
| C-6 Migration Guide | Must document new paths | Unblocked |
| C-7 Staleness Hook | Will reference edify-plugin/ paths | Unblocked |
| C-8 Plugin Publishing | N/A (future) | N/A |

**Gaps:** Critical Issues #1-5 must be resolved before Phase 0 execution, otherwise Components 1-2 will reference inconsistent paths.

---

## Positive Observations

- Clear objective and implementation steps with numbered sequence
- Correct understanding that `git mv` preserves history
- Appropriate use of grep to find remaining references
- Good validation criteria with specific commands
- Proper unexpected result handling with concrete fallback steps
- Symlink auto-adjust explanation is technically correct (git tracks symlink target strings, relative paths update automatically)
- Report path specified for execution tracking

## Recommendations

1. **Perform two-phase grep:** Run comprehensive grep BEFORE `git mv` to get complete inventory, then targeted grep AFTER to verify
2. **Categorize updates:** Group files by update type (config files, rules, agents, plans) with separate validation per group
3. **Add reference count baseline:** Document expected number of references in each category so grep validation can detect missing updates
4. **Strengthen symlink validation:** Test all 31 symlinks, not just one sample
5. **Add automated @ reference check:** Script to validate CLAUDE.md @ paths resolve before considering step complete
6. **Consider plans/ staleness:** Make explicit decision whether to update historical plan documentation or accept path staleness

## Next Steps

**Before execution:**
1. Expand "Affected Files" section (step 99-107) to include all files identified in Critical Issues #1-3
2. Add explicit substeps for .claude/rules/, plan-specific agents, and plans/ directory
3. Update Makefile changes from "Possibly" to definite requirement with specific line changes
4. Reorder steps: cache filename rename before CLAUDE.md @ reference update
5. Enhance symlink validation from single test to comprehensive check
6. Add automated @ reference validation script before manual session check

**During execution:**
1. Run initial grep and save output for reference count baseline
2. Perform git mv
3. Update all identified files
4. Run validation grep and compare reference counts
5. Test all symlinks, not just one
6. Validate @ references automatically
7. Run justfile tests

**Risk mitigation:**
- Create backup branch before starting (already standard practice)
- Commit atomically (all renames + updates in single commit) to maintain referential integrity
- Test in worktree first if high risk aversion
