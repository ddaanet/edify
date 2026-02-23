"""Integration tests for prepare-runbook.py inline phase support."""

import importlib.util
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

parse_frontmatter = _mod.parse_frontmatter
extract_sections = _mod.extract_sections
extract_cycles = _mod.extract_cycles
validate_and_create = _mod.validate_and_create
derive_paths = _mod.derive_paths


# --- Fixtures ---

MIXED_RUNBOOK = """\
---
name: mixed-test
model: haiku
---

## Common Context

**Project:** test

---

### Phase 1: Contract updates (type: inline)

- Add inline type row to pipeline-contracts.md
- Update eligibility criteria

### Phase 2: Core behavior (type: tdd)

## Cycle 2.1: Load config

**Execution Model**: Sonnet

**RED Phase:**
Test load_config returns dict.
**Expected failure:** ImportError
**Verify RED:** `pytest tests/test_load.py -v`

---

**GREEN Phase:**
Implement load_config.
**Verify GREEN:** `pytest tests/test_load.py -v`

---

**Stop/Error Conditions:** STOP if RED passes unexpectedly.
"""

INLINE_ONLY_RUNBOOK = """\
---
name: inline-only-test
model: haiku
---

## Common Context

**Project:** inline-only test

---

### Phase 1: Type definition (type: inline)

- Update pipeline-contracts.md: add inline row to type table
- Update workflow-optimization.md: replace heuristic

### Phase 2: Planning pipeline (type: inline)

- Update runbook/SKILL.md: add inline expansion path
- Update plan-reviewer.md: add inline detection
"""


class TestFrontmatterInlineType:
    """Verify parse_frontmatter accepts 'inline' as a valid type."""

    def test_inline_type_accepted(self) -> None:
        """Inline type preserved through frontmatter parsing."""
        content = "---\ntype: inline\nname: test\n---\nBody"
        meta, _body = parse_frontmatter(content)
        assert meta["type"] == "inline"

    def test_inline_not_overwritten_to_general(self) -> None:
        """Inline must not be silently downgraded to general."""
        content = "---\ntype: inline\nname: test\n---\nBody"
        meta, _ = parse_frontmatter(content)
        assert meta["type"] == "inline"


