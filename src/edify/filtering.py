"""Filtering and categorization functions for feedback analysis."""

from edify.models import FeedbackItem


def is_noise(content: str) -> bool:
    """Detect if content is noise (command output, system messages, etc)."""
    if "<command-name>" in content:
        return True
    if "<bash-stdout>" in content or "<bash-input>" in content:
        return True
    if "Caveat:" in content or "Warmup" in content or "<tool_use_error>" in content:
        return True
    return len(content) < 10


def filter_feedback(items: list[FeedbackItem]) -> list[FeedbackItem]:
    """Filter out noise items from a list of feedback."""
    return [item for item in items if not is_noise(item.content)]


def categorize_feedback(item: FeedbackItem) -> str:
    """Categorize feedback into specific categories based on content.

    Analyzes the content to determine if feedback is instructions, corrections,
    process-related, or code review.
    """
    content_lower = item.content.lower()

    # Check for code_review keywords
    code_review_keywords = ["review", "refactor", "improve", "clarity"]
    if any(keyword in content_lower for keyword in code_review_keywords):
        return "code_review"

    # Check for process keywords
    process_keywords = ["plan", "next step", "workflow", "before", "after"]
    if any(keyword in content_lower for keyword in process_keywords):
        return "process"

    # Check for correction keywords
    correction_keywords = ["no", "wrong", "incorrect", "fix", "error"]
    if any(keyword in content_lower for keyword in correction_keywords):
        return "corrections"

    # Check for instruction keywords
    instruction_keywords = ["don't", "never", "always", "must", "should"]
    if any(keyword in content_lower for keyword in instruction_keywords):
        return "instructions"

    return "instructions"
