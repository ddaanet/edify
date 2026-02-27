"""Characterization tests for learnings consolidation merge scenarios."""

from claudeutils.worktree.resolve import diff3_merge_segments

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
