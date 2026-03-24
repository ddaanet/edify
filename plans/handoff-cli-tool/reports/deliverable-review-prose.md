# Prose+Config Review: handoff-cli-tool (RC7 Layer 1)

**Date:** 2026-03-24
**Design reference:** plans/handoff-cli-tool/outline.md
**Scope:** Full-scope review. Four files (2 agentic prose, 2 configuration).
**Prior review:** RC6 prose review (0C/0M/0m).

## Files Reviewed

| File | Type | Delta (vs merge-base) |
|------|------|----------------------|
| agent-core/skills/handoff/SKILL.md | Agentic prose | +6/-2 (net +4) |
| agent-core/skills/design/SKILL.md | Agentic prose | +3/-4 (net -1) |
| .claude/settings.local.json | Configuration | +1/-1 (trailing newline) |
| .gitignore | Configuration | +1/-1 (/.vscode/ to /.vscode) |

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

None.

## RC6 Finding Verification

RC6 prose layer had 0C/0M/0m. Nothing to verify.

## Per-File Assessment

### agent-core/skills/handoff/SKILL.md

**Changes (4 commits: 52db16c..45f33d6):**
1. Fresh-write-resets-Completed rule added to Step 1 (52db16c)
2. Step 7 Precommit Gate inserted; old Step 7 renumbered to Step 8 (392e463)
3. `allowed-tools` expanded: `Bash(wc:*)` to `Bash(just:*,wc:*,git:*)` (4226b23)
4. `allowed-tools` expanded further: added `claudeutils:*` (45f33d6)

**Conformance:** Outline Scope (line 374-375): "Handoff skill must add `just precommit` as a pre-handoff gate (before calling `_handoff` CLI). Delivered with the CLI." Step 7 runs `just precommit` after all file-mutation steps (2-6) and before STATUS display. Requirement satisfied.

**Actionability:** "Run `just precommit` after all writes ... On failure: output the precommit result, STOP" — directly executable with unambiguous stop/continue behavior.

**Constraint precision:** Gate covers all mutation steps. No bypass path exists between Steps 2-6 and Step 8.

**Scope boundaries:** All `allowed-tools` additions correspond to commands used within the skill body: `just:*` for Step 7, `git:*` for Step 1, `claudeutils:*` for Step 2.

### agent-core/skills/design/SKILL.md

**Changes (1 commit: d85e7e7):** Simple routing restructured — removed step 3 "Execute: implement directly," collapsed step numbering, added "Do NOT implement directly" prohibition.

**Conformance:** Outside this plan's direct scope. Outline Scope OUT: "Skill modifications (commit/status skills updated separately)." The coupled skill update names only the handoff skill. This change addresses the "When skill steps offer competing execution paths" learning. Correctly attributed to that fix, not this plan.

**Functional correctness (observation):** Old routing had steps 3-4 offering competing execution permissions. New routing makes `/inline` the sole execution path (3 steps: Recall, Explore, Continuation). Loophole closed.

**Determinism:** Same classification → same path. No ambiguity in step sequencing.

### .claude/settings.local.json

Content: `{}` with trailing newline. Merge-base lacked POSIX trailing newline. Valid JSON. No semantic change.

### .gitignore

`/.vscode/` changed to `/.vscode`. Both patterns ignore the `.vscode` directory at project root. Standard normalization. No functional impact.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 0 |

Handoff skill precommit gate satisfies the outline's coupled skill update requirement. Design SKILL.md change is outside plan scope (observation only). Configuration files are formatting-only changes. Two consecutive review rounds (RC6, RC7) with 0C/0M/0m for the prose+config layer.
