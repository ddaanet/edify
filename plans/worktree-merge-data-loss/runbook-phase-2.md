# Phase 2: Skill Update (General)

**Type:** general
**Model:** haiku
**Scope:** Track 3 (SKILL.md Mode C documentation)

---

## Step 2.1: Update SKILL.md Mode C step 3 — add `rm` exit 1 handling and escalation guidance

**Objective:** Document the new `rm` exit 1 behavior (from Phase 1) in the worktree skill Mode C merge ceremony.

**Script Evaluation:** Small (≤25 lines inline prose addition)

**Execution Model:** Haiku

**Prerequisite:** Read `agent-core/skills/worktree/SKILL.md` (lines 84-115) — understand Mode C merge ceremony flow, especially step 3 (exit code 0 success path).

**Implementation:**

After successful merge (step 3, line 92), the skill calls `claudeutils _worktree rm <slug>` to clean up. Phase 1 Track 1 implementation adds a guard to `rm` that refuses removal (exit 1) when the branch has unmerged real history.

Add handling for `rm` exit 1 after the merge success case. Insert new prose between current step 3 and step 4.

**Content to add (after line 92):**

```markdown
   **Handle `rm` exit 1:** After successful merge (exit 0), `rm` may refuse removal if the branch has unmerged commits. Check `rm` exit code:

   - **Exit code 0:** Cleanup succeeded. Continue to "Task complete" output.
   - **Exit code 1:** Guard refused removal due to unmerged commits. This indicates the merge may be incomplete despite reporting success (exit 0). **Escalate to user:** "Merge may be incomplete — branch {slug} has unmerged commits after merge reported success. Verify merge correctness before forcing removal."

   Do NOT retry `rm` with force flags or work around the refusal. The guard detects a merge correctness issue that requires investigation.
```

**Location:**
- File: `agent-core/skills/worktree/SKILL.md`
- Section: Mode C (Merge Ceremony)
- Insertion point: After line 92 (step 3), before line 94 (step 4)
- Current step 3 ends with: `Output: "Merged and cleaned up <slug>. Task complete."`
- New content handles the `rm` exit 1 case before proceeding to step 4

**Expected Outcome:**

Mode C step 3 now has two exit code branches:
1. **`rm` exit 0:** Cleanup succeeded → output success message
2. **`rm` exit 1:** Guard refused → escalate to user with explanation

The escalation message explains:
- What happened: merge succeeded (exit 0) but rm refused (exit 1)
- Why it's concerning: mismatch indicates possible merge incompleteness
- What NOT to do: retry with force or workarounds
- What to do: verify merge correctness, investigate

**Error Conditions:**

None — prose-only addition to documentation.

**Validation:**

1. **Read** the modified SKILL.md Mode C section
2. **Verify** new prose is present after step 3
3. **Verify** content matches design specification (design.md line 162)
4. **Verify** no unintended changes to surrounding steps

**Design Reference:** design.md lines 158-164 (Track 3: Skill Update)

**Relationship to Phase 1:** Depends on Phase 1 Track 1 guard implementation (Cycles 1.1-1.8). The `rm` command will now exit 1 when branch has unmerged real history. This step documents that new behavior in the skill that orchestrates merge+rm.

