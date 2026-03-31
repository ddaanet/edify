# Prioritization Report — 2026-03-02b

**Methodology:** WSJF-adapted (CoD/Size). Fibonacci scale (1-8). Flat priority ordering (tiers removed). Supersedes 2026-03-02 report.

**Delta from 2026-03-02:** 6 new tasks scored. Tiers removed from session.md — tasks ordered by WSJF with pragmatic override (ME=1 quick wins first). Score prototype parameterized (`tmp/score.py --new <file>`). pushback-grounding archived (delivered). Learnings merge validated clean across all post-diff3 merges.

**New tasks scored:**
- Directive skill promotion (1.6) — opus, d:/p:/w prose-gate failures
- Plan-completion ceremony (1.4) — opus, 7/12 orphaned plans traced to this gap
- plugin lint coverage (1.0) — opus, zero enforcement on load-bearing hooks
- Worktree exit ceremony (1.6) — sonnet, restored after autostrategy merge drop
- Discuss-to-pending chain (1.6) — sonnet, restored after autostrategy merge drop
- Worktree merge resilience (2.2) — sonnet, outlined, ready for /runbook

**Column key:** WF=Workflow Friction, DP=Decay Pressure, CRR=Compound Risk Reduction, ME=Marginal Effort, CRC=Context Recovery Cost. Tasks marked `*` are new.

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Orchestrate evolution | 5 | 5 | 8 | 18 | 1 | 2 | 3 | 6.0 | sonnet, restart |
| 2 | Merge completed filter | 3 | 2 | 3 | 8 | 1 | 1 | 2 | 4.0 | sonnet, inline |
| 3 | Execute flag lint | 5 | 2 | 5 | 12 | 3 | 1 | 4 | 3.0 | haiku |
| 4 | Skill disclosure | 5 | 3 | 5 | 13 | 3 | 2 | 5 | 2.6 | opus |
| 5 | Session.md validator | 5 | 2 | 5 | 12 | 3 | 2 | 5 | 2.4 | sonnet |
| 6 | Worktree merge resilience * | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 6 | Session scraping | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 6 | Worktree merge from main | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 6 | Handoff --commit removal | 5 | 3 | 3 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 10 | Explore Anthropic plugins | 2 | 3 | 3 | 8 | 3 | 1 | 4 | 2.0 | sonnet, restart |
| 10 | Wt ls session ordering | 5 | 2 | 1 | 8 | 3 | 1 | 4 | 2.0 | sonnet |
| 12 | Tool deviation hook | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 12 | Artifact staleness gate | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 12 | Lint-gated recall | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 12 | Lint recall gate | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 12 | Recall tool consolidation | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | sonnet |
| 12 | Ground workflow skills | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | opus |
| 12 | Markdown migration | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | opus |
| 19 | Merge lifecycle audit | 3 | 3 | 5 | 11 | 3 | 3 | 6 | 1.8 | sonnet |
| 19 | Codebase sweep | 2 | 2 | 3 | 7 | 3 | 1 | 4 | 1.8 | sonnet |
| 19 | Block cd-chaining | 3 | 1 | 3 | 7 | 3 | 1 | 4 | 1.8 | sonnet |
| 22 | Fix task-context bloat | 5 | 2 | 3 | 10 | 5 | 1 | 6 | 1.7 | sonnet |
| 23 | Skill-dev skill | 3 | 3 | 5 | 11 | 5 | 2 | 7 | 1.6 | sonnet |
| 23 | Directive skill promotion * | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | opus |
| 23 | Entry gate propagation | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | opus |
| 23 | Retrofit skill pre-work | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | opus |
| 23 | Worktree exit ceremony * | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 23 | Discuss-to-pending chain * | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 23 | Tweakcc | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 23 | Wt rm task cleanup | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 23 | Worktree ad-hoc task | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 23 | Plugin migration | 2 | 8 | 3 | 13 | 3 | 5 | 8 | 1.6 | opus |
| 33 | Remove wt rm --force | 2 | 1 | 3 | 6 | 3 | 1 | 4 | 1.5 | sonnet |
| 33 | Design context gate | 3 | 3 | 3 | 9 | 3 | 3 | 6 | 1.5 | sonnet |
| 35 | Plan-completion ceremony * | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 35 | Generate memory index | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 35 | Agent rule injection | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | sonnet |
| 35 | Tier threshold grounding | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 39 | Handoff insertion policy | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 39 | Test diagnostic helper | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 39 | Cross-tree requirements | 3 | 3 | 3 | 9 | 5 | 2 | 7 | 1.3 | sonnet |
| 39 | Agentic prose terminology | 2 | 1 | 1 | 4 | 2 | 1 | 3 | 1.3 | sonnet |
| 43 | Corrector removal audit | 3 | 2 | 5 | 10 | 5 | 3 | 8 | 1.2 | sonnet |
| 43 | Memory-index loading docs | 2 | 2 | 1 | 5 | 3 | 1 | 4 | 1.2 | sonnet |
| 43 | Wt merge-rm shorthand | 3 | 1 | 1 | 5 | 3 | 1 | 4 | 1.2 | sonnet |
| 46 | Runbook outline review | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 46 | TDD test optimization | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 46 | Review auto-commit | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 46 | Moderate outline gate | 3 | 3 | 3 | 9 | 5 | 3 | 8 | 1.1 | opus, self-ref |
| 46 | Dev integration branch | 3 | 3 | 3 | 9 | 5 | 3 | 8 | 1.1 | opus |
| 51 | Worktree CLI UX | 3 | 1 | 3 | 7 | 5 | 2 | 7 | 1.0 | sonnet |
| 51 | plugin lint coverage * | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 51 | Recall deduplication | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 51 | Recall pipeline | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 51 | Compensate-continue skill | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 51 | Skill prompt-composer | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 51 | Model directive pipeline | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 51 | Decision drift audit | 2 | 3 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 51 | Recall usage scoring | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 51 | Delivery supercession | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 51 | Upstream skills field | 1 | 1 | 1 | 3 | 2 | 1 | 3 | 1.0 | sonnet |
| 51 | Registry cache to tmp | 2 | 1 | 1 | 4 | 3 | 1 | 4 | 1.0 | sonnet, inline |
| 51 | Update prioritize skill | 2 | 1 | 1 | 4 | 3 | 1 | 4 | 1.0 | sonnet |
| 64 | Merge lock retry | 2 | 1 | 3 | 6 | 5 | 2 | 7 | 0.9 | sonnet |
| 64 | Diagnose compression loss | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | sonnet |
| 64 | Test diamond migration | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | sonnet |
| 64 | Safety review expansion | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | opus |
| 64 | Recall learnings design | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | opus |
| 64 | Feature prototypes | 2 | 2 | 2 | 6 | 5 | 2 | 7 | 0.9 | sonnet |
| 70 | Diagnostic opus review | 2 | 1 | 3 | 6 | 5 | 3 | 8 | 0.8 | opus |
| 70 | Task notation migration | 1 | 1 | 1 | 3 | 3 | 1 | 4 | 0.8 | sonnet |
| 72 | Infrastructure scripts | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 72 | Cache expiration | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 72 | Prioritize script | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 75 | Design-to-deliverable | 3 | 2 | 3 | 8 | 8 | 5 | 13 | 0.6 | opus, restart |
| 76 | Ground state coverage | 2 | 1 | 3 | 6 | 8 | 5 | 13 | 0.5 | opus |
| 76 | Workflow formal analysis | 2 | 1 | 3 | 6 | 8 | 5 | 13 | 0.5 | opus |
| 76 | Prose gate terminology | 2 | 1 | 1 | 4 | 5 | 3 | 8 | 0.5 | opus |
| 79 | Behavioral design | 2 | 1 | 2 | 5 | 8 | 5 | 13 | 0.4 | opus |

