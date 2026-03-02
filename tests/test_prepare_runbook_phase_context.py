"""Tests for extract_phase_preambles and phase context injection (RC-2, D-2)."""

import contextlib
import importlib.util
import io
from pathlib import Path

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

extract_phase_preambles = _mod.extract_phase_preambles
parse_frontmatter = _mod.parse_frontmatter
extract_sections = _mod.extract_sections
extract_cycles = _mod.extract_cycles
extract_phase_models = _mod.extract_phase_models
validate_and_create = _mod.validate_and_create


def _run_prepare(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str, content: str
) -> Path:
    """Set up git repo, run validate_and_create, return steps_dir."""
    setup_git_repo(tmp_path)
    setup_baseline_agents(tmp_path)
    monkeypatch.chdir(tmp_path)
    rf = tmp_path / "runbook.md"
    rf.write_text(content)
    metadata, body = parse_frontmatter(content)
    sections = extract_sections(body)
    cycles = extract_cycles(body)
    phase_models = extract_phase_models(body)
    preambles = extract_phase_preambles(body)
    steps_dir = tmp_path / "plans" / name / "steps"
    stderr_buf = io.StringIO()
    with contextlib.redirect_stderr(stderr_buf):
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
            preambles,
        )
    assert result is True, f"validate_and_create failed: {stderr_buf.getvalue()}"
    return steps_dir


class TestPhaseContext:
    """extract_phase_preambles extracts per-phase preamble text."""

    def test_extract_phase_preambles(self) -> None:
        """All phases returned; empty string when no preamble."""
        content = (
            "### Phase 1: Core behavior (type: tdd, model: sonnet)\n\n"
            "RC-1 fix. Prerequisites: foo module exists.\n\n"
            "**Constraints:** No backward-incompatible changes.\n\n"
            "## Cycle 1.1: Test thing\n\n"
            "### Phase 2: Infrastructure (type: general)\n\n"
            "Setup database connections. Verify connectivity.\n\n"
            "## Step 2.1: Configure DB\n\n"
            "### Phase 3: Cleanup (type: tdd, model: sonnet)\n\n"
            "## Cycle 3.1: Clean state\n"
        )
        result = extract_phase_preambles(content)
        assert set(result.keys()) == {1, 2, 3}
        assert "RC-1 fix" in result[1]
        assert "Constraints" in result[1]
        assert "Setup database connections" in result[2]
        assert result[3] == ""
        assert "### Phase 1:" not in result[1]
        assert "## Cycle 1.1:" not in result[1]

    def test_step_and_cycle_files_include_phase_context(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Phase preamble text appears in generated step and cycle files."""
        steps_dir = _run_prepare(
            tmp_path,
            monkeypatch,
            "context-test",
            """\
---
type: mixed
model: sonnet
name: context-test
---

### Phase 1: TDD phase (type: tdd, model: sonnet)

Phase 1 prerequisites: module X exists.

## Cycle 1.1: First cycle

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 2: General phase (type: general, model: sonnet)

Phase 2 constraints: no breaking changes.

## Step 2.1: First step

Step 2.1 content.
""",
        )
        cycle_content = (steps_dir / "step-1-1-test.md").read_text()
        step_content = (steps_dir / "step-2-1.md").read_text()

        assert "## Phase Context" in cycle_content
        assert "Phase 1 prerequisites: module X exists." in cycle_content
        assert "## Phase Context" in step_content
        assert "Phase 2 constraints: no breaking changes." in step_content

        # Verify ordering: metadata BEFORE phase context BEFORE body
        for label, content in [("cycle", cycle_content), ("step", step_content)]:
            meta_pos = content.find("**Plan**:")
            ctx_pos = content.find("## Phase Context")
            body_pos = content.rfind("---\n\n") + 5
            assert meta_pos < ctx_pos, f"{label}: metadata must precede Phase Context"
            assert ctx_pos < body_pos, f"{label}: Phase Context must precede body"

    def test_no_phase_context_when_preamble_empty(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Whitespace-only preamble omits Phase Context section."""
        steps_dir = _run_prepare(
            tmp_path,
            monkeypatch,
            "preamble-test",
            """\
---
type: mixed
model: sonnet
name: preamble-test
---

### Phase 1: Core (type: tdd, model: sonnet)


## Cycle 1.1: Direct start

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 2: Extra (type: general, model: sonnet)

Some preamble here.

## Step 2.1: Thing

Step content.
""",
        )
        cycle_content = (steps_dir / "step-1-1-test.md").read_text()
        step_content = (steps_dir / "step-2-1.md").read_text()

        assert "## Phase Context" not in cycle_content
        assert "## Phase Context" in step_content
        assert "Some preamble here." in step_content


class TestModelPropagation:
    """C1/C2 verification: model propagation and phase numbering."""

    def test_phase_model_overrides_frontmatter(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Phase model: sonnet overrides frontmatter model: haiku in step file."""
        steps_dir = _run_prepare(
            tmp_path,
            monkeypatch,
            "model-test",
            """\
---
type: tdd
model: haiku
name: model-test
---

### Phase 1: Core (type: tdd, model: sonnet)

## Cycle 1.1: First cycle

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.
""",
        )
        content = (steps_dir / "step-1-1-test.md").read_text()
        assert "**Execution Model**: sonnet" in content

    def test_gapped_phase_numbering_preserved(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Phases 1, 3, 5 generate step files with correct phase numbers."""
        steps_dir = _run_prepare(
            tmp_path,
            monkeypatch,
            "gap-test",
            """\
---
type: tdd
model: sonnet
name: gap-test
---

### Phase 1: First (type: tdd, model: sonnet)

## Cycle 1.1: First thing

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 3: Third (type: tdd, model: sonnet)

## Cycle 3.1: Third thing

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 5: Fifth (type: tdd, model: sonnet)

## Cycle 5.1: Fifth thing

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.
""",
        )
        assert (steps_dir / "step-1-1-test.md").exists()
        assert (steps_dir / "step-3-1-test.md").exists()
        assert (steps_dir / "step-5-1-test.md").exists()
        assert not (steps_dir / "step-2-1-test.md").exists()
        assert "**Phase**: 3" in (steps_dir / "step-3-1-test.md").read_text()
        assert "**Phase**: 5" in (steps_dir / "step-5-1-test.md").read_text()


class TestPhaseContextCompleteness:
    """C3 verification: post-cycle content in preambles."""

    def test_post_cycle_content_not_in_preamble(self) -> None:
        """Post-cycle content is not captured in preamble (by design)."""
        content = (
            "### Phase 1: Core (type: tdd, model: sonnet)\n\n"
            "Prerequisites: module X exists.\n\n"
            "## Cycle 1.1: First\n\n"
            "Cycle content.\n\n"
            "## Cycle 1.2: Second\n\n"
            "More content.\n\n"
            "**Completion validation:** All 2 tests pass.\n\n"
            "### Phase 2: Next (type: tdd, model: sonnet)\n\n"
            "## Cycle 2.1: Start\n"
        )
        result = extract_phase_preambles(content)
        assert "Prerequisites: module X exists." in result[1]
        assert "Completion validation" not in result.get(1, "")
