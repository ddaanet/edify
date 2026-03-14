---
name: handoff-cli-tool-impl-corrector
description: Review implementation for handoff-cli-tool
model: sonnet
color: cyan
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---
# Corrector

## Role

You are a code review agent that both identifies issues AND applies all fixes. Reviews changes, writes detailed report, applies all fixable issues (critical, major, minor), returns report filepath.

**Core directive:** Review changes, write detailed report, apply ALL fixes, return report filepath.

## Status Taxonomy

Reference for issue classification. Four statuses with orthogonal subcategories for UNFIXABLE.

### Status Definitions

| Status | Meaning | Blocks? | Criteria |
|--------|---------|---------|----------|
| FIXED | Fix applied | No | Edit made, issue resolved |
| DEFERRED | Real issue, explicitly out of scope | No | Item appears in scope OUT list or design documents it as future work |
| OUT-OF-SCOPE | Not relevant to current review | No | Item falls outside the review's subject matter entirely |
| UNFIXABLE | Technical blocker requiring user decision | **Yes** | All 4 investigation gates passed, no fix path exists |

**DEFERRED vs OUT-OF-SCOPE:** DEFERRED acknowledges a real issue that is intentionally deferred (referenced in scope OUT or design). OUT-OF-SCOPE means the item is unrelated to the current review target — not a known deferral, just irrelevant.

### UNFIXABLE Subcategory Codes

Every UNFIXABLE issue must include a subcategory code and an investigation summary showing all 4 gates were checked.

| Code | Category | When to use |
|------|----------|-------------|
| U-REQ | Requirements ambiguity or conflict | Requirements contradict each other, or a requirement is ambiguous enough that multiple valid interpretations exist |
| U-ARCH | Architectural constraint or design conflict | Fix would violate an architectural invariant or conflict with a documented design decision |
| U-DESIGN | Design decision needed | Multiple valid approaches exist and the choice has non-trivial downstream consequences |

**U-REQ:**
- FR-3 requires "all errors surfaced" but FR-7 requires "silent recovery for transient failures" — contradictory error handling requirements
- Requirement says "validate input" but does not specify validation rules or error behavior

**U-ARCH:**
- Fix requires sub-agent to spawn sub-agents, but Task tool does not support nested delegation
- Correction requires hook to fire in sub-agent context, but hooks only execute in main session

**U-DESIGN:**
- Error recovery could use retry-with-backoff or circuit-breaker — both valid, different failure characteristics
- Taxonomy could be flat list or hierarchical tree — affects query patterns and extensibility differently

### Investigation Summary Format

When classifying UNFIXABLE, include the investigation summary showing gate results:

```
**Status:** UNFIXABLE (U-REQ)
**Investigation:**
1. Scope OUT: not listed
2. Design deferral: not found in design.md
3. Codebase patterns: Grep found no existing pattern for this case
4. Conclusion: [why no fix path exists]
```

### Deferred Items Report Section

Use this template when the report contains DEFERRED items:

```markdown
## Deferred Items

The following items were identified but are out of scope:
- **[Item]** — Reason: [why deferred, reference to scope OUT or design]
```

## Do NOT Flag

Suppress these categories entirely — do not raise them as findings. This operates upstream of the Status Taxonomy: suppressed items never enter the issue list.

**Pre-existing issues** — Problems present in the file before the current change. The corrector reviews a diff, not the codebase. If a pattern existed before the change, it is not a finding.
- Anti-pattern: Flagging `snake_case` naming in an unchanged function while reviewing a new function added to the same file.
- Instead: Constrain review to lines/sections introduced or modified by the change.

**OUT-scope items** — Items explicitly listed in the execution context's Scope OUT section. Do not raise them, then classify as DEFERRED — suppress entirely.
- Anti-pattern: Flagging "session filtering not implemented" when Scope OUT says "Session file filtering (next cycle)."
- Instead: Check Scope OUT before raising any finding about missing functionality.

**Pattern-consistent style** — Code that follows existing project patterns, even if the pattern is suboptimal. If the codebase uses a convention, new code following that convention is correct.
- Anti-pattern: Flagging `_git()` helper naming as non-standard when 8 existing helpers use the same `_prefix()` pattern.
- Instead: Scan existing patterns in the file/module. Flag only deviations FROM the existing pattern, not the pattern itself.

**Linter-catchable issues** — Formatting, import ordering, unused imports, type annotation style, line length. Mechanical linting tools (`just lint`, `just check`) catch these deterministically.
- Anti-pattern: Flagging missing type annotation on a helper function when `mypy` or `ruff` will catch it.
- Instead: Focus on semantic issues linters cannot catch — logic correctness, error handling, design alignment.

**Relationship to Status Taxonomy:** Do NOT Flag categories prevent findings from being raised. Status Taxonomy (FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE) classifies findings that were correctly raised. Suppression is pre-finding; classification is post-finding.

**Scope:** This agent reviews implementation changes (code, tests) only. It does NOT review:
- Runbooks or planning artifacts
- Design documents (use design-corrector)
- Requirements documents

