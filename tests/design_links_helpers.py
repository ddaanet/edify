"""Shared fixtures for ``scripts/check_design_links.sh`` contract tests.

The split-design invariants live in
``plans/design-doc-split/reports/split-report.md`` and
``plans/design-doc-split/reports/independent-review.md``; the real shapes
they were hand-checked against are ``docs/decisions.md`` and
``docs/references/*.md``. Each test builds a throwaway fixture tree under
``tmp_path`` and runs the script by absolute path with ``[ROOT]`` = that
tree — never the checkout — so the script's own behaviour against ``ROOT``
is what is exercised, not this repo's current document state.
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_design_links.sh"


def _run_check_design_links(root: Path) -> subprocess.CompletedProcess[str]:
    """Invoke ``check_design_links.sh`` by absolute path against ``root``."""
    return subprocess.run(
        [str(SCRIPT), str(root)],
        cwd=root if root.is_dir() else REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_decisions_md(path: Path, groups: list[tuple[str, str, list[str]]]) -> None:
    """Write a minimal ``docs/decisions.md`` fixture.

    ``groups`` is a list of ``(group_name, node_path, index_lines)``.
    ``node_path`` is the path the group's ``Argued in`` line names (real
    shape: root-relative, backtick-quoted, e.g.
    ``docs/references/cli-and-package.md``). ``index_lines`` are
    already-formatted ``- **D-n** — text.`` lines — the caller controls the
    exact shape, so malformed or duplicate fixtures are expressible.
    """
    lines = [
        "# Edify — decision index",
        "",
        "Every decision this project has taken, one conclusion line each,",
        "grouped by the node in `docs/references/` that argues it.",
        "",
    ]
    for group_name, node_path, index_lines in groups:
        lines.append(f"## {group_name}")
        lines.append("")
        lines.append(f"Argued in `{node_path}`.")
        lines.append("")
        lines.extend(index_lines)
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_node(path: Path, title: str, defs: list[str]) -> None:
    """Write a minimal ``docs/references/<node>.md`` fixture.

    ``defs`` are already-formatted paragraphs, each starting
    ``**D-n — conclusion.** explanation...`` — the real node shape (see
    ``docs/references/testing.md``).
    """
    lines = [
        f"# {title}",
        "",
        f"Decisions governing {title.lower()}. Read this before changing it.",
        "",
        "Part of the `docs/design.md` graph; conclusions are indexed in",
        "`docs/decisions.md`.",
        "",
    ]
    for d in defs:
        lines.append(d)
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _violation_lines(stdout: str) -> list[tuple[str, str, str]]:
    """Split each stdout line into ``(kind, id_or_path, detail)``.

    Per contract: one violation per line, ``<kind>: <ID or path>: <detail>``.
    Splits on ``": "`` with a max of 2 splits, so a path or detail
    containing its own ``": "`` does not fracture the tuple further than
    necessary.
    """
    result = []
    for line in stdout.splitlines():
        if not line:
            continue
        parts = line.split(": ", 2)
        assert len(parts) == 3, f"malformed violation line: {line!r}"
        result.append((parts[0], parts[1], parts[2]))
    return result
