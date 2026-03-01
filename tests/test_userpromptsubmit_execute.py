"""Tests for execute command injection (FR-2).

UserPromptSubmit hook parses session.md when `x` shortcut fires,
extracting task commands for injection into additionalContext.
"""

from pathlib import Path

import pytest

from tests.ups_hook_helpers import call_hook


class TestExecuteCommandInjection:
    """Test FR-2: x shortcut injects task command from session.md."""

    def test_x_injects_pending_task_command(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """X with session.md pending task injects Invoke directive."""
        session_dir = tmp_path / "agents"
        session_dir.mkdir()
        (session_dir / "session.md").write_text(
            "## Pending Tasks\n\n"
            "- [ ] **Do something** — `/design my-requirements` | sonnet\n"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        result = call_hook("x")
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "Invoke: /design my-requirements" in ctx

    def test_x_skips_non_eligible_tasks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """X skips completed, blocked, failed, and canceled tasks."""
        session_dir = tmp_path / "agents"
        session_dir.mkdir()
        (session_dir / "session.md").write_text(
            "## Pending Tasks\n\n"
            "- [x] **Done task** — `/commit` | sonnet\n"
            "- [!] **Blocked task** — `/orchestrate blocked-job` | sonnet\n"
            "- [\u2717] **Failed task** — `/design failed-thing` | opus\n"
            "- [\u2013] **Canceled task** — `/runbook canceled-thing` | sonnet\n"
            "- [ ] **Actual pending** — `/runbook actual-work` | sonnet\n"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        result = call_hook("x")
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "Invoke: /runbook actual-work" in ctx
        # Must NOT inject commands from non-eligible tasks
        assert "Invoke: /commit" not in ctx
        assert "blocked-job" not in ctx
        assert "failed-thing" not in ctx
        assert "canceled-thing" not in ctx

    def test_x_prefers_in_progress_task(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """X extracts in-progress [>] task command over pending [ ] task."""
        session_dir = tmp_path / "agents"
        session_dir.mkdir()
        (session_dir / "session.md").write_text(
            "## Pending Tasks\n\n"
            "- [>] **Resumable task** — `/orchestrate my-job` | sonnet\n"
            "- [ ] **Next pending** — `/design other-thing` | sonnet\n"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        result = call_hook("x")
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "Invoke: /orchestrate my-job" in ctx
        assert "other-thing" not in ctx

    def test_x_fallback_no_session_md(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """X without session.md uses generic expansion only."""
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        result = call_hook("x")
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "[#execute]" in ctx
        assert "Invoke:" not in ctx

    def test_x_fallback_no_eligible_tasks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """X with no eligible tasks uses generic expansion.

        When session.md contains only non-eligible tasks, x falls back to the
        generic [#execute] expansion without Invoke directive.
        """
        session_dir = tmp_path / "agents"
        session_dir.mkdir()
        (session_dir / "session.md").write_text(
            "## Pending Tasks\n\n"
            "- [x] **Done** — `/commit` | sonnet\n"
            "- [!] **Blocked** — `/orchestrate something` | sonnet\n"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        result = call_hook("x")
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "[#execute]" in ctx
        assert "Invoke:" not in ctx

    def test_x_uses_planstate_command_over_session(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Planstate-derived command takes priority over session.md command."""
        session_dir = tmp_path / "agents"
        session_dir.mkdir()
        (session_dir / "session.md").write_text(
            "## Pending Tasks\n\n"
            "- [ ] **My task** — `/design my-plan` | sonnet\n"
            "  - Plan: my-plan | Status: requirements\n"
        )
        # Create plan directory with design.md so planstate infers "designed"
        plan_dir = tmp_path / "plans" / "my-plan"
        plan_dir.mkdir(parents=True)
        (plan_dir / "design.md").write_text("# Design\n")
        (plan_dir / "requirements.md").write_text("# Requirements\n")

        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        result = call_hook("x")
        ctx = result["hookSpecificOutput"]["additionalContext"]
        # Planstate "designed" -> runbook command, not session.md /design
        assert "Invoke: /runbook plans/my-plan/design.md" in ctx


class TestExecuteBackwardCompat:
    """Confirm non-x modes are unaffected by inject logic (C-3)."""

    def test_xc_does_not_inject(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """XC mode does not inject Invoke directive (C-3 backward compat)."""
        session_dir = tmp_path / "agents"
        session_dir.mkdir()
        (session_dir / "session.md").write_text(
            "## Pending Tasks\n\n"
            "- [ ] **Do something** — `/design my-requirements` | sonnet\n"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        result = call_hook("xc")
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "[execute, commit]" in ctx
        assert "Invoke:" not in ctx

    def test_r_does_not_inject(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Resume mode does not inject Invoke directive (C-3)."""
        session_dir = tmp_path / "agents"
        session_dir.mkdir()
        (session_dir / "session.md").write_text(
            "## Pending Tasks\n\n"
            "- [ ] **Do something** — `/design my-requirements` | sonnet\n"
        )
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
        result = call_hook("r")
        ctx = result["hookSpecificOutput"]["additionalContext"]
        assert "[#resume]" in ctx
        assert "Invoke:" not in ctx