class TestMixedRunbookWithInline:
    """Mixed runbook: step files for TDD phases, none for inline."""

    def test_auto_detects_mixed_with_inline(self) -> None:
        """Auto-detection treats inline-tagged phases correctly."""
        _meta, body = parse_frontmatter(MIXED_RUNBOOK)
        _sections = extract_sections(body)
        cycles = extract_cycles(body)

        # Has cycles from Phase 2 (TDD)
        assert len(cycles) == 1
        assert cycles[0]["number"] == "2.1"

    def test_step_files_only_for_tdd_phases(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Inline phases must NOT produce step files; TDD phases must."""
        _setup_git_repo(tmp_path)
        _setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        plan_dir = tmp_path / "plans" / "mixed-test"
        plan_dir.mkdir(parents=True)
        runbook_path = plan_dir / "runbook.md"
        runbook_path.write_text(MIXED_RUNBOOK)

        name, agent_path, steps_dir, orch_path = derive_paths(runbook_path)
        meta, body = parse_frontmatter(MIXED_RUNBOOK)
        sections = extract_sections(body)
        cycles = extract_cycles(body)

        # Auto-detect type (mirrors main() logic)
        has_inline = bool(sections.get("inline_phases"))
        if cycles and (sections["steps"] or has_inline):
            meta["type"] = "mixed"
        elif cycles:
            meta["type"] = "tdd"
        elif has_inline and not sections["steps"]:
            meta["type"] = "inline"

        result = validate_and_create(
            runbook_path,
            sections,
            name,
            tmp_path / agent_path,
            tmp_path / steps_dir,
            tmp_path / orch_path,
            meta,
            cycles,
        )
        assert result is True

        step_files = sorted((tmp_path / steps_dir).glob("*.md"))
        step_names = [f.name for f in step_files]
        assert "step-2-1.md" in step_names
        assert not any("phase-1" in n or "inline" in n for n in step_names)

    def test_orchestrator_plan_marks_inline(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Orchestrator plan must have 'Execution: inline' for inline phases."""
        _setup_git_repo(tmp_path)
        _setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        plan_dir = tmp_path / "plans" / "mixed-test"
        plan_dir.mkdir(parents=True)
        runbook_path = plan_dir / "runbook.md"
        runbook_path.write_text(MIXED_RUNBOOK)

        name, agent_path, steps_dir, orch_path = derive_paths(runbook_path)
        meta, body = parse_frontmatter(MIXED_RUNBOOK)
        sections = extract_sections(body)
        cycles = extract_cycles(body)

        has_inline = bool(sections.get("inline_phases"))
        if cycles and (sections["steps"] or has_inline):
            meta["type"] = "mixed"
        elif cycles:
            meta["type"] = "tdd"

        validate_and_create(
            runbook_path,
            sections,
            name,
            tmp_path / agent_path,
            tmp_path / steps_dir,
            tmp_path / orch_path,
            meta,
            cycles,
        )

        orch_content = (tmp_path / orch_path).read_text()
        assert "Execution: inline" in orch_content


class TestInlineOnlyRunbook:
    """All-inline runbook: no step files at all."""

    def test_no_step_files_generated(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """All-inline runbook produces zero step files."""
        _setup_git_repo(tmp_path)
        _setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        plan_dir = tmp_path / "plans" / "inline-only-test"
        plan_dir.mkdir(parents=True)
        runbook_path = plan_dir / "runbook.md"
        runbook_path.write_text(INLINE_ONLY_RUNBOOK)

        name, agent_path, steps_dir, orch_path = derive_paths(runbook_path)
        meta, body = parse_frontmatter(INLINE_ONLY_RUNBOOK)
        sections = extract_sections(body)
        cycles = extract_cycles(body)

        has_inline = bool(sections.get("inline_phases"))
        if has_inline and not sections["steps"] and not cycles:
            meta["type"] = "inline"

        result = validate_and_create(
            runbook_path,
            sections,
            name,
            tmp_path / agent_path,
            tmp_path / steps_dir,
            tmp_path / orch_path,
            meta,
            cycles,
        )
        assert result is True

        step_files = list((tmp_path / steps_dir).glob("*.md"))
        assert len(step_files) == 0

    def test_orchestrator_plan_all_inline(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """All-inline orchestrator plan has no step file references."""
        _setup_git_repo(tmp_path)
        _setup_baseline_agents(tmp_path)
        monkeypatch.chdir(tmp_path)

        plan_dir = tmp_path / "plans" / "inline-only-test"
        plan_dir.mkdir(parents=True)
        runbook_path = plan_dir / "runbook.md"
        runbook_path.write_text(INLINE_ONLY_RUNBOOK)

        name, agent_path, steps_dir, orch_path = derive_paths(runbook_path)
        meta, body = parse_frontmatter(INLINE_ONLY_RUNBOOK)
        sections = extract_sections(body)
        cycles = extract_cycles(body)

        has_inline = bool(sections.get("inline_phases"))
        if has_inline and not sections["steps"] and not cycles:
            meta["type"] = "inline"

        validate_and_create(
            runbook_path,
            sections,
            name,
            tmp_path / agent_path,
            tmp_path / steps_dir,
            tmp_path / orch_path,
            meta,
            cycles,
        )

        orch_content = (tmp_path / orch_path).read_text()
        assert "Execution: inline" in orch_content
        assert "steps/step-" not in orch_content


# --- Helpers ---


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

    artisan = agents_dir / "artisan.md"
    artisan.write_text("---\nname: artisan\n---\n# Artisan\nBaseline agent.")

    test_driver = agents_dir / "test-driver.md"
    test_driver.write_text(
        "---\nname: test-driver\n---\n# Test Driver\nBaseline TDD agent."
    )
