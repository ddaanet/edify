"""Tests for phase numbering (RC-3) and model propagation (RC-1)."""

import importlib.util
import re
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
generate_default_orchestrator = _mod.generate_default_orchestrator
validate_and_create = _mod.validate_and_create

# Phase 3 has no model annotation — Step 3.1 resolves via frontmatter model: sonnet.
# This exercises the frontmatter-fallback path in validate_and_create().
MIXED_RUNBOOK_5PHASE = """\
---
type: mixed
model: sonnet
name: test-runbook
---

### Phase 1: Core behavior (type: general, model: sonnet)

## Step 1.1: First step

Step 1.1 content.

## Step 1.2: Second step

Step 1.2 content.

### Phase 2: TDD cycles (type: tdd, model: sonnet)

## Cycle 2.1: First cycle

**RED Phase:**
Test for cycle 2.1.
**GREEN Phase:**
Impl for cycle 2.1.
**Stop/Error Conditions:** STOP if unexpected.

## Cycle 2.2: Second cycle

**RED Phase:**
Test for cycle 2.2.
**GREEN Phase:**
Impl for cycle 2.2.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 3: Cleanup (type: general)

## Step 3.1: Cleanup step

Cleanup content.

### Phase 4: Advanced (type: tdd, model: opus)

## Cycle 4.1: Advanced cycle

**RED Phase:**
Test for cycle 4.1.
**GREEN Phase:**
Impl for cycle 4.1.
**Stop/Error Conditions:** STOP if unexpected.

### Phase 5: Documentation (type: inline)

- Update documentation
- Write release notes
"""


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


class TestModelPropagation:
    """extract_phase_models extracts per-phase model overrides from headers."""

    def test_extract_phase_models_from_headers(self) -> None:
        """Returns {phase_num: model} for phases with model annotation only."""
        content = (
            "### Phase 1: Core behavior (type: tdd, model: sonnet)\n\n"
            "Cycle 1.1: Test thing\n\n"
            "### Phase 2: Infrastructure (type: general)\n\n"
            "Step 2.1: Setup\n\n"
            "### Phase 3: Refinement (type: tdd, model: opus)\n\n"
            "Cycle 3.1: Refine\n"
        )

        result = extract_phase_models(content)

        assert result == {1: "sonnet", 3: "opus"}
        assert 2 not in result

    def test_phase_model_overrides_frontmatter(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Phase model overrides frontmatter default in generated step files."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        result, steps_dir = _run_validate(
            tmp_path,
            """\
---
type: tdd
model: haiku
name: override-test
---

### Phase 1: Core (type: tdd, model: sonnet)

## Cycle 1.1: Test override

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.
""",
            "override-test",
        )

        assert result is True
        step_file = steps_dir / "step-1-1.md"
        assert step_file.exists()
        content = step_file.read_text()
        assert "**Execution Model**: sonnet" in content, (
            f"Expected 'sonnet' but got haiku in step file. Content:\n{content[:500]}"
        )

    def test_step_model_overrides_phase_model(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Step body model overrides phase model and frontmatter model."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        result, steps_dir = _run_validate(
            tmp_path,
            """\
---
type: tdd
model: haiku
name: step-override-test
---

### Phase 1: Core (type: tdd, model: sonnet)

## Cycle 1.1: Test step override

**Execution Model**: opus
**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.
""",
            "step-override-test",
        )

        assert result is True
        step_file = steps_dir / "step-1-1.md"
        assert step_file.exists()
        content = step_file.read_text()
        assert "**Execution Model**: opus" in content, (
            f"Expected step override 'opus', got phase/frontmatter model.\n"
            f"{content[:500]}"
        )

    def test_missing_model_produces_error(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Missing model at all levels causes error, no step files written."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        result, steps_dir = _run_validate(
            tmp_path,
            """\
---
type: tdd
name: no-model-test
---

### Phase 1: Core (type: tdd)

## Cycle 1.1: Test without model

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.
""",
            "no-model-test",
        )

        assert result is False, "Expected False when no model specified at any level"
        captured = capsys.readouterr()
        assert "model" in captured.err.lower(), (
            f"Expected 'model' in stderr. Got: {captured.err!r}"
        )
        step_files = list(steps_dir.glob("*.md")) if steps_dir.exists() else []
        assert step_files == [], f"Expected no step files written, found: {step_files}"

    def test_assembly_frontmatter_uses_detected_model(self, tmp_path: Path) -> None:
        """Frontmatter model comes from phase header, not hardcoded haiku."""
        phase1 = tmp_path / "runbook-phase-1.md"
        phase1.write_text(
            "### Phase 1: Core (type: tdd, model: sonnet)\n\n"
            "## Cycle 1.1: Test thing\n\n"
            "**RED Phase:**\nTest.\n"
            "**GREEN Phase:**\nImpl.\n"
            "**Stop/Error Conditions:** STOP if unexpected."
        )

        content, _ = assemble_phase_files(tmp_path)

        assert content is not None
        metadata, _ = parse_frontmatter(content)
        got = metadata.get("model")
        assert got == "sonnet", (
            f"Expected model 'sonnet' from phase header, got '{got}'. "
            f"Full frontmatter: {content[:200]}"
        )


