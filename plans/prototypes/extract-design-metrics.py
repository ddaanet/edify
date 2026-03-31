#!/usr/bin/env python3
"""Extract structured metrics from all /design sessions for grounding
analysis."""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
# no imports needed beyond stdlib for this extraction

# All sessions with /design invocations
SESSIONS = """
-Users-david-code-edify-continuation-passing/7a774b81-084f-4307-ad71-b1c8d37b46f0
-Users-david-code-edify-continuation-passing/cb82aca8-5e1e-4d82-9ccb-ee7c59b3deb0
-Users-david-code-edify-memory-index-recall/1362c8b6-cc0d-48bf-bd7b-78002ae6d65d
-Users-david-code-edify-memory-index-recall/3f0ecf5f-785b-4089-aeb5-3eda96110bd1
-Users-david-code-edify-plugin-migration/130ad4c3-11fc-43d3-ad0c-a54fb85e77df
-Users-david-code-edify-prompt-composer-eval/0f669ee2-560a-4c7d-81a2-793b1ea39c7f
-Users-david-code-edify-wt-design-quality-gates/4452d81a-4250-48a5-8afa-07a253429fc8
-Users-david-code-edify-wt-design-workwoods/f36b9829-b075-4272-a8a8-37f6d9988c15
-Users-david-code-edify-wt-error-handling-design/383be939-fbff-4398-b209-df8223c65a9d
-Users-david-code-edify-wt-planstate-delivered/106ae2db-6270-436a-a420-4d8e2d6182c6
-Users-david-code-edify-wt-prepare-runbook-fixes/c2391c15-c317-4635-b76d-f554a62fba70
-Users-david-code-edify-wt-pushback/2e376b75-4d5d-4465-96fe-277521b5be27
-Users-david-code-edify-wt-requirements-skill/b89c8ef6-7eef-444e-bbb0-cc0c5e80ce01
-Users-david-code-edify-wt-runbook-skill-fixes/09bcd67d-cc27-4a5e-a6d6-6ecaff6cce7f
-Users-david-code-edify-wt-when-resolve-fix/1731750b-38a6-44de-86a9-267ca6d54ae2
-Users-david-code-edify-wt-worktree-merge-data-loss/ebe6cbf8-eaff-4cc2-bb1d-4c5e60b301dc
-Users-david-code-edify-wt-worktree-merge-resilience/bf04aacb-3942-4907-85dd-38cec4c74bbe
-Users-david-code-edify-wt-worktree-rm-error-ux/26ea8674-503d-47dc-af31-6878d6f846cc
-Users-david-code-edify-wt-worktree-rm-safety-gate/f43a07d1-5999-41c6-b6ac-37d28df20f74
-Users-david-code-edify-wt-worktree/262b20bd-707a-4f37-a367-b3778b476577
-Users-david-code-edify-wt-worktree/889b451a-d2af-4351-bd69-6705da28a74a
-Users-david-code-edify-wt-wt-merge-session-loss/f420e1c1-5266-4509-81e0-cf1a1f79ae34
-Users-david-code-edify/065996f4-c62a-4d2b-ad28-f6a559870543
-Users-david-code-edify/1926e939-1494-474f-8d0c-84da0db5da79
-Users-david-code-edify/4c9ba70f-142e-4ce5-8023-bebdaa3eb6f7
-Users-david-code-edify/4d06bcdf-847b-4f07-8e37-3abb74660ab3
-Users-david-code-edify/4ec020d3-da78-429c-b598-57cc738d6bd2
-Users-david-code-edify/7de1cdd1-d79e-446d-9343-b93da377dffe
-Users-david-code-edify/8e01b115-8e67-4910-8525-6fc21b4f051d
-Users-david-code-edify/a7e0dd5a-aa0a-419b-92ae-1316582f32ef
-Users-david-code-edify/b2fbde3a-4f42-40cb-ba74-5c20492eac06
-Users-david-code-edify/b305cd51-0dba-4e4c-82c1-c178d85bc3b3
-Users-david-code-edify/b5509d34-16ca-4114-a76d-373459ec4a7d
-Users-david-code-edify/bb473a1c-fad1-4ef0-8758-11992710dc8d
-Users-david-code-edify/dfd23c89-1fbb-478a-af54-821ab6dbe291
-Users-david-code-edify/e106aa80-f2a7-486c-ba5e-746f17c5acdc
-Users-david-code-edify/e6b4297e-18c2-43e2-8b51-9c7f2cf5f4ba
-Users-david-code-edify/f90ea499-baf5-4417-9f2f-493b17cdf9ed
""".strip().split("\n")

PROJECTS_DIR = Path.home() / ".claude" / "projects"

