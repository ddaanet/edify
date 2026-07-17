# Plugin Packaging

How the `edify` Claude Code plugin and the `edify-cli` PyPI package share one
git tree, and how the plugin obtains the CLI it depends on at runtime.

## De-submodule the plugin into a subdirectory of the package repo

**Decision Date:** 2026-07-16

**Decision:** One git tree. The repo root *is* the `edify-cli` PyPI package
(`pyproject.toml` at root, source in `src/edify/`). It carries the Claude Code
plugin as a plain tracked subdirectory `plugin/` (holding
`.claude-plugin/plugin.json`, `skills/`, `fragments/`, `bin/`). `plugin/` stops
being a git submodule.

**Options considered:**
- A) Keep `plugin/` as a submodule (status quo) — separate `ddaanet/edify-plugin`
  repo, gitlink in the parent.
- B) Merge the plugin *up to the repo root* — one root serving as both package
  and plugin.
- C) De-submodule `plugin/` into a plain subdirectory of the package repo,
  keeping it as the plugin root.

**Chosen:** C.

**Rationale:**
- A ships a live defect: a parent repo cannot `git add` inside a submodule, so
  `git add plugin/.claude-plugin/plugin.json` fails ("Pathspec is in submodule")
  and `just release` cannot complete a real release. C removes the boundary and
  fixes this directly. (See [[plugin-transition-eval]].)
- A also carries permanent gitlink-drift overhead (bump/sync the plugin gitlink
  on every plugin change). C eliminates it — one fewer submodule. The `memory`
  submodule is unaffected (it is the gitlore-gated one and stays).
- B was rejected because it would force the plugin to carry the inert `src/`
  tree as *its own* content. A subdir-sourced plugin install copies **only** the
  plugin's directory into the cache — never sibling files
  (`plugins-reference.md`, "Path traversal limitations"). Keeping `plugin/` as
  the plugin root means the plugin's content is exactly `plugin/`; `src/` stays
  out of the plugin footprint.
- `check-version-consistency.py` needs **no** change under C: it computes
  `repo_root = __file__.parent.parent.parent` then `repo_root / "plugin" / ...`;
  `plugin/` stays a subdir at the same depth, so both paths still resolve. (The
  eval's "needs a path rewrite" assumed B.)

**Marketplace sourcing:** `git-subdir` source pointing at `plugin/`:
```json
{ "name": "edify",
  "source": { "source": "git-subdir", "url": "https://github.com/<owner>/edify-cli.git", "path": "plugin" } }
```
Claude Code does a sparse partial clone of only `path`; the rest of the repo is
not fetched into the cache.

**Status:** De-submodule **executed 2026-07-16** (commit `c3c4477f`). The
`plugin` submodule's unpushed commits were absorbed via the flatten (content is
a blob-for-blob match with its old HEAD `c7cbaaf`), and its GitHub repo
(`ddaanet/edify-plugin`) was archived. The **SessionStart venv hook is
implemented** (2026-07-17): `plugin/bin/bootstrap-venv.sh` + `plugin/hooks/
hooks.json`, covered by `tests/bootstrap-venv.bats` (run from pytest via
`tests/test_bootstrap_hook.py`). Still pending: the PyPI publish and the
marketplace `git-subdir` entry.

## Plugin obtains the CLI via a SessionStart uv-built venv, pinned from an index

**Decision Date:** 2026-07-16 (stdlib) — **revised 2026-07-17 to use uv.**

**Decision:** The plugin ships a `SessionStart` hook that uses **uv** to build a
venv and install `edify-cli` at a version pinned to the plugin's own version. uv
provisions a Python **≥3.14** interpreter for the venv even when the host
`python3` is older. When uv is absent the hook degrades gracefully — it emits a
SessionStart `systemMessage` (user-facing) and `additionalContext`
(Claude-facing) reporting that edify-cli is unavailable, and exits 0 without
blocking the session.

**Options considered:**
- A) Co-located source — plugin runs the CLI from the `src/` tree in the same
  repo. Impossible: subdir install does not copy sibling source into the cache.
