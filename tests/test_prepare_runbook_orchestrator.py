"""Tests for orchestrator plan generation (RC-4 fix)."""

import importlib.util
from pathlib import Path

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

assemble_phase_files = _mod.assemble_phase_files
extract_phase_models = _mod.extract_phase_models
parse_frontmatter = _mod.parse_frontmatter
extract_sections = _mod.extract_sections
extract_cycles = _mod.extract_cycles
validate_and_create = _mod.validate_and_create


def _run_validate(tmp_path: Path, runbook_content: str, name: str) -> tuple[bool, Path]:
    """Run validate_and_create for a TDD runbook; return (result, steps_dir)."""
    rf = tmp_path / "runbook.md"
    rf.write_text(runbook_content)
    metadata, body = parse_frontmatter(runbook_content)
    metadata["type"] = "tdd"
    sections = extract_sections(body)
    cycles = extract_cycles(body)
    phase_models = extract_phase_models(body)
    steps_dir = tmp_path / "plans" / name / "steps"
    result = validate_and_create(
        rf,
        sections,
        name,
        tmp_path / ".claude" / "agents" / f"{name}-task.md",
        steps_dir,
        tmp_path / "plans" / name / "orchestrator-plan.md",
        metadata,
        cycles,
        phase_models,
    )
    return result, steps_dir


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
        agent_path = tmp_path / ".claude" / "agents" / "test-job-task.md"

        result = validate_and_create(
            plan_dir / "runbook.md",
            sections,
            "test-job",
            agent_path,
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
