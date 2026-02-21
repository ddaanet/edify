# Runbook Review: Phase 4 — Session Health Checks

**Artifact**: `plans/hook-batch/runbook-phase-4.md`
**Date**: 2026-02-21T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (3 steps)

## Summary

Phase 4 covers session health check delivery via dual-hook coordination (D-4). The step structure is sound and dependency ordering is correct (4.1 → 4.2 → 4.3). Four issues found: one critical implementation contradiction in Step 4.1, one bug in Step 4.2 under `set -euo pipefail`, one script size misclassification in Step 4.3, and weak validation assertions in Step 4.1. All fixed inline.

**Overall Assessment**: Ready

---

## Findings

### Critical Issues

**1. Step 4.1: `--summary` placement contradicts prerequisite note**
- **Location**: Step 4.1, Implementation section
- **Problem**: Instruction says "Add `--summary` detection at start of main()" but the prerequisite note says "reuse existing computation variables, not duplicate logic." The computation variables (`total_entries`, `entries_7plus`, `staleness_days`) are computed at lines 181-193, partway through `main()`. Detection at start would require duplicating all computation. These are mutually contradictory — an executor following "at start" would either duplicate logic or fail to produce correct output.
- **Fix**: Replaced pseudo-code to show detection placed AFTER the computation block (after line 193, before `print("# Learning Ages Report")`), branching only the output path and reusing all computed variables.
- **Status**: FIXED

### Major Issues

**2. Step 4.2: `grep` exit 1 kills script under `set -euo pipefail`**
- **Location**: Step 4.2, Health check 3 — stale worktrees
- **Problem**: The worktree listing pipeline ends with `grep -v "^$(git rev-parse --show-toplevel)$"`. With `set -euo pipefail`, if there are no non-main worktrees (grep finds no lines to output), grep exits 1, which kills the script via pipefail. This is a latent bug that fires on clean single-worktree setups.
- **Fix**: Added `|| true` at end of the pipeline in the process substitution.
- **Status**: FIXED

### Minor Issues

**3. Step 4.3: Script Evaluation misclassified as "Small"**
- **Location**: Step 4.3, Script Evaluation line
- **Problem**: Step 4.3 duplicates the same 3 health checks as Step 4.2 (which is correctly classified Medium). The Stop fallback is only "simpler" in the fast-exit path — the full execution path has identical complexity. Misclassification can lead haiku to treat it as a trivial inline script and underspec it.
- **Fix**: Changed to "Medium" with explanatory note.
- **Status**: FIXED

**4. Step 4.1: Weak validation assertions**
- **Location**: Step 4.1, Validation section
- **Problem**: Validation only checked "Content contains 'entries'" — too weak to catch format deviations. Both output formats are precisely specified in the step; the validation should verify against them. Also missing: regression check that normal mode output starts with `# Learning Ages Report`.
- **Fix**: Added regex check matching both expected format patterns. Added explicit regression assertion for normal mode first line.
- **Status**: FIXED

**5. Step 4.2: JSON output `\n` semantics undocumented**
- **Location**: Step 4.2, Output format section
- **Problem**: The `message=` assignment uses `\n` in a double-quoted bash string — these are literal backslash-n, not shell newlines. This is the correct approach for embedding escape sequences in JSON, but without a note, an executor may "fix" it to `$'...'` syntax or actual newlines, breaking JSON validity.
- **Fix**: Added inline note clarifying intentional literal `\n` and warning against `$'...'` syntax.
- **Status**: FIXED

**6. (Advisory) Model assignment: haiku for Steps 4.2 and 4.3**
- **Location**: Step 4.2 and Step 4.3, Execution Model
- **Problem**: Both steps create non-trivial Bash scripts with JSON stdin parsing, multi-check logic, and flag file coordination. Haiku has a documented failure mode of rationalizing test failures (see learnings.md). Steps 4.2 and 4.3 have no automated tests — validation is manual bash invocation. Haiku risk is lower here than in TDD contexts, but worth noting.
- **Fix**: No change — advisory only. Model selection is caller judgment.
- **Status**: Advisory, no action taken

---

## Fixes Applied

- Step 4.1, Implementation — Replaced "at start of main()" pseudo-code with placement after computation block, showing `--summary` branches output only
- Step 4.2, Health check 3 — Added `|| true` to worktree grep pipeline to prevent pipefail on no-match
- Step 4.2, Output format — Added note clarifying intentional literal `\n` in double-quoted bash strings
- Step 4.1, Validation — Strengthened with regex format check and explicit regression assertion for normal mode
- Step 4.3, Script Evaluation — Corrected from "Small" to "Medium"

---

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
