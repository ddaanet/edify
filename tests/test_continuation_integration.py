"""Integration tests for continuation passing 2-skill chain.

Tests the full flow:
1. Hook parses multi-skill input → emits additionalContext
2. First skill reads additionalContext → tail-calls next skill with [CONTINUATION: ...]
3. Second skill reads args suffix → tail-calls remaining skill(s)
4. Verify chain completes correctly

Based on design Component 4 integration test requirements.
"""

import importlib.util
import re
from pathlib import Path

import pytest

# Import the hook script as a module
hook_script_path = (
    Path(__file__).parent.parent
    / "plugin"
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
format_continuation_context = hook_module.format_continuation_context


class TestTwoSkillChain:
    """Integration tests for 2-skill continuation chains."""

    def test_design_plan_chain(self) -> None:
        """Test /design, /plan-adhoc chain (user-specified, no default-exit)."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "plan_adhoc": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "handoff": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }

        # Step 1: Hook parses user input
        user_input = "/design plans/foo, /plan_adhoc"
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed["current"]["skill"] == "design"
        assert "plans/foo" in parsed["current"]["args"]

        # Continuation: user-specified only (no default-exit appending)
        assert len(parsed["continuation"]) == 1
        assert parsed["continuation"][0]["skill"] == "plan_adhoc"

        # Step 2: Format additionalContext for first skill (design)
        context = format_continuation_context(parsed)

        assert "[CONTINUATION-PASSING]" in context
        assert "Current: /design plans/foo" in context
        assert 'Skill(skill: "plan_adhoc"' in context
        assert "Do NOT include continuation metadata in Task tool prompts" in context

    def test_handoff_commit_chain(self) -> None:
        """Test /handoff, /commit chain (explicit multi-skill)."""
        registry = {
            "handoff": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }

        # Single skill returns None — skill handles own default-exit
        single_input = "/handoff"
        assert parse_continuation(single_input, registry) is None

        # Explicit multi-skill chain triggers continuation parsing
        user_input = "/handoff, /commit"
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed["current"]["skill"] == "handoff"
        assert len(parsed["continuation"]) == 1
        assert parsed["continuation"][0]["skill"] == "commit"

        # Format additionalContext
        context = format_continuation_context(parsed)
        assert "[CONTINUATION-PASSING]" in context
        assert 'Skill(skill: "commit"' in context

    def test_three_skill_chain(self) -> None:
        """Test 3-skill chain: /design, /plan, /orchestrate."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "plan": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "orchestrate": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "handoff": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }

        # Step 1: Hook parses 3-skill input
        user_input = "/design foo, /plan bar and /orchestrate"
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed["current"]["skill"] == "design"

        # Continuation: user-specified only (no default-exit)
        continuation_skills = [e["skill"] for e in parsed["continuation"]]
        assert "plan" in continuation_skills
        assert "orchestrate" in continuation_skills
        assert "handoff" not in continuation_skills  # no default-exit
        assert "commit" not in continuation_skills  # no default-exit

        # Step 2: First skill tail-calls second
        context = format_continuation_context(parsed)
        assert 'Skill(skill: "plan"' in context

        # Last skill (orchestrate) uses its own default-exit when continuation empty

    def test_multiline_chain(self) -> None:
        """Test multi-line continuation format."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "plan": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "orchestrate": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "handoff": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }

        # Step 1: Parse multi-line format
        user_input = "/design foo and\n- /plan bar\n- /orchestrate baz"
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed["current"]["skill"] == "design"
        assert parsed["current"]["args"] == "foo"

        # Continuation: user-specified only with args preserved
        continuation_map = {e["skill"]: e["args"] for e in parsed["continuation"]}
        assert "plan" in continuation_map
        assert continuation_map["plan"] == "bar"
        assert "orchestrate" in continuation_map
        assert continuation_map["orchestrate"] == "baz"

        # No default-exit appending
        assert "handoff" not in continuation_map
        assert "commit" not in continuation_map

    def test_handoff_terminal_in_chain(self) -> None:
        """Test /design, /handoff stops chain (handoff is terminal)."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "handoff": {"cooperative": True, "default-exit": []},
        }

        # Step 1: Parse chain ending with /handoff (terminal skill)
        user_input = "/design foo, /handoff"
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed["current"]["skill"] == "design"

        # Continuation: handoff only — no commit appended
        continuation_skills = [e["skill"] for e in parsed["continuation"]]
        assert "handoff" in continuation_skills

        # Handoff has empty args (no flags)
        handoff_entry = next(
            (e for e in parsed["continuation"] if e["skill"] == "handoff"), None
        )
        assert handoff_entry is not None
        assert handoff_entry["args"] == ""

        # Commit is NOT in continuation — user explicitly chose /handoff only
        assert "commit" not in continuation_skills


