"""Tests for userpromptsubmit-shortcuts hook."""

import importlib.util
import json
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

# Import hook module using importlib (filename contains hyphen)
HOOK_PATH = (
    Path(__file__).parent.parent
    / "agent-core"
    / "hooks"
    / "userpromptsubmit-shortcuts.py"
)
spec = importlib.util.spec_from_file_location("hook_module", HOOK_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Failed to load hook module from {HOOK_PATH}")
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def call_hook(prompt: str) -> dict[str, Any]:
    """Call hook with prompt, return parsed output or empty dict if exit 0."""
    hook_input = {"prompt": prompt}
    input_data = json.dumps(hook_input)

    # Capture stdout and stderr
    captured_stdout = StringIO()
    captured_stderr = StringIO()

    with (
        patch("sys.stdin", StringIO(input_data)),
        patch("sys.stdout", captured_stdout),
        patch("sys.stderr", captured_stderr),
    ):
        try:
            hook.main()
        except SystemExit as e:
            if e.code == 0:
                # Silent pass-through
                return {}
            raise

    # Parse output
    output_str = captured_stdout.getvalue()
    if not output_str:
        return {}

    result = json.loads(output_str)
    if not isinstance(result, dict):
        return {}
    return result


class TestTier1Commands:
    """Test Tier 1 command matching on any prompt line."""

    def test_tier1_shortcut_on_own_line_in_multiline_prompt(self) -> None:
        """Shortcut on own line in multi-line prompt triggers expansion."""
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
        assert "systemMessage" not in result

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
        assert "systemMessage" not in result

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
        assert "[DISCUSS]" in output_after_fence["systemMessage"]
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
