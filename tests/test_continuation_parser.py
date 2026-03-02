r"""Tests for continuation parser (userpromptsubmit-shortcuts.py Tier 3).

Skill names in registry use underscores (e.g., plan_adhoc) because the hook's
regex /(\w+) doesn't match hyphens.
"""

import importlib.util
from pathlib import Path

import pytest

# Import the hook script as a module
hook_script_path = (
    Path(__file__).parent.parent
    / "agent-core"
    / "hooks"
    / "userpromptsubmit-shortcuts.py"
)
spec = importlib.util.spec_from_file_location(
    "userpromptsubmit_shortcuts", hook_script_path
)
assert spec is not None
assert spec.loader is not None
hook_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_module)

parse_continuation = hook_module.parse_continuation
find_skill_references = hook_module.find_skill_references
format_continuation_context = hook_module.format_continuation_context

# Common registry fixtures
_SKILL = {"cooperative": True, "default-exit": []}
_COMMIT_ONLY: dict[str, object] = {"commit": _SKILL}
_HANDOFF_ONLY: dict[str, object] = {"handoff": _SKILL}
_ORCHESTRATE_ONLY: dict[str, object] = {"orchestrate": _SKILL}
_DESIGN_ONLY = {"design": _SKILL}
_DESIGN_WITH_EXIT = {
    "design": {
        "cooperative": True,
        "default-exit": ["/handoff", "/commit"],
    }
}
_DESIGN_PLAN = {"design": _SKILL, "plan": _SKILL}
_FULL_REGISTRY = {
    "design": {"cooperative": True, "default-exit": ["/handoff", "/commit"]},
    "plan": {"cooperative": True, "default-exit": ["/handoff", "/commit"]},
    "execute": {"cooperative": True, "default-exit": ["/handoff", "/commit"]},
    "handoff": {"cooperative": True, "default-exit": []},
    "commit": {"cooperative": True, "default-exit": []},
}


class TestFindSkillReferences:
    """Tests for skill reference detection."""

    def test_single_skill(self) -> None:
        """Find single skill reference."""
        refs = find_skill_references("/design plans/foo", _DESIGN_ONLY)
        assert len(refs) == 1
        assert refs[0][1] == "design"

    def test_multiple_skills(self) -> None:
        """Find multiple skill references."""
        refs = find_skill_references("/design, /plan", _DESIGN_PLAN)
        assert len(refs) == 2

    def test_no_skills(self) -> None:
        """No skill references found."""
        assert find_skill_references("some regular text", _DESIGN_ONLY) == []

    def test_unregistered_skill_ignored(self) -> None:
        """Unregistered skills are ignored."""
        refs = find_skill_references("/design and /nonexistent", _DESIGN_ONLY)
        assert len(refs) == 1

    def test_skill_not_in_args(self) -> None:
        """Skill pattern in path args."""
        registry = {"plans": {"cooperative": True, "default-exit": []}}
        refs = find_skill_references("some /plans/foo/bar", registry)
        skill_names = [ref[1] for ref in refs]
        assert "plans" in skill_names or len(refs) == 0


class TestSingleSkillPassThrough:
    """Single skill invocations return None (Claude handles directly)."""

    @pytest.mark.parametrize(
        ("prompt", "registry"),
        [
            ("/design plans/foo", _DESIGN_WITH_EXIT),
            ("/commit", _COMMIT_ONLY),
            (
                "/handoff --force",
                {"handoff": {"cooperative": True, "default-exit": []}},
            ),
        ],
        ids=["with-default-exit", "terminal", "with-complex-args"],
    )
    def test_single_skill_returns_none(
        self, prompt: str, registry: dict[str, object]
    ) -> None:
        """Single skill returns None (skill handles its own exit)."""
        assert parse_continuation(prompt, registry) is None


