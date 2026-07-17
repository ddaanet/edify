#!/bin/sh
# SessionStart bootstrap: provision a venv holding the version-matched edify-cli,
# using uv.
#
# uv (not a stdlib `python3 -m venv`) so the venv gets a Python >=3.14
# interpreter even when the host python3 is older — uv fetches a suitable one.
# The trade-off is a uv runtime dependency; when uv is absent the hook degrades
# gracefully with an informative message rather than a broken environment.
#
# The venv lives at ${CLAUDE_PLUGIN_DATA}/venv-<version>/ — version-scoped by
# path, so an absent directory is itself the rebuild signal. A `current` symlink
# points at the active venv, giving skills a version-independent path.
#
# Local dogfooding needs no registry push: uv installs from an *index*, not from
# PyPI specifically. Point uv at a locally built wheel with UV_FIND_LINKS /
# UV_INDEX (or --find-links) for dev; production resolves from PyPI.
#
# On any bootstrap failure this prints SessionStart JSON (systemMessage for the
# user, additionalContext for Claude) and exits 0, so the session is never
# blocked — edify is simply reported as unavailable until the cause is fixed.
set -eu

# Emit SessionStart "edify unavailable" JSON. $1 = user-facing warning,
# $2 = Claude-facing context. Both are controlled literals (no embedded " \ or
# %), so no JSON escaping is needed.
emit_unavailable() {
  printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' \
    "$1" "$2"
}

PLUGIN_JSON="${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"
VERSION=$(sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$PLUGIN_JSON")
[ -n "$VERSION" ] || { echo "edify plugin: no version in $PLUGIN_JSON" >&2; exit 2; }

VENV="${CLAUDE_PLUGIN_DATA}/venv-${VERSION}"

# Fast path: the matching venv is already built (uv not even needed).
[ -x "${VENV}/bin/edify" ] && exit 0

# uv is required to build — it provisions the >=3.14 interpreter.
if ! command -v uv >/dev/null 2>&1; then
  emit_unavailable \
    "edify-cli is unavailable this session: the uv package manager is not installed. Install uv (https://docs.astral.sh/uv/) and restart the session to enable edify commands." \
    "edify-cli was not installed because uv (its bootstrapper) is missing from PATH. The edify skills (proof, ground, formalize, requirements, deliverable-review) and CLI (tokens, markdown, check) will not work until uv is installed and a session is restarted."
  exit 0
fi

# Prune stale version venvs (and any half-built current-version dir).
for d in "${CLAUDE_PLUGIN_DATA}"/venv-*; do
  [ -e "$d" ] || continue
  rm -rf "$d"
done

# Build. uv provisions a >=3.14 interpreter even if the host python3 is older;
# uv's own diagnostics go to stderr (visible), stdout is muted to keep this
# hook's stdout pure JSON.
if ! uv venv --python '>=3.14' "$VENV" >/dev/null; then
  emit_unavailable \
    "edify-cli is unavailable this session: uv could not create a Python >=3.14 environment." \
    "uv venv --python '>=3.14' failed while bootstrapping edify-cli; edify commands will not work this session. See the hook's stderr for uv's diagnostics."
  exit 0
fi

# Install the pinned CLI from the configured index (UV_FIND_LINKS / UV_INDEX for
# a local wheel in dev; PyPI in production).
if ! uv pip install --python "${VENV}/bin/python" "edify-cli==${VERSION}" >/dev/null; then
  emit_unavailable \
    "edify-cli is unavailable this session: installing edify-cli==${VERSION} failed." \
    "uv pip install edify-cli==${VERSION} failed (network, index, or version availability); edify commands will not work this session. See the hook's stderr for uv's diagnostics."
  rm -rf "$VENV"
  exit 0
fi

# Stable, version-independent path for skills to invoke.
ln -sfn "$VENV" "${CLAUDE_PLUGIN_DATA}/current"
