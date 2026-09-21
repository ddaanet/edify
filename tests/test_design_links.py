"""Contract tests for ``scripts/check_design_links.sh``.

Pins the crosslink invariants of the split living design (hub
``docs/design.md``, decision index ``docs/decisions.md``, argument nodes
``docs/references/*.md``) named in
``plans/design-doc-split/reports/split-report.md`` §"Things I was unsure
about" item 4 and hand-checked in
``plans/design-doc-split/reports/independent-review.md`` §1-3. Each test
builds a minimal fixture tree under ``tmp_path`` using the real line shapes
those two reports were checked against, runs the script by absolute path,
and asserts exit status plus the violation line.

Real-shape notes (derived from ``docs/decisions.md`` and
``docs/references/*.md`` directly, not from the reports' prose):

- A node's decision definition is a bolded paragraph lead,
  ``**D-<n> — <conclusion>.**`` followed by explanation prose in the same
  paragraph (``docs/references/testing.md:10``).
- A decisions.md index line is ``- **D-<n>** — <conclusion>.``
  (``docs/decisions.md:15``).
- A group is ``## <Group Name>`` then a blank line then
  ``Argued in `docs/references/<file>.md`.`` (``docs/decisions.md:11-13``).
- The index conclusion is not always byte-identical to the node's: for a
  superseded decision the node's conclusion is a *prefix* of the index's,
  which appends a parenthetical the node's own lead-in does not carry
  (``docs/decisions.md:67-68`` vs. ``docs/references/pipeline-contracts.md:131``,
  D-31). Confirmed by joining wrapped paragraph lines and comparing all 85
  D-/L- ids in the real tree: 0 mismatches once wrapping is joined and the
  node conclusion's trailing period is stripped before the prefix check.
  Both node leads and index lines wrap across two physical lines under
  ``just format``'s 80-column reflow (e.g. D-12's lead in
  ``docs/references/cli-and-package.md``, D-54's index line) — the real
  implementation must join wrapped paragraphs before comparing, not read
  line-by-line.
"""

import re
from pathlib import Path

from .design_links_helpers import (
    REPO_ROOT,
    _run_check_design_links,
    _violation_lines,
    _write_decisions_md,
    _write_node,
)

SIGNOFF_RE = re.compile(
    r"^design-links: \d+ decisions indexed, defined once, "
    r"conclusions match, \d+ nodes present$"
)


def test_design_links_reports_unindexed_decision(tmp_path: Path) -> None:
    """A node's decision with no index line is ``unindexed-decision``."""
    root = tmp_path / "root"
    _write_node(
        root / "docs" / "references" / "cli-and-package.md",
        "CLI and package",
        ["**D-1 — Two output conventions, split by consumer.** Detail."],
    )
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [("CLI and package", "docs/references/cli-and-package.md", [])],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 1, result.stdout + result.stderr
    kinds = {(k, i) for k, i, _ in _violation_lines(result.stdout)}
    assert ("unindexed-decision", "D-1") in kinds, result.stdout


def test_design_links_reports_orphan_index_line(tmp_path: Path) -> None:
    """An index line with no node definition is ``orphan-index-line``."""
    root = tmp_path / "root"
    _write_node(
        root / "docs" / "references" / "testing.md",
        "Testing",
        ["**D-1 — Patch where the object is used.** Detail."],
    )
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [
            (
                "Testing",
                "docs/references/testing.md",
                [
                    "- **D-1** — Patch where the object is used.",
                    "- **D-2** — Never defined in any node.",
                ],
            )
        ],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 1, result.stdout + result.stderr
    kinds = {(k, i) for k, i, _ in _violation_lines(result.stdout)}
    assert ("orphan-index-line", "D-2") in kinds, result.stdout


def test_design_links_reports_duplicate_definition(tmp_path: Path) -> None:
    """An ID defined in two nodes is ``duplicate-definition``."""
    root = tmp_path / "root"
    _write_node(
        root / "docs" / "references" / "cli-and-package.md",
        "CLI and package",
        ["**D-1 — Two output conventions, split by consumer.** Detail."],
    )
    _write_node(
        root / "docs" / "references" / "testing.md",
        "Testing",
        ["**D-1 — Two output conventions, split by consumer.** Detail."],
    )
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [
            (
                "CLI and package",
                "docs/references/cli-and-package.md",
                ["- **D-1** — Two output conventions, split by consumer."],
            ),
            ("Testing", "docs/references/testing.md", []),
        ],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 1, result.stdout + result.stderr
    kinds = {(k, i) for k, i, _ in _violation_lines(result.stdout)}
    assert ("duplicate-definition", "D-1") in kinds, result.stdout


def test_design_links_reports_duplicate_index_line(tmp_path: Path) -> None:
    """Two index lines for one ID is ``duplicate-index-line``."""
    root = tmp_path / "root"
    _write_node(
        root / "docs" / "references" / "cli-and-package.md",
        "CLI and package",
        ["**D-1 — Two output conventions, split by consumer.** Detail."],
    )
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [
            (
                "CLI and package",
                "docs/references/cli-and-package.md",
                [
                    "- **D-1** — Two output conventions, split by consumer.",
                    "- **D-1** — Two output conventions, split by consumer.",
                ],
            )
        ],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 1, result.stdout + result.stderr
    kinds = {(k, i) for k, i, _ in _violation_lines(result.stdout)}
    assert ("duplicate-index-line", "D-1") in kinds, result.stdout


