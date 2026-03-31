"""Pure-function unit tests for diff3_merge_segments resolution matrix."""

from edify.worktree.resolve import (
    _format_conflict_segment,
    _resolve_heading,
    _segments_to_content_with_conflicts,
    diff3_merge_segments,
)


class TestDiff3ResolutionMatrix:
    """Tests for all 15 rows of the resolution matrix."""

    def test_theirs_created(self) -> None:
        """Row 1: — | — | new → append theirs."""
        merged, conflicts = diff3_merge_segments({}, {}, {"When X": ["- new entry"]})
        assert "When X" in merged
        assert merged["When X"] == ["- new entry"]
        assert conflicts == []

    def test_ours_created(self) -> None:
        """Row 2: — | new | — → keep ours."""
        merged, conflicts = diff3_merge_segments({}, {"When X": ["- ours entry"]}, {})
        assert "When X" in merged
        assert merged["When X"] == ["- ours entry"]
        assert conflicts == []

    def test_convergent_creation(self) -> None:
        """Row 3: — | new-A | new-A → keep (same body, no conflict)."""
        merged, conflicts = diff3_merge_segments(
            {},
            {"When X": ["- same entry"]},
            {"When X": ["- same entry"]},
        )
        assert "When X" in merged
        assert merged["When X"] == ["- same entry"]
        assert conflicts == []

    def test_divergent_creation_conflict(self) -> None:
        """Row 4: — | new-A | new-B → conflict (divergent creation)."""
        merged, conflicts = diff3_merge_segments(
            {},
            {"When X": ["- ours version"]},
            {"When X": ["- theirs version"]},
        )
        assert "When X" in conflicts
        assert "When X" in merged
        assert merged["When X"] == ["- ours version"]

    def test_unchanged(self) -> None:
        """Row 5: entry | entry | entry → keep (unchanged)."""
        body = ["- unchanged"]
        merged, conflicts = diff3_merge_segments(
            {"When X": body}, {"When X": body}, {"When X": body}
        )
        assert "When X" in merged
        assert merged["When X"] == body
        assert conflicts == []

    def test_only_ours_modified(self) -> None:
        """Row 6: entry | modified | entry → keep ours."""
        merged, conflicts = diff3_merge_segments(
            {"When X": ["- original"]},
            {"When X": ["- ours modified"]},
            {"When X": ["- original"]},
        )
        assert merged["When X"] == ["- ours modified"]
        assert conflicts == []

    def test_only_theirs_modified(self) -> None:
        """Row 7: entry | entry | modified → take theirs."""
        merged, conflicts = diff3_merge_segments(
            {"When X": ["- original"]},
            {"When X": ["- original"]},
            {"When X": ["- theirs modified"]},
        )
        assert merged["When X"] == ["- theirs modified"]
        assert conflicts == []

    def test_convergent_edit(self) -> None:
        """Row 8: entry | modified-A | modified-A → keep (same edit, no conflict)."""
        merged, conflicts = diff3_merge_segments(
            {"When X": ["- original"]},
            {"When X": ["- both modified same"]},
            {"When X": ["- both modified same"]},
        )
        assert merged["When X"] == ["- both modified same"]
        assert conflicts == []

    def test_divergent_edit_conflict(self) -> None:
        """Row 9: entry | modified-A | modified-B → conflict."""
        merged, conflicts = diff3_merge_segments(
            {"When X": ["- original"]},
            {"When X": ["- ours modified"]},
            {"When X": ["- theirs modified"]},
        )
        assert "When X" in conflicts
        assert merged["When X"] == ["- ours modified"]

    def test_ours_deleted_theirs_unchanged(self) -> None:
        """Row 10: entry | — | entry → delete."""
        merged, conflicts = diff3_merge_segments(
            {"When X": ["- body"]},
            {},
            {"When X": ["- body"]},
        )
        assert "When X" not in merged
        assert conflicts == []

    def test_theirs_deleted_ours_unchanged(self) -> None:
        """Row 11: entry | entry | — → delete."""
        merged, conflicts = diff3_merge_segments(
            {"When X": ["- body"]},
            {"When X": ["- body"]},
            {},
        )
        assert "When X" not in merged
        assert conflicts == []

    def test_ours_deleted_theirs_modified_conflict(self) -> None:
        """Row 12: entry | — | modified → conflict."""
        _merged, conflicts = diff3_merge_segments(
            {"When X": ["- original"]},
            {},
            {"When X": ["- modified by theirs"]},
        )
        assert "When X" in conflicts

    def test_theirs_deleted_ours_modified_conflict(self) -> None:
        """Row 13: entry | modified | — → conflict."""
        _merged, conflicts = diff3_merge_segments(
            {"When X": ["- original"]},
            {"When X": ["- modified by ours"]},
            {},
        )
        assert "When X" in conflicts

    def test_both_deleted(self) -> None:
        """Row 14: entry | — | — → delete."""
        merged, conflicts = diff3_merge_segments(
            {"When X": ["- body"]},
            {},
            {},
        )
        assert "When X" not in merged
        assert conflicts == []

    # Row 15 (— | — | —) is not possible: heading must appear in at least one dict.