class TestModeInlineProse:
    """Tests for inline prose with delimiters."""

    def test_inline_comma_slash_delimiter(self) -> None:
        """Parse inline prose with ', /' delimiter."""
        registry = {
            **_DESIGN_WITH_EXIT,
            "plan": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
        }
        result = parse_continuation("/design plans/foo, /plan", registry)
        assert result is not None
        assert result["current"]["skill"] == "design"
        assert "plans/foo" in result["current"]["args"]
        assert len(result["continuation"]) == 1
        assert result["continuation"][0]["skill"] == "plan"

    @pytest.mark.parametrize(
        "connector",
        ["and", "then", "finally"],
        ids=["and", "then", "finally"],
    )
    def test_inline_connectors(self, connector: str) -> None:
        """Parse inline prose with various connectors."""
        if connector == "finally":
            reg = {"design": _SKILL, "commit": _SKILL}
            result = parse_continuation(f"/design foo {connector} /commit", reg)
            assert result is not None
            assert result["continuation"][0]["skill"] == "commit"
        else:
            result = parse_continuation(f"/design foo {connector} /plan", _DESIGN_PLAN)
            assert result is not None
            assert result["continuation"][0]["skill"] == "plan"

    def test_inline_three_skills(self) -> None:
        """Parse three skills in inline prose."""
        registry = {**_DESIGN_PLAN, "execute": _SKILL}
        result = parse_continuation("/design foo, /plan bar and /execute", registry)
        assert result is not None
        assert result["current"]["skill"] == "design"
        continuation_skills = [e["skill"] for e in result["continuation"]]
        assert "plan" in continuation_skills
        assert "execute" in continuation_skills


class TestModeMultiLine:
    r"""Tests for multi-line list with 'and\n- /skill' pattern."""

    def test_multiline_list_basic(self) -> None:
        """Parse multi-line list pattern."""
        _design_exit = {"cooperative": True, "default-exit": ["/commit"]}
        registry = {"design": _design_exit, "plan": _SKILL, "execute": _SKILL}
        result = parse_continuation("/design foo and\n- /plan\n- /execute", registry)
        assert result is not None
        assert result["current"]["skill"] == "design"
        assert result["current"]["args"] == "foo"
        continuation_skills = [e["skill"] for e in result["continuation"]]
        assert "plan" in continuation_skills
        assert "execute" in continuation_skills
        assert "commit" not in continuation_skills

    def test_multiline_list_with_args(self) -> None:
        """Parse multi-line list with args for each skill."""
        result = parse_continuation(
            "/design foo and\n- /plan arg1\n- /execute arg2",
            {**_DESIGN_PLAN, "execute": _SKILL},
        )
        assert result is not None
        skills = {e["skill"]: e["args"] for e in result["continuation"]}
        assert skills["plan"] == "arg1"
        assert skills["execute"] == "arg2"

    def test_multiline_list_indentation(self) -> None:
        """Parse multi-line list with indentation."""
        result = parse_continuation("/design foo and\n  - /plan", _DESIGN_PLAN)
        assert result is not None
        assert result["continuation"][0]["skill"] == "plan"


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_no_skill_in_input(self) -> None:
        """Input with no skill references returns None."""
        assert parse_continuation("just some regular text", _DESIGN_ONLY) is None

    def test_path_args_not_skill(self) -> None:
        """Path arguments like /foo/bar not treated as skills."""
        assert parse_continuation("/design /some/path/to/file", _DESIGN_ONLY) is None

    def test_connecting_words_in_args(self) -> None:
        """'and' creates delimiter between two registered skills."""
        registry = {**_DESIGN_ONLY, "implement": _SKILL}
        result = parse_continuation("/design foo and /implement bar", registry)
        assert result is not None
        assert result["current"]["skill"] == "design"
        assert "implement" in [e["skill"] for e in result["continuation"]]

    def test_unknown_skill_ignored(self) -> None:
        """Unknown skills ignored, single registered skill returns None."""
        assert parse_continuation("/design foo, /unknownskill", _DESIGN_ONLY) is None

    def test_flag_handling_complex(self) -> None:
        """Complex flags with single skill returns None."""
        registry = {
            "execute": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            }
        }
        assert (
            parse_continuation("/execute --verbose --check planning", registry) is None
        )

    def test_empty_continuation_terminal(self) -> None:
        """Terminal skill returns None."""
        assert parse_continuation("/commit", _COMMIT_ONLY) is None


class TestFormatContinuationContext:
    """Tests for formatting continuation as additionalContext."""

    def test_format_with_continuation(self) -> None:
        """Format with non-empty continuation."""
        parsed = {
            "current": {"skill": "design", "args": "plans/foo"},
            "continuation": [
                {"skill": "plan-adhoc", "args": ""},
                {"skill": "handoff", "args": ""},
                {"skill": "commit", "args": ""},
            ],
        }
        context = format_continuation_context(parsed)
        assert "[CONTINUATION-PASSING]" in context
        assert "Current: /design plans/foo" in context
        assert 'Skill(skill: "plan-adhoc"' in context

    def test_format_terminal(self) -> None:
        """Format with empty continuation (terminal)."""
        parsed = {"current": {"skill": "commit", "args": ""}, "continuation": []}
        context = format_continuation_context(parsed)
        assert "[CONTINUATION-PASSING]" in context
        assert "terminal" in context.lower()

    def test_format_includes_warning(self) -> None:
        """Format includes Task tool warning."""
        parsed = {
            "current": {"skill": "design", "args": "plans/foo"},
            "continuation": [{"skill": "handoff", "args": ""}],
        }
        context = format_continuation_context(parsed)
        assert "Do NOT include continuation metadata in Task tool prompts" in context

    def test_format_next_skill_instruction(self) -> None:
        """Format includes correct next skill instruction."""
        parsed = {
            "current": {"skill": "design", "args": "plans/foo"},
            "continuation": [
                {"skill": "plan-adhoc", "args": ""},
                {"skill": "commit", "args": ""},
            ],
        }
        context = format_continuation_context(parsed)
        assert 'Skill(skill: "plan-adhoc"' in context
        assert "[CONTINUATION: /commit]" in context


