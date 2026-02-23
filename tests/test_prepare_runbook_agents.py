"""Tests for agent naming convention (crew- prefix, phase-scoped naming)."""

import importlib.util
from pathlib import Path

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

generate_agent_frontmatter = _mod.generate_agent_frontmatter
get_phase_baseline_type = _mod.get_phase_baseline_type
generate_phase_agent = _mod.generate_phase_agent
detect_phase_types = _mod.detect_phase_types
generate_default_orchestrator = _mod.generate_default_orchestrator
validate_and_create = _mod.validate_and_create
parse_frontmatter = _mod.parse_frontmatter
extract_sections = _mod.extract_sections
extract_cycles = _mod.extract_cycles
extract_phase_models = _mod.extract_phase_models
extract_phase_preambles = _mod.extract_phase_preambles


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


class TestOrchestratorAgentField:
    """Agent field per step and Phase-Agent Mapping table."""

    def test_orchestrator_agent_field_per_step(self) -> None:
        """Agent field after step header; no old {name}-task reference."""
        result = generate_default_orchestrator(
            "testjob",
            cycles=[
                {"major": 1, "minor": 1, "number": "1.1", "content": ""},
                {"major": 2, "minor": 1, "number": "2.1", "content": ""},
            ],
            phase_agents={1: "crew-testjob-p1", 2: "crew-testjob-p2"},
        )
        assert "Agent: crew-testjob-p1" in result
        assert "Agent: crew-testjob-p2" in result
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
        step_idx = result.index("## Step Execution Order")
        assert mapping_idx < step_idx


_RUNBOOK_2PHASE = """\
---
type: mixed
model: sonnet
name: testmixed
---

## Common Context

Shared info about the project.

### Phase 1: Core (type: tdd)

## Cycle 1.1: First cycle

**Execution Model**: sonnet

**RED Phase:**
Write a test.

**GREEN Phase:**
Implement it.

**Stop Conditions:**
Stop on error.

### Phase 2: Cleanup (type: general)

## Step 2.1: Do cleanup

**Execution Model**: sonnet

Do some cleanup work.
"""

_RUNBOOK_3PHASE_INLINE = """\
---
type: mixed
model: sonnet
name: testinline
---

## Common Context

Shared info about the project.

### Phase 1: Core (type: tdd)

## Cycle 1.1: First cycle

**Execution Model**: sonnet

**RED Phase:**
Write a test.

**GREEN Phase:**
Implement it.

**Stop Conditions:**
Stop on error.

### Phase 2: Infrastructure (type: inline)

Inline orchestration work done by orchestrator directly.

### Phase 3: Cleanup (type: general)

## Step 3.1: Do cleanup

**Execution Model**: sonnet

Do some cleanup work.
"""


class TestValidateCreatesPerPhaseAgents:
    """validate_and_create() creates per-phase agent files in agents_dir."""

    def test_validate_creates_per_phase_agents(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """2-phase mixed runbook creates crew-<name>-p1 and -p2 agents."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        agents_dir = tmp_path / ".claude" / "agents"
        steps_dir = tmp_path / "plans" / "testmixed" / "steps"
        orchestrator_path = tmp_path / "plans" / "testmixed" / "orchestrator-plan.md"
        runbook_path = tmp_path / "plans" / "testmixed" / "runbook.md"

        metadata, body = parse_frontmatter(_RUNBOOK_2PHASE)
        sections = extract_sections(body)
        cycles = extract_cycles(body)
        phase_models = extract_phase_models(body)
        phase_preambles = extract_phase_preambles(body)

        result = validate_and_create(
            runbook_path,
            sections,
            "testmixed",
            agents_dir=agents_dir,
            steps_dir=steps_dir,
            orchestrator_path=orchestrator_path,
            metadata=metadata,
            cycles=cycles,
            phase_models=phase_models,
            phase_preambles=phase_preambles,
        )

        assert result is True
        # Phase agent files created with correct naming
        assert (agents_dir / "crew-testmixed-p1.md").exists()
        assert (agents_dir / "crew-testmixed-p2.md").exists()
        # Old single-agent naming gone
        assert not (agents_dir / "testmixed-task.md").exists()
        # Phase 1 agent uses test-driver baseline
        p1_content = (agents_dir / "crew-testmixed-p1.md").read_text()
        assert "Test Driver" in p1_content
        # Phase 2 agent uses artisan baseline
        p2_content = (agents_dir / "crew-testmixed-p2.md").read_text()
        assert "Artisan" in p2_content
        # Both agents contain plan context
        assert "Shared info" in p1_content
        assert "Shared info" in p2_content
        # Preambles may be empty for these test runbooks (no preamble text)
        # Orchestrator uses per-phase agent names
        orch_content = orchestrator_path.read_text()
        assert "crew-testmixed-p1" in orch_content
        assert "crew-testmixed-p2" in orch_content

    def test_validate_inline_phase_no_agent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """3-phase runbook: inline phase gets no agent file."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        agents_dir = tmp_path / ".claude" / "agents"
        steps_dir = tmp_path / "plans" / "testinline" / "steps"
        orchestrator_path = tmp_path / "plans" / "testinline" / "orchestrator-plan.md"
        runbook_path = tmp_path / "plans" / "testinline" / "runbook.md"

        metadata, body = parse_frontmatter(_RUNBOOK_3PHASE_INLINE)
        sections = extract_sections(body)
        cycles = extract_cycles(body)
        phase_models = extract_phase_models(body)
        phase_preambles = extract_phase_preambles(body)

        result = validate_and_create(
            runbook_path,
            sections,
            "testinline",
            agents_dir=agents_dir,
            steps_dir=steps_dir,
            orchestrator_path=orchestrator_path,
            metadata=metadata,
            cycles=cycles,
            phase_models=phase_models,
            phase_preambles=phase_preambles,
        )

        assert result is True
        # Phase 1 (TDD) and Phase 3 (general) get agent files
        assert (agents_dir / "crew-testinline-p1.md").exists()
        assert (agents_dir / "crew-testinline-p3.md").exists()
        # Phase 2 (inline) has NO agent file
        assert not (agents_dir / "crew-testinline-p2.md").exists()
        # Orchestrator plan contains "(orchestrator-direct)" for phase 2
        orch_content = orchestrator_path.read_text()
        assert "(orchestrator-direct)" in orch_content
