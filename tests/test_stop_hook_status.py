"""Tests for stop hook status display module."""

import pytest

from claudeutils.hooks.stop_status_display import (
    format_ansi,
    process_hook,
    should_trigger,
)


class TestShouldTrigger:
    """Parametrized tests for trigger detection."""

    @pytest.mark.parametrize(
        ("message", "expected"),
        [
            ("Status.", True),
            ("Check the Status.", False),
            ("Status", False),
            ("Status.\nMore text", False),
            ("", False),
        ],
    )
    def test_should_trigger(
        self,
        message: str,
        expected: bool,  # noqa: FBT001
    ) -> None:
        """Test trigger detection with various inputs."""
        assert should_trigger(message) is expected


class TestFormatAnsi:
    """Test ANSI reset formatting."""

    def test_format_ansi_single_line(self) -> None:
        """Each line starts with ANSI reset."""
        result = format_ansi("line1")
        assert result.startswith("\033[0m")

    def test_format_ansi_multiple_lines(self) -> None:
        """Each line gets ANSI reset prepended."""
        result = format_ansi("line1\nline2\nline3")
        lines = result.split("\n")
        for line in lines:
            if line:
                assert line.startswith("\033[0m"), f"Line '{line}' missing reset"

    def test_format_ansi_empty_string(self) -> None:
        """Empty string still gets ANSI reset."""
        result = format_ansi("")
        assert result.startswith("\033[0m")


class TestProcessHookLoopGuard:
    """Test loop guard in process_hook."""

    def test_process_hook_loop_guard_active(self) -> None:
        """Returns None when stop_hook_active is True."""
        result = process_hook(
            {
                "last_assistant_message": "Status.",
                "stop_hook_active": True,
            }
        )
        assert result is None

    def test_process_hook_triggered_with_status(self) -> None:
        """Returns systemMessage when triggered.

        Uses mock status_fn to avoid CLI dependency.
        """
        result = process_hook(
            {
                "last_assistant_message": "Status.",
                "stop_hook_active": False,
            },
            status_fn=lambda: "mock status output",
        )
        assert result is not None
        assert "systemMessage" in result

    def test_process_hook_uses_status_fn(self) -> None:
        """Injects status output into systemMessage with ANSI."""
        result = process_hook(
            {
                "last_assistant_message": "Status.",
                "stop_hook_active": False,
            },
            status_fn=lambda: "mock output",
        )
        assert result is not None
        assert "systemMessage" in result
        assert "mock output" in result["systemMessage"]
        assert "\033[0m" in result["systemMessage"]

    def test_process_hook_status_failure(self) -> None:
        """Falls back to unavailable message on status error."""

        def raises_exception() -> str:
            raise RuntimeError("fail")

        result = process_hook(
            {
                "last_assistant_message": "Status.",
                "stop_hook_active": False,
            },
            status_fn=raises_exception,
        )
        assert result is not None
        assert "systemMessage" in result
        assert "Status unavailable" in result["systemMessage"]
