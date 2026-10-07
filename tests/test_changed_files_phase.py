"""Contract tests for ``changed-files.sh <job> --phase``.

D-89 and D-94: the phase base is the latest commit in ``<run base>..HEAD``
touching ``plans/<job>/reports/phase-*-corrector.md``, keyed on that path and
never on the commit subject, and the run base (D-88) when no such commit
exists. The list is the same filtered diff as without ``--phase``, since that
base.

Split from ``tests/test_changed_files.py``, which keeps the base and list
tests, to keep each module under its line cap. The exit-code tests are in
``tests/test_changed_files_errors.py``. See ``tests/changed_files_helpers.py``
for the shared fixtures.
"""

from pathlib import Path

from .changed_files_helpers import _commit, _init_repo, _run_script


def test_phase_without_boundary_gives_run_base(tmp_path: Path) -> None:
    """``--phase`` with no boundary landed in the run falls back to the run base.

    D-89 and D-94: the phase base is the latest commit in ``<run base>..HEAD``
    touching ``plans/j/reports/phase-*-corrector.md``, and the run base (D-88)
    when none matches. History: seed -> a ``phase-1-corrector.md`` report for
    ``j`` -> ``j``'s ``runbook.md``, the run base -> item 1.1 (report, new
    ``a.txt``) -> another job's ``plans/jj/reports/phase-1-corrector.md``
    inside the run -> item 1.2 (report, changed ``b.txt``).

    The pre-run report sits one commit before the run base, so a search over
    the whole history names it, not the base; the in-run ``jj`` report
    catches a search ignoring the job, which would name it as the base. Only
    the run base, the commit before item 1.1, is right. ``--phase`` must also
    print exactly what the bare call prints; only ``plans/j/`` is filtered
    out, so the list is ``a.txt``, ``b.txt`` and the other job's report.
    """
    repo = _init_repo(tmp_path)
    _commit(repo, "pre-run phase", {"plans/j/reports/phase-1-corrector.md": "p\n"})
    base_sha = _commit(repo, "j planning", {"plans/j/runbook.md": "v1\n"})
    _commit(repo, "item 1.1", {"plans/j/reports/item-1-1.md": "1\n", "a.txt": "a\n"})
    _commit(repo, "jj boundary", {"plans/jj/reports/phase-1-corrector.md": "o\n"})
    _commit(repo, "item 1.2", {"plans/j/reports/item-1-2.md": "2\n", "b.txt": "x\n"})

    plain = _run_script(repo, "j")
    assert plain.returncode == 0, plain.stdout + plain.stderr
    assert plain.stdout.splitlines() == [
        f"BASE: {base_sha}",
        "a.txt",
        "b.txt",
        "plans/jj/reports/phase-1-corrector.md",
    ], plain.stdout

    result = _run_script(repo, "j", "--phase")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == plain.stdout


def test_phase_base_is_latest_boundary_commit(tmp_path: Path) -> None:
    """``--phase`` takes the latest commit touching ``j``'s corrector report.

    D-89 and D-94: the base is keyed on the report's path history in
    ``<run base>..HEAD``, never the subject, and ``-1`` takes the latest, so a
    report committed twice resolves to the later commit. A commit that
    modifies ``phase-1-corrector.md`` again is therefore the base, and only
    files after it are listed. History: seed -> ``j`` planning, the run base
    -> items 1.1 and 1.2 -> the boundary (subject "fix review findings": it
    adds the report and ``fix.txt``) -> item 2.1 -> the report modified again
    with ``f.txt``, the expected base -> a decoy whose subject says "Phase 2
    boundary" but touches no report (``d.txt``) -> item 2.2 (``g.txt``) ->
    another job's ``phase-2-corrector.md``.

    Each decoy rules out wrong derivations: the first boundary, a
    ``--diff-filter=A`` or oldest-first search (the later commit only
    modifies the report); the subject decoy, a match on subject alone, with
    a path fallback, or unioned with the path (it is later than the real
    base); the other job's report, a search ignoring the job (it would be
    the latest commit). The range itself is pinned by
    ``test_phase_without_boundary_gives_run_base``: here an in-run boundary
    is always later than any pre-run commit. The list is ``d.txt``,
    ``g.txt`` and the other job's report; ``plans/j/`` drops out. The bare
    call in the same repo still gives the run base and the full list.
    """
    repo = _init_repo(tmp_path)
    run_base = _commit(repo, "j planning", {"plans/j/runbook.md": "v1\n"})
    _commit(repo, "item 1.1", {"plans/j/reports/item-1-1.md": "1\n", "a.txt": "a\n"})
    _commit(repo, "item 1.2", {"plans/j/reports/item-1-2.md": "2\n", "c.txt": "c\n"})
    _commit(
        repo,
        "fix review findings",
        {"plans/j/reports/phase-1-corrector.md": "v1\n", "fix.txt": "f\n"},
    )
    _commit(repo, "item 2.1", {"plans/j/reports/item-2-1.md": "3\n", "e.txt": "e\n"})
    boundary = _commit(
        repo, "tweak", {"plans/j/reports/phase-1-corrector.md": "v2\n", "f.txt": "f\n"}
    )
    _commit(repo, "Phase 2 boundary", {"d.txt": "d\n"})
    _commit(repo, "item 2.2", {"plans/j/reports/item-2-2.md": "4\n", "g.txt": "g\n"})
    _commit(repo, "jj boundary", {"plans/jj/reports/phase-2-corrector.md": "o\n"})

    plain = _run_script(repo, "j")
    assert plain.returncode == 0, plain.stdout + plain.stderr
    assert plain.stdout.splitlines() == [
        f"BASE: {run_base}",
        "a.txt",
        "c.txt",
        "d.txt",
        "e.txt",
        "f.txt",
        "fix.txt",
        "g.txt",
        "plans/jj/reports/phase-2-corrector.md",
    ], plain.stdout

    result = _run_script(repo, "j", "--phase")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        f"BASE: {boundary}",
        "d.txt",
        "g.txt",
        "plans/jj/reports/phase-2-corrector.md",
    ], result.stdout


