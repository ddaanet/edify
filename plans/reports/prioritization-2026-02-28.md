# Prioritization Report — 2026-02-28

**Methodology:** WSJF-adapted (CoD/Size). Fibonacci scale (1-8). User directive: recall/when-resolve first → workflow prose → workflow non-prose → rest. Supersedes 2026-02-27 report.

**Delta from 2026-02-27:** Post-merge rescore. 3 tasks delivered (removed), 3 tasks disappeared (absorbed/completed in worktrees), 19 tasks new or rescored. Arithmetic via `tmp/score.py`.

**Column key:** WF=Workflow Friction, DP=Decay Pressure, CRR=Compound Risk Reduction, ME=Marginal Effort, CRC=Context Recovery Cost. Tasks marked `*` are new or rescored.

## Priority Table

| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |
|------|------|----|----|-----|-----|----|-----|------|----------|-----------|
| 1 | Orchestrate evolution | 5 | 5 | 8 | 18 | 1 | 2 | 3 | 6.0 | sonnet, restart |
| 2 | Recall skill path fix * | 3 | 3 | 3 | 9 | 1 | 1 | 2 | 4.5 | haiku, inline |
| 3 | UPS topic injection * | 5 | 3 | 5 | 13 | 2 | 2 | 4 | 3.2 | sonnet |
| 4 | Execute flag lint * | 5 | 2 | 5 | 12 | 3 | 1 | 4 | 3.0 | haiku |
| 5 | Task classification | 5 | 3 | 3 | 11 | 2 | 2 | 4 | 2.8 | sonnet |
| 6 | Fix planstate detector * | 5 | 3 | 5 | 13 | 3 | 2 | 5 | 2.6 | sonnet |
| 6 | Skill disclosure | 5 | 3 | 5 | 13 | 3 | 2 | 5 | 2.6 | opus |
| 8 | Session.md validator * | 5 | 2 | 5 | 12 | 3 | 2 | 5 | 2.4 | sonnet |
| 9 | Session scraping | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 9 | Worktree merge from main | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 9 | Runbook recall expansion | 3 | 3 | 5 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 9 | Handoff --commit removal | 5 | 3 | 3 | 11 | 3 | 2 | 5 | 2.2 | sonnet |
| 13 | Explore Anthropic plugins | 2 | 3 | 3 | 8 | 3 | 1 | 4 | 2.0 | sonnet, restart |
| 13 | Wt ls session ordering * | 5 | 2 | 1 | 8 | 3 | 1 | 4 | 2.0 | sonnet |
| 15 | Lint-gated recall * | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 15 | Lint recall gate * | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 15 | Tool deviation hook | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 15 | Artifact staleness gate | 5 | 3 | 5 | 13 | 5 | 2 | 7 | 1.9 | sonnet |
| 15 | Recall tool consolidation | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | sonnet |
| 15 | Ground workflow skills | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | opus |
| 15 | Markdown migration | 5 | 5 | 5 | 15 | 5 | 3 | 8 | 1.9 | opus |
| 22 | Block cd-chaining * | 3 | 1 | 3 | 7 | 3 | 1 | 4 | 1.8 | sonnet |
| 22 | Codebase sweep | 2 | 2 | 3 | 7 | 3 | 1 | 4 | 1.8 | sonnet |
| 24 | Fix task-context bloat | 5 | 2 | 3 | 10 | 5 | 1 | 6 | 1.7 | sonnet |
| 25 | Skill-dev skill | 3 | 3 | 5 | 11 | 5 | 2 | 7 | 1.6 | sonnet |
| 25 | Entry gate propagation | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | opus |
| 25 | Retrofit skill pre-work | 5 | 3 | 5 | 13 | 5 | 3 | 8 | 1.6 | opus |
| 25 | Pushback grounding * | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 25 | Continuation prepend | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 25 | Tweakcc | 3 | 2 | 3 | 8 | 3 | 2 | 5 | 1.6 | sonnet |
| 25 | Plugin migration | 2 | 8 | 3 | 13 | 3 | 5 | 8 | 1.6 | opus |
| 32 | Remove wt rm --force * | 2 | 1 | 3 | 6 | 3 | 1 | 4 | 1.5 | sonnet |
| 33 | Generate memory index | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 33 | Agent rule injection | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | sonnet |
| 33 | Tier threshold grounding | 3 | 3 | 5 | 11 | 5 | 3 | 8 | 1.4 | opus |
| 36 | Handoff insertion policy | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 36 | Test diagnostic helper | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 36 | Worktree fuzzy matching | 3 | 2 | 3 | 8 | 5 | 1 | 6 | 1.3 | sonnet |
| 36 | Cross-tree requirements | 3 | 3 | 3 | 9 | 5 | 2 | 7 | 1.3 | sonnet |
| 36 | Agentic prose terminology | 2 | 1 | 1 | 4 | 2 | 1 | 3 | 1.3 | sonnet |
| 41 | Memory-index loading docs * | 2 | 2 | 1 | 5 | 3 | 1 | 4 | 1.2 | sonnet |
| 42 | Runbook outline review | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 42 | TDD test optimization | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 42 | Review auto-commit | 3 | 2 | 3 | 8 | 5 | 2 | 7 | 1.1 | sonnet |
| 42 | Moderate outline gate * | 3 | 3 | 3 | 9 | 5 | 3 | 8 | 1.1 | opus, self-ref |
| 42 | Dev integration branch * | 3 | 3 | 3 | 9 | 5 | 3 | 8 | 1.1 | opus |
| 47 | Recall usage scoring * | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 47 | Delivery supercession * | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 47 | Decision drift audit * | 2 | 3 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 47 | Recall deduplication | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 47 | Recall pipeline | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 47 | Compensate-continue skill | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 47 | Skill prompt-composer | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | sonnet |
| 47 | Model directive pipeline | 3 | 2 | 3 | 8 | 5 | 3 | 8 | 1.0 | opus |
| 47 | Upstream skills field | 1 | 1 | 1 | 3 | 2 | 1 | 3 | 1.0 | sonnet |
| 47 | Registry cache to tmp * | 2 | 1 | 1 | 4 | 3 | 1 | 4 | 1.0 | sonnet, inline |
| 47 | Update prioritize skill * | 2 | 1 | 1 | 4 | 3 | 1 | 4 | 1.0 | sonnet |
| 58 | Diagnose compression loss | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | sonnet |
| 58 | Test diamond migration | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | sonnet |
| 58 | Safety review expansion | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | opus |
| 58 | Recall learnings design | 2 | 2 | 3 | 7 | 5 | 3 | 8 | 0.9 | opus |
| 58 | Feature prototypes | 2 | 2 | 2 | 6 | 5 | 2 | 7 | 0.9 | sonnet |
| 63 | Diagnostic opus review | 2 | 1 | 3 | 6 | 5 | 3 | 8 | 0.8 | opus |
| 64 | Infrastructure scripts | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 64 | Cache expiration | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 64 | Prioritize script | 2 | 1 | 2 | 5 | 5 | 2 | 7 | 0.7 | sonnet |
| 67 | Design-to-deliverable | 3 | 2 | 3 | 8 | 8 | 5 | 13 | 0.6 | opus, restart |
| 68 | Prose gate terminology | 2 | 1 | 1 | 4 | 5 | 3 | 8 | 0.5 | opus |
| 68 | Ground state coverage | 2 | 1 | 3 | 6 | 8 | 5 | 13 | 0.5 | opus |
| 68 | Workflow formal analysis | 2 | 1 | 3 | 6 | 8 | 5 | 13 | 0.5 | opus |
| 71 | Behavioral design | 2 | 1 | 2 | 5 | 8 | 5 | 13 | 0.4 | opus |

