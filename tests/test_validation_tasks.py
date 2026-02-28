"""Tests for tasks validator."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from claudeutils.validation.tasks import (
    check_history,
    extract_learning_keys,
    extract_task_names,
    get_merge_parents,
    get_new_tasks,
    get_session_from_commit,
    get_staged_session,
    validate,
)


class TestExtractTaskNames:
    """Tests for extract_task_names function."""

    def test_extract_single_task(self) -> None:
        """Extract a single task."""
        lines = ["# Session", "", "## In-tree Tasks", "", "- [ ] **Task One** — desc"]
        assert extract_task_names(lines) == [(5, "Task One")]

    def test_extract_multiple_tasks(self) -> None:
        """Extract multiple tasks with different states."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Task One** — desc",
            "- [x] **Task Two** — done",
            "- [>] **Task Three** — in progress",
        ]
        tasks = extract_task_names(lines)
        assert len(tasks) == 3
        assert tasks[0] == (2, "Task One")
        assert tasks[1] == (3, "Task Two")
        assert tasks[2] == (4, "Task Three")

    def test_extract_tasks_with_special_characters(self) -> None:
        """Extract tasks with special characters in names."""
        lines = [
            "- [ ] **Task (With Parens)** — desc",
            "- [ ] **Task [With Brackets]** — desc",
        ]
        tasks = extract_task_names(lines)
        assert tasks[0][1] == "Task (With Parens)"
        assert tasks[1][1] == "Task [With Brackets]"

    def test_no_tasks_returns_empty(self) -> None:
        """File with no tasks returns empty list."""
        assert extract_task_names(["# Session", "", "Some content"]) == []

    def test_blocked_failed_canceled_statuses(self) -> None:
        """Tasks with [!], [✗], [–] statuses extracted."""  # noqa: RUF002
        lines = [
            "- [!] **Blocked Task** — waiting on signal",
            "- [✗] **Failed Task** — terminal failure",
            "- [–] **Canceled Task** — user canceled",  # noqa: RUF001
        ]
        tasks = extract_task_names(lines)
        assert len(tasks) == 3
        assert tasks[0] == (1, "Blocked Task")
        assert tasks[1] == (2, "Failed Task")
        assert tasks[2] == (3, "Canceled Task")

    def test_malformed_task_line_ignored(self) -> None:
        """Malformed task lines are ignored."""
        lines = [
            "- [ ] Task One — missing asterisks",
            "- [ ] **Task Two — missing closing",
            "- [ ] **Task Three** — valid",
        ]
        assert extract_task_names(lines) == [(3, "Task Three")]


class TestExtractLearningKeys:
    """Tests for extract_learning_keys function."""

    def test_extract_learning_keys(self) -> None:
        """Extract learning keys from ## headers."""
        lines = [
            "# Learnings",
            "Intro",
            "",
            "## First Learning",
            "Content",
            "## Second Learning",
            "More",
        ]
        assert extract_learning_keys(lines) == {"first learning", "second learning"}

    def test_learning_keys_lowercase(self) -> None:
        """Learning keys are lowercase."""
        lines = ["# Learnings", "## Capital Letters HERE", "content"]
        assert "capital letters here" in extract_learning_keys(lines)

    def test_no_h1_title_skip_keys(self) -> None:
        """Keys before H1 are skipped."""
        lines = [
            "## Should Not Match",
            "## Also Not",
            "# Main Title",
            "## Should Match",
            "content",
        ]
        assert extract_learning_keys(lines) == {"should match"}

    def test_empty_file_no_keys(self) -> None:
        """Empty file returns no keys."""
        assert extract_learning_keys([]) == set()


