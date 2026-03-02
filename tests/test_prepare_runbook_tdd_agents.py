"""Tests for TDD agent type generation.

Covers tester, implementer, test-corrector, impl-corrector agents.
"""

import importlib.util
import io
import sys
from pathlib import Path

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

validate_and_create = _mod.validate_and_create
parse_frontmatter = _mod.parse_frontmatter
extract_sections = _mod.extract_sections
extract_cycles = _mod.extract_cycles
extract_phase_models = _mod.extract_phase_models
extract_phase_preambles = _mod.extract_phase_preambles


_RUNBOOK_PURE_TDD = """\
---
type: tdd
model: sonnet
name: testplan
---

## Common Context

Shared project context.

### Phase 1: Core (type: tdd)

## Cycle 1.1: First cycle

**Execution Model**: sonnet

**RED Phase:**
Write a failing test.

**GREEN Phase:**
Make the test pass.

**Stop Conditions:**
Stop on unexpected results.
"""


_RUNBOOK_PURE_GENERAL = """\
---
type: general
model: sonnet
name: testgeneral
---

## Common Context

Shared project context.

### Phase 1: Work (type: general)

## Step 1.1: Do work

**Execution Model**: sonnet

Work content here.
"""


def _run_validate(tmp_path: Path, runbook_text: str) -> tuple[Path, bool]:
    """Run validate_and_create for testplan, return (agents_dir, result)."""
    setup_git_repo(tmp_path)
    setup_baseline_agents(tmp_path)

    plan_dir = tmp_path / "plans" / "testplan"
    plan_dir.mkdir(parents=True)
    runbook_path = plan_dir / "runbook.md"
    runbook_path.write_text(runbook_text)

    agents_dir = tmp_path / ".claude" / "agents"
    steps_dir = plan_dir / "steps"
    orchestrator_path = plan_dir / "orchestrator-plan.md"

    _, body = parse_frontmatter(runbook_text)
    sections = extract_sections(body)
    cycles = extract_cycles(body)
    phase_models = extract_phase_models(body)
    phase_preambles = extract_phase_preambles(body)
    frontmatter, _ = parse_frontmatter(runbook_text)

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        result = validate_and_create(
            str(runbook_path),
            sections,
            "testplan",
            agents_dir,
            steps_dir,
            orchestrator_path,
            frontmatter,
            cycles=cycles,
            phase_models=phase_models,
            phase_preambles=phase_preambles,
        )
    finally:
        sys.stdout = old_stdout

    return agents_dir, result


