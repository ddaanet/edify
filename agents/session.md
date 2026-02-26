# Session Handoff: 2026-02-26

**Status:** Routing model applied to `/design` and `/runbook` skills. 7 fix points implemented. Discussion identified two additional issues: A.2.5 gate design (recall-diff inappropriate, replaced with when-resolve null anchor) and direct execution criteria alignment (design gate must match runbook Tier 1 on capacity).

## Completed This Session

**Complexity routing grounding (`/ground`):**
- Parallel diverge: internal codebase exploration (scout) + external research (7 frameworks: Cynefin, Stacey, Boehm Spiral, XP Spikes, SAFe Enablers, Lean Startup, Gartner Bimodal)
- Synthesized 6 principles, all general-first with project instance
- Three-dimensional classification model: complexity (existing Stacey) × work type (new: Production/Exploration/Investigation) × artifact destination (new: production/exploration/investigation paths)
- 7 fix points across `/design` (Phase 0 output, Phase 0 vocabulary, Simple path recall, Phase B routing, second recall after explore) and `/runbook` (destination-aware counting, threshold flagging)
- Discussion resolved all gaps: three-tier structure grounded in execution environment constraints, time-boxing irrelevant to agentic execution, prototype-to-production handled by existing `/design`, artifact destination reclassified as adaptation not gap
- Grounding quality: Strong

**Execution strategy decision file:**
- `agents/decisions/execution-strategy.md` — captures why three tiers (context window capacity, delegation overhead, prompt generation cost), boundary analysis, relationship to complexity routing
- User's explanation preserved as reference for future `/design` and `/runbook` skill revisions

**Apply routing model (7 fix points):**
- `/design` Phase 0: Work Type Assessment subsection (Production/Exploration/Investigation vocabulary, diagnostic questions, assessment signals), artifact destination table, expanded classification output block
- `/design` Simple routing: recall-explore-execute pattern replaces bare "skip design"
- `/design` A.2.5: Post-explore recall gate with `when-resolve.py null` anchor (replaced recall-diff.sh — wrong tool for uncommitted exploration)
- `/design` Phase B + C.5: Work-type-aware execution routing (exploration/investigation → direct, production + behavioral code → /runbook), capacity criterion added, changelog text removed
- `/runbook` tier assessment: artifact destination field + destination-aware file counting table
- `/runbook` Tier 1/2/3: all thresholds flagged as ungrounded with cross-reference to execution-strategy.md

**Discussion findings (post-implementation):**
- `recall-diff.sh` inappropriate for A.2.5: uses git log since mtime, but exploration reports are uncommitted — script finds nothing. Replaced with memory-index re-scan + when-resolve gate anchor
- `when-resolve.py null` does not exist yet — needs implementation as no-op mode for gate anchoring (equalizes cost between positive/negative recall paths)
- Direct execution criteria in `/design` must assess capacity (not just coordination complexity) since it bypasses `/runbook` entirely
- Session scraping integration into when-resolve.py discussed as path to context-aware deduplication — separate task

## Pending Tasks

- [x] **Complexity routing** — `/ground plans/complexity-routing/problem.md` | opus | restart
  - Ground classification + routing model against external frameworks (Cynefin, XP spikes, Lean)
  - Produces revised taxonomy and routing rules; skill edits are separate execution task
- [x] **Apply routing model** — apply grounded model to `/design` and `/runbook` skills | sonnet
  - 7 fix points from grounding report: `plans/reports/complexity-routing-grounding.md`
  - `/design`: Phase 0 output + vocabulary, Simple path recall-explore-recall, Phase B exploration routing, second recall after explore
  - `/runbook`: destination-aware file counting, flag thresholds as ungrounded
  - Reference: `agents/decisions/execution-strategy.md` for tier rationale
- [ ] **when-resolve null mode** — add no-op `null` argument to `when-resolve.py` for gate anchoring | sonnet
  - Equalizes tool call cost between positive/negative recall paths
  - Prevents fast-pathing past recall gates
  - Referenced by `/design` A.2.5 post-explore recall gate
- [ ] **Recall deduplication** — integrate session context scraping into `when-resolve.py` to filter already-loaded entries | sonnet
  - Session scraper prototype: `plans/prototypes/session-scraper.py`
  - Dedup should be opt-in (`--new-only` flag or `null` mode), not default — explicit queries may resolve for sub-agent prompts
- [ ] **Tier threshold grounding** — calibrate Tier 1/2/3 file-count thresholds against empirical data | opus
  - Thresholds (<6, 6-15, >15) are ungrounded operational parameters
  - Needs measurement from execution history, not confabulated heuristics

## Reference Files

- `plans/reports/complexity-routing-grounding.md` — grounded classification + routing model (6 principles, 7 fix points)
- `plans/reports/complexity-routing-internal-codebase.md` — internal branch: decision gates, git history, failure patterns
- `plans/reports/complexity-routing-external-research.md` — external branch: 7 frameworks with routing analysis
- `agents/decisions/execution-strategy.md` — three-tier execution rationale (context window economics)
- `plans/complexity-routing/problem.md` — original problem statement (4 gaps)
