"""Tests for agent caching model (single {name}-task agent)."""

import importlib.util
from pathlib import Path

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

validate_and_create = _mod.validate_and_create
parse_frontmatter = _mod.parse_frontmatter
extract_sections = _mod.extract_sections
extract_cycles = _mod.extract_cycles
extract_phase_models = _mod.extract_phase_models
extract_phase_preambles = _mod.extract_phase_preambles


_RUNBOOK_2PHASE_GENERAL = """\
---
type: general
model: sonnet
name: testgeneral
---

## Common Context

Shared info about the project.

### Phase 1: Setup (type: general)

## Step 1.1: Do setup

**Execution Model**: sonnet

Do some setup work.

### Phase 2: Cleanup (type: general)

## Step 2.1: Do cleanup

**Execution Model**: sonnet

Do some cleanup work.
"""


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

_RUNBOOK_1PHASE_GENERAL = """\
---
type: general
model: sonnet
name: testsingle
---

## Common Context

Shared info.

### Phase 1: Work (type: general)

## Step 1.1: Do work

**Execution Model**: sonnet

Work content here.
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


class TestSingleTaskAgent:
    """Single {name}-task agent replaces per-phase crew- agents."""

    def test_single_task_agent_replaces_per_phase(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """2-phase general runbook creates exactly 1 agent: {name}-task.md."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        agents_dir = tmp_path / ".claude" / "agents"
        steps_dir = tmp_path / "plans" / "testgeneral" / "steps"
        orchestrator_path = tmp_path / "plans" / "testgeneral" / "orchestrator-plan.md"
        runbook_path = tmp_path / "plans" / "testgeneral" / "runbook.md"

        metadata, body = parse_frontmatter(_RUNBOOK_2PHASE_GENERAL)
        sections = extract_sections(body)
        cycles = extract_cycles(body)
        phase_models = extract_phase_models(body)
        phase_preambles = extract_phase_preambles(body)

        result = validate_and_create(
            runbook_path,
            sections,
            "testgeneral",
            agents_dir=agents_dir,
            steps_dir=steps_dir,
            orchestrator_path=orchestrator_path,
            metadata=metadata,
            cycles=cycles,
            phase_models=phase_models,
            phase_preambles=phase_preambles,
        )

        assert result is True

        # No per-phase crew- agents — replaced by role-based agents
        assert not (agents_dir / "crew-testgeneral-p1.md").exists()
        assert not (agents_dir / "crew-testgeneral-p2.md").exists()

        # Agent filename is {name}-task.md
        task_agent = agents_dir / "testgeneral-task.md"
        created_agents = list(agents_dir.glob("*.md"))
        assert task_agent.exists(), (
            f"testgeneral-task.md not found, got: {[a.name for a in created_agents]}"
        )

        content = task_agent.read_text()

        # Frontmatter name field is {name}-task
        assert "name: testgeneral-task" in content

        # Scope enforcement footer
        assert "Execute ONLY the step file" in content

        # Clean tree footer
        assert "Commit all changes before reporting success" in content

        # Artisan baseline content (general runbook)
        assert "Artisan" in content


class TestValidateCreatesTaskAgent:
    """validate_and_create() creates a single {name}-task agent file."""

    def test_validate_creates_single_task_agent_mixed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """2-phase mixed runbook creates single testmixed-task.md agent."""
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
        # Single task agent created, no per-phase agents
        assert (agents_dir / "testmixed-task.md").exists()
        assert not (agents_dir / "crew-testmixed-p1.md").exists()
        assert not (agents_dir / "crew-testmixed-p2.md").exists()
        # Mixed runbook uses artisan baseline
        content = (agents_dir / "testmixed-task.md").read_text()
        assert "Artisan" in content
        # Agent contains plan context
        assert "Shared info" in content
        # Orchestrator references task agent
        orch_content = orchestrator_path.read_text()
        assert "testmixed-task" in orch_content

    def test_validate_inline_phase_no_extra_agent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """3-phase runbook with inline phase: still produces 1 task agent."""
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
        # Single task agent, no per-phase agents
        assert (agents_dir / "testinline-task.md").exists()
        assert not (agents_dir / "crew-testinline-p1.md").exists()
        assert not (agents_dir / "crew-testinline-p2.md").exists()
        assert not (agents_dir / "crew-testinline-p3.md").exists()
        # Orchestrator plan contains "(orchestrator-direct)" for phase 2
        orch_content = orchestrator_path.read_text()
        assert "(orchestrator-direct)" in orch_content


def test_corrector_agent_generated_for_multi_phase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Multi-phase plan generates corrector agent alongside task agent."""
    setup_git_repo(tmp_path)
    setup_baseline_agents(tmp_path)
    monkeypatch.chdir(tmp_path)

    agents_dir = tmp_path / ".claude" / "agents"
    steps_dir = tmp_path / "plans" / "testgeneral" / "steps"
    orchestrator_path = tmp_path / "plans" / "testgeneral" / "orchestrator-plan.md"
    runbook_path = tmp_path / "plans" / "testgeneral" / "runbook.md"

    metadata, body = parse_frontmatter(_RUNBOOK_2PHASE_GENERAL)
    sections = extract_sections(body)
    cycles = extract_cycles(body)
    phase_models = extract_phase_models(body)
    phase_preambles = extract_phase_preambles(body)

    result = validate_and_create(
        runbook_path,
        sections,
        "testgeneral",
        agents_dir=agents_dir,
        steps_dir=steps_dir,
        orchestrator_path=orchestrator_path,
        metadata=metadata,
        cycles=cycles,
        phase_models=phase_models,
        phase_preambles=phase_preambles,
    )

    assert result is True

    # Corrector agent created alongside task agent
    corrector = agents_dir / "testgeneral-corrector.md"
    assert corrector.exists(), "testgeneral-corrector.md not found"

    content = corrector.read_text()

    # Uses corrector baseline body
    assert "Corrector" in content

    # Always model: sonnet
    assert "model: sonnet" in content

    # Contains Plan Context (design + outline)
    assert "# Plan Context" in content

    # Corrector-specific scope footer
    assert "Review ONLY the phase checkpoint" in content


def test_corrector_agent_skipped_for_single_phase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Single non-inline phase runbook: no corrector agent created."""
    setup_git_repo(tmp_path)
    setup_baseline_agents(tmp_path)
    monkeypatch.chdir(tmp_path)

    agents_dir = tmp_path / ".claude" / "agents"
    steps_dir = tmp_path / "plans" / "testsingle" / "steps"
    orchestrator_path = tmp_path / "plans" / "testsingle" / "orchestrator-plan.md"
    runbook_path = tmp_path / "plans" / "testsingle" / "runbook.md"

    metadata, body = parse_frontmatter(_RUNBOOK_1PHASE_GENERAL)
    sections = extract_sections(body)
    cycles = extract_cycles(body)
    phase_models = extract_phase_models(body)
    phase_preambles = extract_phase_preambles(body)

    result = validate_and_create(
        runbook_path,
        sections,
        "testsingle",
        agents_dir=agents_dir,
        steps_dir=steps_dir,
        orchestrator_path=orchestrator_path,
        metadata=metadata,
        cycles=cycles,
        phase_models=phase_models,
        phase_preambles=phase_preambles,
    )

    assert result is True
    assert not (agents_dir / "testsingle-corrector.md").exists()
