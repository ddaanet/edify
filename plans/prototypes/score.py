#!/usr/bin/env python3
"""WSJF priority scorer — parameterizable.

Usage:
    # Score all tasks (existing + new from JSON):
    python tmp/score.py --new tmp/new-tasks.json

    # Score only new tasks (for delta reports):
    python tmp/score.py --new tmp/new-tasks.json --only-new

    # Override existing tasks file:
    python tmp/score.py --existing tmp/existing.json --new tmp/new-tasks.json

JSON format (array of arrays):
    [["Task name", WF, DP, CRR, ME, CRC, "modifiers"], ...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Default existing tasks — carried forward baseline
DEFAULT_EXISTING: list[tuple[str, int, int, int, int, int, str]] = [
    ("Orchestrate evolution", 5, 5, 8, 1, 2, "sonnet, restart"),
    ("Skill disclosure", 5, 3, 5, 3, 2, "opus"),
    ("Handoff --commit removal", 5, 3, 3, 3, 2, "sonnet"),
    ("Session scraping", 3, 3, 5, 3, 2, "sonnet"),
    ("Worktree merge from main", 3, 3, 5, 3, 2, "sonnet"),
    ("Explore Anthropic plugins", 2, 3, 3, 3, 1, "sonnet, restart"),
    ("Recall tool consolidation", 5, 5, 5, 5, 3, "sonnet"),
    ("Ground workflow skills", 5, 5, 5, 5, 3, "opus"),
    ("Tool deviation hook", 5, 3, 5, 5, 2, "sonnet"),
    ("Markdown migration", 5, 5, 5, 5, 3, "opus"),
    ("Artifact staleness gate", 5, 3, 5, 5, 2, "sonnet"),
    ("Codebase sweep", 2, 2, 3, 3, 1, "sonnet"),
    ("Fix task-context bloat", 5, 2, 3, 5, 1, "sonnet"),
    ("Skill-dev skill", 3, 3, 5, 5, 2, "sonnet"),
    ("Entry gate propagation", 5, 3, 5, 5, 3, "opus"),
    ("Retrofit skill pre-work", 5, 3, 5, 5, 3, "opus"),
    ("Plugin migration", 2, 8, 3, 3, 5, "opus"),
    ("Tweakcc", 3, 2, 3, 3, 2, "sonnet"),
    ("Generate memory index", 3, 3, 5, 5, 3, "opus"),
    ("Agent rule injection", 3, 3, 5, 5, 3, "sonnet"),
    ("Tier threshold grounding", 3, 3, 5, 5, 3, "opus"),
    ("Handoff insertion policy", 3, 2, 3, 5, 1, "sonnet"),
    ("Cross-tree requirements", 3, 3, 3, 5, 2, "sonnet"),
    ("Agentic prose terminology", 2, 1, 1, 2, 1, "sonnet"),
    ("Test diagnostic helper", 3, 2, 3, 5, 1, "sonnet"),
    ("Runbook outline review", 3, 2, 3, 5, 2, "sonnet"),
    ("TDD test optimization", 3, 2, 3, 5, 2, "sonnet"),
    ("Review auto-commit", 3, 2, 3, 5, 2, "sonnet"),
    ("Recall deduplication", 3, 2, 3, 5, 3, "sonnet"),
    ("Recall pipeline", 3, 2, 3, 5, 3, "opus"),
    ("Compensate-continue skill", 3, 2, 3, 5, 3, "opus"),
    ("Upstream skills field", 1, 1, 1, 2, 1, "sonnet"),
    ("Skill prompt-composer", 3, 2, 3, 5, 3, "sonnet"),
    ("Model directive pipeline", 3, 2, 3, 5, 3, "opus"),
    ("Feature prototypes", 2, 2, 2, 5, 2, "sonnet"),
    ("Diagnose compression loss", 2, 2, 3, 5, 3, "sonnet"),
    ("Test diamond migration", 2, 2, 3, 5, 3, "sonnet"),
    ("Safety review expansion", 2, 2, 3, 5, 3, "opus"),
    ("Recall learnings design", 2, 2, 3, 5, 3, "opus"),
    ("Diagnostic opus review", 2, 1, 3, 5, 3, "opus"),
    ("Infrastructure scripts", 2, 1, 2, 5, 2, "sonnet"),
    ("Cache expiration", 2, 1, 2, 5, 2, "sonnet"),
    ("Prioritize script", 2, 1, 2, 5, 2, "sonnet"),
    ("Design-to-deliverable", 3, 2, 3, 8, 5, "opus, restart"),
    ("Prose gate terminology", 2, 1, 1, 5, 3, "opus"),
    ("Ground state coverage", 2, 1, 3, 8, 5, "opus"),
    ("Workflow formal analysis", 2, 1, 3, 8, 5, "opus"),
    ("Behavioral design", 2, 1, 2, 8, 5, "opus"),
    ("Execute flag lint", 5, 2, 5, 3, 1, "haiku"),
    ("Session.md validator", 5, 2, 5, 3, 2, "sonnet"),
    ("Wt ls session ordering", 5, 2, 1, 3, 1, "sonnet"),
    ("Block cd-chaining", 3, 1, 3, 3, 1, "sonnet"),
    ("Remove wt rm --force", 2, 1, 3, 3, 1, "sonnet"),
    ("Memory-index loading docs", 2, 2, 1, 3, 1, "sonnet"),
    ("Moderate outline gate", 3, 3, 3, 5, 3, "opus, self-ref"),
    ("Decision drift audit", 2, 3, 3, 5, 3, "sonnet"),
    ("Registry cache to tmp", 2, 1, 1, 3, 1, "sonnet, inline"),
    ("Dev integration branch", 3, 3, 3, 5, 3, "opus"),
    ("Update prioritize skill", 2, 1, 1, 3, 1, "sonnet"),
    ("Recall usage scoring", 3, 2, 3, 5, 3, "sonnet"),
    ("Delivery supercession", 3, 2, 3, 5, 3, "opus"),
    ("Lint-gated recall", 5, 3, 5, 5, 2, "sonnet"),
    ("Lint recall gate", 5, 3, 5, 5, 2, "sonnet"),
    ("Merge completed filter", 3, 2, 3, 1, 1, "sonnet, inline"),
    ("Merge lock retry", 2, 1, 3, 5, 2, "sonnet"),
    ("Merge lifecycle audit", 3, 3, 5, 3, 3, "sonnet"),
    ("Task notation migration", 1, 1, 1, 3, 1, "sonnet"),
    ("Wt rm task cleanup", 3, 2, 3, 3, 2, "sonnet"),
    ("Design context gate", 3, 3, 3, 3, 3, "sonnet"),
    ("Worktree CLI UX", 3, 1, 3, 5, 2, "sonnet"),
    ("Corrector removal audit", 3, 2, 5, 5, 3, "sonnet"),
    ("Wt merge-rm shorthand", 3, 1, 1, 3, 1, "sonnet"),
    ("Worktree ad-hoc task", 3, 2, 3, 3, 2, "sonnet"),
]


def load_tasks(path: str) -> list[tuple[str, int, int, int, int, int, str]]:
    data = json.loads(Path(path).read_text())
    return [
        (str(t[0]), int(t[1]), int(t[2]), int(t[3]), int(t[4]), int(t[5]), str(t[6]))
        for t in data
    ]


def score_and_rank(
    existing: list[tuple[str, int, int, int, int, int, str]],
    new: list[tuple[str, int, int, int, int, int, str]],
    only_new: bool = False,
) -> None:
    new_names = set(t[0] for t in new)
    all_tasks = new + existing if not only_new else new

    results = []
    for name, wf, dp, crr, me, crc, mods in all_tasks:
        cod = wf + dp + crr
        size = me + crc
        priority = round(cod / size, 1)
        is_new = name in new_names
        results.append((priority, cod, size, wf, dp, crr, me, crc, name, mods, is_new))

    results.sort(key=lambda x: (-x[0], -x[5], x[2]))

    print(
        "| Rank | Task | WF | DP | CRR | CoD | ME | CRC | Size | Priority | Modifiers |"
    )
    print(
        "|------|------|----|----|-----|-----|----|-----|------|----------|-----------|"
    )
    rank = 1
    prev_priority = None
    for i, (pri, cod, size, wf, dp, crr, me, crc, name, mods, is_new) in enumerate(
        results
    ):
        if pri != prev_priority:
            rank = i + 1
            prev_priority = pri
        marker = " *" if is_new else ""
        print(
            f"| {rank} | {name}{marker} | {wf} | {dp} | {crr} | {cod} | {me} | {crc} | {size} | {pri} | {mods} |"
        )

    print(f"\nTotal: {len(results)} tasks")
    print(f"New/rescored: {sum(1 for r in results if r[10])}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="WSJF priority scorer")
    parser.add_argument("--new", help="JSON file with new tasks to score")
    parser.add_argument(
        "--existing", help="JSON file to override default existing tasks"
    )
    parser.add_argument("--only-new", action="store_true", help="Only show new tasks")
    args = parser.parse_args()

    existing = load_tasks(args.existing) if args.existing else DEFAULT_EXISTING
    new = load_tasks(args.new) if args.new else []

    if not new and not args.existing:
        # No args: score default existing as baseline
        score_and_rank(existing, [], only_new=False)
    else:
        score_and_rank(existing, new, only_new=args.only_new)
