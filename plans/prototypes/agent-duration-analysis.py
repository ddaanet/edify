#!/usr/bin/env python3
"""Analyze sub-agent execution durations and tool use counts for timeout calibration.

Extracts Task tool call data from Claude session JSONL files across all projects.
Dual measurement: duration_ms from usage metadata (when available, post-W06 2026),
timestamp delta with gap detection as fallback.

Sleep detection: entries with both duration_ms and tool_uses where seconds-per-tool-use
exceeds SUSPECT_PER_TOOL_THRESHOLD are flagged as sleep-inflated (laptop suspend during
agent execution inflates wall-clock time without proportional tool use increase).
Normal p50 is ~6s/tool, p95 ~19s/tool.

Filters for orchestration-relevant agents: review, execution, remember, factorize.
"""
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration ---

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-")

# Agents relevant to orchestration timeout calibration
REVIEW_AGENTS = {
    "vet-fix-agent", "vet-agent", "design-vet-agent",
    "outline-review-agent", "runbook-outline-review-agent",
    "plan-reviewer", "tdd-plan-reviewer",
    "plugin-dev:skill-reviewer", "plugin-dev:agent-creator",
    "review-tdd-process",
}
EXECUTION_AGENTS_SUFFIX = "-task"  # *-task pattern
EXECUTION_AGENTS_EXACT = {
    "tdd-task", "quiet-task", "refactor",
    "pushback-task", "when-recall-task",
    "workflow-rca-fixes-task",
}
MEMORY_AGENTS = {"remember-task", "memory-refactor"}
EXPLORATION_AGENTS = {"Explore", "quiet-explore", "Plan"}
GUIDE_AGENTS = {"claude-code-guide"}

# Max plausible duration for timestamp fallback (10 min)
# Anything longer is likely a session gap
MAX_PLAUSIBLE_DELTA_S = 600

# Sleep detection: if seconds-per-tool-use exceeds this, duration is suspect
# Normal distribution: p50=6s, p90=12s, p95=19s
SUSPECT_PER_TOOL_THRESHOLD = 30

# Usage metadata patterns
DURATION_RE = re.compile(r"duration_ms:\s*(\d+)")
TOOL_USES_RE = re.compile(r"tool_uses:\s*(\d+)")
TOTAL_TOKENS_RE = re.compile(r"total_tokens:\s*(\d+)")


def classify_agent(agent_type):
    """Classify agent into a category for grouping."""
    if agent_type in REVIEW_AGENTS:
        return "review"
    if agent_type in MEMORY_AGENTS:
        return "memory"
    if agent_type in EXPLORATION_AGENTS:
        return "exploration"
    if agent_type in GUIDE_AGENTS:
        return "guide"
    if agent_type in EXECUTION_AGENTS_EXACT or agent_type.endswith(EXECUTION_AGENTS_SUFFIX):
        return "execution"
    return None  # not in filter set


