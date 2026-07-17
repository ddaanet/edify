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
(`ddaanet/edify-plugin`) was archived. The runtime bootstrap below (SessionStart
venv hook, PyPI publish, marketplace `git-subdir` entry) is designed here but
**not yet implemented**.

## Plugin obtains the CLI via a SessionStart-built stdlib venv, pinned from PyPI

**Decision Date:** 2026-07-16

**Decision:** The plugin ships a `SessionStart` hook that builds a Python
virtual environment and installs `edify-cli` from PyPI at a version pinned to
the plugin's own version. The venv is built with the **standard library only**
(`python3 -m venv` + `pip`), never `uv`.

**Options considered:**
- A) Co-located source — plugin runs the CLI from the `src/` tree in the same
  repo. Impossible: subdir install does not copy sibling source into the cache.
- B) Require a separate global install (`uv tool install edify-cli`) as a
  documented prerequisite. Works but couples the plugin to an out-of-band manual
  step and to `uv` being present.
- C) Plugin self-bootstraps a venv at `SessionStart` and installs
  `edify-cli==<version>` from PyPI, using stdlib tooling only.

**Chosen:** C.

**Rationale:**
- The tree does not deliver the *code* to the plugin (A is impossible), but it
  delivers the *version pin*: `check-version-consistency.py` locks
  `plugin.json` version == `pyproject.toml` version, so the hook can install the
  exact matching `edify-cli==<plugin version>` with no drift.
- stdlib-only (not `uv`) because the bootstrap must run on any host with a
  suitable `python3`; it cannot assume `uv` is installed.

**Constraints this imposes:**
- **Publish ordering is hard:** `edify-cli` must be on PyPI *before* the plugin
  version that pins it. A plugin version can never lead its package.
- **Host Python floor:** `edify-cli` requires Python ≥3.14. A stdlib venv
  inherits the creating interpreter, so the host `python3` must already be
  ≥3.14 — the bootstrap cannot install a newer interpreter (as `uv` could). The
  hook version-checks and fails loudly if too old.
- **ensurepip must be present:** Debian/Ubuntu split it into a `python3-venv`
  apt package; a bare `python3 -m venv` fails there. The hook fails with a clear
  "install python3-venv" message rather than silently.
- This reintroduces one `SessionStart` hook after the 2026-07-16 hook retirement
  — a load-bearing bootstrap, unrelated to the retired autoformat/block-tmp
  hooks. (See [[plugin-transition-eval]].)

**Dev/test (decided 2026-07-17): local index first, never a PyPI push for
dogfooding.** The bootstrap installs from a *package index*, not from PyPI
specifically. To develop and test the hook, build the wheel locally and point
pip at it (`pip install --find-links=<dist-dir> edify-cli==<version>`), prove the
whole bootstrap green offline, then publish to real PyPI and drop the
`--find-links`. The publish-ordering constraint binds *releases*, not
development — never cut a throwaway public version just to exercise the
bootstrap. (General rule, not edify-specific: local dogfooding must never require
a registry publish.)

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

## Implementation sketch (not yet created)

`plugin/hooks/hooks.json`:
```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/bin/bootstrap-venv.sh\"" } ] }
    ]
  }
}
```

`plugin/bin/bootstrap-venv.sh` (stdlib-only, fail-loud, idempotent):
```sh
#!/bin/sh
set -eu

VERSION=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
  "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json")
VENV="${CLAUDE_PLUGIN_DATA}/venv-${VERSION}"

# Fast path: matching venv already built.
[ -x "${VENV}/bin/edify" ] && exit 0

# Prune stale version venvs.
for d in "${CLAUDE_PLUGIN_DATA}"/venv-*; do
  [ -e "$d" ] || continue
  [ "$d" = "$VENV" ] || rm -rf "$d"
done

# Enforce the edify-cli interpreter floor (>= 3.14).
python3 - <<'PY' || { echo "edify plugin: needs python3 >= 3.14 on PATH" >&2; exit 2; }
import sys
sys.exit(0 if sys.version_info >= (3, 14) else 1)
PY

# Build with stdlib only (ensurepip required; Debian: python3-venv).
python3 -m venv "$VENV" \
  || { echo "edify plugin: 'python3 -m venv' failed — install python3-venv (ensurepip)" >&2; exit 2; }
"${VENV}/bin/python" -m pip install --quiet --upgrade pip
"${VENV}/bin/python" -m pip install --quiet "edify-cli==${VERSION}" \
  || { echo "edify plugin: pip install edify-cli==${VERSION} failed" >&2; exit 2; }

# Stable path for skills (pending the open-question verification above).
ln -sfn "$VENV" "${CLAUDE_PLUGIN_DATA}/current"
```

`exit 2` surfaces the message as a non-blocking hook-error notice; SessionStart
does not block the session on it.
