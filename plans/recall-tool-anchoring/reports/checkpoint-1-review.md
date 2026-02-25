# Review: Phase 1 Checkpoint — recall-tool-anchoring

**Scope**: `agent-core/bin/recall-check.sh`, `agent-core/bin/recall-resolve.sh`, `agent-core/bin/recall-diff.sh`
**Date**: 2026-02-24
**Mode**: review + fix

## Summary

Three prototype shell scripts implementing the recall toolchain (check, resolve, diff). All scripts are executable, have correct shebangs and `set -euo pipefail`, and match the Step 1.1–1.3 specs from runbook.md. Precommit passes cleanly. One minor issue found: recall-resolve.sh parses the artifact line-by-line but includes lines beginning with `**` (markdown bold) as trigger phrases — this only affects the current content-dump artifact format and will work correctly once Phase 2 converts the artifact to reference manifest format. One minor issue with the `—` (em dash) strip pattern: the spec uses ` — ` (space-em-dash-space) as the annotation separator, but the script's strip pattern `%% — *` uses `%%` which strips the longest match from the end — correct per POSIX parameter expansion but subtly different from splitting on first occurrence. This is fine since annotations appear only once per line.

**Overall Assessment**: Ready (precommit passes, all issues fixed)

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **recall-resolve.sh: `%%` longest-match strip may be incorrect for multi-dash lines**
   - Location: `agent-core/bin/recall-resolve.sh:25`
   - Note: `line="${line%% — *}"` uses `%%` (longest match from end = strip everything from last ` — ` onward). For manifest lines with a single annotation, `%` (shortest match) and `%%` (longest match) produce identical results. But if a trigger phrase itself contains ` — `, the longest-match strip would incorrectly truncate the trigger. Spec trigger phrases don't contain ` — `, but this is fragile.
   - Fix: Use `%` (single percent) for shortest-match strip — removes only the last annotation, not any dashes in the trigger phrase itself.
   - **Status**: FIXED

2. **recall-diff.sh: `|| true` applies to full pipeline, masking potential sort errors**
   - Location: `agent-core/bin/recall-diff.sh:28`
   - Note: The `|| true` guards against `grep -v` returning exit 1 when no lines match (empty output after filtering) — appropriate per the error-handling exception for expected non-zero exits. However, it applies to the full pipeline including `sort -u`, masking any sort errors.
   - Fix: Sort failures are vanishingly rare for this use case and the scripts are explicitly throwaway prototypes (D-2). The `|| true` on the full pipeline is acceptable. No change needed.
   - **Status**: OUT-OF-SCOPE — throwaway prototype (D-2), sort failure mode not realistic

## Fixes Applied

- `agent-core/bin/recall-resolve.sh:25` — Changed `%%` to `%` (shortest-match strip) so only the first ` — ` annotation separator is stripped; trigger phrases containing ` — ` are not truncated.

## Requirements Validation

No requirements context provided in the task prompt — validating against runbook.md Step 1.1–1.3 specs and outline.md design decisions instead.

| Spec Item | Status | Evidence |
|-----------|--------|----------|
| recall-check.sh: shebang + set -euo pipefail | Satisfied | Lines 1-2 |
| recall-check.sh: accepts `<job-name>` | Satisfied | Line 9 |
| recall-check.sh: checks exists and non-empty | Satisfied | Lines 12-19 |
| recall-check.sh: exit 0 no output on success | Satisfied | Falls through to implicit exit 0 |
| recall-check.sh: exit 1 with stderr diagnostic | Satisfied | Lines 14, 18 |
| recall-check.sh: missing arg → usage + exit 1 | Satisfied | Lines 4-7 |
| recall-check.sh: executable | Satisfied | `-rwxr-xr-x` confirmed |
| recall-resolve.sh: shebang + set -euo pipefail | Satisfied | Lines 1-2 |
| recall-resolve.sh: accepts `<artifact-path>` | Satisfied | Line 9 |
| recall-resolve.sh: strip annotations | Satisfied | Line 25 |
| recall-resolve.sh: skip blank + comment lines | Satisfied | Lines 29-30 |
| recall-resolve.sh: single invocation to when-resolve.py | Satisfied | Line 46 |
| recall-resolve.sh: when/how prefix logic | Satisfied | Lines 32-37 |
| recall-resolve.sh: missing artifact → stderr + exit 1 | Satisfied | Lines 11-14 |
| recall-resolve.sh: unreadable artifact → stderr + exit 1 | Satisfied | Lines 16-19 |
| recall-resolve.sh: empty manifest → stderr + exit 0 | Satisfied | Lines 40-43 |
| recall-resolve.sh: executable | Satisfied | `-rwxr-xr-x` confirmed |
| recall-diff.sh: shebang + set -euo pipefail | Satisfied | Lines 1-2 |
| recall-diff.sh: accepts `<job-name>` | Satisfied | Line 9 |
| recall-diff.sh: missing artifact → stderr + exit 1 | Satisfied | Lines 12-15 |
| recall-diff.sh: not in git repo → stderr + exit 1 | Satisfied | Lines 17-20 |
| recall-diff.sh: get artifact mtime | Satisfied | Line 22 |
| recall-diff.sh: git log --since with --name-only | Satisfied | Lines 24-27 |
| recall-diff.sh: exclude recall-artifact.md itself | Satisfied | Line 26 |
| recall-diff.sh: missing arg → usage + exit 1 | Satisfied | Lines 4-7 |
| recall-diff.sh: executable | Satisfied | `-rwxr-xr-x` confirmed |

**Gaps:** None. All spec items satisfied.

---

## Positive Observations

- All three scripts use `BASH_SOURCE[0]`-based SCRIPT_DIR resolution in recall-resolve.sh — correct for symlinked invocations from any working directory.
- recall-diff.sh uses `date -r "$ARTIFACT"` for mtime (macOS-compatible), and `git log --since` with ISO format — correct approach.
- Consistent stderr routing for all error messages across all three scripts.
- `|| true` in recall-diff.sh correctly handles the grep-no-match case (expected non-zero from grep -v filtering).
- recall-resolve.sh: readable-check (lines 16-19) catches permission errors separate from existence errors — defensive and correct.
- Manifest line parsing handles both `when`/`how` prefixes and defaulting to `when` prefix — matches spec exactly.
