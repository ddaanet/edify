# Brief: delivery-supercession

## Problem

When a plan delivers and its directory is deleted, superseded decision entries in other files persist. Agents load both the old and new entry, get contradictory guidance.

The delivery workflow (`/handoff` → `/commit` → plan-archive → trim) has no supercession check. It updates the target decision file but never scans for entries the new decision contradicts.

## Evidence

**task-classification delivery (2026-02-28):**
- Delivered two-section model (In-tree / Worktree Tasks) to `operational-tooling.md`
- Left stale single-section entry in `workflow-advanced.md` (2026-02-20)
- Agent running `wt` loaded both entries, got conflicting section model
- Downstream: `wt` Mode B couldn't dispatch — all tasks In-tree, stale model said single section was correct

## Existing Delivery Chain

Per "How to end workflow with handoff and commit" (workflow-optimization.md): all tiers end with `/handoff` → `/commit`. Handoff captures context and learnings, plan-archive records delivery, trim removes the task. None of these steps check for superseded entries.

Per "When writing recall artifacts" (workflow-advanced.md): artifacts are keys only, downstream resolves current content. This means stale *entries* (not stale *excerpts*) are the problem — an entry pointing to a superseded decision resolves to contradictory content.

Per "When deleting agent artifacts" (workflow-planning.md): distinguish audit trails from redundant restates. Superseded decision entries are redundant restates of a now-incorrect position — they should be deleted, not preserved for audit.

## Proposed Solution

Memory-index supercession pass at plan delivery. After writing/updating the primary decision entry:
1. Scan `agents/memory-index.md` for entries whose trigger phrases overlap with the new entry's domain
2. Resolve candidates via `claudeutils _recall resolve`
3. Compare against new entry — contradictory entries get deleted, partially overlapping entries get updated
4. Remove stale memory-index triggers pointing to deleted entries

## Scope Questions (for /design)

- **Automated vs agent-judged:** Keyword overlap detection (mechanical) or read-both-and-assess (judgment)? Per "When verifying delivered plan artifacts": presence != completeness, content verification needed. Suggests agent-judged.
- **Trigger point:** At `/codify` consolidation, at plan-archive write, or both? `/codify` already touches memory-index (step 4a) — natural insertion point. But delivery without `/codify` (direct decision write) would skip the gate.
- **Partial overlap:** Old entry partially superseded (some content still valid). Update retained content or split into a new entry?
- **Self-referential check:** Per "When checking self-referential modification" — the scan must exclude the plan's own new entry from the candidate set.

## Related

- **Plan-completion ceremony** (1.4) — the delivery side-effects gap causing orphan plans. Supercession is one missing side-effect alongside plan-dir deletion, plan-archive write, lifecycle.md update.
- **Decision drift audit** (1.0) — reactive audit of stale assumptions. This task is the proactive gate that prevents drift at source.
- **`/codify` step 4a** — manual append to memory-index, no supercession check. Natural integration point.
