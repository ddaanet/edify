# Deliverable Review: Prose & Configuration Artifacts

**Reviewer:** Opus
**Date:** 2026-02-13
**Scope:** SKILL.md, justfile recipes, agent-core justfile, execute-rule.md
**Reference:** `plans/worktree-update/design.md`

---

## SKILL.md (`agent-core/skills/worktree/SKILL.md`)

### Finding 1: Mode A uses single `new --task` call (PASS)

- **Axis:** Conformance
- **Severity:** n/a
- **Detail:** Step 2 invokes `claudeutils _worktree new --task "<task name>"` as a single call. Step 3 parses `<slug>\t<path>`. Matches design D7 (single call replaces 3 separate).

### Finding 2: Mode A marker format correct (PASS)

- **Axis:** Conformance
- **Severity:** n/a
- **Detail:** Step 4 shows `-> <slug>` marker (no `wt/` prefix). Matches design lines 231-235.

### Finding 3: Mode B uses `new --task` loop (PASS)

- **Axis:** Conformance
- **Severity:** n/a
- **Detail:** Step 4 iterates tasks calling `claudeutils _worktree new --task "<task name>"` per task. Sequential processing specified.

### Finding 4: Mode C references `merge` and `rm` commands (PASS)

- **Axis:** Conformance
- **Severity:** n/a
- **Detail:** Step 2 invokes `claudeutils _worktree merge <slug>`, step 3 invokes `claudeutils _worktree rm <slug>`.

### Finding 5: Frontmatter `allowed-tools` includes worktree CLI pattern (PASS)

- **Axis:** Conformance
- **Severity:** n/a
- **Detail:** Line 12: `Bash(claudeutils _worktree:*)` present. Matches design.

### Finding 6: Mode C step 2 says "three-phase merge" but implementation has four phases

- **File:** `agent-core/skills/worktree/SKILL.md:89`
- **Axis:** Functional correctness
- **Severity:** Minor
- **Detail:** Step 2 describes "the three-phase merge: submodule resolution, parent repo merge, and precommit validation." The actual Python implementation (`merge.py`) has four phases: (1) pre-checks/clean tree validation, (2) submodule resolution, (3) parent merge, (4) precommit. The skill omits Phase 1 (pre-checks) from the description. While the agent doesn't need to know internal phase numbering, "three-phase" is factually wrong. The merge has four phases; the description lists three by name.

### Finding 7: Mode C step 1 handoff prerequisite is cognitive/ambiguous

- **File:** `agent-core/skills/worktree/SKILL.md:87`
- **Axis:** Actionability
- **Severity:** Minor
- **Detail:** Step 1 says "invoke `/handoff --commit` to ensure clean tree and session context committed." The rationale is embedded inline ("merge operations require a clean working tree, and handoff ensures..."). This is explanatory prose, not a tool call. The actionable part is "invoke `/handoff --commit`" which is clear; the rest is rationale that could be trimmed for density. Not blocking but adds tokens without aiding execution.

### Finding 8: Mode B step 2 dependency analysis is highly cognitive

- **File:** `agent-core/skills/worktree/SKILL.md:50-61`
- **Axis:** Determinism
- **Severity:** Major
- **Detail:** Step 2 requires the agent to build a dependency map from four criteria (plan directory independence, logical dependencies, model tier compatibility, restart requirements). "Scan the Blockers/Gotchas section for mentions of other tasks" and "Check Pending Tasks section for explicit ordering hints" are judgment-heavy. Different agents will interpret "mentions" and "ordering hints" differently. The execute-rule.md `#status` already performs this same parallel group detection (lines 73-87). The skill duplicates this logic in prose without referencing the existing implementation pattern or providing a deterministic algorithm. The word "mentions" is especially problematic: does a task mentioning another task's plan directory count? Does referencing the same methodology document?

### Finding 9: Mode B parallel group detection duplicates #status logic

