"""Tests for assemble_phase_files phase header injection (RC-3 fix)."""

import importlib.util
import re
import subprocess
from pathlib import Path

import pytest

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


def _setup_git_repo(tmp_path: Path) -> None:
    """Initialize a git repo in tmp_path for git add in validate_and_create."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=False)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )


def _setup_baseline_agents(tmp_path: Path) -> None:
    """Create minimal baseline agent files that prepare-runbook.py reads."""
    agents_dir = tmp_path / "agent-core" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    quiet_task = agents_dir / "quiet-task.md"
    quiet_task.write_text("---\nname: quiet-task\n---\n# Quiet Task\nBaseline agent.")

    tdd_task = agents_dir / "tdd-task.md"
    tdd_task.write_text("---\nname: tdd-task\n---\n# TDD Task\nBaseline TDD agent.")


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
        _setup_git_repo(tmp_path)
        _setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        runbook_content = """\
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
"""
        runbook_file = tmp_path / "runbook.md"
        runbook_file.write_text(runbook_content)

        metadata, body = parse_frontmatter(runbook_content)
        sections = extract_sections(body)
        cycles = extract_cycles(body)
        phase_models = extract_phase_models(body)
        metadata["type"] = "tdd"

        agent_path = tmp_path / ".claude" / "agents" / "override-test-task.md"
        steps_dir = tmp_path / "plans" / "override-test" / "steps"
        orchestrator_path = (
            tmp_path / "plans" / "override-test" / "orchestrator-plan.md"
        )

        result = validate_and_create(
            runbook_file,
            sections,
            "override-test",
            agent_path,
            steps_dir,
            orchestrator_path,
            metadata,
            cycles,
            phase_models,
        )

        assert result is True
        step_file = steps_dir / "step-1-1.md"
        assert step_file.exists()
        content = step_file.read_text()
        assert "**Execution Model**: sonnet" in content, (
            f"Expected 'sonnet' but got haiku in step file. Content:\n{content[:500]}"
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
        assert "### Phase 1:" in content
        assert "### Phase 2:" in content
        assert "### Phase 3:" in content

        p1_pos = content.index("### Phase 1:")
        p2_pos = content.index("### Phase 2:")
        p3_pos = content.index("### Phase 3:")
        assert p1_pos < p2_pos < p3_pos

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
        assert content.count("### Phase 1:") == 1
        assert content.count("### Phase 2:") == 1
        assert content.count("### Phase 3:") == 1
        assert "### Phase 1: Core behavior (type: tdd, model: sonnet)" in content
        assert "### Phase 2: Infrastructure (type: general)" in content
        assert "### Phase 3: Cleanup (type: inline)" in content

    def test_mixed_runbook_phase_metadata_and_orchestrator_correct(self) -> None:
        """Phase metadata and orchestrator correct with phase headers."""
        _, body = parse_frontmatter(MIXED_RUNBOOK_5PHASE)
        sections = extract_sections(body)
        cycles = extract_cycles(body)

        # Phase metadata assertions
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

        # Orchestrator plan assertions
        orch = generate_default_orchestrator(
            "test-runbook",
            cycles=cycles,
            steps=sections["steps"],
            step_phases=step_phases,
            inline_phases=inline_phases,
        )

        # PHASE_BOUNDARY labels reference correct phase numbers
        pb_matches = re.findall(r"Last item of phase (\d+)", orch)
        assert pb_matches[0] == "1", (
            f"First PHASE_BOUNDARY should be phase 1, got {pb_matches}"
        )
        assert pb_matches[1] == "2", (
            f"Second PHASE_BOUNDARY should be phase 2, got {pb_matches}"
        )

        # Items appear in phase order (no interleaving)
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

        # No interleaving: within each phase, minor numbers monotonically increase
        for i in range(len(items_found) - 1):
            p_curr, m_curr = items_found[i]
            p_next, m_next = items_found[i + 1]
            if p_curr == p_next:
                assert m_curr < m_next, (
                    f"Interleaving: {items_found[i]} followed by {items_found[i + 1]}"
                )
