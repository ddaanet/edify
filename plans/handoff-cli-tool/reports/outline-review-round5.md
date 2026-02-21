# Outline Review: handoff-cli-tool (Round 5)

**Artifact**: plans/handoff-cli-tool/outline.md
**Date**: 2026-02-21
**Mode**: review + fix-all

## Summary

Post-feedback review focused on terminology consistency ("Gate B" to "vet check"), `→ wt` marker integration, exit code alignment with S-3, and YAML artifact elimination. Found 4 terminology inconsistencies where "vet gate" survived the rename, 1 exit code misalignment (ST-2 used exit 1 for input validation), and 1 domain boundary gap (H-1 table silent on `→ wt` ownership). All fixed. No YAML artifacts remain. No critical issues.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements derived from session.md task description, brief.md, and prior round context (no requirements.md).

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: `_session` command group (handoff, commit, status) | Approach, S-1 | Complete | Three subcommands with shared infrastructure |
| FR-2: Structured markdown I/O (stdin/stdout, no stderr) | S-3, Input/Output sections | Complete | S-3 convention applied uniformly |
| FR-3: Session.md mechanical writes (handoff) | H-1, H-2, Pipeline | Complete | Domain boundaries explicit |
| FR-4: State caching for retry (handoff) | H-4, Pipeline step 2 | Complete | Cache before first mutation |
| FR-5: Sole commit path with vet check | C-1, C-4, Pipeline | Complete | Terminology now consistent |
| FR-6: Submodule coordination | C-2 | Complete | 4-case truth table |
| FR-7: Commit ID in output | Output examples | Complete | `**Committed:** a7f38c2` in all success examples |
| FR-8: STATUS rendering (pure data transformation) | Status Pipeline, Output | Complete | No mutations, no stdin |
| FR-9: `→ wt` worktree-destined tasks | S-4, ST-0, H-1, Status Output | Complete | Parser, rendering, domain ownership all addressed |
| FR-10: Parallel detection without model/restart constraints | ST-1 | Complete | Rationale: worktree parallelism eliminates both |
| FR-11: Missing session.md = fatal error | ST-2 | Complete | Exit 2 (input validation) after fix |
| FR-12: `_git()` extraction to shared module | S-2 | Complete | Move from worktree/utils.py |

**Traceability Assessment**: All requirements covered.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **"Vet gate" terminology survived rename in 5 locations**
   - Location: S-1 line 28 (gate.py annotation), commit example line 159, pipeline summary line 140, Scope IN line 329, Phase 5 line 349
   - Problem: Task specified "Gate B" renamed to "Vet check" / "Scripted vet check". Five references still used the old "vet gate" phrasing. The C-1 heading was correctly "Scripted vet check" but downstream references diverged.
   - Fix: Updated all 5 to use "vet check" or "scripted vet check" consistently. Also caught "gate passes" in C-1 body (line 238) and updated to "check passes".
   - **Status**: FIXED

2. **ST-2 exit code inconsistent with S-3 taxonomy**
   - Location: ST-2 (line 316)
   - Problem: Missing session.md triggered exit 1 ("pipeline error / runtime failure"). Per S-3, exit 2 is for "input validation (malformed caller input)". Missing session.md is an input validation failure — the expected input file doesn't exist, indicating wrong cwd, corruption, or accidental deletion. Not a runtime pipeline failure.
   - Fix: Changed to exit 2 with rationale note referencing S-3.
   - **Status**: FIXED

### Minor Issues

1. **H-1 domain boundary table missing `→ wt` ownership**
   - Location: H-1 (line 102-103)
   - Problem: Table listed `Worktree CLI | → slug markers` but was silent on who owns `→ wt` markers. ST-0 states "set by user/agent at task creation time" — making it Agent-owned. But H-1's boundary table (the authoritative ownership reference) didn't reflect this, creating ambiguity for implementers.
   - Fix: Added `→ wt` markers to Agent (Edit/Write) row. Added clarifying parenthetical to Worktree CLI row: "(set on `wt` branch-off)".
   - **Status**: FIXED

## Fixes Applied

- S-1 line 28 — `gate.py` annotation: "Vet gate" to "Scripted vet check"
- Commit example line 159 — message text: "scripted vet gate" to "scripted vet check"
- Pipeline summary line 140 — "gate" to "vet check"
- C-1 body line 238 — "gate passes" to "check passes"
- Scope IN line 329 — "vet gate" to "scripted vet check"
- Phase 5 line 349 — "vet gate" to "scripted vet check"
- ST-2 line 316 — exit 1 to exit 2 with S-3 rationale
- H-1 line 102 — Added "(set on `wt` branch-off)" to Worktree CLI row
- H-1 line 103 — Added `→ wt` markers to Agent (Edit/Write) row

## Positive Observations

- The `→ wt` mechanism integrates cleanly: S-4 parser recognizes it, ST-0 defines rendering behavior, status output example shows both forms, and `Next:` skip logic covers both marker types.
- Exit code taxonomy (S-3) is well-defined and consistently applied across all commit output examples (0=success, 1=pipeline error, 2=input validation).
- No YAML-in-markdown artifacts remain — all output examples use `**Header:** content` format.
- H-2 committed detection cases are explicit with a truth-table approach.
- The `gate.py` filename is kept as-is (the rename was conceptual/terminology, not a file rename decision) — avoids confusion between "what the module is called" and "what the feature is called."

## Recommendations

- The commit message example in the Input section (line 156: "Add scripted gate classification reference") still uses "gate" — this is illustrative commit message text and doesn't affect implementation, but could be updated for full consistency if desired.
- Gate A references in Scope OUT (lines 335, 341) are correct — Gate A is the skill-level session freshness check, a different concept from the CLI's scripted vet check. No action needed, noting for clarity.

---

**Ready for user presentation**: Yes
