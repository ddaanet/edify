#!/usr/bin/env bats
# Hermetic tests for plugin/bin/bootstrap-venv.sh.
#
# The bootstrap's real work (uv provisions a >=3.14 venv, uv installs edify-cli
# from an index) needs network and a published package, so these tests stub `uv`
# on PATH to exercise the script's control logic offline: version parse,
# fast-path idempotency, stale-version pruning, graceful degradation when uv is
# missing / venv fails / install fails, and the happy path down to the `current`
# symlink. The uv stub logs its argv so tests can assert the script's contract
# (it requests `--python >=3.14` and the version-pinned edify-cli). Stub shape
# follows shell-gotchas' "lock it in with a PATH stub" pattern.

bats_require_minimum_version 1.5.0

setup() {
  REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/.." && pwd)"
  SCRIPT="$REPO_ROOT/plugin/bin/bootstrap-venv.sh"
  export CLAUDE_PLUGIN_ROOT="$BATS_TEST_TMPDIR/root"
  export CLAUDE_PLUGIN_DATA="$BATS_TEST_TMPDIR/data"
  STUBBIN="$BATS_TEST_TMPDIR/stubbin"
  export UVLOG="$BATS_TEST_TMPDIR/uv.log"
  mkdir -p "$CLAUDE_PLUGIN_ROOT/.claude-plugin" "$CLAUDE_PLUGIN_DATA" "$STUBBIN"
  printf '%s\n' '{ "name": "edify", "version": "9.9.9" }' \
    > "$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json"
}

# Install a `uv` stub. Arg $1 controls the pip step: "ok" installs (creates
# bin/edify), "fail-install" makes `uv pip install` exit 1, "fail-venv" makes
# `uv venv` exit 1. The stub logs its full argv to $UVLOG.
stub_uv() {
  behavior="${1:-ok}"
  cat > "$STUBBIN/uv" <<EOF
#!/bin/sh
echo "\$@" >> "$UVLOG"
behavior="$behavior"
sub="\$1"; shift
case "\$sub" in
  venv)
    [ "\$behavior" = fail-venv ] && exit 1
    dir=""
    while [ \$# -gt 0 ]; do
      case "\$1" in --python) shift ;; --*) ;; *) dir="\$1" ;; esac
      shift
    done
    mkdir -p "\$dir/bin"; : > "\$dir/bin/python"; chmod 755 "\$dir/bin/python"
    ;;
  pip)
    [ "\$behavior" = fail-install ] && exit 1
    py=""; want=0
    while [ \$# -gt 0 ]; do
      case "\$1" in --python) shift; py="\$1" ;; edify-cli==*) want=1 ;; esac
      shift
    done
    if [ "\$want" = 1 ] && [ -n "\$py" ]; then
      d=\$(CDPATH= cd "\$(dirname "\$py")" && pwd)
      printf '#!/bin/sh\necho "edify (stub)"\n' > "\$d/edify"; chmod 755 "\$d/edify"
    fi
    ;;
esac
exit 0
EOF
  chmod 755 "$STUBBIN/uv"
}

@test "fast path: an existing venv/bin/edify exits 0 and never calls uv" {
  mkdir -p "$CLAUDE_PLUGIN_DATA/venv-9.9.9/bin"
  printf '#!/bin/sh\n' > "$CLAUDE_PLUGIN_DATA/venv-9.9.9/bin/edify"
  chmod 755 "$CLAUDE_PLUGIN_DATA/venv-9.9.9/bin/edify"
  stub_uv ok
  PATH="$STUBBIN:$PATH" run sh "$SCRIPT"
  [ "$status" -eq 0 ]
  [ ! -e "$UVLOG" ]
}

@test "uv missing: exits 0 with a user warning and Claude context, builds nothing" {
  # A PATH without uv (and without the stub) simulates uv absent.
  PATH="/usr/bin:/bin" run --separate-stderr sh "$SCRIPT"
  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.hookSpecificOutput.hookEventName == "SessionStart"'
  echo "$output" | jq -e '.systemMessage | test("uv")'
  echo "$output" | jq -e '.hookSpecificOutput.additionalContext | test("uv")'
  [ ! -e "$CLAUDE_PLUGIN_DATA/venv-9.9.9" ]
}

@test "happy path: builds venv, installs pinned edify-cli, links current" {
  stub_uv ok
  PATH="$STUBBIN:$PATH" run sh "$SCRIPT"
  [ "$status" -eq 0 ]
  [ -x "$CLAUDE_PLUGIN_DATA/venv-9.9.9/bin/edify" ]
  [ -L "$CLAUDE_PLUGIN_DATA/current" ]
  [ "$(readlink "$CLAUDE_PLUGIN_DATA/current")" = "$CLAUDE_PLUGIN_DATA/venv-9.9.9" ]
  # The script must request a >=3.14 interpreter and the version-pinned CLI.
  grep -q -- "--python >=3.14" "$UVLOG"
  grep -q -- "edify-cli==9.9.9" "$UVLOG"
}

@test "prune: a stale version venv is removed before the new one is built" {
  mkdir -p "$CLAUDE_PLUGIN_DATA/venv-1.0.0/bin"
  stub_uv ok
  PATH="$STUBBIN:$PATH" run sh "$SCRIPT"
  [ "$status" -eq 0 ]
  [ ! -e "$CLAUDE_PLUGIN_DATA/venv-1.0.0" ]
  [ -x "$CLAUDE_PLUGIN_DATA/venv-9.9.9/bin/edify" ]
}

@test "venv failure: exits 0 with the unavailable message, no current symlink" {
  stub_uv fail-venv
  PATH="$STUBBIN:$PATH" run --separate-stderr sh "$SCRIPT"
  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.systemMessage | test("unavailable")'
  [ ! -e "$CLAUDE_PLUGIN_DATA/current" ]
  [ ! -x "$CLAUDE_PLUGIN_DATA/venv-9.9.9/bin/edify" ]
}

@test "install failure: exits 0, reports unavailable, removes the half-built venv" {
  stub_uv fail-install
  PATH="$STUBBIN:$PATH" run --separate-stderr sh "$SCRIPT"
  [ "$status" -eq 0 ]
  echo "$output" | jq -e '.systemMessage | test("unavailable")'
  [ ! -e "$CLAUDE_PLUGIN_DATA/venv-9.9.9" ]
  [ ! -e "$CLAUDE_PLUGIN_DATA/current" ]
}

@test "missing version in plugin.json: exits 2 before touching uv" {
  printf '%s\n' '{ "name": "edify" }' \
    > "$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json"
  stub_uv ok
  PATH="$STUBBIN:$PATH" run sh "$SCRIPT"
  [ "$status" -eq 2 ]
  [[ "$output" == *"no version"* ]]
  [ ! -e "$UVLOG" ]
}