class TestPhaseNumbering:
    """Phase header injection in assemble_phase_files."""

    def test_assembly_injects_phase_headers_when_absent(self, tmp_path: Path) -> None:
        """Headers injected from filenames when absent from phase files."""
        phase1 = tmp_path / "runbook-phase-1.md"
        phase1.write_text("## Step 1.1: Do thing\n\nStep content.")

        phase2 = tmp_path / "runbook-phase-2.md"
        phase2.write_text(
            "## Cycle 2.1: Test thing\n\n"
            "**RED Phase:**\nTest.\n"
            "**GREEN Phase:**\nImpl.\n"
            "**Stop/Error Conditions:** STOP if unexpected."
        )

        phase3 = tmp_path / "runbook-phase-3.md"
        phase3.write_text("## Step 3.1: Final thing\n\nFinal content.")

        content, _ = assemble_phase_files(tmp_path)

        assert content is not None
        p1 = content.index("### Phase 1:")
        p2 = content.index("### Phase 2:")
        p3 = content.index("### Phase 3:")
        assert p1 < p2 < p3

    def test_assembly_preserves_existing_phase_headers(self, tmp_path: Path) -> None:
        """Existing phase headers not duplicated during assembly."""
        phase1 = tmp_path / "runbook-phase-1.md"
        phase1.write_text(
            "### Phase 1: Core behavior (type: tdd, model: sonnet)\n\n"
            "## Cycle 1.1: Test\n\n"
            "**RED Phase:**\nTest.\n"
            "**GREEN Phase:**\nImpl.\n"
            "**Stop/Error Conditions:** STOP if unexpected."
        )

        phase2 = tmp_path / "runbook-phase-2.md"
        phase2.write_text(
            "### Phase 2: Infrastructure (type: general)\n\n"
            "## Step 2.1: Setup\n\n"
            "Setup content."
        )

        phase3 = tmp_path / "runbook-phase-3.md"
        phase3.write_text("### Phase 3: Cleanup (type: inline)\n\n- Clean up resources")

        content, _ = assemble_phase_files(tmp_path)

        assert content is not None
        for header in [
            "### Phase 1: Core behavior (type: tdd, model: sonnet)",
            "### Phase 2: Infrastructure (type: general)",
            "### Phase 3: Cleanup (type: inline)",
        ]:
            assert content.count(header) == 1, f"Expected exactly one: {header}"

    def test_mixed_runbook_phase_metadata_and_orchestrator_correct(self) -> None:
        """Phase metadata and orchestrator correct with phase headers."""
        _, body = parse_frontmatter(MIXED_RUNBOOK_5PHASE)
        sections = extract_sections(body)
        cycles = extract_cycles(body)

        step_phases = sections["step_phases"]
        assert step_phases["1.1"] == 1
        assert step_phases["1.2"] == 1
        assert step_phases["3.1"] == 3

        cycle_by_num = {c["number"]: c for c in cycles}
        assert cycle_by_num["2.1"]["major"] == 2
        assert cycle_by_num["2.2"]["major"] == 2
        assert cycle_by_num["4.1"]["major"] == 4

        inline_phases = sections["inline_phases"]
        assert 5 in inline_phases

        orch = generate_default_orchestrator(
            "test-runbook",
            cycles=cycles,
            steps=sections["steps"],
            step_phases=step_phases,
            inline_phases=inline_phases,
        )

        pb_matches = re.findall(r"Last item of phase (\d+)", orch)
        assert pb_matches[0] == "1", (
            f"First PHASE_BOUNDARY should be phase 1, got {pb_matches}"
        )
        assert pb_matches[1] == "2", (
            f"Second PHASE_BOUNDARY should be phase 2, got {pb_matches}"
        )

        item_pattern = re.compile(r"^## step-(\d+)-(\d+)|^## phase-(\d+)", re.MULTILINE)
        items_found = []
        for m in item_pattern.finditer(orch):
            if m.group(1):
                items_found.append((int(m.group(1)), int(m.group(2))))
            else:
                items_found.append((int(m.group(3)), 0))

        phases_seen = [phase for phase, _ in items_found]
        assert phases_seen == sorted(phases_seen), (
            f"Items not in phase order: {phases_seen}"
        )

        for i in range(len(items_found) - 1):
            p_curr, m_curr = items_found[i]
            p_next, m_next = items_found[i + 1]
            if p_curr == p_next:
                assert m_curr < m_next, (
                    f"Interleaving: {items_found[i]} followed by {items_found[i + 1]}"
                )
