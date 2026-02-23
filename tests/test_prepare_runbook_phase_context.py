"""Tests for extract_phase_preambles and phase context injection (RC-2, D-2)."""

import importlib.util
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
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        runbook_content = """\
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
"""

        rf = tmp_path / "runbook.md"
        rf.write_text(runbook_content)
        metadata, body = parse_frontmatter(runbook_content)
        sections = extract_sections(body)
        cycles = extract_cycles(body)
        phase_models = extract_phase_models(body)
        phase_preambles = extract_phase_preambles(body)
        steps_dir = tmp_path / "plans" / "context-test" / "steps"
        result = validate_and_create(
            rf,
            sections,
            "context-test",
            tmp_path / ".claude" / "agents",
            steps_dir,
            tmp_path / "plans" / "context-test" / "orchestrator-plan.md",
            metadata,
            cycles,
            phase_models,
            phase_preambles,
        )

        assert result is True

        cycle_file = steps_dir / "step-1-1.md"
        assert cycle_file.exists()
        cycle_content = cycle_file.read_text()

        step_file = steps_dir / "step-2-1.md"
        assert step_file.exists()
        step_content = step_file.read_text()

        assert "## Phase Context" in cycle_content, (
            f"Expected '## Phase Context' in cycle file. Got:\n{cycle_content}"
        )
        assert "Phase 1 prerequisites: module X exists." in cycle_content, (
            f"Expected preamble text in cycle file. Got:\n{cycle_content}"
        )
        assert "## Phase Context" in step_content, (
            f"Expected '## Phase Context' in step file. Got:\n{step_content}"
        )
        assert "Phase 2 constraints: no breaking changes." in step_content, (
            f"Expected preamble text in step file. Got:\n{step_content}"
        )

        # Verify ordering: metadata header BEFORE phase context BEFORE body content
        for filename, content in [("cycle", cycle_content), ("step", step_content)]:
            metadata_pos = content.find("**Plan**:")
            phase_ctx_pos = content.find("## Phase Context")
            # Use rfind to locate the last "---" divider, which precedes body content
            body_pos = content.rfind("---\n\n") + 5

            assert metadata_pos < phase_ctx_pos, (
                f"{filename}: metadata header must precede ## Phase Context"
            )
            assert phase_ctx_pos < body_pos, (
                f"{filename}: ## Phase Context must appear before body content"
            )

    def test_no_phase_context_when_preamble_empty(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Whitespace-only preamble omits Phase Context section."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        runbook_content = """\
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
"""

        rf = tmp_path / "runbook.md"
        rf.write_text(runbook_content)
        metadata, body = parse_frontmatter(runbook_content)
        sections = extract_sections(body)
        cycles = extract_cycles(body)
        phase_models = extract_phase_models(body)
        preambles = extract_phase_preambles(body)
        steps_dir = tmp_path / "plans" / "preamble-test" / "steps"

        assert preambles.get(1, "").strip() == "", (
            f"Phase 1 preamble should be empty after strip, got: {preambles.get(1)!r}"
        )

        result = validate_and_create(
            rf,
            sections,
            "preamble-test",
            tmp_path / ".claude" / "agents",
            steps_dir,
            tmp_path / "plans" / "preamble-test" / "orchestrator-plan.md",
            metadata,
            cycles,
            phase_models,
            preambles,
        )
        assert result is True

        cycle_file = steps_dir / "step-1-1.md"
        assert cycle_file.exists()
        cycle_content = cycle_file.read_text()
        assert "## Phase Context" not in cycle_content, (
            "Whitespace-only preamble injected Phase Context section:\n"
            f"{cycle_content[:500]}"
        )

        step_file = steps_dir / "step-2-1.md"
        assert step_file.exists()
        step_content = step_file.read_text()
        assert "## Phase Context" in step_content, (
            f"Expected Phase Context section in step-2-1.md:\n{step_content[:500]}"
        )
        assert "Some preamble here." in step_content, (
            f"Expected preamble text in step-2-1.md:\n{step_content[:500]}"
        )
