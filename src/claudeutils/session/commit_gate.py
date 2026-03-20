"""Commit gates: file validation and vet check."""

from __future__ import annotations

import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path, PurePath


class CleanFileError(Exception):
    """Listed files have no uncommitted changes."""

    def __init__(self, clean_files: list[str]) -> None:
        """Build error with STOP directive listing clean files."""
        self.clean_files = clean_files
        files_list = "\n".join(f"- {f}" for f in clean_files)
        msg = (
            "**Error:** Listed files have no uncommitted changes\n"
            f"{files_list}\n\n"
            "STOP: Do not remove files and retry."
        )
        super().__init__(msg)


def _git_output(
    *args: str,
    cwd: Path | None = None,
) -> str:
    """Run git command and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def _dirty_files(cwd: Path | None = None) -> set[str]:
    """Get files with uncommitted changes from git status."""
    # Use raw stdout — strip() destroys leading space in porcelain XY format
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if len(line) > 3:
            # porcelain format: XY <path> or XY <path> -> <path>
            path = line[3:].split(" -> ")[-1]
            paths.add(path)
    return paths


def _head_files(cwd: Path | None = None) -> set[str]:
    """Get files in HEAD commit via diff-tree."""
    output = _git_output(
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-only",
        "-r",
        "HEAD",
        cwd=cwd,
    )
    return set(output.splitlines()) if output else set()


def validate_files(
    files: list[str],
    *,
    amend: bool = False,
    cwd: Path | None = None,
) -> None:
    """Validate all listed files have uncommitted changes.

    Raises CleanFileError for files with no changes.
    """
    dirty = _dirty_files(cwd)
    allowed = dirty | _head_files(cwd) if amend else dirty

    clean = [f for f in files if f not in allowed]
    if clean:
        raise CleanFileError(clean)


@dataclass
class VetResult:
    """Result of scripted vet check."""

    passed: bool
    reason: str | None = None
    unreviewed_files: list[str] = field(default_factory=list)
    stale_info: str | None = None


def _load_review_patterns() -> list[str]:
    """Load require-review patterns from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        return []
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    commit_cfg = data.get("tool", {}).get("claudeutils", {}).get("commit", {})
    patterns: list[str] = commit_cfg.get("require-review", [])
    return patterns


def _find_reports() -> list[Path]:
    """Discover review reports in plans/*/reports/."""
    reports_root = Path("plans")
    if not reports_root.exists():
        return []
    return [
        p
        for p in reports_root.glob("*/reports/*")
        if p.is_file() and ("vet" in p.name or "review" in p.name)
    ]


def _newest_mtime(files: list[Path]) -> float:
    """Return the newest mtime among files."""
    return max(f.stat().st_mtime for f in files)


def vet_check(files: list[str]) -> VetResult:
    """Check files against require-review patterns."""
    patterns = _load_review_patterns()
    if not patterns:
        return VetResult(passed=True)

    matched = [f for f in files if any(PurePath(f).full_match(pat) for pat in patterns)]
    if not matched:
        return VetResult(passed=True)

    reports = _find_reports()
    if not reports:
        return VetResult(
            passed=False,
            reason="unreviewed",
            unreviewed_files=matched,
        )

    matched_paths = [Path(f) for f in matched if Path(f).exists()]
    if not matched_paths:
        return VetResult(passed=True)

    newest_source = _newest_mtime(matched_paths)
    newest_report = _newest_mtime(reports)

    if newest_source > newest_report:
        delta = f"{newest_source - newest_report:.0f}s"
        return VetResult(
            passed=False,
            reason="stale",
            stale_info=f"Source newer than reports by {delta}",
        )

    return VetResult(passed=True)
