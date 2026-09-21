"""Contract tests for ``scripts/check_line_limits.sh``.

KD-7 in ``plans/provenance-enforcement-and-routing/outline.md`` (Item 1.10).
Each test builds a throwaway fixture tree under ``tmp_path`` and runs the
script by absolute path with ``[ROOT]`` = that tree, ``cwd=tmp_path`` (never
the checkout — the script must honour ``ROOT`` rather than walking the repo
it happens to run from).
"""

import os
from pathlib import Path

import pytest

from .line_limits_helpers import _run_check_line_limits, _write_allowlist, _write_lines


def test_line_limits_passes_clean_tree(tmp_path: Path) -> None:
    """A clean tree of small files exits 0 with no ``oversized-file:`` line."""
    root = tmp_path / "root"
    _write_lines(root / "plugin" / "skills" / "x" / "SKILL.md", 10)
    _write_lines(root / "docs" / "notes.md", 10)

    result = _run_check_line_limits(root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "oversized-file:" not in result.stdout, result.stdout


def test_line_limits_fails_markdown_over_400(tmp_path: Path) -> None:
    """A 401-line non-``SKILL.md`` markdown file exits 1 naming the overage.

    The reported path is root-relative (``docs/notes.md``, not an absolute
    path) — that is what a reader of ``just precommit`` output needs, since
    an absolute path would vary by checkout location.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 401)

    result = _run_check_line_limits(root)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/notes.md: 401 lines > 400"
    ], result.stdout


def test_line_limits_fails_skill_hub_over_200(tmp_path: Path) -> None:
    """The cap is path-picked: 200 for ``SKILL.md``, 400 for a sibling.

    Two separate trees, since a single tree holding both fixtures would
    exit 1 regardless of the sibling's own cap — the second half asserts
    exit 0 for the sibling in isolation.
    """
    skill_root = tmp_path / "skill_root"
    _write_lines(skill_root / "plugin" / "skills" / "x" / "SKILL.md", 201)

    skill_result = _run_check_line_limits(skill_root)

    assert skill_result.returncode == 1, skill_result.stdout + skill_result.stderr
    assert skill_result.stdout.splitlines() == [
        "oversized-file: plugin/skills/x/SKILL.md: 201 lines > 200"
    ], skill_result.stdout

    notes_root = tmp_path / "notes_root"
    _write_lines(notes_root / "plugin" / "skills" / "x" / "notes.md", 201)

    notes_result = _run_check_line_limits(notes_root)

    assert notes_result.returncode == 0, notes_result.stdout + notes_result.stderr
    assert "oversized-file:" not in notes_result.stdout, notes_result.stdout


def test_line_limits_reports_allowlisted_without_failing(tmp_path: Path) -> None:
    """An allowlisted file at its recorded ceiling is reported, not failed.

    The entry records the file's current 401-line count as its ceiling — at or
    under the ceiling, the file is still printed (an allowlist entry is
    disclosure, not silence) but does not fail the run.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 401)
    allowlist = tmp_path / "allowlist.txt"
    _write_allowlist(allowlist, [("docs/notes.md", 401, "no job yet")])

    result = _run_check_line_limits(root, allowlist=allowlist)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/notes.md: 401 lines > 400"
    ], result.stdout


def test_line_limits_allowlisted_file_shrunk_below_cap_is_silent(
    tmp_path: Path,
) -> None:
    """A stale allowlist entry for a file that has since shrunk is inert.

    The file is now under the 400 cap: it must not appear in the report
    and must not fail the run, even though the allowlist still names it.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 350)
    allowlist = tmp_path / "allowlist.txt"
    _write_allowlist(allowlist, [("docs/notes.md", 401, "no job yet")])

    result = _run_check_line_limits(root, allowlist=allowlist)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "oversized-file:" not in result.stdout, result.stdout


def test_line_limits_fails_allowlisted_file_over_ceiling(tmp_path: Path) -> None:
    """An allowlisted file that has grown past its ceiling fails the run.

    The ceiling (450) is below the file's current 451 lines. The printed message
    still names the path-picked cap (400), not the ceiling — the ceiling only
    gates pass/fail, it is not the number reported.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 451)
    allowlist = tmp_path / "allowlist.txt"
    _write_allowlist(allowlist, [("docs/notes.md", 450, "no job yet")])

    result = _run_check_line_limits(root, allowlist=allowlist)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/notes.md: 451 lines > 400"
    ], result.stdout


