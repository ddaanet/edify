# Task Prioritization — 2026-02-18 (rev 4)

**Formula:** Priority = CoD / Size
**CoD** = Workflow Friction + Decay Pressure + Compound Risk Reduction
**Size** = Marginal Effort + Context Recovery Cost
Fibonacci scale (1,2,3,5,8). Tiebreak: higher CRR → lower Size → higher WF.

**Plan states (from `edify _worktree ls`):**
- plugin-migration: ready | runbook-quality-gates: ready | when-recall: ready
- worktree-merge-data-loss: ready | worktree-update: ready | workwoods: ready
- orchestrate-evolution: designed | worktree-skill: designed
- continuation-prepend/error-handling/parallel-orchestration/pretool-hook-cd-pattern/prototypes/quality-infrastructure/remaining-workflow-items/remember-skill-update/runbook-evolution/tweakcc/worktree-merge-resilience/worktree-rm-safety: requirements

**Completeness flag:** Vet delegation routing and Design runbook evolution marked `likely-complete` — design-runbook-evolution worktree implemented both (routing table in vet-requirement.md; SKILL.md + anti-patterns.md edits for all 5 FRs). Pending handoff verification.

---

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Runbook quality gates Phase B | 5 | 3 | 5 | 13 | 1 | 2 | 3 | **4.3** | sonnet |
| 2 | Runbook model assignment | 5 | 3 | 8 | 16 | 3 | 3 | 6 | **2.7** | sonnet |
| 3 | Script commit vet gate | 8 | 3 | 8 | 19 | 5 | 2 | 7 | **2.7** | sonnet |
| 4 | Vet delegation routing | 5 | 3 | 8 | 16 | 5 | 2 | 7 | **2.3** | sonnet, likely-complete |
| 5 | Worktree CLI default to --task | 3 | 5 | 8 | 16 | 5 | 2 | 7 | **2.3** | sonnet |
| 6 | Commit CLI tool | 8 | 3 | 5 | 16 | 5 | 2 | 7 | **2.3** | sonnet |
| 7 | Design quality gates | 5 | 3 | 5 | 13 | 3 | 3 | 6 | **2.2** | opus, restart |
| 8 | Continuation prepend | 5 | 2 | 3 | 10 | 3 | 2 | 5 | **2.0** | sonnet |
| 9 | Fix worktree rm dirty check | 3 | 5 | 5 | 13 | 5 | 2 | 7 | **1.9** | sonnet |
| 10 | Pre-merge untracked file fix | 3 | 5 | 5 | 13 | 5 | 2 | 7 | **1.9** | sonnet |
| 11 | Pipeline skill updates | 5 | 5 | 5 | 15 | 5 | 3 | 8 | **1.9** | opus, restart |
| 12 | Execute plugin migration | 2 | 8 | 3 | 13 | 2 | 5 | 7 | **1.9** | opus, stale |
| 13 | Quality infrastructure reform | 3 | 3 | 5 | 11 | 3 | 3 | 6 | **1.8** | opus |
| 14 | Cross-tree requirements transport | 3 | 3 | 3 | 9 | 3 | 2 | 5 | **1.8** | sonnet |
| 15 | Design runbook evolution | 5 | 3 | 3 | 11 | 3 | 3 | 6 | **1.8** | opus, restart, likely-complete |
| 16 | Test diagnostic helper | 3 | 2 | 5 | 10 | 5 | 1 | 6 | **1.7** | sonnet |
| 17 | Memory-index auto-sync | 3 | 3 | 5 | 11 | 5 | 2 | 7 | **1.6** | sonnet |
| 18 | Codebase quality sweep | 3 | 3 | 5 | 11 | 5 | 2 | 7 | **1.6** | sonnet |
| 19 | Remember skill update | 3 | 5 | 5 | 13 | 3 | 5 | 8 | **1.6** | opus |
| 20 | Handoff wt awareness | 5 | 3 | 3 | 11 | 5 | 2 | 7 | **1.6** | sonnet |
| 21 | Agent rule injection | 3 | 2 | 5 | 10 | 5 | 2 | 7 | **1.4** | sonnet |
| 22 | Handoff insertion policy | 5 | 2 | 3 | 10 | 5 | 2 | 7 | **1.4** | sonnet |
| 23 | Learning ages consol | 3 | 2 | 3 | 8 | 5 | 1 | 6 | **1.3** | sonnet |
| 24 | Revert cross-tree sandbox access | 3 | 3 | 3 | 9 | 5 | 2 | 7 | **1.3** | sonnet |
| 25 | Model tier awareness hook | 3 | 2 | 3 | 8 | 5 | 2 | 7 | **1.1** | sonnet, restart |
| 26 | Simplify when-resolve CLI | 3 | 2 | 1 | 6 | 5 | 1 | 6 | **1.0** | sonnet |
| 27 | Explore Anthropic plugins | 2 | 2 | 3 | 7 | 5 | 2 | 7 | **1.0** | sonnet, restart |
| 28 | Behavioral design | 3 | 5 | 5 | 13 | 8 | 5 | 13 | **1.0** | opus |
| 29 | Rename remember skill | 3 | 2 | 1 | 6 | 5 | 2 | 7 | **0.9** | sonnet, restart |
| 30 | Debug failed merge | 2 | 1 | 3 | 6 | 5 | 3 | 8 | **0.8** | sonnet |
| 31 | Feature prototypes | 2 | 2 | 1 | 5 | 3 | 3 | 6 | **0.8** | sonnet |
| 32 | Design-to-deliverable | 3 | 3 | 3 | 9 | 8 | 5 | 13 | **0.7** | opus, restart |
| 33 | Worktree skill adhoc mode | 2 | 2 | 1 | 5 | 5 | 2 | 7 | **0.7** | sonnet |
| 34 | Infrastructure scripts | 2 | 1 | 1 | 4 | 5 | 2 | 7 | **0.6** | sonnet |
| 35 | Diagnostic opus review | 2 | 2 | 3 | 7 | 8 | 5 | 13 | **0.5** | opus |
| 36 | Ground state-machine review criteria | 2 | 2 | 3 | 7 | 8 | 5 | 13 | **0.5** | opus |
| 37 | Upstream skills field | 1 | 1 | 1 | 3 | 5 | 1 | 6 | **0.5** | sonnet |
| 38 | Workflow formal analysis | 1 | 1 | 1 | 3 | 8 | 5 | 13 | **0.2** | opus |

