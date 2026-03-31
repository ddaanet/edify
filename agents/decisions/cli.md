# CLI Design

CLI-specific patterns and conventions for edify command-line interface.

## .CLI Conventions

### When Getting Current Working Directory

**Decision:** Use `Path.cwd()` for default project directory

**Rationale:** Consistency with pathlib usage throughout codebase

**Implementation:** `cli.py:main()`

### How to Output Errors To Stderr

**Decision:** Print errors to stderr using `print(..., file=sys.stderr)` before `sys.exit(1)`

**Applies to:** User-facing commands (`analyze`, `rules`, `tokens`) — standard Unix convention.

**Examples:**
- "No session found with prefix 'xyz'" → stderr, exit 1
- "Multiple sessions match prefix 'abc'" → stderr, exit 1

### When CLI Commands Are LLM-Native

**Decision:** All output to stdout as structured markdown. Exit code carries success/failure signal. No stderr.

**Applies to:** Internal commands consumed by LLM agents (`_session` group — underscore prefix, hidden from `--help`).

**Rationale:** LLM callers consume stdout natively. stderr is invisible to the calling agent's structured parsing. Exit code is the only reliable signal channel. Structured markdown is the format LLMs produce and consume without quoting/escaping issues.

**Format:** `**Header:** content` for key-value items, bulleted lists for multi-item output, `STOP:` directive for data-loss risk errors.

**Distinction from user-facing:** User-facing commands follow Unix convention (stderr for errors, text/JSON format options). LLM-native commands follow agent convention (all stdout, markdown, exit codes).

### How to Configure Script Entry Points

**Decision:** Add `[project.scripts]` in pyproject.toml: `edify = "edify.cli:main"`

**Rationale:** Simpler invocation (`edify list` vs `uv run python -m edify.cli list`)

**Impact:** Direct command usage after install

## .Safety Patterns

### When Writing CLI Output

**Decision Date:** 2026-02-18

**Anti-pattern:** CLI suggesting destructive commands in output (e.g., `"use: git branch -D <slug>"`). LLM agents treat CLI output as instructions and execute the suggested command.

**Correct pattern:** Report the problem without prescribing destructive workarounds. Let the calling agent or user decide the action. CLI should refuse destructive operations, not suggest them.

**Evidence:** `_worktree rm` suggested `git branch -D` for unmerged branch. Agent followed the instruction, permanently deleting the only copy of unmerged parent repo changes.

## .Output Formats

### When Choosing Feedback Output Format

**Decision:** Support both `--format text` (default) and `--format json`

**Rationale:** Text for human review, JSON for piping to other tools

**Impact:** All batch commands (`analyze`, `rules`) support both formats

### How to Format Token Count Output

**Decision:** Human-readable text by default, JSON with `--json` flag; include resolved model ID in all outputs

**Text format:**
```
Using model: claude-sonnet-4-5-20250929
path/to/file1.md: 150 tokens
path/to/file2.md: 200 tokens
Total: 350 tokens
```