# Classification patterns in agent answers
COMPLEX_RE = re.compile(r"(?:complex|Complex|COMPLEX)", re.IGNORECASE)
MODERATE_RE = re.compile(r"(?:moderate|Moderate|MODERATE)", re.IGNORECASE)
SIMPLE_RE = re.compile(r"(?:simple|Simple|SIMPLE)", re.IGNORECASE)
CLASSIFY_PATTERNS = [
    (re.compile(r"[Cc]omplexity[:\s]*[Cc]omplex"), "Complex"),
    (re.compile(r"[Cc]omplexity[:\s]*[Mm]oderate"), "Moderate"),
    (re.compile(r"[Cc]omplexity[:\s]*[Ss]imple"), "Simple"),
    (re.compile(r"[Cc]lassification[:\s]*[Cc]omplex"), "Complex"),
    (re.compile(r"[Cc]lassification[:\s]*[Mm]oderate"), "Moderate"),
    (re.compile(r"[Cc]lassification[:\s]*[Ss]imple"), "Simple"),
    (re.compile(r"[Cc]omplexity [Tt]riage[:\s]*[Cc]omplex"), "Complex"),
    (re.compile(r"[Cc]omplexity [Tt]riage[:\s]*[Mm]oderate"), "Moderate"),
    (re.compile(r"[Cc]omplexity [Tt]riage[:\s]*[Ss]imple"), "Simple"),
    (re.compile(r"[Tt]riage[d]?.*[Cc]omplex"), "Complex"),
    (re.compile(r"[Tt]riage[d]?.*[Mm]oderate"), "Moderate"),
    (re.compile(r"[Tt]riage[d]?.*[Ss]imple"), "Simple"),
    # "This is (a) complex/moderate/simple" phrasing
    (re.compile(r"[Tt]his is (?:a )?[Cc]omplex"), "Complex"),
    (re.compile(r"[Tt]his is (?:a )?[Mm]oderate"), "Moderate"),
    (re.compile(r"[Tt]his is (?:a )?[Ss]imple"), "Simple"),
    (re.compile(r"[Dd]esign already exists"), "Shortcircuit"),
]


def extract_classification(lines):
    """Find the first complexity classification in agent answers."""
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") != "assistant":
            continue
        content = e.get("message", {}).get("content", "")
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = "\n".join(text_parts)
        if not isinstance(content, str):
            continue
        # Strip markdown bold markers so **Complexity:** Moderate matches
        content = content.replace("**", "")
        for pattern, label in CLASSIFY_PATTERNS:
            if pattern.search(content):
                return label
    return "Unknown"


def count_entry_types(lines):
    """Count entries by type."""
    counts = {
        "user_prompts": 0,
        "tool_calls": 0,
        "tool_errors": 0,
        "interrupts": 0,
        "agent_answers": 0,
        "skill_invocations": 0,
        "commits": 0,
    }
    commit_re = re.compile(r"\[(?:[^\[\]]*?\s+)?([0-9a-f]{7,12})\]")
    git_markers = {"file changed", "files changed", "create mode"}

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue

        etype = e.get("type")
        content = e.get("message", {}).get("content", "")

        if etype == "assistant":
            counts["agent_answers"] += 1
            # Check for tool_use blocks
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        counts["tool_calls"] += 1
                        if block.get("name") == "Skill":
                            inp = block.get("input", {})
                            if inp.get("skill") == "design":
                                counts["skill_invocations"] += 1

        elif etype == "user":
            if isinstance(content, str):
                if "[Request interrupted by user]" in content:
                    counts["interrupts"] += 1
                elif "<command-name>" in content:
                    if "design" in content:
                        counts["skill_invocations"] += 1
                else:
                    counts["user_prompts"] += 1
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        # Check text blocks for interrupt message
                        if block.get("type") == "text":
                            text = block.get("text", "")
                            if "[Request interrupted by user]" in text:
                                counts["interrupts"] += 1
                        # Check for tool results
                        elif block.get("type") == "tool_result":
                            if block.get("is_error"):
                                counts["tool_errors"] += 1
                            # Check for commit
                            raw_output = block.get("content", "")
                            if isinstance(raw_output, str):
                                m = commit_re.search(raw_output)
                                if m and any(
                                    marker in raw_output for marker in git_markers
                                ):
                                    counts["commits"] += 1

    return counts


def count_agents(session_dir, session_id):
    """Count sub-agent files for a session."""
    subagents_dir = session_dir / session_id / "subagents"
    if not subagents_dir.exists():
        return 0
    return sum(1 for _ in subagents_dir.glob("agent-*.jsonl"))


def get_first_last_timestamp(lines):
    """Get first and last timestamps."""
    first = last = None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = e.get("timestamp")
        if ts:
            if first is None:
                first = ts
            last = ts
    return first, last


