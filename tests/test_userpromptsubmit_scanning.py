"""Tests for directive scanning: fence detection, any-line matching, enhanced d:."""

from tests.ups_hook_helpers import call_hook, hook


class TestDirectiveCharacterization:
    """Characterization tests for each directive in isolation (FR-6)."""

    def test_d_directive_standalone(self) -> None:
        """d: directive produces discuss expansion."""
        result = call_hook("d: analyze this approach")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert (
            "DISCUSS" in additional_context
            or "Evaluate critically" in additional_context
        )
        assert "diverge" in additional_context.lower()
        assert "discuss" in result["systemMessage"].lower()

    def test_p_directive_standalone(self) -> None:
        """p: directive produces pending expansion."""
        result = call_hook("p: implement feature X")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert "PENDING" in additional_context or "Do NOT execute" in additional_context
        assert (
            "model tier" in additional_context.lower()
            or "opus" in additional_context.lower()
        )
        assert "pending" in result["systemMessage"].lower()

    def test_b_directive_standalone(self) -> None:
        """b: directive produces brainstorm expansion."""
        result = call_hook("b: approaches for caching")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert (
            "BRAINSTORM" in additional_context
            or "diverge" in additional_context.lower()
        )
        assert "brainstorm" in result["systemMessage"].lower()

    def test_q_directive_standalone(self) -> None:
        """q: directive produces quick/terse expansion."""
        result = call_hook("q: what does FR-1 mean")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert "QUICK" in additional_context or "terse" in additional_context.lower()
        assert "quick" in result["systemMessage"].lower()

    def test_learn_directive_standalone(self) -> None:
        """learn: directive produces learn expansion."""
        result = call_hook("learn: always use project-local tmp")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert "LEARN" in additional_context or "learnings.md" in additional_context
        assert "learn" in result["systemMessage"].lower()

    def test_no_match_pass_through(self) -> None:
        """Prompt with no feature match produces silent exit (empty result)."""
        assert call_hook("just a regular prompt with no shortcuts") == {}
        assert call_hook("hello world") == {}


class TestLongFormAliases:
    """Test long-form directive aliases."""

    def test_long_form_aliases(self) -> None:
        """Test that discuss: and pending: produce same output as d: and p:."""
        # Test discuss: vs d:
        output_discuss = call_hook("discuss: some topic")
        output_d = call_hook("d: some topic")

        # Both should have same additionalContext
        assert "hookSpecificOutput" in output_discuss
        assert "hookSpecificOutput" in output_d
        assert (
            output_discuss["hookSpecificOutput"]["additionalContext"]
            == output_d["hookSpecificOutput"]["additionalContext"]
        )

        # Both should have same systemMessage
        assert output_discuss["systemMessage"] == output_d["systemMessage"]

        # Test pending: vs p:
        output_pending = call_hook("pending: new task")
        output_p = call_hook("p: new task")

        # Both should have same additionalContext
        assert "hookSpecificOutput" in output_pending
        assert "hookSpecificOutput" in output_p
        assert (
            output_pending["hookSpecificOutput"]["additionalContext"]
            == output_p["hookSpecificOutput"]["additionalContext"]
        )

        # Both should have same systemMessage
        assert output_pending["systemMessage"] == output_p["systemMessage"]


class TestEnhancedDDirective:
    """Test enhanced d: directive with counterfactual evaluation structure."""

    def test_enhanced_d_injection(self) -> None:
        """Test that d: includes counterfactual evaluation framework."""
        output = call_hook("d: should we use approach X?")

        # Verify output structure
        assert "hookSpecificOutput" in output
        assert "systemMessage" in output

        additional_context = output["hookSpecificOutput"]["additionalContext"]
        system_message = output["systemMessage"]

        # additionalContext includes verdict-first evaluation structure
        assert "assess" in additional_context.lower() or (
            "verdict" in additional_context.lower()
        )
        assert "diverge" in additional_context.lower()
        assert "agree" in additional_context.lower() or (
            "disagree" in additional_context.lower()
        )

        # additionalContext preserves "do not execute" instruction
        assert "do not execute" in additional_context.lower()

        # systemMessage stays concise (no full evaluation framework)
        assert "discuss" in system_message.lower()
        assert "do not execute" not in system_message.lower()
        # systemMessage should NOT have full evaluation framework
        assert len(system_message) < 200