**Blocked tasks** (scored but not actionable):
- Parallel orchestration — blocked on Orchestrate evolution
- Session CLI tool — blocked [!]
- Python hook ordering fix — blocked [!]
- Calibrate topic params — needs production data accumulation
- Safety review expansion — depends on Explore Anthropic plugins

## Pragmatic Ordering

Session.md uses WSJF as base with one override: Merge completed filter (4.0, ME=1) placed first despite Orchestrate evolution (6.0) having higher WSJF. Rationale: single-line fix delivers immediate merge-safety value; Orchestrate evolution requires restart + 14 steps.

No tier structure. WSJF scores shown inline on each task for transparent ordering rationale.

## Scoring Assumptions (new tasks)

- **Directive skill promotion WF=5:** d: fires every discussion, p: every task creation. DP=3: directive infrastructure stable but growing. CRR=5: 2× grounding skip + 3× model misclassification in single session.
- **Plan-completion ceremony WF=3:** Fires per plan delivery (weekly). DP=3: orphan count grows. CRR=5: 7/12 orphans traced to this gap, defect compounding.
- **plugin lint coverage WF=3:** Hook edits are weekly. DP=2: hooks stable. CRR=3: proactive catch, no incidents yet. ME=5: no design artifact.
- **Worktree exit ceremony WF=3, CRR=3:** Per-worktree lifecycle. Requirements exist (brief.md).
- **Discuss-to-pending chain WF=3, CRR=3:** Per-discussion verdict. 3× missed in one session. Requirements exist (brief.md).
- **Worktree merge resilience WF=3, CRR=5:** Per-merge. Outline ready. Post-diff3 validation shows no current data loss, but outline addresses gaps (divergent edits, precommit structural validation) that diff3 doesn't cover.
