# Runbook Review: Phase 6 — Symlink cleanup, settings migration, and doc updates

**Artifact**: `plans/plugin-migration/runbook-phase-6.md`
**Date**: 2026-03-14T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (3 steps)

## Summary

Phase 6 covers symlink removal, settings.json cleanup, fragment documentation updates, and a final validation checkpoint. Three issues found and fixed: a missing step to delete `pretooluse-symlink-redirect.sh` (required by outline), a vacuous item targeting `delegation.md` (no `sync-to-parent` references exist there), and two vague validation criteria (one ambiguous symlink grep qualifier, one prose-only `@`-reference check without a concrete command).

**Overall Assessment**: Ready (after fixes applied)

## Critical Issues

None.

## Major Issues

1. **Missing deletion of `pretooluse-symlink-redirect.sh`**
   - Location: Step 6.1, Implementation
   - Problem: Outline line 162 explicitly requires deleting `pretooluse-symlink-redirect.sh` from `plugin/hooks/` as part of symlink cleanup. Step 6.1 listed 6 items but omitted this deletion, leaving a dead hook script on disk.
   - Fix: Added item 7 with `rm plugin/hooks/pretooluse-symlink-redirect.sh`, cross-reference to hooks.json entry removal, validation command `test ! -f plugin/hooks/pretooluse-symlink-redirect.sh && echo OK`, and added to Expected Outcome.
   - **Status**: FIXED

2. **Vacuous `delegation.md` item in Step 6.2**
   - Location: Step 6.2, Prerequisites read-list and item 4
   - Problem: Step 6.2 instructed reading `plugin/fragments/delegation.md` and "updating examples referencing `sync-to-parent`." Grep confirms `delegation.md` contains zero `sync-to-parent` references — the item is a dead instruction that wastes executor time and risks scope creep.
   - Fix: Removed `delegation.md` from prerequisites read-list; removed item 4 from Implementation. Remaining items 1–3 made more specific (exact subsection targets named).
   - **Status**: FIXED

## Minor Issues

1. **Ambiguous symlink grep validation in Step 6.2**
   - Location: Step 6.2, Validation, second bullet
   - Problem: `grep -r 'symlink' plugin/fragments/claude-config-layout.md` with qualifier "or only in historical context" — this is not a binary pass/fail criterion. An executor cannot determine what "historical context" means.
   - Fix: Changed to `grep 'sync-to-parent\|Symlinks in .claude' plugin/fragments/claude-config-layout.md` targeting the exact subsection heading and content being removed. Zero matches = pass.
   - **Status**: FIXED

2. **Vague FR-7 `@`-reference check in Step 6.3**
   - Location: Step 6.3, Implementation item 2
   - Problem: "No broken references in CLAUDE.md, fragments, skills / All `@`-references resolve" — prose description with no concrete command. An executor cannot verify this without tool guidance.
   - Fix: Replaced with two concrete grep commands: one to find `@plugin/` references in CLAUDE.md and rules, one to enumerate `^@` references within fragments/skills — both with verification action stated.
   - **Status**: FIXED

3. **Step 6.1 gitignore item lacked specificity**
   - Location: Step 6.1, item 7 (now item 8)
   - Problem: "Update `.gitignore` if it has entries related to symlinks" — no specific patterns to check for, no command, ambiguous pass condition.
   - Fix: Added concrete grep command and named the pattern categories to look for.
   - **Status**: FIXED

## Fixes Applied

- Step 6.1 Implementation — Added item 7: delete `pretooluse-symlink-redirect.sh` with `rm` command and hooks.json cross-check
- Step 6.1 Implementation item 7 (now 8) — Added concrete grep command for gitignore check
- Step 6.1 Expected Outcome — Added `pretooluse-symlink-redirect.sh` deleted to outcomes list
- Step 6.1 Validation — Added `test ! -f plugin/hooks/pretooluse-symlink-redirect.sh && echo OK`
- Step 6.2 Prerequisites — Removed `delegation.md` from read-list
- Step 6.2 Implementation — Removed item 4 (`delegation.md` update); made items 1–3 more specific with exact subsection targets
- Step 6.2 Validation — Replaced ambiguous symlink grep with targeted `sync-to-parent\|Symlinks in .claude` pattern
- Step 6.3 Implementation item 2 — Replaced prose FR-7 check with two concrete grep commands

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
