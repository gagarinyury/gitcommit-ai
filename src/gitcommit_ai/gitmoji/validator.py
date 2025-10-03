"""Terminal UTF-8 support validation for emoji display."""
import sys


def supports_utf8() -> bool:
    """Check if terminal supports UTF-8 encoding.

    Returns:
        True if stdout encoding is UTF-8, False otherwise.
    """
    encoding = getattr(sys.stdout, "encoding", "").lower()
    return "utf-8" in encoding or "utf8" in encoding
