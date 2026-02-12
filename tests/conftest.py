"""Shared pytest fixtures for all tests."""

import subprocess
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from anthropic import Anthropic
from pytest_mock import MockerFixture

from claudeutils.tokens import ModelId


# API Key Management
@pytest.fixture(autouse=True)
def clear_api_key(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Clear ANTHROPIC_API_KEY for all tests except e2e tests.

    This prevents tests from accidentally using real API keys and ensures tests
    are properly mocked. E2e tests marked with @pytest.mark.e2e are skipped to
    allow them to use real API credentials.
    """
    # Skip for e2e tests
    if "e2e" in request.keywords:
        return

    # Clear the API key for all other tests
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


# Project Directory Fixture
@pytest.fixture
def temp_project_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    """Create temporary project and history directories.

    Returns:
        Tuple of (project_dir, history_dir) with mocked get_project_history_dir.
    """
    project = tmp_path / "myproject"
    project.mkdir()

    history_dir = tmp_path / ".claude" / "projects" / "-tmp-myproject"
    history_dir.mkdir(parents=True)

    def mock_get_history(proj: str) -> Path:
        return history_dir

    # Patch for discovery module (used in test_discovery and test_agent_files)
    monkeypatch.setattr(
        "claudeutils.discovery.get_project_history_dir", mock_get_history
    )

    return project, history_dir


# History Directory Fixture for extraction tests
@pytest.fixture
def temp_history_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path]:
    """Mock history directory for extraction and agent file testing.

    Patches both extraction and discovery modules for recursive testing.

    Returns:
        Tuple of (project_dir, history_dir) with mocked get_project_history_dir.
    """
    history_dir = tmp_path / "history"
    history_dir.mkdir()

    def mock_get_history(proj: str) -> Path:
        return history_dir

    # Patch both modules for recursive extraction testing
    monkeypatch.setattr(
        "claudeutils.extraction.get_project_history_dir", mock_get_history
    )
    monkeypatch.setattr(
        "claudeutils.discovery.get_project_history_dir", mock_get_history
    )

    return tmp_path / "project", history_dir


# Token Counter Fixtures


@pytest.fixture
def mock_anthropic_client(mocker: MockerFixture) -> Callable[..., Mock]:
    """Create factory fixture for mocking Anthropic client.

    Returns function accepting token_count (int, default 5) or side_effect
    parameters. Creates mock with spec=Anthropic, patches
    claudeutils.tokens.Anthropic.
    """

    def factory(
        token_count: int = 5,
        side_effect: object = None,
    ) -> Mock:
        """Create and return mock Anthropic client."""
        mock_client = Mock(spec=Anthropic)
        mock_response = Mock()

        if side_effect is not None:
            mock_client.messages.count_tokens.side_effect = side_effect
        else:
            mock_response.input_tokens = token_count
            mock_client.messages.count_tokens.return_value = mock_response

        mocker.patch(
            "claudeutils.tokens.Anthropic", return_value=mock_client, autospec=True
        )
        return mock_client

    return factory


@pytest.fixture
def test_markdown_file(tmp_path: Path) -> Callable[..., Path]:
    """Factory fixture for creating test markdown files.

    Returns function accepting content (str, default "Hello world") and filename
    (str, default "test.md").
    """

    def factory(content: str = "Hello world", filename: str = "test.md") -> Path:
        """Create and return test file path."""
        test_file = tmp_path / filename
        test_file.write_text(content)
        return test_file

    return factory


@pytest.fixture
def mock_models_api(mocker: MockerFixture) -> Callable[..., Mock]:
    """Create factory fixture for mocking models API.

    Returns function accepting models list (list of dicts with id/created_at) or
    raise_error. Creates mock client with spec=Anthropic, mocks
    client.models.list().
    """

    def factory(
        models: list[dict[str, str]] | None = None,
        raise_error: Exception | None = None,
    ) -> Mock:
        """Create and return mock Anthropic client with models API."""
        if models is None:
            models = [
                {
                    "id": "claude-sonnet-4-5-20250929",
                    "created_at": "2025-09-29T00:00:00Z",
                }
            ]

        mock_client = Mock(spec=Anthropic)

        if raise_error is not None:
            mock_client.models.list.side_effect = raise_error
        else:
            # Convert dict models to mock objects with id and created_at attributes
            mock_models = []
            for model_dict in models:
                mock_model = Mock()
                mock_model.id = model_dict["id"]
                mock_model.created_at = datetime.fromisoformat(model_dict["created_at"])
                mock_models.append(mock_model)
            mock_client.models.list.return_value = mock_models

        return mock_client

    return factory


@pytest.fixture
def mock_token_counting(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
) -> Callable[..., None]:
    """Create factory fixture for mocking token counting in CLI tests.

    Accepts model_id (str) and counts (int or list). Patches resolve_model_alias
    and count_tokens_for_file, and sets a fake API key for authentication.
    """

    def factory(
        model_id: str = "claude-sonnet-4-5-20250929", counts: int | list[int] = 5
    ) -> None:
        """Patch token counting functions for CLI tests."""
        # Set fake API key to pass authentication check
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

        # Mock Anthropic client to avoid instantiation with SOCKS proxy
        mocker.patch("claudeutils.tokens_cli.Anthropic", autospec=True)

        mocker.patch(
            "claudeutils.tokens_cli.resolve_model_alias",
            return_value=ModelId(model_id),
        )

        # Handle both single count and list of counts
        if isinstance(counts, list):
            mocker.patch(
                "claudeutils.tokens_cli.count_tokens_for_file",
                side_effect=counts,
            )
        else:
            mocker.patch(
                "claudeutils.tokens_cli.count_tokens_for_file",
                return_value=counts,
            )

    return factory


@pytest.fixture
def api_key_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove ANTHROPIC_API_KEY from environment."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.fixture
def api_key_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set ANTHROPIC_API_KEY to empty string."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")


@pytest.fixture
def cli_base_mocks(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
) -> dict[str, Mock]:
    """Create base mocks for CLI token tests.

    Returns dict with 'anthropic' and 'resolve' mocks. Does not mock
    count_tokens_for_file to allow real file operations in some tests. Sets a
    fake API key for authentication.
    """
    # Set fake API key to pass authentication check
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")

    return {
        "anthropic": mocker.patch("claudeutils.tokens_cli.Anthropic", autospec=True),
        "resolve": mocker.patch(
            "claudeutils.tokens_cli.resolve_model_alias", autospec=True
        ),
    }


# Markdown Fixtures
@pytest.fixture(autouse=True, scope="session")
def markdown_fixtures_dir() -> Path:
    """Create markdown fixtures directory structure.

    Ensures tests/fixtures/markdown/ directory exists for parametrized test
    cases. Created once per test session.
    """
    fixtures_dir = Path(__file__).parent / "fixtures" / "markdown"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    return fixtures_dir


# Worktree Fixtures
@pytest.fixture
def init_repo() -> Callable[[Path], None]:
    """Return function to initialize git repo with user config and initial
    commit."""

    def _init_repo(repo_path: Path) -> None:
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        (repo_path / "README.md").write_text("test")
        subprocess.run(
            ["git", "add", "README.md"], cwd=repo_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

    return _init_repo


@pytest.fixture
def repo_with_submodule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create git repo with submodule and session files.

    Returns the main repo path. The repo has:
    - Initial commit with README.md
    - agent-core submodule initialized
    - agents/session.md, agents/jobs.md, agents/learnings.md committed
    """
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    monkeypatch.chdir(repo_path)

    # Initialize main repo
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], check=True, capture_output=True
    )

    # Create initial commit
    (repo_path / "README.md").write_text("test")
    subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], check=True, capture_output=True
    )

    # Initialize submodule (agent-core)
    submodule_path = repo_path / "agent-core"
    submodule_path.mkdir()
    subprocess.run(["git", "init"], cwd=submodule_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )
    (submodule_path / "README.md").write_text("submodule")
    subprocess.run(
        ["git", "add", "README.md"], cwd=submodule_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Submodule initial"],
        cwd=submodule_path,
        check=True,
        capture_output=True,
    )

    # Add submodule to main repo
    subprocess.run(
        ["git", "submodule", "add", str(submodule_path), "agent-core"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Add submodule"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Add session files
    agents_dir = repo_path / "agents"
    agents_dir.mkdir()
    (agents_dir / "session.md").write_text("# Session\n")
    (agents_dir / "jobs.md").write_text("# Jobs\n")
    (agents_dir / "learnings.md").write_text("# Learnings\n")
    subprocess.run(["git", "add", "agents/"], check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Add session files"], check=True, capture_output=True
    )

    return repo_path