def test_line_limits_allowlists_a_spaced_path(tmp_path: Path) -> None:
    """An allowlist entry whose path contains a space matches that file.

    This is what the TAB separator buys: the reader must split the entry on
    TAB, not on whitespace, or the path becomes ``docs/my`` and the ceiling
    becomes ``notes.md``. Reported at the cap, and exit 0 at the ceiling.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "my notes.md", 401)
    allowlist = tmp_path / "allowlist.txt"
    _write_allowlist(allowlist, [("docs/my notes.md", 401, "no job yet")])

    result = _run_check_line_limits(root, allowlist=allowlist)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/my notes.md: 401 lines > 400"
    ], result.stdout


def test_line_limits_matches_allowlist_paths_exactly(tmp_path: Path) -> None:
    """An allowlist entry covers its own path and no path sharing its basename.

    Both files are 401 lines and ``docs/notes.md`` is allowlisted at ceiling
    500 — strictly above 401, which is what makes the two implementations
    diverge. ``docs/sub/notes.md`` shares the entry's basename: under a
    basename comparison it inherits ceiling 500, stays under it and stops
    failing the run; under exact-path matching it is not allowlisted at all
    and must still fail. Either way both files are over cap and reported, so
    the exit code carries the whole signal — 1 here, 0 under the mutant.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 401)
    _write_lines(root / "docs" / "sub" / "notes.md", 401)
    allowlist = tmp_path / "allowlist.txt"
    _write_allowlist(allowlist, [("docs/notes.md", 500, "no job yet")])

    result = _run_check_line_limits(root, allowlist=allowlist)

    assert result.returncode == 1, result.stdout + result.stderr
    assert sorted(result.stdout.splitlines()) == [
        "oversized-file: docs/notes.md: 401 lines > 400",
        "oversized-file: docs/sub/notes.md: 401 lines > 400",
    ], result.stdout


def test_line_limits_skips_frozen_docs(tmp_path: Path) -> None:
    """``docs/superpowers/plans/`` and ``specs/`` are frozen work, excluded.

    Both hold a 401-line file; neither may be reported and neither may fail the
    run. Separate trees so each exclusion is asserted on its own — sharing one
    tree would let a single working exclusion carry the other.
    """
    for frozen in ("plans", "specs"):
        root = tmp_path / frozen
        _write_lines(root / "docs" / "superpowers" / frozen / "old.md", 401)

        result = _run_check_line_limits(root)

        assert result.returncode == 0, result.stdout + result.stderr
        assert "oversized-file:" not in result.stdout, result.stdout


