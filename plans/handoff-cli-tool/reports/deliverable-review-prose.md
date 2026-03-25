# Prose & Configuration Review Findings

**Review round:** RC11 (full-scope, no delta-scoping per scoping-deliverable-review-iterations learning)
**Design reference:** `plans/handoff-cli-tool/outline.md`
**Methodology:** `agents/decisions/deliverable-review.md`

## Summary

Reviewed 4 files (+11/-8 lines): 2 agentic prose (design SKILL.md, handoff SKILL.md), 2 configuration (settings.local.json, .gitignore). Evaluated agentic prose against universal + actionability, constraint precision, determinism, scope boundaries axes. Evaluated configuration against universal axes only.

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

None.

## Per-File Assessment

### agent-core/skills/handoff/SKILL.md (Agentic prose, +6/-2)

Three changes across commits 52db16c..45f33d6:

**1. allowed-tools expansion (line 4):** `Bash(wc:*)` to `Bash(just:*,wc:*,git:*,claudeutils:*)`.
- **Conformance:** Each glob maps to a skill step: `just:*` for Step 7 precommit gate, `git:*` for Steps 1/2 diff/status checks, `claudeutils:*` for Step 2 `_worktree ls`. No excess grants beyond what steps require. No missing permissions.
- **Functional correctness:** Without `just:*`, Step 7 (`just precommit`) would fail at tool permission level. The grant is necessary.

**2. Fresh-write-resets-Completed rule (line 28):** Added bullet under Step 1 (Gather Context).
- **Actionability:** Concrete instruction: "contains only work from this conversation." Agent knows exactly what content belongs.
- **Scope boundaries:** Correctly scoped to fresh-write paths only; the incremental merge path (prior uncommitted handoff) is unaffected.
- **Conformance:** Aligns with outline H-2 "Overwrite" mode for first-handoff/committed state.

**3. Precommit Gate — Step 7 (lines 147-149):**
- **Conformance:** Outline line 375 requires: "Handoff skill must add `just precommit` as a pre-handoff gate (before calling `_handoff` CLI)." The gate is delivered. The outline specifies "before calling `_handoff` CLI" but the skill does not yet call `_handoff` CLI — Skill integration is explicitly future scope (outline line 379). In the current architecture where the skill performs writes itself, positioning after all mutation steps (2-6) and before display (Step 8) is the functionally equivalent location.
- **Constraint precision:** Specifies exact command (`just precommit`), exact failure behavior ("output the precommit result, STOP"), exact success behavior ("continue to STATUS display"). No agent judgment required.
- **Determinism:** Binary gate — precommit passes or fails. No interpretation needed.
- **Functional completeness:** Step renumbering correct (old Step 7 Display STATUS becomes Step 8).

### agent-core/skills/design/SKILL.md (Agentic prose, +3/-4)

Single change (commit d85e7e7): Simple routing loophole fix.

- **Conformance (scope):** Outline line 373 lists "Skill modifications (commit/status skills updated separately)" as OUT. This design SKILL.md change is a concurrent bugfix for the "competing execution paths" learning (learnings.md line 113), not a plan deliverable. It addresses a defect discovered during plan execution but is independent of the handoff-cli-tool scope. Reviewed because it was in the provided file set — no conformance concern since it does not conflict with plan scope.
- **Functional correctness:** Old routing offered steps 3 ("implement directly") and 4 ("chain to /inline") as competing paths. Agent would execute at step 3, bypassing corrector gates. New routing collapses to: recall (step 1), explore (step 2), chain to /inline (step 3). Explicit prohibition added: "Do NOT implement directly." Closes the documented loophole.
- **Actionability:** Three numbered steps, each with a concrete action. No ambiguity.
- **Determinism:** Simple classification maps to exactly one routing path with no conditional branching.
- **Excess:** None. The change is minimal — removes the competing permission and adds the prohibition. No unrelated content introduced.

### .claude/settings.local.json (Configuration, +1/-1)

- **Functional correctness:** Content remains `{}`. Change is trailing newline addition (POSIX compliance). No semantic change.
- **Vacuity:** Not vacuous — POSIX-compliant line endings prevent diff noise and tool warnings.

### .gitignore (Configuration, +1/-1)

- **Functional correctness:** `/.vscode/` changed to `/.vscode`. Removes trailing slash, broadening from directory-only match to file-or-directory match. Correctly handles the `.vscode` character device created by Claude Code sandboxing (not a directory, so `/.vscode/` pattern would not match it).
- **Excess:** None. Change is within plan execution scope (sandbox compatibility fix encountered during development).

## Notes

- The handoff SKILL.md precommit gate is well-positioned in the skill lifecycle. When the future `_handoff` CLI integration happens (outline line 379), the gate's position relative to the CLI call will need verification, but the current placement is correct for the current architecture.
- The design SKILL.md fix, while out of plan scope, is a genuine and well-executed bugfix grounded in a documented learning with evidence.
- All four changes are minimal and targeted. No scope creep detected.