class TestDiff3Preamble:
    """Tests for preamble (empty-key) segment handling."""

    def test_preamble_additive_merge(self) -> None:
        """Preamble lines from both sides combined (additive)."""
        base = {"": ["# Header", "", "---"]}
        ours = {"": ["# Header", "", "---", "- ours line"]}
        theirs = {"": ["# Header", "", "---", "- theirs line"]}
        merged, conflicts = diff3_merge_segments(base, ours, theirs)
        preamble = merged.get("", [])
        assert "- ours line" in preamble
        assert "- theirs line" in preamble
        assert conflicts == []

    def test_preamble_no_duplicate(self) -> None:
        """Preamble: shared lines not duplicated."""
        base = {"": ["# Header"]}
        ours = {"": ["# Header", "- shared"]}
        theirs = {"": ["# Header", "- shared"]}
        merged, _ = diff3_merge_segments(base, ours, theirs)
        assert merged.get("", []).count("- shared") == 1


class TestDiff3Ordering:
    """Tests for heading ordering in merged output."""

    def test_base_order_preserved(self) -> None:
        """Headings from base appear in base order."""
        base = {"When A": ["- a"], "When B": ["- b"], "When C": ["- c"]}
        ours = dict(base)
        theirs = dict(base)
        merged, _ = diff3_merge_segments(base, ours, theirs)
        keys = [k for k in merged if k != ""]
        assert keys == ["When A", "When B", "When C"]

    def test_theirs_new_appended_after_ours(self) -> None:
        """Theirs-only new entries appear after ours entries."""
        base = {"When A": ["- a"]}
        ours = {"When A": ["- a"], "When B": ["- b"]}
        theirs = {"When A": ["- a"], "When C": ["- c"]}
        merged, _ = diff3_merge_segments(base, ours, theirs)
        keys = [k for k in merged if k != ""]
        assert keys.index("When B") < keys.index("When C")


class TestFormatConflictSegment:
    """Tests for _format_conflict_segment marker output."""

    def test_markers_present(self) -> None:
        """_format_conflict_segment produces heading and all three markers."""
        lines = _format_conflict_segment("When X", ["- ours"], ["- theirs"])
        assert lines[0] == "## When X"
        assert "<<<<<<< ours" in lines
        assert "=======" in lines
        assert ">>>>>>> theirs" in lines

    def test_body_content_inside_markers(self) -> None:
        """Body lines appear inside the correct marker sections."""
        lines = _format_conflict_segment(
            "When X", ["- ours body", "- ours line 2"], ["- theirs body"]
        )
        open_idx = lines.index("<<<<<<< ours")
        sep_idx = lines.index("=======")
        close_idx = lines.index(">>>>>>> theirs")
        ours_section = lines[open_idx + 1 : sep_idx]
        theirs_section = lines[sep_idx + 1 : close_idx]
        assert ours_section == ["- ours body", "- ours line 2"]
        assert theirs_section == ["- theirs body"]

    def test_empty_body(self) -> None:
        """Empty body (deleted side) works without error."""
        lines = _format_conflict_segment("When X", [], ["- theirs"])
        assert "<<<<<<< ours" in lines
        assert "- theirs" in lines


