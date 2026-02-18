"""Tests for per-section session.md merge strategies (D-5)."""

import pytest

from claudeutils.worktree.resolve import _merge_session_contents
from claudeutils.worktree.session import extract_blockers


class TestStatusLineSquashStrategy:
    """Cycle 5.2: Status line keeps ours, discards theirs."""

    def test_status_line_squash_strategy(self) -> None:
        """Ours status line preserved, theirs discarded."""
        ours = (
            "# Session Handoff: 2026-02-16\n"
            "\n"
            "**Status:** Main work in progress.\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — `/do-a` | sonnet\n"
        )
        theirs = (
            "# Session Handoff: 2026-02-15\n"
            "\n"
            "**Status:** Worktree work happening.\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — `/do-a` | sonnet\n"
        )
        result = _merge_session_contents(ours, theirs)
        assert "# Session Handoff: 2026-02-16" in result
        assert "**Status:** Main work in progress." in result
        assert "2026-02-15" not in result
        assert "Worktree work happening" not in result


class TestCompletedThisSessionSquashStrategy:
    """Cycle 5.3: Completed This Session keeps ours, discards theirs."""

    def test_completed_this_session_squash_strategy(self) -> None:
        """Ours completed items preserved, theirs discarded."""
        ours = (
            "# Session Handoff: 2026-02-16\n"
            "\n"
            "## Completed This Session\n"
            "\n"
            "- Main item 1\n"
            "- Main item 2\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
        )
        theirs = (
            "# Session Handoff: 2026-02-15\n"
            "\n"
            "## Completed This Session\n"
            "\n"
            "- Worktree item 1\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
        )
        result = _merge_session_contents(ours, theirs)
        assert "Main item 1" in result
        assert "Main item 2" in result
        assert "Worktree item 1" not in result


class TestPendingTasksAdditiveStrategy:
    """Cycle 5.4: Pending Tasks uses additive union by task name."""

    def test_pending_tasks_additive_strategy(self) -> None:
        """Union by task name, no duplicates."""
        ours = (
            "# Session Handoff: 2026-02-16\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — `/do-a` | sonnet\n"
            "- [ ] **Task B** — `/do-b` | sonnet\n"
        )
        theirs = (
            "# Session Handoff: 2026-02-15\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task B** — `/do-b` | sonnet\n"
            "- [ ] **Task C** — `/do-c` | haiku\n"
        )
        result = _merge_session_contents(ours, theirs)
        assert "**Task A**" in result
        assert "**Task B**" in result
        assert "**Task C**" in result
        assert result.count("**Task B**") == 1


class TestKeepOursStrategies:
    """Cycle 5.5: Worktree Tasks, Reference Files, Next Steps all keep ours."""

    @pytest.mark.parametrize(
        ("section_name", "ours_content", "theirs_content"),
        [
            (
                "Worktree Tasks",
                "- [ ] **WT Task** → `slug` — main tracking",
                "- [ ] **WT Task** → `slug` — worktree view",
            ),
            (
                "Reference Files",
                "- agents/session.md\n- plans/foo/design.md",
                "- /worktree/path/session.md\n- /worktree/path/design.md",
            ),
            (
                "Next Steps",
                "Continue with Phase 5 on main.",
                "Finish worktree-specific work.",
            ),
        ],
    )
    def test_keep_ours_strategies(
        self, section_name: str, ours_content: str, theirs_content: str
    ) -> None:
        """Ours section preserved, theirs discarded."""
        ours = (
            "# Session Handoff: 2026-02-16\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            f"## {section_name}\n"
            "\n"
            f"{ours_content}\n"
        )
        theirs = (
            "# Session Handoff: 2026-02-15\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            f"## {section_name}\n"
            "\n"
            f"{theirs_content}\n"
        )
        result = _merge_session_contents(ours, theirs)
        assert ours_content in result
        assert theirs_content not in result


class TestExtractBlockersFunction:
    """Cycle 5.6: extract_blockers() parses Blockers / Gotchas section."""

    def test_single_blocker(self) -> None:
        """Single blocker with continuation line."""
        content = "# Session\n\n## Blockers / Gotchas\n\n- Issue X\n  Details here\n"
        result = extract_blockers(content)
        assert len(result) == 1
        assert result[0] == ["- Issue X", "  Details here"]

    def test_two_blockers(self) -> None:
        """Two blockers separated by blank line."""
        content = (
            "# Session\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Issue X\n"
            "  Detail X\n"
            "\n"
            "- Issue Y\n"
            "  Detail Y\n"
        )
        result = extract_blockers(content)
        assert len(result) == 2

    def test_no_blockers_section(self) -> None:
        """Missing Blockers section returns empty list."""
        content = "# Session\n\n## Pending Tasks\n\n- [ ] **Task** — cmd\n"
        result = extract_blockers(content)
        assert result == []

    def test_multiline_blocker(self) -> None:
        """Blocker with 3 continuation lines."""
        content = (
            "# Session\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Big issue\n"
            "  Line 1\n"
            "  Line 2\n"
            "  Line 3\n"
        )
        result = extract_blockers(content)
        assert len(result) == 1
        assert len(result[0]) == 4
        assert result[0][0] == "- Big issue"
        assert result[0][3] == "  Line 3"


