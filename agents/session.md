# Session Handoff: 2026-02-20

**Status:** When recall evaluation complete. memory-index.md demotion unblocked with evidence.

## Completed This Session

**When recall evaluation:**
- Wrote prototype `tmp/when-recall-eval.py` scanning 801 sessions across 71 project directories (main + 70 worktrees)
- Findings: `/when` used in 8/193 post-merge sessions (4.1%), 22 total calls, direct reads unchanged (21.2% → 21.8%), 1.1× improvement (noise)
- Root cause: metacognitive recognition bottleneck — changing lookup mechanism (Read → Skill) doesn't change the recognition step (knowing you're uncertain)
- Discussion conclusion: hook-based injection or structural embedding are the viable paths; `/when` occupies a dead zone requiring the same recognition it was designed to bypass
- Report: `tmp/when-recall-eval-report.md`
- Updated `plans/context-optimization/brief.md` — unblocked memory-index.md (3.7k tokens) demotion with evidence, updated savings estimate to ~34%

## Pending Tasks

- [x] **When recall evaluation** — sonnet

## Reference Files

- `tmp/when-recall-eval-report.md` — Full evaluation report with methodology, weekly timeline, per-file breakdown
- `tmp/when-recall-eval.py` — Prototype script (reusable for future measurement)
- `plans/context-optimization/brief.md` — Updated with memory-index demotion evidence
