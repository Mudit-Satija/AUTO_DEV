"""Build Plan Generator — converts SRS + Knowledge into a deterministic file blueprint.

Every file must have requirement lineage:
- reason_for_existence: why this file exists
- source_requirement: which SRS requirement created it
- source_page: which SRS page created it
- source_entity: which SRS entity created it
- source_flow: which SRS flow created it

No file is generated without answering: which SRS entry created it?
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from coding_agent.naming import entity_prop_name, entity_setter_name

def generate_build_plan(project_rules: dict) -> dict:
    """Convert project_rules (derived from SRS) into a structured build plan.

    Every file blueprint includes requirement lineage.
    Pages come ONLY from SRS.pages.
    Backend artifacts come ONLY from SRS entities + flow.
    """
    files: List[Dict[str, Any]] = []

    backend_fw = (project_rules.get("backend_framework") or "").lower()
    frontend_fw = (project_rules.get("frontend_framework") or "").lower()
    database = (project_rules.get("database") or "").lower()

    srs = project_rules.get("srs", {})
    if not isinstance(srs, dict):
        srs = {}

    pages = srs.get("pages", []) or []
    entities = srs.get("entities", []) or []
    flow = srs.get("flow", []) or []
    requirements = srs.get("requirements", []) or []
    project_name = srs.get("project_name", "Untitled")

    # README
    files.append({
        "path": "README.md",
        "type": "documentation",
        "purpose": f"Project overview and setup instructions for {project_name}",
        "reason_for_existence": f"Required for project {project_name}",
        "source_requirement": "project_documentation",
        "source_page": "",
        "source_entity": "",
        "source_flow": "",
        "depends_on": [],
        "provides": [],
        "requirements": [],
    })

    # Frontend-only mode: skip all backend + database files
    is_frontend_only = backend_fw in ("", "none", "frontend only")
    has_backend = not is_frontend_only and bool(backend_fw)

    if is_frontend_only:
        files.extend(_build_frontend_config(frontend_fw, has_backend=False, project_name=project_name))
        files.extend(_build_pages(frontend_fw, pages, entities, has_backend=False))
        _wire_app_deps(files)
        _assign_bundles(files)
        _apply_deterministic_static_content(files, project_name, backend_fw, frontend_fw, database, entities)
        return {"files": files}

    # Backend config files (tech stack infrastructure — minimal)
    files.extend(_build_backend_config(backend_fw, database))

    # Backend entity files — one route + model per SRS entity
    files.extend(_build_entity_artifacts(backend_fw, database, entities, flow))

    # Backend flow-specific endpoints (non-CRUD operations from flow)
    files.extend(_build_flow_endpoints(backend_fw, database, flow, entities))

    # Frontend config files
    files.extend(_build_frontend_config(frontend_fw, has_backend, project_name=project_name))

    # Frontend pages — ONLY from SRS.pages
    files.extend(_build_pages(frontend_fw, pages, entities, has_backend))

    # Database files
    files.extend(_build_database_files(database, backend_fw, entities))

    # Dynamically connect frontend pages and styles to the main App component
    _wire_app_deps(files)

    # Assign bundle
    for f in files:
        f["bundle"] = _infer_bundle(f)

    _apply_deterministic_static_content(files, project_name, backend_fw, frontend_fw, database, entities)

    return {"files": files}


def _pascal_case(stem: str) -> str:
    parts = re.split(r"[-_\s]", stem)
    return "".join(p.capitalize() for p in parts)


def _sanitize_page_name(name: str) -> str:
    parts = name.split()
    clean = "".join(p[0].upper() + p[1:] if p else "" for p in parts)
    return clean if clean else "Page"


def _page_route_path(name: str) -> str:
    """Convert page name to a URL path (kebab-case).
    Dashboard is the home route -> '/'.
    """
    if name.lower() == "dashboard":
        return "/"
    return "/" + name.lower().replace(" ", "-")


def _nav_link_path(name: str) -> str:
    """Nav link path for a page. Dashboard uses '/'."""
    return _page_route_path(name)


def _entity_module_name(entity_name: str) -> str:
    name = _pascal_case(entity_name)
    if name.endswith("s") and len(name) > 1:
        name = name[:-1]
    return name


def _entity_route_name(entity_name: str) -> str:
    return entity_name.lower().replace(" ", "-")


def _entity_model_name(entity_name: str) -> str:
    return _entity_module_name(entity_name)


def _db_kind(database: str) -> str:
    val = (database or "").strip().lower()
    if "mongo" in val:
        return "mongo"
    if "postgres" in val or "mysql" in val or "sql" in val:
        return "sql"
    return "unknown"


def _build_backend_config(backend_fw: str, database: str) -> List[Dict[str, Any]]:
    files = []

    if "express" in backend_fw or "node" in backend_fw:
        db_dep = "mongoose" if "mongo" in _db_kind(database) else "pg" if _db_kind(database) == "sql" else "database client"
        files.append({
            "path": "backend/.gitignore", "type": "config",
            "purpose": "Git ignore rules for Node.js backend",
            "reason_for_existence": f"Tech stack: {backend_fw}",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [], "provides": [], "requirements": [],
        })
        files.append({
            "path": "backend/.env", "type": "env",
            "purpose": "Environment variables for backend",
            "reason_for_existence": f"Tech stack: {backend_fw}",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [], "provides": [], "requirements": [],
        })
        files.append({
            "path": "backend/package.json", "type": "config",
            "purpose": f"Node.js dependencies — must include express, {db_dep}, dotenv, cors",
            "reason_for_existence": f"Tech stack: {backend_fw}",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [], "provides": [], "requirements": [],
        })
        files.append({
            "path": "backend/src/app.js", "type": "source",
            "purpose": "Express application setup — middleware, route mounting, server start",
            "reason_for_existence": f"Tech stack: {backend_fw}",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": ["backend/src/config/index.js", "backend/src/config/database.js",
                           "backend/src/middleware/errorHandler.js", "backend/src/routes/index.js"],
            "provides": [], "requirements": ["middleware setup", "route mounting", "server start"],
        })
        files.append({
            "path": "backend/src/config/index.js", "type": "config",
            "purpose": "Configuration loader for environment variables",
            "reason_for_existence": f"Tech stack: {backend_fw}",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [], "provides": [], "requirements": ["configuration export"],
        })
        files.append({
            "path": "backend/src/config/database.js", "type": "config",
            "purpose": f"Database connection setup for {database}",
            "reason_for_existence": f"Tech stack: {backend_fw}, Database: {database}",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [], "provides": [], "requirements": ["database connection"],
        })
        files.append({
            "path": "backend/src/middleware/errorHandler.js", "type": "source",
            "purpose": "Global error handler middleware",
            "reason_for_existence": f"Tech stack: {backend_fw}",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [], "provides": [], "requirements": ["error handling"],
        })
        files.append({
            "path": "backend/src/routes/index.js", "type": "source",
            "purpose": "Route aggregator — mounts all entity route files under /api",
            "reason_for_existence": f"Tech stack: {backend_fw}",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [], "provides": [], "requirements": ["route aggregation"],
        })

    elif "fastapi" in backend_fw or "python" in backend_fw:
        files.extend([
            {"path": ".gitignore", "type": "config",
             "purpose": "Git ignore rules for Python backend",
             "reason_for_existence": f"Tech stack: {backend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": ".env", "type": "env",
             "purpose": "Environment variables",
             "reason_for_existence": f"Tech stack: {backend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "requirements.txt", "type": "config",
             "purpose": f"Python dependencies for FastAPI and {database}",
             "reason_for_existence": f"Tech stack: {backend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "app/__init__.py", "type": "source",
             "purpose": "App package init",
             "reason_for_existence": f"Tech stack: {backend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "app/main.py", "type": "source",
             "purpose": "FastAPI application setup and router mounting",
             "reason_for_existence": f"Tech stack: {backend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": ["app/core/config.py", "app/db/database.py"],
             "provides": [], "requirements": ["app setup", "router mounting"]},
            {"path": "main.py", "type": "source",
             "purpose": "Application entry point",
             "reason_for_existence": f"Tech stack: {backend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": ["app/main.py"], "provides": [], "requirements": ["app startup"]},
            {"path": "app/core/config.py", "type": "config",
             "purpose": "Configuration settings",
             "reason_for_existence": f"Tech stack: {backend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": ["configuration settings"]},
            {"path": "app/db/database.py", "type": "config",
             "purpose": f"Database connection for {database}",
             "reason_for_existence": f"Tech stack: {backend_fw}, Database: {database}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": ["database connection"]},
        ])

    return files


def _build_entity_artifacts(
    backend_fw: str, database: str,
    entities: List[Dict], flow: List[Dict],
) -> List[Dict[str, Any]]:
    """Generate one route + model per SRS entity.

    Endpoints derive from CRUD needs + flow references.
    """
    files = []
    db_kind = _db_kind(database)
    is_node = "express" in backend_fw or "node" in backend_fw
    is_python = "fastapi" in backend_fw or "python" in backend_fw

    # Collect entity references from flow
    flow_entity_refs: Dict[str, List[str]] = {}
    for f in flow:
        for ent in (f.get("entities", []) or []):
            e_key = ent.lower().strip()
            if e_key not in flow_entity_refs:
                flow_entity_refs[e_key] = []
            flow_entity_refs[e_key].append(f.get("name", ""))

    for entity in entities:
        name = entity.get("name", "")
        if not name:
            continue
        fields = entity.get("fields", []) or []
        description = entity.get("description", "")
        route_name = _entity_route_name(name)
        model_name = _entity_model_name(name)
        entity_flows = flow_entity_refs.get(name.lower(), [])

        if is_node:
            db_dep_file = "backend/src/config/database.js"
            files.append({
                "path": f"backend/src/models/{route_name}.js",
                "type": "module",
                "purpose": f"{name} data model for {database}",
                "reason_for_existence": f"SRS entity: {name}",
                "source_requirement": "entity_model",
                "source_page": "",
                "source_entity": name,
                "source_flow": "; ".join(entity_flows) if entity_flows else "",
                "depends_on": [db_dep_file],
                "provides": [],
                "requirements": ["model definition"],
            })
            all_model_paths = [f"backend/src/models/{_entity_route_name(e.get('name', ''))}.js" for e in entities if e.get("name")]
            files.append({
                "path": f"backend/src/routes/{route_name}.js",
                "type": "module",
                "purpose": f"{name} API routes — CRUD + flow-specific endpoints",
                "reason_for_existence": f"SRS entity: {name}",
                "source_requirement": "entity_api",
                "source_page": "",
                "source_entity": name,
                "source_flow": "; ".join(entity_flows) if entity_flows else "",
                "depends_on": [db_dep_file, f"backend/src/models/{route_name}.js", "backend/src/middleware/errorHandler.js", "backend/src/config/index.js", "backend/src/models/index.js"] + all_model_paths,
                "provides": [],
                "requirements": ["list", "create", "update", "delete"],
            })

        elif is_python:
            db_dep_file = "app/db/database.py"
            files.append({
                "path": f"app/models/{route_name}.py",
                "type": "module",
                "purpose": f"{name} {'MongoDB document' if db_kind == 'mongo' else 'SQLAlchemy'} model",
                "reason_for_existence": f"SRS entity: {name}",
                "source_requirement": "entity_model",
                "source_page": "",
                "source_entity": name,
                "source_flow": "; ".join(entity_flows) if entity_flows else "",
                "depends_on": [],
                "provides": [],
                "requirements": ["model definition"],
            })
            files.append({
                "path": f"app/schemas/{route_name}.py",
                "type": "module",
                "purpose": f"{name} Pydantic schemas for request/response validation",
                "reason_for_existence": f"SRS entity: {name}",
                "source_requirement": "entity_schema",
                "source_page": "",
                "source_entity": name,
                "source_flow": "",
                "depends_on": [],
                "provides": [],
                "requirements": ["schema definition"],
            })
            all_model_paths = [f"app/models/{_entity_route_name(e.get('name', ''))}.py" for e in entities if e.get("name")]
            all_schema_paths = [f"app/schemas/{_entity_route_name(e.get('name', ''))}.py" for e in entities if e.get("name")]
            files.append({
                "path": f"app/routers/{route_name}.py",
                "type": "module",
                "purpose": f"{name} API routes — CRUD + flow-specific endpoints",
                "reason_for_existence": f"SRS entity: {name}",
                "source_requirement": "entity_api",
                "source_page": "",
                "source_entity": name,
                "source_flow": "; ".join(entity_flows) if entity_flows else "",
                "depends_on": [f"app/schemas/{route_name}.py", f"app/models/{route_name}.py", "app/core/config.py", "app/db/database.py", "app/models/__init__.py"] + all_model_paths + all_schema_paths,
                "provides": [],
                "requirements": ["list", "create", "update", "delete"],
            })
            files.append({
                "path": f"app/services/{route_name}.py",
                "type": "module",
                "purpose": f"{name} business logic layer",
                "reason_for_existence": f"SRS entity: {name}",
                "source_requirement": "entity_service",
                "source_page": "",
                "source_entity": name,
                "source_flow": "",
                "depends_on": [f"app/models/{route_name}.py", "app/models/__init__.py"],
                "provides": [],
                "requirements": ["business logic"],
            })

    if is_node and entities:
        files.append({
            "path": "backend/src/models/index.js",
            "type": "module",
            "purpose": "Export all backend models from a single entrypoint",
            "reason_for_existence": "Convenience index exporter for database models",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [f"backend/src/models/{_entity_route_name(e.get('name', ''))}.js" for e in entities if e.get("name")],
            "provides": [], "requirements": [],
        })
    elif is_python and entities:
        files.append({
            "path": "app/models/__init__.py",
            "type": "module",
            "purpose": "Export all backend models from a single entrypoint",
            "reason_for_existence": "Convenience index exporter for database models",
            "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [f"app/models/{_entity_route_name(e.get('name', ''))}.py" for e in entities if e.get("name")],
            "provides": [], "requirements": [],
        })

    return files


def _build_flow_endpoints(
    backend_fw: str, database: str,
    flow: List[Dict], entities: List[Dict],
) -> List[Dict[str, Any]]:
    """Generate additional endpoint files for flow-specific operations
    that go beyond standard CRUD (e.g. search, reports, transfers).
    """
    files = []
    if not flow:
        return files

    is_node = "express" in backend_fw or "node" in backend_fw
    is_python = "fastapi" in backend_fw or "python" in backend_fw
    if not is_node and not is_python:
        return files

    entity_names = {e.get("name", "").lower() for e in entities}

    # Detect non-CRUD operations from flow steps
    crud_operations = {"create", "list", "update", "delete", "view", "edit", "add", "remove"}
    non_crud_flows = []
    for f in flow:
        for step in (f.get("steps", []) or []):
            step_lower = step.lower()
            contains_crud = any(op in step_lower for op in crud_operations)
            if not contains_crud and entity_names:
                for ent_name in entity_names:
                    if ent_name in step_lower:
                        non_crud_flows.append(f)
                        break

    seen_modules = set()
    for f in non_crud_flows:
        flow_entities = f.get("entities", []) or []
        for ent_name in flow_entities:
            route_name = _entity_route_name(ent_name)
            if route_name in seen_modules:
                continue
            seen_modules.add(route_name)

            if is_node:
                route_path = f"backend/src/routes/{route_name}-flow.js"
                all_model_paths = [f"backend/src/models/{_entity_route_name(e.get('name', ''))}.js" for e in entities if e.get("name")]
                files.append({
                    "path": route_path,
                    "type": "module",
                    "purpose": f"Flow-specific endpoints for {ent_name} — {f.get('name', '')}",
                    "reason_for_existence": f"SRS flow: {f.get('name', '')}",
                    "source_requirement": "flow_endpoint",
                    "source_page": "",
                    "source_entity": ent_name,
                    "source_flow": f.get("name", ""),
                    "depends_on": [f"backend/src/models/{route_name}.js", "backend/src/middleware/errorHandler.js", "backend/src/config/index.js", "backend/src/models/index.js"] + all_model_paths,
                    "provides": [],
                    "requirements": [],
                })

    return files


def _build_frontend_config(frontend_fw: str, has_backend: bool = True, project_name: str = "Untitled") -> List[Dict[str, Any]]:
    files = []
    is_ts = "typescript" in frontend_fw or "ts" in frontend_fw
    is_tailwind = "tailwind" in frontend_fw
    ext = "tsx" if is_ts else "jsx"

    if "react" in frontend_fw or "next" in frontend_fw:
        pkg_purpose = "Frontend dependencies — react, react-dom, react-router-dom, axios, vite, @vitejs/plugin-react"
        if is_ts:
            pkg_purpose += ", typescript, @types/react, @types/react-dom, @types/react-router-dom, @types/node"
        if is_tailwind:
            pkg_purpose += ", tailwindcss, postcss, autoprefixer"
        if is_ts:
            pkg_purpose += ". Build script must be 'tsc && vite build'."

        base_files = [
            {"path": "frontend/package.json", "type": "config",
             "purpose": pkg_purpose,
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": [],
             "static_content": json.dumps({
                  "name": project_name.lower().replace(" ", "-") + "-frontend",
                  "private": True,
                  "version": "1.0.0",
                  "type": "module",
                  "scripts": {
                      "dev": "vite",
                      "build": "vite build",
                      "preview": "vite preview",
                  },
                   "dependencies": {
                       "react": "^18.2.0",
                       "react-dom": "^18.2.0",
                       "react-router-dom": "^6.20.0",
                       "uuid": "^9.0.0",
                   },
                  "devDependencies": {
                      "@vitejs/plugin-react": "^4.2.0",
                      "vite": "^5.0.0",
                  },
              }, indent=2)},
            {"path": "frontend/.env", "type": "env",
             "purpose": "Frontend environment variables",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": f"frontend/vite.config.{'ts' if is_ts else 'js'}", "type": "config",
             "purpose": f"Vite build configuration for React {'with TypeScript support' if is_ts else ''}",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": [],
             "static_content": 'import { defineConfig } from "vite";\nimport react from "@vitejs/plugin-react";\n\nexport default defineConfig({\n  plugins: [react()],\n});\n'},
            {"path": "frontend/index.html", "type": "source",
             "purpose": f"HTML entry point referencing /src/main.{ext}",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": [],
             "static_content": '<!DOCTYPE html>\n<html lang="en">\n  <head>\n    <meta charset="UTF-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n    <title>RecipeBook</title>\n  </head>\n  <body>\n    <div id="root"></div>\n    <script type="module" src="/src/main.jsx"></script>\n  </body>\n</html>\n'},
            {"path": f"frontend/src/main.{ext}", "type": "source",
             "purpose": "React entry point rendering Root component",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [f"frontend/src/App.{ext}"], "provides": [], "requirements": ["app rendering"],
             "static_content": 'import React from "react";\nimport { createRoot } from "react-dom/client";\nimport App from "./App";\n\nconst root = createRoot(document.getElementById("root"));\nroot.render(<App />);\n'},
            {"path": f"frontend/src/App.{ext}", "type": "source",
             "purpose": "Root application component with router and styling wrapper",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": ["component export", "route configuration"]},
            {"path": "frontend/src/App.css", "type": "source",
             "purpose": f"Global CSS styles {'including Tailwind directives (@tailwind base; @tailwind components; @tailwind utilities;)' if is_tailwind else ''}",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
        ]

        if is_ts:
            base_files.extend([
                {"path": "frontend/tsconfig.json", "type": "config",
                 "purpose": "TypeScript compiler settings config",
                 "reason_for_existence": f"Tech stack: {frontend_fw}",
                 "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
                 "depends_on": [], "provides": [], "requirements": []},
                {"path": "frontend/src/vite-env.d.ts", "type": "config",
                 "purpose": "Vite environment types definition",
                 "reason_for_existence": f"Tech stack: {frontend_fw}",
                 "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
                 "depends_on": [], "provides": [], "requirements": []},
            ])

        if is_tailwind:
            base_files.extend([
                {"path": "frontend/tailwind.config.cjs", "type": "config",
                 "purpose": "Tailwind CSS content paths configuration",
                 "reason_for_existence": f"Tech stack: {frontend_fw}",
                 "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
                 "depends_on": [], "provides": [], "requirements": []},
                {"path": "frontend/postcss.config.cjs", "type": "config",
                 "purpose": "PostCSS config with tailwindcss and autoprefixer",
                 "reason_for_existence": f"Tech stack: {frontend_fw}",
                 "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
                 "depends_on": [], "provides": [], "requirements": []},
            ])

        if has_backend:
            base_files.append({
                "path": f"frontend/src/services/api.{'ts' if is_ts else 'js'}", "type": "source",
                "purpose": "API client using axios",
                "reason_for_existence": f"Tech stack: {frontend_fw}",
                "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
                "depends_on": [], "provides": [], "requirements": ["api client"],
            })
        files.extend(base_files)
    elif "vue" in frontend_fw:
        base_files = [
            {"path": "frontend/package.json", "type": "config",
             "purpose": "Frontend dependencies",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "frontend/.env", "type": "env",
             "purpose": "Frontend environment variables",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "frontend/vite.config.js", "type": "config",
             "purpose": "Vite build configuration",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "frontend/index.html", "type": "source",
             "purpose": "HTML entry point",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "frontend/src/main.js", "type": "source",
             "purpose": "Vue entry point",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": ["frontend/src/App.vue"], "provides": [], "requirements": ["app mounting"]},
            {"path": "frontend/src/App.vue", "type": "source",
             "purpose": "Root application component",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": ["frontend/src/router/index.js"], "provides": [], "requirements": ["component export"]},
            {"path": "frontend/src/router/index.js", "type": "source",
             "purpose": "Vue Router configuration",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": ["route configuration"]},
        ]
        if has_backend:
            base_files.append({
                "path": "frontend/src/services/api.js", "type": "source",
                "purpose": "API client using axios",
                "reason_for_existence": f"Tech stack: {frontend_fw}",
                "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
                "depends_on": [], "provides": [], "requirements": ["api client"],
            })
        files.extend(base_files)

    return files


def _build_pages(
    frontend_fw: str,
    pages: List[Dict],
    entities: List[Dict],
    has_backend: bool = True,
) -> List[Dict[str, Any]]:
    """Generate page files ONLY from SRS.pages.

    No automatic Dashboard, Login, Register, Profile, or Settings.
    """
    files = []
    entity_names = {e.get("name", "").lower() for e in entities if e.get("name")}
    is_ts = "typescript" in frontend_fw or "ts" in frontend_fw
    ext = "tsx" if is_ts else "jsx"

    for page in pages:
        name = page.get("name", "")
        purpose = page.get("purpose", "")
        page_entities = page.get("entities", []) or []

        if not name:
            continue

        safe = _sanitize_page_name(name)

        if "react" in frontend_fw or "next" in frontend_fw:
            page_path = f"frontend/src/pages/{safe}.{ext}"
        elif "vue" in frontend_fw:
            page_path = f"frontend/src/views/{safe}.vue"
        else:
            page_path = f"frontend/src/pages/{safe}.js"

        # Dashboard is a summary/stats page, NOT a data entry form
        if name.lower() == "dashboard":
            derived_purpose = (
                f"{name} page — SUMMARY with counts/recent activity, NO add/edit forms. "
                "CRITICAL: Do NOT include any <form>, <input>, <select>, <textarea>, "
                "<button type='submit'>, or state variables for creating/editing data. "
                "This page ONLY displays read-only aggregated data (counts, lists, stats)."
            )
        elif purpose:
            derived_purpose = purpose
        else:
            derived_purpose = f"{name} page"

        bp = {
            "path": page_path,
            "type": "page",
            "purpose": derived_purpose,
            "reason_for_existence": f"SRS page: {name}",
            "source_requirement": "page_definition",
            "source_page": name,
            "source_entity": "; ".join(page_entities) if page_entities else "",
            "source_flow": "",
            "depends_on": [],
            "provides": [],
            "requirements": ["component export"],
            "route_path": _page_route_path(name),
        }

        # Build spec from entities referenced by this page
        if has_backend:
            api_calls = []
            for pe in page_entities:
                ent_route = _entity_route_name(pe)
                api_calls.append({"method": "GET", "endpoint": f"/api/{ent_route}"})
                api_calls.append({"method": "POST", "endpoint": f"/api/{ent_route}"})
                api_calls.append({"method": "PUT", "endpoint": f"/api/{ent_route}/:id"})
                api_calls.append({"method": "DELETE", "endpoint": f"/api/{ent_route}/:id"})

            if api_calls:
                bp["spec"] = {"api_calls": api_calls}

        # Frontend-only: store exact prop names in spec (single deterministic computation)
        if not has_backend and page_entities:
            prop_names = [entity_prop_name(e) for e in page_entities]
            setter_names = [entity_setter_name(e) for e in page_entities]
            props_parts = [f"{p}, {s}" for p, s in zip(prop_names, setter_names)]
            funct_name = name.replace(" ", "")
            bp["spec"] = {
                "frontend_props": {
                    "signature": f"function {funct_name}({{ {', '.join(props_parts)} }})",
                    "destructure": ", ".join(props_parts),
                }
            }

        files.append(bp)

    return files


def _build_database_files(
    database: str, backend_fw: str, entities: List[Dict],
) -> List[Dict[str, Any]]:
    files = []
    db_kind = _db_kind(database)

    if db_kind == "sql":
        files.append({
            "path": "migrations/001_initial.sql",
            "type": "database",
            "purpose": "Initial SQL schema — tables for all SRS entities",
            "reason_for_existence": f"Database: {database}",
            "source_requirement": "database_schema",
            "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [], "provides": [], "requirements": ["schema creation"],
        })
        files.append({
            "path": "seeds/seed.sql",
            "type": "database",
            "purpose": "SQL seed data for development",
            "reason_for_existence": f"Database: {database}",
            "source_requirement": "database_seed",
            "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": ["migrations/001_initial.sql"],
            "provides": [], "requirements": ["seed data"],
        })

    elif db_kind == "mongo":
        ext = ".py" if "fastapi" in backend_fw or "python" in backend_fw else ".js"
        db_deps = [f"backend/src/models/{_entity_route_name(e.get('name', ''))}.js" for e in entities if e.get("name")] + ["backend/src/models/index.js"] if ext == ".js" else [f"app/models/{_entity_route_name(e.get('name', ''))}.py" for e in entities if e.get("name")] + ["app/models/__init__.py"]
        files.append({
            "path": f"seeds/seed{ext}",
            "type": "database",
            "purpose": "MongoDB seed data for development",
            "reason_for_existence": f"Database: {database}",
            "source_requirement": "database_seed",
            "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": db_deps,
            "provides": [], "requirements": ["seed data"],
        })

    return files


def _wire_app_deps(files: List[Dict[str, Any]]) -> None:
    app_bp = None
    for f in files:
        if f["path"] in ("frontend/src/App.jsx", "frontend/src/App.tsx", "frontend/src/App.vue"):
            app_bp = f
            break
    if app_bp is not None:
        page_paths = [f["path"] for f in files if f["type"] == "page"]
        css_paths = [f["path"] for f in files if f["path"] in ("frontend/src/App.css", "frontend/src/index.css")]
        app_bp["depends_on"] = css_paths + page_paths


def _assign_bundles(files: List[Dict[str, Any]]) -> None:
    for f in files:
        f["bundle"] = _infer_bundle(f)


def _infer_bundle(blueprint: dict) -> str:
    path = blueprint.get("path", "")
    ftype = blueprint.get("type", "")

    if ftype == "documentation" or path == "README.md":
        return "docs"
    if ftype == "database":
        return "database"
    if path.startswith("migrations/") or path.startswith("seeds/"):
        return "database"
    if ftype == "page":
        return "frontend"
    if path.startswith("frontend/"):
        return "frontend"
    if path.startswith("backend/") or path.startswith("app/"):
        return "backend"
    return "backend"


def _apply_deterministic_static_content(files: List[Dict[str, Any]], project_name: str, backend_fw: str, frontend_fw: str, database: str, entities: List[Dict[str, Any]]) -> None:
    db_kind = _db_kind(database)
    is_ts = "typescript" in frontend_fw or "ts" in frontend_fw
    is_tailwind = "tailwind" in frontend_fw
    ext = "tsx" if is_ts else "jsx"
    
    express_route_imports = []
    express_route_mounts = []
    fastapi_router_imports = []
    fastapi_router_includes = []
    
    for f in files:
        path = f["path"]
        if path.startswith("backend/src/routes/") and path != "backend/src/routes/index.js":
            stem = Path(path).stem
            express_route_imports.append(f"const {stem.replace('-', '_')}Router = require('./{stem}');")
            express_route_mounts.append(f"router.use('/{stem}', {stem.replace('-', '_')}Router);")
        elif path.startswith("app/routers/") and path != "app/routers/__init__.py":
            stem = Path(path).stem
            fastapi_router_imports.append(f"from app.routers import {stem}")
            fastapi_router_includes.append(f"app.include_router({stem}.router, prefix='/api/{stem}', tags=['{stem}'])")

    for f in files:
        path = f["path"]
        
        if path == "README.md":
            f["static_content"] = f"""# {project_name}

