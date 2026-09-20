# CLI and package

Decisions behind the `edify-cli` package: output conventions, error handling,
data structures, the plugin/package split and the runtime bootstrap, plus the
markdown postprocessor and the token counter. Read this before changing anything
under `src/edify/` or `plugin/bin/`.

Part of the `docs/design.md` graph; conclusions are indexed in
`docs/decisions.md`.

## CLI and package

**D-1 — Two output conventions, split by consumer.** User-facing commands follow
Unix convention: errors to stderr via `print(..., file=sys.stderr)` before
`sys.exit(1)`, with text and JSON format options. Commands whose sole caller is
an LLM agent emit everything to stdout as structured markdown and carry
success/failure only in the exit code. stderr is invisible to a calling agent's
structured parsing, and exit code is the only reliable channel. Structured
markdown is the format LLMs produce and consume without quoting or escaping
problems: `**Header:** content` for key-value items, bulleted lists for
multi-item output, a `STOP:` directive for data-loss risk.

**D-2 — CLI output never prescribes destructive commands.** LLM agents treat CLI
output as instructions and execute what it suggests. Report the problem; let the
caller decide. A CLI should refuse destructive operations, not recommend them.
*Grounding:* a worktree removal command suggested `git branch -D` for an
unmerged branch; the agent followed it and permanently deleted the only copy of
unmerged changes.