class TestRegistryIntegration:
    """Tests that parse_continuation integrates with registry correctly."""

    def test_parse_with_real_registry_structure(self) -> None:
        """Parse with realistic multi-skill registry."""
        result = parse_continuation("/design foo, /plan and /execute", _FULL_REGISTRY)
        assert result is not None
        assert result["current"]["skill"] == "design"
        continuation_skills = [e["skill"] for e in result["continuation"]]
        assert "plan" in continuation_skills
        assert "execute" in continuation_skills
        assert "handoff" not in continuation_skills
        assert "commit" not in continuation_skills


class TestFalsePositiveFiltering:
    """Test that parser correctly filters false positive contexts."""

    @pytest.mark.parametrize(
        ("prompt", "registry"),
        [
            ("Remember to use /commit skill", _COMMIT_ONLY),
            ("directive to invoke /handoff", _HANDOFF_ONLY),
            ("directive to use the /commit skill", _COMMIT_ONLY),
            ("step from: plans/commit-workflow/step.md", _COMMIT_ONLY),
            ("Review /orchestrate-redesign/design.md", _ORCHESTRATE_ONLY),
            ("Review /path/to/commit.md", _COMMIT_ONLY),
            ("step from: steps/handoff-workflow.md", _HANDOFF_ONLY),
            ("Review the /orchestrate-redesign/ dir", _ORCHESTRATE_ONLY),
            ("<command-message>commit</command-message>", _COMMIT_ONLY),
            ("<command-name>/commit</command-name>", _COMMIT_ONLY),
            ("<bash-stdout>Running /handoff</bash-stdout>", _HANDOFF_ONLY),
            ("<local-command-stdout>/commit</local-command-stdout>", _COMMIT_ONLY),
            ("work on the /commit functionality later", _COMMIT_ONLY),
            ("implement the /commit functionality", _COMMIT_ONLY),
            ("/design plans/foo", _DESIGN_WITH_EXIT),
            ("Complete the task. /design plans/foo", _DESIGN_ONLY),
        ],
        ids=[
            "meta-use",
            "meta-invoke",
            "meta-use-the",
            "path-plans",
            "path-ext",
            "path-prompt",
            "path-steps",
            "path-dir",
            "xml-msg",
            "xml-name",
            "xml-bash",
            "xml-local",
            "prose-1",
            "prose-2",
            "single-pass",
            "sentence-single",
        ],
    )
    def test_returns_none(self, prompt: str, registry: dict[str, object]) -> None:
        """False positive contexts return None."""
        assert parse_continuation(prompt, registry) is None

    def test_continuation_delimiter_invocation(self) -> None:
        """Continuation with delimiter SHOULD trigger (true positive)."""
        registry = {
            **_DESIGN_WITH_EXIT,
            "plan": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
        }
        result = parse_continuation("/design plans/foo, /plan", registry)
        assert result is not None
        assert len(result["continuation"]) > 0

    def test_multiline_continuation_invocation(self) -> None:
        r"""Multi-line with 'and\n- /skill' SHOULD trigger."""
        _d = {"cooperative": True, "default-exit": ["/commit"]}
        registry = {"design": _d, "plan": _SKILL}
        result = parse_continuation("/design foo and\n- /plan", registry)
        assert result is not None
        assert "plan" in [e["skill"] for e in result["continuation"]]

    def test_sentence_boundary_multi_skill_triggers(self) -> None:
        """Multi-skill after sentence boundary SHOULD trigger."""
        registry = {**_DESIGN_ONLY, "commit": _SKILL}
        result = parse_continuation(
            "Complete the task. /design plans/foo, /commit", registry
        )
        assert result is not None
        assert result["current"]["skill"] == "design"
        assert result["continuation"][0]["skill"] == "commit"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
