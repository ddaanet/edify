# Prioritization Report — 2026-02-27

**Methodology:** WSJF-adapted (CoD/Size). Fibonacci scale (1-8). User directive: recall/when-resolve first → workflow prose → workflow non-prose → rest.

**Column key:** WF=Workflow Friction, DP=Decay Pressure, CRR=Compound Risk Reduction, ME=Marginal Effort, CRC=Context Recovery Cost.

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Orchestrate evolution | 5 | 5 | 8 | 18 | 1 | 2 | 3 | 6.0 | sonnet, restart |
| 2 | Fix when-resolve.py | 8 | 3 | 8 | 19 | 3 | 1 | 4 | 4.8 | sonnet |
| 3 | when-resolve null mode | 5 | 3 | 5 | 13 | 2 | 1 | 3 | 4.3 | sonnet |
| 4 | Task classification | 5 | 3 | 3 | 11 | 2 | 2 | 4 | 2.8 | sonnet |
| 5 | Recall CLI integration | 5 | 3 | 5 | 13 | 3 | 2 | 5 | 2.6 | sonnet |
| 5 | Skill disclosure | 5 | 3 | 5 | 13 | 3 | 2 | 5 | 2.6 | opus |
| 7 | UserPromptSubmit topic | 8 | 3 | 8 | 19 | 5 | 3 | 8 | 2.4 | sonnet |
| 8 | Handoff --commit removal | 5 | 3 | 3 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 8 | Fix inline-exec findings | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | opus |
| 8 | Session scraping | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 8 | Worktree merge from main | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 8 | Runbook recall expansion | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 13 | When-resolve bloat | 5 | 2 | 5 | 12 | 5 | 1 | 6 | 2.0 | sonnet |
| 13 | Explore Anthropic plugins | 2 | 3 | 3 | 8 | 3 | 1 | 4 | 2.0 | sonnet, restart |
| 15 | Recall tool consolidation | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | sonnet |
| 15 | Ground workflow skills | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | opus |
| 15 | Tool deviation hook | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 15 | Markdown migration | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | opus |
| 15 | Artifact staleness gate | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 20 | Codebase sweep | 2 | 2 | 3 | 7 | 3 | 1 | 4 | 1.8 | sonnet |
| 21 | Fix task-context bloat | 5 | 2 | 3 | 10 | 5 | 1 | 6 | 1.7 | sonnet |
| 22 | Skill-dev skill | 3 | 3 | 5 | 11 | 5 | 2 | 7 | 1.6 | sonnet |
| 22 | Continuation prepend | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 22 | Entry gate propagation | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | opus |
| 22 | Retrofit skill pre-work | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | opus |
| 22 | Plugin migration | 2 | 8 | 3 | 13 | 3 | 5 | 8 | 1.6 | opus |
| 22 | Tweakcc | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 29 | Generate memory index | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 29 | Runbook post-explore gate | 3 | 2 | 5 | 10 | 5 | 2 | 7 | 1.4 | sonnet |
| 29 | Agent rule injection | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | sonnet |
| 29 | Tier threshold grounding | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 33 | Handoff insertion policy | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 33 | Cross-tree requirements | 3 | 3 | 3 | 9 | 5 | 2 | 7 | 1.3 | sonnet |
| 33 | Agentic prose terminology | 2 | 1 | 1 | 4 | 2 | 1 | 3 | 1.3 | sonnet |
| 33 | Test diagnostic helper | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 33 | Worktree fuzzy matching | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 38 | Stale recall artifact | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 38 | Runbook outline review | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 38 | TDD test optimization | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 38 | Review auto-commit | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 42 | Recall deduplication | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 42 | Recall pipeline | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 42 | Compensate-continue skill | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 42 | Upstream skills field | 1 | 1 | 1 | 3 | 2 | 1 | 3 | 1.0 | sonnet |
| 42 | Skill prompt-composer | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 42 | Model directive pipeline | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 48 | Feature prototypes | 2 | 2 | 2 | 6 | 5 | 2 | 7 | 0.9 | sonnet |
| 48 | Diagnose compression loss | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | sonnet |
| 48 | Test diamond migration | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | sonnet |
| 48 | Safety review expansion | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | opus |
| 48 | Recall learnings design | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | opus |
| 53 | Diagnostic opus review | 2 | 1 | 3 | 6 | 5 | 3 | 8 | 0.8 | opus |
| 54 | Infrastructure scripts | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 54 | Cache expiration | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 54 | Prioritize script | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 57 | Design-to-deliverable | 3 | 2 | 3 | 8 | 8 | 5 | 13 | 0.6 | opus, restart |
| 58 | Prose gate terminology | 2 | 1 | 1 | 4 | 5 | 3 | 8 | 0.5 | opus |
| 58 | Ground state coverage | 2 | 1 | 3 | 6 | 8 | 5 | 13 | 0.5 | opus |
| 58 | Workflow formal analysis | 2 | 1 | 3 | 6 | 8 | 5 | 13 | 0.5 | opus |
| 61 | Behavioral design | 2 | 1 | 2 | 5 | 8 | 5 | 13 | 0.4 | opus |

**Blocked tasks** (scored but not actionable):
- Parallel orchestration (2.2) — blocked on Orchestrate evolution
- Session CLI tool (2.2) — blocked [!]
- Test diamond migration (0.9) — depends on runbook evolution
- Safety review expansion (0.9) — depends on Explore Anthropic plugins

**Worktree task** (separate execution context):
- Session.md validator → `session-md-validator`

