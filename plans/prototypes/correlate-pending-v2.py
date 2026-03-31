#!/usr/bin/env python3
"""Correlate p: directives with ALL git task insertions (including batch)."""

import json
import re
import subprocess
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from edify.paths import encode_project_path

PENDING_PATTERN = re.compile(r"^\s*(?:p|pending)\s*:\s*(.+)", re.IGNORECASE)
TASK_RE = re.compile(r"^- \[[ x>]\] \*\*(.+?)\*\*")

PROJECT_DIRS = [Path.home() / "code" / "edify"]
wt_container = Path.home() / "code" / "edify-wt"
if wt_container.exists():
    for d in sorted(wt_container.iterdir()):
        if d.is_dir():
            PROJECT_DIRS.append(d)


def get_history_dir(project_dir: Path) -> Path:
    return Path.home() / ".claude" / "projects" / encode_project_path(str(project_dir))


def scrape_pending_directives() -> list[dict]:
    results = []
    uuid_pat = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$"
    )
    for project_dir in PROJECT_DIRS:
        history_dir = get_history_dir(project_dir)
        if not history_dir.exists():
            continue
        for sf in history_dir.glob("*.jsonl"):
            if not uuid_pat.match(sf.name):
                continue
            try:
                lines = sf.read_text().strip().split("\n")
            except OSError:
                continue
            for line in lines:
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") != "user":
                    continue
                msg = entry.get("message", {})
                content = msg.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        b.get("text", "")
                        for b in content
                        if isinstance(b, dict) and b.get("type") == "text"
                    )
                m = PENDING_PATTERN.match(content.strip())
                if m:
                    results.append(
                        {
                            "date": entry.get("timestamp", "")[:10],
                            "text": m.group(1).strip()[:200],
                        }
                    )
    results.sort(key=lambda r: r["date"])
    return results


def extract_tasks(content):
    tasks = []
    in_pending = False
    for line in content.split("\n"):
        if "## Pending Tasks" in line:
            in_pending = True
            continue
        if in_pending and line.startswith("## "):
            break
        if in_pending:
            m = TASK_RE.match(line)
            if m:
                tasks.append(m.group(1).split("**")[0].strip())
    return tasks