Generated dynamically via AUTO_DEV pipeline.

## Project Structure
- Frontend: {frontend_fw or 'None'}
- Backend: {backend_fw or 'None'}
- Database: {database or 'None'}

## Installation & Setup

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
npm install
npm start
```
"""
        elif path == "frontend/.env":
            f["static_content"] = "VITE_API_URL=/api\n"
        elif path == "frontend/package.json":
            if "react" in frontend_fw or "next" in frontend_fw:
                deps = {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-router-dom": "^6.20.0",
                    "axios": "^1.6.2"
                }
                dev_deps = {
                    "@vitejs/plugin-react": "^4.2.0",
                    "vite": "^5.0.0"
                }
                if is_ts:
                    dev_deps.update({
                        "typescript": "^5.2.2",
                        "@types/react": "^18.2.37",
                        "@types/react-dom": "^18.2.15"
                    })
                f["static_content"] = json.dumps({
                    "name": project_name.lower().replace(" ", "-") + "-frontend",
                    "private": True,
                    "version": "1.0.0",
                    "type": "module",
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview"
                    },
                    "dependencies": deps,
                    "devDependencies": dev_deps
                }, indent=2)
            elif "vue" in frontend_fw:
                f["static_content"] = json.dumps({
                    "name": project_name.lower().replace(" ", "-") + "-frontend",
                    "private": True,
                    "version": "1.0.0",
                    "type": "module",
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "preview": "vite preview"
                    },
                    "dependencies": {
                        "vue": "^3.3.8",
                        "vue-router": "^4.2.5",
                        "axios": "^1.6.2"
                    },
                    "devDependencies": {
                        "@vitejs/plugin-vue": "^4.5.0",
                        "vite": "^5.0.0"
                    }
                }, indent=2)
        elif path in ("frontend/vite.config.js", "frontend/vite.config.ts"):
            plugin_import = 'import react from "@vitejs/plugin-react";' if "react" in frontend_fw else 'import vue from "@vitejs/plugin-vue";'
            plugin_call = 'react()' if "react" in frontend_fw else 'vue()'
            f["static_content"] = f"""import {{ defineConfig }} from "vite";
{plugin_import}

export default defineConfig({{
  plugins: [{plugin_call}],
  server: {{
    port: 3000,
    proxy: {{
      '/api': {{
        target: 'http://localhost:5000',
        changeOrigin: true
      }}
    }}
  }}
}});
"""
        elif path == "frontend/tsconfig.json":
            f["static_content"] = json.dumps({
                "compilerOptions": {
                    "target": "ES2020",
                    "useDefineForClassFields": True,
                    "lib": ["DOM", "DOM.Iterable", "ScriptHost", "ES2020"],
                    "module": "ESNext",
                    "skipLibCheck": True,
                    "moduleResolution": "bundler",
                    "allowImportingTsExtensions": True,
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "noEmit": True,
                    "jsx": "react-jsx",
                    "strict": True,
                    "noUnusedLocals": True,
                    "noUnusedParameters": True,
                    "noFallthroughCasesInSwitch": True
                },
                "include": ["src"]
            }, indent=2)
        elif path == "frontend/src/vite-env.d.ts":
            f["static_content"] = "/// <reference types=\"vite/client\" />\n"
        elif path in ("frontend/postcss.config.js", "frontend/postcss.config.cjs"):
            f["static_content"] = """module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""
        elif path in ("frontend/tailwind.config.js", "frontend/tailwind.config.cjs"):
            f["static_content"] = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,vue}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"""
        elif path == "frontend/index.html":
            script_ext = "tsx" if is_ts else "jsx" if "react" in frontend_fw else "js"
            script_path = f"/src/main.{script_ext}"
            f["static_content"] = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="{script_path}"></script>
  </body>
</html>
"""
        elif path == f"frontend/src/main.{ext}":
            f["static_content"] = f"""import React from "react";
import {{ createRoot }} from "react-dom/client";
import App from "./App";
import "./App.css";

const root = createRoot(document.getElementById("root"));
root.render(<App />);
"""
        elif path == "frontend/src/App.css":
            f["static_content"] = """@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-primary: #0b0f19;
  --bg-secondary: #161b26;
  --bg-tertiary: #1f2638;
  --border-color: #2e374a;
  --text-primary: #f3f4f6;
  --text-secondary: #9ca3af;
  --text-muted: #6b7280;
  --primary: #3b82f6;
  --primary-hover: #2563eb;
  --danger: #ef4444;
  --danger-hover: #dc2626;
  --success: #10b981;
  --radius-lg: 12px;
  --radius-md: 8px;
  --radius-sm: 4px;
  --transition: all 0.2s ease-in-out;
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-family);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-wrapper {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: var(--transition);
}

.nav-link:hover {
  color: var(--primary);
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--text-primary);
}

.page-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 24px;
}

.section h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.form-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 24px;
}

.form-card h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 10px 14px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-family: inherit;
  font-size: 14px;
  transition: var(--transition);
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 20px;
  transition: var(--transition);
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: var(--primary);
}

.stat-card h3 {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-details {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.item-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: var(--transition);
}

.item-card:hover {
  border-color: var(--primary);
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}

.item-details {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 12px;
  flex-grow: 1;
}

.item-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 12px;
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  transition: var(--transition);
  text-decoration: none;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-secondary {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background-color: var(--border-color);
}

.btn-danger {
  background-color: var(--danger);
  color: white;
}

.btn-danger:hover {
  background-color: var(--danger-hover);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.error-message {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--danger);
  color: var(--danger);
  padding: 12px;
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  font-size: 14px;
}

.recent-activity {
  list-style: none;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-color);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-title {
  font-size: 14px;
  color: var(--text-primary);
}

.activity-date {
  font-size: 12px;
  color: var(--text-muted);
}
"""
        elif path in ("frontend/src/services/api.js", "frontend/src/services/api.ts"):
            f["static_content"] = """import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

export default api;
"""
        elif path == "backend/.env":
            db_url = "mongodb://localhost:27017/" + project_name.lower() if db_kind == "mongo" else "postgresql://postgres:postgres@localhost:5432/" + project_name.lower()
            f["static_content"] = f"PORT=5000\nDATABASE_URL={db_url}\nJWT_SECRET=supersecretjwtkey\n"
        elif path == "backend/package.json":
            db_dep = {"mongoose": "^8.0.0"} if db_kind == "mongo" else {"pg": "^8.11.3"} if db_kind == "sql" else {}
            deps = {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "dotenv": "^16.3.1"
            }
            deps.update(db_dep)
            f["static_content"] = json.dumps({
                "name": project_name.lower().replace(" ", "-") + "-backend",
                "version": "1.0.0",
                "main": "src/app.js",
                "scripts": {
                    "start": "node src/app.js"
                },
                "dependencies": deps
            }, indent=2)
        elif path == "backend/src/app.js":
            db_connect = "const connectDB = require('./config/database');\nconnectDB();" if db_kind == "mongo" else "const pool = require('./config/database');"
            f["static_content"] = f"""const express = require('express');
const cors = require('cors');
const config = require('./config');
const apiRouter = require('./routes');
const errorHandler = require('./middleware/errorHandler');

{db_connect}

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api', apiRouter);

app.use(errorHandler);

const PORT = config.port || 5000;
app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});

module.exports = app;
"""
        elif path == "backend/src/config/index.js":
            f["static_content"] = """require('dotenv').config();

module.exports = {
  port: process.env.PORT || 5000,
  databaseUrl: process.env.DATABASE_URL || 'mongodb://localhost:27017/autodev',
  jwtSecret: process.env.JWT_SECRET || 'secret'
};
"""
        elif path == "backend/src/config/database.js":
            if db_kind == "mongo":
                f["static_content"] = """const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.DATABASE_URL || 'mongodb://localhost:27017/autodev');
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`Database Connection Error: ${error.message}`);
    process.exit(1);
  }
};

module.exports = connectDB;
"""
            else:
                f["static_content"] = """const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/autodev'
});

module.exports = pool;
"""
        elif path == "backend/src/middleware/errorHandler.js":
            f["static_content"] = """module.exports = (err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: {
      message: err.message || 'Internal Server Error'
    }
  });
};
"""
        elif path == "backend/src/routes/index.js":
            f["static_content"] = f"""const express = require('express');
const router = express.Router();

{chr(10).join(express_route_imports)}

{chr(10).join(express_route_mounts)}

module.exports = router;
"""
        elif path == "app/core/config.py":
            f["static_content"] = f"""import os

class Settings:
    PROJECT_NAME = "{project_name}"
    DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/autodev")
    PORT = int(os.getenv("PORT", "8000"))

settings = Settings()
"""
        elif path == "app/db/database.py":
            if db_kind == "mongo":
                f["static_content"] = """import os
from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/autodev")
client = AsyncIOMotorClient(DATABASE_URL)
db = client.get_default_database()
"""
            else:
                f["static_content"] = """import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/autodev")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
        elif path == "app/main.py":
            f["static_content"] = f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

{chr(10).join(fastapi_router_imports)}

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {{"message": "Welcome to FastAPI backend"}}

{chr(10).join(fastapi_router_includes)}
"""
        elif path == "main.py":
            f["static_content"] = """import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
"""
        elif path == "requirements.txt":
            db_req = "motor>=3.3.0" if db_kind == "mongo" else "sqlalchemy>=2.0.0\npsycopg2-binary>=2.9.0"
            f["static_content"] = f"fastapi>=0.100.0\nuvicorn>=0.22.0\npydantic>=2.0.0\npython-dotenv>=1.0.0\n{db_req}\n"
        elif path == ".env":
            db_url = "mongodb://localhost:27017/" + project_name.lower() if db_kind == "mongo" else "postgresql://postgres:postgres@localhost:5432/" + project_name.lower()
            f["static_content"] = f"PORT=8000\nDATABASE_URL={db_url}\n"
        elif path == "backend/src/models/index.js":
            imports = []
            exports = []
            for e in entities:
                name = e.get("name", "")
                if name:
                    r_name = _entity_route_name(name)
                    imports.append(f"const {name} = require('./{r_name}');")
                    exports.append(f"  {name},")
            f["static_content"] = "\n".join(imports) + "\n\nmodule.exports = {\n" + "\n".join(exports) + "\n};\n"
        elif path == "app/models/__init__.py":
            imports = []
            for e in entities:
                name = e.get("name", "")
                if name:
                    r_name = _entity_route_name(name)
                    imports.append(f"from app.models.{r_name} import {name}")
            f["static_content"] = "\n".join(imports) + "\n"
        elif path.endswith(".gitignore"):
            f["static_content"] = "node_modules/\n.env\n.env.*\ndist/\nbuild/\n.DS_Store\n"
