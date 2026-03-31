"""Tests for orchestrator plan generation (D-5)."""

import importlib.util
from pathlib import Path

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

assemble_phase_files = _mod.assemble_phase_files
extract_phase_models = _mod.extract_phase_models
extract_step_metadata = _mod.extract_step_metadata
generate_default_orchestrator = _mod.generate_default_orchestrator
parse_frontmatter = _mod.parse_frontmatter
extract_sections = _mod.extract_sections
extract_cycles = _mod.extract_cycles
validate_and_create = _mod.validate_and_create


def _run_validate(tmp_path: Path, runbook_content: str, name: str) -> tuple[bool, Path]:
    """Run validate_and_create for a TDD runbook; return (result, steps_dir)."""
    rf = tmp_path / "runbook.md"
    rf.write_text(runbook_content)
    metadata, body = parse_frontmatter(runbook_content)
    sections = extract_sections(body)
    cycles = extract_cycles(body)
    phase_models = extract_phase_models(body)
    steps_dir = tmp_path / "plans" / name / "steps"
    result = validate_and_create(
        rf,
        sections,
        name,
        tmp_path / ".claude" / "agents",
        steps_dir,
        tmp_path / "plans" / name / "orchestrator-plan.md",
        metadata,
        cycles,
        phase_models,
    )
    return result, steps_dir


_THREE_PHASE_CYCLES = [
    {"major": 1, "minor": 1, "number": "1.1", "title": "First", "content": "test 1"},
    {"major": 1, "minor": 2, "number": "1.2", "title": "Second", "content": "test 2"},
    {"major": 2, "minor": 1, "number": "2.1", "title": "Third", "content": "test 3"},
]