class TestTDDAgentsGenerated:
    """4 TDD-specific agent files generated for TDD runbooks."""

    def test_tdd_agents_generated_for_tdd_runbook(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Pure-TDD runbook produces exactly 4 TDD agent files."""
        monkeypatch.chdir(tmp_path)
        agents_dir, result = _run_validate(tmp_path, _RUNBOOK_PURE_TDD)

        assert result is True
        agent_files = {f.name for f in agents_dir.glob("*.md")}

        assert "testplan-tester.md" in agent_files
        assert "testplan-implementer.md" in agent_files
        assert "testplan-test-corrector.md" in agent_files
        assert "testplan-impl-corrector.md" in agent_files
        assert len(agent_files) == 4

    def test_tester_uses_test_driver_baseline(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Tester agent body contains test-driver.md baseline content."""
        monkeypatch.chdir(tmp_path)
        agents_dir, result = _run_validate(tmp_path, _RUNBOOK_PURE_TDD)

        assert result is True
        tester_content = (agents_dir / "testplan-tester.md").read_text()
        assert "TDD Task Agent - Baseline Template" in tester_content

    def test_implementer_uses_test_driver_baseline(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Implementer agent body contains test-driver.md baseline content."""
        monkeypatch.chdir(tmp_path)
        agents_dir, result = _run_validate(tmp_path, _RUNBOOK_PURE_TDD)

        assert result is True
        impl_content = (agents_dir / "testplan-implementer.md").read_text()
        assert "TDD Task Agent - Baseline Template" in impl_content

    def test_test_corrector_uses_corrector_baseline(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test-corrector agent body contains corrector.md baseline content."""
        monkeypatch.chdir(tmp_path)
        agents_dir, result = _run_validate(tmp_path, _RUNBOOK_PURE_TDD)

        assert result is True
        tc_content = (agents_dir / "testplan-test-corrector.md").read_text()
        assert "# Corrector" in tc_content

    def test_impl_corrector_uses_corrector_baseline(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Impl-corrector agent body contains corrector.md baseline content."""
        monkeypatch.chdir(tmp_path)
        agents_dir, result = _run_validate(tmp_path, _RUNBOOK_PURE_TDD)

        assert result is True
        ic_content = (agents_dir / "testplan-impl-corrector.md").read_text()
        assert "# Corrector" in ic_content

    def test_all_four_agents_contain_plan_context(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """All 4 TDD agents embed # Plan Context with ## Design subsection."""
        monkeypatch.chdir(tmp_path)
        agents_dir, result = _run_validate(tmp_path, _RUNBOOK_PURE_TDD)

        assert result is True
        for agent_name in [
            "testplan-tester.md",
            "testplan-implementer.md",
            "testplan-test-corrector.md",
            "testplan-impl-corrector.md",
        ]:
            content = (agents_dir / agent_name).read_text()
            assert "# Plan Context" in content, f"{agent_name} missing # Plan Context"
            assert "## Design" in content, f"{agent_name} missing ## Design"

    def test_tester_contains_test_quality_directive(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Tester agent contains role-specific test quality directive."""
        monkeypatch.chdir(tmp_path)
        agents_dir, result = _run_validate(tmp_path, _RUNBOOK_PURE_TDD)

        assert result is True
        tester_content = (agents_dir / "testplan-tester.md").read_text()
        assert "test quality" in tester_content.lower()

    def test_implementer_contains_implementation_directive(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Implementer agent contains role-specific implementation directive."""
        monkeypatch.chdir(tmp_path)
        agents_dir, result = _run_validate(tmp_path, _RUNBOOK_PURE_TDD)

        assert result is True
        impl_content = (agents_dir / "testplan-implementer.md").read_text()
        assert (
            "implementation" in impl_content.lower() or "coding" in impl_content.lower()
        )


class TestNoTDDAgentsForGeneralRunbook:
    """General runbooks preserve Phase 1 behavior — no TDD agents generated."""

    def test_no_tdd_agents_for_general_runbook(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """General runbook produces no TDD-specific agent files."""
        monkeypatch.chdir(tmp_path)
        agents_dir, result = _run_validate(tmp_path, _RUNBOOK_PURE_GENERAL)

        assert result is True
        agent_files = {f.name for f in agents_dir.glob("*.md")}

        assert "testgeneral-tester.md" not in agent_files
        assert "testgeneral-implementer.md" not in agent_files
        assert "testgeneral-test-corrector.md" not in agent_files
        assert "testgeneral-impl-corrector.md" not in agent_files

    def test_general_runbook_still_creates_task_agent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """General runbook still creates the task agent (Phase 1 preserved)."""
        monkeypatch.chdir(tmp_path)
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)

        plan_dir = tmp_path / "plans" / "testgeneral"
        plan_dir.mkdir(parents=True)
        runbook_path = plan_dir / "runbook.md"
        runbook_path.write_text(_RUNBOOK_PURE_GENERAL)

        agents_dir = tmp_path / ".claude" / "agents"
        steps_dir = plan_dir / "steps"
        orchestrator_path = plan_dir / "orchestrator-plan.md"

        _, body = parse_frontmatter(_RUNBOOK_PURE_GENERAL)
        sections = extract_sections(body)
        cycles = extract_cycles(body)
        phase_models = extract_phase_models(body)
        phase_preambles = extract_phase_preambles(body)
        frontmatter, _ = parse_frontmatter(_RUNBOOK_PURE_GENERAL)

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            result = validate_and_create(
                str(runbook_path),
                sections,
                "testgeneral",
                agents_dir,
                steps_dir,
                orchestrator_path,
                frontmatter,
                cycles=cycles,
                phase_models=phase_models,
                phase_preambles=phase_preambles,
            )
        finally:
            sys.stdout = old_stdout

        assert result is True
        agent_files = {f.name for f in agents_dir.glob("*.md")}
        assert "testgeneral-task.md" in agent_files
