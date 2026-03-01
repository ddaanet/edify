"""Tests for userpromptsubmit-shortcuts hook."""

from unittest.mock import patch

from tests.ups_hook_helpers import call_hook, hook


class TestTier1Commands:
    """Test Tier 1 command matching on any prompt line."""

    def test_multiline_command_no_systemmessage(self) -> None:
        """Command + plain text, no other feature (FR-2).

        Multi-line command produces additionalContext only, no systemMessage.
        """
        result = call_hook("s\nsome additional context")
        assert result != {}
        assert "[#status]" in result["hookSpecificOutput"]["additionalContext"]
        assert (
            "[#execute]"
            in call_hook("x\ndo the next thing")["hookSpecificOutput"][
                "additionalContext"
            ]
        )
        # Multi-line: additionalContext only, no systemMessage
        assert "systemMessage" not in call_hook("s\nsome additional context")

    def test_tier1_shortcut_exact_match_unchanged(self) -> None:
        """Single-line match produces systemMessage + additionalContext."""
        result_s = call_hook("s")
        assert "[#status]" in result_s["systemMessage"]
        assert "[#execute]" in call_hook("x")["systemMessage"]
        assert "[#status]" in result_s["hookSpecificOutput"]["additionalContext"]

    def test_r_expansion_graduated_lookup(self) -> None:
        """R expansion includes graduated lookup steps."""
        result = call_hook("r")
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert "conversation context" in additional_context
        assert "session.md" in additional_context
        assert "Error if no in-progress" not in additional_context

    def test_xc_hc_bracket_compression(self) -> None:
        """Xc and hc use bracket style."""
        assert call_hook("xc")["systemMessage"].startswith("[execute, commit]")
        assert call_hook("hc")["systemMessage"].startswith("[handoff, commit]")
        assert "[#execute --commit]" not in call_hook("xc")["systemMessage"]
        assert "[/handoff --commit]" not in call_hook("hc")["systemMessage"]

    def test_tier1_no_false_positive_embedded(self) -> None:
        """Shortcuts embedded in words or with trailing text do not trigger."""
        assert call_hook("this is about status") == {}
        assert call_hook("fix something") == {}
        assert call_hook("  s  trailing space") == {}

    def test_command_cofires_with_directive(self) -> None:
        """Command on one line + directive on another → both fire."""
        result = call_hook("s\nd: discuss this topic")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        # Command expansion must be present
        assert "[#status]" in additional_context
        # Directive expansion must also be present
        assert (
            "DISCUSS" in additional_context
            or "Evaluate critically" in additional_context
        )
        # systemMessage should include directive summary (not command multiline)
        assert "discuss" in result["systemMessage"].lower()

    def test_h_expansion(self) -> None:
        """H command expands to handoff instruction."""
        result = call_hook("h")
        assert "[/handoff]" in result["systemMessage"]
        assert "Update session.md" in result["systemMessage"]

    def test_ci_expansion(self) -> None:
        """CI command expands to commit instruction."""
        result = call_hook("ci")
        assert "[/commit]" in result["systemMessage"]
        assert "status display" in result["systemMessage"]

    def test_c_expansion(self) -> None:
        """C command expands to continue instruction."""
        result = call_hook("c")
        assert "Continue." in result["systemMessage"]

    def test_y_expansion(self) -> None:
        """Y command expands to proceed instruction."""
        result = call_hook("y")
        assert "Yes, proceed." in result["systemMessage"]

    def test_question_expansion(self) -> None:
        """? command expands to help instruction."""
        result = call_hook("?")
        assert "[#help]" in result["systemMessage"]
        assert "shortcuts" in result["systemMessage"].lower()
        assert "skills" in result["systemMessage"].lower()

    def test_multi_command_first_wins(self) -> None:
        """Multiple commands → only first fires, warning in systemMessage."""
        result = call_hook("s\nx")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        # First command (s) fires
        assert "[#status]" in additional_context
        # Second command (x) does NOT fire
        assert "[#execute]" not in additional_context
        # Warning in systemMessage
        assert "s" in result["systemMessage"]
        assert "x" in result["systemMessage"]

    def test_multi_command_reverse_order(self) -> None:
        """Verify first-wins is position-based, not alphabetical."""
        result = call_hook("x\ns")
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert "[#execute]" in additional_context
        assert "[#status]" not in additional_context

    def test_single_command_no_warning(self) -> None:
        """Single command produces no multi-command warning."""
        result = call_hook("s")
        sys_msg = result["systemMessage"]
        # systemMessage should contain expansion, not a warning about multiple commands
        assert "Multiple" not in sys_msg


