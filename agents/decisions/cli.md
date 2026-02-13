# CLI Design

CLI-specific patterns and conventions for claudeutils command-line interface.

## .CLI Conventions

### When Getting Current Working Directory

**Decision:** Use `Path.cwd()` for default project directory

**Rationale:** Consistency with pathlib usage throughout codebase

**Implementation:** `cli.py:main()`

### How to Output Errors To Stderr

**Decision:** Print errors to stderr using `print(..., file=sys.stderr)` before `sys.exit(1)`

**Rationale:** Standard Unix convention - errors to stderr, data to stdout

**Examples:**
- "No session found with prefix 'xyz'" → stderr, exit 1
- "Multiple sessions match prefix 'abc'" → stderr, exit 1

### How to Configure Script Entry Points

**Decision:** Add `[project.scripts]` in pyproject.toml: `claudeutils = "claudeutils.cli:main"`

**Rationale:** Simpler invocation (`claudeutils list` vs `uv run python -m claudeutils.cli list`)

**Impact:** Direct command usage after install

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
