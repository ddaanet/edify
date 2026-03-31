# Review: SP-2 /commit skill CLI composition

**Scope**: `plugin/skills/commit/SKILL.md` — Step 4 replacement, Step 1b simplification, Post-Commit replacement, allowed-tools update
**Date**: 2026-03-30
**Design reference**: `plans/skill-cli-integration/outline.md` D-2

## Summary

The skill correctly composes structured markdown input for `edify _commit` via heredoc (Step 4), replaces the Post-Commit section with `Status.` trigger convention (D-1), simplifies Step 1b to info-gathering only, and adds `Bash(edify _commit*)` to allowed-tools. The CLI input format (`## Files`, `## Options`, `## Submodule`, `## Message`) matches the parser at `src/edify/session/commit.py`.

Three composition boundary violations identified — all pre-existing or requiring CLI-side changes.

**Overall Assessment**: Ready (in-scope changes correct; Majors are pre-existing/CLI-gap)

## Issues Found

### Major Issues

**M-1: Double validation — skill runs precommit that D-2 assigns to CLI**
- Location: `SKILL.md:88-97` (Step 1)
- D-2 assigns validation gates to CLI. Step 1 runs `just precommit` pre-existing.
- **Status**: DEFERRED — Step 1 was not modified in this change. Pre-existing boundary violation. Track separately.

**M-2: `--test` flag has no CLI path — maps to `just-lint`**
- Location: `SKILL.md:167` (Step 4, `## Options` guidance)
- Flags section defines `--test` as "just test only." Options mapping says `--test` → `just-lint`. CLI's `_VALID_OPTIONS` has no `just-test`.
- Note: The `--test → just-lint` mapping was specified in the runbook given CLI limitations. Fix requires adding `just-test` to CLI.
- **Status**: DEFERRED — requires CLI-side change (`_VALID_OPTIONS` + pipeline path).

**M-3: Step 1c stages settings files directly — bypasses CLI staging**
- Location: `SKILL.md:129-131` (Step 1c, `git add`)
- D-2 assigns file staging to CLI. Step 1c's `git add` is pre-existing.
- **Status**: DEFERRED — Step 1c was not modified in this change. Pre-existing boundary violation.

### Minor Issues

**m-1: Allowlist constraint references orphaned `git commit`**
- Location: `SKILL.md:62`
- Text: "Do NOT chain commands (`git add && git commit`)" — `git commit` is no longer a skill operation.
- **Status**: FIXED — updated to reference current operations.

**m-2: `Bash(git add:*)` unused if M-3 fixed**
- **Status**: DEFERRED — conditional on M-3.

**m-3: `Bash(just precommit)` etc. unnecessary if M-1 fixed**
- **Status**: DEFERRED — conditional on M-1.

**m-4: Step 1 heading says "Pre-commit validation + discovery"**
- **Status**: DEFERRED — conditional on M-1.

## Requirements Validation

| Requirement (D-2) | Status | Evidence |
|-------------------|--------|----------|
| Skill keeps: discovery, vet classification, message drafting, gitmoji, settings triage, context-mode | Satisfied | Steps 1-3 preserved |
| CLI owns: File staging, validation, submodule commit, parent commit | Satisfied (new work) | Step 4 delegates to `edify _commit` |
| Composition: structured markdown → heredoc → CLI | Satisfied | SKILL.md:148-162 |
| CLI input format matches parser | Satisfied | `## Files`, `## Options`, `## Submodule`, `## Message` |
| Post-commit: `Status.` trigger | Satisfied | SKILL.md:175-183 |
| allowed-tools updated | Satisfied | `Bash(edify _commit*)` added |
| Pre-existing boundary violations (M-1, M-3) | DEFERRED | Not in change scope |
| `--test` CLI option gap (M-2) | DEFERRED | Requires CLI-side work |
