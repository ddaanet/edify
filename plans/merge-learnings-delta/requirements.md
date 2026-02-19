# Merge Learnings Delta

## Problem

When merging a worktree branch that diverged before a learnings consolidation on main, `claudeutils _worktree merge` brings in the branch's full pre-consolidation `agents/learnings.md` over main's consolidated version. Git's merge strategy sees the branch version as a superset and favors it, silently reverting the consolidation.

**Observed:** 30-line (consolidated) → 222-line (pre-consolidation + branch additions) after merge. 175 lines were duplicates of content already consolidated into permanent documentation (`agents/decisions/*.md`, `agent-core/fragments/*.md`).

**Root cause:** Git textual merge has no semantic understanding of consolidation. The branch's learnings.md is a strict superset of the common ancestor, so git takes the branch version. Main's version is shorter (post-consolidation) and git treats the deletions as conflicting with the branch's additions.

**Scope:** `agents/learnings.md` is the primary target. `agents/session.md` has similar merge semantics but is handled by existing ours-strategy resolution. This requirements doc focuses on learnings.md only.

**Both merge directions affected:**
- **Branch → main** (`_worktree merge`): Main consolidated, branch has pre-consolidation content. Observed case.
- **Main → branch** (merge-from-main / catch-up): Branch has pre-consolidation content, main consolidated since branch point. Same divergence, reversed roles — the "local" side has stale content, "incoming" side has consolidated version. The reconciliation strategy is symmetric: consolidated version is the base, delta from the other side is appended.

## Functional Requirements

**FR-1: Detect consolidation divergence**

After merge completes, detect when a consolidation event occurred on one side since the common ancestor. The consolidated side is the base; the other side's delta is appended. Applies to both merge directions.

Detection must use explicit consolidation markers, not line-count heuristics. "Shorter than ancestor" is unreliable — learnings can shrink from supersession (new learning replaces old), invalidation (step 4b of handoff), or manual cleanup. None of these are consolidations.

Acceptance criteria:
- Detect consolidation via explicit marker (see Open Questions Q-1)
- Identify which side(s) had consolidation events since common ancestor
- Flag when merged result contains pre-consolidation content from the non-consolidated side
- Works for both `_worktree merge` (branch → main) and merge-from-main (main → branch)

**FR-2: Reconstruct correct learnings.md**

When consolidation divergence is detected, automatically reconstruct the correct file: consolidated version (side with consolidation marker) + delta from the other side (new entries added after branch point).

Acceptance criteria:
- Consolidated side's learnings.md is the base
- Append only new `## heading` blocks that appear in the other side's tip but not in the common ancestor
- Preserve ordering of appended entries (same order as branch tip)
- Result is staged and included in the merge commit (amend if merge commit already created)

**FR-3: Handle edge cases**

Acceptance criteria:
- No delta (non-consolidated side didn't add learnings): learnings.md matches consolidated version exactly
- Non-consolidated side modified existing entries (not just appended): modifications to entries that were consolidated are dropped (consolidation is authoritative); modifications to entries still in consolidated version are preserved
- No consolidation happened (no marker on either side): no action needed, standard merge behavior correct
- Multiple consolidations since branch point: same logic applies (consolidated version is authoritative base)
- Both sides consolidated independently: merge both consolidated versions, append both deltas (degenerate case — unlikely in practice)

## Non-Functional Requirements

**NFR-1: No merge failure**
Learnings reconciliation must not cause the merge to fail. If reconstruction fails for any reason, warn and leave the merged file as-is (user can fix manually). The merge tool already has exit code conventions — this should not introduce new failure modes.

**NFR-2: Transparent operation**
Report when reconciliation is applied: "Reconciled learnings.md: kept N consolidated + appended M new entries from branch (dropped K pre-consolidation duplicates)."

## Open Questions

**Q-1: Consolidation marker mechanism**

How to mark consolidation commits so the merge tool can detect them reliably.

Candidates:
- **Git trailer** (`Consolidation: true` in commit message) — lightweight, queryable via `git log --grep`, no tooling change beyond `/remember` adding the trailer
- **Co-modification signature** (commit touches both `agents/learnings.md` and `agents/decisions/` or `agent-core/fragments/`) — heuristic, no marker needed, but needs empirical grounding against commit history to verify reliability
- **Metadata file** (e.g., `agents/.last-consolidation` with commit SHA) — explicit, but adds a tracked file

Recommendation: Git trailer is simplest. `/remember` already controls the commit — adding a trailer is a one-line change. Merge tool queries `git log --grep="Consolidation: true" <ancestor>..<tip> -- agents/learnings.md`.

Needs: Empirical check of co-modification signature against existing history before deciding. If signature is reliable, trailer is redundant.

## Implementation Notes

- The merge tool already has special handling for session.md (ours strategy). Learnings.md needs a different strategy: "consolidated base + other side's delta."
- `git merge-base` provides the common ancestor. `git show <ref>:agents/learnings.md` provides content at any point.
- Entry boundaries are `## ` headings — each learning is a discrete block.
- The delta extraction can use heading comparison: headings in one side's tip that don't appear in common ancestor are new.
- Strategy is direction-agnostic: detect which side had a consolidation event, use it as base, append delta from the other side. Same code path for both merge directions.