class TestBlockersEvaluateStrategy:
    """Cycle 5.7: Blockers from theirs appended with [from: slug] tag."""

    def test_blockers_evaluate_strategy(self) -> None:
        """Theirs blockers tagged and appended to ours."""
        ours = (
            "# Session Handoff: 2026-02-16\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Main blocker\n"
            "  Main detail\n"
        )
        theirs = (
            "# Session Handoff: 2026-02-15\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- WT blocker 1\n"
            "  WT detail 1\n"
            "\n"
            "- WT blocker 2\n"
            "  WT detail 2\n"
        )
        result = _merge_session_contents(ours, theirs, slug="test-slug")
        assert "- Main blocker" in result
        assert "- WT blocker 1 [from: test-slug]" in result
        assert "- WT blocker 2 [from: test-slug]" in result
        assert "  WT detail 1" in result
        assert "  WT detail 2" in result

    def test_blockers_no_section_in_ours(self) -> None:
        """Blockers section created in ours when only theirs has it."""
        ours = (
            "# Session Handoff: 2026-02-16\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
        )
        theirs = (
            "# Session Handoff: 2026-02-15\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- New blocker\n"
        )
        result = _merge_session_contents(ours, theirs, slug="wt-slug")
        assert "## Blockers / Gotchas" in result
        assert "- New blocker [from: wt-slug]" in result


class TestFullSessionMdMergeIntegration:
    """Cycle 5.8: Integration test for all per-section merge strategies."""

    def test_full_session_md_merge_integration(self) -> None:
        """All D-5 strategies applied correctly in combination."""
        ours = (
            "# Session Handoff: 2026-02-16\n"
            "\n"
            "**Status:** Main branch active work.\n"
            "\n"
            "## Completed This Session\n"
            "\n"
            "- Main completed item 1\n"
            "- Main completed item 2\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task A** — `/do-a` | sonnet\n"
            "- [ ] **Task B** — `/do-b` | haiku\n"
            "\n"
            "## Worktree Tasks\n"
            "\n"
            "- [ ] **WT Task** → `other-slug` — cmd | sonnet\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- Main blocker\n"
            "  Main detail\n"
            "\n"
            "## Reference Files\n"
            "\n"
            "- agents/session.md\n"
            "\n"
            "## Next Steps\n"
            "\n"
            "Continue Phase 5 on main.\n"
        )
        theirs = (
            "# Session Handoff: 2026-02-15\n"
            "\n"
            "**Status:** Worktree branch work.\n"
            "\n"
            "## Completed This Session\n"
            "\n"
            "- Worktree completed item\n"
            "\n"
            "## Pending Tasks\n"
            "\n"
            "- [ ] **Task B** — `/do-b` | haiku\n"
            "- [ ] **Task C** — `/do-c` | opus\n"
            "\n"
            "## Worktree Tasks\n"
            "\n"
            "- [ ] **WT Other** → `wt` — cmd\n"
            "\n"
            "## Blockers / Gotchas\n"
            "\n"
            "- WT blocker 1\n"
            "  WT detail 1\n"
            "\n"
            "- WT blocker 2\n"
            "  WT detail 2\n"
            "\n"
            "## Reference Files\n"
            "\n"
            "- /worktree/path/session.md\n"
            "\n"
            "## Next Steps\n"
            "\n"
            "Finish worktree work.\n"
        )
        result = _merge_session_contents(ours, theirs, slug="test-slug")

        # Status line: ours preserved, theirs discarded
        assert "# Session Handoff: 2026-02-16" in result
        assert "**Status:** Main branch active work." in result
        assert "2026-02-15" not in result
        assert "Worktree branch work" not in result

        # Completed This Session: ours preserved, theirs discarded
        assert "Main completed item 1" in result
        assert "Main completed item 2" in result
        assert "Worktree completed item" not in result

        # Pending Tasks: union (A, B, C — no duplicate B)
        assert "**Task A**" in result
        assert "**Task B**" in result
        assert "**Task C**" in result
        assert result.count("**Task B**") == 1

        # Worktree Tasks: ours preserved, theirs discarded
        assert "**WT Task**" in result
        assert "**WT Other**" not in result

        # Blockers: ours preserved, theirs appended with tag
        assert "- Main blocker" in result
        assert "- WT blocker 1 [from: test-slug]" in result
        assert "- WT blocker 2 [from: test-slug]" in result

        # Reference Files: ours preserved, theirs discarded
        assert "- agents/session.md" in result
        assert "/worktree/path/session.md" not in result

        # Next Steps: ours preserved, theirs discarded
        assert "Continue Phase 5 on main." in result
        assert "Finish worktree work." not in result