class TestGetSessionFromCommit:
    """Tests for get_session_from_commit function."""

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_success(self, mock_run: MagicMock) -> None:
        """Successful retrieval of session from commit."""
        mock_run.return_value = MagicMock(stdout="line 1\nline 2\nline 3", returncode=0)
        result = get_session_from_commit("HEAD", Path("agents/session.md"))
        assert result == ["line 1", "line 2", "line 3"]

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_not_found(self, mock_run: MagicMock) -> None:
        """Graceful handling when commit file not found."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        assert get_session_from_commit("MISSING", Path("agents/session.md")) == []


class TestGetMergeParents:
    """Tests for get_merge_parents function."""

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_in_merge(self, mock_run: MagicMock) -> None:
        """Detect merge in progress."""
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="merge_head_hash\n"),
            MagicMock(returncode=0, stdout="head_hash\n"),
        ]
        assert get_merge_parents() == ("head_hash", "merge_head_hash")

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_not_in_merge(self, mock_run: MagicMock) -> None:
        """Not in a merge returns None."""
        mock_run.return_value = MagicMock(returncode=1)
        assert get_merge_parents() is None


class TestGetStagedSession:
    """Tests for get_staged_session function."""

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_success(self, mock_run: MagicMock) -> None:
        """Successful retrieval of staged session."""
        mock_run.return_value = MagicMock(
            stdout="staged line 1\nstaged line 2", returncode=0
        )
        assert get_staged_session(Path("agents/session.md")) == [
            "staged line 1",
            "staged line 2",
        ]

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_not_staged(self, mock_run: MagicMock) -> None:
        """Graceful handling when file not staged."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        assert get_staged_session(Path("agents/session.md")) == []


class TestGetNewTasks:
    """Tests for get_new_tasks function."""

    @patch("claudeutils.validation.tasks.get_staged_session")
    @patch("claudeutils.validation.tasks.get_merge_parents")
    @patch("claudeutils.validation.tasks.get_session_from_commit")
    def test_regular_commit(
        self,
        mock_session: MagicMock,
        mock_merge: MagicMock,
        mock_staged: MagicMock,
    ) -> None:
        """New task detection in regular commit."""
        mock_merge.return_value = None
        mock_staged.return_value = [
            "- [ ] **Task One** — desc",
            "- [ ] **Task Two** — desc",
        ]
        mock_session.return_value = ["- [ ] **Task One** — desc"]
        result = get_new_tasks(Path("agents/session.md"))
        assert "Task Two" in result

    @patch("claudeutils.validation.tasks.subprocess.run")
    @patch("claudeutils.validation.tasks.get_staged_session")
    @patch("claudeutils.validation.tasks.get_merge_parents")
    @patch("claudeutils.validation.tasks.get_session_from_commit")
    def test_merge_commit(
        self,
        mock_session: MagicMock,
        mock_merge: MagicMock,
        mock_staged: MagicMock,
        mock_run: MagicMock,
    ) -> None:
        """New task detection in merge (new only if absent from all parents)."""
        mock_merge.return_value = ("parent1", "parent2")
        mock_run.return_value = MagicMock(
            returncode=0, stdout="commit parent1 parent2\n"
        )
        mock_staged.return_value = [
            "- [ ] **Task One** — desc",
            "- [ ] **Task Two** — desc",
            "- [ ] **Task Three** — desc",
        ]
        mock_session.side_effect = [
            ["- [ ] **Task One** — desc"],
            ["- [ ] **Task Two** — desc"],
        ]
        result = get_new_tasks(Path("agents/session.md"))
        assert "Task Three" in result
        assert "Task One" not in result
        assert "Task Two" not in result

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_octopus_merge_error(self, mock_run: MagicMock) -> None:
        """Octopus merge detection raises error."""
        with (
            patch("claudeutils.validation.tasks.get_merge_parents") as mock_merge,
            patch("claudeutils.validation.tasks.get_staged_session") as mock_staged,
        ):
            mock_merge.return_value = ("p1", "p2")
            mock_staged.return_value = []
            mock_run.return_value = MagicMock(returncode=0, stdout="commit p1 p2 p3\n")
            with pytest.raises(SystemExit):
                get_new_tasks(Path("agents/session.md"))


