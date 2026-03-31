"""Tests for prepare-runbook.py file reference validation."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "plugin" / "bin" / "prepare-runbook.py"

_spec = importlib.util.spec_from_file_location("prepare_runbook", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

validate_file_references = _mod.validate_file_references


class TestValidateFileReferencesDirectoryAware:
    """Validator skips paths whose parent directory does not exist."""

    def test_warns_when_parent_exists_file_missing(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Path in existing dir but missing file warns."""
        (tmp_path / "src" / "pkg").mkdir(parents=True)
        monkeypatch.chdir(tmp_path)
        sections = {
            "steps": {"1.1": "Edit `src/pkg/typo.py` with fix"},
        }
        warnings = validate_file_references(sections)
        assert len(warnings) == 1
        assert "typo.py" in warnings[0]

    def test_silent_when_parent_missing(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Path in non-existent directory is silent."""
        monkeypatch.chdir(tmp_path)
        sections = {
            "steps": {"1.1": "Ref `zz_nonexistent/handler.py` here"},
        }
        warnings = validate_file_references(sections)
        assert len(warnings) == 0
