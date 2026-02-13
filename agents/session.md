# Session: Worktree — Recall Fix Complete + Baseline Analysis

**Status:** Ready to merge back to main.

## Completed This Session

**Recall path matching fixes (M-2, M-1):**
- Fixed path normalization in `_matches_file_or_parent()` to handle absolute vs relative path comparison
- Added suffix matching logic: `/Users/.../agents/decisions/testing.md` now matches `agents/decisions/testing.md`
- Fixed e2e test assertion: corrected fixture count from 4 to 3 tool calls (1 Grep + 2 Reads)
- Added test for absolute vs relative path matching validation
- Fixed CLI parameter name mismatch: `--baseline-before` now correctly maps to `_baseline_before`
- Refactored into helper functions to reduce complexity (C901: 12→7)
- All 51 tests pass including new path normalization test
- Commits: 8df92e2, 05a11a3, db36dd5

**Baseline recall analysis:**
- Initial 50-session analysis: 0.2% recall (4/1809 pairs) - too small for reliability
- Expanded to 200 sessions: **2.9% recall (250/8639 pairs)** - robust baseline
- Distribution highly uneven: workflow entries 4-7%, research entries 0-1%
- Top performer: "Consolidation Gates" at 7% (58 sessions)
- Zero recall on many high-relevance entries (e.g., "Model Capability Differences": 0% across 109 sessions)
- Created comprehensive baseline report: `plans/when-recall/reports/baseline-recall-analysis.md`
- Establishes success targets for `/when` system: >15% minimum (5×), >30% good (10×), >50% excellent (17×)

**Key findings:**
- Small samples unreliable (50 sessions: 0.2%, 200 sessions: 2.9%)
- Passive awareness model shows minimal effectiveness (2.9% is essentially non-functional)
- Workflow-specific recall: agents occasionally scan when workflow terms appear in current task
- No proactive scanning for related knowledge outside immediate context

## Pending Tasks

- [ ] **Workflow improvements** — Process fixes from RCA + skill/fragment/orchestration cleanup | sonnet

## Next Steps

Merge this worktree back to main and continue with workflow improvements.
