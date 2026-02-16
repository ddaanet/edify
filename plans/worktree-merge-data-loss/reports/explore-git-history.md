# Worktree Merge Data Loss: Git History Investigation

## Summary

The worktree merge for `review-runbook-delegation` (3d72597) lost parent repository files (pipeline-contracts.md, learnings.md, memory-index.md) that were committed to the worktree branch tip (063add3) after the agent-core submodule merge (63a10da). The merge operation succeeded, exited 0, and reported "Precommit passed" despite the data loss. The missing files were later recovered via cherry-pick (1438fbc).

## Key Findings

### Commit Timeline and Merge Structure

**Worktree branch sequence:**
- Commit `63a10da` (2026-02-16 12:47:42): Merge agent-core from review-runbook-delegation
  - Parent: `63a10da^1` (HEAD at parent merge point: 2026-02-16 12:47:42)
  - Changed: `agent-core` submodule pointer only
  - Absolute path: `/Users/david/code/claudeutils/` history shows this as merge commit

- Commit `063add3` (2026-02-16 12:47:16): Add artifact review routing table and orchestrator delegation
  - Parent: `28c7641` (Focused session for review-runbook-delegation)
  - Changed: 5 files in both parent repo and agent-core submodule
    - `agent-core` → submodule update
    - `agents/decisions/pipeline-contracts.md` → +19 lines (new "When Routing Artifact Review" section)
    - `agents/learnings.md` → updated (6 lines changed)
    - `agents/memory-index.md` → +1 line (new entry: `/when routing artifact review`)
    - `agents/session.md` → +28/-9 lines (orchestrator review delegation updates)

**Merge commit:**
- Commit `3d72597` (2026-02-16 12:48:38): 🔀 Merge review-runbook-delegation
  - Parent: `63a10da` (only one parent recorded in git object)
  - Changed: Only `agents/session.md` (-6 lines, removing completed worktree tasks)
  - Timing: ~1 minute after worktree branch tip (063add3)

**Recovery:**
- Commit `1438fbc` (2026-02-16 12:49:44): 🩹 Recover review-runbook-delegation parent repo changes
  - Cherry-picked from 063add3 to recover the lost files
  - Changed: Same 3 parent-repo files as in 063add3
    - `agents/decisions/pipeline-contracts.md` → +19 lines
    - `agents/learnings.md` → +6/-3 lines
    - `agents/memory-index.md` → +1 line

### Data Loss Analysis

**Files that should have merged but didn't:**

1. **`agents/decisions/pipeline-contracts.md`**
   - Worktree branch (063add3): 128 lines (109 + 19 new)
   - Main after merge (3d72597): 109 lines
   - Content lost: "When Routing Artifact Review" section with artifact type → reviewer routing table
   - Lines lost: 19

2. **`agents/learnings.md`**
   - Worktree branch (063add3): Updated with broader orchestrator review delegation scope
   - Main after merge (3d72597): Not updated
   - Content lost: Updated learning about review delegation scope
   - Lines lost: 3 (net of consolidation changes)

3. **`agents/memory-index.md`**
   - Worktree branch (063add3): Added `/when routing artifact review` entry
   - Main after merge (3d72597): Entry not added
   - Content lost: Memory index entry for artifact review routing
   - Lines lost: 1

**Files that did merge correctly:**

- `agents/session.md`: Correctly merged (removed completed worktree task entries)
- `agent-core` submodule: Correctly merged (submodule pointer updated)

### Merge Operation Details

**Merge process (from merge.py implementation):**

The worktree CLI invokes 4 phases:
1. **Phase 1 (_phase1_validate_clean_trees):** Check branch exists and both trees are clean
2. **Phase 2 (_phase2_resolve_submodule):** Resolve agent-core submodule if worktree differs
3. **Phase 3 (_phase3_merge_parent):** Initiate `git merge --no-commit --no-ff slug`
4. **Phase 4 (_phase4_merge_commit_and_precommit):** Commit merge and run `just precommit`

**Session.md conflict resolution:**