- B) Require a separate global install (`uv tool install edify-cli`) as a
  documented prerequisite. Works but couples the plugin to an out-of-band manual
  step.
- C) Self-bootstrap a **stdlib** venv (`python3 -m venv` + pip), never uv.
- D) Self-bootstrap a venv with **uv** at `SessionStart`, installing
  `edify-cli==<version>` from an index.

**Chosen:** D. (C was the 2026-07-16 choice; reversed — see below.)

**Rationale:**
- The tree does not deliver the *code* to the plugin (A impossible), but it
  delivers the *version pin*: `check-version-consistency.py` locks
  `plugin.json` version == `pyproject.toml` version, so the hook installs the
  exact matching `edify-cli==<plugin version>` with no drift.
- **Why uv over stdlib (the reversal):** a stdlib venv inherits the host
  interpreter, so C required the host `python3` to already be ≥3.14 and failed
  loudly otherwise — unshippable on the many hosts still on 3.13. uv *fetches* a
  ≥3.14 interpreter itself (`uv venv --python '>=3.14'`), removing the host floor
  entirely. The price is a uv runtime dependency, paid down by graceful,
  informative degradation when uv is missing rather than a hard failure.

**Constraints this imposes:**
- **Publish ordering is hard:** `edify-cli` must be on the index *before* the
  plugin version that pins it. A plugin version can never lead its package.
- **uv is a runtime dependency:** the host must have `uv` on PATH. Absent uv,
  edify-cli is unavailable that session and the hook says so (`systemMessage` +
  `additionalContext`), exit 0 — the session is not blocked.
- This reintroduces one `SessionStart` hook after the 2026-07-16 hook retirement
  — a load-bearing bootstrap, unrelated to the retired autoformat/block-tmp
  hooks. (See [[plugin-transition-eval]].)

**Dissolved by the uv switch:** the stdlib design's **host Python ≥3.14 floor**
and its **ensurepip / `python3-venv` requirement** both vanish — uv provisions
the interpreter and needs no host ensurepip.

**Dev/test (decided 2026-07-17): local index first, never a registry push for
dogfooding.** The bootstrap installs from a *package index*, not from PyPI
specifically. To develop and test the hook, build the wheel locally and point uv
at it (`UV_FIND_LINKS=<dist-dir>` / `--find-links`, or `UV_INDEX`), prove the
whole bootstrap green offline, then publish to real PyPI and drop the override.
The publish-ordering constraint binds *releases*, not development — never cut a
throwaway public version just to exercise the bootstrap. (General rule, not
edify-specific: local dogfooding must never require a registry publish.)

## venv lives in `CLAUDE_PLUGIN_DATA`, version-scoped by path

**Decision Date:** 2026-07-16

**Decision:** Build the venv at `${CLAUDE_PLUGIN_DATA}/venv-<version>/`. On a
version change the path changes, so an absent directory *is* the rebuild signal;
the hook prunes non-matching `venv-*` siblings when it builds.

**Options considered:**
- A) `${CLAUDE_PLUGIN_ROOT}/.venv` — ROOT is already version-scoped (fresh dir
  per plugin version) and auto-GC'd (~7 days), giving automatic
  invalidation-on-bump and cleanup for free, with zero state management.
- B) `${CLAUDE_PLUGIN_DATA}/venv-<version>/` — DATA is the documented,
  guaranteed-writable persistent location; version-scope the *path* to
  reproduce A's automatic invalidation; prune stale siblings manually.

**Chosen:** B.

**Rationale:**
- A's semantics are more elegant, but ROOT writability at hook time is
  **unverifiable** from the docs. The docs say "treat as ephemeral, don't write
  state there" — prescriptive (updates replace the dir), *not* a documented
  read-only mount — and provide no evidence writes into ROOT persist across a
  session. (Guide research, 2026-07-16.)
- The venv is **expensive** to build: `edify-cli` → CrossHair → z3, tens of
  seconds of network + install. If A's persistence assumption is wrong, the
  failure is silent and manifests as a full z3 reinstall at *every*
  SessionStart. That cost asymmetry — B's ~2 lines of sibling pruning vs. A's
  risk of a slow rebuild every session — decides it.