def test_design_links_reports_conclusion_mismatch(tmp_path: Path) -> None:
    """A non-prefix index conclusion is ``conclusion-mismatch``."""
    root = tmp_path / "root"
    _write_node(
        root / "docs" / "references" / "cli-and-package.md",
        "CLI and package",
        ["**D-1 — Two output conventions, split by consumer.** Detail."],
    )
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [
            (
                "CLI and package",
                "docs/references/cli-and-package.md",
                ["- **D-1** — An entirely unrelated conclusion text."],
            )
        ],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 1, result.stdout + result.stderr
    kinds = {(k, i) for k, i, _ in _violation_lines(result.stdout)}
    assert ("conclusion-mismatch", "D-1") in kinds, result.stdout


def test_design_links_reports_missing_node(tmp_path: Path) -> None:
    """A group whose ``Argued in`` path does not exist is ``missing-node``."""
    root = tmp_path / "root"
    (root / "docs" / "references").mkdir(parents=True, exist_ok=True)
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [("Ghost", "docs/references/ghost.md", [])],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 1, result.stdout + result.stderr
    kinds = {(k, i) for k, i, _ in _violation_lines(result.stdout)}
    assert ("missing-node", "docs/references/ghost.md") in kinds, result.stdout


def test_design_links_exit2_missing_decisions(tmp_path: Path) -> None:
    """A missing ``docs/decisions.md`` is a failure to run, not a clean pass."""
    root = tmp_path / "root"
    _write_node(
        root / "docs" / "references" / "cli-and-package.md",
        "CLI and package",
        ["**D-1 — Two output conventions, split by consumer.** Detail."],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stderr.strip(), "expected a stderr diagnostic"


def test_design_links_exit2_missing_references_dir(tmp_path: Path) -> None:
    """A missing ``docs/references/`` directory is a failure to run."""
    root = tmp_path / "root"
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [("CLI and package", "docs/references/cli-and-package.md", [])],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stderr.strip(), "expected a stderr diagnostic"


def test_design_links_exit2_outranks_exit1(tmp_path: Path) -> None:
    """A run-failure and a content violation together still exit 2, not 1.

    ``docs/decisions.md`` carries a self-contained violation (two index
    lines for the same ID, detectable from the index alone) while
    ``docs/references/`` is entirely absent. The missing directory must
    win: exit 2, never the 1 the duplicate index line would earn alone.
    """
    root = tmp_path / "root"
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [
            (
                "CLI and package",
                "docs/references/cli-and-package.md",
                [
                    "- **D-1** — Two output conventions, split by consumer.",
                    "- **D-1** — Two output conventions, split by consumer.",
                ],
            )
        ],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 2, result.stdout + result.stderr


def test_design_links_clean_tree_reports_signoff(tmp_path: Path) -> None:
    """A clean two-decision, two-node tree exits 0 with the sign-off line.

    Never a bare ``OK`` — the sign-off names the counts, so a check that
    silently ran nothing is distinguishable from one that verified
    something.
    """
    root = tmp_path / "root"
    _write_node(
        root / "docs" / "references" / "cli-and-package.md",
        "CLI and package",
        ["**D-1 — Two output conventions, split by consumer.** Detail."],
    )
    _write_node(
        root / "docs" / "references" / "testing.md",
        "Testing",
        ["**D-2 — Patch where the object is used, not where it is defined.** Detail."],
    )
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [
            (
                "CLI and package",
                "docs/references/cli-and-package.md",
                ["- **D-1** — Two output conventions, split by consumer."],
            ),
            (
                "Testing",
                "docs/references/testing.md",
                [
                    "- **D-2** — Patch where the object is used, not where "
                    "it is defined."
                ],
            ),
        ],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "design-links: 2 decisions indexed, defined once, conclusions "
        "match, 2 nodes present"
    ], result.stdout


def test_design_links_handles_node_path_with_space(tmp_path: Path) -> None:
    """A node path containing a space is matched intact, never split.

    NUL/space-safe path handling is the contract's own requirement — a
    reader splitting the ``Argued in`` path or the ``find``/``glob`` walk
    on whitespace would see ``docs/references/my`` and ``node.md`` as two
    tokens and report the node missing.
    """
    root = tmp_path / "root"
    _write_node(
        root / "docs" / "references" / "my node.md",
        "My Node",
        ["**D-1 — Some conclusion worth stating.** Detail."],
    )
    _write_decisions_md(
        root / "docs" / "decisions.md",
        [
            (
                "My Node",
                "docs/references/my node.md",
                ["- **D-1** — Some conclusion worth stating."],
            )
        ],
    )

    result = _run_check_design_links(root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.splitlines() == [
        "design-links: 1 decisions indexed, defined once, conclusions "
        "match, 1 nodes present"
    ], result.stdout


def test_design_links_real_repo_root(tmp_path: Path) -> None:
    """Run against the real repo tree: today's ``docs/`` is clean.

    Asserts the sign-off line's shape rather than its exact counts — the
    counts drift as decisions are added, but the format itself
    (``design-links: N decisions indexed, defined once, conclusions match,
    M nodes present``) is the contract. This test is red against the stub
    for the same reason every other test here is: the stub prints nothing,
    so no line matches.
    """
    result = _run_check_design_links(REPO_ROOT)

    assert result.returncode == 0, result.stdout + result.stderr
    assert any(SIGNOFF_RE.match(line) for line in result.stdout.splitlines()), (
        result.stdout
    )
