# CLI and package

Decisions behind the `edify-cli` package: output conventions, error handling,
data structures, the plugin/package split and the runtime bootstrap, plus the
markdown postprocessor and the token counter. Read this before changing anything
under `src/edify/` or `plugin/bin/`.

Part of the `docs/design.md` graph; conclusions are indexed in
`docs/decisions.md`.

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

**D-9 — Publication is postponed indefinitely (2026-07-17, user decision).**
*Reversed 2026-08-04:* `edify-cli` 0.0.3 shipped to PyPI through `just release`,
and the `ddaanet` marketplace now carries an `edify` entry with a `git-subdir`
source (`url: ddaanet/edify`, `path: plugin`). Edify is installable. No in-repo
source records *why* the postponement was lifted; the nearest thing is the note
that the publish was verified end to end through the SessionStart bootstrap
resolving from PyPI, which is the occasion rather than a stated reason. What
survives the reversal is the ordering constraint it warned about: `edify-cli`
must reach the index *before* the plugin version that pins it, because the
bootstrap installs `edify-cli==<plugin version>`, so a plugin version can never
lead its package. `scripts/release.sh` encodes that order — the PyPI publish
sits between the tag push and the GitHub release (D-87).

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

**D-87 — The release recipe is edify's own, because the shared plugin toolkit
excludes hybrid repos by design.** `scripts/release.sh`, behind `just release`,
bumps `plugin/.claude-plugin/plugin.json` as the version source of truth, syncs
`pyproject.toml` through `uv version`, commits, tags, pushes, publishes the
wheel to PyPI, creates the GitHub release and bumps the marketplace entry, each
external step probing what already landed so `--resume` can finish a release
that died partway. The publish sits between the tag push and the GitHub release,
which is where the D-9 ordering constraint binds. The script lives at the repo
root rather than under `plugin/`, because that directory ships verbatim to every
install and `MARKETPLACE_DIR` paths and PyPI credentials have no business inside
it. Adopting `claude-plugin-dev` instead is not a configuration question: that
project rules edify's shape out in its own record, both as a repo non-goal
("Don't add hybrid Python+plugin support … Repos like `edify` are deliberately
out of scope") and as a stated limitation ("Hybrid Python+plugin repos (e.g.
edify) are out of scope. … Edify keeps its bespoke recipe"). The shape it
excludes is the one §5.1 describes — two products in one tree whose versions
move in lockstep (NFR-4). Concretely its recipe carries no PyPI build or publish
step and no `pyproject.toml` awareness, drives a single manifest rather than two
version files, and resolves that manifest at the repo root, where edify's sits a
directory down with no search and no configuration to point it there. Adoption
is also not free-standing: integration vendors the toolkit as a `git subtree`
plus an imported justfile, and installs a PreToolUse hook that denies any Write
or Edit changing `plugin.json`'s `.version`. Edify's script is not independent
invention — its GitHub and marketplace steps are ported near-verbatim from the
toolkit's with the PyPI step spliced in, so the divergence stays legible and the
port is what to re-read when those steps change upstream. Three frictions are
not grounds either way: submodule handling stopped being a need when D-10
flattened `plugin/`; the marketplace side effect stopped being a differentiator
once `scripts/release.sh` grew the same `MARKETPLACE_DIR` requirement and the
same synthesize-an-entry-if-absent branch; and the dry-run and rollback gaps are
real but are the toolkit's own framing of its exclusion rather than edify's
requirement — edify has neither, and offers `--resume` instead.
*Taken 2026-07-16* (user decision) as keep-now-migrate-later, not as a permanent
split; the migration needs the exclusion lifted, and nothing has lifted it.
*Reopen-if:* the toolkit grows a hybrid path, or its maintainers revisit an
exclusion that predates the de-submodule (D-10) — the edify it ruled out was a
different shape from the merged one.

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

**Extending `claude-plugin-dev` to cover hybrid repos** — reverses that
project's documented non-goal, and by its own reasoning the conditionals needed
would obscure its main path or break edify outright (D-87).

**Un-hybridising edify so the toolkit fits** — the single-manifest model would
apply if the plugin were published as its own thing again, which is exactly what
D-10 undid (D-87).

**Adopting the toolkit on the grounds that its exclusion predates the merge** —
the exclusion stands in that project's current record, so adopting anyway is
edify deciding another project's scope for it. It is D-87's reopen gate, not a
route around it.

**A JSON file as a general key-value store** — the existing models cache is a
special case (bounded, ~50 entries, TTL-refreshed); extending it to unbounded
append-heavy caches cargo-cults the storage choice. sqlite via sqlalchemy is the
answer for persistent caches: stdlib sqlite3 handles concurrent access, mapped
classes match the Pydantic convention.
