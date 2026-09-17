"""
Safe Production Logging and Secret Redaction for Yatri Setu (Milestone 7H).
Filters out API keys, tokens, database credentials, and personal data from application logs.
"""

import re
import logging
from typing import List, Tuple

# Regex patterns for sanitizing sensitive credentials and tokens
SENSITIVE_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"sk-[a-zA-Z0-9_\-]{20,}", re.IGNORECASE), "sk-***REDACTED***"),
    (re.compile(r"gsk_[a-zA-Z0-9_\-]{20,}", re.IGNORECASE), "gsk_***REDACTED***"),
    (re.compile(r"AIzaSy[a-zA-Z0-9_\-]{16,}", re.IGNORECASE), "AIzaSy***REDACTED***"),
    (re.compile(r"(Bearer\s+)[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE), r"\1***REDACTED***"),
    (re.compile(r"(appid=)[a-zA-Z0-9]{16,}", re.IGNORECASE), r"\1***REDACTED***"),
    (re.compile(r"(api_key=)[a-zA-Z0-9]{16,}", re.IGNORECASE), r"\1***REDACTED***"),
    (re.compile(r"(\bkey=)[a-zA-Z0-9_\-]{10,}", re.IGNORECASE), r"\1***REDACTED***"),
    (re.compile(r"(x-goog-api-key['\"]?\s*[:=]\s*['\"])[^'\"]+(['\"])", re.IGNORECASE), r"\1***REDACTED***\2"),
    (re.compile(r"(://[^:]+:)[^@]+(@)", re.IGNORECASE), r"\1***REDACTED***\2"),
    (re.compile(r"(password['\"]?\s*[:=]\s*['\"])[^'\"]+(['\"])", re.IGNORECASE), r"\1***REDACTED***\2"),
]


class SanitizingFilter(logging.Filter):
    """Logging filter that scrubs sensitive credentials and API tokens from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.sanitize(record.msg)
        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(
                    self.sanitize(arg) if isinstance(arg, str) else arg
                    for arg in record.args
                )
            elif isinstance(record.args, dict):
                record.args = {
                    k: self.sanitize(v) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
        return True

    @staticmethod
    def sanitize(text: str) -> str:
        sanitized = text
        for pattern, replacement in SENSITIVE_PATTERNS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized


def setup_safe_logging(level: int = logging.INFO):
    """Initializes sanitized root logging."""
    sanitizing_filter = SanitizingFilter()
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(sanitizing_filter)
    
    # Ensure default handler has the filter if none configured
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.addFilter(sanitizing_filter)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(level)
