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
generate_default_orchestrator = _mod.generate_default_orchestrator


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


class TestStepFileSplitting:
    """TDD cycles produce split step-N-test.md + step-N-impl.md files."""

    def test_tdd_cycle_splits_into_test_and_impl_files(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """TDD cycle splits into test and impl step files."""
        monkeypatch.chdir(tmp_path)
        _, result = _run_validate(tmp_path, _RUNBOOK_PURE_TDD)

        assert result is True
        steps_dir = tmp_path / "plans" / "testplan" / "steps"
        step_files = {f.name for f in steps_dir.glob("*.md")}

        # Two files produced per cycle, not one
        assert "step-1-1-test.md" in step_files, "test file missing"
        assert "step-1-1-impl.md" in step_files, "impl file missing"
        assert "step-1-1.md" not in step_files, "unsplit file should not exist"

        test_content = (steps_dir / "step-1-1-test.md").read_text()
        impl_content = (steps_dir / "step-1-1-impl.md").read_text()

        # Test file contains RED phase content
        assert "RED Phase" in test_content
        assert "Write a failing test." in test_content

        # Test file does NOT contain GREEN phase content
        assert "GREEN Phase" not in test_content
        assert "Make the test pass." not in test_content

        # Impl file contains GREEN phase content
        assert "GREEN Phase" in impl_content
        assert "Make the test pass." in impl_content

        # Impl file does NOT contain RED phase content
        assert "RED Phase" not in impl_content
        assert "Write a failing test." not in impl_content

        # Both files have metadata headers
        for content in (test_content, impl_content):
            assert "**Plan**:" in content
            assert "**Phase**:" in content
            assert "**Execution Model**:" in content

    def test_general_step_not_split(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """General runbook steps produce single step-N-M.md (no splitting)."""
        monkeypatch.chdir(tmp_path)
        # Use testplan dir (hardcoded in _run_validate helper)
        _run_validate(tmp_path, _RUNBOOK_PURE_GENERAL)

        steps_dir = tmp_path / "plans" / "testplan" / "steps"
        step_files = {f.name for f in steps_dir.glob("*.md")}

        assert "step-1-1.md" in step_files
        assert "step-1-1-test.md" not in step_files
        assert "step-1-1-impl.md" not in step_files


_TDD_CYCLES = [
    {
        "number": "1.1",
        "major": 1,
        "minor": 1,
        "content": "**Execution Model**: sonnet\n**Max Turns**: 25\n",
    },
    {
        "number": "1.2",
        "major": 1,
        "minor": 2,
        "content": "**Execution Model**: sonnet\n**Max Turns**: 25\n",
    },
]

_GENERAL_STEPS = {"1.1": "**Execution Model**: sonnet\n**Max Turns**: 25\nWork here.\n"}


def test_orchestrator_plan_tdd_role_markers() -> None:
    """TDD step entries have TEST/IMPLEMENT markers; general steps do not."""
    tdd_plan = generate_default_orchestrator(
        "testplan",
        cycles=_TDD_CYCLES,
        default_model="sonnet",
    )

    # Test step entries have TEST marker, impl step entries have IMPLEMENT marker
    assert "step-1-1-test.md | Phase 1 | sonnet | 25 | TEST" in tdd_plan
    assert "step-1-1-impl.md | Phase 1 | sonnet | 25 | IMPLEMENT" in tdd_plan

    # TEST appears before IMPLEMENT for each cycle
    test_pos = tdd_plan.index("step-1-1-test.md")
    impl_pos = tdd_plan.index("step-1-1-impl.md")
    assert test_pos < impl_pos, "TEST entry must appear before IMPLEMENT entry"

    # No single unsplit entry for TDD cycles
    assert "step-1-1.md" not in tdd_plan

    # Plan associates TEST steps with tester agent and IMPLEMENT steps with implementer
    assert "tester" in tdd_plan
    assert "implementer" in tdd_plan

    # General runbook step entries have no role marker
    general_plan = generate_default_orchestrator(
        "testgeneral",
        steps=_GENERAL_STEPS,
        default_model="sonnet",
    )
    assert "| TEST" not in general_plan
    assert "| IMPLEMENT" not in general_plan
    assert "step-1-1.md | Phase 1 | sonnet | 25" in general_plan
