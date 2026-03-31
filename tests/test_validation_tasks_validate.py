"""Tests for tasks validator - validate function."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from edify.validation.tasks import validate


class TestValidate:
    """Tests for validate function."""

    def test_valid_session_returns_no_errors(self, tmp_path: Path) -> None:
        """Test that valid session returns no errors."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## In-tree Tasks

- [ ] **Task One** — description
- [ ] **Task Two** — another task
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("""# Learnings

## Some Learning
""")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert errors == []

    def test_duplicate_task_names_detected(self, tmp_path: Path) -> None:
        """Test that duplicate task names are detected."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## In-tree Tasks

- [ ] **Task One** — first
- [ ] **Task Two** — second
- [ ] **Task One** — duplicate
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("# Learnings\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "duplicate task name" in errors[0]
        assert "Task One" in errors[0]

    def test_duplicate_task_names_case_insensitive(self, tmp_path: Path) -> None:
        """Test that duplicate detection is case-insensitive."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## In-tree Tasks

- [ ] **Task One** — first
- [ ] **task one** — duplicate
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("# Learnings\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "duplicate" in errors[0]

    def test_task_conflicts_with_learning_key(self, tmp_path: Path) -> None:
        """Test that task names conflicting with learning keys are detected."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## In-tree Tasks

- [ ] **Conflicting Task** — description
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("""# Learnings

## Conflicting Task
Content here.
""")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "task name conflicts with learning key" in errors[0]
        assert "Conflicting Task" in errors[0]

    def test_task_conflict_case_insensitive(self, tmp_path: Path) -> None:
        """Test that conflict detection is case-insensitive."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## In-tree Tasks

- [ ] **conflicting task** — description
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("""# Learnings

## Conflicting Task
""")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "conflicts" in errors[0]

    @patch("edify.validation.tasks.check_history")
    @patch("edify.validation.tasks.get_new_tasks")
    def test_new_task_in_git_history_error(
        self,
        mock_get_new: MagicMock,
        mock_check_history: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test that new task found in history is flagged."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## In-tree Tasks

- [ ] **New Task** — description
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("# Learnings\n")
        mock_get_new.return_value = ["New Task"]
        mock_check_history.return_value = True
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "exists in git history" in errors[0]
        assert "New Task" in errors[0]

    def test_missing_session_file_returns_no_errors(self, tmp_path: Path) -> None:
        """Test that missing session file returns no errors.

        Graceful degradation behavior.
        """
        errors = validate("nonexistent.md", "nonexistent.md", tmp_path)
        assert errors == []

    def test_missing_learnings_file_still_validates_tasks(self, tmp_path: Path) -> None:
        """Test that missing learnings file validation continues.

        Missing learnings file doesn't prevent task validation.
        """
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## In-tree Tasks

- [ ] **Task One** — description
- [ ] **Task One** — duplicate
""")
        errors = validate("session.md", "nonexistent.md", tmp_path)
        assert len(errors) == 1
        assert "duplicate" in errors[0]

    def test_multiple_errors_all_reported(self, tmp_path: Path) -> None:
        """Test that all errors are reported, not just first."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

## In-tree Tasks

- [ ] **Task One** — first
- [ ] **task one** — duplicate
- [ ] **Learning Key** — conflicts
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("""# Learnings

## Learning Key
Content.
""")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 2
        assert any("duplicate" in e for e in errors)
        assert any("conflicts" in e for e in errors)

    def test_line_numbers_reported_correctly(self, tmp_path: Path) -> None:
        """Test that line numbers are reported correctly."""
        session_file = tmp_path / "session.md"
        session_file.write_text("""# Session Handoff

Line 3
Line 4
## In-tree Tasks

Line 7
- [ ] **Task One** — line 8
- [ ] **Task Two** — line 9
- [ ] **Task One** — line 10 (duplicate)
""")
        learnings_file = tmp_path / "learnings.md"
        learnings_file.write_text("# Learnings\n")
        errors = validate("session.md", "learnings.md", tmp_path)
        assert len(errors) == 1
        assert "line 10" in errors[0]
        assert "first at line 8" in errors[0]
