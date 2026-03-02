# Cycle 3.1

**Plan**: `plans/worktree-merge-from-main/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Cycle 3.1: `resolve_learnings_md` from-main policy (FR-2)

When `from_main=True`, invert ours/theirs in diff3: main (theirs) is base, branch (ours) additions are delta.

**Files:** `src/claudeutils/worktree/resolve.py`

**RED:** Set up merge with conflicting learnings.md. Main has consolidated learnings (fewer entries), branch has original + new entries. Call `resolve_learnings_md(conflicts, from_main=True)`. Assert: result uses main's entries as base, branch-only entries appended, entries in both not doubled.

**GREEN:** Add `from_main: bool = False` to `resolve_learnings_md`. When from_main: swap ours/theirs when calling `diff3_merge_segments` — pass theirs_segs as ours and ours_segs as theirs. The diff3 merge then treats main as the authoritative base and branch entries as additions.

**Dependencies:** Phase 1 (Cycles 1.1, 1.2)

**Stop/Error Conditions:**
- RED passes before implementation → conflict fixture may not include learnings.md; verify index stages :1:/:2:/:3: exist
- Entries doubled in result → ours/theirs swap logic incorrect; check which side is base vs delta
- Branch-only entries missing → diff3 treating branch entries as deletions instead of additions
