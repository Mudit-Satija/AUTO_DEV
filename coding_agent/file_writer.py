"""File Writer — persists generated files to disk with directory creation."""

import os
from pathlib import Path


def write_file(generated_file: dict, output_dir: str) -> dict:
    """Write a generated file to disk, creating directories as needed.

    Args:
        generated_file: Dict with keys "path" (relative path) and "content" (str).
        output_dir: Root directory under which the file will be written.

    Returns:
        Dict with keys:
            path (str): original relative path
            absolute_path (str): full path on disk
            bytes_written (int): number of bytes written
    """
    file_path = generated_file.get("path", "unknown")
    content = generated_file.get("content", "")

    absolute = Path(output_dir) / file_path
    absolute.parent.mkdir(parents=True, exist_ok=True)

    encoded = content.encode("utf-8")
    absolute.write_bytes(encoded)

    return {
        "path": file_path,
        "absolute_path": str(absolute.resolve()),
        "bytes_written": len(encoded),
    }
