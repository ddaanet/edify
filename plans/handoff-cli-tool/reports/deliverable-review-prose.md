# Prose+Config Review: handoff-cli-tool (Round 2)

**Design reference:** `plans/handoff-cli-tool/outline.md`
**Date:** 2026-03-22

## Files Reviewed

| File | Type |
|------|------|
| `agent-core/skills/handoff/SKILL.md` | Agentic prose |
| `.claude/settings.local.json` | Configuration |

## Fix Verification

**C#1: FIXED.** `allowed-tools` changed from `Bash(wc:*)` to `Bash(just:*,wc:*,git:*)`. Step 7 (`just precommit`) now covered by `Bash(just:*)`. Step 1 (`git diff HEAD -- agents/session.md`) and line 93 (`git rev-parse --git-dir`) now covered by `Bash(git:*)`. The fix also resolves the pre-existing major finding from round 1 (missing `Bash(git diff:*)`).

## New Findings

### N-1. SKILL.md — Missing `Bash(claudeutils:*)` for command derivation

- **Location:** `agent-core/skills/handoff/SKILL.md:4` (allowed-tools) vs `:77` (instruction)
- **Axis:** Functional correctness
- **Severity:** Major

Line 77 instructs: "Run `Bash: claudeutils _worktree ls` to load current plan statuses." The allowed-tools `Bash(just:*,wc:*,git:*)` does not include `claudeutils`. The skill agent cannot execute this command.

Round 1 recommended adding `Bash(claudeutils _worktree ls)` alongside the `just precommit` fix. The `just` and `git` parts were addressed; `claudeutils` was not.

**Fix:** Change allowed-tools to `Bash(just:*,wc:*,git:*,claudeutils:*)` or add the specific pattern `Bash(claudeutils _worktree ls)`.

### settings.local.json — No findings

File contains `{}`. No plan-related configuration. Consistent with round 1 assessment (not a plan deliverable).

## Summary

| Category | Count | Details |
|----------|-------|---------|
| Fix verified | 1 | C#1 FIXED — `Bash(just:*,wc:*,git:*)` covers precommit gate and git commands |
| New findings | 1 | N-1 Major — `claudeutils _worktree ls` (line 77) blocked by allowed-tools (line 4) |
