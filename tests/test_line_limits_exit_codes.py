"""Exit-code precedence for ``scripts/check_line_limits.sh``.

KD-7 (Item 1.10) pins "exit 2 outranks exit 1": a run carrying both an
over-cap file (the exit-1 condition) and a failure to run the check (an
exit-2 condition — an unreadable file or a directory ``find`` cannot walk)
must exit 2, never 1. Split from ``tests/test_line_limits.py`` to keep that
module under its line cap; shared fixtures live in
``tests/line_limits_helpers.py``.

Both conditions here have a deterministic order: the script walks
``plugin`` to completion before it starts ``docs`` (``for dir in plugin
docs``), so putting the exit-2 condition under ``plugin`` and the oversized
file under ``docs`` guarantees the script reaches the exit-2 site first —
regardless of ``find``'s own (unspecified) entry order within a directory.
The two ``exit 2`` sites the precedence tests pin are the only ones that can
be reached after ``check_cap`` has already run at least once: every other
exit-2 site (bad ``--allowlist`` argument, unknown option, a second
positional ``ROOT``, malformed or CRLF allowlist entry, a failed
``mktemp``) fires during argument or allowlist parsing, strictly before the
first ``check_cap`` call, so none of them can co-occur with an already-set
``EXIT_CODE=1``.

``test_two_positional_roots_exits_2_with_usage_diagnostic`` is one of those
parse-time sites rather than a precedence test, and sits here only because
``tests/test_line_limits.py``, its natural home, has no room left under its
line cap.
"""

import os
from pathlib import Path

import pytest

from .line_limits_helpers import _run_check_line_limits, _write_lines


def test_unreadable_file_outranks_a_later_overage(tmp_path: Path) -> None:
    """An unreadable file under ``plugin`` beats a later overage under ``docs``.

    ``plugin/locked.md`` is chmod 0000: ``check_cap`` cannot ``wc -l`` it and
    exits 2 mid-walk, before the script ever starts the ``docs`` walk that
    holds the 401-line ``over.md``. The oversized file must never be
    reported — its stage is never reached.
    """
    if os.geteuid() == 0:
        pytest.skip("root ignores file permissions; chmod 0000 has no effect")

    root = tmp_path / "root"
    locked = root / "plugin" / "locked.md"
    _write_lines(locked, 5)
    _write_lines(root / "docs" / "over.md", 401)
    locked.chmod(0o000)
    try:
        result = _run_check_line_limits(root)
    finally:
        locked.chmod(0o644)

    assert result.returncode == 2, result.stdout + result.stderr
    assert "oversized-file:" not in result.stdout, result.stdout


def test_two_positional_roots_exits_2_with_usage_diagnostic(tmp_path: Path) -> None:
    """A second positional `ROOT` is a usage error, not a silent second root.

    `scripts/check_line_limits.sh:56-59`'s `*)` arm assigns `ROOT="$1"`
    unconditionally on every non-flag argument, so a second positional
    silently overwrites the first: the run proceeds against the *second*
    root and walks straight past the 401-line file waiting under the first,
    exiting 0 with no diagnostic at all. Usage at `:4` is
    `[--allowlist FILE] [ROOT]` — one optional `ROOT` — so a second
    positional must instead be rejected with a usage diagnostic on stderr
    and exit 2, the treatment the `-*)` arm just above (`:52-55`) already
    gives an unrecognised flag.

    The 401-line file under the *first* root is what makes the three
    outcomes distinguishable: exit 0 means the script silently walked the
    second root, exit 1 means it walked the first, exit 2 means it rejected
    the invocation without walking either.
    """
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    _write_lines(root_a / "docs" / "over.md", 401)
    root_b.mkdir(parents=True, exist_ok=True)

    result = _run_check_line_limits(root_a, second_root=root_b)

    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stderr.strip() != "", "expected a usage diagnostic on stderr"
    assert "oversized-file:" not in result.stdout, result.stdout


def test_walk_failure_outranks_a_later_overage(tmp_path: Path) -> None:
    """A ``find``-unreadable directory under ``plugin`` beats a later overage.

    ``plugin/locked/`` is chmod 0000: ``find`` fails walking it and the
    script exits 2 before it ever starts the ``docs`` walk that holds the
    401-line ``over.md``. The oversized file must never be reported.
    """
    if os.geteuid() == 0:
        pytest.skip("root ignores directory permissions; chmod 0000 has no effect")

    root = tmp_path / "root"
    locked_dir = root / "plugin" / "locked"
    _write_lines(locked_dir / "hidden.md", 401)
    _write_lines(root / "docs" / "over.md", 401)
    locked_dir.chmod(0o000)
    try:
        result = _run_check_line_limits(root)
    finally:
        locked_dir.chmod(0o700)

    assert result.returncode == 2, result.stdout + result.stderr
    assert "oversized-file:" not in result.stdout, result.stdout