- **File:** `agent-core/skills/worktree/SKILL.md:50-61`
- **Axis:** Excess (duplication)
- **Severity:** Minor
- **Detail:** The `#status` command in execute-rule.md (lines 73-87) already detects parallelizable groups with the same four criteria. Mode B re-specifies the algorithm. This creates a maintenance risk: changes to parallel detection criteria must be synchronized across both locations. The skill could reference the #status output instead of reimplementing detection.

### Finding 10: Mode C precommit recovery path references `git commit --amend --no-edit`

- **File:** `agent-core/skills/worktree/SKILL.md:104`
- **Axis:** Functional correctness
- **Severity:** Minor
- **Detail:** Step 4 (precommit failure) instructs the agent to run `git commit --amend --no-edit`. This is correct for the described scenario (merge commit exists, precommit failed, fixes staged). However, the Python `merge` command exits 1 on precommit failure. Re-running `claudeutils _worktree merge <slug>` after amending would re-run Phase 1-4 from scratch. The skill says "Re-run: `claudeutils _worktree merge <slug>` to resume cleanup phase" (line 106) but the merge command isn't truly idempotent after a commit exists -- Phase 3 `git merge --no-commit --no-ff` would fail because there's nothing to merge. The agent should amend, verify precommit, then proceed to cleanup (step 3) directly, not re-run merge.

### Finding 11: Usage note claims merge "detects partial completion and resumes"

- **File:** `agent-core/skills/worktree/SKILL.md:119`
- **Axis:** Functional correctness
- **Severity:** Major
- **Detail:** Line 119 says "It detects partial completion and resumes from the appropriate phase." The actual `merge()` implementation in `merge.py` is a linear sequence: `_phase1 -> _phase2 -> _phase3 -> _phase4`. There is no state tracking, no phase detection, no resume logic. If merge is re-run after a conflict resolution + manual commit, Phase 1 re-validates clean trees (fine), Phase 2 re-checks submodule (fine, idempotent), Phase 3 attempts `git merge --no-commit --no-ff` which will say "Already up to date" if already merged (exit 0, fine). Phase 4 re-runs precommit (fine). So it IS practically idempotent for the conflict case. But for precommit failure after merge commit, Phase 3 would be a no-op and Phase 4 would re-run precommit. The "detects partial completion" claim overstates the mechanism -- it's incidental idempotency from git operations being individually idempotent, not explicit resume logic.

---

## Justfile Recipes

### Finding 12: `wt-ls` still calls `claudeutils _worktree ls` (design violation)

- **File:** `justfile:140-141`
- **Axis:** Conformance
- **Severity:** Critical
- **Detail:** Design D8 states "Justfile completely independent from Python CLI." Design line 261: "wt-ls: Replace `claudeutils _worktree ls` call with native bash `git worktree list` parsing (removes last CLI dependency)." The recipe still calls `@claudeutils _worktree ls`. This is the only remaining coupling between justfile and Python CLI.

### Finding 13: `wt-merge` lacks THEIRS clean tree check (design violation)

- **File:** `justfile:209-222`
- **Axis:** Conformance
- **Severity:** Critical
- **Detail:** Design D8 states: "THEIRS is strict (no session exemption -- uncommitted state would be lost). Both Python merge and justfile `wt-merge` must check both sides (justfile currently only checks OURS)." The justfile `wt-merge` only checks OURS (lines 210-222). It never checks the worktree side for dirty state. Compare with Python `merge.py:178` which correctly calls `_check_clean_for_merge(path=wt_path(slug), label="worktree")` in strict mode (no exemptions).

### Finding 14: `wt-merge` learnings.md resolution is simplified stub

- **File:** `justfile:283-288`
- **Axis:** Functional completeness
- **Severity:** Minor
- **Detail:** The justfile comment says "Simplified: just keep ours for now (full logic needs parsing)." The design spec (lines 154-158) requires appending theirs-only content. The Python implementation does this correctly. The justfile doesn't. Acceptable per D8 (recipes are independent fallback with acceptable duplication) but the "simplified" implementation drops theirs-only learnings, which contradicts the design intent.

### Finding 15: `wt-merge` commit may fail when nothing staged

