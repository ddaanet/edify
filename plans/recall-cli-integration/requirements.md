# Recall CLI Integration

Production `claudeutils _recall` CLI replacing the three prototype shell scripts (`recall-check.sh`, `recall-resolve.sh`, `recall-diff.sh`) with a Click-based, LLM-native command group. TDD.

## Requirements

### Functional Requirements

**FR-1: `_recall check <job-name>`**
Validates that `plans/<job>/recall-artifact.md` exists and is non-empty. Exit 0 on success. Exit 1 with diagnostic on failure (missing file, empty file). Replaces `agent-core/bin/recall-check.sh`.

Acceptance criteria:
- Exit 0 when artifact exists and has content
- Exit 1 + "recall-artifact.md missing for <job>" when file absent
- Exit 1 + "recall-artifact.md empty for <job>" when file exists but empty
- Operates relative to project root (cwd)

**FR-2: `_recall resolve` — two modes**
Resolves recall triggers via `claudeutils.when.resolver.resolve()`. Outputs resolved content to stdout with `---` separators. Two invocation modes with different error semantics.

**Artifact mode:** `_recall resolve <artifact-path>`
Reads recall artifact reference manifest file. Every entry was curated — resolution failure means broken artifact. Replaces `agent-core/bin/recall-resolve.sh`.

Acceptance criteria:
- Parses manifest lines: `<trigger> — <annotation>` format
- Strips annotation, preserves trigger
- Detects operator prefix: lines starting with "when"/"how" used as-is, others get "when" prepended
- Skips blank lines, comment lines (`#` prefix), and markdown headers (`##` prefix)
- Null entries (`null — no relevant entries found`) pass through to resolver which handles them silently (delivered: recall-null). Not counted as resolution failures
- Deduplicates resolved content (same entry referenced twice → output once)
- Exit 0 on success (including empty manifest / all-null)
- **Exit 1 if ANY non-null trigger fails to resolve** — artifact integrity check

**Argument mode:** `_recall resolve <trigger> [<trigger> ...]`
Agent passes triggers as CLI arguments. Exploratory, best-effort — partial success is acceptable.

Acceptance criteria:
- Each argument is a trigger string (operator prefix optional, same stripping as artifact mode)
- Null trigger (`null`) delegated to resolver (silent handling, not counted toward resolution success/failure)
- Deduplicates resolved content
- **Exit 0 if at least one trigger resolves** — best-effort for agent-driven recall
- Exit 1 only if zero triggers resolve
- Reuses `claudeutils.when.resolver.resolve()` — no independent resolution implementation

**Mode detection:** First argument is a file path (exists on disk) → artifact mode. Otherwise → argument mode.

**FR-3: `_recall diff <job-name>`**
Lists files changed in `plans/<job>/` since `recall-artifact.md` was last modified. Uses git log with mtime comparison. Excludes the artifact file itself from results. Replaces `agent-core/bin/recall-diff.sh`.

Acceptance criteria:
- Lists files changed since artifact mtime via `git log --since=<mtime> --name-only`
- Excludes `plans/<job>/recall-artifact.md` from output
- Deduplicates file list
- Sorted output
- Exit 0 always (empty output = no changes)
- Exit 1 if not inside git repository
- Exit 1 if artifact file missing

**FR-4: Click group registration**
Register `_recall` as a hidden Click group (`name="_recall"`) on the main CLI. Three subcommands: `check`, `resolve`, `diff`.

Acceptance criteria:
- `claudeutils _recall check <job>` works
- `claudeutils _recall resolve <path>` works (artifact mode)
- `claudeutils _recall resolve "when X" "how Y"` works (argument mode)
- `claudeutils _recall diff <job>` works
- Hidden from `claudeutils --help` (underscore prefix convention)
- Does not conflict with existing `recall` command (recall effectiveness analysis)

**FR-5: LLM-native output**
All output to stdout as structured markdown. No stderr for normal operation. Exit codes carry success/failure signal. Error messages are facts only — no suggestions, no recovery advice.

Acceptance criteria:
- All output to stdout
- Error messages state what IS, not what MIGHT BE
- No destructive suggestions in error output
- Exit codes: 0 (success), 1 (error)

### Constraints

**C-1: Reuse when/resolver**
`_recall resolve` delegates to `claudeutils.when.resolver.resolve()`. No independent resolution implementation. Rationale: when/resolver is the canonical resolution engine; duplication creates divergence risk.

**C-2: Path derivation from cwd**
`check` and `diff` derive `plans/<job>/recall-artifact.md` from cwd + job name. `resolve` artifact mode takes an explicit file path; argument mode takes trigger strings. Matches existing CLI pattern (`Path.cwd()` for project directory).

**C-3: No project-specific hardcoded paths**
Module code must not hardcode `agents/memory-index.md` or `agents/decisions/` paths. These are resolved via the when/resolver's existing path resolution, or passed as arguments.

### Out of Scope

- `_recall generate` — entry selection is cognitive, deferred (D-4 from outline)
- Resolution caching — measure before solving (D-7 from outline)
- Replacing `when-resolve.py` or the `when` command — that's the separate "Recall tool consolidation" task
- Recall effectiveness analysis changes — existing `recall` command stays unchanged
- Hook registration or PreToolUse gate changes — already delivered by recall-tool-anchoring
- Memory-index format changes — separate consolidation scope

### Dependencies

- `claudeutils.when.resolver.resolve()` — importable and stable, includes null mode (recall-null delivered). Tested in `test_when_resolver*.py`, `test_when_null.py`
- Prototype scripts — `agent-core/bin/recall-{check,resolve,diff}.sh` define behavioral spec

### Open Questions

- Q-1: After production CLI ships, should the prototype shell scripts be deleted? (Likely yes — code removal principle — but confirm timing relative to skill D+B restructure references)

### References

- `agent-core/bin/recall-check.sh` — prototype behavioral spec for check
- `agent-core/bin/recall-resolve.sh` — prototype behavioral spec for resolve
- `agent-core/bin/recall-diff.sh` — prototype behavioral spec for diff
- `plans/recall-tool-anchoring/outline.md` (git: `42526e00`) — design decisions D-1 through D-7
- `agents/decisions/cli.md` — CLI conventions, LLM-native patterns, _fail helper
- `agents/decisions/testing.md` — CliRunner, TDD patterns, e2e with real git repos
