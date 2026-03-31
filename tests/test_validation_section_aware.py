"""Tests for section-aware task line validation."""

from edify.validation.session_structure import check_task_section_lines


class TestCheckTaskSectionLines:
    """Tests for check_task_section_lines function."""

    def test_valid_task_in_in_tree_tasks_section(self) -> None:
        """Valid task lines in In-tree Tasks section produce no errors."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Task One** — `command` | sonnet",
            "- [x] **Task Two** — `/skill plans/x` | opus",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_valid_task_in_worktree_tasks_section(self) -> None:
        """Valid task lines in Worktree Tasks section produce no errors."""
        lines = [
            "## Worktree Tasks",
            "- [ ] **Task A** — description | haiku",
            "- [>] **Task B** → `slug` — `/runbook plans/x`",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_valid_task_in_pending_tasks_legacy_section(self) -> None:
        """Legacy Pending Tasks section produces no errors.

        Valid task lines in legacy Pending Tasks section produce no errors.
        """
        lines = [
            "## Pending Tasks",
            "- [ ] **Old Task** — `/design foo`",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_blank_lines_in_task_section_ignored(self) -> None:
        """Blank lines in task sections don't produce errors."""
        lines = [
            "## In-tree Tasks",
            "",
            "- [ ] **Task** — description",
            "",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_indented_lines_in_task_section_allowed(self) -> None:
        """Indented sub-items (nested content) are allowed in task sections."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Task** — description",
            "  - nested sub-item",
            "    - deeply nested",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_html_comments_in_task_section_allowed(self) -> None:
        """HTML comments in task sections are allowed."""
        lines = [
            "## In-tree Tasks",
            "<!-- TODO: fix this -->",
            "- [ ] **Task** — description",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_h3_subsection_headings_in_task_section_allowed(self) -> None:
        """H3 subsection headings within task sections are allowed."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Task One** — description",
            "### Blocked / Terminal",
            "- [!] **Blocked Task** — waiting on signal",
            "- [†] **Failed Task** — needs user decision",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_unparseable_line_in_task_section_error(self) -> None:
        """Non-task lines that don't parse produce errors."""
        lines = [
            "## In-tree Tasks",
            "- [] **Missing space**",
            "Some random text",
        ]
        errors = check_task_section_lines(lines)
        assert len(errors) == 2
        assert any("line 2" in e for e in errors)
        assert any("line 3" in e for e in errors)

    def test_invalid_checkbox_in_task_section_error(self) -> None:
        """Task-like lines with invalid checkboxes produce errors."""
        lines = [
            "## In-tree Tasks",
            "- [?] **Task** — description",
            "- [X] **Task** — description",
        ]
        errors = check_task_section_lines(lines)
        assert len(errors) == 2
        assert any("line 2" in e for e in errors)
        assert any("line 3" in e for e in errors)

    def test_invalid_model_in_task_section_error(self) -> None:
        """Task lines with invalid model tier produce errors."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Task** — description | gpt4",
            "- [ ] **Task** — description | claude",
        ]
        errors = check_task_section_lines(lines)
        assert len(errors) == 2
        assert any("line 2" in e for e in errors)
        assert any("line 3" in e for e in errors)

    def test_non_task_section_lines_not_checked(self) -> None:
        """Lines in non-task sections are not validated as tasks."""
        lines = [
            "## Reference Files",
            "Some random content",
            "- not a task",
            "## Next Steps",
            "Do something",
            "- [?] not validated",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_multiple_errors_reported(self) -> None:
        """Multiple errors in task sections all reported."""
        lines = [
            "## In-tree Tasks",
            "- [?] **Bad Checkbox** — desc",
            "Random garbage line",
            "- [ ] **Task** — desc | invalid_model",
        ]
        errors = check_task_section_lines(lines)
        assert len(errors) == 3
        error_lines = [
            int(e.split("line ")[1].split(":")[0]) for e in errors if "line " in e
        ]
        assert 2 in error_lines
        assert 3 in error_lines
        assert 4 in error_lines

    def test_mixed_valid_and_invalid_in_section(self) -> None:
        """Mix of valid and invalid lines reports only invalid ones.

        Section with mix of valid and invalid lines reports only invalid ones.
        """
        lines = [
            "## In-tree Tasks",
            "- [ ] **Valid Task** — description",
            "- [?] **Invalid Checkbox** — desc",
            "- [x] **Another Valid** — `/cmd` | opus",
            "Unparseable line",
        ]
        errors = check_task_section_lines(lines)
        assert len(errors) == 2
        assert any("line 3" in e for e in errors)
        assert any("line 5" in e for e in errors)

    def test_all_valid_checkboxes_accepted(self) -> None:
        """All VALID_CHECKBOXES values are accepted."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Pending** — desc",
            "- [x] **Completed** — desc",
            "- [>] **In Progress** — desc",
            "- [!] **Blocked** — desc",
            "- [\u2020] **Failed** — desc",
            "- [-] **Canceled** — desc",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_all_valid_models_accepted(self) -> None:
        """All VALID_MODELS values are accepted."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Task** — desc | haiku",
            "- [ ] **Task** — desc | sonnet",
            "- [ ] **Task** — desc | opus",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_task_with_no_model_valid(self) -> None:
        """Task lines without model tier are valid."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Task** — description",
            "- [x] **Done** — `/cmd`",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_free_text_with_pipes_not_flagged_as_invalid_model(self) -> None:
        """Free-text descriptions with pipes not treated as metadata."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Test diamond migration** — Needs scoping"
            " | depends on runbook evolution (delivered) | sonnet | 0.9",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_capitalized_model_names_accepted(self) -> None:
        """Model names are case-insensitive (Sonnet, OPUS accepted)."""
        lines = [
            "## In-tree Tasks",
            "- [ ] **Task A** — desc | Sonnet",
            "- [ ] **Task B** — desc | OPUS",
            "- [ ] **Task C** — desc | Haiku",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_empty_lines_list_no_errors(self) -> None:
        """Empty or missing sections produce no errors."""
        lines: list[str] = []
        errors = check_task_section_lines(lines)
        assert errors == []

    def test_no_task_sections_no_errors(self) -> None:
        """File with no task sections produce no errors."""
        lines = [
            "## Reference Files",
            "- `path/to/file`",
            "## Next Steps",
            "Do something",
        ]
        errors = check_task_section_lines(lines)
        assert errors == []
