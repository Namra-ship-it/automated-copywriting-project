"""Utility functions for file handling, logging, sanitization, and text processing."""

import json
import re
from pathlib import Path
from typing import Any

from loguru import logger


def read_json_file(file_path: Path | str) -> Any:
    """Read and parse a JSON file."""
    path = Path(file_path)

    if not path.exists():
        logger.error(f"JSON file not found: {path}")
        raise FileNotFoundError(f"JSON file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        content = json.load(f)

    logger.debug(f"Successfully loaded JSON from {path}")
    return content


def write_json_file(
    file_path: Path | str,
    data: Any,
    indent: int = 2,
) -> None:
    """Write data to a JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

    logger.debug(f"Successfully wrote JSON to {path}")


def count_characters(text: str) -> int:
    """Count the exact number of characters in a text string."""
    return len(text)


def sanitize_text(text: str) -> str:
    """Sanitize text for safe prompt injection and JSON compatibility."""
    if not text:
        return ""

    text = text.strip()
    text = re.sub(r"[ ]{2,}", " ", text)

    # Remove control characters except newline, tab, and carriage return.
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Normalize line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    return text


def truncate_to_limit(
    text: str,
    limit: int,
    suffix: str = "...",
) -> str:
    """Truncate text to fit within a character limit."""
    if len(text) <= limit:
        return text

    truncate_at = limit - len(suffix)

    if truncate_at < 0:
        truncate_at = limit

    return text[:truncate_at] + suffix


def setup_file_logger(
    log_dir: Path,
    level: str = "INFO",
) -> None:
    """Configure loguru to write to a rotating file."""
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"

    logger.add(
        str(log_file),
        rotation="10 MB",
        retention="7 days",
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=True,
    )

    logger.info(f"File logging configured at {log_file} with level {level}")
