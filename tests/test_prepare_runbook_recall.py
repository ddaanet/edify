"""Tests for recall artifact resolution in prepare-runbook.py."""

import importlib.util
import subprocess
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "agent-core" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

parse_recall_artifact = _mod.parse_recall_artifact
resolve_recall_entries = _mod.resolve_recall_entries
resolve_recall_for_runbook = _mod.resolve_recall_for_runbook

ARTIFACT_TEMPLATE = """\
# Recall Artifact: Test

## Entry Keys

{entries}
"""


def _mock_result(stdout: str = "", rc: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=rc, stdout=stdout, stderr="")


def _setup_e2e(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    runbook_text: str,
    artifact_text: str | None = None,
) -> Path:
    """Set up e2e test fixtures.

    Creates git repo, baseline agents, plan dir, and optional artifact.
    """
    setup_git_repo(tmp_path)
    setup_baseline_agents(tmp_path)
    monkeypatch.chdir(tmp_path)
    plan_dir = tmp_path / "plans" / name
    plan_dir.mkdir(parents=True)
    (plan_dir / "runbook.md").write_text(runbook_text)
    if artifact_text:
        (plan_dir / "recall-artifact.md").write_text(artifact_text)
    return plan_dir


class TestParseRecallArtifact:
    """Parse recall artifact with optional phase tags."""

    def test_no_artifact_returns_none(self, tmp_path: Path) -> None:
        """Missing artifact file returns None."""
        assert parse_recall_artifact(tmp_path / "x.md") is None

    def test_shared_entries_only(self, tmp_path: Path) -> None:
        """Entries without phase tags are all shared."""
        artifact = tmp_path / "recall-artifact.md"
        entries = (
            "when writing recall artifacts — keys only\n"
            "when editing skill files — safety"
        )
        artifact.write_text(ARTIFACT_TEMPLATE.format(entries=entries))
        shared, phased = parse_recall_artifact(artifact)
        assert len(shared) == 2
        assert "when writing recall artifacts" in shared[0]
        assert "when editing skill files" in shared[1]
        assert phased == {}

    def test_phase_tagged_entries(self, tmp_path: Path) -> None:
        """Entries with (phase N) suffix are phase-tagged."""
        artifact = tmp_path / "recall-artifact.md"
        entries = (
            "when writing recall artifacts — all phases\n"
            "when editing skill files — p2 context (phase 2)\n"
            "when testing patterns — p1 TDD (phase 1)"
        )
        artifact.write_text(ARTIFACT_TEMPLATE.format(entries=entries))
        shared, phased = parse_recall_artifact(artifact)
        assert len(shared) == 1
        assert 1 in phased
        assert 2 in phased
        assert "when testing patterns" in phased[1][0]
        assert "when editing skill files" in phased[2][0]

    def test_null_entry_skipped(self, tmp_path: Path) -> None:
        """Null entry is excluded from triggers."""
        artifact = tmp_path / "recall-artifact.md"
        artifact.write_text(ARTIFACT_TEMPLATE.format(entries="null — no entries"))
        shared, phased = parse_recall_artifact(artifact)
        assert shared == []
        assert phased == {}

    def test_empty_entry_keys_returns_none(self, tmp_path: Path) -> None:
        """Artifact with no entry keys section returns None."""
        artifact = tmp_path / "recall-artifact.md"
        artifact.write_text("# Recall Artifact: Test\n\nNo entries.\n")
        assert parse_recall_artifact(artifact) is None


class TestResolveRecallEntries:
    """Resolve triggers via subprocess."""

    def test_returns_empty_for_no_triggers(self) -> None:
        """Empty trigger list returns empty string."""
        assert resolve_recall_entries([]) == ""

    def test_calls_subprocess_with_triggers(self) -> None:
        """Invokes claudeutils _recall resolve with all triggers."""
        with patch.object(
            _mod.subprocess,
            "run",
            return_value=_mock_result("# Resolved\ncontent"),
        ) as mock_run:
            result = resolve_recall_entries(["when writing artifacts", "when testing"])
            call_args = mock_run.call_args[0][0]
            assert call_args[:3] == ["claudeutils", "_recall", "resolve"]
            assert "when writing artifacts" in call_args
            assert result == "# Resolved\ncontent"

    def test_returns_empty_on_failure(self) -> None:
        """Subprocess failure returns empty string."""
        with patch.object(_mod.subprocess, "run", return_value=_mock_result(rc=1)):
            assert resolve_recall_entries(["when nonexistent"]) == ""