class TestSegmentsToContentWithConflicts:
    """Tests for _segments_to_content_with_conflicts assembly."""

    def test_clean_segment_rendered_normally(self) -> None:
        """Non-conflicting segments appear as heading + body."""
        merged = {"When A": ["- body"]}
        content = _segments_to_content_with_conflicts(merged, [], {}, {})
        assert "## When A" in content
        assert "- body" in content
        assert "<<<<<<<" not in content

    def test_conflicting_segment_has_markers(self) -> None:
        """Conflicting segment gets diff3 markers."""
        merged = {"When X": ["- ours"]}
        ours = {"When X": ["- ours"]}
        theirs = {"When X": ["- theirs"]}
        content = _segments_to_content_with_conflicts(merged, ["When X"], ours, theirs)
        assert "<<<<<<<" in content
        assert "=======" in content
        assert ">>>>>>>" in content
        assert "- ours" in content
        assert "- theirs" in content

    def test_mixed_clean_and_conflict(self) -> None:
        """Mixed: clean segment normal, conflict segment has markers."""
        merged = {"When A": ["- clean"], "When B": ["- ours b"]}
        ours = {"When B": ["- ours b"]}
        theirs = {"When B": ["- theirs b"]}
        content = _segments_to_content_with_conflicts(merged, ["When B"], ours, theirs)
        assert "## When A" in content
        assert "- clean" in content
        assert "<<<<<<<" in content
        assert "- theirs b" in content

    def test_preamble_not_wrapped_in_markers(self) -> None:
        """Preamble (empty key) rendered without ## heading."""
        merged = {"": ["# Header", "preamble line"], "When X": ["- body"]}
        content = _segments_to_content_with_conflicts(merged, [], {}, {})
        assert content.startswith("# Header")
        assert "## " not in content.split("## When")[0]


class TestResolveHeadingDirect:
    """Direct tests of _resolve_heading for the deletion/creation cases."""

    def test_row10_ours_absent_theirs_unchanged(self) -> None:
        """Row 10: ours absent, theirs matches base → omit (no conflict)."""
        body, is_conflict = _resolve_heading(
            "When X",
            {"When X": ["- body"]},
            {},
            {"When X": ["- body"]},
        )
        assert body is None
        assert not is_conflict

    def test_row11_theirs_absent_ours_unchanged(self) -> None:
        """Row 11: theirs absent, ours matches base → omit (no conflict)."""
        body, is_conflict = _resolve_heading(
            "When X",
            {"When X": ["- body"]},
            {"When X": ["- body"]},
            {},
        )
        assert body is None
        assert not is_conflict

    def test_row12_ours_absent_theirs_modified(self) -> None:
        """Row 12: ours absent, theirs modified → conflict."""
        _body, is_conflict = _resolve_heading(
            "When X",
            {"When X": ["- original"]},
            {},
            {"When X": ["- theirs modified"]},
        )
        assert is_conflict

    def test_row13_theirs_absent_ours_modified(self) -> None:
        """Row 13: theirs absent, ours modified → conflict."""
        _body, is_conflict = _resolve_heading(
            "When X",
            {"When X": ["- original"]},
            {"When X": ["- ours modified"]},
            {},
        )
        assert is_conflict

    def test_row4_divergent_creation(self) -> None:
        """Row 4: both new (absent from base), different bodies → conflict."""
        _body, is_conflict = _resolve_heading(
            "When X",
            {},
            {"When X": ["- ours version"]},
            {"When X": ["- theirs version"]},
        )
        assert is_conflict
