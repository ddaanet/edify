#!/usr/bin/env python3
"""Measure Task delegation token overhead across all edify sessions.

Extracts per-Task-call data: total_tokens, prompt_chars, tool_uses, duration_ms,
agent_type, model. Aggregates to show the fixed cost of spinning up any sub-agent
(CLAUDE.md injection + agent definition + system prompt) vs. the variable cost
(prompt content + tool calls).

Data source: ~/.claude/projects/ JSONL session files.
Filters: edify projects only, excludes sidechain entries.

Output: TSV to stdout (for analysis), summary stats to stderr.
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-")
TOTAL_TOKENS_RE = re.compile(r"total_tokens:\s*(\d+)")
TOOL_USES_RE = re.compile(r"tool_uses:\s*(\d+)")
DURATION_RE = re.compile(r"duration_ms:\s*(\d+)")


def extract_task_pairs(entries):
    """Match Task tool_use → tool_result pairs, extract metrics."""
    pending = {}
    pairs = []

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

            if block.get("type") == "tool_use" and block.get("name") == "Task":
                inp = block.get("input", {})
                pending[block["id"]] = {
                    "agent_type": inp.get("subagent_type", "unknown"),
                    "model": inp.get("model", ""),
                    "prompt_chars": len(inp.get("prompt", "")),
                    "description": inp.get("description", ""),
                    "background": bool(inp.get("run_in_background")),
                    "max_turns": inp.get("max_turns"),
                    "timestamp": entry.get("timestamp", ""),
                }

            if block.get("type") == "tool_result":
                tid = block.get("tool_use_id", "")
                if tid not in pending:
                    continue
                call = pending.pop(tid)
                result_text = str(block.get("content", ""))

                tok_m = TOTAL_TOKENS_RE.search(result_text)
                tu_m = TOOL_USES_RE.search(result_text)
                dur_m = DURATION_RE.search(result_text)

                # Only include entries with token data
                if not tok_m:
                    continue

                pairs.append(
                    {
                        **call,
                        "total_tokens": int(tok_m.group(1)),
                        "tool_uses": int(tu_m.group(1)) if tu_m else None,
                        "duration_ms": int(dur_m.group(1)) if dur_m else None,
                    }
                )

    return pairs


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
    p95 = percentile(values, 95)
    print(
        f"  {label} (n={n}): p25={p25:.0f}{unit} p50={p50:.0f}{unit} p75={p75:.0f}{unit} p90={p90:.0f}{unit} p95={p95:.0f}{unit} max={values[-1]:.0f}{unit}",
        file=sys.stderr,
    )


def main():
    all_pairs = []
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

            pairs = extract_task_pairs(entries)
            for p in pairs:
                p["session"] = fname[:8]
                p["project"] = proj_name
            all_pairs.extend(pairs)

    print(f"Sessions scanned: {sessions_scanned}", file=sys.stderr)
    print(f"Task pairs with token data: {len(all_pairs)}", file=sys.stderr)

    # --- TSV output ---
    header = [
        "agent_type",
        "model",
        "prompt_chars",
        "total_tokens",
        "tool_uses",
        "duration_ms",
        "background",
        "session",
        "project",
        "description",
    ]
    print("\t".join(header))
    for p in all_pairs:
        row = [
            p["agent_type"],
            p["model"] or "default",
            str(p["prompt_chars"]),
            str(p["total_tokens"]),
            str(p["tool_uses"]) if p["tool_uses"] is not None else "",
            str(p["duration_ms"]) if p["duration_ms"] is not None else "",
            str(p["background"]),
            p["session"],
            p["project"],
            p["description"][:80],
        ]
        print("\t".join(row))

    # --- Summary stats to stderr ---
    print(f"\n{'=' * 70}", file=sys.stderr)
    print("DELEGATION OVERHEAD SUMMARY", file=sys.stderr)
    print(f"{'=' * 70}", file=sys.stderr)

    # Overall token distribution
    all_tokens = [p["total_tokens"] for p in all_pairs]
    print_dist("All agents: total_tokens", all_tokens)

    # By model
    by_model = defaultdict(list)
    for p in all_pairs:
        by_model[p["model"] or "default"].append(p["total_tokens"])
    for model in sorted(by_model.keys()):
        print_dist(f"  model={model}: total_tokens", by_model[model])

    # Minimum-work agents: tool_uses <= 3 (baseline overhead)
    # These are the closest proxy for "fixed cost of delegation"
    minimal = [
        p for p in all_pairs if p["tool_uses"] is not None and p["tool_uses"] <= 3
    ]
    if minimal:
        print(
            f"\n  Minimal-work agents (tool_uses <= 3, n={len(minimal)}):",
            file=sys.stderr,
        )
        print_dist("    total_tokens", [p["total_tokens"] for p in minimal])
        print_dist("    prompt_chars", [p["prompt_chars"] for p in minimal])

    # By agent type (n >= 3)
    print(f"\n{'=' * 70}", file=sys.stderr)
    print("BY AGENT TYPE (n >= 3)", file=sys.stderr)
    print(f"{'=' * 70}", file=sys.stderr)
    by_type = defaultdict(list)
    for p in all_pairs:
        by_type[p["agent_type"]].append(p)
    for agent_type in sorted(by_type.keys(), key=lambda k: -len(by_type[k])):
        agents = by_type[agent_type]
        if len(agents) < 3:
            continue
        tokens = [a["total_tokens"] for a in agents]
        prompts = [a["prompt_chars"] for a in agents]
        tools = [a["tool_uses"] for a in agents if a["tool_uses"] is not None]
        print(f"\n  {agent_type} (n={len(agents)}):", file=sys.stderr)
        print_dist("    total_tokens", tokens)
        print_dist("    prompt_chars", prompts)
        if tools:
            print_dist("    tool_uses", tools)

    # Token-per-tool-use (marginal cost per tool call)
    print(f"\n{'=' * 70}", file=sys.stderr)
    print("MARGINAL COST (tokens per tool use)", file=sys.stderr)
    print(f"{'=' * 70}", file=sys.stderr)
    with_both = [
        (p["total_tokens"], p["tool_uses"])
        for p in all_pairs
        if p["tool_uses"] is not None and p["tool_uses"] > 0
    ]
    if with_both:
        per_tool = [t / u for t, u in with_both]
        print_dist("tokens_per_tool_use", per_tool)

    # Explore vs execution agents (baseline comparison)
    explore = [
        p["total_tokens"]
        for p in all_pairs
        if p["agent_type"] in ("Explore", "quiet-explore")
    ]
    execution = [
        p["total_tokens"]
        for p in all_pairs
        if p["agent_type"].endswith("-task")
        or p["agent_type"] in ("tdd-task", "quiet-task", "refactor")
    ]
    review = [
        p["total_tokens"]
        for p in all_pairs
        if "vet" in p["agent_type"]
        or "review" in p["agent_type"]
        or "reviewer" in p["agent_type"]
    ]
    if explore:
        print_dist("  explore agents: total_tokens", explore)
    if execution:
        print_dist("  execution agents: total_tokens", execution)
    if review:
        print_dist("  review agents: total_tokens", review)


if __name__ == "__main__":
    main()
