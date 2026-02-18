# Step 5.3

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Step 5.3: Update SKILL.md Mode C — add exit code 3 handling (C-1, prose atomicity)

**Objective:** Document exit code 3 semantics and resolution workflow in SKILL.md Mode C. Update existing exit 1 handling to distinguish precommit failure from conflict-pause. All SKILL.md changes in this single step.

**Script Evaluation:** Prose — targeted edits to existing Mode C section.

**Execution Model:** Opus (prose artifact, LLM-consumed — wording determines downstream agent behavior).

**Implementation:**
Read `agent-core/skills/worktree/SKILL.md` Mode C (lines ~84-114) fully before editing.

Changes needed:
1. **Add step for exit code 3** — insert as new step 4, after the current step 3 (exit 0 success) and before the current step 4 (exit code 1). Move and adapt the conflict-handling content currently in the exit 1 section:
   - "**Parse merge exit code 3** (conflicts, merge paused). Read stdout for conflict report. The report contains: conflicted file list with conflict type, per-file diff stats, branch divergence summary, and a hint command. For each conflicted file: `Edit` to resolve conflict markers, `git add <file>`. When all conflicts resolved, re-run `claudeutils _worktree merge <slug>` (idempotent — resumes from current state, skips already-completed phases)."
   - This moves the "If conflicts detected" workflow from the current exit 1 section into the new exit 3 step. Preserve the existing 4-substep conflict workflow (Edit → git add → Re-run) — adapt, don't rewrite from scratch.

2. **Update step 4 (currently exit 1 handling)** — rename to step 5; remove the "If conflicts detected" sub-bullet (now in exit 3). What remains: precommit failure handling only.
   - Update heading: "**Parse merge exit code 1** (error: precommit failure or git error). Read stdout for error message."
   - Retain the precommit failure substeps (review failed checks, fix issues, git add, git commit --amend, just precommit, re-run merge). Remove the conflict sub-bullet entirely.

3. **Update step 5 (currently exit 2 handling)** — rename to step 6; no content change needed.

**Scope:** Mode C section only (`## Mode C:` heading through end of section or next `##` heading). Do NOT modify Mode A, Mode B, or Usage Notes beyond exit-code-related content.

**Expected Outcome:** Mode C accurately documents exit codes 0, 1, 2, 3. Agent reading the skill can correctly handle all merge outcomes.

**Error Conditions:**
- Exit code numbering conflict (e.g., if current Mode C has different step numbering) → renumber consistently, preserving content
- Content overlap between exit 1 conflict section and new exit 3 section → remove overlap from exit 1

**Validation:**
- Read `agent-core/skills/worktree/SKILL.md` Mode C after edit — verify:
  - Exit 3 section present with `claudeutils _worktree merge <slug>` re-run instruction
  - Exit 1 section no longer mentions "conflicts" (conflict-pause moved to exit 3)
  - Step numbering is consistent
- `just precommit` passes

---

**Phase 5 STOP conditions:**
- Step 5.1 finds a `SystemExit(3)` on a precommit failure path → STOP, wrong exit code (precommit = exit 1)
- Step 5.2 finds `err=True` outside merge scope → do NOT change; report to orchestrator
- Step 5.3 introduces wording that contradicts Phase 1–4 implementation (e.g., wrong exit codes, wrong command format) → STOP, verify against merge.py implementation
