# Prose + Config Deliverable Review: handoff-cli-tool (RC9)

**Date:** 2026-03-24
**Design reference:** plans/handoff-cli-tool/outline.md
**Methodology:** Full-scope fresh review (no RC8 findings in this category).
**Scope:** Four files (2 agentic prose in submodule, 2 configuration in parent).

## Files Reviewed

| File | Type | Delta (vs main) |
|------|------|-----------------|
| agent-core/skills/handoff/SKILL.md | Agentic prose | +6/-2 (net +4) |
| agent-core/skills/design/SKILL.md | Agentic prose | +3/-14 (net -11) |
| .claude/settings.local.json | Configuration | no diff vs main |
| .gitignore | Configuration | no diff vs main |

**Note:** No commits touched any of these four files since RC8 review (0C/0M/0m). Full-scope review confirms RC8 findings hold.

## Agentic Prose Findings

### Critical
None

### Major
None

### Minor
None

## Configuration Findings

None. `.claude/settings.local.json` and `.gitignore` show no diff against main on this branch. The +1/-1 delta cited in the review request does not match current state — these files are unchanged.

## Per-File Assessment

### agent-core/skills/handoff/SKILL.md

**Key design requirement check (outline line 375):** "Handoff skill must add `just precommit` as a pre-handoff gate (before calling `_handoff` CLI)."

Step 7 (line 147-149) adds "Precommit Gate" — runs `just precommit` after all writes, before STATUS display. Positioned after mutation steps (2-6), before display (Step 8). Satisfies requirement.

**allowed-tools (line 4):** Expanded from `Bash(wc:*)` to `Bash(just:*,wc:*,git:*,claudeutils:*)`. Each glob corresponds to commands in the skill body: `just:*` for Step 7, `git:*` for Steps 1/2, `claudeutils:*` for Step 2. No missing permissions, no excess grants.

**Actionability:** Step 7 instruction is concrete — command to run, failure behavior (output + STOP), success behavior (continue). No ambiguity.

**Determinism:** Gate behavior is deterministic given project state.

**Scope boundaries:** Skill boundary unchanged. Steps 1-6 (gather + write), 7 (gate), 8 (display). Continuation section unmodified.

### agent-core/skills/design/SKILL.md

**Scope note:** Changes are outside plan's direct scope (outline line 373 OUT: "Skill modifications updated separately"). Included because provided in review file set. The change is a concurrent bugfix (commit d85e7e7: "Fix Simple routing loophole").

**Functional correctness:** Old Simple routing had steps 3-4 offering competing permissions ("implement directly" then "chain to /inline"). New routing removes step 3 execute, makes `/inline` the sole execution path with explicit prohibition. Closes the loophole documented in learnings ("When skill steps offer competing execution paths").

**Moderate routing:** Collapsed from 15-line multi-path block (prose path + non-prose path, each with code reading, generation, proof, routing) to 1-line routing. The `/proof` invocation for Moderate tasks is removed. This is consistent with the routing model where `/inline` and `/runbook` provide their own quality gates downstream. No orphaned references.

**Determinism:** Each classification maps to exactly one routing action. No ambiguity.

### .claude/settings.local.json

Content: `{}`. No plan-specified changes. Valid JSON.

### .gitignore

Standard project gitignore. No plan-specified changes.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 0 |

Four consecutive review rounds (RC6-RC9) with 0C/0M/0m for the prose+config layer. Handoff skill precommit gate satisfies the coupled skill update requirement. Design SKILL.md routing loophole fix is correct but out-of-plan-scope (concurrent bugfix).
