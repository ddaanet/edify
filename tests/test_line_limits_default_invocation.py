"""Coverage for the invocation form production actually uses.

`justfile` and `plugin/portable.just` both run
`./scripts/check_line_limits.sh` with **no arguments at all** — `ROOT`
defaults to `.` and `ALLOWLIST_EXPLICIT` stays `0`, taking the
default-sidecar branch at `scripts/check_line_limits.sh:63-65`. Every test
in `tests/test_line_limits.py` and `tests/test_line_limits_exit_codes.py`
passes `--allowlist` explicitly (the F-2 fix), which is correct for those
tests' own fixtures but leaves the form production always uses with no
cover at all. A separate module because these tests need a relocated copy
of the script (so `SCRIPT_DIR` resolves somewhere the test controls) and a
plain `cwd=root` invocation, neither of which any other module needs.
"""

import shutil
from pathlib import Path

from .line_limits_helpers import (
    SCRIPT,
    _run_check_line_limits,
    _write_allowlist,
    _write_lines,
)


def _copy_script(bin_dir: Path) -> Path:
    """Copy ``check_line_limits.sh`` into ``bin_dir``, preserving mode 0755.

    ``SCRIPT_DIR`` (``scripts/check_line_limits.sh:34``) is derived from
    ``BASH_SOURCE[0]``, so only relocating the script itself moves where its
    default sidecar (``$SCRIPT_DIR/check_line_limits.allow``) resolves.
    """
    bin_dir.mkdir(parents=True, exist_ok=True)
    script_copy = bin_dir / "check_line_limits.sh"
    shutil.copy2(SCRIPT, script_copy)
    script_copy.chmod(0o755)
    return script_copy


def test_line_limits_default_sidecar_applies_its_ceiling(tmp_path: Path) -> None:
    """A relocated copy's own sidecar ceiling suppresses the fail, not the cap.

    A sidecar `check_line_limits.allow` sits beside the copy, recording a
    ceiling equal to the fixture file's line count. Run with no
    `--allowlist` at all (`allowlist="default"`): the file is still over the
    path-picked cap and is reported, but the sidecar's ceiling means it does
    not fail the run.
    """
    bin_dir = tmp_path / "bin"
    script_copy = _copy_script(bin_dir)
    _write_allowlist(
        bin_dir / "check_line_limits.allow",
        [("docs/notes.md", 401, "no job yet")],
    )
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 401)

    result = _run_check_line_limits(root, allowlist="default", script=script_copy)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/notes.md: 401 lines > 400"
    ], result.stdout


def test_line_limits_default_sidecar_missing_is_empty_allowlist(
    tmp_path: Path,
) -> None:
    """A relocated copy with no sidecar beside it fails on any overage.

    `scripts/check_line_limits.sh:21-22` documents "a missing default allowlist
    file means an empty allowlist" — the `-f` guard at `:74`. No sidecar is
    written next to the copy here, so the over-cap file must fail the run
    exactly as it would with an explicit empty allowlist.
    """
    bin_dir = tmp_path / "bin"
    script_copy = _copy_script(bin_dir)
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 401)

    result = _run_check_line_limits(root, allowlist="default", script=script_copy)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/notes.md: 401 lines > 400"
    ], result.stdout


def test_line_limits_root_defaults_to_cwd_when_omitted(tmp_path: Path) -> None:
    """`ROOT` defaults to `.` when no positional argument is given.

    Production invokes the script bare — no `ROOT`, no `--allowlist`. This
    pins the `ROOT="."` default (`scripts/check_line_limits.sh:35`) in
    isolation from the default-sidecar question above: an explicit empty
    allowlist still applies (`allowlist=None`, the ordinary default), only
    the `ROOT` positional is omitted and `cwd` stands in for it.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 401)

    result = _run_check_line_limits(root, omit_root=True)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/notes.md: 401 lines > 400"
    ], result.stdout