class TestPatternGuards:
    """Test Tier 2.5 pattern guards."""

    def test_skill_editing_guard_verb_noun(self) -> None:
        """Editing verb + skill/agent noun triggers skill-editing reminder."""
        result = call_hook("fix the commit skill")
        assert result != {}
        assert (
            "plugin-dev:skill-development"
            in result["hookSpecificOutput"]["additionalContext"]
        )
        assert "systemMessage" in result

    def test_skill_editing_guard_slash_pattern(self) -> None:
        """Slash-prefixed skill name with editing verb triggers reminder."""
        result1 = call_hook("update /design description")
        assert (
            "plugin-dev:skill-development"
            in result1["hookSpecificOutput"]["additionalContext"]
        )
        result2 = call_hook("improve /commit skill")
        assert (
            "plugin-dev:skill-development"
            in result2["hookSpecificOutput"]["additionalContext"]
        )

    def test_ccg_guard_hooks_keyword(self) -> None:
        """Platform keyword 'hooks' triggers CCG reminder."""
        result = call_hook("how do hooks work")
        assert result != {}
        assert "claude-code-guide" in result["hookSpecificOutput"]["additionalContext"]
        assert "systemMessage" in result

    def test_ccg_guard_platform_keywords(self) -> None:
        """Various platform capability keywords trigger CCG reminder."""
        assert (
            "claude-code-guide"
            in call_hook("configure a PreToolUse hook")["hookSpecificOutput"][
                "additionalContext"
            ]
        )
        assert (
            "claude-code-guide"
            in call_hook("set up MCP server")["hookSpecificOutput"]["additionalContext"]
        )
        assert (
            "claude-code-guide"
            in call_hook("add a slash command")["hookSpecificOutput"][
                "additionalContext"
            ]
        )

    def test_pattern_guard_no_false_positives(self) -> None:
        """Non-matching prompts don't trigger guards."""
        assert call_hook("fix the bug in parsing") == {}
        assert call_hook("the skill level is high") == {}

    def test_guard_additive_with_directive(self) -> None:
        """Guard fires additively alongside directive output."""
        result = call_hook("d: how do hooks work")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        # DISCUSS directive must fire
        assert (
            "DISCUSS" in additional_context
            or "Evaluate critically" in additional_context
        )
        # CCG guard must also fire
        assert "claude-code-guide" in additional_context

    def test_guard_combines_with_continuation(self) -> None:
        """Pattern guard output combines with Tier 3 continuation."""
        fake_registry = {
            "handoff": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }
        with patch.object(hook, "build_registry", return_value=fake_registry):
            result = call_hook("fix the skill /handoff and /commit")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        # Tier 2.5: skill-editing guard must fire
        assert "plugin-dev:skill-development" in additional_context
        # Tier 3: continuation must also fire
        assert "CONTINUATION" in additional_context


