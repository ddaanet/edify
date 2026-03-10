#!/usr/bin/env python3
"""Forced selection harness for A/B testing verb form effects.

For each (task, variant) pair:
  1. Present Claude with the index variant + task description
  2. Ask: "Which /how entries are relevant to this task?"
  3. Parse the response for listed entries
  4. Record as binary observations (listed / not listed per entry)

Usage:
  ./ab-harness.py                    # run full experiment
  ./ab-harness.py --dry-run          # show prompts without API calls
  ./ab-harness.py --tasks N          # limit to first N tasks
  ./ab-harness.py --resume results.json  # resume from partial results
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import anthropic


PROMPT_TEMPLATE = """You are reviewing a project's memory index to find entries relevant to a task.

Below is the memory index. Each line starting with /how describes procedural knowledge about how to do something.

<memory_index>
{index_content}
</memory_index>

<task>
{task_description}
</task>

Which /how entries from the index above are relevant to this task? List ONLY the /how trigger lines that are relevant, one per line. Include the full trigger text exactly as it appears in the index. If no entries are relevant, respond with "NONE".

Relevant entries:"""

MODEL = "claude-sonnet-4-20250514"


def extract_how_entries(index_content: str) -> list[str]:
    """Extract /how trigger lines from index content (skip header)."""
    entries = []
    in_entries = False
    for line in index_content.split("\n"):
        if line.startswith("## "):
            in_entries = True
        if in_entries and line.startswith("/how "):
            entries.append(line.strip())
    return entries


def parse_response_entries(response_text: str, valid_entries: list[str]) -> list[str]:
    """Parse response to extract listed /how entries.

    Uses fuzzy matching: if the response contains the trigger text (with or
    without the /how prefix, with or without "to"), match it to the closest
    valid entry.
    """
    if "NONE" in response_text.strip().upper()[:10]:
        return []

    matched = []
    response_lower = response_text.lower()

    for entry in valid_entries:
        # Check exact match
        if entry.lower() in response_lower:
            matched.append(entry)
            continue
        # Check without /how prefix
        trigger = entry[5:] if entry.startswith("/how ") else entry
        # For variant B entries, also strip "to "
        trigger_bare = trigger.removeprefix("to ")
        if trigger.lower() in response_lower or trigger_bare.lower() in response_lower:
            matched.append(entry)

    return matched


def run_forced_selection(
    client: anthropic.Anthropic,
    index_content: str,
    task_desc: str,
) -> dict:
    """Run one forced selection query."""
    prompt = PROMPT_TEMPLATE.format(
        index_content=index_content,
        task_description=task_desc,
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text
    return {
        "response_text": response_text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


def run_experiment(
    tasks: list[dict],
    variant_a_path: Path,
    variant_b_path: Path,
    dry_run: bool = False,
    existing_results: dict | None = None,
) -> dict:
    """Run the full A/B experiment."""
    variant_a = variant_a_path.read_text()
    variant_b = variant_b_path.read_text()

    entries_a = extract_how_entries(variant_a)
    entries_b = extract_how_entries(variant_b)

    print(f"Variant A entries: {len(entries_a)}")
    print(f"Variant B entries: {len(entries_b)}")
    print(f"Tasks: {len(tasks)}")
    print()

    if dry_run:
        # Show first prompt only
        prompt = PROMPT_TEMPLATE.format(
            index_content=variant_a[:500] + "\n...",
            task_description=tasks[0]["description"],
        )
        print("=== DRY RUN: Sample prompt ===")
        print(prompt[:1000])
        print("...")
        return {}

    client = anthropic.Anthropic()
    results = existing_results or {
        "metadata": {
            "model": MODEL,
            "entries_a": len(entries_a),
            "entries_b": len(entries_b),
            "tasks": len(tasks),
        },
        "observations": [],
    }

    completed_keys = {
        (o["task_id"], o["variant"]) for o in results.get("observations", [])
    }

    total_pairs = len(tasks) * 2
    done = len(completed_keys)

    for task in tasks:
        for variant_label, index_content, entries in [
            ("A", variant_a, entries_a),
            ("B", variant_b, entries_b),
        ]:
            key = (task["task_id"], variant_label)
            if key in completed_keys:
                continue

            done += 1
            print(
                f"[{done}/{total_pairs}] {task['task_id']} variant {variant_label}...",
                end=" ",
                flush=True,
            )

            result = run_forced_selection(client, index_content, task["description"])
            matched = parse_response_entries(result["response_text"], entries)

            observation = {
                "task_id": task["task_id"],
                "variant": variant_label,
                "matched_entries": matched,
                "matched_count": len(matched),
                "response_text": result["response_text"],
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
            }
            results["observations"].append(observation)
            print(f"{len(matched)} entries matched")

            # Rate limit: ~1 req/sec
            time.sleep(1.0)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="A/B forced selection harness")
    parser.add_argument(
        "--tasks-json", required=True, help="Path to task contexts JSON"
    )
    parser.add_argument("--variant-a", required=True, help="Path to variant A index")
    parser.add_argument("--variant-b", required=True, help="Path to variant B index")
    parser.add_argument(
        "-o", "--output", required=True, help="Output results JSON path"
    )
    parser.add_argument("--dry-run", action="store_true", help="Show prompts only")
    parser.add_argument("--max-tasks", type=int, default=0, help="Limit to N tasks")
    parser.add_argument("--resume", action="store_true", help="Resume from output file")
    args = parser.parse_args()

    tasks = json.loads(Path(args.tasks_json).read_text())
    if args.max_tasks > 0:
        tasks = tasks[: args.max_tasks]

    variant_a = Path(args.variant_a)
    variant_b = Path(args.variant_b)
    for p in [variant_a, variant_b]:
        if not p.exists():
            print(f"Not found: {p}", file=sys.stderr)
            sys.exit(1)

    existing = None
    if args.resume:
        out_path = Path(args.output)
        if out_path.exists():
            existing = json.loads(out_path.read_text())

    results = run_experiment(tasks, variant_a, variant_b, args.dry_run, existing)

    if not args.dry_run and results:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(results, indent=2))
        print(f"\nResults written to: {out_path}")

        # Quick summary
        obs = results["observations"]
        a_obs = [o for o in obs if o["variant"] == "A"]
        b_obs = [o for o in obs if o["variant"] == "B"]
        a_avg = sum(o["matched_count"] for o in a_obs) / len(a_obs) if a_obs else 0
        b_avg = sum(o["matched_count"] for o in b_obs) / len(b_obs) if b_obs else 0
        print(f"\nQuick summary:")
        print(f"  Variant A avg matched: {a_avg:.1f}")
        print(f"  Variant B avg matched: {b_avg:.1f}")
        total_in = sum(o["input_tokens"] for o in obs)
        total_out = sum(o["output_tokens"] for o in obs)
        print(f"  Total tokens: {total_in:,} in + {total_out:,} out")


if __name__ == "__main__":
    main()
