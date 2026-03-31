"""Tests for cycle extraction boundary behavior and provenance metadata."""

import importlib.util
from pathlib import Path

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

extract_cycles = _mod.extract_cycles
extract_sections = _mod.extract_sections
extract_phase_models = _mod.extract_phase_models
extract_phase_preambles = _mod.extract_phase_preambles
parse_frontmatter = _mod.parse_frontmatter
validate_and_create = _mod.validate_and_create


# -- Fixtures ----------------------------------------------------------------

MULTI_PHASE_CONTENT = """\
### Phase 1: Core behavior (type: tdd, model: sonnet)

Phase 1 preamble text.

## Cycle 1.1: First cycle

**RED Phase:**
Test for cycle 1.1.
**GREEN Phase:**
Impl for cycle 1.1.
**Stop/Error Conditions:** STOP if unexpected.

## Cycle 1.2: Last cycle of phase 1

**RED Phase:**
Test for cycle 1.2.
**GREEN Phase:**
Impl for cycle 1.2.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 2: Advanced behavior (type: tdd, model: opus)

Phase 2 preamble with important context.
This should NOT appear in cycle 1.2.

## Cycle 2.1: First cycle of phase 2

**RED Phase:**
Test for cycle 2.1.
**GREEN Phase:**
Impl for cycle 2.1.
**Stop/Error Conditions:** STOP if unexpected.
"""


class TestCycleBoundaryExtraction:
    """extract_cycles terminates on phase headers, not just H2 headers."""

    def test_last_cycle_excludes_next_phase_preamble(self) -> None:
        """Cycle 1.2 content must not contain Phase 2 preamble text."""
        cycles = extract_cycles(MULTI_PHASE_CONTENT)

        cycle_1_2 = next(c for c in cycles if c["number"] == "1.2")

        assert "Phase 2 preamble" not in cycle_1_2["content"]
        assert "should NOT appear" not in cycle_1_2["content"]

    def test_last_cycle_excludes_next_phase_header(self) -> None:
        """Cycle 1.2 content must not contain the Phase 2 header line."""
        cycles = extract_cycles(MULTI_PHASE_CONTENT)

        cycle_1_2 = next(c for c in cycles if c["number"] == "1.2")

        assert "### Phase 2" not in cycle_1_2["content"]

    def test_all_cycles_extracted(self) -> None:
        """All three cycles across both phases are found."""
        cycles = extract_cycles(MULTI_PHASE_CONTENT)

        numbers = [c["number"] for c in cycles]
        assert numbers == ["1.1", "1.2", "2.1"]

    def test_phase_2_cycle_content_intact(self) -> None:
        """Phase 2 cycle content is correctly captured after boundary."""
        cycles = extract_cycles(MULTI_PHASE_CONTENT)

        cycle_2_1 = next(c for c in cycles if c["number"] == "2.1")

        assert "Test for cycle 2.1" in cycle_2_1["content"]

    def test_single_phase_cycles_intact(self) -> None:
        """Single-phase runbook extracts cycles via final-flush path."""
        content = """\
### Phase 1: Core behavior (type: tdd, model: sonnet)

Phase 1 preamble text.

## Cycle 1.1: First cycle

**RED Phase:**
Test for cycle 1.1.
**GREEN Phase:**
Impl for cycle 1.1.
**Stop/Error Conditions:** STOP if unexpected.

## Cycle 1.2: Last cycle

**RED Phase:**
Test for cycle 1.2.
**GREEN Phase:**
Impl for cycle 1.2.
**Stop/Error Conditions:** STOP if unexpected.
"""
        cycles = extract_cycles(content)

        numbers = [c["number"] for c in cycles]
        assert numbers == ["1.1", "1.2"]
        assert "Phase 1 preamble" not in cycles[-1]["content"]
        assert "Test for cycle 1.2" in cycles[-1]["content"]


# -- Bug 2: Provenance metadata path ----------------------------------------