class TestIntegration:
    """Integration tests verifying all enhancements work together."""

    def test_integration_e2e(self) -> None:
        """Test full hook execution with combined scenarios."""
        # Scenario 1: discuss: on line 3 inside triple-backtick fence
        # → no match (excluded)
        prompt_fenced = """line 1
line 2
```
discuss: inside fence should be excluded
```
line 6 after fence"""
        output_fenced = call_hook(prompt_fenced)
        # Should return empty (no directive matched outside fence)
        assert output_fenced == {}

        # Scenario 2: discuss: on line 5 after fence closes
        # → match with enhanced injection
        prompt_after_fence = """line 1
line 2
```
code block
```
discuss: after fence should match"""
        output_after_fence = call_hook(prompt_after_fence)
        assert "hookSpecificOutput" in output_after_fence
        assert "discuss" in output_after_fence["systemMessage"].lower()
        # Verify enhanced content includes counterfactual structure
        additional_context = output_after_fence["hookSpecificOutput"][
            "additionalContext"
        ]
        assert "stress-test" in additional_context.lower()
        assert "verdict" in additional_context.lower() or (
            "agree" in additional_context.lower()
        )

        # Scenario 3: Tier 1 command s → exact match output unchanged from baseline
        output_s = call_hook("s")
        # Tier 1 commands should have both hookSpecificOutput and systemMessage
        assert "hookSpecificOutput" in output_s
        assert "systemMessage" in output_s
        # Both should contain the expansion text
        assert "[#status]" in output_s["systemMessage"]
        assert "[#status]" in output_s["hookSpecificOutput"]["additionalContext"]

        # Scenario 4: Tier 1 command x → exact match unchanged
        output_x = call_hook("x")
        assert "hookSpecificOutput" in output_x
        assert "systemMessage" in output_x
        assert "[#execute]" in output_x["systemMessage"]
        assert "[#execute]" in output_x["hookSpecificOutput"]["additionalContext"]


class TestContinuationOnly:
    """Test Tier 3 continuation parsing with no guards matching."""

    def test_continuation_with_cooperative_skills(self) -> None:
        """Continuation parsing detects multi-skill chains without guards."""
        fake_registry = {
            "handoff": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }
        with patch.object(hook, "build_registry", return_value=fake_registry):
            result = call_hook("/handoff and /commit")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert "CONTINUATION" in additional_context
        assert "Current:" in additional_context
        assert "handoff" in additional_context
        assert "commit" in additional_context


class TestDirectiveWithContinuation:
    """Test directive + continuation co-firing (Cycle 4: FR-4)."""

    def test_directive_cofires_with_continuation(self) -> None:
        """Directive + continuation co-fire as expected.

        Both directive and continuation outputs are present in hook result.
        Verifies that Cycle 2 refactor removed the early-return block.
        """
        fake_registry = {
            "handoff": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }
        with patch.object(hook, "build_registry", return_value=fake_registry):
            result = call_hook("p: new task\n/handoff and /commit")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        # Directive expansion must be present
        assert "PENDING" in additional_context or "Do NOT execute" in additional_context
        # Continuation must also be present
        assert "CONTINUATION" in additional_context
        # systemMessage should include directive summary
        assert "pending" in result["systemMessage"].lower()


class TestFeatureCombinations:
    """Test pairwise and triple feature combinations (FR-7)."""

    def test_command_plus_pattern_guard(self) -> None:
        """Command on one line + CCG pattern keyword → both fire."""
        result = call_hook("s\nhow do hooks work")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert "[#status]" in additional_context
        assert "claude-code-guide" in additional_context
        # systemMessage: multi-line command adds nothing, CCG guard adds summary
        assert "systemMessage" in result
        assert "claude-code-guide" in result["systemMessage"].lower()

    def test_command_plus_continuation(self) -> None:
        """Command on one line + continuation chain → both fire."""
        fake_registry = {
            "handoff": {"cooperative": True, "default-exit": []},
            "commit": {"cooperative": True, "default-exit": []},
        }
        with patch.object(hook, "build_registry", return_value=fake_registry):
            result = call_hook("s\n/handoff and /commit")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        assert "[#status]" in additional_context
        assert "CONTINUATION" in additional_context
        # systemMessage: multi-line command and continuation both add nothing
        assert "systemMessage" not in result

    def test_command_plus_directive_plus_guard(self) -> None:
        """Command + directive + pattern guard triple → all three fire."""
        result = call_hook("s\nd: how do hooks work")
        assert result != {}
        additional_context = result["hookSpecificOutput"]["additionalContext"]
        # Command
        assert "[#status]" in additional_context
        # Directive
        assert (
            "DISCUSS" in additional_context
            or "Evaluate critically" in additional_context
        )
        # CCG guard (triggered by "hooks" keyword)
        assert "claude-code-guide" in additional_context
        # systemMessage should include directive and guard summaries
        sys_msg = result["systemMessage"]
        assert "discuss" in sys_msg.lower()
        assert "claude-code-guide" in sys_msg.lower()