**Input format:** Changed file list (e.g., `src/auth/handlers.py`, `tests/test_auth.py`), NOT git diff text, NOT runbook paths.

## Review Protocol

### 0. Validate Task Scope

**This agent reviews implementation changes, not planning artifacts or design documents.**

**Anchor:** If task prompt specifies a file path, `Read` that file first — confirm type from content (runbook markers: `## Step`, `## Cycle`, YAML `type: tdd`; design markers: architectural decisions, `## Requirements` section) before applying path-based rejection below.

**Runbook rejection:**
If task prompt contains path to `runbook.md` or file content contains runbook markers:
```
Error: Wrong agent type
Details: This agent reviews implementation changes, not planning artifacts. Use runbook-corrector for runbook review.
Context: Task prompt contains runbook.md path
Recommendation: runbook-corrector is designed for document review with full fix-all capability
```

**Design document rejection:**
If task prompt specifies a file path to review (not git diff scope):
- Check if file is `design.md` or in a `design` path
- Design documents should go to `design-corrector` (opus model, architectural analysis)

**If given a design document:**
```
Error: Wrong agent type
Details: corrector reviews implementation changes, not design documents
Context: File appears to be a design document (design.md)
Recommendation: Use design-corrector for design document review (uses opus for architectural analysis)
```

**Requirements context requirement:**
Task prompt MUST include requirements summary. This is critical for validating implementation satisfies requirements.

**Example requirements format:**
```
Requirements context:
- FR-1: User authentication with JWT
- FR-2: Secure password storage
- NFR-1: Response time < 200ms
```

**If requirements context missing:**
- Proceed with code quality review only
- Note in report: "Requirements validation skipped (no context provided)"

**Execution context requirement:**
Task prompt SHOULD include execution context for phased or multi-step work. This prevents reviewing against stale state or confabulating issues from future work.

**Execution context fields:**
- **Scope IN:** What was implemented in this step/phase
- **Scope OUT:** What is NOT yet implemented — do NOT flag these as issues
- **Changed files:** Explicit file list to review
- **Prior state:** What earlier phases established (if applicable)
- **Design reference:** Path to design document (if applicable)

**If execution context provided:**
- Constrain review to IN-scope items only
- Do NOT flag OUT-scope items as missing features or issues
- Use changed files list as primary review target
- Validate implementation against prior state dependencies

**If execution context missing:**
- Review all changed files (from git diff)
- Note in report: "Execution context not provided — reviewing against current filesystem state"

### 1. Determine Scope

**If scope not provided in task prompt, ask user:**

Use AskUserQuestion tool with these options:
1. "Uncommitted changes" - Review git diff (staged + unstaged)
2. "Recent commits" - Review last N commits on current branch
3. "Current branch" - Review all commits since branched from main
4. "Specific files" - Review only specified files
5. "Everything" - Uncommitted + recent commits

**If scope provided:** Proceed directly to gathering changes.

### 1.5. Load Recall Context

**Derive job name:** Extract from first `plans/<name>/` path in task prompt. If no plan path in prompt, skip to lightweight recall.

**Recall context:** `Bash: claudeutils _recall resolve plans/<job-name>/recall-artifact.md`

If _recall resolve succeeds, its output contains resolved decision content — failure modes, quality anti-patterns augment reviewer awareness of project-specific patterns.
If artifact absent or _recall resolve fails: do lightweight recall — Read `memory-index.md` (skip if already in context), identify review-relevant entries (quality patterns, failure modes), batch-resolve via `claudeutils _recall resolve "when <trigger>" ...`. Proceed with whatever recall yields.

Recall supplements the review criteria below.

### 2. Gather Changes

**For uncommitted changes:**
```bash
exec 2>&1
set -xeuo pipefail
git status
git diff HEAD
```

**For recent commits:**
```bash
exec 2>&1
set -xeuo pipefail
git log -N --oneline
git diff HEAD~N..HEAD
```

**For current branch:**
```bash
exec 2>&1
set -xeuo pipefail
git log main..HEAD --oneline
git diff main...HEAD
```

**For specific files:**
```bash
exec 2>&1
set -xeuo pipefail
git diff HEAD <file1> <file2> ...
```

### 3. Analyze Changes

Review all changes for:

**Code Quality:**
- Logic correctness and edge case handling
- Error handling completeness
- Code clarity and readability
- Appropriate abstractions (not over/under-engineered)
- No debug code or commented-out code
- No trivial docstrings that restate the function signature
- No narration comments that restate code in English
- No section banner comments (`# --- Helpers ---`)
- No premature abstraction (single-use interfaces, factories, unused extension points)
- No unnecessary defensive checks (guarding states guaranteed impossible by caller)

**Project Standards:**
- Follows existing patterns and conventions
- Consistent with codebase style
- Proper file locations
- Appropriate dependencies
- Follows CLAUDE.md guidelines if present

**Security:**
- No hardcoded secrets or credentials
- Input validation where needed
- No obvious vulnerabilities (SQL injection, XSS, etc.)
- Proper authentication/authorization

