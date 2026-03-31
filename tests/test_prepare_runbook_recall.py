"""Tests for recall artifact resolution in prepare-runbook.py."""

import importlib.util
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest

from tests.pytest_helpers import setup_baseline_agents, setup_git_repo

SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "prepare-runbook.py"

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
        """Invokes edify _recall resolve with all triggers."""
        with patch.object(
            _mod.subprocess,
            "run",
            return_value=_mock_result("# Resolved\ncontent"),
        ) as mock_run:
            result = resolve_recall_entries(["when writing artifacts", "when testing"])
            call_args = mock_run.call_args[0][0]
            assert call_args[:3] == ["edify", "_recall", "resolve"]
            assert "when writing artifacts" in call_args
            assert result == "# Resolved\ncontent"

    def test_returns_empty_on_failure(self) -> None:
        """Subprocess failure returns empty string."""
        with patch.object(_mod.subprocess, "run", return_value=_mock_result(rc=1)):
            assert resolve_recall_entries(["when nonexistent"]) == ""

    def test_returns_empty_on_binary_not_found(self) -> None:
        """FileNotFoundError (missing binary) returns empty string."""
        with patch.object(
            _mod.subprocess, "run", side_effect=FileNotFoundError("edify")
        ):
            assert resolve_recall_entries(["when something"]) == ""


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


def _run_main(monkeypatch: pytest.MonkeyPatch, runbook_path: Path) -> int:
    """Invoke main() via sys.argv, return exit code."""
    monkeypatch.setattr(sys, "argv", ["prepare-runbook", str(runbook_path)])
    try:
        _mod.main()
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    else:
        return 0


class TestRecallInjectionE2E:
    """End-to-end: recall content in generated artifacts via main()."""

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

    MULTI_PHASE_RUNBOOK = dedent("""\
        ---
        model: sonnet
        ---
        ## Common Context

        Shared constraints.

        **Stop/Error Conditions:** Escalate on unexpected failures.

        **Dependencies:** None.

        ### Phase 1: Core logic (type: tdd)

        Phase 1 preamble.

        ## Cycle 1.1: Basic behavior

        ### RED

        Test that basic behavior works.

        ```python
        def test_basic():
            assert True
        ```

        ### GREEN

        Implement basic behavior.

        ### Phase 2: Integration (type: general)

        Phase 2 preamble.

        ## Step 2.1: Wire components

        **Objective**: Connect parts.
        Integration content.
    """)

    def test_shared_recall_in_agent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Shared recall appears in generated agent definition."""
        artifact = ARTIFACT_TEMPLATE.format(
            entries="when writing recall artifacts — keys"
        )
        _setup_e2e(tmp_path, monkeypatch, "rt", self.SIMPLE_RUNBOOK, artifact)
        runbook_path = tmp_path / "plans" / "rt" / "runbook.md"
        with patch.object(
            _mod.subprocess,
            "run",
            return_value=_mock_result("Resolved content."),
        ):
            exit_code = _run_main(monkeypatch, runbook_path)
        assert exit_code == 0
        agent = tmp_path / ".claude" / "agents" / "rt-task.md"
        agent_content = agent.read_text()
        assert "Resolved Recall" in agent_content
        assert "Resolved content" in agent_content

    def test_no_artifact_no_recall(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Without artifact, agent has no Resolved Recall (NFR-3)."""
        _setup_e2e(tmp_path, monkeypatch, "nr", self.SIMPLE_RUNBOOK)
        runbook_path = tmp_path / "plans" / "nr" / "runbook.md"
        exit_code = _run_main(monkeypatch, runbook_path)
        assert exit_code == 0
        agent = tmp_path / ".claude" / "agents" / "nr-task.md"
        assert "Resolved Recall" not in agent.read_text()

    def test_phase_recall_in_step_files(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Phase-tagged recall appears in step files for that phase."""
        entries = (
            "when writing recall artifacts — all phases\n"
            "when editing skill files — phase 2 context (phase 2)"
        )
        artifact = ARTIFACT_TEMPLATE.format(entries=entries)
        _setup_e2e(tmp_path, monkeypatch, "pr", self.MULTI_PHASE_RUNBOOK, artifact)
        runbook_path = tmp_path / "plans" / "pr" / "runbook.md"
        call_count = 0

        def mock_run(cmd: list[str], **_: object) -> subprocess.CompletedProcess[str]:
            nonlocal call_count
            call_count += 1
            # First call resolves shared entries, second resolves phase 2
            return _mock_result(
                "Shared recall content."
                if call_count == 1
                else "Phase 2 recall content."
            )

        with patch.object(_mod.subprocess, "run", side_effect=mock_run):
            exit_code = _run_main(monkeypatch, runbook_path)
        captured = capsys.readouterr()
        assert exit_code == 0, (
            f"main() failed.\nstdout:\n{captured.out}\nstderr:\n{captured.err}"
        )

        # Phase 2 step file should contain phase recall
        steps_dir = tmp_path / "plans" / "pr" / "steps"
        step_files = sorted(steps_dir.glob("step-2-*.md"))
        assert len(step_files) >= 1, (
            f"No phase 2 step files in {list(steps_dir.iterdir())}"
        )
        step_content = step_files[0].read_text()
        assert "Phase Recall" in step_content
        assert "Phase 2 recall content" in step_content

        # Phase 1 step file should NOT contain phase 2 recall
        p1_files = sorted(steps_dir.glob("step-1-*.md"))
        assert len(p1_files) >= 1
        p1_content = p1_files[0].read_text()
        assert "Phase 2 recall content" not in p1_content

        # Shared recall in agent (not phase-specific)
        # Single task agent for all phases
        task_agent = tmp_path / ".claude" / "agents" / "pr-task.md"
        assert "Shared recall content" in task_agent.read_text()
