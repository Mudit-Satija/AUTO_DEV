"""File Registry — tracks all generated files in a JSON manifest."""

import json
import os
from pathlib import Path


REGISTRY_FILENAME = ".autodev_registry.json"


def register_file(registry: dict, file_blueprint: dict, written_metadata: dict) -> dict:
    """Add a file entry to the registry.

    Args:
        registry: The in-memory registry dict (mutated in place and returned).
        file_blueprint: Original blueprint with keys path, type, purpose.
        written_metadata: Output from file_writer.write_file() with key absolute_path.

    Returns:
        The updated registry dict.
    """
    file_path = file_blueprint.get("path", "unknown")

    registry[file_path] = {
        "purpose": file_blueprint.get("purpose", ""),
        "type": file_blueprint.get("type", ""),
        "absolute_path": written_metadata.get("absolute_path", ""),
    }

    return registry


def save_registry(registry: dict, output_dir: str) -> str:
    """Write the registry to disk as .autodev_registry.json.

    Args:
        registry: The in-memory registry dict.
        output_dir: Root directory of the generated project.

    Returns:
        The absolute path to the saved registry file.
    """
    path = Path(output_dir) / REGISTRY_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return str(path.resolve())


def load_registry(output_dir: str) -> dict:
    """Load the registry from disk.

    Args:
        output_dir: Root directory of the generated project.

    Returns:
        The registry dict, or an empty dict if the file does not exist.
    """
    path = Path(output_dir) / REGISTRY_FILENAME
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
