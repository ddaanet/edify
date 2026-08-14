#!/usr/bin/env python3
"""Validate runbook files for structural and semantic correctness."""

import argparse
import importlib.util
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "prepare_runbook", Path(__file__).parent / "prepare-runbook.py"
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
extract_cycles = _mod.extract_cycles
assemble_phase_files = _mod.assemble_phase_files
extract_step_metadata = _mod.extract_step_metadata

ARTIFACT_PREFIXES = (
    "plugin/skills/",
    "plugin/fragments/",
    "plugin/agents/",
)

# The living design record. Design documents are opus work (docs/design.md
# D-42); before the 2026-08 fold this clause named the four workflow-*.md
# files under agents/decisions/.
ARTIFACT_FILES = ("docs/design.md",)


def _is_artifact_path(file_path: str) -> bool:
    if any(file_path.startswith(p) for p in ARTIFACT_PREFIXES):
        return file_path.endswith(".md")
    return file_path in ARTIFACT_FILES


def write_report(
    subcommand: str,
    path: str,
    violations: list[str],
    ambiguous: list[str] | None = None,
    skipped: str | None = None,
    not_applicable: str | None = None,
) -> Path:
    """Write validation report.

    For directory input: report goes to <path>/reports/validation-<subcommand>.md.
    For file input: report goes to plans/<job>/reports/validation-<subcommand>.md.

    Args:
        skipped: Operator-supplied reason the check was skipped. A SKIPPED
            report is not evidence the check ran — the reason is recorded so a
            reader can tell the two apart.
        not_applicable: Reason the check has no subject matter in this runbook
            (e.g. a TDD-only check against a general runbook). Distinct from
            PASS, which asserts the check ran and found nothing.
    """
    p = Path(path)
    report_dir = p / "reports" if p.is_dir() else Path("plans") / p.stem / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"validation-{subcommand}.md"

    if skipped:
        result = "SKIPPED"
    elif not_applicable:
        result = "NOT-APPLICABLE"
    elif violations:
        result = "FAIL"
    elif ambiguous:
        result = "AMBIGUOUS"
    else:
        result = "PASS"
    date = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# Validation Report: {subcommand}\n\n",
        f"**Runbook:** {path}\n\n",
        f"**Date:** {date}\n\n",
        f"**Result:** {result}\n\n",
    ]
    if skipped:
        lines.append(f"**Skipped because:** {skipped}\n\n")
        lines.append(
            "This check did NOT run. Do not read this report as evidence of "
            "conformance.\n\n"
        )
    if not_applicable:
        lines.append(f"**Not applicable because:** {not_applicable}\n\n")
    lines += [
        "## Summary\n\n",
        f"Failed: {len(violations)}\n\n",
    ]
    if ambiguous is not None:
        lines.insert(-1, f"Ambiguous: {len(ambiguous)}\n\n")
    if violations:
        lines.append("## Violations\n\n")
        lines.extend(f"- {v}\n" for v in violations)
    if ambiguous:
        lines.append("\n## Ambiguous\n\n")
        lines.extend(f"- {a}\n" for a in ambiguous)
    report_path.write_text("".join(lines))
    return report_path


# Checks that read TDD cycle structure. Against a general/inline runbook these
# find no cycles and would otherwise report PASS — an empty result reported as
# conformance. They report NOT-APPLICABLE instead.
CYCLE_BASED = ("model-tags", "lifecycle", "test-counts", "red-plausibility")


def _load_content(path: str) -> str:
    p = Path(path)
    if p.is_dir():
        content, _ = assemble_phase_files(path)
    else:
        content = p.read_text()
    return content


def _no_cycles_reason(subcommand: str, content: str) -> str | None:
    """Return a NOT-APPLICABLE reason when a cycle-based check has no subject."""
    if subcommand not in CYCLE_BASED:
        return None
    if extract_cycles(content):
        return None
    return (
        f"`{subcommand}` reads TDD cycle structure; this runbook declares no "
        f"cycles (general or inline phases only)."
    )


