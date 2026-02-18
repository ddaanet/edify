## Phase 5: Exit code threading + skill update + stdout unification (type: general)

**Goal:** Three independent, non-behavioral changes: (1) audit all `SystemExit` calls in `merge.py` and reclassify conflict-pause exits as exit 3, (2) migrate all `click.echo(..., err=True)` to stdout, (3) update SKILL.md Mode C with exit 3 handling.

**Files:** `src/claudeutils/worktree/merge.py`, `src/claudeutils/worktree/cli.py` (merge handler), `agent-core/skills/worktree/SKILL.md`

**Depends on:** Phases 1–4 (all exit code semantics stable before this step).

**Prose atomicity:** All SKILL.md changes in Step 5.3 only. Do not split across steps.
**Self-modification ordering:** This phase is last — implementation complete before documentation.

---

## Step 5.1: Audit exit codes — reclassify conflict-pause exits to SystemExit(3)

**Objective:** Ensure every `raise SystemExit` in `merge.py` uses the correct code from D-1 semantics: exit 0 = success, exit 1 = error (recoverable, not a merge state issue), exit 2 = fatal (branch missing, merge state corrupt), exit 3 = conflicts need resolution (merge paused).

**Script Evaluation:** Prose — medium scope (read full merge.py, classify each exit, make targeted edits).

**Execution Model:** Sonnet (code audit + judgment on error vs conflict classification).

**Implementation:**
1. Read full `src/claudeutils/worktree/merge.py` (current state after Phases 1-4)
2. List every `raise SystemExit(N)` with line number and context
3. For each: classify as error (1), fatal (2), or conflict-pause (3) per D-1:
   - `SystemExit(3)`: any path where MERGE_HEAD is preserved and agent needs to resolve conflicts
   - `SystemExit(1)`: precommit failure, git command error, unrecognized merge failure (non-conflict)
   - `SystemExit(2)`: branch not found, merge state corrupt (`slug not fully merged`, `nothing to commit and branch not merged`)
4. Update any misclassified exits (Phases 1-4 may have used `SystemExit(1)` for conflict-pause paths)
5. Verify: `grep -n "SystemExit" src/claudeutils/worktree/merge.py` — review each occurrence for correctness

**Expected Outcome:** All conflict-pause exits use `SystemExit(3)`. No exit 1 on paths where MERGE_HEAD is preserved. No exit 3 on precommit failure or git error paths.

**Error Conditions:**
- If a path is ambiguous (could be error or conflict-pause): classify as exit 1 and add inline comment explaining the distinction
- If audit finds unexpected paths: STOP and report

**Validation:**
- `grep -n "SystemExit" src/claudeutils/worktree/merge.py` — manually verify each entry
- `just precommit` passes

---

## Step 5.2: Migrate all `click.echo(..., err=True)` to stdout (D-8, C-2)

**Objective:** All merge-related output goes to stdout. Exit code carries the semantic signal. Eliminates need for `2>&1` at call sites.

**Script Evaluation:** Haiku — mechanical substitution.

**Execution Model:** Haiku (mechanical substitution, enumerate call sites with grep).

**Implementation:**
1. Run: `grep -n "err=True" src/claudeutils/worktree/merge.py src/claudeutils/worktree/cli.py`
2. For each match: remove the `err=True` keyword argument (leave all other arguments intact)
3. Verify no `err=True` remains: `grep -n "err=True" src/claudeutils/worktree/merge.py src/claudeutils/worktree/cli.py` returns no matches

**Scope boundary:** Only `merge.py` and `cli.py` merge handler. Do NOT modify other CLI commands or non-merge output.

**Expected Outcome:** Zero `err=True` occurrences in merge.py and cli.py merge handler. All output visible via stdout only.

**Error Conditions:**
- `err=True` in a non-merge context (e.g., `new.py`, `rm.py`) — do NOT change those; scope is merge only
- Multiple `err=True` on same line → remove argument, preserve other arguments

**Validation:**
- `grep -n "err=True" src/claudeutils/worktree/merge.py src/claudeutils/worktree/cli.py` — zero matches
- `just precommit` passes

---

## Step 5.3: Update SKILL.md Mode C — add exit code 3 handling (C-1, prose atomicity)

**Objective:** Document exit code 3 semantics and resolution workflow in SKILL.md Mode C. Update existing exit 1 handling to distinguish precommit failure from conflict-pause. All SKILL.md changes in this single step.

**Script Evaluation:** Prose — targeted edits to existing Mode C section.

**Execution Model:** Opus (prose artifact, LLM-consumed — wording determines downstream agent behavior).

**Implementation:**
Read `agent-core/skills/worktree/SKILL.md` Mode C (lines ~84-114) fully before editing.

Changes needed:
1. **Add step for exit code 3** — insert after the current step 3 (exit 0 success) and before step 4 (exit code 1). New step:
   - "**Parse merge exit code 3** (conflicts, merge paused). Read stdout for conflict report. The report contains: conflicted file list with conflict type, per-file diff stats, branch divergence summary, and a hint command. For each conflicted file: `Edit` to resolve conflict markers, `git add <file>`. When all conflicts resolved, re-run `claudeutils _worktree merge <slug>` (idempotent — resumes from current state, skips already-completed phases)."

2. **Update step 4 (currently exit 1 handling)** — rename to step 5; clarify that exit 1 now means only errors (precommit failure, git command error), NOT conflict-pause (which is now exit 3):
   - Update step 4 → step 5: "**Parse merge exit code 1** (error: precommit failure or git error). Read stdout for error message. ..."
   - Remove the "If conflicts detected" sub-bullet from the old exit 1 section — conflicts are now exit 3 only.

3. **Update step 5 (currently exit 2 handling)** — rename to step 6; no content change needed.

4. **Update Usage Notes** — the "Merge is idempotent" note (line ~122) is already accurate; verify it references the updated state machine.

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