class TestOrchestratorPlan:
    """Orchestrator plan generation: phase file paths and model table."""

    def test_orchestrator_plan_includes_phase_file_paths(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """PHASE_BOUNDARY entries contain source phase file paths."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        plan_dir = tmp_path / "plans" / "test-job"
        plan_dir.mkdir(parents=True)

        phase1 = plan_dir / "runbook-phase-1.md"
        phase1.write_text(
            "### Phase 1: Setup (type: general, model: sonnet)\n\n"
            "## Step 1.1: First step\n\nStep content."
        )

        phase2 = plan_dir / "runbook-phase-2.md"
        phase2.write_text(
            "### Phase 2: TDD (type: tdd, model: sonnet)\n\n"
            "## Cycle 2.1: First cycle\n\n"
            "**RED Phase:**\nWrite test.\n"
            "**GREEN Phase:**\nImplement it.\n"
            "**Stop/Error Conditions:** STOP if unexpected."
        )

        content, _ = assemble_phase_files(plan_dir)
        assert content is not None

        metadata, body = parse_frontmatter(content)
        metadata["type"] = "mixed"
        sections = extract_sections(body)
        cycles = extract_cycles(body)
        phase_models = extract_phase_models(body)

        orch_path = tmp_path / "plans" / "test-job" / "orchestrator-plan.md"
        steps_dir = tmp_path / "plans" / "test-job" / "steps"
        agents_dir = tmp_path / ".claude" / "agents"

        result = validate_and_create(
            plan_dir / "runbook.md",
            sections,
            "test-job",
            agents_dir,
            steps_dir,
            orch_path,
            metadata,
            cycles,
            phase_models,
            phase_dir=str(plan_dir),
        )

        assert result is True
        orch_content = orch_path.read_text()

        assert f"Phase file: {plan_dir}/runbook-phase-1.md" in orch_content, (
            f"Expected phase 1 file path in orchestrator. Got:\n{orch_content}"
        )
        assert f"Phase file: {plan_dir}/runbook-phase-2.md" in orch_content, (
            f"Expected phase 2 file path in orchestrator. Got:\n{orch_content}"
        )

    def test_orchestrator_plan_includes_phase_model_table(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Phase Models section lists each phase with its resolved model."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        runbook_content = """\
---
type: tdd
model: haiku
name: phase-model-table-test
---

### Phase 1: Core (type: tdd, model: sonnet)

## Cycle 1.1: Test phase 1

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 2: Advanced (type: tdd, model: opus)

## Cycle 2.1: Test phase 2

**RED Phase:**
Write another test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 3: Cleanup (type: tdd)

## Cycle 3.1: Test phase 3

**RED Phase:**
Write cleanup test.
**GREEN Phase:**
Implement cleanup.
**Stop/Error Conditions:** STOP if unexpected.
"""
        result, _steps_dir = _run_validate(
            tmp_path, runbook_content, "phase-model-table-test"
        )

        assert result is True
        orch_path = (
            tmp_path / "plans" / "phase-model-table-test" / "orchestrator-plan.md"
        )
        assert orch_path.exists()
        orch_content = orch_path.read_text()

        assert "## Phase Models" in orch_content, (
            f"Expected '## Phase Models' section in orchestrator plan.\n{orch_content}"
        )
        assert "- Phase 1: sonnet" in orch_content, (
            f"Expected '- Phase 1: sonnet' in Phase Models.\n{orch_content}"
        )
        assert "- Phase 2: opus" in orch_content, (
            f"Expected '- Phase 2: opus' in Phase Models.\n{orch_content}"
        )
        assert "- Phase 3: haiku" in orch_content, (
            f"Expected '- Phase 3: haiku' (frontmatter fallback).\n{orch_content}"
        )

    def test_orchestrator_plan_omits_phase_models_when_no_model_info(self) -> None:
        """Phase Models omitted when no model info provided."""
        content = generate_default_orchestrator(
            "no-model-job",
            cycles=[
                {
                    "major": 1,
                    "minor": 1,
                    "number": "1.1",
                    "title": "Test",
                    "content": "body",
                }
            ],
            phase_models=None,
            default_model=None,
        )
        assert "## Phase Models" not in content, (
            f"Phase Models section should be absent without model info.\n{content}"
        )

    def test_orchestrator_plan_structured_format(self) -> None:
        """Orchestrator plan uses structured header and step list."""
        content = generate_default_orchestrator(
            "test-job",
            cycles=_THREE_PHASE_CYCLES,
            phase_models={1: "sonnet", 2: "opus"},
        )

        # TDD runbooks use none (tester/implementer dispatch)
        assert "**Agent:** none" in content, (
            f"Expected Agent: none for TDD runbook (no general task agent).\n{content}"
        )
        assert "**Corrector Agent:** test-job-corrector" in content, (
            f"Expected multi-phase corrector agent in header.\n{content}"
        )
        assert "**Type:** tdd" in content, f"Expected Type field set to tdd.\n{content}"

        # Check Steps section exists
        assert "## Steps" in content, f"Expected Steps section.\n{content}"

        # Check pipe-delimited step format with TEST/IMPLEMENT role markers
        assert "- step-1-1-test.md | Phase 1 | sonnet | 30 | TEST" in content, (
            f"Expected TEST step entry for cycle 1.1.\n{content}"
        )
        assert "- step-1-1-impl.md | Phase 1 | sonnet | 30 | IMPLEMENT" in content, (
            f"Expected IMPLEMENT step entry for cycle 1.1.\n{content}"
        )
        assert (
            "- step-1-2-impl.md | Phase 1 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY"
            in content
        ), f"Expected phase boundary marker for last phase 1 item.\n{content}"
        assert "- step-2-1-test.md | Phase 2 | opus | 30 | TEST" in content, (
            f"Expected TEST step entry for cycle 2.1.\n{content}"
        )

    def test_orchestrator_plan_single_phase_corrector_agent(self) -> None:
        """Single-phase runbook has 'none' for corrector agent."""
        content = generate_default_orchestrator(
            "single-phase-job",
            steps={
                "1.1": "first",
                "1.2": "second",
            },
            step_phases={"1.1": 1, "1.2": 1},
            phase_models={1: "haiku"},
        )

        assert "**Corrector Agent:** none" in content, (
            f"Expected corrector agent as none for single-phase.\n{content}"
        )

    def test_orchestrator_plan_boundaries_and_summaries(self) -> None:
        """Orchestrator plan marks phase boundaries and phase summaries."""
        content = generate_default_orchestrator(
            "test-job",
            cycles=_THREE_PHASE_CYCLES,
            inline_phases={3: "inline phase 3 content"},
            phase_models={1: "sonnet", 2: "opus", 3: "haiku"},
        )

        # PHASE_BOUNDARY markers on last step of each phase (impl is last in TDD)
        assert (
            "step-1-2-impl.md | Phase 1 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY"
            in content
        )
        assert (
            "step-2-1-impl.md | Phase 2 | opus | 30 | IMPLEMENT | PHASE_BOUNDARY"
            in content
        )
        assert "- INLINE | Phase 3 | —" in content
        # Phase Summaries with per-phase subsections
        assert "## Phase Summaries" in content
        assert "### Phase 1:" in content
        assert "### Phase 2:" in content
        assert "### Phase 3:" in content

        # Check IN:/OUT: bullet items in summaries
        assert "- IN:" in content, f"Expected IN: bullets in summaries.\n{content}"
        assert "- OUT:" in content, f"Expected OUT: bullets in summaries.\n{content}"

    def test_max_turns_extraction_and_propagation(self) -> None:
        """Max Turns extracted from metadata and propagated to orchestrator."""
        cycle_with_max_turns = {
            "major": 1,
            "minor": 1,
            "number": "1.1",
            "title": "First",
            "content": "**MAX TURNS**: 25\n\nTest content",
        }
        cycle_default_max_turns = {
            "major": 1,
            "minor": 2,
            "number": "1.2",
            "title": "Second",
            "content": "Test content without max turns",
        }

        # Test extract_step_metadata
        metadata_with_max = extract_step_metadata(cycle_with_max_turns["content"])
        assert "max_turns" in metadata_with_max, (
            f"Expected max_turns in metadata. Got {metadata_with_max}"
        )
        assert metadata_with_max["max_turns"] == 25, (
            f"Expected max_turns=25, got {metadata_with_max.get('max_turns')}"
        )

        metadata_default = extract_step_metadata(cycle_default_max_turns["content"])
        assert "max_turns" in metadata_default, (
            f"Expected max_turns in metadata. Got {metadata_default}"
        )
        assert metadata_default["max_turns"] == 30, (
            f"Expected max_turns=30 (default), got {metadata_default.get('max_turns')}"
        )

        # Test orchestrator plan uses extracted max_turns
        content = generate_default_orchestrator(
            "test-job",
            cycles=[cycle_with_max_turns, cycle_default_max_turns],
            phase_models={1: "sonnet"},
        )

        # Test step with explicit max turns should show 25
        assert "- step-1-1-test.md | Phase 1 | sonnet | 25 | TEST" in content, (
            f"Expected max_turns=25 in TEST step entry.\n{content}"
        )
        assert "- step-1-1-impl.md | Phase 1 | sonnet | 25 | IMPLEMENT" in content, (
            f"Expected max_turns=25 in IMPLEMENT step entry.\n{content}"
        )

        # Steps with default max turns should show 30
        assert "- step-1-2-test.md | Phase 1 | sonnet | 30 | TEST" in content, (
            f"Expected max_turns=30 in TEST step entry.\n{content}"
        )
        assert (
            "- step-1-2-impl.md | Phase 1 | sonnet | 30 | IMPLEMENT | PHASE_BOUNDARY"
            in content
        ), f"Expected max_turns=30 in IMPLEMENT step entry.\n{content}"


class TestPhaseSummariesFromPreambles:
    """Phase Summaries section uses preamble text instead of placeholders."""

    def test_preambles_populate_in_scope(self) -> None:
        """Phase preambles appear as IN scope in Phase Summaries."""
        content = generate_default_orchestrator(
            "testjob",
            steps={"1.1": "Work here.", "2.1": "More work."},
            step_phases={"1.1": 1, "2.1": 2},
            default_model="sonnet",
            phase_preambles={1: "Core data model", 2: "API layer"},
        )
        assert "- IN: Core data model" in content
        assert "- IN: API layer" in content

    def test_missing_preamble_shows_not_specified(self) -> None:
        """Phases without preamble text show '(not specified)'."""
        content = generate_default_orchestrator(
            "testjob",
            steps={"1.1": "Work here."},
            default_model="sonnet",
        )
        assert "- IN: (not specified)" in content

    def test_out_scope_references_other_phases(self) -> None:
        """OUT scope lists other phase numbers."""
        content = generate_default_orchestrator(
            "testjob",
            steps={"1.1": "Work.", "2.1": "More.", "3.1": "Final."},
            step_phases={"1.1": 1, "2.1": 2, "3.1": 3},
            default_model="sonnet",
            phase_preambles={1: "Core", 2: "API", 3: "Docs"},
        )
        # Phase 1 OUT should reference phases 2 and 3
        p1_section = content.split("### Phase 1:")[1].split("### Phase 2:")[0]
        out_line = next(x for x in p1_section.splitlines() if x.startswith("- OUT:"))
        assert "Phase 2" in out_line
        assert "Phase 3" in out_line

    def test_single_phase_out_scope(self) -> None:
        """Single-phase plan shows '(single phase)' for OUT."""
        content = generate_default_orchestrator(
            "testjob",
            steps={"1.1": "Work here."},
            default_model="sonnet",
            phase_preambles={1: "Everything"},
        )
        assert "- OUT: (single phase)" in content
