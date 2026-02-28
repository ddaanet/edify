# Recall CLI Integration

Production `claudeutils _recall` CLI replacing the three prototype shell scripts (`recall-check.sh`, `recall-resolve.sh`, `recall-diff.sh`) with a Click-based, LLM-native command group. TDD.

## Requirements

### Functional Requirements

**FR-1: `_recall check <job-name>`**
Validates that `plans/<job>/recall-artifact.md` is a structurally valid recall artifact. Existence alone is insufficient — the artifact must contain a `## Entry Keys` section with at least one parseable entry. The null entry (`null — no relevant entries found`) satisfies minimum validity. Replaces `agent-core/bin/recall-check.sh`.

Acceptance criteria:
- Exit 0 when artifact has `## Entry Keys` section with at least one parseable line
- Exit 1 + "recall-artifact.md missing for <job>" when file absent
- Exit 1 + "recall-artifact.md has no Entry Keys section for <job>" when section missing
- Exit 1 + "recall-artifact.md has no entries for <job>" when section exists but empty
- Null entry counts as valid (parseable, resolver handles silently)
- Operates relative to project root

**FR-2: `_recall resolve` — two modes**
Resolves recall triggers via `claudeutils.when.resolver.resolve()`. Outputs resolved content to stdout with `---` separators. Two invocation modes with different error semantics.

**Artifact mode:** `_recall resolve <artifact-path>`
Reads recall artifact reference manifest file. Every entry was curated — resolution failure means broken artifact. Replaces `agent-core/bin/recall-resolve.sh`.

Acceptance criteria:
- Parses only the `## Entry Keys` section (terminal section — read from section header to EOF)
- All content above `## Entry Keys` (title, preamble prose, metadata) is structurally excluded
- Entry lines: `<trigger> — <annotation>` or bare `<trigger>` (annotation optional, supports sub-agent flat-list format)
- When annotation present: strips on first `—` separator, left side is trigger
- Detects operator prefix: lines starting with "when"/"how" used as-is, others get "when" prepended
- Skips blank lines and comment lines (`#` prefix) within the section
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

**C-2: Project root via `CLAUDE_PROJECT_DIR`**
`check` and `diff` derive `plans/<job>/recall-artifact.md` from project root + job name. `resolve` artifact mode takes an explicit file path; argument mode takes trigger strings. Project root: `Path(os.getenv("CLAUDE_PROJECT_DIR", "."))` — matches `when/cli.py:84`, the resolver `_recall` delegates to.

**C-3: No project-specific hardcoded paths**
Module code must not hardcode `agents/memory-index.md` or `agents/decisions/` paths. These are resolved via the when/resolver's existing path resolution, or passed as arguments.

**C-4: `## Entry Keys` is terminal section**
Recall artifacts must have `## Entry Keys` as the final section. Parser reads from section header to EOF — no closing boundary detection needed. Preamble (title, description, future metadata sections) lives above. Simplifies both `check` (section exists + has content) and `resolve` (parse to EOF).

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

### Resolved Questions

- Q-1: Delete prototype scripts after CLI ships? **Yes.** Deliverable includes deleting `agent-core/bin/recall-{check,resolve,diff}.sh` and updating referencing skills/docs in same change. Code removal principle; git history preserves originals.

### References

- `agent-core/bin/recall-check.sh` — prototype behavioral spec for check
- `agent-core/bin/recall-resolve.sh` — prototype behavioral spec for resolve
- `agent-core/bin/recall-diff.sh` — prototype behavioral spec for diff
- `plans/recall-tool-anchoring/outline.md` (git: `42526e00`) — design decisions D-1 through D-7
- `agents/decisions/cli.md` — CLI conventions, LLM-native patterns, _fail helper
- `agents/decisions/testing.md` — CliRunner, TDD patterns, e2e with real git repos