def check_model_tags(content: str, path: str) -> list[str]:
    """Check that artifact-type file references use opus Execution Model."""
    violations = []
    cycles = extract_cycles(content)
    for cycle in cycles:
        cycle_content = cycle["content"]
        metadata = extract_step_metadata(cycle_content)
        model = metadata.get("model", "haiku")
        file_refs = re.findall(r"- File: `?([^`\n]+)`?", cycle_content)
        for file_path in file_refs:
            file_path = file_path.strip()
            if _is_artifact_path(file_path) and model != "opus":
                violations.append(
                    f"Cycle {cycle['number']}: `{file_path}` — "
                    f"**Expected:** opus, got: {model}"
                )
    return violations


def cmd_model_tags(args: argparse.Namespace) -> None:
    path = args.path
    if args.skip_model_tags:
        write_report("model-tags", path, [], skipped=args.skip_model_tags)
        sys.exit(0)
    content = _load_content(path)
    if reason := _no_cycles_reason("model-tags", content):
        write_report("model-tags", path, [], not_applicable=reason)
        sys.exit(0)
    violations = check_model_tags(content, path)
    write_report("model-tags", path, violations)
    sys.exit(1 if violations else 0)


def check_lifecycle(
    content: str, path: str, known_files: set[str] | None = None
) -> list[str]:
    """Check that files are created before being modified.

    Args:
        known_files: Set of file paths known to pre-exist. These are exempt
            from modify-before-create violations.
    """
    violations = []
    _known = known_files or set()
    cycles = extract_cycles(content)
    # Map file_path -> (action_type, cycle_number) for first occurrence
    first_seen: dict[str, tuple[str, str]] = {}
    for cycle in cycles:
        cycle_content = cycle["content"]
        cycle_id = cycle["number"]
        # Extract File: / Action: pairs from Changes section
        file_action_pairs = re.findall(
            r"- File: `?([^`\n]+)`?\s*\n\s+Action: ([^\n]+)", cycle_content
        )
        for file_path, action_raw in file_action_pairs:
            file_path = file_path.strip()
            action = action_raw.strip()
            action_lower = action.lower()
            is_create = any(
                action_lower.startswith(kw) for kw in ("create", "write new")
            )
            is_modify = any(
                action_lower.startswith(kw)
                for kw in ("modify", "add", "update", "edit", "extend")
            )
            if file_path not in first_seen:
                first_seen[file_path] = (action, cycle_id)
                if is_modify and file_path not in _known:
                    violations.append(
                        f"Cycle {cycle_id}: `{file_path}` — no prior creation found"
                    )
            elif is_create:
                orig_action, orig_cycle = first_seen[file_path]
                orig_lower = orig_action.lower()
                orig_was_create = any(
                    orig_lower.startswith(kw) for kw in ("create", "write new")
                )
                if orig_was_create:
                    violations.append(
                        f"Cycle {cycle_id}: `{file_path}` created again "
                        f"(first seen in Cycle {orig_cycle} as '{orig_action}')"
                    )
            elif is_modify:
                orig_action, orig_cycle = first_seen[file_path]
                orig_lower = orig_action.lower()
                already_flagged = any(
                    orig_lower.startswith(kw)
                    for kw in ("modify", "add", "update", "edit", "extend")
                )
                if (
                    not any(orig_lower.startswith(kw) for kw in ("create", "write new"))
                    and not already_flagged
                ):
                    violations.append(
                        f"Cycle {cycle_id}: `{file_path}` modified before creation "
                        f"(first seen in Cycle {orig_cycle} as '{orig_action}')"
                    )
    return violations


def cmd_lifecycle(args: argparse.Namespace) -> None:
    path = args.path
    if args.skip_lifecycle:
        write_report("lifecycle", path, [], skipped=args.skip_lifecycle)
        sys.exit(0)
    content = _load_content(path)
    if reason := _no_cycles_reason("lifecycle", content):
        write_report("lifecycle", path, [], not_applicable=reason)
        sys.exit(0)
    known = set(getattr(args, "known_file", None) or [])
    violations = check_lifecycle(content, path, known_files=known)
    write_report("lifecycle", path, violations)
    sys.exit(1 if violations else 0)


