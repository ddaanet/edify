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


def _run_check_line_limits(root: Path) -> subprocess.CompletedProcess[str]:
    """Invoke ``check_line_limits.sh`` by absolute path against ``root``."""
    return subprocess.run(
        [str(SCRIPT), str(root)],
        cwd=root.parent,
        capture_output=True,
        text=True,
        check=False,
    )


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