During Phase 3, the merge operation encounters a conflict in agents/session.md because:
- Main (63a10da parent): Has completed worktree tasks in Worktree Tasks section
- Worktree branch (063add3): Removed completed tasks (they're done)
- Conflict auto-resolved by `_resolve_session_md_conflict()`: Merges task blocks by name, keeping "ours" (main) base with new tasks from worktree inserted

**Critical finding:** The merge operation reports `returncode == 0` in Phase 3 despite parent-repo files NOT being merged:

```python
# Phase 3 merge initiation
result = subprocess.run(
    ["git", "merge", "--no-commit", "--no-ff", slug],
    capture_output=True,
    text=True,
    check=False,
)
if result.returncode == 0:
    return  # <-- EXITS HERE (line 238-239 in merge.py)
```

If merge succeeds (returncode == 0), Phase 3 returns immediately without checking what was actually merged.

### Root Cause Hypothesis

The merge succeeded because there were no conflicts in the files that should have been updated. However, git's three-way merge strategy failed to detect that:

1. **63a10da parent tree** had 109 lines in pipeline-contracts.md
2. **063add3 worktree tree** had 128 lines in pipeline-contracts.md (added routing table)
3. **Merge result (3d72597)** kept 109 lines (worktree changes lost)

This suggests one of:
- Git's merge strategy algorithm selected the wrong parent (incorrect tree traversal)
- The merge algorithm was in "fast-forward" or "ours" mode despite `--no-ff` flag
- The merge algorithm didn't properly compare the parent tree vs worktree tree for non-conflicting files
- The merge was actually a squash or cherry-pick disguised as a merge (unlikely given `--no-ff`)

**Observable evidence of incorrect merge:**
```
git cat-file -p 3d72597 | grep parent
# Output: parent 63a10da0689055f49aa3fe1257a0fa0e4734be99
# ONLY ONE PARENT — but merge.py runs: git merge --no-commit --no-ff slug
# The --no-ff flag should force a merge commit with TWO parents
```

The merge has only ONE parent in git object storage, indicating the merge was either:
- Never actually a two-way merge (branch squashed or rebased before merge)
- Executed as a fast-forward instead of a true merge
- The merge algorithm never considered the worktree branch tip

### Session.md Conflict Auto-Resolution

The one file that WAS merged correctly provides a clue:

**Session.md conflict resolution steps (from _resolve_session_md_conflict):**
1. Extract task blocks from both sides (ours: main, theirs: worktree)
2. Find new tasks in theirs that don't exist in ours
3. Insert new task blocks before next section
4. **Explicitly call:** `_git("add", "agents/session.md")` (line 111)

Session.md was processed by explicit conflict resolution code, so it merged correctly. The other 3 files were NOT in the explicit conflict list, so they fell through to git's automatic merge — which failed silently.

### No-Conflict Merge Failure Pattern

**The bug pattern:**
- Files with explicit conflict resolution (session.md) → merged correctly
- Files without conflicts (pipeline-contracts.md, learnings.md, memory-index.md) → silently lost
- Git's automatic merge for non-conflicting files failed to notice parent-repo changes

This is not a git bug (git is working correctly for conflicts/no-conflicts distinction). This is a merge orchestration bug: the worktree merge code assumes that if `git merge --no-commit` returns 0, all intended changes were merged. But when there are no conflicts, git reports success without verifying that all parent repo changes were actually included.

### Submodule Merge Success

The agent-core submodule merged correctly:
- Phase 2 resolves submodule differences before the main merge
- Submodule pointer is deterministically resolved before moving to parent merge
- Submodule conflict handling is explicit and tested

The fact that submodule merged correctly while parent-repo files didn't suggests the issue is specific to the parent repository merge strategy, not a git issue.

## Patterns and Cross-File Consistency

**All three lost files are "semantic" files:**
- `pipeline-contracts.md`: Defines contracts and decision routing
- `learnings.md`: Records institutional knowledge
- `memory-index.md`: Records knowledge retrieval paths

**All three would be detected by precommit if the detection were working:**
- `agents/memory-index.md`: Validated by precommit (word count, orphan entries, placement)
- `agents/learnings.md`: Validated by precommit (word count, invalidated entries)
- `agents/decisions/pipeline-contracts.md`: Validated by reference checks (decisions/...)

**Why precommit didn't catch this:**
The merge reported "Precommit passed" but the precommit check couldn't have run on the original worktree branch changes because those files were already lost before precommit ran. Precommit validated the *merge result state*, not the worktree branch content.

## Investigation Gaps and Unresolved Questions

1. **Two-parent mystery:** Why does git show only ONE parent for a `--no-ff` merge?
   - Need to: Reproduce the exact git sequence to understand if this is a git version issue, a merge strategy selection issue, or a CLI invocation issue
   - Speculation: The merge may have been run without `--no-ff`, or the branch may have been fast-forwarded during the merge

2. **Silent failure of `git merge` exit code 0:**
   - Git returns 0 for successful merges (completed + resolved conflicts)
   - Git returns 0 for successful automatic merges (no conflicts)
   - Git does NOT return 0 for incomplete merges (unresolved conflicts)
   - The merge succeeded, but didn't merge all intended files — a successful partial merge

3. **Phase 2 submodule resolution side effects:**
   - Did Phase 2 submodule merge accidentally commit changes that affected subsequent file merge state?
   - The agent-core submodule pointer was updated; did this trigger a weird merge state?

4. **Git version and merge strategy:**
   - What version of git was used? (affects merge strategy algorithm)
   - What was the configured `merge.strategy`? (could be set to "ours" or "recursive" with different behavior)
   - Was there a merge driver configured for specific files?

5. **Exact command sequence in Phase 3/4:**
   - The merge.py code calls `git merge --no-commit --no-ff slug`
   - But the resulting commit shows only one parent
   - Need to trace: Did `git merge` succeed and complete? Or did it return before creating the merge?

## Recovery Strategy Effectiveness

The cherry-pick recovery (1438fbc) successfully restored the three lost files with exact content from the worktree branch tip (063add3). Recovery was mechanical and non-destructive — it added the missing content back after the merge.

**Effectiveness limitations:**
- Cherry-pick only works if the lost commit is still in git history (063add3 still exists)
- Recovery was manual discovery after the fact (not automatic)
- No automated detection occurred; loss was discovered through review
- The merge CLI reported success despite data loss, so no alerts

## Files Changed in Worktree Branch (063add3)

**Worktree branch tip (063add3) vs its parent (63a10da):**

```
agent-core                             |  2 +-  (submodule update)
agents/decisions/pipeline-contracts.md | 19 ++++++++++++++++++++
agents/learnings.md                    |  6 +++---
agents/memory-index.md                 |  1 +
agents/session.md                      | 28 +++++++++++++++++++++++-----
5 files changed, 47 insertions(+), 9 deletions(-)
```

Specifically:
- **pipeline-contracts.md**: Added new "When Routing Artifact Review" section with 6-row artifact type → reviewer mapping table
- **learnings.md**: Updated orchestrator review delegation scope (3 lines changed, broader context)
- **memory-index.md**: Added entry `/when routing artifact review` for memory index recall
- **session.md**: Updated orchestrator review delegation context in Pending Tasks
- **agent-core**: Submodule pointer advanced to new commit with runbook patterns updates

## Merge Commit Content

**Merge commit (3d72597) diff:**

Only `agents/session.md` shows in diff:
```
diff --git a/agents/session.md b/agents/session.md
index 266e5ba..d8a355c 100644
--- a/agents/session.md
+++ b/agents/session.md
@@ -120,13 +120,7 @@

 ## Worktree Tasks

-- [ ] **Review runbook delegation** → `review-runbook-delegation` — ...
-- [ ] **Handoff memory naming** → `handoff-memory-naming` — ...

 ## Blockers / Gotchas
```

The merge removed the two completed worktree task entries as expected. But the three other files from the worktree branch (pipeline-contracts.md, learnings.md, memory-index.md) are completely absent from the merge result — they were not merged.

## Precommit Validation Post-Merge

The merge claimed "Precommit passed" in Phase 4 (line 295 in merge.py):

```python
precommit_result = subprocess.run(
    ["just", "precommit"],
    capture_output=True,
    text=True,
    check=False,
)

if precommit_result.returncode == 0:
    click.echo("Precommit passed")
```

**Why precommit didn't catch the loss:**

Precommit runs AFTER the merge is complete, validating the working tree state at that point. The three lost files were never merged into the tree, so precommit has no way to know they should have been there. It validates the current state (109-line pipeline-contracts.md), which is internally consistent — the file exists, has valid structure, all references are resolvable.

Precommit would have caught the loss if:
1. There was a reference validator that checked "pipeline-contracts.md must have section X"
2. There was a git merge validator that compared merge input vs output
3. There was a worktree merge-specific validator that checked branch content vs merge result

None of these exist in the current precommit checks.

## Recommended Investigation Steps

1. **Check git object store:** Verify merge.py actually created a two-parent merge or if the merge was squashed/rebased
2. **Test git version:** Reproduce with `git merge --no-commit --no-ff` on a test branch to see if same issue occurs
3. **Review merge.py call sequence:** Add debug output to verify all phases execute as expected
4. **Add post-merge validation:** Check that merge output contains expected files from worktree branch
5. **Add content hash verification:** After merge, verify key files have content from worktree branch, not just presence

## Related Code Locations

- **Merge implementation:** `/Users/david/code/claudeutils/src/claudeutils/worktree/merge.py` (302-line module)
- **CLI entry point:** `/Users/david/code/claudeutils/src/claudeutils/worktree/cli.py` (merge command at line 342-344)
- **Session conflict resolution:** `merge.py` lines 58-113 (_resolve_session_md_conflict)
- **Phase 3 merge initiation:** `merge.py` lines 230-258 (_phase3_merge_parent)
- **Phase 4 precommit:** `merge.py` lines 261-299 (_phase4_merge_commit_and_precommit)

## Git Command Verification

To verify the merge structure:

```bash
# Check parent count
git cat-file -p 3d72597 | grep parent
# Expected: parent <hash1> and parent <hash2> (two lines for merge commit)
# Actual: parent 63a10da0689055f49aa3fe1257a0fa0e4734be99 (one parent only)

# Check what files the merge touched
git diff 3d72597^1 3d72597 --name-only
# Only returns: agents/session.md

# Check if worktree branch was actually merged
git merge-base 3d72597 063add3
# Returns: 9879075 (common ancestor is far back, not 063add3)
```

The single-parent merge structure is the smoking gun: a merge with `--no-ff` should always create two parents, even if the content would be identical to a fast-forward.
