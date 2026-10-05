"""Fail-closed tests for ``plugin/skills/build/scripts/verify-step.sh``.

The exemption-pattern tests live in ``tests/test_verify_step_exemption.py``,
split out to keep each module under its line cap; see
``tests/verify_step_helpers.py`` for the shared fixtures.
"""

import os
import shutil
import sys
from pathlib import Path

import pytest

from .verify_step_helpers import (
    SCRIPT,
    _assert_dirty,
    _init_repo,
    _run_git,
    _run_script,
    _stub_just,
)


def test_git_status_failure_exits_2(tmp_path: Path) -> None:
    """A CWD outside any repo fails closed with exit 2, not a raw fatal.

    ``GIT_CEILING_DIRECTORIES`` blocks git from discovering an enclosing
    repository, so the failure is deterministic regardless of checkout.
    """
    outside = tmp_path / "outside"
    outside.mkdir()
    bin_dir = tmp_path / "bin"

    result = _run_script(
        outside,
        bin_dir,
        extra_env={"GIT_CEILING_DIRECTORIES": str(tmp_path)},
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ERROR: git status failed" in result.stdout.splitlines(), result.stdout
    assert not any(
        line.startswith(("CLEAN:", "DIRTY:")) for line in result.stdout.splitlines()
    ), result.stdout


def test_missing_just_exits_2(tmp_path: Path) -> None:
    """A clean repo with no ``just`` on ``PATH`` fails closed, not silently.

    Pre-F-2 code ran ``just precommit`` unconditionally, so a missing tool
    was reported as a precommit failure rather than an environment fault.
    """
    repo = _init_repo(tmp_path)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("bash", "git", "grep"):
        resolved = shutil.which(tool)
        assert resolved is not None, f"{tool} not found on the outer PATH"
        (bin_dir / tool).symlink_to(resolved)
    assert shutil.which("just", path=str(bin_dir)) is None

    result = _run_script(repo, bin_dir, extra_env={"PATH": str(bin_dir)})
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ERROR: just not found on PATH" in result.stdout.splitlines(), result.stdout
    assert "PRECOMMIT:" not in result.stdout, result.stdout


@pytest.mark.skipif(
    sys.platform == "darwin",
    reason="APFS rejects a path that is not valid UTF-8, so the fixture cannot exist",
)
def test_quotepath_false_does_not_hide_dirt(tmp_path: Path) -> None:
    r"""A local ``core.quotePath false`` cannot make non-UTF-8 dirt read clean.

    With ``quotePath`` off, git prints the raw ``0xFF`` byte of an untracked
    ``inbox/x\377/y.md``; grep in a UTF-8 locale then treats the status as
    binary and drops the line, so the tree would read ``CLEAN:``. The script
    forces ``core.quotePath=true``, so the line arrives quoted and is listed as
    dirt. The config is repo-local because ``GIT_CONFIG_GLOBAL`` is nulled for
    the script run. ``LC_ALL`` is pinned because under ``C`` grep passes the
    raw byte through and the hazard does not arise.
    """
    repo = _init_repo(tmp_path)
    _run_git(repo, "config", "core.quotePath", "false")
    # fsdecode maps the invalid byte to a surrogate that the filesystem calls
    # encode back to the raw 0xFF byte.
    nested = repo / os.fsdecode(b"inbox/x\xff")
    nested.mkdir(parents=True)
    (nested / "y.md").write_bytes(b"y\n")

    bin_dir, marker = _stub_just(tmp_path)

    result = _run_script(repo, bin_dir, extra_env={"LC_ALL": "C.UTF-8"})
    _assert_dirty(result, r'?? "inbox/x\377/y.md"')
    assert not marker.exists(), "just was invoked: " + result.stdout


@pytest.mark.parametrize(
    "exempt_paths",
    [
        pytest.param(None, id="absent"),
        pytest.param("# defines nothing\n", id="defines-nothing"),
    ],
)
def test_unloadable_exempt_paths_is_an_error_not_dirty(
    tmp_path: Path, exempt_paths: str | None
) -> None:
    """An ``exempt-paths.sh`` that cannot supply the alternation exits 2.

    The script under test is copied into ``tmp_path/scripts`` beside a
    doctored ``exempt-paths.sh``: absent, or present and defining nothing.
    The repo holds an untracked file, so a script that carried on would print
    ``DIRTY:`` and exit 1. The load guard must turn either case into
    ``ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh`` with
    exit 2. A bare ``source`` fails with exit 1 (the missing file, or the
    unbound variable under ``set -u``), which is ``DIRTY:``'s code.
    """
    repo = _init_repo(tmp_path)
    (repo / "dirt.txt").write_text("dirt\n", encoding="utf-8")
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copy2(SCRIPT, scripts / SCRIPT.name)
    if exempt_paths is not None:
        (scripts / "exempt-paths.sh").write_text(exempt_paths, encoding="utf-8")
    bin_dir, marker = _stub_just(tmp_path)

    result = _run_script(repo, bin_dir, script=scripts / SCRIPT.name)
    assert result.returncode == 2, result.stdout + result.stderr
    assert (
        "ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh"
        in result.stdout.splitlines()
    ), result.stdout
    assert "DIRTY:" not in result.stdout, result.stdout
    assert not marker.exists(), "just was invoked: " + result.stdout
