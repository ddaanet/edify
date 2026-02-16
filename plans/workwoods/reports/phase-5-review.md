# Runbook Review: Phase 5 - Merge Strategies + Skill Update

**Artifact**: plans/workwoods/runbook-phase-5.md
**Date**: 2026-02-16T00:00:00Z
**Mode**: review + fix-all
**Phase types**: Mixed (10 TDD cycles, 3 general steps)

## Summary

Phase 5 implements per-section session.md merge strategies (TDD cycles 5.1-5.10) and updates worktree skill + execute-rule.md fragment for bidirectional merge workflow (general steps 5.11-5.13).

- Total items: 13 (10 cycles, 3 steps)
- Issues found: 0 critical, 3 major, 2 minor
- Issues fixed: 5
- Unfixable (escalation required): 0

**Overall Assessment**: Ready

## Major Issues

### Issue 1: Weak RED assertions in Cycle 5.1
**Location**: Cycle 5.1, RED Phase
**Problem**: RED phase assertions were structural (return type) without specific expected values for edge cases. "Returns (start_line, end_line) tuple" doesn't specify which line numbers to expect, making test prose too vague.
**Fix**: Added specific expected tuples for each assertion:
- `(2, 8)` for Pending Tasks test case
- `(9, 14)` for Worktree Tasks test case
- `(15, 20)` for Blockers with slash
- `(N, len(lines))` for EOF section
**Status**: FIXED

### Issue 2: Weak RED assertions in Cycle 5.8
**Location**: Cycle 5.8, RED Phase
**Problem**: Assertions described structure ("list of blocker items as line groups") without concrete examples. Executor could write tests checking only list type, not actual line group content.
**Fix**: Added specific test cases:
- Single blocker with 2 lines returns `[["- Issue X", "  Details here"]]`
- Two blockers return list of length 2
- No Blockers section returns `[]`
- Multi-line blocker with 3 continuations returns 4-string item
**Status**: FIXED

### Issue 3: Weak RED assertions in Cycle 5.10
**Location**: Cycle 5.10, RED Phase
**Problem**: Integration test assertions listed section names without expected merged values. "Status line: ours preserved" doesn't specify which date should appear or that theirs date should be absent.
**Fix**: Added specific expected values for each section strategy:
- Status line: ours date `"2026-02-16"` preserved, theirs `"2026-02-15"` discarded
- Pending Tasks: A+B+C merge with no duplicate B
- Blockers: 3 total (1 ours + 2 theirs tagged with `[from: test-slug]`)
- All other sections: ours preserved with item counts
**Status**: FIXED

## Minor Issues

### Issue 4: Missing prerequisite validation (Step 5.11)
**Location**: Step 5.11
**Problem**: Creation/modification step lacks investigation prerequisite. Step modifies skill file (Mode C section) but doesn't require reading it first to understand current behavior.
**Fix**: Added prerequisite: "Read `agent-core/skills/worktree/SKILL.md` Mode C section (lines 84-114) — understand merge ceremony workflow and exit code 0 auto-rm behavior."
**Status**: FIXED

### Issue 5: Missing prerequisite validation (Step 5.12)
**Location**: Step 5.12
**Problem**: Modification step lacks investigation prerequisite. Step changes execute-rule.md STATUS mode but doesn't require reading current implementation.
**Fix**: Added prerequisite: "Read `agent-core/fragments/execute-rule.md` STATUS mode section (lines 16-54) — understand current jobs.md data source and Unscheduled Plans display format."
**Status**: FIXED

## Fixes Applied

- Cycle 5.1 RED Phase: Added specific expected tuple values for all test assertions
- Cycle 5.8 RED Phase: Added concrete example test cases with expected list-of-lists structure
- Cycle 5.10 RED Phase: Added specific merged values for all section strategies (dates, task names, blocker counts, tags)
- Step 5.11: Added investigation prerequisite for worktree skill Mode C section
- Step 5.12: Added investigation prerequisite for execute-rule.md STATUS mode section
- Checkpoint 5.a: Added intermediate checkpoint after Cycle 5.5 (reduces gap from 10 cycles to 5+5 cycles between checkpoints)

## Observations

**TDD Discipline**: Strong. All RED phases have specific failure expectations. GREEN phases use behavior descriptions + hints, no prescriptive code. RED/GREEN sequencing is correct with foundation-first ordering (section identification → strategies → integration).

**Density consideration**: Cycles 5.2-5.7 apply identical "keep-ours" strategy to six different sections. While this creates apparent density, each section has different semantics (Status = volatile, Completed = session-scoped, Worktree Tasks = main-tracking, Reference Files/Next Steps = context-specific). Separate cycles document intent and enable independent failure analysis during execution. **Acceptable as-is.**

**File growth**: All projected additions well within limits:
- merge.py: ~100 lines (section strategies + blockers logic)
- session.py: ~30 lines (extract_blockers function)
- test_worktree_merge_sections.py: ~300 lines (new file, 10 tests)

**Checkpoint spacing**: Now optimal with checkpoints at 5.a (after 5 cycles) and 5.mid (after 10 cycles), plus final verification at 5.13.

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