**D-3 — Error messages state facts, not hypotheses.** No suggested causes ("may
have been committed already") and no recovery advice ("remove and retry") —
agents treat suggestions as instructions and rationalize past real problems. For
unrecoverable errors include `STOP:`; for recoverable ones the CLI handles
recovery itself and surfaces a warning. *Grounding:* an error without `STOP:`
led an agent to drop the file from its list and confabulate "already committed".

**D-4 — Expected states are branches, not exceptions.** EAFP is idiomatic for IO
where failure is uncommon; existence checks and availability queries are normal
control flow and get a boolean. `_git_ok(*args) -> bool` returning
`returncode == 0` replaced both a raw-subprocess LBYL idiom and an EAFP
`try/except CalledProcessError`. Broad exception types for expected conditions
mask real bugs under the same handler, so domain conditions get custom classes
(`SessionNotFoundError`) — which also satisfies the lint rule about hardcoded
exception messages without the `msg` variable dodge. *Sources:* Real Python
EAFP/LBYL; charlax/antipatterns.

**D-5 — One responsibility per error-handling layer.** The failure site collects
context and raises a typed exception; the top level displays and exits. When
both print, output duplicates or conflicts. `raise from` preserves the causal
chain without duplicating display. Error termination is a single call —
`_fail(msg, code=1) -> Never` — because separated display and exit statements
drift apart. Click's `ClickException` was considered and rejected: its hardcoded
exit codes (UsageError→2, Abort→1) do not map to this project's exit semantics.

**D-6 — A call site that explodes under Black has an API problem.** When a call
consistently takes 5+ lines after formatting, it has too many parameters for
inline use. Extract a helper whose defaults encode the common kwargs as policy.
*Reopen-if:* the formatter changes its line-joining algorithm.

**D-7 — Pydantic for all data structures, StrEnum for closed vocabularies.**
Runtime type validation, ISO 8601 timestamp handling and
`model_dump(mode="json")` serialization, rather than static analysis alone.

**D-8 — Malformed session data degrades, it does not abort.** Skip malformed
entries, log a warning, continue. Empty files skip; malformed JSON logs and
skips; a missing `sessionId` is treated as non-match; a non-existent history
directory raises `FileNotFoundError`. Partial data beats total failure, and the
warnings tell the user where to look. Optional fields use
`.get(field, default)`.

**D-9 — Publication is postponed indefinitely (2026-07-17, user decision).** The
PyPI publish and the marketplace `git-subdir` entry are parked. The marketplace
manifest has no `edify` entry, so edify is uninstallable meanwhile. *Reopen-if:*
the user asks to publish; note that publish ordering is hard — `edify-cli` must
reach the index *before* the plugin version that pins it, so a plugin version
can never lead its package.

**D-10 — The plugin is a subdirectory, not a submodule.** A parent repo cannot
`git add` inside a submodule, so `git add plugin/.claude-plugin/plugin.json`
failed and `just release` could not complete a real release. Flattening removes
the boundary and the permanent gitlink-drift overhead. Merging the plugin all
the way up to the repo root was rejected: it would force the plugin to carry the
inert `src/` tree as its own content, whereas keeping `plugin/` as the plugin
root means the plugin's content is exactly `plugin/`. *Executed 2026-07-16*
(`c3c4477f`); the old `ddaanet/edify-plugin` GitHub repo was archived.

**D-11 — The venv lives in `CLAUDE_PLUGIN_DATA`, version-scoped by path.** Build
at `${CLAUDE_PLUGIN_DATA}/venv-<version>/`; a version change changes the path,
so an absent directory *is* the rebuild signal and the hook prunes non-matching
siblings. `${CLAUDE_PLUGIN_ROOT}/.venv` is more elegant — ROOT is already
version-scoped and auto-GC'd — but ROOT writability at hook time is unverifiable
from the docs, which say "treat as ephemeral" prescriptively without documenting
a read-only mount. The venv is expensive (CrossHair pulls z3); if the
persistence assumption were wrong the failure would be silent and cost a full
reinstall every session. Two lines of sibling pruning beat that risk.
*Reopen-if:* one throwaway test confirms a write into ROOT survives to the next
tool call.

**D-12 — Skills reach the binary by content substitution, never a hardcoded
path.** Skill and agent markdown support `${CLAUDE_PLUGIN_ROOT}` /
`${CLAUDE_PLUGIN_DATA}` substitution in their *content*; those variables are
exported as environment variables only to hook, MCP and LSP subprocesses, not to
Bash-tool subprocesses. If `${CLAUDE_PLUGIN_DATA}` proved not to substitute in
skill content, the fix is a different substitutable mechanism, not a literal
`~/.claude/plugins/data/...` path: a rarely-exercised fallback path format
drifts and rots silently, failing exactly when the primary mechanism is already
unavailable. *Open gate:* one throwaway skill echoing the placeholder confirms
`DATA` (not just `ROOT`) substitutes.

**D-13 — Dogfooding never requires a registry publish.** The bootstrap installs
from a package index, not from PyPI specifically. Build the wheel locally, point
uv at it (`UV_FIND_LINKS`, `UV_INDEX`), prove the bootstrap green offline, then
publish and drop the override. The publish-ordering constraint binds releases,
not development.

## Markdown and token tooling

**D-14 — remark-cli is the formatter.** Chosen 2026-01-07 over Prettier and
markdownlint-cli2: idempotent by design with fixed configuration, 100%
CommonMark compliance via micromark, correct nested code blocks, exact YAML
frontmatter preservation. Prettier is non-idempotent (documented bugs on empty
sub-bullets, mid-word underscores, extra-indent lists), strips frontmatter
comments and reduces backticks inconsistently. markdownlint-cli2 is a linter,
not a formatter, and offers no idempotency guarantee. Both Prettier and remark
passed the test corpus over three runs; Prettier's documented edge cases decided
it.

**D-15 — The preprocessor runs before the formatter and fails loudly.** Claude
emits markdown-like output that is not always valid markdown: emoji-prefixed
lines that should be lists, improperly nested fences, metadata labels needing
indentation. `markdown.py` fixes structure, then remark applies style. When
inner fences are detected in non-markdown blocks the preprocessor errors out
rather than silently skipping (which hides the problem until remark fails) or
auto-fixing (which risks corrupting code content). Fix order is line-based
first, then spacing, then block-based last, because line fixes interfere with
each other otherwise and the code-block pass needs complete structure. Prefix
detection is generic — any consistent non-markup prefix — rather than a
whitelist that needs updating for each new pattern. Nested lists indent 2
spaces, matching the remark default.

**D-16 — Model aliases resolve at runtime with a 24-hour cache.** Anything
starting with `claude-` passes through unchanged. A short alias (`sonnet`,
`haiku`, `opus`) is resolved by querying `client.models.list()`, filtering by
substring and selecting the latest `created_at`, cached in the platform user
cache directory via `platformdirs`. An unresolvable alias passes through so the
API produces the error. Every output names the resolved model ID, because
aliases auto-update and reproducibility depends on knowing which snapshot ran.
Empty files return 0 without an API call.

## Rejected alternatives

**Prettier and markdownlint-cli2 as the markdown formatter** — see D-14.

**Merging the plugin to the repo root** — would force the plugin to carry the
inert `src/` tree as its own content (D-10).

**Keeping `plugin/` as a submodule** — ships a live defect: `git add` inside a
submodule fails, so `just release` cannot complete (D-10).

**A stdlib venv (`python3 -m venv` + pip) for the bootstrap** — chosen
2026-07-16 and reversed 2026-07-17. A stdlib venv inherits the host interpreter,
so it required host `python3` ≥3.14 and failed loudly otherwise — unshippable on
hosts still at 3.13. uv fetches its own interpreter, removing the host floor.
The price is a uv runtime dependency, paid down by informative degradation
(NFR-5).

**Requiring a separate global `uv tool install edify-cli`** — works, but couples
the plugin to an out-of-band manual step.

**Running the CLI from the `src/` tree in the same repo** — impossible: a subdir
install does not copy sibling source into the cache.

**`${CLAUDE_PLUGIN_ROOT}/.venv` for the venv** — more elegant semantics, but
ROOT writability at hook time is unverifiable from the docs (D-11).

**A hardcoded `~/.claude/plugins/data/...` fallback path in skills** — a
rarely-exercised path format drifts and rots silently (D-12).

**Click's `ClickException` for CLI failure** — hardcoded exit codes do not map
to this project's semantics (D-5).

**A JSON file as a general key-value store** — the existing models cache is a
special case (bounded, ~50 entries, TTL-refreshed); extending it to unbounded
append-heavy caches cargo-cults the storage choice. sqlite via sqlalchemy is the
answer for persistent caches: stdlib sqlite3 handles concurrent access, mapped
classes match the Pydantic convention.