class TestContinuationExtraction:
    """Tests for extracting continuation from Skill args."""

    def test_extract_continuation_from_args(self) -> None:
        """Test extracting [CONTINUATION: ...] from args string."""
        args = "some regular args [CONTINUATION: /handoff, /commit]"

        # Extract continuation
        cont_match = re.search(r"\[CONTINUATION:\s*(.+?)\]", args)
        assert cont_match is not None

        cont_str = cont_match.group(1)
        assert "/handoff" in cont_str
        assert "/commit" in cont_str

        # Extract regular args (before continuation)
        regular_args = args[: cont_match.start()].strip()
        assert regular_args == "some regular args"

    def test_extract_empty_continuation(self) -> None:
        """Test extracting empty continuation."""
        args = "[CONTINUATION: ]"

        cont_match = re.search(r"\[CONTINUATION:\s*(.+?)?\]", args)
        assert cont_match is not None

        cont_str = cont_match.group(1)
        # Empty continuation
        assert not cont_str or cont_str.strip() == ""

    def test_no_continuation_in_args(self) -> None:
        """Test args without continuation marker."""
        args = "just regular args here"

        cont_match = re.search(r"\[CONTINUATION:\s*(.+?)\]", args)
        assert cont_match is None


class TestChainCompletion:
    """Tests for chain completion scenarios."""

    def test_chain_reaches_terminal(self) -> None:
        """Verify chain properly reaches terminal skill."""
        registry = {
            "design": {"cooperative": True, "default-exit": ["/commit"]},
            "commit": {"cooperative": True, "default-exit": []},
        }

        # Single skill returns None — skill manages own default-exit
        assert parse_continuation("/design foo", registry) is None

        # Explicit chain: design → commit
        user_input = "/design foo, /commit"
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed["continuation"][0]["skill"] == "commit"

        # Verify terminal formatting
        commit_parsed = {"current": {"skill": "commit", "args": ""}, "continuation": []}
        context = format_continuation_context(commit_parsed)
        assert "terminal" in context.lower()
        assert "do not tail-call" in context.lower()

    def test_chain_with_args_preserved(self) -> None:
        """Verify skill args are preserved through chain."""
        registry = {
            "design": {
                "cooperative": True,
                "default-exit": ["/handoff", "/commit"],
            },
            "handoff": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }

        # Explicit chain with args
        user_input = "/design some-file-path.md, /handoff"
        parsed = parse_continuation(user_input, registry)

        assert parsed is not None
        assert parsed["current"]["skill"] == "design"
        assert "some-file-path.md" in parsed["current"]["args"]

        # Format context
        context = format_continuation_context(parsed)
        assert "Current: /design some-file-path.md" in context


class TestContinuationPrepend:
    """Tests for subroutine call pattern (prepend to continuation)."""

    def test_prepend_preserves_original_chain(self) -> None:
        """Prepending entries keeps original chain as immutable suffix."""
        # Simulate: skill has [/handoff, /commit]
        # Needs /commit checkpoint first → prepend /commit
        original = ["/handoff", "/commit"]
        prepended = ["/commit", *original]

        assert prepended == ["/commit", "/handoff", "/commit"]
        # Original chain unchanged as suffix
        assert prepended[1:] == original

    def test_prepend_consume_resumes_chain(self) -> None:
        """After consuming prepended entry, remainder is the original chain."""
        original = ["/handoff", "/commit"]
        prepended = ["/commit", *original]

        # Consume first (the prepended subroutine)
        consumed = prepended[0]
        remainder = prepended[1:]

        assert consumed == "/commit"
        assert remainder == ["/handoff", "/commit"]

    def test_multiple_prepends_consumed_in_order(self) -> None:
        """Multiple prepended entries are consumed in prepend order."""
        original = ["/handoff", "/commit"]
        # Skill needs /review then /commit before chain resumes
        prepended = ["/review", "/commit", *original]

        assert prepended == ["/review", "/commit", "/handoff", "/commit"]

        # Consume first: /review
        first = prepended[0]
        after_first = prepended[1:]
        assert first == "/review"
        assert after_first == ["/commit", "/handoff", "/commit"]

        # Consume second: /commit (the checkpoint)
        second = after_first[0]
        after_second = after_first[1:]
        assert second == "/commit"
        assert after_second == ["/handoff", "/commit"]
        # Original chain intact
        assert after_second == original

    def test_prepend_with_args_in_transport_format(self) -> None:
        """Prepend works correctly when parsed from transport format."""
        args = "myplan [CONTINUATION: /handoff, /commit]"

        cont_match = re.search(r"\[CONTINUATION:\s*(.+?)\]", args)
        assert cont_match is not None

        cont_str = cont_match.group(1)
        entries = [e.strip() for e in cont_str.split(",")]
        assert entries == ["/handoff", "/commit"]

        prepended = ["/commit", *entries]

        new_cont = ", ".join(prepended)
        assert new_cont == "/commit, /handoff, /commit"

        first = prepended[0]
        remainder = prepended[1:]
        remainder_str = ", ".join(remainder)
        assert first == "/commit"
        assert remainder_str == "/handoff, /commit"

    def test_no_prepend_skips_step(self) -> None:
        """Skills that don't prepend behave identically to original protocol."""
        entries = ["/handoff", "/commit"]

        # No prepend — consume directly (step 2 skipped)
        first = entries[0]
        remainder = entries[1:]

        assert first == "/handoff"
        assert remainder == ["/commit"]

    def test_prepend_empty_continuation_creates_chain(self) -> None:
        """Prepending to empty continuation creates a new chain."""
        original: list[str] = []
        prepended = ["/commit", *original]

        assert prepended == ["/commit"]
        first = prepended[0]
        remainder = prepended[1:]
        assert first == "/commit"
        assert remainder == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
