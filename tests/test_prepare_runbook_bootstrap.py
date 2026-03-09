"""Tests for Bootstrap tag support and mixed-type Common Context injection."""

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
generate_default_orchestrator = _mod.generate_default_orchestrator
split_cycle_content = _mod.split_cycle_content
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
        tmp_path / ".claude" / "agents",
        steps_dir,
        tmp_path / "plans" / name / "orchestrator-plan.md",
        metadata,
        cycles,
        phase_models,
    )
    return result, steps_dir


class TestMixedCommonContext:
    """DEFAULT_TDD_COMMON_CONTEXT injection for mixed-type runbooks."""

    def test_mixed_assembly_injects_default_common_context(
        self, tmp_path: Path
    ) -> None:
        """Mixed runbook (general first, TDD later) injects Common Context."""
        phase1 = tmp_path / "runbook-phase-1.md"
        phase1.write_text(
            "### Phase 1: Infrastructure (type: general)\n\n"
            "## Step 1.1: Setup\n\nSetup content.\n"
        )

        phase2 = tmp_path / "runbook-phase-2.md"
        phase2.write_text(
            "### Phase 2: Core behavior (type: tdd, model: sonnet)\n\n"
            "## Cycle 2.1: First cycle\n\n"
            "**RED Phase:**\nTest for cycle 2.1.\n"
            "**GREEN Phase:**\nImpl for cycle 2.1.\n"
        )

        content, _ = assemble_phase_files(tmp_path)

        assert content is not None, "Assembly returned None"
        assert "## Common Context" in content, (
            "Mixed runbook missing Common Context injection"
        )
        assert "stop/error conditions" in content.lower(), (
            "Injected Common Context missing stop/error conditions"
        )


class TestBootstrapSplit:
    """split_cycle_content detects Bootstrap marker and returns 3-tuple."""

    def test_split_with_bootstrap(self) -> None:
        """Cycle with Bootstrap returns 3-tuple with bootstrap content."""
        content = (
            "**Bootstrap:** Create stub module with default return.\n\n"
            "---\n\n"
            "**RED Phase:**\nWrite test.\n"
            "**GREEN Phase:**\nImplement."
        )

        bootstrap, red, green = split_cycle_content(content)

        assert "Create stub" in bootstrap
        assert "RED Phase" in red
        assert "GREEN Phase" in green

    def test_split_without_bootstrap(self) -> None:
        """Cycle without Bootstrap returns empty bootstrap in 3-tuple."""
        content = "**RED Phase:**\nWrite test.\n**GREEN Phase:**\nImplement."

        bootstrap, red, green = split_cycle_content(content)

        assert bootstrap == ""
        assert "RED Phase" in red
        assert "GREEN Phase" in green

    def test_split_bootstrap_missing_separator(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Bootstrap marker without --- separator: empty bootstrap, warning emitted."""
        content = (
            "**Bootstrap:** Create stub.\n"
            "**RED Phase:**\nWrite test.\n"
            "**GREEN Phase:**\nImplement."
        )

        bootstrap, red, green = split_cycle_content(content)

        assert bootstrap == "", "Bootstrap empty when separator missing"
        assert "Bootstrap" in red, (
            "Bootstrap text leaks into RED when separator missing"
        )
        assert "GREEN Phase" in green
        assert "WARNING" in capsys.readouterr().err


class TestBootstrapStepFiles:
    """Bootstrap cycles generate 3 step files (bootstrap + test + impl)."""

    def test_bootstrap_generates_three_step_files(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Cycle with Bootstrap produces bootstrap, test, and impl files."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        result, steps_dir = _run_validate(
            tmp_path,
            """\
---
type: tdd
model: sonnet
name: bootstrap-test
---

### Phase 1: Core (type: tdd, model: sonnet)

## Cycle 1.1: Test bootstrap

**Bootstrap:** Create stub module with default return.

---

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.
""",
            "bootstrap-test",
        )

        assert result is True
        assert (steps_dir / "step-1-1-bootstrap.md").exists(), (
            "Missing bootstrap step file"
        )
        assert (steps_dir / "step-1-1-test.md").exists(), "Missing test step file"
        assert (steps_dir / "step-1-1-impl.md").exists(), "Missing impl step file"

        bootstrap_content = (steps_dir / "step-1-1-bootstrap.md").read_text()
        assert "Create stub" in bootstrap_content

    def test_no_bootstrap_generates_two_step_files(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Cycle without Bootstrap produces only test and impl step files."""
        setup_git_repo(tmp_path)
        setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        result, steps_dir = _run_validate(
            tmp_path,
            """\
---
type: tdd
model: sonnet
name: no-bootstrap-test
---

### Phase 1: Core (type: tdd, model: sonnet)

## Cycle 1.1: Test without bootstrap

**RED Phase:**
Write a test.
**GREEN Phase:**
Implement it.
**Stop/Error Conditions:** STOP if unexpected.
""",
            "no-bootstrap-test",
        )

        assert result is True
        assert (steps_dir / "step-1-1-test.md").exists()
        assert (steps_dir / "step-1-1-impl.md").exists()
        assert not (steps_dir / "step-1-1-bootstrap.md").exists(), (
            "Bootstrap file should not exist for cycle without Bootstrap section"
        )


class TestBootstrapOrchestrator:
    """Orchestrator plan includes BOOTSTRAP role items for bootstrap cycles."""

    def test_orchestrator_includes_bootstrap_items(self) -> None:
        """Cycles with Bootstrap produce BOOTSTRAP entries in orchestrator."""
        cycles = [
            {
                "major": 1,
                "minor": 1,
                "number": "1.1",
                "title": "Test bootstrap",
                "content": (
                    "**Bootstrap:** Create stub.\n\n---\n\n"
                    "**RED Phase:**\nTest.\n"
                    "**GREEN Phase:**\nImpl.\n"
                    "**Stop/Error Conditions:** STOP."
                ),
            }
        ]

        orch = generate_default_orchestrator("test-orch", cycles=cycles)

        assert "BOOTSTRAP" in orch, "Orchestrator missing BOOTSTRAP role"
        # BOOTSTRAP should appear before TEST
        bootstrap_pos = orch.index("BOOTSTRAP")
        test_pos = orch.index("TEST")
        assert bootstrap_pos < test_pos, (
            "BOOTSTRAP should appear before TEST in orchestrator"
        )

    def test_orchestrator_no_bootstrap_unchanged(self) -> None:
        """Cycles without Bootstrap produce only TEST + IMPLEMENT entries."""
        cycles = [
            {
                "major": 1,
                "minor": 1,
                "number": "1.1",
                "title": "No bootstrap",
                "content": (
                    "**RED Phase:**\nTest.\n"
                    "**GREEN Phase:**\nImpl.\n"
                    "**Stop/Error Conditions:** STOP."
                ),
            }
        ]

        orch = generate_default_orchestrator("test-orch", cycles=cycles)

        assert "BOOTSTRAP" not in orch, (
            "BOOTSTRAP should not appear for cycles without Bootstrap section"
        )
        assert "TEST" in orch
        assert "IMPLEMENT" in orch