def test_line_limits_checks_living_superpowers_docs(tmp_path: Path) -> None:
    """``docs/superpowers/design/`` is living work — checked, not excluded.

    The exclusion is pinned to the two frozen subdirectories; a GREEN that
    excluded ``docs/superpowers/`` wholesale would pass
    ``test_line_limits_skips_frozen_docs`` and fail here.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "superpowers" / "design" / "living.md", 401)

    result = _run_check_line_limits(root)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/superpowers/design/living.md: 401 lines > 400"
    ], result.stdout


def test_line_limits_fails_when_find_cannot_walk(tmp_path: Path) -> None:
    """A directory ``find`` cannot read is a failure to run, not a clean pass.

    ``docs/locked/`` is chmod 0o000 and holds the tree's only over-cap file:
    ``find`` hits the directory mid-walk, prints ``Permission denied`` to
    stderr and exits non-zero — but the script reads that ``find`` from a
    process substitution, whose exit status ``set -e`` cannot see. Slices
    3-7's code review (Finding 3) found this leaves the gate green: exit 0,
    the 401-line file never checked and never reported.

    Exit 2 is the contract asserted here, with ``find``'s own diagnostic
    reaching stderr. What a partial walk printed before it failed is
    deliberately not asserted: a fix that reports already-walked files before
    exiting 2 is as acceptable as one that reports nothing, and this fixture
    could not tell them apart anyway — the only readable file is under cap.
    """
    if os.geteuid() == 0:
        pytest.skip("root ignores directory permissions; chmod 0o000 has no effect")

    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 10)
    locked_dir = root / "docs" / "locked"
    _write_lines(locked_dir / "hidden.md", 401)
    locked_dir.chmod(0o000)
    try:
        result = _run_check_line_limits(root)
    finally:
        locked_dir.chmod(0o700)

    assert result.returncode == 2, result.stdout + result.stderr
    assert "docs/locked" in result.stderr, result.stderr


def test_line_limits_rejects_crlf_on_full_entry_line(tmp_path: Path) -> None:
    """A CRLF-terminated three-field entry line is a malformed-allowlist error.

    The carriage return lands in the (unused) ``note`` field — ``read``'s
    last named variable absorbs it — so today's integer regex on
    ``ceiling`` never sees it and the line is silently accepted, masking a
    genuine encoding problem instead of reporting one. The required
    behaviour treats any CR in an allowlist line as malformed: exit 2 (the
    script's other malformed-allowlist exit status), a diagnostic naming
    the allowlist line number and a CRLF/carriage-return line ending, and
    never the misleading ``ceiling is not an integer`` message.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 10)
    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_bytes(b"docs/notes.md\t401\tno job yet\r\n")

    result = _run_check_line_limits(root, allowlist=allowlist)

    # The allowlist's own tmp_path is embedded in the script's diagnostic
    # (it names $ALLOWLIST) and pytest derives that tmp_path directory name
    # from this test's own name — which contains "crlf". Stripped out
    # before the wording check below, or that substring would make the
    # check pass on the path, not on the script's diagnostic text.
    diagnostic = result.stderr.replace(str(allowlist), "<allowlist>")

    assert result.returncode == 2, result.stdout + result.stderr
    assert "line 1" in diagnostic, diagnostic
    assert "carriage return" in diagnostic.lower() or "crlf" in diagnostic.lower(), (
        diagnostic
    )
    assert "ceiling is not an integer" not in diagnostic, diagnostic


def test_line_limits_rejects_crlf_on_two_field_entry_line(tmp_path: Path) -> None:
    """A CRLF-terminated two-field line (missing ``note``) is also malformed.

    The script's format comment names three fields, but its read loop
    leaves ``_note`` empty without error when a line has only ``path`` and
    ``ceiling`` — so a real-world entry can omit the note, and here the
    carriage return lands directly on the ``ceiling`` field instead. Today
    this already exits 2, but via the misleading ``ceiling is not an
    integer: 401<CR>`` message; the required diagnostic names the CRLF
    instead of blaming the ceiling.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 10)
    allowlist = tmp_path / "allowlist.txt"
    allowlist.write_bytes(b"docs/notes.md\t401\r\n")

    result = _run_check_line_limits(root, allowlist=allowlist)

    # See the sibling three-field test above: strip the allowlist's own
    # tmp_path out of stderr before the wording check, since pytest's
    # tmp_path directory name is derived from this test's name (which
    # contains "crlf") and would otherwise make the check pass on the path.
    diagnostic = result.stderr.replace(str(allowlist), "<allowlist>")

    assert result.returncode == 2, result.stdout + result.stderr
    assert "line 1" in diagnostic, diagnostic
    assert "carriage return" in diagnostic.lower() or "crlf" in diagnostic.lower(), (
        diagnostic
    )
    assert "ceiling is not an integer" not in diagnostic, diagnostic


def test_line_limits_handles_spaced_path(tmp_path: Path) -> None:
    """A path with spaces is reported intact, never split on whitespace."""
    root = tmp_path / "root"
    _write_lines(root / "docs" / "my notes.md", 401)

    result = _run_check_line_limits(root)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/my notes.md: 401 lines > 400"
    ], result.stdout
