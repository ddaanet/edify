"""Handoff context: diagnostic output formatting."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PrecommitResult:
    """Result of a precommit validation run."""

    passed: bool
    output: str


def format_diagnostics(
    precommit: PrecommitResult,
    git_output: str | None,
    learnings_age_days: int | None,
) -> str:
    """Format handoff diagnostics as structured markdown.

    Args:
        precommit: Result of running the precommit check.
        git_output: Combined git status/diff output; only shown on pass.
        learnings_age_days: Number of learnings entries aged ≥7 days;
            None if none qualify.

    Returns:
        Markdown-formatted diagnostic string.
    """
    sections: list[str] = []

    status = "✓ passed" if precommit.passed else "✗ failed"
    sections.append(f"**Precommit:** {status}\n\n```\n{precommit.output}\n```")

    if precommit.passed and git_output:
        sections.append(f"**Git status:**\n\n```\n{git_output}\n```")

    if learnings_age_days is not None and learnings_age_days >= 7:
        sections.append(
            f"**Learnings:** {learnings_age_days} entries ≥7 days — consider /codify"
        )

    return "\n\n".join(sections)
