"""Custom exceptions for edify."""


class ClaudeUtilsError(Exception):
    """Base exception for all edify errors."""


class ApiAuthenticationError(ClaudeUtilsError):
    """Raised when Anthropic API authentication fails."""

    def __init__(self) -> None:
        """Initialize with default authentication error message."""
        super().__init__(
            "Authentication failed. Set ANTHROPIC_API_KEY env var "
            "or add [anthropic] api_key to ~/.config/edify/config.toml"
        )


class ApiRateLimitError(ClaudeUtilsError):
    """Raised when Anthropic API rate limit is exceeded."""

    def __init__(self) -> None:
        """Initialize with default rate limit error message."""
        super().__init__("API rate limit exceeded. Please try again later.")


class ModelResolutionError(ClaudeUtilsError):
    """Raised when model alias cannot be resolved via API."""

    def __init__(self, alias: str) -> None:
        """Initialize with model alias in error message."""
        super().__init__(
            f"Models API is unreachable and cannot resolve alias '{alias}'. "
            "This is a transient failure. Please retry."
        )


class ApiError(ClaudeUtilsError):
    """Raised when a generic Anthropic API error occurs."""

    def __init__(self, details: str) -> None:
        """Initialize with API error details."""
        super().__init__(f"API error: {details}")


class FileReadError(ClaudeUtilsError):
    """Raised when a file cannot be read."""

    def __init__(self, path: str, reason: str) -> None:
        """Initialize with file path and read failure reason."""
        super().__init__(f"Failed to read {path}: {reason}")


class MarkdownProcessingError(ClaudeUtilsError):
    """Raised when markdown processing fails."""

    def __init__(self, filepath: str, error: Exception) -> None:
        """Initialize with file path and underlying error, preserving chain."""
        super().__init__(f"{filepath}: {error}")
        self.__cause__ = error


class MarkdownInnerFenceError(ClaudeUtilsError):
    """Raised when inner fence is detected in non-markdown block."""
