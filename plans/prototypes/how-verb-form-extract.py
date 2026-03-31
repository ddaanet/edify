#!/usr/bin/env python3
"""Extract /how invocations from sessions and classify verb forms.

Reads session JSONL files to find actual /how query patterns agents use.
Classifies into: bare imperative, infinitive (to+verb), gerund, other.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from edify.paths import encode_project_path

# Match /how invocations — skill tool calls and direct text
HOW_PATTERN = re.compile(r'/how\s+(.+?)(?:\n|$|")', re.IGNORECASE)
SKILL_HOW_PATTERN = re.compile(
    r'"skill"\s*:\s*"how".*?"args"\s*:\s*"([^"]+)"', re.DOTALL
)
# Also match Skill tool usage with how
SKILL_TOOL_PATTERN = re.compile(
    r'"name"\s*:\s*"Skill".*?"skill"\s*:\s*"how".*?"args"\s*:\s*"([^"]*)"', re.DOTALL
)

# Verb form classification
GERUND_RE = re.compile(r"^(\w+ing)\b")
INFINITIVE_RE = re.compile(r"^to\s+(\w+)\b")
BARE_RE = re.compile(r"^(\w+)\b")

# Common verbs that end in -ing but are not gerunds
NOT_GERUND = {
    "string",
    "ring",
    "king",
    "thing",
    "bring",
    "spring",
    "swing",
    "sing",
    "sting",
}


def classify_verb_form(query: str) -> str:
    """Classify the verb form of a /how query."""
    q = query.strip().lower()
    if not q:
        return "empty"

    # Check infinitive first (to + verb)
    m = INFINITIVE_RE.match(q)
    if m:
        return "infinitive"

    # Check gerund (-ing form)
    m = GERUND_RE.match(q)
    if m and m.group(1) not in NOT_GERUND:
        return "gerund"

    # Default: bare imperative
    return "bare"


def extract_how_queries(project_path: str) -> list[dict]:
    """Extract all /how queries from session files."""
    projects_dir = Path.home() / ".claude" / "projects"
    encoded = encode_project_path(project_path)

    results = []

    for history_dir in sorted(projects_dir.iterdir()):
        if not history_dir.is_dir():
            continue
        if not history_dir.name.startswith(encoded):
            continue

        for jsonl_file in sorted(history_dir.glob("*.jsonl")):
            try:
                for line in jsonl_file.read_text().splitlines():
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    content = ""
                    msg = entry.get("message", {})
                    if isinstance(msg, dict):
                        c = msg.get("content", "")
                        if isinstance(c, str):
                            content = c
                        elif isinstance(c, list):
                            for block in c:
                                if isinstance(block, dict):
                                    if block.get("type") == "text":
                                        content += block.get("text", "") + "\n"
                                    elif block.get("type") == "tool_use":
                                        # Check for Skill tool with how
                                        inp = block.get("input", {})
                                        if (
                                            isinstance(inp, dict)
                                            and inp.get("skill") == "how"
                                        ):
                                            args = inp.get("args", "")
                                            if args:
                                                results.append(
                                                    {
                                                        "query": args,
                                                        "source": "skill_tool",
                                                        "session": jsonl_file.stem[:8],
                                                        "form": classify_verb_form(
                                                            args
                                                        ),
                                                    }
                                                )
                                    # Also check tool_input for Skill calls
                                    tool_input = block.get("tool_input", {})
                                    if (
                                        isinstance(tool_input, dict)
                                        and tool_input.get("skill") == "how"
                                    ):
                                        args = tool_input.get("args", "")
                                        if args:
                                            results.append(
                                                {
                                                    "query": args,
                                                    "source": "skill_tool",
                                                    "session": jsonl_file.stem[:8],
                                                    "form": classify_verb_form(args),
                                                }
                                            )

                    # Also scan raw content for /how patterns
                    for m in HOW_PATTERN.finditer(content):
                        query = m.group(1).strip()
                        # Skip if it's part of code/docs (e.g., "/how <trigger>")
                        if (
                            query.startswith("<")
                            or query.startswith("{")
                            or "trigger" in query.lower()
                        ):
                            continue
                        # Skip index references
                        if query.startswith("output") and len(query) > 100:
                            continue
                        if len(query) > 80:
                            continue
                        results.append(
                            {
                                "query": query,
                                "source": "text_match",
                                "session": jsonl_file.stem[:8],
                                "form": classify_verb_form(query),
                            }
                        )
            except Exception:
                continue

    return results


def main() -> None:
    project = "/Users/david/code/edify"
    queries = extract_how_queries(project)

    # Deduplicate by (query, session)
    seen = set()
    unique = []
    for q in queries:
        key = (q["query"].lower(), q["session"])
        if key not in seen:
            seen.add(key)
            unique.append(q)

    print(f"Total /how queries found: {len(unique)}")
    print()

    # Classify verb forms
    form_counts = Counter(q["form"] for q in unique)
    print("=== Verb Form Distribution ===")
    for form, count in form_counts.most_common():
        pct = count / len(unique) * 100
        print(f"  {form:<15} {count:>4} ({pct:.1f}%)")
    print()

    # Show examples of each form
    by_form = defaultdict(list)
    for q in unique:
        by_form[q["form"]].append(q["query"])

    print("=== Examples by Form ===")
    for form in ["bare", "infinitive", "gerund", "other", "empty"]:
        examples = by_form.get(form, [])
        if not examples:
            continue
        print(f"\n{form} ({len(examples)} total):")
        # Show up to 15 unique queries
        shown = set()
        for ex in examples:
            normalized = ex.lower().strip()
            if normalized not in shown and len(shown) < 15:
                shown.add(normalized)
                print(f"  /how {ex}")

    # Extract the leading verb from bare imperatives
    print("\n=== Most Common Leading Verbs (bare form) ===")
    verb_counts = Counter()
    for q in unique:
        if q["form"] == "bare":
            m = BARE_RE.match(q["query"].lower())
            if m:
                verb_counts[m.group(1)] += 1
    for verb, count in verb_counts.most_common(20):
        print(f"  {verb:<20} {count:>4}")


if __name__ == "__main__":
    main()
