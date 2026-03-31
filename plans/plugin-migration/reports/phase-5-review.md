# Runbook Review: Phase 5 — Version Coordination and Precommit

**Artifact**: plans/plugin-migration/runbook-phase-5.md
**Date**: 2026-03-14T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (2 steps)

## Summary

Phase 5 is a 2-step general phase creating `.edify.yaml` and adding the version consistency precommit check (FR-12). Review found 4 issues: one major deferred-decision embedded in an error condition, one major under-specified integration with the existing `just release` recipe, one minor validation hardcoding version instead of reading from source, and one minor incorrect executable-flag claim. All issues fixed.

**Overall Assessment**: Ready

## Findings

### Major Issues

1. **Deferred decision disguised as error condition (Step 5.2)**
   - Location: Step 5.2, Error Conditions
   - Problem: "If `just release` recipe doesn't exist → create it or add version bump to existing release workflow" — `just release` exists and is a 50-line complex recipe with interactive confirmation, rollback, git push, PyPI publish, and GitHub release creation. The fork "doesn't exist" never applies. The "add to existing" path gave no integration guidance.
   - Fix: Removed the always-false branch. Remaining error condition now just covers `plugin.json` path changes.
   - **Status**: FIXED

2. **Under-specified `just release` modification (Step 5.2)**
   - Location: Step 5.2, Implementation point 3
   - Problem: "Update `just release` recipe to bump both files together — Accept version argument, Update pyproject.toml version, Update plugin.json version, Run consistency check." The existing recipe uses `uv version --bump "$BUMP"` (bump levels: patch/minor/major, not explicit version), and commits `pyproject.toml uv.lock` in a specific line. Without reading the actual recipe first, an executor would make wrong assumptions about the integration point. No insertion point specified.
   - Fix: Replaced vague bullets with concrete insertion-point instructions (after `uv version --bump "$BUMP"` line ~478, extend the `git add` line, insert consistency check). Added prerequisite to read the relevant justfile line ranges before implementing.
   - **Status**: FIXED

### Minor Issues

3. **Validation hardcodes version string (Step 5.1)**
   - Location: Step 5.1, Validation
   - Problem: `assert d['version']=='0.0.2'` — hardcoded version will be stale after first release. Should verify `.edify.yaml` version matches `pyproject.toml` dynamically.
   - Fix: Updated validation command to read `pyproject.toml` via `tomllib` and compare against `.edify.yaml` version.
   - **Status**: FIXED

4. **Expected Outcome claims script "is executable" (Step 5.2)**
   - Location: Step 5.2, Expected Outcome
   - Problem: "exists and is executable" — the step invokes it as `python3 plugin/bin/check-version-consistency.py`, not as a direct executable. Other scripts in `plugin/bin/` follow the same pattern (confirmed by justfile precommit calling scripts via `python3`). The executable-flag claim is inconsistent.
   - Fix: Updated to "exists (invoked as `python3 plugin/bin/...`, not as a direct executable)".
   - **Status**: FIXED

### Prerequisite Format

5. **Non-standard prerequisite format (Steps 5.1 and 5.2)**
   - Location: Step 5.1 prerequisites; Step 5.2 prerequisites
   - Problem: Step 5.1 used an informal bullet list; Step 5.2 used a list without the `**Prerequisite:** Read [file:lines] — understand [behavior]` format required for creation steps.
   - Fix: Reformatted Step 5.1 to single-line `**Prerequisite:**` format. Expanded Step 5.2 prerequisites to three structured prerequisite items with line ranges and specific reading goals.
   - **Status**: FIXED

## Fixes Applied

- `runbook-phase-5.md:11-12` — Reformatted Step 5.1 prerequisite to standard format with line range
- `runbook-phase-5.md:33-34` — Updated Step 5.1 validation to compare `.edify.yaml` version against `pyproject.toml` dynamically via `tomllib`
- `runbook-phase-5.md:42-44` — Replaced Step 5.2 informal prerequisite list with three structured prerequisites (justfile release recipe lines, precommit recipe lines, plugin.json structure)
- `runbook-phase-5.md:53-57` — Replaced vague `just release` modification bullets with concrete insertion-point instructions referencing actual line numbers
- `runbook-phase-5.md:60` — Corrected "is executable" to "invoked as `python3 ...`, not as a direct executable"
- `runbook-phase-5.md:65-66` — Removed always-false "if recipe doesn't exist" error condition branch

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
