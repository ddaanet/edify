"""Extract topic keywords from session user prompts."""

import json
import logging
import re
from pathlib import Path

from edify.parsing import extract_content_text, is_trivial

logger = logging.getLogger(__name__)

# Additional noise words specific to Claude sessions
SESSION_NOISE_WORDS = {
    "please",
    "help",
    "want",
    "need",
    "use",
    "like",
    "think",
    "thank",
    "thanks",
}

STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "can",
    "for",
    "from",
    "to",
    "at",
    "in",
    "by",
    "on",
    "with",
    "as",
    "if",
    "and",
    "or",
    "not",
    "this",
    "that",
    "it",
    "its",
    "my",
    "your",
    "our",
    "their",
    "of",
}


def extract_session_topics(session_file: Path) -> set[str]:
    """Extract topic keywords from user prompts.

    Collects all user message text, tokenizes, removes stopwords and noise,
    and returns keyword set.

    Args:
        session_file: Path to session JSONL file

    Returns:
        Set of topic keywords
    """
    keywords: set[str] = set()

    try:
        with session_file.open() as f:
            for line_num, current_line in enumerate(f, 1):
                stripped_line = current_line.strip()
                if not stripped_line:
                    continue

                try:
                    entry = json.loads(stripped_line)
                except json.JSONDecodeError as e:
                    logger.debug(
                        "Malformed JSON in %s line %d: %s",
                        session_file.name,
                        line_num,
                        e,
                    )
                    continue

                # Only process user entries
                if entry.get("type") != "user":
                    continue

                # Extract text from message
                message = entry.get("message", {})
                content = message.get("content", "")

                # Handle both string and array content formats
                text = extract_content_text(content)

                if not text:
                    continue

                # Filter trivial messages
                if is_trivial(text):
                    continue

                # Tokenize and extract keywords
                tokens = re.split(r"[\s\-_.,;:()[\]{}\"'`]+", text.lower())

                for token in tokens:
                    if (
                        token
                        and len(token) > 1
                        and token not in STOPWORDS
                        and token not in SESSION_NOISE_WORDS
                    ):
                        keywords.add(token)

    except OSError as e:
        logger.warning("Failed to read %s: %s", session_file, e)

    return keywords