**Blocked tasks** (scored but not actionable):
- Parallel orchestration — blocked on Orchestrate evolution
- Session CLI tool — blocked [!]
- Python hook ordering fix — blocked [!]
- Calibrate topic params — blocked by UPS topic injection
- Test diamond migration — depends on runbook evolution (delivered, but task not updated)
- Safety review expansion — depends on Explore Anthropic plugins

## Delivered Since Last Report (removed)

- Fix when-resolve.py (was rank 2, priority 4.8) → plan: when-resolve-fix [delivered]
- when-resolve null mode (was rank 3, priority 4.3) → plan: recall-null [delivered]
- Recall CLI integration (was rank 5, priority 2.6) → plan: recall-cli-integration [delivered]

## Disappeared (absorbed or completed in worktrees)

- When-resolve bloat (was rank 13, priority 2.0) — not in session.md
- Fix inline-exec findings (was rank 8, priority 2.2) — inline-execute plan in `rework`, no explicit pending task
- Runbook post-explore gate (was rank 29, priority 1.4) — not in session.md
- Stale recall artifact (was rank 38, priority 1.1) — absorbed into Recall tool consolidation

## Recommended Execution Order

User directive preserved: recall → workflow prose → workflow non-prose → rest.

### Tier 1: Recall (foundational)

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 1 | Recall skill path fix | 4.5 | ME=1, just completed in this session. Needs commit only. |
| 2 | UPS topic injection | 3.2 | Outline exists, infrastructure delivered (flatten-hook-tiers). Narrower scope than old "UserPromptSubmit topic" — injection only. |
| 3 | Fix planstate detector | 2.6 | Requirements exist. Two known misdetections (task-classification, userpromptsubmit-topic) causing wrong routing commands. |
| 4 | Runbook recall expansion | 2.2 | Step agent + corrector recall. 7 FRs at requirements stage. |