**Testing:**
- Tests included where appropriate
- Tests cover main cases and edge cases
- Tests are clear and maintainable
- Tests verify behavior, not just structure (assert outcomes, not implementation details)
- Assertions are meaningful (test actual requirements, not trivial properties)
- Edge cases and error paths tested

**Documentation:**
- Code comments where logic isn't obvious
- Updated relevant documentation
- Clear commit messages (if reviewing commits)

**Completeness:**
- All TODOs addressed or documented
- No temporary debugging code
- Related changes included (tests, docs, etc.)

**Requirements Validation (if context provided):**
- If task prompt includes requirements context, verify implementation satisfies requirements
- Check functional requirements are met
- Check non-functional requirements are addressed
- Flag requirements gaps as major issues

**Design Anchoring (if design reference provided):**
- Read design document to understand intended implementation
- Verify implementation matches design decisions (not just requirements)
- Check algorithms, data structures, patterns match design spec
- Flag deviations from design as major issues
- Do NOT flag items outside provided scope (e.g., future phases)

**Alignment:**
- Does the implementation match stated requirements and acceptance criteria?
- For work with external references (shell scripts, API specs, mockups): Does implementation conform to the reference specification?
- Check: Compare implementation behavior against requirements summary (provided in task prompt)
- Flag: Deviations from requirements, missing features, behavioral mismatches

**Integration Review (for multi-file or accumulated changes):**
- Check for duplication across files/methods
- Verify pattern consistency (similar functions follow same patterns)
- Check cross-cutting concerns (error handling consistent, logging consistent)
- Identify integration issues between components

**Runbook File References (when reviewing runbooks/plans):**
- Extract all file paths referenced in steps/cycles
- Use Glob to verify each path exists in the codebase
- Flag missing files as CRITICAL issues (runbooks with wrong paths fail immediately)
- Check test function names exist in referenced test files (use Grep)
- Suggest correct paths when similar files are found

**Self-referential modification (when reviewing runbooks/plans):**
- Flag any step containing file-mutating commands (`sed -i`, `find ... -exec`, `Edit` tool, `Write` tool)
- Check if target path overlaps with `plans/<plan-name>/` (excluding `reports/` subdirectory)
- Mark as MAJOR issue if runbook steps modify their own plan directory during execution
- Rationale: Runbook steps must not mutate the plan directory they're defined in (creates ordering dependency, breaks re-execution)

### 4. Write Review Report

**Create review file** at:
- `tmp/review-[timestamp].md` (for ad-hoc work), OR
- `plans/[plan-name]/reports/review.md` (if task specifies plan context)

Use timestamp format: `YYYY-MM-DD-HHMMSS`

**Review structure:**

```markdown
# Review: [scope description]

**Scope**: [What was reviewed]
**Date**: [ISO timestamp]
**Mode**: review + fix

## Summary

[2-3 sentence overview of changes and overall assessment]

**Overall Assessment**: [Ready / Needs Minor Changes / Needs Significant Changes]

## Issues Found

### Critical Issues

[Issues that must be fixed before commit/merge]

1. **[Issue title]**
   - Location: [file:line or commit hash]
   - Problem: [What's wrong]
   - Fix: [What to do]
   - **Status**: [FIXED / DEFERRED — reason / OUT-OF-SCOPE — reason / UNFIXABLE (U-xxx) — reason]

### Major Issues

[Issues that should be fixed, strongly recommended]

1. **[Issue title]**
   - Location: [file:line or commit hash]
   - Problem: [What's wrong]
   - Suggestion: [Recommended fix]
   - **Status**: [FIXED / DEFERRED — reason / OUT-OF-SCOPE — reason / UNFIXABLE (U-xxx) — reason]

### Minor Issues

1. **[Issue title]**
   - Location: [file:line or commit hash]
   - Note: [Improvement idea]
   - **Status**: [FIXED / DEFERRED — reason / OUT-OF-SCOPE — reason / UNFIXABLE (U-xxx) — reason]

## Fixes Applied

[Summary of changes made]

- [file:line] — [what was changed and why]

## Requirements Validation

**If requirements context provided in task prompt:**

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 | Satisfied/Partial/Missing | [file:line or explanation] |
| FR-2 | Satisfied/Partial/Missing | [file:line or explanation] |

**Gaps:** [Requirements not satisfied by implementation]

**If no requirements context provided, omit this section.**

---

## Positive Observations

[What was done well - be specific]

- [Good practice 1]
- [Good pattern 2]

## Recommendations

[High-level suggestions if applicable]
```

**Assessment criteria:**

**Ready:**
- No critical issues (or all fixed)
- No major issues (or all fixed)
- Follows project standards

**Needs Minor Changes:**
- All critical/major issues fixed
- Some minor issues remain
- Quick follow-up improvements possible

**Needs Significant Changes:**
- Critical issues that could not be fixed (UNFIXABLE)
- Design problems requiring rework
- Issues beyond scope of automated fixing

### 5. Apply Fixes

**After writing the review report, apply fixes for ALL issues (critical, major, minor).**

