"""Shared prompt constraints derived from project_rules and build plan files.

No auth constraints. All constraints are SRS-driven and tech-stack-aware.
"""

from typing import List, Optional


def database_kind(database: str) -> str:
    val = (database or "").strip().lower()
    if "mongo" in val:
        return "mongo"
    if "postgres" in val or "mysql" in val or "sql" in val:
        return "sql"
    return "unknown"


def _csv(values: List[str]) -> str:
    return ", ".join(values) if values else "none"


def build_prompt_constraints(
    project_rules: dict,
    file_blueprints: Optional[List[dict]] = None,
) -> List[str]:
    backend_fw = (project_rules.get("backend_framework") or "").lower()
    frontend_fw = (project_rules.get("frontend_framework") or "").lower()
    database = project_rules.get("database") or ""
    db_kind = database_kind(database)
    modules = [str(m) for m in project_rules.get("required_backend_modules", [])]
    pages = [str(p) for p in project_rules.get("required_pages", [])]
    paths = [bp.get("path", "") for bp in file_blueprints or []]
    route_files = [p for p in paths if "/routes/" in p or "/routers/" in p]
    model_files = [p for p in paths if "/models/" in p]
    page_files = [p for p in paths if "/pages/" in p or "/views/" in p]

    lines = [
        f"- Required backend modules from SRS entities: {_csv(modules)}.",
        f"- Required frontend pages from SRS: {_csv(pages)}.",
        "- Treat the listed files/build plan as the single source of truth.",
        "- Never import, mount, document, or call modules, routes, models, pages, middleware, services, or database clients that are not implied by the build plan and listed file paths.",
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

    if db_kind == "mongo":
        lines.append("- Database is MongoDB: use MongoDB/Mongoose for Express or Motor for FastAPI. Do not generate pg, pg.Pool, PostgreSQL SQL, SQLAlchemy, Sequelize, Prisma, CREATE TABLE, or INSERT INTO code.")
    elif db_kind == "sql":
        lines.append("- Database is SQL: use pg.Pool/raw SQL for Express/PostgreSQL or SQLAlchemy for FastAPI SQL. Do not generate MongoDB, mongoose, Motor, or document-schema code.")

    if "express" in backend_fw or "node" in backend_fw:
        if "package.json" in paths:
            lines.append("- package.json scripts must use src/app.js for start/dev because server.js and src/index.js are not listed files.")
        lines.append("- Express route aggregation must import and mount exactly the module route files listed by depends_on.")
        lines.append("- Express app.js must mount routes/index.js under /api, call connectDB before app.listen for MongoDB, and must not create a separate server.js unless server.js is listed.")
    if "fastapi" in backend_fw or "python" in backend_fw:
        lines.append("- FastAPI imports must use the app package paths that correspond to listed files; do not import routers, schemas, models, or services that are not listed.")
    if "react" in frontend_fw or "next" in frontend_fw:
        is_ts = "typescript" in frontend_fw or "ts" in frontend_fw
        ext = "tsx" if is_ts else "jsx"
        lines.append(f"- React/Vite files must use JSX/React/TSX conventions and import only listed src/pages/*.{ext} files.")
        if is_ts:
            lines.append("- Since the project uses TypeScript, all generated code in .ts and .tsx files must be fully typed (e.g. define interfaces/types for all state variables like useState<Task[]>([]), specify parameter and return types for functions). Avoid implicit 'any' types.")
            lines.append("- In import statements in .ts and .tsx files, do not append '.ts' or '.tsx' extensions to local imports (e.g. use './App' instead of './App.tsx').")
    if "vue" in frontend_fw:
        lines.append("- Vue/Vite files must use Vue conventions, src/router/index.js, and listed src/views/*.vue files. Do not generate React JSX or React Router imports.")

    if len(pages) > 1:
        if "react" in frontend_fw or "next" in frontend_fw:
            lines.append("- Since there are multiple pages, App.tsx/App.jsx must render a visible navigation header/bar (e.g. using Link from 'react-router-dom') to allow navigating to all pages (Dashboard, Tasks, etc.).")
        elif "vue" in frontend_fw:
            lines.append("- Since there are multiple pages, App.vue must render a visible navigation header/bar (e.g. using RouterLink) to allow navigating to all views (Dashboard, Tasks, etc.).")

    # Shared entity state and mock data constraints
    lines.extend([
        "- Do NOT generate mock/sample/demo data arrays for tracked entities (such as tasks, etc.) in any page or component unless explicitly requested in the SRS.",
        "- For any entity that appears on multiple pages (like 'Task' appearing on both Dashboard and Tasks pages), a single source of truth must exist.",
        "- In frontend-only projects with no backend/database, this single source of truth must be a shared localStorage key (e.g., 'tasks') or a unified React/Vue Context/state store. Pages like Dashboard and Tasks must read from/write to the exact same localStorage key or state store.",
        "- Statistics and analytics pages must retrieve and compute metrics dynamically from this shared live entity collection. If the retrieved collection is empty, display a beautiful empty state with a link/button to redirect the user to the management page (e.g., Tasks page) to add items.",
    ])

    return lines
