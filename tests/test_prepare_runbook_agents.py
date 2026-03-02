"""Tests for phase type detection and orchestrator plan format."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

get_phase_baseline_type = _mod.get_phase_baseline_type
detect_phase_types = _mod.detect_phase_types
generate_default_orchestrator = _mod.generate_default_orchestrator


class TestDetectPhaseTypes:
    """Phase type detection from assembled runbook content."""

    def test_detect_phase_types_mixed(self) -> None:
        """Mixed content: TDD, inline, and general phases detected correctly."""
        content = (
            "### Phase 1: Core functions\n\n"
            "## Cycle 1.1: First cycle\n"
            "**RED Phase:** test\n"
            "**GREEN Phase:** impl\n\n"
            "### Phase 2: Infrastructure (type: inline)\n\n"
            "Some inline orchestration text.\n\n"
            "### Phase 3: Cleanup\n\n"
            "## Step 3.1: Do cleanup\n"
            "Step content here.\n"
        )
        result = detect_phase_types(content)
        assert result == {1: "tdd", 2: "inline", 3: "general"}


class TestPhaseBaselineType:
    """Per-phase baseline selection based on content structure."""

    def test_get_phase_baseline_type_tdd(self) -> None:
        """Content with Cycle headers is TDD type."""
        content = "## Cycle 1.1: First\n**RED Phase:**\ntest\n**GREEN Phase:**\nimpl"
        assert get_phase_baseline_type(content) == "tdd"

    def test_get_phase_baseline_type_general(self) -> None:
        """Content with Step headers is general type."""
        assert (
            get_phase_baseline_type("## Step 1.1: First\nStep content here")
            == "general"
        )

    def test_get_phase_baseline_type_default(self) -> None:
        """Content with no headers defaults to general type."""
        assert get_phase_baseline_type("No headers, just prose") == "general"


class TestOrchestratorAgentField:
    """Agent field per step and Phase-Agent Mapping table."""

    def test_orchestrator_agent_field_per_step(self) -> None:
        """Agent field in Phase-Agent Mapping; no old {name}-task reference."""
        result = generate_default_orchestrator(
            "testjob",
            cycles=[
                {"major": 1, "minor": 1, "number": "1.1", "content": ""},
                {"major": 2, "minor": 1, "number": "2.1", "content": ""},
            ],
            phase_agents={1: "crew-testjob-p1", 2: "crew-testjob-p2"},
        )
        assert "crew-testjob-p1" in result
        assert "crew-testjob-p2" in result
        assert "using testjob-task agent" not in result

    def test_orchestrator_phase_agent_mapping_table(self) -> None:
        """Phase-Agent Mapping table before step list with correct rows."""
        result = generate_default_orchestrator(
            "testjob",
            cycles=[
                {"major": 1, "minor": 1, "number": "1.1", "content": ""},
                {"major": 3, "minor": 1, "number": "3.1", "content": ""},
            ],
            inline_phases={2: "inline content"},
            phase_agents={
                1: "crew-testjob-p1",
                2: "(orchestrator-direct)",
                3: "crew-testjob-p3",
            },
            phase_types={1: "tdd", 2: "inline", 3: "general"},
        )
        assert "## Phase-Agent Mapping" in result
        # Table rows contain phase, agent, type
        assert "| 1 |" in result
        assert "crew-testjob-p1" in result
        assert "tdd" in result
        assert "| 2 |" in result
        assert "(orchestrator-direct)" in result
        assert "inline" in result
        assert "| 3 |" in result
        assert "crew-testjob-p3" in result
        assert "general" in result
        # Mapping table appears before step list
        mapping_idx = result.index("## Phase-Agent Mapping")
        step_idx = result.index("## Steps")
        assert mapping_idx < step_idx