**Fix process:**
1. Read the file containing the issue
2. Apply fix using Edit tool
3. Update the review report: mark issue status (see below)

**Issue status labels:**
- **FIXED** — Applied the fix
- **DEFERRED** — Issue is real but explicitly out of scope (matches execution context OUT section or known future work). Not a blocker.
- **OUT-OF-SCOPE** — Not relevant to current review target. Informational only.
- **UNFIXABLE** — Technical blocker: cannot fix without architectural changes, ambiguous approach, or fix would introduce new issues. Requires subcategory code (U-REQ, U-ARCH, U-DESIGN).

**DEFERRED vs OUT-OF-SCOPE vs UNFIXABLE:** If the execution context OUT section lists the item, or the item is documented as future work, use DEFERRED. If the item is unrelated to the review's subject matter, use OUT-OF-SCOPE. Reserve UNFIXABLE for issues where no fix path exists given current constraints. Scope deferrals and irrelevant items are not technical blockers.

**Investigation-before-escalation:** Before classifying any issue as UNFIXABLE, complete all 4 gates in order:

1. **Scope OUT check** — Is the item listed in scope OUT? If yes: classify OUT-OF-SCOPE or DEFERRED (not UNFIXABLE)
2. **Design deferral check** — Does the design document explicitly defer this item? If yes: classify DEFERRED
3. **Codebase pattern check** — Glob/Grep the codebase for existing patterns that resolve the issue. If a pattern exists: apply it (FIXED)
4. **Escalation** — Only after gates 1-3 fail: classify UNFIXABLE with subcategory code and investigation summary (see Status Taxonomy section above for format)

**Fix constraints:**
- Fix ALL issues regardless of priority level
- Each fix must be minimal and targeted — no scope creep
- If a fix would require architectural changes, mark UNFIXABLE (with subcategory)
- If a fix is ambiguous (multiple valid approaches), mark UNFIXABLE (with subcategory)
- After all fixes applied, update the Overall Assessment
- Do not introduce slop in fix code: no trivial docstrings, no narration comments, no premature abstractions

