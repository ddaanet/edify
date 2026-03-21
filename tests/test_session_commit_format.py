"""Tests for commit output formatting (Cycle 6.5)."""

from __future__ import annotations

from claudeutils.session.commit_pipeline import format_commit_output

# Cycle 6.5: output formatting


def test_format_success_parent() -> None:
    """Parent-only success: raw git output, no prefix."""
    output = format_commit_output(
        parent_output=(
            "[main a7f38c2] ✨ Add commit CLI\n"
            " 3 files changed, 142 insertions(+), 8 deletions(-)"
        ),
    )
    assert "[main a7f38c2]" in output
    assert "3 files changed" in output
    # No submodule prefix
    assert ":" not in output.split("\n")[0] or "a7f38c2]" in output


def test_format_success_submodule() -> None:
    """Submodule success: labeled with path, parent unlabeled."""
    output = format_commit_output(
        submodule_outputs={
            "agent-core": (
                "[main 4b2c1a0] 🤖 Update fragment\n"
                " 1 file changed, 5 insertions(+), 2 deletions(-)"
            ),
        },
        parent_output=(
            "[main a7f38c2] ✨ Add commit CLI\n"
            " 4 files changed, 142 insertions(+), 8 deletions(-)"
        ),
    )
    assert "agent-core:" in output
    # Submodule output appears before parent
    assert output.index("agent-core:") < output.index("Add commit CLI")


def test_format_warning() -> None:
    """Warning prepended before git output."""
    output = format_commit_output(
        warnings=[
            "## Submodule agent-core has no matching files",
        ],
        parent_output="[main a7f38c2] ✨ Add commit CLI",
    )
    assert "**Warning:**" in output
    assert output.index("**Warning:**") < output.index("Add commit CLI")


def test_format_strips_hints() -> None:
    """Git hint/advice lines stripped from output."""
    output = format_commit_output(
        parent_output=(
            "[main abc1234] msg\nhint: some advice\nhint: more advice\n 1 file changed"
        ),
    )
    assert "hint:" not in output
    assert "1 file changed" in output