### Tier 2: Workflow prose

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 5 | Skill disclosure | 2.6 | Progressive disclosure at gate boundaries. Requirements exist. |
| 6 | Ground workflow skills | 1.9 | Per audit: /runbook → review agents → /orchestrate → /handoff. |

### Tier 3: Workflow non-prose

| Order | Task | Priority | Rationale |
|-------|------|----------|-----------|
| 7 | Orchestrate evolution | 6.0 | Highest WSJF. Ready for orchestration. Restart required. |
| 8 | Task classification | 2.8 | Outline reviewed, ready for runbook (planstate bug shows `requirements`). |
| 9 | Handoff --commit removal | 2.2 | ~60 occurrences, well-scoped. |

## Parallel Batches

**Batch A — haiku/sonnet, recall, no restart:**
- Recall skill path fix (4.5) — already done this session, needs commit
- Execute flag lint (3.0) — target: precommit validators
- Fix planstate detector (2.6) — target: planstate detection code

**Batch B — sonnet, workflow, no restart:**
- Task classification (2.8) — target: session.py, resolve.py, execute-rule.md
- Session.md validator (2.4) — target: precommit validators
- Handoff --commit removal (2.2) — target: skills, fragments (~60 files)

**Batch C — opus, no restart:**
- Skill disclosure (2.6) — target: /design, /runbook skill loading
- Ground workflow skills (1.9) — target: skills per audit
- Entry gate propagation (1.6) — target: /orchestrate, /deliverable-review, corrector

**Batch D — sonnet, restart cohort:**
- Orchestrate evolution (6.0) — 14 steps, restart required
- Explore Anthropic plugins (2.0) — install 28 plugins, restart required

## Scoring Assumptions

- **Recall skill path fix ME=1:** Mechanical substitution across 15 active files. Already executed in this session — only commit remains.
- **UPS topic injection ME=2:** Outline exists and was updated post-flattening. Infrastructure delivered (flatten-hook-tiers reviewed). Narrower scope than parent "UserPromptSubmit topic" task.
- **Execute flag lint ME=3:** Clear requirements in session.md (pattern match on session.md pending tasks). No plan artifact.
- **Fix planstate detector ME=3:** Requirements at `plans/fix-planstate-detector/requirements.md`. CLI shows `requirements` status.
- **Session.md validator ME=3:** Requirements at `plans/session-validator/requirements.md`. Includes plan-archive coverage check.
- **Wt ls session ordering WF=5:** Fires every status display. But CRR=1 (cosmetic ordering, no defect fix).
- **Lint-gated recall / Lint recall gate:** Both address "loaded decisions miss error context" learning (2+ occurrences). Complementary layers: injection (PostToolUse) + gate (PreToolUse). ME=5 each (no design artifact, needs hook design).
- **Moderate outline gate:** Self-referential (modifies /design during active use). Single data point — trigger condition needs sharper criteria.

## Tension: WSJF vs User Directive (updated)

Same tension as 2026-02-27: Orchestrate evolution (6.0) scores highest but falls in tier 3. The recall skill path fix (4.5) is new at rank 2 but already executed — effectively free. UPS topic injection (3.2) is the highest-effort new task in tier 1.

Updated pragmatic ordering: commit recall skill fix → UPS topic injection → Fix planstate detector → Orchestrate evolution → rest of tiers.
