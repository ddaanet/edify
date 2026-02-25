# Review: recall-tool-anchoring execution

**Scope**: Final review of full runbook execution (Phases 1-4)
**Date**: 2026-02-24
**Mode**: review + fix

## Summary

All four phases completed. Three scripts are present and executable. Hook is registered. D+B restructure applied to all 8 target files. Two recall-artifact entries have trigger phrases that don't match their memory-index keys (`how to X` instead of `how X`), causing recall-resolve.sh to fail on those entries at runtime. No other issues found.

**Overall Assessment**: Ready

---

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **recall-artifact.md: two `how to X` triggers don't match memory-index keys**
   - Location: `plans/recall-tool-anchoring/recall-artifact.md` lines 3 and 8
   - Note: Memory-index keys are `/how prevent skill steps from being skipped` and `/how recall sub-agent memory` (no "to"). The artifact has `how to prevent...` and `how to recall...` — when-resolve.py strips the `how ` prefix and receives `to prevent...` / `to recall...` which don't match. Confirmed: `when-resolve.py "how to prevent skill steps from being skipped"` exits 1 with "No match".
   - Fix: Remove "to" from both trigger phrases to match the index keys.
   - **Status**: FIXED

---

## Fixes Applied

- `plans/recall-tool-anchoring/recall-artifact.md:3` — Changed `how to prevent skill steps from being skipped` to `how prevent skill steps from being skipped` to match memory-index key `/how prevent skill steps from being skipped`
- `plans/recall-tool-anchoring/recall-artifact.md:8` — Changed `how to recall sub-agent memory` to `how recall sub-agent memory` to match memory-index key `/how recall sub-agent memory`

---

## Success Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 3 scripts executable (recall-check.sh, recall-resolve.sh, recall-diff.sh) | Satisfied | All 3 at `agent-core/bin/`, `-rwxr-xr-x` |
| recall-artifact.md in reference manifest format (one line per entry, trigger — annotation) | Satisfied | 16 entries, all lines have ` — ` separator, no content dumps |
| 8 files have tool-anchored recall gates | Satisfied | 6 read-side files have `Bash: agent-core/bin/recall-resolve.sh`; 2 write-side files have `Bash: agent-core/bin/recall-diff.sh` at 3 gates |
| Hook fires on Task delegation with missing artifact | Satisfied | `agent-core/hooks/pretooluse-recall-check.py` registered in settings.json under Task matcher |
| "proceed without it" anti-pattern eliminated | Satisfied | Zero occurrences in `agent-core/` (occurrences in plan docs are historical references) |
| Permission registered (recall-*:*) | Satisfied | `Bash(agent-core/bin/recall-*:*)` in settings.json allow list |
| recall-resolve.sh resolves all artifact triggers | Partial before fix → Satisfied after fix | 2 of 16 triggers failed due to `how to X` vs `how X` mismatch; fixed |

**Read-side gates (6 files, recall-resolve.sh):**
- `agent-core/agents/design-corrector.md` — Step 1.5
- `agent-core/agents/outline-corrector.md` — Step 2 item 4
- `agent-core/agents/runbook-outline-corrector.md` — Step 2 item 4
- `agent-core/skills/review-plan/SKILL.md` — Recall Context section
- `agent-core/skills/deliverable-review/SKILL.md` — Layer 2 recall
- `agent-core/skills/orchestrate/SKILL.md` — Review recall

**Write-side gates (2 files, recall-diff.sh, 3 gates):**
- `agent-core/skills/design/SKILL.md` — A.5 and C.1
- `agent-core/skills/runbook/SKILL.md` — Phase 0.75

---

## Positive Observations

- D+B restructure is consistent across all 8 target files — tool-call anchor appears as first instruction in each gate section
- All read-side gates include fallback to lightweight recall when artifact absent or resolve fails — "proceed without it" anti-pattern is fully eliminated
- recall-resolve.sh handles both `when` and `how` prefixes correctly; the annotation strip using bash pattern expansion is correct for the em-dash separator
- Hook implementation follows the existing pretooluse pattern (stdin JSON → additionalContext output) with no blocking behavior — matches the soft-warning spec
- recall-diff.sh uses `git log --since` against artifact mtime, cleanly filtering out the artifact file itself from the diff output
- runbook.md constraint "DO NOT modify recall generation gates (design A.1, runbook Phase 0.5)" correctly observed — Phase 0.5 uses Read + when-resolve.py directly (it creates artifacts, not reads them)
