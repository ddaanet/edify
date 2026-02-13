"""Tests for userpromptsubmit-shortcuts hook."""

import importlib.util
import json
from io import StringIO
from pathlib import Path

import pytest


# Import hook module using importlib (filename contains hyphen)
HOOK_PATH = Path(__file__).parent.parent / "agent-core" / "hooks" / "userpromptsubmit-shortcuts.py"
spec = importlib.util.spec_from_file_location("hook_module", HOOK_PATH)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def call_hook(prompt: str) -> dict:
    """Call hook with prompt, return parsed output or empty dict if exit 0."""
    import sys
    from unittest.mock import patch

    hook_input = {"prompt": prompt}
    input_data = json.dumps(hook_input)

    # Capture stdout and stderr
    captured_stdout = StringIO()
    captured_stderr = StringIO()

    with patch("sys.stdin", StringIO(input_data)):
        with patch("sys.stdout", captured_stdout):
            with patch("sys.stderr", captured_stderr):
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

    return json.loads(output_str)


class TestLongFormAliases:
    """Test long-form directive aliases."""

    def test_long_form_aliases(self):
        """Test that discuss: and pending: produce same output as d: and p:."""
        # Test discuss: vs d:
        output_discuss = call_hook("discuss: some topic")
        output_d = call_hook("d: some topic")

        # Both should have same additionalContext
        assert "hookSpecificOutput" in output_discuss
        assert "hookSpecificOutput" in output_d
        assert output_discuss["hookSpecificOutput"]["additionalContext"] == output_d["hookSpecificOutput"]["additionalContext"]

        # Both should have same systemMessage
        assert output_discuss["systemMessage"] == output_d["systemMessage"]

        # Test pending: vs p:
        output_pending = call_hook("pending: new task")
        output_p = call_hook("p: new task")

        # Both should have same additionalContext
        assert "hookSpecificOutput" in output_pending
        assert "hookSpecificOutput" in output_p
        assert output_pending["hookSpecificOutput"]["additionalContext"] == output_p["hookSpecificOutput"]["additionalContext"]

        # Both should have same systemMessage
        assert output_pending["systemMessage"] == output_p["systemMessage"]


class TestEnhancedDDirective:
    """Test enhanced d: directive with counterfactual evaluation structure."""

    def test_enhanced_d_injection(self):
        """Test that d: includes counterfactual evaluation framework."""
        output = call_hook("d: should we use approach X?")

        # Verify output structure
        assert "hookSpecificOutput" in output
        assert "systemMessage" in output

        additional_context = output["hookSpecificOutput"]["additionalContext"]
        system_message = output["systemMessage"]

        # additionalContext includes all counterfactual structure elements
        assert "identify assumptions" in additional_context.lower()
        assert "articulate failure conditions" in additional_context.lower() or "failure" in additional_context.lower()
        assert "name alternatives" in additional_context.lower() or "alternatives" in additional_context.lower()
        assert "confidence level" in additional_context.lower() or "confidence" in additional_context.lower()

        # additionalContext preserves "do not execute" instruction
        assert "do not execute" in additional_context.lower()

        # systemMessage stays concise (no full evaluation framework in user-visible message)
        assert "[DIRECTIVE: DISCUSS]" in system_message
        assert "do not execute" in system_message.lower()
        # systemMessage should NOT have the full evaluation framework (keep it under 150 chars)
        assert len(system_message) < 200


