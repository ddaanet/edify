"""Keychain wrapper for macOS security command.

This module provides a wrapper around the macOS `security` command-line utility
for managing keychain entries. It requires macOS and will gracefully degrade on
other platforms or when the security command is unavailable.

Platform dependency: macOS only (requires `security` command)
"""

import subprocess


class Keychain:
    """Wrapper for macOS Keychain security commands.

    Error handling strategy:
    - find(): Returns None on errors (gateway method, called frequently)
    - add()/delete(): Fail loudly on errors (user-initiated, errors are informative)

    This asymmetry is intentional: find() is defensive because it's the gateway
    method that determines if keychain operations are available. If find() returns
    None, callers know not to attempt add/delete operations.
    """

    def find(self, account: str, service: str) -> str | None:
        """Find password in keychain.

        Args:
            account: Account name to search for
            service: Service name to search for

        Returns:
            Password string from keychain, or None if entry not found
        """
        try:
            result = subprocess.run(
                [
                    "security",
                    "find-generic-password",
                    "-a",
                    account,
                    "-s",
                    service,
                    "-w",
                ],
                capture_output=True,
                text=False,
                check=False,
            )

            # Return None if keychain entry not found (non-zero returncode)
            if result.returncode != 0:
                return None

            # Extract password from output (remove newline if present)
            return result.stdout.decode("utf-8").strip()
        except FileNotFoundError:
            # Return None if security command is not available
            return None

    def add(self, account: str, password: str, service: str) -> None:
        """Add password to keychain.

        Args:
            account: Account name to store
            password: Password to store
            service: Service name to store under
        """
        subprocess.run(
            [
                "security",
                "add-generic-password",
                "-a",
                account,
                "-s",
                service,
                "-p",
                password,
            ],
            check=False,
        )

    def delete(self, account: str, service: str) -> None:
        """Delete password from keychain.

        Args:
            account: Account name to delete
            service: Service name to delete from
        """
        subprocess.run(
            [
                "security",
                "delete-generic-password",
                "-a",
                account,
                "-s",
                service,
            ],
            check=False,
        )