def test_phase_flag_only_as_exact_second_argument(tmp_path: Path) -> None:
    """Anything but ``<job>`` or ``<job> --phase`` is a usage error.

    Pins the exact-``--phase`` guard from slice 1's code review: a near-miss
    flag, an extra word, the flag first, and the flag alone (the job
    missing, which would otherwise read as a job with no report, exit 1) each
    exit 2 with ``ERROR:``.
    """
    repo = _init_repo(tmp_path)
    for args in (
        ("j", "--phases"),
        ("j", "extra"),
        ("--phase", "j"),
        ("--phase",),
        ("--phase", "--phase"),
    ):
        result = _run_script(repo, *args)
        assert (result.returncode, result.stdout[: len("ERROR:")]) == (
            2,
            "ERROR:",
        ), f"{args}: {result.stdout}{result.stderr}"


def test_phase_list_keeps_the_filters(tmp_path: Path) -> None:
    """Under ``--phase`` the exempt-path and ``plans/j/`` drops still apply.

    D-89, D-90 and D-91: the list since the phase base is filtered as the bare
    list is. History: seed -> ``j`` planning, the run base -> item 1.1 -> the
    boundary (``phase-1-corrector.md``, the expected base) -> a commit of the
    three exempt paths (``inbox/x.md``, ``.claude/handoff-task.md``, a file
    named ``memory``), ``j``'s item 2.1 report and a ``runbook.md`` revision,
    and near-misses of the exempt alternation that stay listed
    (``inbox/sub/y.md``, ``memoryx.txt``) -> a decoy commit adding only
    ``plans/j/reports/phase-9/old-corrector.md`` and
    ``plans/j/reports/sub/phase-9-corrector.md``.

    The decoy pins the ``:(glob)`` magic on the base query: git's default
    ``*`` crosses ``/``, so ``phase-*-corrector.md`` would match
    ``phase-9/old-corrector.md`` and move the base past the kept files.
    ``sub/phase-9-corrector.md`` matches neither way: it pins the literal
    ``reports/phase-`` prefix, catching a pathspec that admits a directory
    before ``phase-`` (``reports/**/phase-*-corrector.md``). The list is
    exactly the near-misses, with the pre-boundary ``a.txt`` and the
    ``fix.txt`` of the boundary commit absent.
    """
    repo = _init_repo(tmp_path)
    _commit(repo, "j planning", {"plans/j/runbook.md": "v1\n"})
    _commit(repo, "item 1.1", {"plans/j/reports/item-1-1.md": "1\n", "a.txt": "a\n"})
    boundary = _commit(
        repo,
        "fix review findings",
        {"plans/j/reports/phase-1-corrector.md": "v1\n", "fix.txt": "f\n"},
    )
    _commit(
        repo,
        "item 2.1",
        {
            "inbox/x.md": "exempt\n",
            ".claude/handoff-task.md": "exempt\n",
            "memory": "exempt\n",
            "plans/j/reports/item-2-1.md": "2\n",
            "plans/j/runbook.md": "v2\n",
            "inbox/sub/y.md": "kept\n",
            "memoryx.txt": "kept\n",
        },
    )
    _commit(
        repo,
        "decoys",
        {
            "plans/j/reports/phase-9/old-corrector.md": "d\n",
            "plans/j/reports/sub/phase-9-corrector.md": "d\n",
        },
    )

    result = _run_script(repo, "j", "--phase")
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        f"BASE: {boundary}",
        "inbox/sub/y.md",
        "memoryx.txt",
    ], result.stdout