- B keeps the property that motivated A: version in the *pathname* is the
  invalidation. No stamp file, no content-diff check — an absent versioned dir
  triggers the rebuild. Automatic invalidation without an explicit invalidation
  mechanism.

**Note:** ROOT (A) remains a legitimate optimization if empirically validated —
one throwaway test (write a file into ROOT at SessionStart, confirm it survives
to the next tool call). Absent that test, B is the committed choice.

## Skills reference the venv binary via content substitution

**Decision Date:** 2026-07-16

**Resolved.** Skill and agent markdown support `${CLAUDE_PLUGIN_ROOT}` /
`${CLAUDE_PLUGIN_DATA}` placeholder substitution in their *content*
(plugins-reference.md env-var table: "Skill and agent content — anywhere the
placeholder appears"). Claude Code replaces the placeholder with a concrete
absolute path in the instructions the agent reads; the agent then runs that path
via Bash. So skills invoke `${CLAUDE_PLUGIN_DATA}/current/bin/edify`, where the
bootstrap maintains the `current` symlink → the active `venv-<version>` — a
version-independent path for skills, versioned dirs underneath.

**Substitution, not a live env var.** The docs export
`${CLAUDE_PLUGIN_ROOT}`/`${CLAUDE_PLUGIN_DATA}` as environment variables only to
hook / MCP / LSP subprocesses — *not* documented for Bash-tool subprocesses. So
skills must rely on content substitution (placeholder replaced in the markdown
text), not on `$VAR` being live in the agent's shell.

**No hardcoded-path fallback (decided 2026-07-17).** If `${CLAUDE_PLUGIN_DATA}`
proves not to substitute in skill content, the fix is *not* a literal
`~/.claude/plugins/data/edify-<marketplace>/…` path baked into skills. A
fallback path is exercised rarely, so its path *format* can drift (id-encoding
or layout changes) and rot silently — failing exactly when the primary
mechanism is already unavailable. The resolution is a proper substitutable
mechanism decided then — e.g. moving the venv under `${CLAUDE_PLUGIN_ROOT}`,
which *is* confirmed to substitute (the ROOT option above; itself gated on the
ROOT-persistence check) — never a hardcoded literal.

**One empirical confirmation pending:** that `${CLAUDE_PLUGIN_DATA}` (not just
`ROOT`) substitutes in skill content — a one-line throwaway skill echoing the
placeholder confirms it. This is now a real gate (it selects the venv-location
resolution above), not merely a preference between placeholder and literal.

## Implementation (2026-07-17)

Built and covered by hermetic tests — see the source rather than duplicating it
here:
- `plugin/hooks/hooks.json` — a `SessionStart` command hook running
  `"${CLAUDE_PLUGIN_ROOT}/bin/bootstrap-venv.sh"` (300 s timeout).
- `plugin/bin/bootstrap-venv.sh` — POSIX sh, shellcheck-clean. Parses the pinned
  version from `plugin.json`; fast-path exits if `venv-<version>/bin/edify`
  exists; else prunes stale `venv-*`, then `uv venv --python '>=3.14'` +
  `uv pip install edify-cli==<version>`, then links `current`. Any bootstrap
  failure — uv missing, venv build, install — emits SessionStart JSON
  (`systemMessage` for the user + `hookSpecificOutput.additionalContext` for
  Claude) and exits 0, so the session is never blocked; a missing version in
  `plugin.json` is a packaging defect and exits 2.
- `tests/bootstrap-venv.bats` — stubs `uv` on PATH to exercise the control logic
  offline (fast-path, uv-missing, prune, happy path, venv/install failure,
  missing-version), run from pytest via `tests/test_bootstrap_hook.py`; `bats`
  is a declared npm dev dependency.

**Unverified end-to-end:** the real uv build + `edify-cli` install has not been
run against a published package (edify-cli is not on PyPI yet). Drive it on a
host with uv once a wheel exists:
`UV_FIND_LINKS=<dist> CLAUDE_PLUGIN_ROOT=… CLAUDE_PLUGIN_DATA=… plugin/bin/bootstrap-venv.sh`.
