"""Prompt Builder â€” converts file blueprints into deterministic Qwen prompts."""

from typing import Any, Dict, List

from coding_agent.prompt_constraints import auth_is_enabled, build_prompt_constraints


def build_file_prompt(file_blueprint: dict, project_rules: dict, all_blueprints: List[Dict] = None) -> str:
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

    # Dependency export information — tell the LLM what each dependency provides
    if all_blueprints:
        bp_by_path = {bp["path"]: bp for bp in all_blueprints}
        deps = file_blueprint.get("depends_on", [])
        if deps:
            lines.append("")
            lines.append("Dependency exports (import only what is listed below):")
            for dep_path in deps:
                dep_bp = bp_by_path.get(dep_path)
                if dep_bp:
                    provides = dep_bp.get("provides", [])
                    if provides:
                        lines.append(f"- {dep_path} exports: {', '.join(provides)}")
                    else:
                        lines.append(f"- {dep_path}: {dep_bp.get('purpose', 'no purpose declared')}")
                else:
                    lines.append(f"- {dep_path}")

    # Seed file instructions — seeds/ is one level deep, config/models are under src/
    if file_path.startswith("seeds/"):
        db_val = (database or "").strip().lower()
        is_mongo = "mongo" in db_val
        modules = project_rules.get("required_backend_modules", [])
        lines.append("- All require() paths must start with ../ — from seeds/, config is at ../src/config/database and models are at ../src/models/")
        if is_mongo:
            lines.append("- Import the database connection: const connectDB = require('../src/config/database')")
            lines.append("- Call connectDB() to connect, then use Mongoose .create() to insert sample documents for each model, then call mongoose.connection.close() to disconnect")
        else:
            lines.append("- Import the database Pool: const pool = require('../src/config/database')")
            lines.append("- Use pool.query() to insert sample data for each model, then call pool.end() to disconnect")
        for mod in modules:
            lines.append(f"- Import the {mod} model: const {mod.capitalize()} = require('../src/models/{mod}')")

    if backend_fw.lower() == "express.js" and database.lower() == "postgresql":
        lines.append("- Database: Use raw SQL with the `pg` library (Pool). Do NOT generate Sequelize, mongoose, or any ORM code.")
        lines.append("- All model files must be plain JS modules that export helper functions using pg.Pool queries.")
        lines.append("- Never import from sequelize. Never call sequelize.define or sequelize.sync.")
        lines.append("- When importing the database Pool, use: const pool = require('../config/database'). Do NOT destructure it.")
        lines.append("- All local require() paths must start with ./ or ../ — never use bare paths like 'config/database'.")
        lines.append("- Route files must export the router as: module.exports = router")
        lines.append("- Route files must be imported with a bare require, not destructured and not using .router property access. Example: const router = require('./routeFile')")
        lines.append("- src/config/database.js must export as: module.exports = connectDB")
        lines.append("- When importing the database connection, always use a bare require: const connectDB = require('../config/database') — do NOT destructure")

    if database.lower() == "mongodb":
        if "express" in backend_fw.lower() or "node" in backend_fw.lower():
            lines.append("- Database: Use Mongoose (MongoDB ODM). Do NOT generate pg, pg.Pool, SQLAlchemy, Sequelize, or raw SQL code.")
            lines.append("- All model files must be Mongoose schemas that define a mongoose.Schema and export a mongoose.model.")
            lines.append("- Never import from pg, sequelize, or any SQL/ORM library.")
            lines.append("- When importing the database connection, use: const mongoose = require('../config/database').")
            lines.append("- All local require() paths must start with ./ or ../ — never use bare paths like 'config/database'.")
            lines.append("- Route files must export the router as: module.exports = router")
            lines.append("- Route files must be imported with a bare require, not destructured and not using .router property access. Example: const router = require('./routeFile')")
            lines.append("- src/config/database.js must export as: module.exports = connectDB")
            lines.append("- When importing the database connection, always use a bare require: const connectDB = require('../config/database') — do NOT destructure")
        elif "fastapi" in backend_fw.lower() or "python" in backend_fw.lower():
            lines.append("- Database: Use Motor (async MongoDB driver for FastAPI). Do NOT generate SQLAlchemy, psycopg2, or raw SQL code.")
            lines.append("- All model files must be Pydantic-compatible document models using Motor collection operations.")
            lines.append("- Never import from sqlalchemy, psycopg2, or any SQL library.")
            lines.append("- When importing the database connection, use: from app.db.database import db.")

    return "\n".join(lines)