class TestFencedBlockExclusion:
    """Test fenced code block detection for directive scanning."""

    def test_fenced_block_exclusion(self) -> None:
        """Test that lines inside fenced blocks are marked as fenced."""
        # Test backtick fences
        backtick_text = """```
d: inside backticks
```
d: outside fence"""

        # Test tilde fences
        tilde_text = """~~~
p: inside tildes
~~~
p: outside fence"""

        # Test mixed valid fences (both types)
        mixed_text = """```python
d: inside first fence
```
p: between fences
~~~
d: inside second fence
~~~
d: after all fences"""

        # Call the fence detection function (should not exist yet, causing RED)
        lines_backtick = backtick_text.split("\n")
        fenced_backtick = [
            hook.is_line_in_fence(lines_backtick, i) for i in range(len(lines_backtick))
        ]

        # Lines 0-2 should be in/part of fence, line 3 should not
        assert fenced_backtick[0] is True  # opening fence
        assert fenced_backtick[1] is True  # inside fence
        assert fenced_backtick[2] is True  # closing fence
        assert fenced_backtick[3] is False  # outside fence

        # Test tildes
        lines_tilde = tilde_text.split("\n")
        fenced_tilde = [
            hook.is_line_in_fence(lines_tilde, i) for i in range(len(lines_tilde))
        ]

        assert fenced_tilde[0] is True  # opening fence
        assert fenced_tilde[1] is True  # inside fence
        assert fenced_tilde[2] is True  # closing fence
        assert fenced_tilde[3] is False  # outside fence

        # Test mixed (complex scenario)
        lines_mixed = mixed_text.split("\n")
        fenced_mixed = [
            hook.is_line_in_fence(lines_mixed, i) for i in range(len(lines_mixed))
        ]

        # First fence: lines 0-2
        assert fenced_mixed[0] is True
        assert fenced_mixed[1] is True
        assert fenced_mixed[2] is True
        # Between fences: line 3
        assert fenced_mixed[3] is False
        # Second fence: lines 4-6
        assert fenced_mixed[4] is True
        assert fenced_mixed[5] is True
        assert fenced_mixed[6] is True
        # After all fences: line 7
        assert fenced_mixed[7] is False


class TestAnyLineMatching:
    """Test any-line directive matching with fenced block exclusion."""

    def test_any_line_matching(self) -> None:
        """Test that directives are found on any line (not just line 1)."""
        # Directive on line 2 (not line 1)
        output_line2 = call_hook("some text before\nd: directive on line 2")
        assert "hookSpecificOutput" in output_line2
        assert "discuss" in output_line2["systemMessage"].lower()

        # Directive on line 3
        output_line3 = call_hook("line 1\nline 2\np: directive on line 3")
        assert "hookSpecificOutput" in output_line3
        assert "pending" in output_line3["systemMessage"].lower()

        # Directive inside fenced block returns None (excluded by fence detection)
        fenced_prompt = """some text
```
d: inside fence
```
p: outside fence"""
        output_fenced = call_hook(fenced_prompt)
        # Should match the p: directive outside fence, not the d: inside
        assert "hookSpecificOutput" in output_fenced
        assert "pending" in output_fenced["systemMessage"].lower()

        # All non-fenced directives fire (additive, D-7)
        multi_prompt = """d: first directive
p: second directive"""
        output_multi = call_hook(multi_prompt)
        assert "hookSpecificOutput" in output_multi
        assert "discuss" in output_multi["systemMessage"].lower()
        assert "pending" in output_multi["systemMessage"].lower()


class TestAdditiveDirectives:
    """Test additive directive scanning: all directives fire (D-7)."""

    def test_multiple_directives_both_fire(self) -> None:
        """All directives in prompt fire, not just the first match."""
        result = call_hook("d: discuss this\np: new task")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        # DISCUSS expansion must appear
        assert (
            "Evaluate critically" in additional_context
            or "DISCUSS" in additional_context
        )
        # PENDING expansion must also appear
        assert "Do NOT execute" in additional_context or "PENDING" in additional_context

    def test_directive_section_scoping(self) -> None:
        """Section spans from directive line to next directive or end."""
        result = call_hook(
            "d: discuss this topic\nsome discussion content\np: new task name"
        )
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert (
            "Evaluate critically" in additional_context
            or "DISCUSS" in additional_context
        )
        assert "Do NOT execute" in additional_context or "PENDING" in additional_context

    def test_single_directive_still_works(self) -> None:
        """Single directive behavior is unchanged by additive refactor."""
        result = call_hook("d: some topic")
        assert result != {}
        assert (
            "Evaluate critically" in result["hookSpecificOutput"]["additionalContext"]
        )
        assert "discuss" in result["systemMessage"].lower()
