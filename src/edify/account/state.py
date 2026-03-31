"""AccountState Pydantic model for representing account configuration state."""

import getpass
from pathlib import Path

from pydantic import BaseModel

from edify.account.keychain import Keychain


def get_account_state() -> AccountState:
    """Load account state from filesystem.

    Reads ~/.claude/account-mode and ~/.claude/account-provider files. Returns
    default values if files don't exist. Also queries keychain for OAuth
    credentials.
    """
    home = Path.home()
    account_mode_file = home / ".claude" / "account-mode"
    account_provider_file = home / ".claude" / "account-provider"

    mode = (
        account_mode_file.read_text(encoding="utf-8").strip()
        if account_mode_file.exists()
        else "plan"
    )
    provider = (
        account_provider_file.read_text(encoding="utf-8").strip()
        if account_provider_file.exists()
        else "anthropic"
    )

    # Check if OAuth credentials are in keychain
    keychain = Keychain()
    oauth_token = keychain.find(
        account=getpass.getuser(), service="Claude Code-credentials"
    )
    oauth_in_keychain = oauth_token is not None

    return AccountState(
        mode=mode,
        provider=provider,
        oauth_in_keychain=oauth_in_keychain,
        api_in_claude_env=False,
        has_api_key_helper=False,
        litellm_proxy_running=False,
    )


class AccountState(BaseModel):
    """Represents the current state of a Claude account configuration.

    Fields track various configuration aspects: authentication method
    (oauth vs api key), environment variables, base URL overrides, and
    proxy status.
    """

    mode: str
    provider: str
    oauth_in_keychain: bool
    api_in_claude_env: bool
    base_url: str | None = None
    has_api_key_helper: bool
    litellm_proxy_running: bool

    def validate_consistency(self) -> list[str]:
        """Validate consistency of account state.

        Returns a list of issue strings if any consistency problems are found.
        Returns an empty list if the state is consistent.
        """
        issues = []
        if self.mode == "plan" and not self.oauth_in_keychain:
            issues.append("Plan mode requires OAuth credentials in keychain")
        if self.mode == "api" and not (
            self.api_in_claude_env or self.has_api_key_helper
        ):
            issues.append("API mode requires API key in environment or helper enabled")
        if self.provider == "litellm" and not self.litellm_proxy_running:
            issues.append("LiteLLM provider requires proxy to be running")
        return issues
