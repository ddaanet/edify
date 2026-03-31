"""Tests for blocker merge fixes: section positioning and deduplication."""

from edify.worktree.resolve import _merge_session_contents


class TestBlockerSectionPositioning:
    """Blockers section inserted at correct structural position, not EOF."""

    def test_blockers_section_positioned_before_reference_files(self) -> None:
        """New Blockers section inserted before Reference Files, not at EOF."""
        ours = (
            "# Session: Main\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Reference Files\n"
            "\n"
            "- agents/session.md\n"
        )
        theirs = (
            "# Session: Branch\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- New blocker\n"
        )
        result = _merge_session_contents(ours, theirs, slug="wt-fix")
        blockers_pos = result.index("## Blockers / Gotchas")
        ref_pos = result.index("## Reference Files")
        assert blockers_pos < ref_pos

    def test_blockers_section_positioned_before_next_steps(self) -> None:
        """New Blockers section inserted before Next Steps."""
        ours = (
            "# Session: Main\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Next Steps\n"
            "\n"
            "Continue work.\n"
        )
        theirs = (
            "# Session: Branch\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Branch blocker\n"
        )
        result = _merge_session_contents(ours, theirs, slug="wt-fix")
        blockers_pos = result.index("## Blockers / Gotchas")
        next_pos = result.index("## Next Steps")
        assert blockers_pos < next_pos

    def test_blockers_before_earliest_when_both_sections_present(self) -> None:
        """Picks earliest of Reference Files and Next Steps for insertion."""
        ours = (
            "# Session: Main\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Reference Files\n"
            "\n"
            "- agents/session.md\n"
            "\n"
            "## Next Steps\n"
            "\n"
            "Continue work.\n"
        )
        theirs = (
            "# Session: Branch\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Branch blocker\n"
        )
        result = _merge_session_contents(ours, theirs, slug="wt-fix")
        blockers_pos = result.index("## Blockers / Gotchas")
        ref_pos = result.index("## Reference Files")
        next_pos = result.index("## Next Steps")
        assert blockers_pos < ref_pos
        assert blockers_pos < next_pos

    def test_blockers_at_eof_when_no_later_sections(self) -> None:
        """Blockers appended at EOF when no later sections exist."""
        ours = (
            "# Session: Main\n\n## In-tree Tasks\n\n- [ ] **Task A** — cmd | sonnet\n"
        )
        theirs = (
            "# Session: Branch\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Branch blocker\n"
        )
        result = _merge_session_contents(ours, theirs, slug="wt-fix")
        assert "## Blockers / Gotchas" in result
        assert "- Branch blocker [from: wt-fix]" in result


class TestBlockerDeduplication:
    """Blockers already in ours not re-appended from theirs."""

    def test_duplicate_blockers_filtered(self) -> None:
        """Blockers with same first line in ours are not appended again."""
        ours = (
            "# Session: Main\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Existing blocker\n"
        )
        theirs = (
            "# Session: Branch\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Existing blocker\n"
            "- New from branch\n"
        )
        result = _merge_session_contents(ours, theirs, slug="wt-fix")
        assert result.count("Existing blocker") == 1
        assert "- New from branch [from: wt-fix]" in result

    def test_dedup_matches_despite_different_continuation_lines(self) -> None:
        """First-line match deduplicates even when continuation lines differ."""
        ours = (
            "# Session: Main\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Shared blocker\n"
            "  Ours detail\n"
        )
        theirs = (
            "# Session: Branch\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Shared blocker\n"
            "  Theirs different detail\n"
        )
        result = _merge_session_contents(ours, theirs, slug="wt-fix")
        assert result.count("Shared blocker") == 1
        assert "Ours detail" in result
        assert "Theirs different detail" not in result

    def test_dedup_strips_prior_merge_tags(self) -> None:
        """Blockers tagged by prior merge still match untagged theirs."""
        ours = (
            "# Session: Main\n\n## Blockers / Gotchas\n\n- Known issue [from: old-wt]\n"
        )
        theirs = "# Session: Branch\n\n## Blockers / Gotchas\n\n- Known issue\n"
        result = _merge_session_contents(ours, theirs, slug="wt-fix")
        assert result.count("Known issue") == 1
        assert "[from: wt-fix]" not in result

    def test_all_duplicate_blockers_produces_no_section_creation(self) -> None:
        """When all theirs blockers match ours, no empty section added."""
        ours = (
            "# Session: Main\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Only blocker\n"
        )
        theirs = (
            "# Session: Branch\n"
            "\n"
            "## In-tree Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Only blocker\n"
        )
        result = _merge_session_contents(ours, theirs, slug="wt-fix")
        assert result.count("Only blocker") == 1
        # No tagged duplicate
        assert "[from: wt-fix]" not in result
