# Runbook Expansion: COMPLETE

**Plan:** worktree-merge-data-loss
**Date:** 2026-02-16
**Status:** Ready for prepare-runbook.py

## What Was Done

### Phase 1: Core Implementation (TDD)
- **File:** plans/worktree-merge-data-loss/runbook-phase-1.md
- **Items:** 13 TDD cycles
- **Tracks:**  - Track 1 (Cycles 1.1-1.8): Removal guard (cli.py)
  - Track 2 (Cycles 1.9-1.13): Merge correctness (merge.py)
- **Review:** Opus review applied 5 fixes (all minor), no UNFIXABLE
- **Report:** plans/worktree-merge-data-loss/reports/runbook-phase-1-review.md

### Phase 2: Skill Update (General)
- **File:** plans/worktree-merge-data-loss/runbook-phase-2.md
- **Items:** 1 prose step (SKILL.md Mode C update)
- **Review:** Opus review found 0 issues, ready as-is
- **Report:** plans/worktree-merge-data-loss/reports/runbook-phase-2-review.md

## Requirements Coverage

All 9 functional requirements addressed:

| Requirement | Phase | Items | Status |
|-------------|-------|-------|--------|
| FR-1: Branch classification | Phase 1 | 1.1-1.3 | ✅ Complete |
| FR-2: Guard refusal (exit 1) | Phase 1 | 1.4-1.5 | ✅ Complete |
| FR-3: Focused-session-only allowed | Phase 1 | 1.6 | ✅ Complete |
| FR-4: Exit codes (0/1/2) | Phase 1 | 1.4-1.6 | ✅ Complete |
| FR-5: No destructive suggestions | Phase 1 | 1.7-1.8 | ✅ Complete |
| FR-6: MERGE_HEAD checkpoint | Phase 1 | 1.9, 1.11 | ✅ Complete |
| FR-7: Ancestry validation | Phase 1 | 1.12 | ✅ Complete |
| FR-8: Removal type messages | Phase 1 | 1.5-1.6 | ✅ Complete |
| FR-9: Skill exit 1 handling | Phase 2 | 2.1 | ✅ Complete |

## Assembly Validation

- ✅ Phase files exist and are committed
- ✅ Reviews complete (5 fixes applied, no blockers)
- ✅ Item numbering sequential
- ✅ Requirements fully traced
- ✅ Cross-phase dependencies verified
- ✅ File path references validated

## Next Step

**Phase 4: Prepare Artifacts**

Run prepare-runbook.py to create execution artifacts:

```bash
agent-core/bin/prepare-runbook.py plans/worktree-merge-data-loss/runbook-phase-1.md
# Requires dangerouslyDisableSandbox: true (writes to .claude/agents/)
```

Then:
1. Copy orchestrate command to clipboard
2. Tail-call `/handoff --commit`
3. Restart session
4. Paste `/orchestrate worktree-merge-data-loss`

## Artifacts Created

- `plans/worktree-merge-data-loss/runbook-phase-1.md` (654 lines)
- `plans/worktree-merge-data-loss/runbook-phase-2.md` (69 lines)
- `plans/worktree-merge-data-loss/reports/runbook-phase-1-review.md`
- `plans/worktree-merge-data-loss/reports/runbook-phase-2-review.md`
- `plans/worktree-merge-data-loss/EXPANSION-COMPLETE.md` (this file)

## Design Alignment

All 7 design decisions mapped to specific cycles:
- D-1: Focused session marker text (Cycle 1.2)
- D-2: Exit codes 0/1/2 (Cycles 1.4-1.6)
- D-3: No destructive output (Cycle 1.8)
- D-4: MERGE_HEAD checkpoint (Cycles 1.9-1.10)
- D-5: Ancestry validation (Cycle 1.12)
- D-6: Guard before destruction (Cycle 1.7)
- D-7: `_is_branch_merged` in utils.py (Cycle 1.1)