def get_all_insertions() -> list[dict]:
    """Get ALL task insertions (single and batch) with positions."""
    result = subprocess.run(
        [
            "git",
            "log",
            "--all",
            "--format=%H %aI",
            "--no-merges",
            "--follow",
            "--",
            "agents/session.md",
        ],
        capture_output=True,
        text=True,
    )
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split(" ", 1)
        commits.append((parts[0], parts[1][:10]))

    # Filter focused sessions
    focused_result = subprocess.run(
        [
            "git",
            "log",
            "--all",
            "--oneline",
            "--no-merges",
            "--grep=Focused session",
            "--",
            "agents/session.md",
        ],
        capture_output=True,
        text=True,
    )
    focused_hashes = {
        line.split()[0] for line in focused_result.stdout.strip().split("\n") if line
    }

    insertions = []
    for i in range(len(commits) - 1):
        curr_hash, curr_date = commits[i]
        prev_hash, _ = commits[i + 1]

        if curr_hash[:7] in focused_hashes or curr_hash in focused_hashes:
            continue

        try:
            curr_content = subprocess.run(
                ["git", "show", f"{curr_hash}:agents/session.md"],
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout
            prev_content = subprocess.run(
                ["git", "show", f"{prev_hash}:agents/session.md"],
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout
        except Exception:
            continue

        curr_tasks = extract_tasks(curr_content)
        prev_tasks = extract_tasks(prev_content)
        prev_set = set(prev_tasks)
        new_tasks = [t for t in curr_tasks if t not in prev_set]

        if not new_tasks or not curr_tasks:
            continue

        for task in new_tasks:
            idx = curr_tasks.index(task)
            total = len(curr_tasks)

            if idx == 0:
                pos = "prepend"
            elif idx == total - 1:
                pos = "append"
            else:
                frac = idx / (total - 1)
                if frac <= 0.25:
                    pos = "near-top"
                elif frac >= 0.75:
                    pos = "near-bottom"
                else:
                    pos = "middle"

            insertions.append(
                {
                    "date": curr_date,
                    "task": task,
                    "pos": pos,
                    "idx": idx,
                    "total": total,
                    "hash": curr_hash[:7],
                    "batch_size": len(new_tasks),
                }
            )

    return insertions


def word_overlap(text1: str, text2: str) -> float:
    w1 = set(re.findall(r"\w{3,}", text1.lower()))  # min 3 chars
    w2 = set(re.findall(r"\w{3,}", text2.lower()))
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


def keyword_match(directive_text: str, task_name: str) -> float:
    """Check if key nouns from directive appear in task name."""
    # Extract significant words (skip common verbs/prepositions)
    skip = {
        "update",
        "add",
        "fix",
        "use",
        "the",
        "for",
        "with",
        "and",
        "that",
        "all",
        "after",
        "from",
        "into",
        "when",
        "should",
        "must",
        "not",
        "has",
        "have",
        "run",
        "make",
        "get",
        "set",
        "new",
        "also",
        "its",
        "this",
        "been",
    }
    d_words = set(re.findall(r"\w{3,}", directive_text.lower())) - skip
    t_words = set(re.findall(r"\w{3,}", task_name.lower())) - skip
    if not d_words or not t_words:
        return 0.0
    return len(d_words & t_words) / min(len(d_words), len(t_words))


def main():
    print("Scraping sessions...", file=sys.stderr)
    directives = scrape_pending_directives()
    print(f"Found {len(directives)} p: directives", file=sys.stderr)

    print("Analyzing git history...", file=sys.stderr)
    insertions = get_all_insertions()
    print(f"Found {len(insertions)} total task insertions", file=sys.stderr)

    # Index by date range
    ins_by_date = defaultdict(list)
    for ins in insertions:
        ins_by_date[ins["date"]].append(ins)

    matches = []
    unmatched = []

    for d in directives:
        if not d["date"]:
            unmatched.append(d)
            continue
        try:
            dt = datetime.strptime(d["date"], "%Y-%m-%d")
        except ValueError:
            unmatched.append(d)
            continue

        candidates = []
        for delta in range(4):  # same day through +3
            check_date = (dt + timedelta(days=delta)).strftime("%Y-%m-%d")
            candidates.extend(ins_by_date.get(check_date, []))

        if not candidates:
            unmatched.append(d)
            continue

        # Score with both metrics, take max
        scored = []
        for c in candidates:
            wo = word_overlap(d["text"], c["task"])
            km = keyword_match(d["text"], c["task"])
            score = max(wo, km)
            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best = scored[0]

        if best_score >= 0.15:
            matches.append({"directive": d, "insertion": best, "score": best_score})
        else:
            # Show best candidate for debugging
            unmatched.append(
                {**d, "best_candidate": best["task"], "best_score": best_score}
            )

    print(f"\n{'=' * 80}")
    print(f"MATCHED: {len(matches)}/{len(directives)}")
    print(f"{'=' * 80}")

    pos_counts = Counter()
    for m in sorted(matches, key=lambda x: x["directive"]["date"]):
        d = m["directive"]
        ins = m["insertion"]
        pos_counts[ins["pos"]] += 1
        batch = f" (batch={ins['batch_size']})" if ins["batch_size"] > 1 else ""
        print(f"\n[{d['date']}] p: {d['text'][:70]}")
        print(
            f"  → [{ins['pos']:12s}] {ins['idx']}/{ins['total'] - 1} {ins['task'][:55]}{batch} (sim={m['score']:.2f})"
        )

    n = len(matches)
    if n:
        print(f"\n{'=' * 80}")
        print(f"p:-originated task insertion distribution (n={n}):")
        for pos in ["prepend", "near-top", "middle", "near-bottom", "append"]:
            count = pos_counts.get(pos, 0)
            pct = count / n * 100
            bar = "#" * int(pct / 2)
            print(f"  {pos:12s}: {count:3d} ({pct:5.1f}%) {bar}")

    if unmatched:
        print(f"\n{'=' * 80}")
        print(f"UNMATCHED ({len(unmatched)}):")
        for d in unmatched:
            bc = d.get("best_candidate", "")
            bs = d.get("best_score", 0)
            suffix = f" | best: {bc[:40]} ({bs:.2f})" if bc else ""
            print(f"  [{d['date']}] {d['text'][:70]}{suffix}")


if __name__ == "__main__":
    main()