### Blocked Tasks (scored, excluded from main ranking)

| Task | Priority | Blocked On |
|------|----------|------------|
| Orchestrate evolution | 3.0 | Design runbook evolution (worktree) |
| RED pass protocol | 1.9 | Error handling design (worktree) |
| Safety review expansion | 1.3 | Explore Anthropic plugins |
| Remember agent routing | 1.3 | Memory redesign (Remember skill update) |
| Migrate test suite to diamond | 1.1 | Runbook evolution design |

---

## Parallel Batches

**Batch A — sonnet, no restart (3 tasks):**
- Runbook quality gates Phase B (priority 4.3) — plans/runbook-quality-gates + validate-runbook.py
- Script commit vet gate (priority 2.7) — commit skill + vet-requirement.md
- Worktree CLI default to --task (priority 2.3) — worktree/cli.py

No shared plan directories or target files.

**Batch B — sonnet, no restart (2 tasks):**
- Runbook model assignment (priority 2.7) — runbook phase files (multiple plans)
- Continuation prepend (priority 2.0) — plans/continuation-prepend

No overlap.

**Batch C — opus, restart (2 tasks):**
- Pipeline skill updates (priority 1.9) — orchestrate/deliverable-review/design skills
- Quality infrastructure reform (priority 1.8) — plans/quality-infrastructure

No overlap. Restart tasks batch adjacently.

**Batch D — sonnet, no restart (3 tasks):**
- Memory-index auto-sync (priority 1.6) — memory-index.md + /remember skill
- Handoff wt awareness (priority 1.6) — handoff skill
- Agent rule injection (priority 1.4) — agent template files

No overlap.

**Note:** Fix worktree rm dirty check (rank 9) and Pre-merge untracked file fix (rank 10) both target `src/edify/worktree/` — cannot parallelize safely.

---

## Top 5 Recommendations

**1. Runbook quality gates Phase B (4.3)** — Ready (runbook exists). Lowest effort (ME=1), immediate execution value. TDD for 4 validate-runbook.py subcommands. Start here.

**2. Batch A parallel (ranks 2, 3, 5)** — Runbook model assignment + Script commit vet gate + Worktree CLI default to --task. All CRR=8, address patterns with 3+ RCA occurrences. No file conflicts. Run concurrently in 3 worktrees.

**3. Design quality gates (2.2, opus, restart)** — Requirements ready, 3 open questions well-scoped. Batch with Pipeline skill updates (Batch C). Requires restart; do after sonnet batch clears.

**4. Continuation prepend (2.0) + Runbook model assignment (2.7)** — Batch B. Both sonnet, no restart. Runbook model assignment is partially landed (directive exists, remaining files to update).

**5. Verify and close likely-complete tasks** — Vet delegation routing (rank 4) and Design runbook evolution (rank 15) may already be done. Verify against session.md during next handoff before queueing.

---

## Scoring Assumptions

- **Vet delegation routing / Design runbook evolution:** Marked `likely-complete` — design-runbook-evolution worktree added routing table to vet-requirement.md and completed all 5 SKILL.md FRs. Session.md not yet updated. Scored at current requirements planstate.
- **Execute plugin migration (rank 12):** DP=8 (stale Feb 9, 19→? skills drift). ME=2 (ready planstate) but CRC=5 (phases need rewrite, conversation history needed). Recovery cost dominates.
- **Orchestrate evolution:** Scores 3.0 but blocked; would rank #2 once Design runbook evolution confirmed complete.
- **Fix worktree rm dirty check:** Plan worktree-rm-safety [requirements]. ME=5 (no runbook yet).
- **Runbook model assignment:** "Partially landed" — directive in design-decisions.md + remaining runbooks known. ME=3 (designed-equivalent).
- **Worktree module conflicts:** Fix worktree rm dirty check + Pre-merge untracked file fix both modify `src/edify/worktree/`. Sequential required.