class TestFencedBlockExclusion:
    """Test fenced code block detection for directive scanning."""

    def test_fenced_block_exclusion(self):
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
        lines_backtick = backtick_text.split('\n')
        fenced_backtick = [hook.is_line_in_fence(lines_backtick, i) for i in range(len(lines_backtick))]

        # Lines 0-2 should be in/part of fence, line 3 should not
        assert fenced_backtick[0] is True  # opening fence
        assert fenced_backtick[1] is True  # inside fence
        assert fenced_backtick[2] is True  # closing fence
        assert fenced_backtick[3] is False  # outside fence

        # Test tildes
        lines_tilde = tilde_text.split('\n')
        fenced_tilde = [hook.is_line_in_fence(lines_tilde, i) for i in range(len(lines_tilde))]

        assert fenced_tilde[0] is True  # opening fence
        assert fenced_tilde[1] is True  # inside fence
        assert fenced_tilde[2] is True  # closing fence
        assert fenced_tilde[3] is False  # outside fence

        # Test mixed (complex scenario)
        lines_mixed = mixed_text.split('\n')
        fenced_mixed = [hook.is_line_in_fence(lines_mixed, i) for i in range(len(lines_mixed))]

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

    def test_any_line_matching(self):
        """Test that directives are found on any line (not just line 1)."""
        # Directive on line 2 (not line 1)
        output_line2 = call_hook("some text before\nd: directive on line 2")
        assert "hookSpecificOutput" in output_line2
        assert "[DIRECTIVE: DISCUSS]" in output_line2["systemMessage"]

        # Directive on line 3
        output_line3 = call_hook("line 1\nline 2\np: directive on line 3")
        assert "hookSpecificOutput" in output_line3
        assert "[DIRECTIVE: PENDING]" in output_line3["systemMessage"]

        # Directive inside fenced block returns None (excluded by fence detection)
        fenced_prompt = """some text
```
d: inside fence
```
p: outside fence"""
        output_fenced = call_hook(fenced_prompt)
        # Should match the p: directive outside fence, not the d: inside
        assert "hookSpecificOutput" in output_fenced
        assert "[DIRECTIVE: PENDING]" in output_fenced["systemMessage"]

        # First non-fenced directive match is returned (not all matches)
        multi_prompt = """d: first directive
p: second directive"""
        output_multi = call_hook(multi_prompt)
        # Should return first match (d:), not second
        assert "hookSpecificOutput" in output_multi
        assert "[DIRECTIVE: DISCUSS]" in output_multi["systemMessage"]


class TestIntegration:
    """Integration tests verifying all enhancements work together."""

    def test_integration_e2e(self):
        """Test full hook execution with combined scenarios."""
        # Scenario 1: discuss: on line 3 inside triple-backtick fence → no match (excluded)
        prompt_fenced = """line 1
line 2
```
discuss: inside fence should be excluded
```
line 6 after fence"""
        output_fenced = call_hook(prompt_fenced)
        # Should return empty (no directive matched outside fence)
        assert output_fenced == {}

        # Scenario 2: discuss: on line 5 after fence closes → match with enhanced injection
        prompt_after_fence = """line 1
line 2
```
code block
```
discuss: after fence should match"""
        output_after_fence = call_hook(prompt_after_fence)
        assert "hookSpecificOutput" in output_after_fence
        assert "[DIRECTIVE: DISCUSS]" in output_after_fence["systemMessage"]
        # Verify enhanced content includes counterfactual structure
        additional_context = output_after_fence["hookSpecificOutput"]["additionalContext"]
        assert "identify assumptions" in additional_context.lower()
        assert "confidence" in additional_context.lower()

        # Scenario 3: Tier 1 command s → exact match output unchanged from baseline
        output_s = call_hook("s")
        # Tier 1 commands should have both hookSpecificOutput and systemMessage
        assert "hookSpecificOutput" in output_s
        assert "systemMessage" in output_s
        # Both should contain the expansion text
        assert "[SHORTCUT: #status]" in output_s["systemMessage"]
        assert "[SHORTCUT: #status]" in output_s["hookSpecificOutput"]["additionalContext"]

        # Scenario 4: Tier 1 command x → exact match unchanged
        output_x = call_hook("x")
        assert "hookSpecificOutput" in output_x
        assert "systemMessage" in output_x
        assert "[SHORTCUT: #execute]" in output_x["systemMessage"]
        assert "[SHORTCUT: #execute]" in output_x["hookSpecificOutput"]["additionalContext"]
