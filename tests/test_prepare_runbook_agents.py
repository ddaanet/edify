"""Tests for agent naming convention (crew- prefix, phase-scoped naming)."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

generate_agent_frontmatter = _mod.generate_agent_frontmatter
get_phase_baseline_type = _mod.get_phase_baseline_type
generate_phase_agent = _mod.generate_phase_agent


def setup_baseline_agents(tmp_path: Path) -> None:
    """Create minimal baseline agent files for read_baseline_agent()."""
    agents_dir = tmp_path / "agent-core" / "agents"
    agents_dir.mkdir(parents=True)
    tdd_baseline = agents_dir / "test-driver.md"
    tdd_baseline.write_text(
        "---\nname: test-driver\ndescription: Test Driver agent\n---\n\n"
        "# Test Driver Baseline\n\nRED/GREEN/REFACTOR protocol.\n"
    )
    general_baseline = agents_dir / "artisan.md"
    general_baseline.write_text(
        "---\nname: artisan\ndescription: Artisan agent\n---\n\n"
        "# Artisan Baseline\n\nGeneral execution protocol.\n"
    )


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


class TestGeneratePhaseAgent:
    """Phase agent body composition from 5 layers."""

    def test_generate_phase_agent_layers(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Five layers compose in order: frontmatter, baseline, plan context, phase context, footer."""  # noqa: E501
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = generate_phase_agent(
            "myplan",
            phase_num=1,
            phase_type="tdd",
            plan_context="## Common Context\nShared info",
            phase_context="Phase 1 preamble text",
            model="sonnet",
            total_phases=2,
        )

        # (1) Frontmatter with crew-myplan-p1 name
        assert "name: crew-myplan-p1" in result
        # (2) Test-driver baseline body
        assert "Test Driver" in result
        # (3) Plan context section
        assert "# Runbook-Specific Context" in result
        assert "## Common Context\nShared info" in result
        # (4) Phase context section
        assert "# Phase Context" in result
        assert "Phase 1 preamble text" in result
        # (5) Footer
        assert "Clean tree requirement" in result

        # Layer ordering
        fm_idx = result.index("name: crew-myplan-p1")
        baseline_idx = result.index("Test Driver")
        plan_ctx_idx = result.index("# Runbook-Specific Context")
        phase_ctx_idx = result.index("# Phase Context")
        footer_idx = result.index("Clean tree requirement")
        assert fm_idx < baseline_idx < plan_ctx_idx < phase_ctx_idx < footer_idx
