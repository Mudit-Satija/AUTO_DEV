"""File Generator — sends file prompts to Qwen and returns generated code."""

from llm_client import CODER_MODEL, get_llm_response
from coding_agent.prompt_builder import build_file_prompt


def generate_file(file_blueprint: dict, project_rules: dict, all_blueprints: list = None) -> dict:
    """Generate a single file by sending a prompt to Qwen.

    Args:
        file_blueprint: Single entry from build_plan["files"] with keys
            path, type, purpose.
        project_rules: Output from rules_engine.build_project_rules().
        all_blueprints: Full build plan file list for dependency export lookup.

    Returns:
        Dict with keys "path" (str) and "content" (str).
    """
    prompt = build_file_prompt(file_blueprint, project_rules, all_blueprints)
    content = get_llm_response(prompt, model=CODER_MODEL)
    return {"path": file_blueprint.get("path", "unknown"), "content": content}