def check_test_counts(content: str, path: str) -> list[str]:
    """Check that checkpoint test-count claims match cumulative test count at
    each position."""
    violations = []
    test_name_pattern = re.compile(r"\*\*Test:\*\*\s*`?([^`\n]+)`?")
    checkpoint_pattern = re.compile(r"All\s+(\d+)\s+tests?\s+pass", re.IGNORECASE)

    # Process line-by-line: accumulate tests, check at each checkpoint
    test_names: set[str] = set()
    for line in content.split("\n"):
        test_match = test_name_pattern.search(line)
        if test_match:
            name = re.sub(r"\[.*?\]$", "", test_match.group(1).strip())
            test_names.add(name)

        cp_match = checkpoint_pattern.search(line)
        if cp_match:
            claimed = int(cp_match.group(1))
            actual = len(test_names)
            if claimed != actual:
                names_list = ", ".join(sorted(test_names))
                violations.append(
                    f"Checkpoint claims {claimed} tests but found {actual} "
                    f"test function(s): {names_list}"
                )

    return violations


def cmd_test_counts(args: argparse.Namespace) -> None:
    path = args.path
    if args.skip_test_counts:
        write_report("test-counts", path, [], skipped=args.skip_test_counts)
        sys.exit(0)
    content = _load_content(path)
    if reason := _no_cycles_reason("test-counts", content):
        write_report("test-counts", path, [], not_applicable=reason)
        sys.exit(0)
    violations = check_test_counts(content, path)
    write_report("test-counts", path, violations)
    sys.exit(1 if violations else 0)


def check_red_plausibility(content: str, path: str) -> tuple[list[str], list[str]]:
    """Check that RED expected failures are plausible given prior GREEN state.

    Returns (violations, ambiguous) where violations are clear already-passing
    RED states and ambiguous are cases requiring semantic judgment.
    """
    violations: list[str] = []
    ambiguous: list[str] = []
    cycles = extract_cycles(content)

    # Names created by prior GREENs: name → creating cycle_id
    created_names: dict[str, str] = {}

    # Pattern to extract module/function name from ImportError/ModuleNotFoundError lines
    import_err_pattern = re.compile(
        r'(?:ImportError|ModuleNotFoundError).*?[`\'"]([\w.]+)[`\'"]',
        re.IGNORECASE,
    )
    # Pattern to detect non-import error types in failure text
    non_import_err_pattern = re.compile(
        r"\b(ValueError|AttributeError|TypeError|RuntimeError|KeyError|IndexError"
        r"|NameError|OSError|FileNotFoundError|NotImplementedError)\b",
        re.IGNORECASE,
    )
    # Pattern to extract stem from "Action: Create" file entries
    create_file_pattern = re.compile(
        r"- File: `?([^`\n]+)`?\s*\n\s+Action:\s*Create",
        re.IGNORECASE,
    )

    for cycle in cycles:
        cycle_content = cycle["content"]
        cycle_id = cycle["number"]

        # Extract RED expected failure text
        red_match = re.search(
            r"\*\*Expected failure:\*\*\s*`?([^\n`]+)`?", cycle_content
        )
        if red_match:
            failure_text = red_match.group(1).strip()
            import_matches = list(import_err_pattern.finditer(failure_text))
            if import_matches:
                for m in import_matches:
                    name = m.group(1)
                    # Check both the full dotted name and the last segment (module stem)
                    stem = name.split(".")[-1]
                    creating_cycle = created_names.get(name) or created_names.get(stem)
                    if creating_cycle:
                        violations.append(
                            f"Cycle {cycle_id}: RED expects `{failure_text}` but "
                            f"`{name}` already created in Cycle {creating_cycle} GREEN"
                        )
                    else:
                        # First-cycle ImportError: structural RED, not behavioral.
                        # Should use Bootstrap + AssertionError instead.
                        has_bootstrap = bool(
                            re.search(r"\*\*Bootstrap:\*\*", cycle_content)
                        )
                        if not has_bootstrap:
                            violations.append(
                                f"Cycle {cycle_id}: RED expects `{failure_text}` "
                                f"(structural). Add Bootstrap step with stub, "
                                f"expect behavioral AssertionError instead"
                            )
            elif non_import_err_pattern.search(failure_text):
                # Non-import error: ambiguous when a created name appears in the failure text
                error_type = non_import_err_pattern.search(failure_text).group(1)
                for name, creating_cycle in created_names.items():
                    if name in failure_text:
                        ambiguous.append(
                            f"Cycle {cycle_id}: `{name}` exists (created Cycle "
                            f"{creating_cycle}) but RED tests different behavior "
                            f"({error_type}) — `{failure_text}`"
                        )
                        break

        # After checking RED, accumulate this cycle's GREEN creations for future cycles
        for m in create_file_pattern.finditer(cycle_content):
            file_path = m.group(1).strip()
            p = Path(file_path)
            # Add both the full path stem and the module-style name (src.module)
            created_names.setdefault(p.stem, cycle_id)
            # Also add dotted module path (src/module.py → src.module)
            parts = p.with_suffix("").parts
            created_names.setdefault(".".join(parts), cycle_id)

    return violations, ambiguous


