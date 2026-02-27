"""Characterization tests for learnings consolidation merge scenarios."""

import subprocess
from collections.abc import Callable
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from claudeutils.validation.learnings import parse_segments
from claudeutils.worktree.remerge import remerge_learnings_md
from claudeutils.worktree.resolve import diff3_merge_segments

PREAMBLE_STR = "# Learnings\n\n---\n"
ENTRY_A = "## When A\n- body A\n"
ENTRY_B = "## When B\n- body B\n"
ENTRY_C = "## When C\n- body C\n"
ENTRY_E = "## When E\n- body E new\n"


def _git(repo: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        msg = f"git {' '.join(args)} failed: {result.stderr}"
        raise RuntimeError(msg)


def _write_commit(repo: Path, relpath: str, content: str, msg: str) -> None:
    target = repo / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    _git(repo, "add", relpath)
    _git(repo, "commit", "-m", msg)


PREAMBLE = {"": ["# Learnings", "", "---"]}


class TestConsolidationScenarios:
    """Consolidation merge scenarios: ours drops entries, theirs adds entries."""

    def test_consolidation_with_new_entries(self) -> None:
        """Ours consolidated A+B away; theirs added E.

        Merged keeps C and E only.
        """
        base = {
            **PREAMBLE,
            "When A": ["- body A"],
            "When B": ["- body B"],
            "When C": ["- body C"],
        }
        ours = {**PREAMBLE, "When C": ["- body C"]}
        theirs = {
            **PREAMBLE,
            "When A": ["- body A"],
            "When B": ["- body B"],
            "When C": ["- body C"],
            "When E": ["- body E"],
        }

        merged, conflicts = diff3_merge_segments(base, ours, theirs)

        assert conflicts == []
        assert "When C" in merged
        assert "When E" in merged
        assert "When A" not in merged
        assert "When B" not in merged

    def test_consolidation_no_new_entries(self) -> None:
        """Ours consolidated A+B away; theirs unchanged from base.

        Merged keeps C only.
        """
        base = {
            **PREAMBLE,
            "When A": ["- body A"],
            "When B": ["- body B"],
            "When C": ["- body C"],
        }
        ours = {**PREAMBLE, "When C": ["- body C"]}
        theirs = {
            **PREAMBLE,
            "When A": ["- body A"],
            "When B": ["- body B"],
            "When C": ["- body C"],
        }

        merged, conflicts = diff3_merge_segments(base, ours, theirs)

        assert conflicts == []
        assert "When C" in merged
        assert "When A" not in merged
        assert "When B" not in merged

    def test_modified_consolidated_away_entry(self) -> None:
        """Ours deleted A; theirs modified A.

        Deletion-vs-modification conflict on A.
        """
        base = {**PREAMBLE, "When A": ["- original A"], "When B": ["- body B"]}
        ours = {**PREAMBLE, "When B": ["- body B"]}
        theirs = {
            **PREAMBLE,
            "When A": ["- modified A by theirs"],
            "When B": ["- body B"],
        }

        _merged, conflicts = diff3_merge_segments(base, ours, theirs)

        assert "When A" in conflicts

    def test_modified_surviving_entry(self) -> None:
        """Ours kept B unchanged, deleted A; theirs modified B body.

        Merged takes theirs B.
        """
        base = {**PREAMBLE, "When A": ["- body A"], "When B": ["- original B"]}
        ours = {**PREAMBLE, "When B": ["- original B"]}
        theirs = {
            **PREAMBLE,
            "When A": ["- body A"],
            "When B": ["- modified B by theirs"],
        }

        merged, conflicts = diff3_merge_segments(base, ours, theirs)

        assert conflicts == []
        assert merged["When B"] == ["- modified B by theirs"]
        assert "When A" not in merged

    def test_no_consolidation_both_added(self) -> None:
        """No consolidation; ours added B, theirs added C.

        All three present in merged.
        """
        base = {**PREAMBLE, "When A": ["- body A"]}
        ours = {**PREAMBLE, "When A": ["- body A"], "When B": ["- body B"]}
        theirs = {**PREAMBLE, "When A": ["- body A"], "When C": ["- body C"]}

        merged, conflicts = diff3_merge_segments(base, ours, theirs)

        assert conflicts == []
        assert "When A" in merged
        assert "When B" in merged
        assert "When C" in merged


class TestConsolidationIntegration:
    """Integration tests for consolidation via remerge_learnings_md()."""

    def test_branch_to_main_consolidation(
        self,
        tmp_path: Path,
        monkeypatch: MonkeyPatch,
        init_repo: Callable[[Path], None],
    ) -> None:
        """Main consolidated A+B away; branch has pre-consolidation + new E.

        Merged (from main's perspective) keeps C and E only.
        """
        repo = tmp_path / "repo"
        repo.mkdir()
        init_repo(repo)

        # Common ancestor: A + B + C
        _write_commit(
            repo,
            "agents/learnings.md",
            PREAMBLE_STR + ENTRY_A + ENTRY_B + ENTRY_C,
            "Base: A B C",
        )

        # Branch: pre-consolidation + new E
        _git(repo, "checkout", "-b", "test-consolidation")
        _write_commit(
            repo,
            "agents/learnings.md",
            PREAMBLE_STR + ENTRY_A + ENTRY_B + ENTRY_C + ENTRY_E,
            "Branch: A B C E",
        )

        # Main: consolidate — keep C only
        _git(repo, "checkout", "main")
        _write_commit(
            repo,
            "agents/learnings.md",
            PREAMBLE_STR + ENTRY_C,
            "Main: consolidated to C",
        )

        # Start merge (main merges branch)
        subprocess.run(
            ["git", "merge", "--no-commit", "--no-ff", "test-consolidation"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

        monkeypatch.chdir(repo)
        remerge_learnings_md()

        segments = parse_segments((repo / "agents" / "learnings.md").read_text())
        assert "When C" in segments
        assert "When E" in segments
        assert "When A" not in segments
        assert "When B" not in segments

    def test_main_to_branch_consolidation(
        self,
        tmp_path: Path,
        monkeypatch: MonkeyPatch,
        init_repo: Callable[[Path], None],
    ) -> None:
        """Branch merges consolidated main; branch has pre-consolidation + E.

        Merged (from branch's perspective) keeps C and E only.
        """
        repo = tmp_path / "repo"
        repo.mkdir()
        init_repo(repo)

        # Common ancestor: A + B + C
        _write_commit(
            repo,
            "agents/learnings.md",
            PREAMBLE_STR + ENTRY_A + ENTRY_B + ENTRY_C,
            "Base: A B C",
        )

        # Branch: pre-consolidation + new E (diverges from base)
        _git(repo, "checkout", "-b", "test-consolidation")
        _write_commit(
            repo,
            "agents/learnings.md",
            PREAMBLE_STR + ENTRY_A + ENTRY_B + ENTRY_C + ENTRY_E,
            "Branch: A B C E",
        )

        # Main: consolidate — keep C only
        _git(repo, "checkout", "main")
        _write_commit(
            repo,
            "agents/learnings.md",
            PREAMBLE_STR + ENTRY_C,
            "Main: consolidated to C",
        )

        # Switch to branch and merge main into it
        _git(repo, "checkout", "test-consolidation")
        subprocess.run(
            ["git", "merge", "--no-commit", "--no-ff", "main"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )

        monkeypatch.chdir(repo)
        remerge_learnings_md()

        segments = parse_segments((repo / "agents" / "learnings.md").read_text())
        assert "When C" in segments
        assert "When E" in segments
        assert "When A" not in segments
        assert "When B" not in segments
