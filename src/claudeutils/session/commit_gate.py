"""Commit gates: file validation and vet check."""

from __future__ import annotations

import subprocess
import tomllib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path, PurePath

from claudeutils.git import _git


def _build_clean_file_error_msg(clean_files: list[str]) -> str:
    """Build message for CleanFileError with file list."""
    files_list = "\n".join(f"- {f}" for f in clean_files)
    return (
        "**Error:** Listed files have no uncommitted changes\n"
        f"{files_list}\n\n"
        "STOP: Do not remove files and retry."
    )


class CleanFileError(Exception):
    """Listed files have no uncommitted changes."""

    def __init__(self, clean_files: list[str]) -> None:
        """Build error with STOP directive listing clean files."""
        self.clean_files = clean_files
        super().__init__(_build_clean_file_error_msg(clean_files))


def _dirty_files(cwd: Path | None = None) -> set[str]:
    """Get files with uncommitted changes from git status."""
    # Use raw stdout — strip() destroys leading space in porcelain XY format.
    # -u lists individual untracked files, not just their parent directories.
    result = subprocess.run(
        ["git", "status", "--porcelain", "-u"],
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
    output = _git(
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-only",
        "-r",
        "HEAD",
        check=False,
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
    allowed = (dirty | _head_files(cwd)) if amend else dirty

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


def _load_review_patterns(cwd: Path | None = None) -> list[str]:
    """Load require-review patterns from pyproject.toml."""
    pyproject = (cwd or Path()) / "pyproject.toml"
    if not pyproject.exists():
        return []
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    commit_cfg = data.get("tool", {}).get("claudeutils", {}).get("commit", {})
    patterns: list[str] = commit_cfg.get("require-review", [])
    return patterns


def _find_reports(cwd: Path | None = None) -> list[Path]:
    """Discover review reports in plans/*/reports/."""
    reports_root = (cwd or Path()) / "plans"
    if not reports_root.exists():
        return []
    return [
        p
        for p in reports_root.glob("*/reports/*")
        if p.is_file() and ("vet" in p.name or "review" in p.name)
    ]


def _newest_file(files: list[Path]) -> tuple[float, Path]:
    """Return newest mtime and path among files."""
    newest = max(files, key=lambda f: f.stat().st_mtime)
    return newest.stat().st_mtime, newest


_AGENT_CORE_PATTERNS = ["plugin/bin/**", "plugin/skills/**/*.sh"]


def vet_check(files: list[str], *, cwd: Path | None = None) -> VetResult:
    """Check files against require-review patterns."""
    patterns = _load_review_patterns(cwd) + _AGENT_CORE_PATTERNS
    if not patterns:
        return VetResult(passed=True)

    matched = [f for f in files if any(PurePath(f).full_match(pat) for pat in patterns)]
    if not matched:
        return VetResult(passed=True)

    reports = _find_reports(cwd)
    if not reports:
        return VetResult(
            passed=False,
            reason="unreviewed",
            unreviewed_files=matched,
        )

    root = Path(cwd or ".")
    matched_paths = [root / f for f in matched if (root / f).exists()]
    if not matched_paths:
        return VetResult(passed=True)

    newest_source_mtime, newest_source_path = _newest_file(matched_paths)
    newest_report_mtime, newest_report_path = _newest_file(reports)

    if newest_source_mtime > newest_report_mtime:
        source_time = datetime.fromtimestamp(newest_source_mtime, tz=UTC).strftime(
            "%Y-%m-%d %H:%M"
        )
        report_time = datetime.fromtimestamp(newest_report_mtime, tz=UTC).strftime(
            "%Y-%m-%d %H:%M"
        )
        stale_info = (
            f"- Newest change: {newest_source_path} ({source_time})\n"
            f"- Newest report: {newest_report_path} ({report_time})"
        )
        return VetResult(
            passed=False,
            reason="stale",
            stale_info=stale_info,
        )

    return VetResult(passed=True)