def parse_timestamp(ts_str):
    """Parse ISO timestamp to datetime."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def extract_task_data(entries):
    """Extract Task tool call data from session entries.

    Returns list of dicts with: agent_type, category, duration_s, tool_uses,
    total_tokens, source (metadata|timestamp), timestamp, description, background.
    """
    results = []

    # Index: tool_use_id -> {timestamp, agent_type, description, background}
    pending_calls = {}

    for entry in entries:
        if entry.get("isSidechain"):
            continue

        ts = entry.get("timestamp", "")
        msg = entry.get("message", {})
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue

            # Task tool_use: record pending call
            if block.get("type") == "tool_use" and block.get("name") == "Task":
                inp = block.get("input", {})
                agent_type = inp.get("subagent_type", "unknown")
                pending_calls[block["id"]] = {
                    "timestamp": ts,
                    "agent_type": agent_type,
                    "description": inp.get("description", ""),
                    "background": bool(inp.get("run_in_background")),
                    "model": inp.get("model", ""),
                    "max_turns": inp.get("max_turns"),
                }

            # Task tool_result: match to pending call
            if block.get("type") == "tool_result":
                tid = block.get("tool_use_id", "")
                if tid not in pending_calls:
                    continue

                call = pending_calls.pop(tid)
                agent_type = call["agent_type"]
                category = classify_agent(agent_type)

                result_text = str(block.get("content", ""))

                # Try metadata first
                dur_match = DURATION_RE.search(result_text)
                tu_match = TOOL_USES_RE.search(result_text)
                tok_match = TOTAL_TOKENS_RE.search(result_text)

                duration_s = None
                tool_uses = None
                total_tokens = None
                source = None

                if dur_match:
                    duration_s = int(dur_match.group(1)) / 1000.0
                    source = "metadata"
                if tu_match:
                    tool_uses = int(tu_match.group(1))
                if tok_match:
                    total_tokens = int(tok_match.group(1))

                # Fallback: timestamp delta (skip background tasks)
                if duration_s is None and not call["background"]:
                    t0 = parse_timestamp(call["timestamp"])
                    t1 = parse_timestamp(ts)
                    if t0 and t1:
                        delta = (t1 - t0).total_seconds()
                        if 1 < delta <= MAX_PLAUSIBLE_DELTA_S:
                            duration_s = delta
                            source = "timestamp"
                        # else: likely session gap or sub-second (background)

                if duration_s is not None or tool_uses is not None:
                    results.append({
                        "agent_type": agent_type,
                        "category": category,
                        "duration_s": duration_s,
                        "tool_uses": tool_uses,
                        "total_tokens": total_tokens,
                        "source": source,
                        "timestamp": call["timestamp"][:10],
                        "description": call["description"],
                        "background": call["background"],
                        "model": call["model"],
                        "max_turns": call["max_turns"],
                    })

    return results


def percentile(values, p):
    """Compute p-th percentile (0-100) of sorted values."""
    if not values:
        return 0
    k = (len(values) - 1) * p / 100.0
    f = int(k)
    c = f + 1
    if c >= len(values):
        return values[-1]
    return values[f] + (k - f) * (values[c] - values[f])


def print_distribution(label, values, unit="s"):
    """Print distribution summary for a list of numeric values."""
    if not values:
        print(f"  {label}: no data")
        return
    values = sorted(values)
    n = len(values)
    p50 = percentile(values, 50)
    p75 = percentile(values, 75)
    p90 = percentile(values, 90)
    p95 = percentile(values, 95)
    p99 = percentile(values, 99)
    mx = values[-1]
    print(f"  {label} (n={n}): p50={p50:.0f}{unit} p75={p75:.0f}{unit} p90={p90:.0f}{unit} p95={p95:.0f}{unit} p99={p99:.0f}{unit} max={mx:.0f}{unit}")


def main():
    all_data = []
    sessions_scanned = 0

    for proj_dir_name in sorted(os.listdir(CLAUDE_PROJECTS_DIR)):
        proj_path = CLAUDE_PROJECTS_DIR / proj_dir_name
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
                        if not line:
                            continue
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
            except OSError:
                continue

            data = extract_task_data(entries)
            all_data.extend(data)

    # --- Partition into clean vs suspect ---
    print(f"Sessions scanned: {sessions_scanned}", file=sys.stderr)
    print(f"Task calls extracted: {len(all_data)}", file=sys.stderr)
    filtered = [d for d in all_data if d["category"] is not None]
    print(f"After agent filter: {len(filtered)}", file=sys.stderr)
    print(f"Source breakdown: metadata={sum(1 for d in filtered if d['source']=='metadata')}, timestamp={sum(1 for d in filtered if d['source']=='timestamp')}", file=sys.stderr)

    # Sleep detection: flag entries where seconds-per-tool-use is abnormally high
    clean = []
    suspect = []
    for d in filtered:
        if d["duration_s"] is not None and d["tool_uses"] is not None and d["tool_uses"] > 0:
            per_tool = d["duration_s"] / d["tool_uses"]
            d["per_tool_s"] = per_tool
            if per_tool > SUSPECT_PER_TOOL_THRESHOLD:
                suspect.append(d)
                continue
        clean.append(d)

    print(f"Clean: {len(clean)}, suspect (sleep-inflated): {len(suspect)}", file=sys.stderr)
    print()

    # --- Section 1: Duration by category (clean only) ---
    print("=" * 80)
    print("DURATION BY CATEGORY (sleep-filtered)")
    print("=" * 80)
    by_cat = defaultdict(list)
    for d in clean:
        if d["duration_s"] is not None:
            by_cat[d["category"]].append(d["duration_s"])
    for cat in ["review", "execution", "memory", "exploration", "guide"]:
        print_distribution(cat, by_cat.get(cat, []))
    print_distribution("ALL filtered", [d["duration_s"] for d in clean if d["duration_s"] is not None])

    # --- Section 2: Duration by agent type (clean only) ---
    print()
    print("=" * 80)
    print("DURATION BY AGENT TYPE (n >= 3, sleep-filtered)")
    print("=" * 80)
    by_type = defaultdict(list)
    for d in clean:
        if d["duration_s"] is not None:
            by_type[d["agent_type"]].append(d["duration_s"])
    for agent_type in sorted(by_type.keys(), key=lambda k: -len(by_type[k])):
        vals = by_type[agent_type]
        if len(vals) >= 3:
            print_distribution(agent_type, vals)

    # --- Section 3: Tool uses by category ---
    print()
    print("=" * 80)
    print("TOOL USES BY CATEGORY (metadata only)")
    print("=" * 80)
    tu_by_cat = defaultdict(list)
    for d in clean:
        if d["tool_uses"] is not None:
            tu_by_cat[d["category"]].append(d["tool_uses"])
    for cat in ["review", "execution", "memory", "exploration", "guide"]:
        print_distribution(cat, tu_by_cat.get(cat, []), unit="")
    print_distribution("ALL filtered", [d["tool_uses"] for d in clean if d["tool_uses"] is not None], unit="")

    # --- Section 4: Tool uses by agent type ---
    print()
    print("=" * 80)
    print("TOOL USES BY AGENT TYPE (n >= 3, metadata only)")
    print("=" * 80)
    tu_by_type = defaultdict(list)
    for d in clean:
        if d["tool_uses"] is not None:
            tu_by_type[d["agent_type"]].append(d["tool_uses"])
    for agent_type in sorted(tu_by_type.keys(), key=lambda k: -len(tu_by_type[k])):
        vals = tu_by_type[agent_type]
        if len(vals) >= 3:
            print_distribution(agent_type, vals, unit="")

    # --- Section 5: Sleep-suspect entries ---
    print()
    print("=" * 80)
    print(f"SLEEP-SUSPECT ENTRIES ({len(suspect)} flagged, per_tool > {SUSPECT_PER_TOOL_THRESHOLD}s)")
    print("=" * 80)
    for d in sorted(suspect, key=lambda x: -x["duration_s"]):
        print(f"  {d['duration_s']:8.0f}s  {d['tool_uses']:4d} tools  {d['per_tool_s']:6.0f}s/tool  {d['agent_type']:30s}  {d['description']}")

    # --- Section 6: Duration vs tool uses correlation (clean only) ---
    print()
    print("=" * 80)
    print("DURATION vs TOOL USES (clean, both available)")
    print("=" * 80)
    both = [(d["duration_s"], d["tool_uses"], d) for d in clean
            if d["duration_s"] is not None and d["tool_uses"] is not None]
    if both:
        print(f"  Paired observations: {len(both)}")
        avg_dur_per_tool = sum(dur / max(tu, 1) for dur, tu, _ in both) / len(both)
        print(f"  Avg seconds per tool use: {avg_dur_per_tool:.1f}s")
        high_tu = sorted(both, key=lambda x: x[1], reverse=True)[:10]
        print(f"  Top 10 by tool uses:")
        for dur, tu, d in high_tu:
            print(f"    {tu:4d} tools, {dur:6.0f}s  {d['agent_type']:30s}  {d['description']}")

    # --- Section 7: Suggested thresholds (clean only) ---
    print()
    print("=" * 80)
    print("SUGGESTED THRESHOLDS (sleep-filtered)")
    print("=" * 80)
    all_dur = sorted([d["duration_s"] for d in clean if d["duration_s"] is not None])
    all_tu = sorted([d["tool_uses"] for d in clean if d["tool_uses"] is not None])
    if all_dur:
        p90d = percentile(all_dur, 90)
        p95d = percentile(all_dur, 95)
        p99d = percentile(all_dur, 99)
        print(f"  Duration: p90={p90d:.0f}s p95={p95d:.0f}s p99={p99d:.0f}s max={all_dur[-1]:.0f}s")
        print(f"  Blanket timeout at p99+margin: ~{int(p99d * 1.25)}s ({int(p99d * 1.25 / 60)}min)")
    if all_tu:
        p90t = percentile(all_tu, 90)
        p95t = percentile(all_tu, 95)
        p99t = percentile(all_tu, 99)
        print(f"  Tool uses: p90={p90t:.0f} p95={p95t:.0f} p99={p99t:.0f} max={all_tu[-1]:.0f}")
        print(f"  Blanket max_turns at p99+margin: ~{int(p99t * 1.25)}")


if __name__ == "__main__":
    main()
