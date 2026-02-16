# Deliverable Review: SKILL.md Mode C (Track 3)

**Scope:** `agent-core/skills/worktree/SKILL.md` — Mode C update for FR-9 (rm exit 1 handling after successful merge)
**Date:** 2026-02-16
**Artifact type:** Agentic prose

## Findings

### 1. Mode C step 3 exit 1 escalation message differs from design

- **Location:** SKILL.md:97
- **Axis:** Conformance
- **Severity:** Minor

SKILL.md says: `"Merge may be incomplete -- branch {slug} has unmerged commits after merge reported success. Verify merge correctness before forcing removal."`

Design (design.md:162) says: `"Merge may be incomplete -- branch {slug} has unmerged commits after merge reported success."`

The SKILL.md adds "Verify merge correctness before forcing removal." which is not in the design spec. However, the addition is consistent with the design intent ("Do not retry rm or force-delete") and provides actionable guidance. The extra sentence is minor excess but arguably improves actionability.

### 2. Exit code mechanism: click.Abort vs SystemExit(1)

- **Location:** SKILL.md:94-99 (references rm exit codes)
- **Axis:** Functional correctness
- **Severity:** Minor (informational)

The SKILL.md correctly states rm exit 1 means guard refused. The implementation uses `click.Abort` (cli.py:339) rather than `raise SystemExit(1)`. Click translates `Abort` to exit code 1 and prints "Aborted!" to stderr. This is functionally equivalent for the skill's purposes — the exit code the skill checks is 1 in both cases. The skill does not reference the "Aborted!" message, so no mismatch.

### 3. Mode C step 3 "Handle rm exit 1" block position

- **Location:** SKILL.md:94-99
- **Axis:** Actionability
- **Severity:** Minor

The "Handle rm exit 1" block appears after the amend step (line 92) but logically must be checked before amending. The flow on line 92 is: rm succeeds → amend merge commit → output "Task complete." The exit 1 handling block follows as a separate paragraph. An agent reading sequentially would execute the amend before checking rm exit code.

However, the skill says "Check rm exit code" with explicit sub-bullets for exit 0 and exit 1, which implies the check happens immediately after rm. The amend is only described in the exit 0 success path context (line 92). The structure is: paragraph 1 describes the success path end-to-end, then paragraph 2 handles the failure path. This is a common skill pattern (happy path then error path), but the amend instruction on line 92 is before the exit code check instruction on line 94.

Rewriting to check exit code first, then branch into success (amend + output) vs failure (escalate) would be clearer.

### 4. Missing exit code 2 handling for rm

- **Location:** SKILL.md:94-99
- **Axis:** Functional completeness
- **Severity:** Major

FR-4 defines three exit codes: 0 (removed), 1 (refused), 2 (error). The "Handle rm exit 1" block in step 3 explicitly handles exit 0 and exit 1 but does not mention exit 2. If rm encounters an error (exit 2) during cleanup after successful merge, the skill provides no guidance.

The existing step 5 (exit code 2 handling) covers merge exit 2, not rm exit 2. An agent encountering rm exit 2 after successful merge has no instruction.

Design.md Track 3 only specifies handling for rm exit 1 (FR-9), so this is technically out of design scope. But from a completeness perspective, the skill now has explicit rm exit code branching that omits one valid code.

### 5. Mode A and Mode B: no mention of rm exit 1

- **Location:** SKILL.md:39-79 (Mode A and Mode B)
- **Axis:** Scope boundaries
- **Severity:** Minor (informational)

Mode A and Mode B do not invoke rm directly. Mode A outputs `cd <path> && claude` and Mode B outputs consolidated launch commands. Neither mode includes cleanup. Mode C is the only mode that calls rm (line 92). The rm exit code changes are correctly scoped to Mode C only.

### 6. Sandbox bypass annotation coverage

- **Location:** SKILL.md:125
- **Axis:** Functional completeness
- **Severity:** None (pass)

The Usage Notes section (line 125) correctly annotates all three mutation commands (`new`, `merge`, `rm`) as requiring `dangerouslyDisableSandbox: true`. This matches the session.md completed work ("Sandbox bypass annotations on all mutation commands").

### 7. "Do NOT retry rm" instruction

- **Location:** SKILL.md:99
- **Axis:** Constraint precision, Determinism
- **Severity:** None (pass)

"Do NOT retry rm with force flags or work around the refusal" is a clear, verifiable constraint. Matches design.md:164 ("Do not retry rm or force-delete").

### 8. Mode C step 3 amend includes session.md only

- **Location:** SKILL.md:92
- **Axis:** Functional correctness
- **Severity:** None (pass)

Line 92: `git add agents/session.md && git commit --amend --no-edit`. The amend targets session.md specifically, which is the file modified by `rm` (session task removal). Matches the session.md completed work ("rm session.md cleanup now amends merge commit").

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 1 |
| Minor | 3 |
| Pass | 3 |

**Major finding:** rm exit 2 not handled in Mode C step 3 exit code branching (#4). This is technically outside FR-9 scope (which only covers exit 1) but creates an incomplete exit code dispatch in the skill.

**Overall:** The SKILL.md Mode C update correctly implements FR-9. The escalation message, constraint against retrying, and sandbox annotations all conform to design. The exit 1 handling is accurate and actionable. The instruction ordering in step 3 could be clearer (check exit code before describing amend), and the rm exit 2 gap is the only substantive issue.
