# Session Handoff: 2026-02-24

**Status:** Recall pass requirements updated with FR-11 (cognitive boundaries), fast path coverage, on-demand memory-index, batch-resolve. Skill review applied.

## Completed This Session

**Recall pass pipeline (prior sessions, carried forward):**
- `plans/recall-pass/requirements.md` — 10 FRs, 3 NFRs, 5 constraints
- `plans/recall-pass/outline.md` — 10 key decisions, all open questions resolved
- 4 pipeline skill files edited with recall artifact generation, augmentation, injection, and review recall (47 insertions across design, runbook, orchestrate, deliverable-review skills)

**`/recall` skill — interactive recall pass (prior sessions, carried forward):**
- Created `agent-core/skills/recall/SKILL.md` — manual recall for interactive sessions
- 5-mode taxonomy: default, deep, broad, all, everything
- Tail-recursive design with mechanical exit condition

**Read tool context optimization test (prior sessions, carried forward):**
- No dedup — each Read appends. Skip-tracking confirmed necessary.

**Recall pass requirements expansion (this session):**
- FR-11 added: recall at every cognitive boundary (not just 4 pipeline stages)
  - Before requirements capture, exploration, design outline (A.5), full design (C.1), runbook outline (0.75), phase expansion (Phase 1), implementation, tests, review/correction
  - Within-session recall as compaction insurance (low cost, high upside)
- FR-1 enhanced: on-demand memory-index read (not preloaded), batch-resolve via `when-resolve.py`, no-requirements keyword derivation, memory-index amplification property documented
- C-1: "pipeline stages" → "cognitive boundaries"
- C-3: expanded integration points to `/requirements`, granular design/runbook phases, Tier 1/2
- Q-4: resolved by FR-11 (yes, mid-design recall)

**Fast path recall coverage (this session):**
- Runbook Tier 1: recall context paragraph — read artifact + lightweight recall when no artifact
- Runbook Tier 2: same + injection into delegation prompts with format-per-tier
- Design direct execution (outline-sufficient + C.5): review recall in corrector prompt
- Runbook Phase 0.5: on-demand memory-index read, batch-resolve, removed stale "do NOT grep" language

**Pipeline contracts updated:**
- T1 output: +recall-artifact.md
- T2 input: +recall-artifact.md

**On-demand memory-index pattern (this session):**
- Removed memory-index from ambient CLAUDE.md preloading assumption
- All recall points now: Read memory-index.md (skip if already in context)
- First recall point in session reads it; subsequent points find it loaded
- "Scan file" language replaced everywhere — prevents spurious file re-reads

**Skill review (this session):**
- Batch review of 5 modified skills (design, runbook, recall, when, how)
- 2 major fixes: runbook description trigger phrases, Tier 1 format-per-tier guidance
- 4 minor fixes: recall skip-phrasing standardized, "Bash transport" → "batch-resolve", cumulative behavior wording, cross-reference stability

**/when and /how stale reference fix:**
- Removed "already loaded via CLAUDE.md @-reference" from both skills
- Replaced with "already in context from prior /recall, /when, or /how invocation"

## Pending Tasks

- [x] **Recall pass requirements** — implemented via Tier 2 delegation
- [ ] **Sync-to-parent sandbox documentation** — update references to document required sandbox bypass | haiku
- [ ] **Rename when-resolve.py to claudeutils _recall** — consolidate into CLI, remove `..file` syntax | sonnet
- [x] **Read tool context optimization test** — run T1 protocol, no dedup confirmed | sonnet
- [ ] **Consolidate /when and /how into /recall** — phase out as separate skills, ensure /recall covers reactive single-entry lookups | sonnet

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**`just sync-to-parent` requires sandbox bypass:**
- Recipe removes and recreates symlinks in `.claude/` — sandbox blocks `rm` on those paths

## Next Steps

Sync-to-parent sandbox documentation (haiku) or consolidate /when+/how into /recall (sonnet).

## Reference Files

- `plans/recall-pass/requirements.md` — 11 FRs including FR-11 cognitive boundaries
- `plans/recall-pass/outline.md` — pipeline recall pass design (10 key decisions)
- `agent-core/skills/recall/SKILL.md` — interactive recall skill (5 modes)
- `agents/decisions/pipeline-contracts.md` — T1/T2 recall-artifact.md in I/O flow