def has_websearch(lines):
    """Check if session contains WebSearch tool calls."""
    for raw in lines:
        if '"WebSearch"' in raw or '"WebFetch"' in raw:
            return True
    return False


def has_outline_corrector(lines):
    """Check if session dispatches outline-corrector."""
    for raw in lines:
        if (
            "outline-corrector" in raw
            or "outline_corrector" in raw
            or "outline corrector" in raw.lower()
        ):
            return True
    return False


def has_design_corrector(lines):
    """Check if session dispatches design-corrector."""
    for raw in lines:
        if (
            "design-corrector" in raw
            or "design_corrector" in raw
            or "design corrector" in raw.lower()
        ):
            return True
    return False


results = []

for entry in SESSIONS:
    encoded_dir, session_id = entry.rsplit("/", 1)
    session_dir = PROJECTS_DIR / encoded_dir
    session_file = session_dir / f"{session_id}.jsonl"

    if not session_file.exists():
        continue

    try:
        lines = session_file.read_text().splitlines()
    except OSError:
        continue

    # Decode project name for display
    project_name = encoded_dir.replace("-Users-david-code-edify", "main")
    if project_name.startswith("main-wt-"):
        project_name = project_name[8:]  # strip "main-wt-"
    elif project_name.startswith("main-"):
        project_name = project_name[5:]  # strip "main-"
    elif project_name == "main":
        project_name = "main"

    counts = count_entry_types(lines)
    classification = extract_classification(lines)
    agents = count_agents(session_dir, session_id)
    first_ts, last_ts = get_first_last_timestamp(lines)
    web_research = has_websearch(lines)
    has_outline_rev = has_outline_corrector(lines)
    has_design_rev = has_design_corrector(lines)

    total_entries = len([l for l in lines if l.strip()])

    results.append(
        {
            "session_id": session_id[:8],
            "project": project_name,
            "entries": total_entries,
            "agents": agents,
            "commits": counts["commits"],
            "interrupts": counts["interrupts"],
            "tool_errors": counts["tool_errors"],
            "classification": classification,
            "web_research": web_research,
            "outline_corrector": has_outline_rev,
            "design_corrector": has_design_rev,
            "first_ts": (first_ts or "")[:16],
            "last_ts": (last_ts or "")[:16],
        }
    )

# Sort by date
results.sort(key=lambda r: r["first_ts"])

# Print header
print(
    f"{'Session':10} {'Project':30} {'Entries':>7} {'Agents':>6} {'Commits':>7} {'Intrs':>5} {'Errs':>4} {'Class':>12} {'Web':>3} {'OC':>3} {'DC':>3} {'Date':>10}"
)
print("-" * 140)

# Aggregate counters
total = len(results)
classifications = {}
phase0_interrupts = 0
complete_sessions = 0
web_research_count = 0
outline_corrector_count = 0
design_corrector_count = 0

for r in results:
    cls = r["classification"]
    classifications[cls] = classifications.get(cls, 0) + 1
    if r["interrupts"] > 0:
        phase0_interrupts += 1
    if r["commits"] > 0 or (r["outline_corrector"] and r["design_corrector"]):
        complete_sessions += 1
    if r["web_research"]:
        web_research_count += 1
    if r["outline_corrector"]:
        outline_corrector_count += 1
    if r["design_corrector"]:
        design_corrector_count += 1

    print(
        f"{r['session_id']:10} {r['project']:30} {r['entries']:>7} {r['agents']:>6} {r['commits']:>7} {r['interrupts']:>5} {r['tool_errors']:>4} {r['classification']:>12} {'Y' if r['web_research'] else '.':>3} {'Y' if r['outline_corrector'] else '.':>3} {'Y' if r['design_corrector'] else '.':>3} {r['first_ts'][:10]:>10}"
    )

print("-" * 140)
print(f"\nTotal sessions: {total}")
print(f"Classifications: {json.dumps(classifications, indent=2)}")
print(
    f"Sessions with interrupts: {phase0_interrupts}/{total} ({100 * phase0_interrupts / total:.0f}%)"
)
print(
    f"Sessions with commits (proxy for completion): {complete_sessions}/{total} ({100 * complete_sessions / total:.0f}%)"
)
print(
    f"Sessions with web research: {web_research_count}/{total} ({100 * web_research_count / total:.0f}%)"
)
print(
    f"Sessions with outline-corrector: {outline_corrector_count}/{total} ({100 * outline_corrector_count / total:.0f}%)"
)
print(
    f"Sessions with design-corrector: {design_corrector_count}/{total} ({100 * design_corrector_count / total:.0f}%)"
)
