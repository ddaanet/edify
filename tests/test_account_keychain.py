"""Tests for Keychain wrapper."""

from unittest.mock import Mock, patch

from edify.account import Keychain


def test_keychain_find_success() -> None:
    """Test that Keychain.find() returns password when keychain entry exists."""
    # Mock subprocess.run to return successful output from security command
    # Note: -w flag returns just the password without label
    mock_result = Mock()
    mock_result.stdout = b"test-password-value"
    mock_result.returncode = 0

    with patch(
        "edify.account.keychain.subprocess.run", return_value=mock_result
    ) as mock_run:
        # Create Keychain instance and call find
        keychain = Keychain()
        password = keychain.find("test-account", "test-service")

        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once_with(
            [
                "security",
                "find-generic-password",
                "-a",
                "test-account",
                "-s",
                "test-service",
                "-w",
            ],
            capture_output=True,
            text=False,
            check=False,
        )

        # Verify password is extracted and returned
        assert password == "test-password-value"  # noqa: S105


def test_keychain_add() -> None:
    """Test that Keychain.add() calls security add-generic-password command."""
    mock_result = Mock()
    mock_result.returncode = 0

    with patch(
        "edify.account.keychain.subprocess.run", return_value=mock_result
    ) as mock_run:
        # Create Keychain instance and call add
        keychain = Keychain()
        keychain.add("test-account", "test-password", "test-service")

        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once_with(
            [
                "security",
                "add-generic-password",
                "-a",
                "test-account",
                "-s",
                "test-service",
                "-p",
                "test-password",
            ],
            check=False,
        )


def test_keychain_delete() -> None:
    """Test that Keychain.delete() calls security delete-generic-password."""
    mock_result = Mock()
    mock_result.returncode = 0

    with patch(
        "edify.account.keychain.subprocess.run", return_value=mock_result
    ) as mock_run:
        # Create Keychain instance and call delete
        keychain = Keychain()
        keychain.delete("test-account", "test-service")

        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once_with(
            [
                "security",
                "delete-generic-password",
                "-a",
                "test-account",
                "-s",
                "test-service",
            ],
            check=False,
        )


def test_keychain_find_not_found() -> None:
    """Test that Keychain.find() returns None when entry doesn't exist."""
    # Mock subprocess.run to return failure when keychain entry not found
    mock_result = Mock()
    mock_result.stdout = b""
    mock_result.returncode = 1  # Non-zero indicates entry not found

    with patch(
        "edify.account.keychain.subprocess.run", return_value=mock_result
    ) as mock_run:
        # Create Keychain instance and call find
        keychain = Keychain()
        result = keychain.find("nonexistent-account", "nonexistent-service")

        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once_with(
            [
                "security",
                "find-generic-password",
                "-a",
                "nonexistent-account",
                "-s",
                "nonexistent-service",
                "-w",
            ],
            capture_output=True,
            text=False,
            check=False,
        )

        # Verify that find() returns None when entry not found
        assert result is None


def test_keychain_command_not_found() -> None:
    """Test Keychain.find() gracefully handles security command unavailable."""
    # Mock subprocess.run to raise FileNotFoundError when security command doesn't exist
    with patch(
        "edify.account.keychain.subprocess.run",
        side_effect=FileNotFoundError("security command not found"),
    ) as mock_run:
        # Create Keychain instance and call find
        keychain = Keychain()
        result = keychain.find("test-account", "test-service")

        # Verify subprocess was called
        mock_run.assert_called_once()

        # Verify that find() returns None when security command is unavailable
        assert result is None