## Recommended Execution Order

User directive applied: recall/when-resolve → workflow prose → workflow non-prose → rest. Within each tier, WSJF determines order. Orchestrate evolution (6.0) is the highest-scoring task overall but falls in tier 3 (workflow non-prose); it surfaces as the first non-recall task.

### Tier 1: Recall/when-resolve fixes (foundational)

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 1 | Fix when-resolve.py | 4.8 | Highest-priority recall fix. Fuzzy match dedup + stdin acceptance. Direct `x`. |
| 2 | when-resolve null mode | 4.3 | Tiny change (add argument handling), anchors recall gates. |
| 3 | Recall CLI integration | 2.6 | Prototype delivered, Click CLI wrapping. Production `_recall` path. |
| 4 | UserPromptSubmit topic | 2.4 | Phase 7 analysis: highest-impact recall improvement. Keyword table + additionalContext injection. |
| 5 | Runbook recall expansion | 2.2 | Step agent + corrector recall during orchestration. Requirements exist. |

### Tier 2: Workflow prose improvements (load bearing)

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 6 | Skill disclosure | 2.6 | Progressive disclosure reduces context pollution. Requirements exist. |
| 7 | Ground workflow skills | 1.9 | /runbook → review agents → /orchestrate → /handoff per audit. |
| 8 | Skill-dev skill | 1.6 | Front-loads skill editing patterns. Replaces ambient rules path trigger. |
| 9 | Agentic prose terminology | 1.3 | Mechanical search-replace. Low effort, low impact. |

### Tier 3: Workflow non-prose

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 10 | Orchestrate evolution | 6.0 | Highest WSJF overall. Unblocks parallel-orchestration + TDD generation. Ready for orchestration. |
| 11 | Task classification | 2.8 | /prime skill + two-section task list. Outline reviewed, ready for runbook. |
| 12 | Handoff --commit removal | 2.2 | ~60 occurrences, well-scoped mechanical work. |
| 13 | Fix inline-exec findings | 2.2 | Rework — classification format + pivot table fixes. |

### Tier 4: Rest (by WSJF)

| Order | Task | Priority | Notable |
|-------|------|----------|---------|
| 14 | Session scraping | 2.2 | Enables recall dedup. Requirements captured. |
| 15 | Worktree merge from main | 2.2 | Merge failures documented in gotchas. |
| 16 | Explore Anthropic plugins | 2.0 | Unblocks safety review expansion. Restart required. |
| 17 | When-resolve bloat | 2.0 | Group entries by section. |
| 18 | Artifact staleness gate | 1.9 | Mechanical checkpoint at skill exit points. |
| 19 | Tool deviation hook | 1.9 | PostToolUse validation framework. |
| 20+ | (remaining 41 tasks) | ≤1.8 | See full table above |

## Parallel Batches

**Batch A — sonnet, recall, no restart:**
- Fix when-resolve.py (4.8) — target: `when-resolve.py`
- Recall CLI integration (2.6) — target: `src/claudeutils/`, Click CLI
- UserPromptSubmit topic (2.4) — target: hooks/settings, new system

**Batch B — sonnet, workflow, no restart:**
- Task classification (2.8) — target: `session.py`, `resolve.py`, execute-rule.md
- Handoff --commit removal (2.2) — target: skills, fragments (~60 files)
- Session scraping (2.2) — target: `plans/session-scraping/`

**Batch C — opus, no restart:**
- Fix inline-exec findings (2.2) — target: `plans/inline-execute/`
- Skill disclosure (2.6) — target: `plans/skill-progressive-disclosure/`
- Entry gate propagation (1.6) — target: /orchestrate, /deliverable-review, corrector

**Batch D — sonnet, restart cohort:**
- Orchestrate evolution (6.0) — 14 steps, restart required
- Explore Anthropic plugins (2.0) — install 28 plugins, restart required

## Scoring Assumptions

- **Fix when-resolve.py ME=3:** Requirements fully described in session.md inline (deduplicate fuzzy matches, accept stdin). Command is `x` (direct execution). No plan artifact, but scope is clear.
- **Task classification ME=2:** Session.md says "designed (outline reviewed, ready for runbook)" despite CLI showing `requirements`. Outline exists and has been reviewed.
- **Orchestrate evolution ME=1:** Plan status `ready`, runbook exists, orchestration command provided. Lowest marginal effort.
- **Plugin migration DP=8:** Flagged stale since Feb 9. Phase 4 needs rewrite. Highest decay pressure.
- **UserPromptSubmit CRR=8:** Phase 7 analysis explicitly recommends as "highest-impact recall improvement." Directly reduces agent recall failures.
- **when-resolve null mode ME=2:** Single argument addition to existing script. Minimal implementation scope.
- **Recall tool consolidation CRR=5 not 8:** Unifies naming but doesn't fix defects. Consolidation enables future fixes rather than directly preventing failures.

## Tension: WSJF vs User Directive

Orchestrate evolution (6.0) scores highest by WSJF due to ME=1 (ready for orchestration) and CRR=8 (unblocks 3+ tasks). The user directive places it in tier 3. This tension is valid — the user's judgment that recall is foundational infrastructure is domain knowledge that WSJF doesn't capture (recall quality affects the scoring of every downstream task's CRR). Recommendation: execute top 2-3 recall fixes first (small, high WSJF within recall tier), then Orchestrate evolution, then return to recall tier.

Pragmatic ordering: Fix when-resolve.py → when-resolve null mode → Orchestrate evolution → Recall CLI integration → rest of tiers.
