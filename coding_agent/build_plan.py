"""Build Plan Generator — converts SRS + Knowledge into a deterministic file blueprint.

Every file must have requirement lineage:
- reason_for_existence: why this file exists
- source_requirement: which SRS requirement created it
- source_page: which SRS page created it
- source_entity: which SRS entity created it
- source_flow: which SRS flow created it

No file is generated without answering: which SRS entry created it?
"""

import re
from pathlib import Path
from typing import Any, Dict, List


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

    # Backend config files (tech stack infrastructure — minimal)
    files.extend(_build_backend_config(backend_fw, database))

    # Backend entity files — one route + model per SRS entity
    files.extend(_build_entity_artifacts(backend_fw, database, entities, flow))

    # Backend flow-specific endpoints (non-CRUD operations from flow)
    files.extend(_build_flow_endpoints(backend_fw, database, flow, entities))

    # Determine if a backend framework is configured
    has_backend = bool(backend_fw)

    # Frontend config files
    files.extend(_build_frontend_config(frontend_fw, has_backend))

    # Frontend pages — ONLY from SRS.pages
    files.extend(_build_pages(frontend_fw, pages, entities, has_backend))

    # Database files
    files.extend(_build_database_files(database, backend_fw, entities))

    # Dynamically connect frontend pages and styles to the main App component
    app_bp = None
    for f in files:
        if f["path"] in ("frontend/src/App.jsx", "frontend/src/App.tsx", "frontend/src/App.vue"):
            app_bp = f
            break
    if app_bp is not None:
        page_paths = [f["path"] for f in files if f["type"] == "page"]
        css_paths = [f["path"] for f in files if f["path"] in ("frontend/src/App.css", "frontend/src/index.css")]
        app_bp["depends_on"] = css_paths + page_paths

    # Assign bundle
    for f in files:
        f["bundle"] = _infer_bundle(f)

    return {"files": files}


def _pascal_case(stem: str) -> str:
    parts = re.split(r"[-_\s]", stem)
    return "".join(p.capitalize() for p in parts)


def _sanitize_page_name(name: str) -> str:
    clean = "".join(part.capitalize() for part in name.split())
    return clean if clean else "Page"


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
            files.append({
                "path": f"backend/src/routes/{route_name}.js",
                "type": "module",
                "purpose": f"{name} API routes — CRUD + flow-specific endpoints",
                "reason_for_existence": f"SRS entity: {name}",
                "source_requirement": "entity_api",
                "source_page": "",
                "source_entity": name,
                "source_flow": "; ".join(entity_flows) if entity_flows else "",
                "depends_on": [db_dep_file, f"backend/src/models/{route_name}.js"],
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
                "depends_on": [db_dep_file],
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
            files.append({
                "path": f"app/routers/{route_name}.py",
                "type": "module",
                "purpose": f"{name} API routes — CRUD + flow-specific endpoints",
                "reason_for_existence": f"SRS entity: {name}",
                "source_requirement": "entity_api",
                "source_page": "",
                "source_entity": name,
                "source_flow": "; ".join(entity_flows) if entity_flows else "",
                "depends_on": [f"app/schemas/{route_name}.py", f"app/models/{route_name}.py"],
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
                "depends_on": [f"app/models/{route_name}.py"],
                "provides": [],
                "requirements": ["business logic"],
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
                files.append({
                    "path": route_path,
                    "type": "module",
                    "purpose": f"Flow-specific endpoints for {ent_name} — {f.get('name', '')}",
                    "reason_for_existence": f"SRS flow: {f.get('name', '')}",
                    "source_requirement": "flow_endpoint",
                    "source_page": "",
                    "source_entity": ent_name,
                    "source_flow": f.get("name", ""),
                    "depends_on": [f"backend/src/models/{route_name}.js"],
                    "provides": [],
                    "requirements": [],
                })

    return files


def _build_frontend_config(frontend_fw: str, has_backend: bool = True) -> List[Dict[str, Any]]:
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
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "frontend/.env", "type": "env",
             "purpose": "Frontend environment variables",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": f"frontend/vite.config.{'ts' if is_ts else 'js'}", "type": "config",
             "purpose": f"Vite build configuration for React {'with TypeScript support' if is_ts else ''}",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "frontend/index.html", "type": "source",
             "purpose": f"HTML entry point referencing /src/main.{ext}",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": f"frontend/src/main.{ext}", "type": "source",
             "purpose": "React entry point rendering Root component",
             "reason_for_existence": f"Tech stack: {frontend_fw}",
             "source_requirement": "tech_stack", "source_page": "", "source_entity": "", "source_flow": "",
             "depends_on": [f"frontend/src/App.{ext}"], "provides": [], "requirements": ["app rendering"]},
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

        bp = {
            "path": page_path,
            "type": "page",
            "purpose": purpose or f"{name} page",
            "reason_for_existence": f"SRS page: {name}",
            "source_requirement": "page_definition",
            "source_page": name,
            "source_entity": "; ".join(page_entities) if page_entities else "",
            "source_flow": "",
            "depends_on": [],
            "provides": [],
            "requirements": ["component export"],
        }

        # Build api_calls spec from entities referenced by this page (backend only)
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
        files.append({
            "path": f"seeds/seed{ext}",
            "type": "database",
            "purpose": "MongoDB seed data for development",
            "reason_for_existence": f"Database: {database}",
            "source_requirement": "database_seed",
            "source_page": "", "source_entity": "", "source_flow": "",
            "depends_on": [],
            "provides": [], "requirements": ["seed data"],
        })

    return files


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