- **File:** `justfile:311`
- **Axis:** Functional correctness
- **Severity:** Minor
- **Detail:** Line 311: `visible git commit -m "..."` runs unconditionally. If the merge was a fast-forward or all changes were already committed, `git commit` fails with "nothing to commit" and `set -e` kills the script. The Python implementation guards this (lines 262-268 check `git diff --cached --quiet`). The justfile should guard with `git diff --quiet --cached || visible git commit -m "..."`.

---

## Agent-Core Justfile

### Finding 16: Missing `setup` recipe (design violation)

- **File:** `agent-core/justfile`
- **Axis:** Conformance
- **Severity:** Critical
- **Detail:** Design D5 and line 89 state: "Prerequisite: add `setup` recipe to agent-core justfile." The design explicitly includes this in scope (line 348: "Agent-core setup: add `setup` recipe to `agent-core/justfile`"). The recipe does not exist. The Python CLI calls `just setup` in worktrees (cli.py:107-115), and the parent justfile's `wt-new` recipe checks for setup availability (line 111). Without a `setup` recipe in agent-core, new worktrees that only inherit the agent-core justfile will fail environment initialization silently.

---

## Execute-rule.md

### Finding 17: Marker format correct (PASS)

- **Axis:** Conformance
- **Detail:** Worktree Tasks section uses `-> <slug>` format (no `wt/` prefix). Status display shows `<slug>` only. All three locations (SKILL.md, execute-rule.md, handoff template) are consistent.

---

## Cross-Cutting Checks

### Path Consistency

- SKILL.md Mode A step 4: `-> <slug>` -- correct
- SKILL.md Mode B step 4: `-> <slug>` -- correct
- execute-rule.md Worktree Tasks: `-> <slug>` -- correct
- execute-rule.md status display: `<slug>` -- correct
- Handoff template (`agent-core/skills/handoff/references/template.md:26`): `-> <slug>` -- correct
- Historical plans (`plans/worktree-skill/`): still contain `-> wt/<slug>` -- acceptable (historical, not modified per session notes)

**Result:** Marker format is consistent across all operational files.

### Command Name Consistency

- SKILL.md invokes: `claudeutils _worktree new`, `merge`, `rm`
- CLI defines: `new`, `merge`, `rm`, `ls`, `clean-tree`, `add-commit`
- All SKILL.md invocations match CLI command names.

### Slug Format Consistency

- `derive_slug()` in Python: lowercase, replace non-alphanumeric with hyphens, strip leading/trailing hyphens, max 30 chars
- Justfile: slug is the recipe argument directly (no transformation)
- SKILL.md: delegates slug derivation to `new --task` (correct)

---

## Summary

| Severity | Count | Findings |
|----------|-------|----------|
| Critical | 3 | #12 (wt-ls CLI coupling), #13 (wt-merge no THEIRS check), #16 (missing setup recipe) |
| Major | 2 | #8 (Mode B cognitive dependency analysis), #11 (false idempotency claim) |
| Minor | 5 | #6 (three vs four phases), #7 (rationale density), #9 (duplication), #10 (amend recovery), #14 (learnings stub), #15 (unconditional commit) |
| Pass | 5 | #1, #2, #3, #4, #5, #17 |

### By Axis

| Axis | Findings |
|------|----------|
| Conformance | #12, #13, #16 (Critical); #1-5, #17 (Pass) |
| Functional correctness | #6, #10, #11, #15 |
| Functional completeness | #14 |
| Determinism | #8 |
| Actionability | #7 |
| Excess | #9 |

### Assessment

Three critical conformance gaps remain: the justfile `wt-ls` still depends on the Python CLI (violating D8), the justfile `wt-merge` lacks THEIRS clean tree validation (violating D8), and the agent-core justfile is missing the `setup` recipe (violating D5). These are design requirements explicitly marked as in-scope that were not implemented in the non-code artifact phase (Phase 8 per design implementation sequence).

The two major findings relate to SKILL.md correctness: the dependency analysis in Mode B is too cognitive for deterministic execution, and the idempotency claim overstates the merge command's resume capabilities.