PHASE_ASSEMBLED_RUNBOOK = """\
---
type: tdd
model: sonnet
name: prov-test
---

### Phase 1: Core (type: tdd, model: sonnet)

## Cycle 1.1: First cycle

**RED Phase:**
Test for cycle 1.1.
**GREEN Phase:**
Impl for cycle 1.1.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 2: General (type: general, model: sonnet)

## Step 2.1: A general step

Step 2.1 content.
"""


def _run_with_phase_dir(
    tmp_path: Path, runbook_content: str, name: str
) -> tuple[bool, Path]:
    """Run validate_and_create simulating directory (phase-assembled) input."""
    # Simulate the phase directory existing
    phase_dir = tmp_path / "plans" / name
    phase_dir.mkdir(parents=True, exist_ok=True)
    (phase_dir / "runbook-phase-1.md").write_text("phase 1 source")
    (phase_dir / "runbook-phase-2.md").write_text("phase 2 source")

    # Synthetic runbook.md path (as main() creates it for assembled input)
    rf = phase_dir / "runbook.md"

    metadata, body = parse_frontmatter(runbook_content)
    sections = extract_sections(body)
    cycles = extract_cycles(body)
    phase_models = extract_phase_models(body)
    preambles = extract_phase_preambles(body)
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
        preambles,
        phase_dir=str(phase_dir),
    )
    return result, steps_dir


SINGLE_FILE_RUNBOOK = """\
---
type: tdd
model: sonnet
name: sf-test
---

## Cycle 1.1: First cycle

**RED Phase:**
Test for cycle 1.1.
**GREEN Phase:**
Impl for cycle 1.1.
**Stop/Error Conditions:** STOP if unexpected.
"""


def _run_without_phase_dir(
    tmp_path: Path, runbook_content: str, name: str
) -> tuple[bool, Path]:
    """Run validate_and_create simulating single-file input (no phase_dir)."""
    plan_dir = tmp_path / "plans" / name
    plan_dir.mkdir(parents=True, exist_ok=True)
    rf = plan_dir / "runbook.md"
    rf.write_text(runbook_content)

    metadata, body = parse_frontmatter(runbook_content)
    sections = extract_sections(body)
    cycles = extract_cycles(body)
    phase_models = extract_phase_models(body)
    preambles = extract_phase_preambles(body)
    steps_dir = plan_dir / "steps"
    result = validate_and_create(
        rf,
        sections,
        name,
        tmp_path / ".claude" / "agents",
        steps_dir,
        plan_dir / "orchestrator-plan.md",
        metadata,
        cycles,
        phase_models,
        preambles,
    )
    return result, steps_dir


class TestProvenanceMetadata:
    """Generated step files reference actual source phase file."""

    def test_cycle_file_references_phase_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Cycle Plan field references runbook-phase-1.md, not runbook.md."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        result, steps_dir = _run_with_phase_dir(
            tmp_path, PHASE_ASSEMBLED_RUNBOOK, "prov-test"
        )
        assert result is True

        cycle_file = steps_dir / "step-1-1-test.md"
        content = cycle_file.read_text()

        assert "runbook-phase-1.md" in content
        assert "runbook.md`" not in content

    def test_step_file_references_phase_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Step Plan field references runbook-phase-2.md, not runbook.md."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        result, steps_dir = _run_with_phase_dir(
            tmp_path, PHASE_ASSEMBLED_RUNBOOK, "prov-test"
        )
        assert result is True

        step_file = steps_dir / "step-2-1.md"
        content = step_file.read_text()

        assert "runbook-phase-2.md" in content
        assert "runbook.md`" not in content

    def test_single_file_references_runbook_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Without phase_dir, Plan field references runbook.md directly."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        result, steps_dir = _run_without_phase_dir(
            tmp_path, SINGLE_FILE_RUNBOOK, "sf-test"
        )
        assert result is True

        cycle_file = steps_dir / "step-1-1-test.md"
        content = cycle_file.read_text()

        assert "runbook.md`" in content
        assert "runbook-phase-" not in content
