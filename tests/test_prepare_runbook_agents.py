"""Tests for agent naming convention (crew- prefix, phase-scoped naming)."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

generate_agent_frontmatter = _mod.generate_agent_frontmatter


class TestAgentNamingConvention:
    """Crew- prefix with optional phase suffix."""

    def test_agent_frontmatter_crew_naming_multi_phase(self) -> None:
        """Multi-phase plan uses crew-<name>-p<N> naming."""
        result = generate_agent_frontmatter(
            "testplan", model="sonnet", phase_num=2, total_phases=3
        )
        assert "name: crew-testplan-p2" in result
        assert "Execute phase 2 of testplan" in result

    def test_agent_frontmatter_crew_naming_single_phase(self) -> None:
        """Single-phase plan uses crew-<name> naming without phase suffix."""
        result = generate_agent_frontmatter(
            "testplan", model="sonnet", phase_num=1, total_phases=1
        )
        assert "name: crew-testplan" in result
        assert "Execute testplan" in result
        assert "-p1" not in result
