#!/usr/bin/env python3
"""Recover files written by an agent from its task output log.

Usage:
    recover-agent-writes.py <agent-id> [--list] [--recover <path>] [--recover-all]

Examples:
    # List all files the agent wrote
    recover-agent-writes.py a93b05c --list

    # Recover a specific file
    recover-agent-writes.py a93b05c --recover plans/foo/reports/review.md

    # Recover all files written by the agent
    recover-agent-writes.py a93b05c --recover-all
"""
import json
import sys
from pathlib import Path

TASK_DIR = Path(
    "tmp/claude/claude-501/"
    "-Users-david-code-edify-wt-design-runbook-evolution/tasks"
)


def extract_writes(agent_id: str) -> list[dict]:
    log_file = TASK_DIR / f"{agent_id}.output"
    if not log_file.exists():
        print(f"No log file: {log_file}", file=sys.stderr)
        sys.exit(1)

    writes = []
    for line in log_file.read_text().splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        contents = entry.get("message", {}).get("content", [])
        if not isinstance(contents, list):
            continue

        for block in contents:
            if block.get("type") == "tool_use" and block.get("name") == "Write":
                inp = block.get("input", {})
                if "file_path" in inp and "content" in inp:
                    writes.append(inp)
    return writes


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Recover agent-written files")
    parser.add_argument("agent_id", help="Agent ID from Task tool")
    parser.add_argument("--list", action="store_true", help="List written files")
    parser.add_argument("--recover", metavar="PATH", help="Recover specific file (substring match)")
    parser.add_argument("--recover-all", action="store_true", help="Recover all files")
    args = parser.parse_args()

    writes = extract_writes(args.agent_id)

    if not writes:
        print("No Write calls found in agent log.", file=sys.stderr)
        sys.exit(1)

    if args.list or (not args.recover and not args.recover_all):
        for w in writes:
            size = len(w["content"])
            print(f"  {w['file_path']}  ({size} bytes)")
        return

    targets = writes
    if args.recover:
        targets = [w for w in writes if args.recover in w["file_path"]]
        if not targets:
            print(f"No Write calls matching '{args.recover}'", file=sys.stderr)
            sys.exit(1)

    for w in targets:
        path = Path(w["file_path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(w["content"])
        print(f"Recovered: {path}")


if __name__ == "__main__":
    main()
