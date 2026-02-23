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
extract_phase_preambles = _mod.extract_phase_preambles
extract_phase_models = _mod.extract_phase_models
strip_fenced_blocks = _mod.strip_fenced_blocks
extract_file_references = _mod.extract_file_references


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


class TestFencedCycleHeaders:
    """Cycle header detection should ignore headers inside fenced blocks."""

    def test_extract_cycles_ignores_cycle_header_inside_fence(self) -> None:
        """Parser should ignore ## Cycle headers inside fenced code blocks."""
        content = dedent("""\
            ## Cycle 1.1: Real cycle

            ### RED Phase
            Test something.

            ### GREEN Phase
            Implement something.

            Example of a cycle definition:

            ```markdown
            ## Cycle 1.2: Example cycle

            ### RED Phase
            Example test.
            ```

            ## Cycle 1.3: Another real cycle

            ### RED Phase
            Test more.
        """)
        cycles = extract_cycles(content)
        numbers = [c["number"] for c in cycles]
        assert "1.1" in numbers
        assert "1.3" in numbers
        assert "1.2" not in numbers
        assert len(cycles) == 2


class TestFencedPhaseHeaders:
    """Phase header detection should ignore headers inside fenced blocks."""

    def test_extract_sections_ignores_inline_phase_inside_fence(self) -> None:
        """Parser should ignore ### Phase headers inside fenced code blocks."""
        content = dedent("""\
            ### Phase 1: Core (type: general)

            ## Step 1.1: Real step

            Example runbook structure:

            ```
            ### Phase 2: Infrastructure (type: inline)

            Edit some files.
            ```

            ## Step 1.2: Second step

            More work.
        """)
        sections = extract_sections(content)
        assert sections is not None
        assert len(sections["inline_phases"]) == 0
        assert len(sections["steps"]) == 2


class TestFencedMultiBacktickFences:
    """Fence detection should handle 4+ backtick fences.

    CommonMark semantics: closing fence requires >= opening count.
    """

    def test_extract_sections_handles_four_backtick_fences(self) -> None:
        """4-backtick fence should not be closed by nested 3-backtick.

        Opening 3-backtick inside 4-backtick fence incorrectly toggles the fence
        state with toggle-based logic.
        """
        content = dedent("""\
            ### Phase 1: Core (type: general)

            ## Step 1.1: Real step

            Example with nested fences:

            ````markdown
            Here is a code example:

            ```python
            print("hello")
            ```

            ## Step 2.1: This is inside the outer fence

            Still inside.
            ````

            ## Step 1.2: Another real step

            More work.
        """)
        sections = extract_sections(content)
        assert sections is not None
        assert "1.1" in sections["steps"]
        assert "1.2" in sections["steps"]
        assert "2.1" not in sections["steps"]
        assert len(sections["steps"]) == 2

    def test_extract_sections_four_backtick_unpaired_inner_fence(self) -> None:
        """Unpaired inner 3-backtick must not leak from 4-backtick fence.

        This is the actual toggle failure mode: a single inner ``` leaves toggle
        state in_fence=False, exposing the step header. Count-based semantics
        correctly keeps in_fence=True (3 < 4 opening count).
        """
        content = dedent("""\
            ### Phase 1: Core (type: general)

            ## Step 1.1: Real step

            ````
            ```python
            ## Step 2.1: Inside outer fence, no closing inner fence
            ````

            ## Step 1.2: Another real step

            More work.
        """)
        sections = extract_sections(content)
        assert sections is not None
        assert "1.1" in sections["steps"]
        assert "1.2" in sections["steps"]
        assert "2.1" not in sections["steps"]
        assert len(sections["steps"]) == 2


class TestFencedTildeFences:
    """Fence detection should handle tilde fences.

    CommonMark semantics: tilde fences ≥3 tildes, closing requires ≥ opening count.
    Tilde and backtick fences do NOT cross-close.
    """

    def test_extract_sections_handles_tilde_fences(self) -> None:
        """Tilde fences should be recognized and tracked separately."""
        content = dedent("""\
            ### Phase 1: Core (type: general)

            ## Step 1.1: Real step

            ~~~
            ## Step 2.1: Inside tilde fence
            ~~~

            ## Step 1.2: Another real step

            Work.
        """)
        sections = extract_sections(content)
        assert sections is not None
        assert "2.1" not in sections["steps"]
        assert len(sections["steps"]) == 2

    def test_extract_sections_backtick_does_not_close_tilde(self) -> None:
        """Backtick fence should not close a tilde fence."""
        content = dedent("""\
            ### Phase 1: Core (type: general)

            ## Step 1.1: Real step

            ~~~
            ```
            ## Step 2.1: Still inside tilde fence
            ```
            ~~~

            ## Step 1.2: Real step two

            Work.
        """)
        sections = extract_sections(content)
        assert sections is not None
        assert "2.1" not in sections["steps"]
        assert len(sections["steps"]) == 2


class TestFencedPhasePreambles:
    """Phase preamble extraction should ignore headers inside fenced blocks."""

    def test_extract_phase_preambles_ignores_fenced_headers(self) -> None:
        """Preamble extraction should not terminate at fenced step headers."""
        content = dedent("""\
            ### Phase 1: Core

            This is the preamble for phase 1.

            Example structure:

            ```
            ## Step 1.1: Example
            Some content.
            ```

            More preamble content after the fence.

            ## Step 1.1: Real step
        """)
        preambles = extract_phase_preambles(content)
        assert 1 in preambles
        assert "More preamble content after the fence." in preambles[1]


class TestExtractPhaseModelsIgnoresFences:
    """Phase model extraction should ignore model: annotations inside fenced blocks."""

    def test_extract_phase_models_ignores_fenced_annotations(self) -> None:
        """Regex should not match phase headers inside fenced code blocks."""
        content = dedent("""\
            ### Phase 1: Core (model: haiku)

            ## Step 1.1: Real step

            Example:

            ```
            ### Phase 2: Infrastructure (model: opus)
            ```
        """)
        models = extract_phase_models(content)
        assert models == {1: "haiku"}
        assert 2 not in models


class TestExtractFileReferencesIgnoresFences:
    """File reference extraction ignores references inside fenced blocks."""

    def test_extract_file_references_handles_four_backtick_fences(self) -> None:
        """4-backtick fence should not expose content to reference extraction.

        Current naive regex re.sub(r"```.*?```", ...) closes on the inner ```
        fence, leaving content after it exposed.
        """
        content = dedent("""\
            Real reference: `src/main.py`

            ````markdown
            Example reference: `src/example.py`

            ```python
            import src.other
            ```

            Another: `src/fake.py`
            ````
        """)
        refs = extract_file_references(content)
        assert "src/main.py" in refs
        assert "src/example.py" not in refs
        assert "src/fake.py" not in refs