**JSON format:**
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "files": [
    {"path": "path/to/file1.md", "count": 150},
    {"path": "path/to/file2.md", "count": 200}
  ],
  "total": 350
}
```

**Rationale:**
- Matches existing CLI patterns (analyze, rules); text for humans, JSON for scripting
- Show resolved model ID so users know which exact model version was used
- Critical for debugging and reproducibility (especially when using aliases that auto-update)

## .Code Density

### When Checking Expected Program State

**Principle:** EAFP is idiomatic Python for IO operations where failure is uncommon (file access, network calls), but expected program states — existence checks, availability queries — are not exceptional events. When a condition is a normal branch in program logic, check it with a boolean return, not a try/except. Source pattern: Real Python EAFP/LBYL guide distinguishes IO-bound EAFP from state-query abuse; charlax/antipatterns: "Exception handling is for unexpected or exceptional events."

**Project instance:** Two inconsistent idioms for "does branch exist?" coexisted — raw subprocess LBYL (5-6 lines under Black) and EAFP try/except that treated an expected condition as exceptional. Consolidated as `_git_ok(*args) -> bool` returning `returncode == 0`. Covers 13 of 15 raw subprocess sites. Two outliers needing stderr remain as raw calls.

### When Writing Error Exit Code

**Principle:** Error termination should be a single call, not a display+exit sequence. CLI frameworks recognize this pattern — Click's `ClickException` and `UsageError` consolidate display and exit into one raise. When display and exit are separate statements, they drift apart: different messages, forgotten exits, inconsistent stderr routing. Source: Click exception hierarchy docs.

**Project instance:** 18 instances of `click.echo(msg, err=True)` followed by `raise SystemExit(N)` across the worktree module. Consolidated as `_fail(msg, code=1) -> Never` in utils.py. `Never` return type informs type checkers that control flow terminates. Click's own `ClickException` was considered and rejected — its hardcoded exit codes (UsageError->2, Abort->1) don't map to this project's exit code semantics.

### When Call Site Expands Under Formatter

**Principle:** When a call site consistently takes 5+ lines after opinionated formatting, the call has too many parameters for inline use. Black's algorithm tries to fit calls on one line, falling back to one-arg-per-line with keyword arguments expanding aggressively. A function that "looks fine" hand-formatted but explodes under Black has an API surface problem, not a formatting problem. Extract a helper whose defaults encode common kwargs as policy — this reduces Black expansion by collapsing keyword arguments into the helper's signature.

**Project instance:** Raw `subprocess.run()` with keyword args expands to 5-6 lines under Black. `_git()` collapses stdout calls to 1 line, but callers bypassed it when they needed returncode. `_git_ok()` covers the returncode case, eliminating the bypass pattern.

### When Raising Exceptions for Expected Conditions

**Principle:** Exception handling is for unexpected or exceptional events, not normal program states. Using broad exception types (`ValueError`) for expected conditions masks legitimate bugs under the same `except` clause — the handler cannot distinguish a real ValueError from the expected-condition signal. Custom exception classes make the distinction explicit. Source: charlax/antipatterns error-handling guide, Real Python EAFP/LBYL.

**Project instance:** `try: _git("rev-parse"...) except CalledProcessError:` used to check branch existence — replaced with `_git_ok()` boolean. `ValueError` raised for expected conditions (no session found, multiple matches) — replaced with custom exception classes (`SessionNotFoundError`). Custom classes also properly satisfy lint rules about hardcoded exception messages, eliminating the `msg` variable circumvention pattern.

### When Adding Error Handling to Call Chain

**Principle:** Each layer in the error handling chain has one responsibility. Failure site: collect context, raise typed exception. Top level: display and exit. When both layers print, you get duplicate output or conflicting messages. The `raise from` chain preserves the causal chain without duplicating display logic.

**Project instance:** Double error handling in cli.py — exceptions caught and messages printed at both the failure site and a top-level handler. Rule: context collection at the failure site, display at the top level, never both.

## .LLM-Native Design

### When Designing CLI Tools For LLM Callers

**Decision Date:** 2026-02-20

**Anti-pattern:** Using traditional CLI conventions (flags, short options, positional args) for tools whose sole caller is an LLM agent. Quoting/escaping in bash heredocs is error-prone, multiline arguments need gymnastics.

**Correct pattern:** Structured markdown on stdin, structured markdown on stdout. LLM-native format — no quoting issues, natural multiline, extensible without code changes. Section-based parsing with known section names as boundaries.

**Rationale:** CLI conventions exist for human ergonomics (tab completion, discoverability). LLMs need formats they produce and consume natively.

### When CLI Error Messages Are LLM-Consumed

**Decision Date:** 2026-02-20

**Anti-pattern:** Including suggested causes or recovery actions in error messages ("may have been committed already", "remove and retry"). LLM agents treat suggestions as instructions, enabling rationalization past real problems.

**Correct pattern:** Facts only — state what IS, not what MIGHT BE. For unrecoverable errors (data loss risk), include `STOP:` directive. For recoverable errors, CLI handles recovery itself and surfaces a warning.

**Evidence:** Clean-files error without STOP → agent removes file from list and confabulates "already committed." With STOP directive, agent reports to user instead.
