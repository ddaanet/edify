"""Contract tests for ``scripts/check_line_limits.sh``.

KD-7 in ``plans/provenance-enforcement-and-routing/outline.md`` (Item 1.10).
Each test builds a throwaway fixture tree under ``tmp_path`` and runs the
script by absolute path with ``[ROOT]`` = that tree, ``cwd=tmp_path`` (never
the checkout — the script must honour ``ROOT`` rather than walking the repo
it happens to run from).
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_line_limits.sh"


def _write_lines(path: Path, count: int) -> None:
    """Write ``count`` newline-terminated filler lines to ``path``.

    The file always ends in a newline, so ``wc -l`` — what the script counts
    — reports exactly ``count`` for ``count >= 1``. Parent directories are
    created; ``path`` may contain spaces (it is never split).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(f"line {i}" for i in range(count)) + "\n"
    path.write_text(text, encoding="utf-8")


def _run_check_line_limits(
    root: Path, allowlist: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Invoke ``check_line_limits.sh`` by absolute path against ``root``.

    ``--allowlist`` precedes ``ROOT`` on the command line when given, per
    the script's ``[--allowlist FILE] [ROOT]`` usage.
    """
    args = [str(SCRIPT)]
    if allowlist is not None:
        args += ["--allowlist", str(allowlist)]
    args.append(str(root))
    return subprocess.run(
        args,
        cwd=root.parent,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_allowlist(path: Path, entries: list[tuple[str, int, str]]) -> None:
    """Write an allowlist file in the format KD-7 pins for this job.

    One entry per line: ``<path><TAB><ceiling><TAB><note>``. ``path`` is
    root-relative and may contain spaces (never split on whitespace);
    ``ceiling`` is the entry's line-count ceiling, which only ratchets
    down; ``note`` names the job that retires the entry, or ``"no job
    yet"``.

    Every fixture opens with a ``#`` comment line and a blank line, so the
    script must skip both to pass any allowlist test — a reader treating
    them as entries would look for a file literally named ``#`` and one
    named ``""``.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# path\tceiling\tnote", ""]
    lines += [
        f"{entry_path}\t{ceiling}\t{note}" for entry_path, ceiling, note in entries
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    """An allowlist entry covers its own path and no path containing it.

    Three 401-line files; only ``docs/notes.md`` is allowlisted.
    ``docs/my-notes.md`` and ``docs/sub/notes.md`` both contain the entry as
    a substring — the first would be caught by an unanchored ``case
    "$file" in *$entry*)``, the second by a basename comparison. Both must
    still fail, so the run exits 1 and reports all three.
    """
    root = tmp_path / "root"
    _write_lines(root / "docs" / "notes.md", 401)
    _write_lines(root / "docs" / "my-notes.md", 401)
    _write_lines(root / "docs" / "sub" / "notes.md", 401)
    allowlist = tmp_path / "allowlist.txt"
    _write_allowlist(allowlist, [("docs/notes.md", 401, "no job yet")])

    result = _run_check_line_limits(root, allowlist=allowlist)

    assert result.returncode == 1, result.stdout + result.stderr
    assert sorted(result.stdout.splitlines()) == [
        "oversized-file: docs/my-notes.md: 401 lines > 400",
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


def test_line_limits_handles_spaced_path(tmp_path: Path) -> None:
    """A path with spaces is reported intact, never split on whitespace."""
    root = tmp_path / "root"
    _write_lines(root / "docs" / "my notes.md", 401)

    result = _run_check_line_limits(root)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "oversized-file: docs/my notes.md: 401 lines > 400"
    ], result.stdout
