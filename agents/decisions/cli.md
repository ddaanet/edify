# CLI Design

CLI-specific patterns and conventions for claudeutils command-line interface.

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

**Decision:** Add `[project.scripts]` in pyproject.toml: `claudeutils = "claudeutils.cli:main"`

**Rationale:** Simpler invocation (`claudeutils list` vs `uv run python -m claudeutils.cli list`)

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

### When Expected State Checks Should Return Booleans

**Principle:** Normal program states checked with boolean returns, not exceptions. EAFP is idiomatic for IO where failure is uncommon, but expected states (existence checks, availability queries) are not exceptional.

**Project instance:** `_git_ok(*args) -> bool` checks branch existence without raising `CalledProcessError`. Returns `returncode == 0`. Replaces try/except blocks that treated expected conditions as exceptions.

### When Error Termination Should Be a Single Call

**Principle:** Consolidate display and exit into a single call. When display and exit are separate statements, they drift apart — different messages, forgotten exits, inconsistent stderr routing.

**Project instance:** `_fail(msg, code=1) -> Never` in utils.py combines `print(msg, file=sys.stderr)` and `raise SystemExit(code)`. The `Never` return type informs type checkers that control flow terminates.

### When Formatter Expansion Signals Abstraction Need

**Principle:** When a call site takes 5+ lines after opinionated formatting (Black), the call has too many parameters for inline use. Extract a helper whose defaults encode common kwargs.

**Project instance:** `subprocess.run()` with keyword args expands to 5-6 lines under Black. The `_git()` helper collapses stdout calls to 1 line; `_git_ok()` covers returncode cases without formatter expansion.

### When Exceptions Should Be for Exceptional Events Only

**Principle:** Custom exception classes for expected conditions (e.g., `SessionNotFoundError`, `MultipleSessionsError`), not broad types like `ValueError`. Broad types mask legitimate bugs under the same `except` clause.

**Project instance:** `ValueError` raised for expected conditions (no session found, multiple matches) → replaced with custom exception classes. Custom classes satisfy lint rules about hardcoded exception messages without workarounds.

### When Error Handling Layers Should Not Overlap

**Principle:** Each error handling layer has one responsibility — failure site collects context and raises typed exception, top level displays and exits. When both layers print, you get duplicate output or conflicting messages.

**Project instance:** Rule in cli.py — context collection at failure site, display at top level, never both. Use `raise from` chains to preserve causal chains without duplicating display logic.
