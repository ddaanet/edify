"""Run the bootstrap-venv.sh bats suite as part of pytest.

The plugin's SessionStart bootstrap is a POSIX shell script; its behavior is
covered by ``tests/bootstrap-venv.bats`` (hermetic, uv stubbed). This wrapper
lets ``just test`` / ``just precommit`` run that suite too — the test sentinel
already hashes ``plugin/bin`` and ``plugin/hooks``. bats is a declared dev
dependency, so a missing bats is a hard failure, never a skip.
"""

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BATS_SUITE = REPO_ROOT / "tests" / "bootstrap-venv.bats"


def _bats() -> str:
    """Prefer the npm-provisioned bats, fall back to one on PATH."""
    local = REPO_ROOT / "node_modules" / ".bin" / "bats"
    if local.exists():
        return str(local)
    found = shutil.which("bats")
    assert found, "bats not found — it is a declared dev dependency (run `npm install`)"
    return found


def test_bootstrap_venv_bats() -> None:
    """The bootstrap-venv.sh bats suite passes."""
    result = subprocess.run(
        [_bats(), str(BATS_SUITE)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
