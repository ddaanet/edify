"""Tests for plan context embedding in the task agent (design, outline)."""

import importlib.util
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


_RUNBOOK_WITH_OUTLINE = """\
---
type: general
model: sonnet
name: testoutline
---

## Common Context

Shared info.

## Outline

Step 1: Do the first thing.
Step 2: Do the second thing.

### Phase 1: Work (type: general)

## Step 1.1: Do work

**Execution Model**: sonnet

Work content here.
"""


def _run_validate(
    tmp_path: Path,
    runbook_text: str,
    plan_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    """Run validate_and_create for runbook text; return agent file content."""
    setup_git_repo(tmp_path)
    setup_baseline_agents(tmp_path)
    monkeypatch.chdir(tmp_path)

    agents_dir = tmp_path / ".claude" / "agents"
    plan_dir = tmp_path / "plans" / plan_name
    steps_dir = plan_dir / "steps"
    orchestrator_path = plan_dir / "orchestrator-plan.md"
    runbook_path = plan_dir / "runbook.md"

    metadata, body = parse_frontmatter(runbook_text)
    sections = extract_sections(body)
    cycles = extract_cycles(body)
    phase_models = extract_phase_models(body)
    phase_preambles = extract_phase_preambles(body)

    result = validate_and_create(
        runbook_path,
        sections,
        plan_name,
        agents_dir=agents_dir,
        steps_dir=steps_dir,
        orchestrator_path=orchestrator_path,
        metadata=metadata,
        cycles=cycles,
        phase_models=phase_models,
        phase_preambles=phase_preambles,
    )
    assert result is True
    return (agents_dir / f"{plan_name}-task.md").read_text()


def test_task_agent_embeds_outline_from_runbook(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Task agent body contains ## Runbook Outline under # Plan Context."""
    plan_dir = tmp_path / "plans" / "testoutline"
    plan_dir.mkdir(parents=True, exist_ok=True)

    content = _run_validate(tmp_path, _RUNBOOK_WITH_OUTLINE, "testoutline", monkeypatch)

    assert "## Runbook Outline" in content
    assert "Step 1: Do the first thing." in content
    assert "Step 2: Do the second thing." in content


def test_task_agent_embeds_outline_from_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When no ## Outline section in runbook, falls back to outline.md file."""
    plan_dir = tmp_path / "plans" / "testgeneral"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "outline.md").write_text("File outline step A.\nFile outline step B.")

    content = _run_validate(
        tmp_path, _RUNBOOK_2PHASE_GENERAL, "testgeneral", monkeypatch
    )

    assert "## Runbook Outline" in content
    assert "File outline step A." in content


def test_task_agent_embeds_outline_priority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Runbook ## Outline section takes precedence over outline.md file."""
    plan_dir = tmp_path / "plans" / "testoutline"
    plan_dir.mkdir(parents=True, exist_ok=True)
    # Write outline.md — should be ignored when runbook has ## Outline
    (plan_dir / "outline.md").write_text("File outline — should not appear.")

    content = _run_validate(tmp_path, _RUNBOOK_WITH_OUTLINE, "testoutline", monkeypatch)

    assert "Step 1: Do the first thing." in content
    assert "File outline — should not appear." not in content


def test_task_agent_embeds_outline_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fallback note included when no outline source exists."""
    plan_dir = tmp_path / "plans" / "testgeneral"
    plan_dir.mkdir(parents=True, exist_ok=True)
    # No outline.md written

    content = _run_validate(
        tmp_path, _RUNBOOK_2PHASE_GENERAL, "testgeneral", monkeypatch
    )

    assert "## Runbook Outline" in content
    assert "No outline found" in content


def test_task_agent_embeds_design_document(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Task agent body embeds design.md under # Plan Context / ## Design."""
    setup_git_repo(tmp_path)
    setup_baseline_agents(tmp_path)
    monkeypatch.chdir(tmp_path)

    # Write a design.md in the plan directory
    plan_dir = tmp_path / "plans" / "testgeneral"
    plan_dir.mkdir(parents=True, exist_ok=True)
    design_content = "# Design\n\nThis is the architecture.\n\nKey decisions here."
    (plan_dir / "design.md").write_text(design_content)

    agents_dir = tmp_path / ".claude" / "agents"
    steps_dir = plan_dir / "steps"
    orchestrator_path = plan_dir / "orchestrator-plan.md"
    runbook_path = plan_dir / "runbook.md"

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
    content = (agents_dir / "testgeneral-task.md").read_text()

    # Plan Context section with Design subsection
    assert "# Plan Context" in content
    assert "## Design" in content

    # Design section contains full design.md text
    assert "This is the architecture." in content
    assert "Key decisions here." in content


def test_task_agent_design_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When design.md absent, agent still generated with fallback note."""
    setup_git_repo(tmp_path)
    setup_baseline_agents(tmp_path)
    monkeypatch.chdir(tmp_path)

    # No design.md written
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
    content = (agents_dir / "testgeneral-task.md").read_text()
    assert "No design document found" in content
