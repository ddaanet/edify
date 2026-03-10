#!/usr/bin/env python3
"""Generate ground truth annotation template for A/B test.

Reads task contexts and outputs a markdown file for human annotation.
The annotator marks which /how entries are relevant to each task.

After annotation, this script can also parse the completed template
back into JSON for analysis comparison.

Usage:
  ./ab-ground-truth.py generate    # create annotation template
  ./ab-ground-truth.py parse       # parse completed annotations to JSON
"""

import argparse
import json
import sys
from pathlib import Path


def generate_template(
    tasks: list[dict], how_entries: list[str], out_path: Path
) -> None:
    """Generate markdown annotation template."""
    lines = [
        "# A/B Test Ground Truth Annotations",
        "",
        "For each task, mark relevant /how entries with [x].",
        "Mark 3-5 entries per task that would be useful for the described work.",
        "",
        "---",
        "",
    ]

    for task in tasks:
        lines.append(f"## {task['task_id']}: {task.get('session_id', '')}")
        lines.append("")
        lines.append(f"**Task:** {task['description']}")
        lines.append("")
        if task.get("how_queries"):
            lines.append(f"**Actually invoked:** {', '.join(task['how_queries'])}")
            lines.append("")
        lines.append("**Relevant entries:**")
        lines.append("")
        for entry in how_entries:
            lines.append(f"- [ ] {entry}")
        lines.append("")
        lines.append("---")
        lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"Template written to: {out_path}")
    print(f"Tasks: {len(tasks)}, entries per task: {len(how_entries)}")


def parse_annotations(template_path: Path) -> dict:
    """Parse completed annotation template back to JSON."""
    content = template_path.read_text()
    tasks = {}
    current_task = None

    for line in content.split("\n"):
        if line.startswith("## task-"):
            current_task = line.split(":")[0].replace("## ", "").strip()
            tasks[current_task] = []
        elif current_task and line.startswith("- [x] "):
            entry = line[6:].strip()
            tasks[current_task].append(entry)
        elif current_task and line.startswith("- [X] "):
            entry = line[6:].strip()
            tasks[current_task].append(entry)

    return tasks


def main() -> None:
    parser = argparse.ArgumentParser(description="A/B ground truth annotation")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Create annotation template")
    gen.add_argument("--tasks-json", required=True, help="Task contexts JSON")
    gen.add_argument(
        "--variant-a", required=True, help="Variant A index (for entry list)"
    )
    gen.add_argument("-o", "--output", required=True, help="Output markdown path")

    parse = sub.add_parser("parse", help="Parse completed annotations to JSON")
    parse.add_argument("template", help="Completed annotation markdown")
    parse.add_argument("-o", "--output", required=True, help="Output JSON path")

    args = parser.parse_args()

    if args.command == "generate":
        tasks = json.loads(Path(args.tasks_json).read_text())

        entries = []
        in_entries = False
        for line in Path(args.variant_a).read_text().split("\n"):
            if line.startswith("## "):
                in_entries = True
            if in_entries and line.startswith("/how "):
                entries.append(line.strip())

        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        generate_template(tasks, entries, out_path)

    elif args.command == "parse":
        template_path = Path(args.template)
        if not template_path.exists():
            print(f"Not found: {template_path}", file=sys.stderr)
            sys.exit(1)

        annotations = parse_annotations(template_path)
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(annotations, indent=2))

        total = sum(len(v) for v in annotations.values())
        annotated = sum(1 for v in annotations.values() if v)
        print(f"Parsed: {annotated}/{len(annotations)} tasks annotated")
        print(f"Total relevant entries: {total}")
        if annotated:
            print(f"Avg per task: {total / annotated:.1f}")
        print(f"Written to: {out_path}")


if __name__ == "__main__":
    main()