class TestCheckHistory:
    """Tests for check_history function."""

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_found(self, mock_run: MagicMock) -> None:
        """Task name found in history."""
        mock_run.return_value = MagicMock(stdout="hash1\nhash2", returncode=0)
        assert check_history("Task Name") is True

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_not_found(self, mock_run: MagicMock) -> None:
        """Task name not found in history."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        assert check_history("Task Name") is False

    @patch("claudeutils.validation.tasks.subprocess.run")
    def test_case_insensitive(self, mock_run: MagicMock) -> None:
        """History search is case-insensitive."""
        mock_run.return_value = MagicMock(stdout="hash1", returncode=0)
        assert check_history("task name") is True
        assert "--regexp-ignore-case" in mock_run.call_args[0][0]


class TestValidate:
    """Tests for validate function."""

    def test_valid_session_no_errors(self, tmp_path: Path) -> None:
        """Valid session returns no errors."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n"
            "- [ ] **Task One** — desc\n"
            "- [ ] **Task Two** — desc\n"
        )
        (tmp_path / "learnings.md").write_text("# Learnings\n\n## Some Learning\n")
        assert validate("session.md", "learnings.md", tmp_path) == []

    def test_duplicate_task_names(self, tmp_path: Path) -> None:
        """Duplicate task names detected."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n- [ ] **Task One** — first\n"
            "- [ ] **Task Two** — second\n- [ ] **Task One** — duplicate\n"
        )
        (tmp_path / "learnings.md").write_text("# Learnings\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "duplicate task name" in errors[0]
        assert "Task One" in errors[0]

    def test_duplicate_case_insensitive(self, tmp_path: Path) -> None:
        """Duplicate detection is case-insensitive."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n"
            "- [ ] **Task One** — first\n"
            "- [ ] **task one** — dup\n"
        )
        (tmp_path / "learnings.md").write_text("# Learnings\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "duplicate" in errors[0]

    def test_task_conflicts_with_learning_key(self, tmp_path: Path) -> None:
        """Task names conflicting with learning keys detected."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n- [ ] **Conflicting Task** — desc\n"
        )
        (tmp_path / "learnings.md").write_text(
            "# Learnings\n\n## Conflicting Task\nContent.\n"
        )
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "task name conflicts with learning key" in errors[0]

    def test_task_conflict_case_insensitive(self, tmp_path: Path) -> None:
        """Conflict detection is case-insensitive."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n- [ ] **conflicting task** — desc\n"
        )
        (tmp_path / "learnings.md").write_text("# Learnings\n\n## Conflicting Task\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "conflicts" in errors[0]

    @patch("claudeutils.validation.tasks.check_history")
    @patch("claudeutils.validation.tasks.get_new_tasks")
    def test_new_task_in_git_history(
        self,
        mock_new: MagicMock,
        mock_history: MagicMock,
        tmp_path: Path,
    ) -> None:
        """New task found in history is flagged."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n- [ ] **New Task** — desc\n"
        )
        (tmp_path / "learnings.md").write_text("# Learnings\n")
        mock_new.return_value = ["New Task"]
        mock_history.return_value = True
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "exists in git history" in errors[0]

    def test_missing_session_file(self, tmp_path: Path) -> None:
        """Missing session file returns no errors (graceful degradation)."""
        assert validate("nonexistent.md", "nonexistent.md", tmp_path) == []

    def test_missing_learnings_still_validates(self, tmp_path: Path) -> None:
        """Missing learnings file doesn't prevent task validation."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n"
            "- [ ] **Task One** — desc\n- [ ] **Task One** — dup\n"
        )
        errors = validate("session.md", "nonexistent.md", tmp_path)
        assert len(errors) == 1
        assert "duplicate" in errors[0]

    def test_multiple_errors_all_reported(self, tmp_path: Path) -> None:
        """All errors reported, not just first."""
        (tmp_path / "session.md").write_text(
            "# Session\n\n## In-tree Tasks\n\n"
            "- [ ] **Task One** — first\n- [ ] **task one** — dup\n"
            "- [ ] **Learning Key** — conflicts\n"
        )
        (tmp_path / "learnings.md").write_text(
            "# Learnings\n\n## Learning Key\nContent.\n"
        )
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 2
        assert any("duplicate" in e for e in errors)
        assert any("conflicts" in e for e in errors)

    def test_line_numbers_reported(self, tmp_path: Path) -> None:
        """Line numbers reported correctly."""
        (tmp_path / "session.md").write_text(
            "# Session\n\nLine 3\nLine 4\n## In-tree Tasks\n\nLine 7\n"
            "- [ ] **Task One** — line 8\n- [ ] **Task Two** — line 9\n"
            "- [ ] **Task One** — line 10 (duplicate)\n"
        )
        (tmp_path / "learnings.md").write_text("# Learnings\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "line 10" in errors[0]
        assert "first at line 8" in errors[0]
