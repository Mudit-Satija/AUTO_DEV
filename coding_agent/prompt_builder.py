"""Prompt Builder â€” converts file blueprints into deterministic Qwen prompts."""

from typing import Any, Dict

from coding_agent.prompt_constraints import auth_is_enabled, build_prompt_constraints


def build_file_prompt(file_blueprint: dict, project_rules: dict) -> str:
    """Build a deterministic prompt for Qwen to generate a single file.

    Args:
        file_blueprint: Single entry from build_plan["files"] with keys
            path, type, purpose.
        project_rules: Output from rules_engine.build_project_rules().

    Returns:
        A prompt string instructing Qwen to generate the file.
    """
    file_path = file_blueprint.get("path", "unknown")
    file_purpose = file_blueprint.get("purpose", "")
    file_type = file_blueprint.get("type", "")

    backend_fw = project_rules.get("backend_framework", "Unknown")
    frontend_fw = project_rules.get("frontend_framework", "Unknown")
    database = project_rules.get("database", "Unknown")
    auth_method = project_rules.get("auth_method", "Unknown")

    lines = [
        "You are a code generation assistant. Generate the content for a single file.",
        "",
        "Context:",
        f"- Backend framework: {backend_fw}",
        f"- Frontend framework: {frontend_fw}",
        f"- Database: {database}",
        f"- Auth method: {auth_method}",
        f"- Required backend modules: {', '.join(str(m) for m in project_rules.get('required_backend_modules', [])) or 'none'}",
        f"- Required frontend pages: {', '.join(str(p) for p in project_rules.get('required_pages', [])) or 'none'}",
        f"- Auth enabled: {'yes' if auth_is_enabled(auth_method) else 'no'}",
        "",
        "File to generate:",
        f"- Path: {file_path}",
        f"- Purpose: {file_purpose}",
        f"- Type: {file_type}",
        "",
        "Instructions:",
        "- Return only the raw source code.",
        "- Do NOT wrap the code in markdown code blocks.",
        "- Do NOT include any explanations, commentary, or natural language.",
        "- Generate only the requested file \u2014 do not suggest or create additional files.",
        "- The code must be complete, functional, and follow best practices.",
    ]

    lines.extend(build_prompt_constraints(project_rules, [file_blueprint]))

    if backend_fw.lower() == "express.js" and database.lower() == "postgresql":
        lines.append("- Database: Use raw SQL with the `pg` library (Pool). Do NOT generate Sequelize, mongoose, or any ORM code.")
        lines.append("- All model files must be plain JS modules that export helper functions using pg.Pool queries.")
        lines.append("- Never import from sequelize. Never call sequelize.define or sequelize.sync.")
        lines.append("- When importing the database Pool, use: const pool = require('../config/database'). Do NOT destructure it.")
        lines.append("- All local require() paths must start with ./ or ../ â€” never use bare paths like 'config/database'.")

    return "\n".join(lines)

