"""Validate session.md command semantics.

Checks for anti-patterns in command fields of task lines.
"""

import re

from edify.validation.task_parsing import parse_task_line

COMMAND_ANTI_PATTERNS = [
    (
        re.compile(r"/inline plans/.* execute"),
        "bypasses Phase 2 recall D+B anchor",
    ),
]


# Checkboxes that require a backtick command
_COMMAND_REQUIRED_CHECKBOXES = frozenset({" ", ">"})


def check_command_presence(lines: list[str]) -> list[str]:
    """Validate that pending/in-progress tasks have backtick commands.

    Args:
        lines: File content as list of lines.

    Returns:
        List of error strings with line number and details.
    """
    errors = []

    for i, line in enumerate(lines, 1):
        parsed = parse_task_line(line, lineno=i)
        if not parsed:
            continue
        if parsed.checkbox in _COMMAND_REQUIRED_CHECKBOXES and not parsed.command:
            errors.append(f"  line {i}: missing command in **{parsed.name}**")

    return errors


# Workflow skills that legitimately appear in task commands (C-2)
WORKFLOW_SKILLS = frozenset(
    {
        "requirements",
        "design",
        "runbook",
        "orchestrate",
        "deliverable-review",
        "inline",
        "ground",
    }
)

# Extract skill name from /skill-name prefix
_SKILL_NAME_PATTERN = re.compile(r"^/([a-z][-a-z]*)")


def check_skill_allowlist(lines: list[str]) -> list[str]:
    """Validate that skill commands use allowed workflow skills.

    Only checks pending/in-progress tasks with slash-command prefixed commands.

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
        if parsed.checkbox not in _COMMAND_REQUIRED_CHECKBOXES:
            continue
        m = _SKILL_NAME_PATTERN.match(parsed.command)
        if not m:
            continue
        skill_name = m.group(1)
        if skill_name not in WORKFLOW_SKILLS:
            errors.append(
                f"  line {i}: unknown skill /{skill_name} in **{parsed.name}**"
            )

    return errors


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
