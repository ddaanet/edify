"""Validate session.md command semantics.

Checks for anti-patterns in command fields of task lines.
"""

import re

from claudeutils.validation.task_parsing import parse_task_line

COMMAND_ANTI_PATTERNS = [
    (
        re.compile(r"/inline plans/.* execute"),
        "bypasses Phase 2 recall D+B anchor",
    ),
]


def check_command_semantics(lines: list[str]) -> list[str]:
    """Validate command fields in task lines for anti-patterns.

    Args:
        lines: File content as list of lines.

    Returns:
        List of error strings with line number and details.
    """
    errors = []

    for i, line in enumerate(lines, 1):
        parsed = parse_task_line(line, lineno=i)
        if not parsed or not parsed.command:
            continue

        for pattern, description in COMMAND_ANTI_PATTERNS:
            if pattern.search(parsed.command):
                errors.append(
                    f"  line {i}: command anti-pattern in **{parsed.name}**: "
                    f"{description}"
                )

    return errors
