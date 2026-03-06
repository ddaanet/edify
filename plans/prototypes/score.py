#!/usr/bin/env python3
"""WSJF priority scoring: JSON stdin → markdown table stdout.

Usage:
    echo '<json>' | python3 plans/prototypes/score.py

Input: JSON array of task objects on stdin.
Output: Markdown priority table on stdout.

Each task object:
{
    "task": "Task Name",
    "wf": 5,       # Workflow Friction (1-8)
    "dp": 3,       # Decay Pressure (1-8)
    "crr": 5,      # Compound Risk Reduction (1-8)
    "me": 2,       # Marginal Effort (1-8)
    "crc": 1,      # Context Recovery Cost (1-5)
    "modifiers": "sonnet"  # optional scheduling modifiers
}
"""

import json
import sys

FIBONACCI = {1, 2, 3, 5, 8}
CRC_MAX = 5
REQUIRED_FIELDS = {"task", "wf", "dp", "crr", "me", "crc"}


def validate_task(task: dict, index: int) -> list[str]:
    """Validate a single task object.

    Returns list of error messages.
    """
    errors = []
    missing = REQUIRED_FIELDS - set(task.keys())
    if missing:
        errors.append(f"Task {index}: missing fields: {', '.join(sorted(missing))}")
        return errors

    for field in ("wf", "dp", "crr", "me"):
        val = task[field]
        if val not in FIBONACCI:
            errors.append(
                f"Task {index} ({task['task']}): {field}={val} not in Fibonacci {{1,2,3,5,8}}"
            )

    crc = task["crc"]
    if crc not in FIBONACCI or crc > CRC_MAX:
        errors.append(
            f"Task {index} ({task['task']}): crc={crc} not in {{1,2,3,5}} (capped at {CRC_MAX})"
        )

    return errors


def score_task(task: dict) -> dict:
    """Compute CoD, Size, Priority for a validated task."""
    cod = task["wf"] + task["dp"] + task["crr"]
    size = task["me"] + task["crc"]
    priority = round(cod / size, 1)
    return {**task, "cod": cod, "size": size, "priority": priority}


def tiebreak_key(task: dict) -> tuple:
    """Sort key: higher priority first, then tiebreakers.

    Tiebreaking (all descending — higher wins):
    1. Higher CRR (defect fixes compound)
    2. Lower Size (smaller unblocks faster) → negate for descending
    3. Higher WF (more frequent pain)
    """
    return (-task["priority"], -task["crr"], task["size"], -task["wf"])


def format_table(scored: list[dict]) -> str:
    """Format scored tasks as markdown priority table."""
    lines = []
    lines.append(
        "| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |"
    )
    lines.append(
        "|------|------|----|----|-----|-----|----|-----|------|----------|-----------|"
    )
    for rank, t in enumerate(scored, 1):
        modifiers = t.get("modifiers", "")
        lines.append(
            f"| {rank} | {t['task']} | {t['wf']} | {t['dp']} | {t['crr']} "
            f"| {t['cod']} | {t['me']} | {t['crc']} | {t['size']} "
            f"| {t['priority']} | {modifiers} |"
        )
    return "\n".join(lines)


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stdout)
        return 1

    if not isinstance(data, list):
        print("Input must be a JSON array of task objects.", file=sys.stdout)
        return 1

    if not data:
        print("Empty task list.", file=sys.stdout)
        return 1

    # Validate all tasks
    errors = []
    for i, task in enumerate(data):
        errors.extend(validate_task(task, i))

    if errors:
        for err in errors:
            print(err, file=sys.stdout)
        return 1

    # Score and sort
    scored = [score_task(t) for t in data]
    scored.sort(key=tiebreak_key)

    print(format_table(scored))
    return 0


if __name__ == "__main__":
    sys.exit(main())