class TestResolveRecallForRunbook:
    """End-to-end recall resolution for a runbook."""

    def _make_plan(self, tmp_path: Path, entries: str) -> Path:
        plan_dir = tmp_path / "plans" / "test-job"
        plan_dir.mkdir(parents=True)
        (plan_dir / "recall-artifact.md").write_text(
            ARTIFACT_TEMPLATE.format(entries=entries)
        )
        runbook = plan_dir / "runbook.md"
        runbook.write_text("")
        return runbook

    def test_no_artifact_returns_empty(self, tmp_path: Path) -> None:
        """Missing artifact returns empty results."""
        runbook = tmp_path / "plans" / "test-job" / "runbook.md"
        runbook.parent.mkdir(parents=True)
        runbook.write_text("")
        shared, phased = resolve_recall_for_runbook(runbook, phase_types={1: "tdd"})
        assert shared == ""
        assert phased == {}

    def test_shared_entries_resolved(self, tmp_path: Path) -> None:
        """Shared entries resolved and returned as shared content."""
        runbook = self._make_plan(tmp_path, "when writing recall artifacts — keys only")
        with patch.object(
            _mod.subprocess,
            "run",
            return_value=_mock_result("Content here."),
        ):
            shared, phased = resolve_recall_for_runbook(
                runbook, phase_types={1: "general"}
            )
        assert "Content here" in shared
        assert phased == {}

    def test_phase_tagged_partitioned(self, tmp_path: Path) -> None:
        """Phase-tagged entries returned in phase dict, not shared."""
        entries = (
            "when writing recall artifacts — all\n"
            "when editing skill files — p2 (phase 2)"
        )
        runbook = self._make_plan(tmp_path, entries)
        call_count = 0

        def mock_run(cmd: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            nonlocal call_count
            call_count += 1
            s = "Shared recall" if call_count == 1 else "Phase 2 recall"
            return _mock_result(s)

        with patch.object(_mod.subprocess, "run", side_effect=mock_run):
            shared, phased = resolve_recall_for_runbook(
                runbook, {1: "tdd", 2: "general"}
            )
        assert "Shared recall" in shared
        assert 2 in phased
        assert "Phase 2 recall" in phased[2]

    def test_nonexistent_phase_errors(self, tmp_path: Path) -> None:
        """Phase tag referencing nonexistent phase returns None."""
        runbook = self._make_plan(tmp_path, "when editing skill files — p3 (phase 3)")
        result = resolve_recall_for_runbook(runbook, {1: "tdd", 2: "general"})
        assert result is None

    def test_inline_phase_errors(self, tmp_path: Path) -> None:
        """Phase tag referencing inline phase returns None."""
        runbook = self._make_plan(tmp_path, "when editing skill files — p2 (phase 2)")
        result = resolve_recall_for_runbook(runbook, {1: "tdd", 2: "inline"})
        assert result is None


class TestRecallInjectionE2E:
    """End-to-end: recall content in generated artifacts."""

    SIMPLE_RUNBOOK = dedent("""\
        ---
        model: sonnet
        ---
        ## Common Context

        Project constraints here.

        ## Step 1.1: Do something

        **Objective**: Test step.
        Step content.
    """)

    def test_shared_recall_in_agent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Shared recall appears in generated agent definition."""
        artifact = ARTIFACT_TEMPLATE.format(
            entries="when writing recall artifacts — keys"
        )
        plan_dir = _setup_e2e(
            tmp_path, monkeypatch, "rt", self.SIMPLE_RUNBOOK, artifact
        )
        runbook = plan_dir / "runbook.md"
        with patch.object(
            _mod.subprocess,
            "run",
            return_value=_mock_result("Resolved content."),
        ):
            content = runbook.read_text()
            metadata, body = _mod.parse_frontmatter(content)
            sections = _mod.extract_sections(body)
            pt = _mod.detect_phase_types(body)
            recall_result = resolve_recall_for_runbook(runbook, pt)
            assert recall_result is not None
            shared_recall, _ = recall_result
            if shared_recall:
                cc = sections.get("common_context") or ""
                sections["common_context"] = (
                    cc + "\n\n## Resolved Recall\n\n" + shared_recall
                )
            result = _mod.validate_and_create(
                runbook,
                sections,
                "rt",
                tmp_path / ".claude" / "agents",
                plan_dir / "steps",
                plan_dir / "orchestrator-plan.md",
                metadata,
                _mod.extract_cycles(body),
                _mod.extract_phase_models(body),
                _mod.extract_phase_preambles(body),
            )
        assert result is True
        agent = tmp_path / ".claude" / "agents" / "crew-rt.md"
        agent_content = agent.read_text()
        assert "Resolved Recall" in agent_content
        assert "Resolved content" in agent_content

    def test_no_artifact_no_recall(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Without artifact, agent has no Resolved Recall (NFR-3)."""
        plan_dir = _setup_e2e(tmp_path, monkeypatch, "nr", self.SIMPLE_RUNBOOK)
        runbook = plan_dir / "runbook.md"
        content = runbook.read_text()
        metadata, body = _mod.parse_frontmatter(content)
        sections = _mod.extract_sections(body)
        pt = _mod.detect_phase_types(body)
        shared, phased = resolve_recall_for_runbook(runbook, pt)
        assert shared == ""
        assert phased == {}
        result = _mod.validate_and_create(
            runbook,
            sections,
            "nr",
            tmp_path / ".claude" / "agents",
            plan_dir / "steps",
            plan_dir / "orchestrator-plan.md",
            metadata,
            _mod.extract_cycles(body),
            _mod.extract_phase_models(body),
            _mod.extract_phase_preambles(body),
        )
        assert result is True
        agent = tmp_path / ".claude" / "agents" / "crew-nr.md"
        assert "Resolved Recall" not in agent.read_text()
