#!/usr/bin/env python3
"""Measure orchestrator inline edit cost — token consumption for direct edits.

Finds assistant turns that contain Read/Edit/Write tool calls (inline work)
WITHOUT Task delegation. Measures the token footprint of doing work directly
vs. delegating to a sub-agent.

Session JSONL entries don't carry per-turn token counts for the main session,
but we can measure:
- Tool call count per inline-edit sequence (between Task calls or session boundaries)
- Prompt size (chars) of Read/Edit/Write inputs
- Content size read/written

This gives a proxy for orchestrator context consumption when doing edits inline.

Data source: ~/.claude/projects/ JSONL session files.
Filters: edify projects only, excludes sidechain entries.

Output: TSV to stdout, summary to stderr.
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-")

EDIT_TOOLS = {"Read", "Edit", "Write", "Glob", "Grep"}
DELEGATION_TOOLS = {"Task"}


def extract_inline_sequences(entries):
    """Find sequences of inline tool calls between Task calls.

    Returns list of dicts describing each inline-edit sequence:
    - tool_calls: [{name, input_size}]
    - total_input_chars: sum of all tool input sizes
    - read_chars: chars read via Read tool
    - write_chars: chars written via Write/Edit
    - n_tools: count of tool calls
    - context: what happened before/after (task/start/end)
    """
    sequences = []
    current_seq = []
    current_input_chars = 0
    current_read_chars = 0
    current_write_chars = 0
    prev_context = "start"

    def flush_seq(next_context):
        nonlocal \
            current_seq, \
            current_input_chars, \
            current_read_chars, \
            current_write_chars, \
            prev_context
        if current_seq:
            # Only include sequences with at least one edit operation
            has_edit = any(tc["name"] in ("Edit", "Write") for tc in current_seq)
            if has_edit:
                sequences.append(
                    {
                        "tool_calls": current_seq,
                        "total_input_chars": current_input_chars,
                        "read_chars": current_read_chars,
                        "write_chars": current_write_chars,
                        "n_tools": len(current_seq),
                        "n_edits": sum(
                            1 for tc in current_seq if tc["name"] in ("Edit", "Write")
                        ),
                        "n_reads": sum(1 for tc in current_seq if tc["name"] == "Read"),
                        "prev_context": prev_context,
                        "next_context": next_context,
                    }
                )
        current_seq = []
        current_input_chars = 0
        current_read_chars = 0
        current_write_chars = 0
        prev_context = next_context

    for entry in entries:
        if entry.get("isSidechain"):
            continue
        msg = entry.get("message", {})
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue

            name = block.get("name", "")
            inp = block.get("input", {})

            if name in DELEGATION_TOOLS:
                flush_seq("task")
                continue

            if name in EDIT_TOOLS:
                input_size = sum(len(str(v)) for v in inp.values())
                tc = {"name": name, "input_size": input_size}

                if name == "Read":
                    # Approximate: content size unknown from tool_use,
                    # but file_path gives us what was targeted
                    current_read_chars += len(inp.get("file_path", ""))
                elif name == "Write":
                    content_len = len(inp.get("content", ""))
                    current_write_chars += content_len
                    tc["content_chars"] = content_len
                elif name == "Edit":
                    old_len = len(inp.get("old_string", ""))
                    new_len = len(inp.get("new_string", ""))
                    current_write_chars += new_len
                    tc["old_chars"] = old_len
                    tc["new_chars"] = new_len

                current_seq.append(tc)
                current_input_chars += input_size

    flush_seq("end")
    return sequences


def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    k = (len(values) - 1) * p / 100.0
    f = int(k)
    c = min(f + 1, len(values) - 1)
    return values[f] + (k - f) * (values[c] - values[f])


def print_dist(label, values, unit=""):
    if not values:
        print(f"  {label}: no data", file=sys.stderr)
        return
    values = sorted(values)
    n = len(values)
    p25 = percentile(values, 25)
    p50 = percentile(values, 50)
    p75 = percentile(values, 75)
    p90 = percentile(values, 90)
    print(
        f"  {label} (n={n}): p25={p25:.0f}{unit} p50={p50:.0f}{unit} p75={p75:.0f}{unit} p90={p90:.0f}{unit} max={values[-1]:.0f}{unit}",
        file=sys.stderr,
    )


def main():
    all_seqs = []
    sessions_scanned = 0

    for proj_name in sorted(os.listdir(CLAUDE_PROJECTS_DIR)):
        if "edify" not in proj_name:
            continue
        proj_path = CLAUDE_PROJECTS_DIR / proj_name
        if not proj_path.is_dir():
            continue

        for fname in os.listdir(proj_path):
            if not fname.endswith(".jsonl") or not UUID_RE.match(fname):
                continue
            sessions_scanned += 1

            entries = []
            try:
                with open(proj_path / fname) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                entries.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
            except OSError:
                continue

            seqs = extract_inline_sequences(entries)
            for s in seqs:
                s["session"] = fname[:8]
                s["project"] = proj_name
            all_seqs.extend(seqs)

    print(f"Sessions scanned: {sessions_scanned}", file=sys.stderr)
    print(f"Inline-edit sequences found: {len(all_seqs)}", file=sys.stderr)

    # --- TSV output ---
    header = [
        "n_tools",
        "n_edits",
        "n_reads",
        "total_input_chars",
        "write_chars",
        "prev_context",
        "next_context",
        "session",
        "project",
    ]
    print("\t".join(header))
    for s in all_seqs:
        row = [
            str(s["n_tools"]),
            str(s["n_edits"]),
            str(s["n_reads"]),
            str(s["total_input_chars"]),
            str(s["write_chars"]),
            s["prev_context"],
            s["next_context"],
            s["session"],
            s["project"],
        ]
        print("\t".join(row))

    # --- Summary stats ---
    print(f"\n{'=' * 70}", file=sys.stderr)
    print("INLINE EDIT SEQUENCE SUMMARY", file=sys.stderr)
    print(f"{'=' * 70}", file=sys.stderr)

    print_dist("tools per sequence", [s["n_tools"] for s in all_seqs])
    print_dist("edits per sequence", [s["n_edits"] for s in all_seqs])
    print_dist("reads per sequence", [s["n_reads"] for s in all_seqs])
    print_dist("input chars per sequence", [s["total_input_chars"] for s in all_seqs])
    print_dist("write chars per sequence", [s["write_chars"] for s in all_seqs])

    # Sequences between Task calls (orchestrator doing inline work between delegations)
    between_tasks = [
        s
        for s in all_seqs
        if s["prev_context"] == "task" and s["next_context"] == "task"
    ]
    if between_tasks:
        print(
            f"\n  Between-task sequences (orchestrator inline, n={len(between_tasks)}):",
            file=sys.stderr,
        )
        print_dist("    tools", [s["n_tools"] for s in between_tasks])
        print_dist("    edits", [s["n_edits"] for s in between_tasks])
        print_dist("    write_chars", [s["write_chars"] for s in between_tasks])

    # Distribution of sequence sizes (how much work is typically done inline)
    print(f"\n{'=' * 70}", file=sys.stderr)
    print("INLINE SEQUENCE SIZE DISTRIBUTION", file=sys.stderr)
    print(f"{'=' * 70}", file=sys.stderr)
    size_buckets = defaultdict(int)
    for s in all_seqs:
        n = s["n_edits"]
        if n <= 1:
            size_buckets["1 edit"] += 1
        elif n <= 3:
            size_buckets["2-3 edits"] += 1
        elif n <= 5:
            size_buckets["4-5 edits"] += 1
        elif n <= 10:
            size_buckets["6-10 edits"] += 1
        else:
            size_buckets["11+ edits"] += 1

    total = len(all_seqs)
    for bucket in ["1 edit", "2-3 edits", "4-5 edits", "6-10 edits", "11+ edits"]:
        count = size_buckets.get(bucket, 0)
        pct = count / total * 100 if total else 0
        bar = "#" * int(pct / 2)
        print(f"  {bucket:12s}: {count:4d} ({pct:5.1f}%) {bar}", file=sys.stderr)


if __name__ == "__main__":
    main()
