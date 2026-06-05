"""Patch Agent — fixes a single generated file without regenerating the project."""

from pathlib import Path

from llm_client import CODER_MODEL, get_llm_response
from coding_agent.file_registry import load_registry


def patch_file(file_path: str, error_description: str, output_dir: str) -> dict:
    """Fix a single generated file identified by its relative path.

    Args:
        file_path: Relative path of the file to patch (e.g. "src/app.js").
        error_description: Description of the bug or issue to fix.
        output_dir: Root directory of the generated project.

    Returns:
        Dict with keys:
            file_path (str): original relative path
            status (str): "patched" or "error"
            error (str, optional): error message if status is "error"
    """
    registry = load_registry(output_dir)

    if file_path not in registry:
        return {
            "file_path": file_path,
            "status": "error",
            "error": f"File '{file_path}' not found in project registry",
        }

    entry = registry[file_path]
    absolute_path = entry.get("absolute_path", "")
    disk_path = Path(absolute_path)

    if not disk_path.exists():
        return {
            "file_path": file_path,
            "status": "error",
            "error": f"File '{absolute_path}' does not exist on disk",
        }

    current_content = disk_path.read_text(encoding="utf-8")

    prompt = _build_patch_prompt(file_path, error_description, current_content)
    new_content = get_llm_response(prompt, model=CODER_MODEL)

    disk_path.write_text(new_content, encoding="utf-8")

    return {
        "file_path": file_path,
        "status": "patched",
    }


def _build_patch_prompt(file_path: str, error_description: str, current_content: str) -> str:
    """Build a deterministic prompt for Qwen to fix a single file."""
    lines = [
        "Fix the following file:",
        "",
        f"File path: {file_path}",
        f"Error: {error_description}",
        "",
        "Current content:",
        "```",
        current_content,
        "```",
        "",
        "Instructions:",
        "- Fix only this file.",
        "- Return only the corrected file content.",
        "- Do NOT wrap the code in markdown code blocks.",
        "- Do NOT include any explanations, commentary, or natural language.",
        "- The code must be complete and functional.",
    ]

    return "\n".join(lines)
