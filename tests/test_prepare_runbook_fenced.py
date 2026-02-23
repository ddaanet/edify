"""Integration tests for prepare-runbook.py fenced code block awareness."""

import importlib.util
from pathlib import Path
from textwrap import dedent

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

extract_sections = _mod.extract_sections
extract_cycles = _mod.extract_cycles


class TestFencedStepHeaders:
    """Step header detection should ignore headers inside fenced blocks."""

    def test_extract_sections_ignores_step_header_inside_fence(self) -> None:
        """Parser should ignore ## Step headers inside fenced code blocks."""
        content = dedent("""\
            ### Phase 1: Core (type: general)

            ## Step 1.1: Real step

            Implementation details.

            Here is an example runbook:

            ```markdown
            ## Step 2.1: Example step

            This is just documentation.
            ```

            ## Step 1.2: Another real step

            More implementation.
        """)
        sections = extract_sections(content)
        assert sections is not None
        assert "1.1" in sections["steps"]
        assert "1.2" in sections["steps"]
        assert "2.1" not in sections["steps"]
        assert len(sections["steps"]) == 2