def cmd_red_plausibility(args: argparse.Namespace) -> None:
    path = args.path
    if args.skip_red_plausibility:
        write_report("red-plausibility", path, [], skipped=args.skip_red_plausibility)
        sys.exit(0)
    content = _load_content(path)
    if reason := _no_cycles_reason("red-plausibility", content):
        write_report("red-plausibility", path, [], not_applicable=reason)
        sys.exit(0)
    violations, ambiguous = check_red_plausibility(content, path)
    write_report("red-plausibility", path, violations, ambiguous)
    if violations:
        sys.exit(1)
    elif ambiguous:
        sys.exit(2)
    else:
        sys.exit(0)


VERIFY_PATH_PATTERN = re.compile(r"\*\*Verify (?:GREEN|RED):\*\*\s*`([^`]+)`")
SPECIFIC_PYTEST_PATH = re.compile(r"pytest\s+\S*(?:tests/|::|\.py)")


def check_verify_green_paths(content: str, path: str) -> list[str]:
    """Check that Verify GREEN/RED lines use universal recipes, not specific
    paths."""
    violations = []
    for m in VERIFY_PATH_PATTERN.finditer(content):
        command = m.group(1).strip()
        if SPECIFIC_PYTEST_PATH.search(command):
            violations.append(
                f"Verify line contains specific pytest path: `{command}` — "
                f"use `just green` instead"
            )
    return violations


def cmd_verify_green_paths(args: argparse.Namespace) -> None:
    path = args.path
    if args.skip_verify_green_paths:
        write_report(
            "verify-green-paths", path, [], skipped=args.skip_verify_green_paths
        )
        sys.exit(0)
    content = _load_content(path)
    violations = check_verify_green_paths(content, path)
    write_report("verify-green-paths", path, violations)


def main() -> None:
    """Entry point for validate-runbook CLI."""
    parser = argparse.ArgumentParser(prog="validate-runbook")
    sub = parser.add_subparsers(dest="subcommand")
    for name, fn, skip_dest in [
        ("model-tags", cmd_model_tags, "skip_model_tags"),
        ("lifecycle", cmd_lifecycle, "skip_lifecycle"),
        ("test-counts", cmd_test_counts, "skip_test_counts"),
        ("red-plausibility", cmd_red_plausibility, "skip_red_plausibility"),
        ("verify-green-paths", cmd_verify_green_paths, "skip_verify_green_paths"),
    ]:
        p = sub.add_parser(name)
        p.add_argument("path")
        p.add_argument(
            f"--skip-{name}",
            dest=skip_dest,
            metavar="REASON",
            default=None,
            help=(
                "Skip this check, recording REASON in the report. Legitimate "
                "only when the check cannot run — not to get past a failure. "
                "The report is stamped SKIPPED and states it is not evidence "
                "of conformance."
            ),
        )
        if name == "lifecycle":
            p.add_argument(
                "--known-file",
                action="append",
                default=[],
                help="File known to pre-exist (repeatable)",
            )
        p.set_defaults(func=fn)

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_usage(sys.stderr)
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