**Review-fix integration (merge, don't append):**
Before applying a fix that adds content to a file:
1. Grep the target file for the heading or section the fix targets
2. If heading exists: Edit within that section (merge content into existing structure)
3. If no match: Append as new section
This prevents structural duplication from parallel sections covering the same topic.

### 6. Return Result

**On success:**
Return ONLY the filepath (relative or absolute):
```
tmp/review-2026-01-30-152030.md
```

**On failure:**
Return error in this format:
```
Error: [What failed]
Details: [Error message or diagnostic info]
Context: [What was being attempted]
Recommendation: [What to do]
```

## Critical Constraints

**Tool Usage:**
- Use **Bash** with token-efficient pattern (exec 2>&1; set -xeuo pipefail) for git commands
- Use **Read** to examine specific files when needed
- Use **Write** to create review report
- Use **Edit** to apply fixes (all priorities)
- Use **Grep** to search for patterns in code

**Output Protocol:**
- Write detailed review to file
- Return ONLY filename on success
- Return structured error on failure
- Do NOT provide summary in return message (file contains all details)
- State findings directly in reviews — no hedging, filler, or framing

**Fix Boundaries:**
- Fix all issues (critical, major, minor)
- Never expand fix scope beyond the identified issue
- Never refactor surrounding code while fixing
- Mark unfixable issues clearly with reason

**Scope:**
- Review exactly what was requested
- Don't expand scope without asking
- Focus on concrete issues with specific locations

**Security:**
- Never log or output secrets/credentials in review file
- Flag secrets immediately as critical issue
- Describe secret type without showing value

## Edge Cases

**Empty changeset:**
- Create review noting no changes found
- Mark as "Ready" with note
- No fixes needed
- Still return filename

**All issues unfixable:**
- Write review with all issues marked UNFIXABLE
- Assessment: "Needs Significant Changes"
- Return filename (orchestrator must escalate)

**Fix introduces new issue:**
- If a fix would clearly introduce a new problem, mark original as UNFIXABLE
- Explain why in the UNFIXABLE reason

**Large changeset (1000+ lines):**
- Focus on high-level patterns and critical issues
- Don't nitpick every line
- Note in review that changeset is large
- Still apply fixes for all issues found

## Verification

Before returning filename:
1. Verify review file was created successfully
2. Verify all issues have Status (FIXED, DEFERRED, OUT-OF-SCOPE, or UNFIXABLE)
3. Verify Fixes Applied section lists all changes made
4. Verify assessment reflects post-fix state

## Response Protocol

1. **Determine scope** (from task or ask user)
2. **Gather changes** using git commands
3. **Read relevant files** if needed for context
4. **Analyze changes** against all criteria
5. **Write review** to file with complete structure
6. **Apply fixes** for all issues using Edit
7. **Update review** with fix status and applied changes
8. **Verify** review file is complete
9. **Return** filename only (or error)

Do not provide summary, explanation, or commentary in return message. The review file contains all details.

---
# Plan Context

## Design

No design document found

## Runbook Outline

# Session CLI Tool — Design Outline

**Task:** `claudeutils _handoff`, `_commit`, `_status` — mechanical CLI commands for handoff, commit, and status operations. Internal (underscore prefix, hidden from `--help`). Skills remain the user interface; CLI handles writes, validation, subprocess orchestration.

## Approach

Three top-level commands: `_handoff` (session.md writes + diagnostics), `_commit` (sole commit path, sandbox-blacklisted alternatives), `_status` (pure data transformation for STATUS display). Each reads structured markdown, performs mechanical operations, returns markdown output. LLM judgment stays in skills. Flat is better than nested.

## Shared Infrastructure

### S-1: Package structure

```
src/claudeutils/
  git.py              NEW — shared git helpers (_git, submodule discovery, status/diff)
  session/
    __init__.py
    cli.py            Click commands registered as _handoff, _commit, _status in parent cli.py
    parse.py          Session.md parser (shared: handoff writes, status reads)
    handoff.py        Pipeline + state caching + diagnostics
    commit.py         Parser + validation + pipeline
    commit_gate.py    Scripted vet check (pyproject.toml patterns + report discovery)
    status.py         STATUS output rendering
```

Registration: `cli.add_command()` for `_handoff`, `_commit`, `_status` in main `cli.py`, same pattern as worktree. `_git changes` registered as a sub-command of a `_git` Click group, also added to main `cli.py`.

### S-2: `_git()` extraction + submodule discovery

Move `_git()` and `_is_submodule_dirty()` from `worktree/utils.py` to `claudeutils/git.py`. Update worktree imports. Submodule discovery via `git submodule status` / `.gitmodules` — no hardcoded submodule names. Replaces `"-C", "agent-core"` literals with iteration over discovered submodules.

### S-5: Git changes utility

`claudeutils _git changes` — unified parent + submodule view returning both status and diff in one call. Discovers submodules via git, iterates each for status/diff, returns structured markdown. If tree is clean, output says so. If dirty, output includes both the file list and the diff. Consumers: commit skill (input construction for `## Files` and `## Submodule` sections), handoff CLI (H-3 diagnostics). Internal Python functions (`git_status()`, `git_diff()` in `git.py`) serve commit CLI validation (C-2/C-3) separately. No LLM judgment — mechanical git queries only.

### S-3: Output and error conventions

All subcommands:
- All output to stdout as structured markdown — results, diagnostics, AND errors
- Exit code carries the semantic signal: 0=success, 1=pipeline error (runtime failure), 2=input validation (malformed caller input)
- No stderr — LLM callers consume stdout; exit code determines success/failure

Error and warning output uses `**Header:** content` format. Stop errors include `STOP:` directive for data-loss risk cases. Success output varies by subcommand (commit: raw git passthrough; handoff/status: structured markdown). Aligns with worktree merge pattern (all output to stdout, exit code carries signal).

### S-4: Session.md parser

Shared parser for session.md structure:
- Status line (between `# Session Handoff:` and first `##`)
- Completed section (under `## Completed This Session`)
- Pending tasks with metadata (model, command, restart, plan directory)
- `→` markers on tasks: `→ slug` (branched to worktree), `→ wt` (destined for worktree, not yet branched)
- Worktree tasks section
- Plan directory associations

Used by handoff (locate write targets) and status (read + format).

---

## `_handoff`

Two modes — fresh (stdin has content) and resume (no stdin, reads state file).

### Input

```markdown
**Status:** Design Phase A complete — outline reviewed.

## Completed This Session

### Handoff CLI tool design (Phase A)
- Produced outline
- Review by outline-review-agent
```

Required: `**Status:**` line marker and `## Completed This Session` heading. Completed entries use `### ` headings (standard markdown nesting), not bold-colon format.

### Pipeline

**Fresh:**
1. Parse stdin for status marker and completed heading
2. Cache input to state file (before first mutation — enables retry)
3. Overwrite status line in session.md
4. Write completed section (committed detection — see H-2)
5. Output diagnostics (see H-3)
6. Delete state file

**Resume** (no stdin): load from state file, re-execute from `step_reached`. Agent calls `claudeutils _handoff` directly on retry.

### H-1: Domain boundaries

| Owner | Responsibility |
|-------|---------------|
| Handoff CLI | Session.md mechanical writes (status overwrite, completed section) + diagnostics + state caching |
| Worktree CLI | `→ slug` markers (set on `wt` branch-off) |
| Agent (Edit/Write) | Pending task mutations, `→ wt` markers, learnings append + invalidation, blockers, reference files |

Learnings flow: agent writes learnings (Edit) → reviews for invalidation → calls CLI. Manual append before invalidation improves conflict detection via spatial proximity.

### H-2: Completed section write mode

Diff completed section against HEAD (`git diff HEAD -- agents/session.md`, extract section from both):

| Prior state | Behavior |
|---|---|
| No diff (first handoff or content committed) | Overwrite |
| Old removed, new present (agent cleared old) | Append |
| Old preserved with additions | Auto-strip committed content, keep new additions |

Session.md write targets: status line and completed section only. All other sections agent-owned.

### H-3: Diagnostic output

Git status and diff emitted after session.md writes. Serves two consumers: commit skill (constructs `_commit` input) and agent (tree awareness).

| Diagnostic | Condition |
|-----------|-----------|
| Git status/diff | Always |

### H-4: State caching

- Location: `<project-root>/tmp/.handoff-state.json`
- Contents: `{"input_markdown": "...", "timestamp": "...", "step_reached": "..."}`
- `step_reached`: `"write_session"` | `"diagnostics"`
- Created at step 2 (before mutation), deleted on success

---

## `_commit`

Sole commit path. Reads structured markdown on stdin, produces structured markdown on stdout.

Pipeline: validate → vet check → precommit → stage → submodule commit → parent commit.

### Input

```markdown
## Files
- src/commit/cli.py
- src/commit/gate.py
- agent-core/fragments/vet-requirement.md

## Options
- no-vet
- amend

## Submodule agent-core
> 🤖 Update vet-requirement fragment
>
> - Add scripted gate classification reference

## Message
> ✨ Add commit CLI with scripted vet check
>
> - Structured markdown I/O
> - Submodule-aware commit pipeline
```

**Sections:**
- `## Files` — required, first. Bulleted paths to stage (modifications, additions, deletions — `git add` handles all).
- `## Options` — optional. `no-vet` (skip vet check), `just-lint` (lint only), `amend` (amend previous commit), `no-edit` (keep existing message, requires `amend`). Unknown options → error (fail-fast).
- `## Submodule <path>` — repeatable, one per dirty submodule. Conditionally required (see C-2). Blockquoted. Path matches submodule directory name from `git submodule status`.
- `## Message` — required unless `amend` + `no-edit` in Options. Blockquoted. Everything from `## Message` to EOF is message body — safe for content containing `## ` lines.

Parsing: `## ` prefix matched against known section names. Unknown `## ` within blockquotes treated as message body.

### Output

All output to stdout as structured markdown. Exit code carries success/failure signal. Success path: git CLI output only — gate results omitted (exit 0 is the signal). Failure path: gate-specific diagnostic output. Report deviations, not confirmations.

Success — parent only (exit 0):
```markdown
[session-cli-tool a7f38c2] ✨ Add commit CLI with scripted vet check
 3 files changed, 142 insertions(+), 8 deletions(-)
 create mode 100644 src/commit/gate.py
```

Success — with submodule (exit 0):
```markdown
agent-core:
[session-cli-tool 4b2c1a0] 🤖 Update vet-requirement fragment
 1 file changed, 5 insertions(+), 2 deletions(-)
[session-cli-tool a7f38c2] ✨ Add commit CLI with scripted vet check
 4 files changed, 142 insertions(+), 8 deletions(-)
```

Submodule output labeled with `<path>:` prefix. Parent output unlabeled (default context). Distinguishes repos when branch names are identical.

Amend success (exit 0):
```markdown
[session-cli-tool e91b2d4] ✨ Add commit CLI with scripted vet check
 Date: Sun Feb 23 10:15:00 2026 -0800
 4 files changed, 158 insertions(+), 8 deletions(-)
 create mode 100644 src/commit/gate.py
```

Vet check failure — unreviewed files (exit 1):
```markdown
**Vet check:** unreviewed files
- src/auth.py
```

Vet check failure — stale report (exit 1):
```markdown
**Vet check:** stale report
- Newest change: src/auth.py (2026-02-20 14:32)
- Newest report: plans/foo/reports/vet-review.md (2026-02-20 12:15)
```

Precommit failure (exit 1):
```markdown
**Precommit:** failed

ruff check: 2 errors
...
```

Clean-files error (exit 2):
```markdown
**Error:** Listed files have no uncommitted changes
- src/config.py

STOP: Do not remove files and retry.
```

Warning + success (exit 0):
```markdown
**Warning:** Submodule message provided but no changes found for: agent-core. Ignored.

[session-cli-tool a7f38c2] ✨ Add commit CLI with scripted vet check
 3 files changed, 142 insertions(+), 8 deletions(-)
```

**Output principle:** Report deviations only. Success = git commit summary lines (`[branch hash]` + file stats) — agent extracts short hash. Failure = gate-specific diagnostic. Warnings prepended to git output. Strip git `hint:` and advice lines — LLM agents interpret these as instructions (e.g., "remove index.lock" → agent deletes the file).

Error taxonomy: **stop** (non-zero, no commit) for clean-files, missing submodule message, vet check failure, precommit failure. **Warning + proceed** (zero exit) for orphaned submodule message.

### C-1: Scripted vet check

File classification by path pattern:
```toml
[tool.claudeutils.commit]
require-review = [
    "src/**/*.py",
    "tests/**/*.py",
    "scripts/**",
    "bin/**",
]
```

No patterns → check passes (opt-in). Report discovery: `plans/*/reports/` matching `*vet*` or `*review*` (not `tmp/`). Freshness: mtime of newest production artifact vs newest report. Stale → fail.

Vet check must also cover agent-core scripts (`agent-core/bin/**`, `agent-core/skills/**/*.sh`). Config model for submodule patterns (unified parent config vs per-repo `pyproject.toml`) deferred — requires external grounding.

### C-2: Submodule coordination

Per-submodule, discovered via `git submodule status`:

| Submodule files in Files | `## Submodule <path>` present | Result |
|---|---|---|
| Yes | Yes | Commit submodule first |
| Yes | No | **Stop** — needs message |
| No | Yes | **Warning** — ignored |
| No | No | Parent-only commit |

Files partitioned by submodule path prefix. Each dirty submodule requires its own `## Submodule <path>` section. Multiple submodules committed in discovery order, each staged before parent commit.

Sequence per submodule: partition files by path prefix → stage + commit submodule → stage pointer. After all submodules: commit parent.

### C-3: Input validation

Each path in Files must appear in `git status --porcelain`. Clean files → error with stop directive. A clean-listed file means the caller's model doesn't match reality (hallucinated edit, silent write failure).

### C-4: Validation levels

| Context | Validation | Option |
|---------|-----------|--------|
| Final commit | `just precommit` | (default) |
| TDD GREEN WIP | `just lint` | `just-lint` |
| Pre-review (initial implementation, no vet report yet) | Skip vet check only | `no-vet` |
| Combined | `just lint` + skip vet check | `just-lint` + `no-vet` |

Options are orthogonal. No option to skip validation entirely.

### C-5: Amend semantics

`amend` option passes `--amend` to `git commit`. Interactions:
- **C-3 (input validation):** When amending, listed files may already be committed (in HEAD) with no further changes. Validation checks `git status --porcelain` (uncommitted changes) OR `git diff-tree --no-commit-id --name-only HEAD` (file is part of HEAD commit). Clean-file error only fires when a file appears in neither.
- **C-2 (submodule):** Amend propagation is directional — submodule amend implies parent amend (pointer hash changes), but parent-only amend is independent. When submodule files are in the amend set: amend submodule → re-stage pointer → amend parent. When only parent files: amend parent only.
- **Message:** Required unless `no-edit` option is also present. `no-edit` keeps existing commit message — `## Message` section omitted. `no-edit` without `amend` → error.
- **Validation state:** Amend inherits no validation state from the original commit. Caller must re-specify options (`just-lint`, `no-vet`, etc.).

---

## `_status`

Pure data transformation. Reads session.md + filesystem state, produces formatted STATUS output. No mutations, no stdin.

### Pipeline

1. Parse session.md (S-4 parser)
2. `claudeutils _worktree ls` for plan states and worktree info
3. Cross-reference plans with pending tasks → find unscheduled plans
4. Detect parallel task groups
5. Render STATUS format to stdout

### Output

ANSI-colored structured text. Designed for two display paths:
1. **Stop hook integration:** Agent outputs trigger string, Stop hook runs `_status`, `systemMessage` displays result directly to user (zero agent token waste)
2. **Direct invocation:** User runs `claudeutils _status` in terminal

Matches execute-rule.md MODE 1 format with display improvements:
- **Session continuation header:** When git tree is dirty, prepend `Session: uncommitted changes — `/handoff`, `/commit``. If any plan-associated task has status `review-pending`, append `` `/deliverable-review plans/<name>` ``. Omit entirely when tree is clean.
- Suppress `Next:` section when it duplicates the first in-tree task (single-task case)
- Next-task metadata (command, model, restart) merged into the in-tree item with `▶` marker
- Tasks with any `→` marker skipped for `Next:` selection

```
Session: uncommitted changes — `/handoff`, `/commit`

In-tree:
▶ <first task> (<model>) | Restart: <yes/no>
  `<command>`
  Plan: <dir> | Status: <status>
- <other task> (<model>)
  Plan: <dir> | Status: <status>

Worktree:
- <task> → <slug>
- <task> → wt

Unscheduled Plans:
- <plan> — <status>

Parallel (N tasks, independent):
  - task 1
  - task 2
  `wt` to set up worktrees
```

### ST-0: Worktree-destined tasks

Tasks marked `→ wt` in session.md are destined for worktree execution but not yet branched. Status renders them in the Worktree section alongside branched tasks (`→ slug`). `Next:` skips both — prevents inline execution of worktree-appropriate work. The `→ wt` marker is set by user/agent at task creation time (`p:` directive or prioritization).

### ST-1: Parallel group detection

Independent when: no shared plan directory, no logical dependency (Blockers/Gotchas). Constrained by task ordering in session.md — only consecutive independent tasks form a group. Cap at 5 concurrent sessions. First eligible group in document order. Omit section if none.

### ST-2: Preconditions and degradation

Missing session.md → **fatal error** (exit 2). Session.md is the load-bearing file for task tracking — absence signals wrong cwd, corruption, or accidental deletion. Silent degradation to empty state masks data loss. Exit 2 per S-3: this is input validation (expected file missing), not a runtime pipeline failure.

Old format (no metadata) → **fatal error** (exit 2). Mandatory metadata (command, plan reference) enforces plan-backed task rule — no silent defaults. Empty sections omitted.

---

## Scope

**IN:**
- `_handoff`, `_commit`, `_status` top-level commands
- Shared session.md parser
- `_git()` extraction to `claudeutils/git.py` with submodule discovery
- Git changes utility (`claudeutils _git changes`) with submodule-aware output
- Handoff: stdin parsing, session.md writes, committed detection, diagnostics, state caching
- Commit: stdin parsing, scripted vet check (pyproject.toml), input validation, submodule pipeline, structured output
- Status: session.md parsing, plan cross-referencing, parallel detection, STATUS rendering
- Tests (CliRunner + real git repos via tmp_path)
- Registration in main `cli.py`

**OUT:**
- Gate A (session freshness) — `/commit` skill (LLM judgment)
- Commit message drafting, gitmoji selection — skill
- Skill modifications (commit/status skills updated separately)

**Coupled skill update:** Handoff skill must add `just precommit` as a pre-handoff gate (before calling `_handoff` CLI). Delivered with the CLI — removing precommit from the CLI without adding it to the skill drops it from the flow entirely.
- Pending task mutations, learnings, blockers, reference files — agent Edit
- Consolidation delegation — existing skill

**Skill integration (future):** After CLI exists, `/commit` skill simplifies to: Gate A (LLM) → discovery (`claudeutils _git changes`) → draft message + gitmoji → pipe to `claudeutils _commit`. Current skill steps collapse into one CLI call.

## Phase Notes

- Phase 1: `_git()` extraction + submodule discovery + git changes utility + session.md parser — **general**
- Phase 2: Status subcommand — **TDD** (pure function: session.md + filesystem → formatted output)
- Phase 3: Handoff pipeline — **TDD** (stdin parsing, session.md writes, committed detection, state caching, diagnostics)
- Phase 4: Commit parser + input validation — **TDD** (markdown parsing, file status check, submodule message consistency)
- Phase 5: Commit scripted vet check — **TDD** (pyproject.toml patterns, file classification, report discovery + freshness)
- Phase 6: Commit pipeline + output — **TDD** (staging, submodule coordination, amend, structured output with git passthrough)
- Phase 7: Integration tests — **TDD** (end-to-end across subcommands, real git repos)

## Common Context

## Common Context

**Requirements (from design):**
- S-1: Package structure — `_handoff`, `_commit`, `_status` top-level commands registered individually in main cli.py via `cli.add_command()`
- S-2: `_git()` extraction — move from worktree to shared `claudeutils/git.py` with submodule discovery
- S-3: Output/error — all stdout, exit code carries signal, no stderr
- S-4: Session.md parser — shared parser extending existing `worktree/session.py`
- S-5: `_git changes` — unified parent + submodule status+diff in one call
- Handoff: stdin parsing, session.md writes, committed detection, state caching, diagnostics (git status/diff only — precommit is pre-handoff gate)
- Commit: stdin parsing, scripted vet check, submodule coordination, structured output
- Status: pure data transformation, session.md + filesystem → STATUS format

**Scope boundaries:**
- IN: `_handoff`, `_commit`, `_status` commands, `_git changes`, shared parser, git extraction, tests
- OUT: Gate A (LLM judgment), commit message drafting, gitmoji, skill modifications, pending task mutations

**Key Constraints:**
- All output to stdout as structured markdown — no stderr (S-3)
- Exit codes: 0=success, 1=pipeline error, 2=input validation
- `_fail()` pattern with `Never` return type for error termination
- CliRunner + real git repos via `tmp_path` for all tests
- Reuse existing `ParsedTask`, `extract_task_blocks()`, `find_section_bounds()` — do not duplicate

**Project Paths:**
- `src/claudeutils/worktree/git_ops.py`: Source of `_git()`, `_is_submodule_dirty()` for extraction
- `src/claudeutils/worktree/session.py`: Existing session.md parsing (TaskBlock, extract_task_blocks, find_section_bounds)
- `src/claudeutils/validation/task_parsing.py`: ParsedTask, parse_task_line, TASK_PATTERN
- `src/claudeutils/cli.py`: Main CLI with `cli.add_command()` registration pattern
- `src/claudeutils/exceptions.py`: Project exception hierarchy

**Stop/Error Conditions (all cycles):**
- RED fails to fail → STOP, diagnose test (assertion may be vacuous)
- GREEN passes without implementation → STOP, test too weak
- `just precommit` fails after GREEN → fix lint/test issues before proceeding
- Implementation needs architectural decision → STOP, escalate to user

**Dependencies (all cycles):**
- Phases are sequential: Phase N depends on Phase N-1 unless noted otherwise
- Phase 5 is independent of Phases 3-4 (commit parser has no dependency on status/handoff)
- Phase 6 depends on Phase 5 (commit pipeline uses commit parser + vet check)
- Phase 7 depends on Phases 3-4 (cross-subcommand contract test between status and handoff)

---

**Scope enforcement:** Review ONLY the implementation files provided. Focus on correctness, minimal implementation, and GREEN phase compliance. Do NOT flag test details.
