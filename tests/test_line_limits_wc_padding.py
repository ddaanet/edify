"""Regression test for F-1: `check_line_limits.sh`'s unguarded `wc -l`.

`scripts/check_line_limits.sh:124` feeds `wc -l`'s output straight into the
`oversized-file:` line with no `tr -d ' '` guard, unlike the two counts in
`plugin/bin/triage-feedback.sh` that reach output (the changed-files count,
`wc -l`, and the committed-report count, `wc -c`), which each pipe through
`tr -d ' '`. The script's remaining `wc -l`, counting `review-*.md` files,
feeds only a numeric `-eq` test, where padding is harmless. BSD/macOS `wc`
left-pads a bare count into a fixed-width field; GNU `wc` reading stdin (the
call shape at `:124`) does not. This module shims `wc` on `PATH` to reproduce
the BSD form on this (Linux) box and pins the exact unpadded line KD-7
requires regardless of which `wc` ran. It is red on unchanged code — on its
stdout assertion, not on a shim, import or fixture error — and is expected to
stay red until the GREEN half of this fix adds the guard.
"""

from pathlib import Path

from .line_limits_helpers import (
    _run_check_line_limits,
    _write_lines,
    _write_padded_wc_shim,
)


def test_line_limits_reports_unpadded_count_under_bsd_style_wc(
    tmp_path: Path,
) -> None:
    """The `oversized-file:` line carries an unpadded count under BSD `wc`."""
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 401)
    bin_dir = tmp_path / "bin"
    _write_padded_wc_shim(bin_dir)

    result = _run_check_line_limits(root, path_prepend=bin_dir)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/notes.md: 401 lines > 400"
    ], result.stdout
