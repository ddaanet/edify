"""Tests for plan archive coverage validation."""

import subprocess
from pathlib import Path

import pytest

from claudeutils.validation.plan_archive import (
    check_plan_archive_coverage,
    get_archive_headings,
    get_staged_plan_deletions,
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create initialized git repo with config."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@test.com")
    return repo


class TestGetStagedPlanDeletions:
    """Tests for get_staged_plan_deletions."""

    def test_no_deletions_returns_empty(self, git_repo: Path) -> None:
        """Repository with no deletions returns empty list."""
        assert get_staged_plan_deletions(git_repo) == []

    def test_deleted_plan_detected(self, git_repo: Path) -> None:
        """Deleted plan directory detected from git staging."""
        plans_dir = git_repo / "plans" / "old-plan"
        plans_dir.mkdir(parents=True)
        (plans_dir / "design.md").write_text("# Design")
        _git(git_repo, "add", ".")
        _git(git_repo, "commit", "-m", "Add plan")
        _git(git_repo, "rm", "-r", "plans/old-plan")

        assert "old-plan" in get_staged_plan_deletions(git_repo)

    def test_multiple_deleted_plans(self, git_repo: Path) -> None:
        """Multiple deleted plans all detected."""
        for name in ["plan-one", "plan-two"]:
            d = git_repo / "plans" / name
            d.mkdir(parents=True)
            (d / "design.md").write_text("# Design")
        _git(git_repo, "add", ".")
        _git(git_repo, "commit", "-m", "Add plans")
        for name in ["plan-one", "plan-two"]:
            _git(git_repo, "rm", "-r", f"plans/{name}")

        result = get_staged_plan_deletions(git_repo)
        assert "plan-one" in result
        assert "plan-two" in result

    def test_plan_with_only_gitkeep_not_deleted(self, git_repo: Path) -> None:
        """Plans containing only .gitkeep not considered substantive."""
        d = git_repo / "plans" / "empty-plan"
        d.mkdir(parents=True)
        (d / ".gitkeep").touch()
        _git(git_repo, "add", ".")
        _git(git_repo, "commit", "-m", "Add empty plan")
        _git(git_repo, "rm", "-r", "plans/empty-plan")

        assert "empty-plan" not in get_staged_plan_deletions(git_repo)


class TestGetArchiveHeadings:
    """Tests for get_archive_headings."""

    def test_extracts_h2_headings(self, tmp_path: Path) -> None:
        """H2 headings extracted from archive file."""
        root = tmp_path
        archive_file = root / "agents" / "plan-archive.md"
        archive_file.parent.mkdir(parents=True)
        archive_file.write_text(
            """# Plan Archive

## plan-one

Some content here.

## plan-two

More content.
"""
        )

        result = get_archive_headings(root)
        assert "plan-one" in result
        assert "plan-two" in result

    def test_case_insensitive_matching(self, tmp_path: Path) -> None:
        """Archive headings match case-insensitively."""
        root = tmp_path
        archive_file = root / "agents" / "plan-archive.md"
        archive_file.parent.mkdir(parents=True)
        archive_file.write_text(
            """# Plan Archive

## MyPlan

Content.
"""
        )

        result = get_archive_headings(root)
        # Should find it even with different case
        assert any(h.lower() == "myplan" for h in result)

    def test_missing_archive_file_returns_empty(self, tmp_path: Path) -> None:
        """Missing archive file returns empty set."""
        root = tmp_path

        result = get_archive_headings(root)
        assert result == set()

    def test_ignores_non_h2_headings(self, tmp_path: Path) -> None:
        """Only H2 headings extracted, not H1 or H3."""
        root = tmp_path
        archive_file = root / "agents" / "plan-archive.md"
        archive_file.parent.mkdir(parents=True)
        archive_file.write_text(
            """# Main Title

## good-plan

Content.

### subsection

Details.

## another-plan

More.
"""
        )

        result = get_archive_headings(root)
        assert "good-plan" in result
        assert "another-plan" in result
        assert "subsection" not in result
        assert "Main Title" not in result


class TestCheckPlanArchiveCoverage:
    """Tests for check_plan_archive_coverage."""

    def test_no_deleted_plans_no_errors(self, tmp_path: Path) -> None:
        """No errors when no plans deleted."""
        archive = tmp_path / "agents" / "plan-archive.md"
        archive.parent.mkdir(parents=True)
        archive.write_text("# Archive\n")
        assert check_plan_archive_coverage(tmp_path) == []

    def test_deleted_plan_with_archive_entry_no_error(self, git_repo: Path) -> None:
        """Deleted plan with archive entry produces no error."""
        d = git_repo / "plans" / "old-plan"
        d.mkdir(parents=True)
        (d / "design.md").write_text("# Design")
        agents = git_repo / "agents"
        agents.mkdir(exist_ok=True)
        (agents / "plan-archive.md").write_text("# Archive\n\n## old-plan\n\nDone.\n")
        _git(git_repo, "add", ".")
        _git(git_repo, "commit", "-m", "Add plan")
        _git(git_repo, "rm", "-r", "plans/old-plan")

        assert check_plan_archive_coverage(git_repo) == []

    def test_deleted_plan_without_archive_entry_error(self, git_repo: Path) -> None:
        """Deleted plan without archive entry produces error."""
        d = git_repo / "plans" / "undocumented-plan"
        d.mkdir(parents=True)
        (d / "design.md").write_text("# Design")
        agents = git_repo / "agents"
        agents.mkdir(exist_ok=True)
        (agents / "plan-archive.md").write_text("# Plan Archive\n")
        _git(git_repo, "add", ".")
        _git(git_repo, "commit", "-m", "Add plan")
        _git(git_repo, "rm", "-r", "plans/undocumented-plan")

        errors = check_plan_archive_coverage(git_repo)
        assert len(errors) == 1
        assert "undocumented-plan" in errors[0]

    def test_multiple_deleted_plans_mixed_coverage(self, git_repo: Path) -> None:
        """Mixed coverage: reports only missing archive entries."""
        for name in ["covered-plan", "uncovered-plan"]:
            d = git_repo / "plans" / name
            d.mkdir(parents=True)
            (d / "design.md").write_text("# Design")
        agents = git_repo / "agents"
        agents.mkdir(exist_ok=True)
        (agents / "plan-archive.md").write_text(
            "# Archive\n\n## covered-plan\n\nArchived.\n"
        )
        _git(git_repo, "add", ".")
        _git(git_repo, "commit", "-m", "Add plans")
        for name in ["covered-plan", "uncovered-plan"]:
            _git(git_repo, "rm", "-r", f"plans/{name}")

        errors = check_plan_archive_coverage(git_repo)
        assert len(errors) == 1
        assert "uncovered-plan" in errors[0]
