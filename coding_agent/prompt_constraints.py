"""Shared prompt constraints derived from project_rules and build plan files."""

from typing import List, Optional


def auth_is_enabled(auth_method: str) -> bool:
    val = (auth_method or "").strip().lower()
    return val not in ("", "unknown", "none", "false", "0", "no-auth", "no auth")


def database_kind(database: str) -> str:
    val = (database or "").strip().lower()
    if "mongo" in val:
        return "mongo"
    if "postgres" in val or "mysql" in val or "sql" in val:
        return "sql"
    return "unknown"


def _csv(values: List[str]) -> str:
    return ", ".join(values) if values else "none"


def build_prompt_constraints(project_rules: dict, file_blueprints: Optional[List[dict]] = None) -> List[str]:
    backend_fw = (project_rules.get("backend_framework") or "").lower()
    frontend_fw = (project_rules.get("frontend_framework") or "").lower()
    database = project_rules.get("database") or ""
    db_kind = database_kind(database)
    modules = [str(m) for m in project_rules.get("required_backend_modules", [])]
    pages = [str(p) for p in project_rules.get("required_pages", [])]
    auth_enabled = auth_is_enabled(project_rules.get("auth_method") or "")
    paths = [bp.get("path", "") for bp in file_blueprints or []]
    route_files = [p for p in paths if "/routes/" in p or "/routers/" in p]
    model_files = [p for p in paths if "/models/" in p]
    page_files = [p for p in paths if "/pages/" in p or "/views/" in p]

    lines = [
        f"- Required backend modules from project_rules: {_csv(modules)}.",
        f"- Required frontend pages from project_rules: {_csv(pages)}.",
        f"- Auth is {'enabled' if auth_enabled else 'disabled'} by auth_method.",
        "- Treat the listed files/build plan as the single source of truth.",
        "- Never import, mount, document, or call modules, routes, models, pages, middleware, services, or database clients that are not implied by project_rules and listed file paths.",
    ]

    if route_files:
        lines.append(f"- Route/router files allowed in this prompt: {_csv(route_files)}.")
    if model_files:
        lines.append(f"- Model files allowed in this prompt: {_csv(model_files)}.")
    if page_files:
        lines.append(f"- Page/view files allowed in this prompt: {_csv(page_files)}.")

    for bp in file_blueprints or []:
        deps = [str(dep) for dep in bp.get("depends_on", [])]
        if deps:
            lines.append(f"- {bp.get('path', 'unknown')} may import only these local build-plan dependencies: {_csv(deps)}.")

    if auth_enabled:
        lines.append("- Auth code may only appear in listed auth files and files that explicitly depend on auth files.")
        lines.append("- Mount public auth routes before protected module routes.")
    else:
        lines.append("- Auth is disabled: do not create, import, mount, document, or depend on auth middleware, auth routes, users auth models, JWT, jsonwebtoken, bcrypt, password hashing, or token handling.")

    if db_kind == "mongo":
        lines.append("- Database is MongoDB: use MongoDB/Mongoose for Express or Motor for FastAPI. Do not generate pg, pg.Pool, PostgreSQL SQL, SQLAlchemy, Sequelize, Prisma, CREATE TABLE, or INSERT INTO code.")
    elif db_kind == "sql":
        lines.append("- Database is SQL: use pg.Pool/raw SQL for Express/PostgreSQL or SQLAlchemy for FastAPI SQL. Do not generate MongoDB, mongoose, Motor, or document-schema code.")

    if "express" in backend_fw or "node" in backend_fw:
        if "package.json" in paths:
            lines.append("- package.json scripts must use src/app.js for start/dev because server.js and src/index.js are not listed files.")
        lines.append("- Express route aggregation must import and mount exactly the module route files listed by depends_on; auth routes are mounted in app.js when listed there. Never hardcode workspaces, projects, tasks, users, products, or auth unless those files are listed.")
        lines.append("- Express app.js must mount public auth routes before protected module routes when auth is enabled, apply auth middleware before module routes, mount routes/index.js under /api, call app.listen, and must not create a separate server.js unless server.js is listed.")
    if "fastapi" in backend_fw or "python" in backend_fw:
        lines.append("- FastAPI imports must use the app package paths that correspond to listed files; do not import routers, schemas, models, or services that are not listed.")
    if "react" in frontend_fw or "next" in frontend_fw:
        lines.append("- React/Vite files must use JSX/React conventions and import only listed src/pages/*.jsx files.")
    if "vue" in frontend_fw:
        lines.append("- Vue/Vite files must use Vue conventions, src/router/index.js, and listed src/views/*.vue files. Do not generate React JSX or React Router imports.")

    return lines


