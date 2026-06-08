"""Build Plan Generator â€” converts project_rules into a deterministic file blueprint."""

import re
from pathlib import Path
from typing import Any, Dict, List


def generate_build_plan(project_rules: dict) -> dict:
    """Convert project_rules into a structured build plan with file blueprints.

    Args:
        project_rules: Output from rules_engine.build_project_rules()

    Returns:
        Dict with key "files", each entry having path, type, purpose.
    """
    files: List[Dict[str, str]] = []

    # 1. Always include README
    files.append({
        "path": "README.md",
        "type": "documentation",
        "purpose": "Project overview and setup instructions",
        "depends_on": [],
        "provides": [],
        "requirements": [],
    })

    backend_fw = project_rules.get("backend_framework", "").lower()
    frontend_fw = project_rules.get("frontend_framework", "").lower()
    database = project_rules.get("database", "").lower()
    modules = project_rules.get("required_backend_modules", [])
    pages = project_rules.get("required_pages", [])
    auth_method = project_rules.get("auth_method", "")

    # 2. Backend files
    files.extend(_get_backend_files(backend_fw, database, modules, auth_method))

    # 3. Frontend files
    files.extend(_get_frontend_files(frontend_fw, pages, modules, auth_method))

    # 4. Database files
    files.extend(_get_database_files(database, backend_fw, modules, auth_method))

    # 5. Assign bundle membership so the build plan is the source of truth
    for f in files:
        f["bundle"] = _infer_bundle(f)
        f["provides"] = _infer_provides(f["path"], f["type"], database, backend_fw)

    return {"files": files}


def _dedup(items: List[str]) -> List[str]:
    seen: set = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _pascal_case(stem: str) -> str:
    parts = re.split(r"[-_\s]", stem)
    return "".join(p.capitalize() for p in parts)


def _model_name(stem: str) -> str:
    name = _pascal_case(stem)
    if name.endswith("s") and len(name) > 1:
        name = name[:-1]
    return name


def _infer_provides(path: str, ftype: str, database: str = "", backend_fw: str = "") -> List[str]:
    _never_imported = {
        "backend/.gitignore", "backend/.env", "backend/package.json",
        "frontend/package.json", "frontend/.env", "frontend/vite.config.js",
        "frontend/index.html", "postcss.config.js",
        "requirements.txt", "pom.xml", "README.md",
        "frontend/src/main.jsx", "frontend/src/main.js",
    }
    if path in _never_imported:
        return []
    if path.endswith(".css") or path.endswith(".scss"):
        return []
    if path.endswith("__init__.py"):
        return []
    if path.endswith("application.yml"):
        return []

    if ftype == "database" or path.startswith("migrations/") or path.startswith("seeds/"):
        return []

    stem = Path(path).stem
    db_val = (database or "").strip().lower()
    db_kind = (
        "mongo" if "mongo" in db_val
        else "sql" if ("postgres" in db_val or "mysql" in db_val or "sql" in db_val)
        else "unknown"
    )
    fw_val = (backend_fw or "").lower()
    is_node = "express" in fw_val or "node" in fw_val
    is_python = "fastapi" in fw_val or "python" in fw_val

    if ftype == "page":
        return [_pascal_case(stem)]
    if path == "frontend/src/App.jsx" or path == "frontend/src/App.vue":
        return ["App"]
    if path == "frontend/src/services/api.js":
        return ["api"]
    if path.startswith("frontend/src/pages/") or path.startswith("frontend/src/views/"):
        return [_pascal_case(stem)]
    if path == "frontend/src/router/index.js":
        return ["router"]

    if is_node:
        if path == "backend/src/config/database.js":
            return ["connectDB"] if db_kind == "mongo" else ["pool"]
        if path == "backend/src/app.js":
            return ["app"]
        if path.startswith("backend/src/models/"):
            return [_model_name(stem)]
        if path.startswith("backend/src/routes/"):
            return ["router"]
        if path == "backend/src/middleware/auth.js":
            return ["authenticateToken"]
        if path == "backend/src/middleware/errorHandler.js":
            return ["errorHandler"]

    if is_python:
        if path == "app/db/database.py":
            return ["db", "get_db"]
        if path == "app/main.py":
            return ["app"]
        if path == "app/core/config.py":
            return ["settings"]
        if path == "app/core/security.py":
            return ["get_current_user"]
        if path == "app/db/base.py":
            return ["Base"]
        if path.startswith("app/models/"):
            return [_model_name(stem)]
        if path.startswith("app/routers/"):
            return ["router"]
        if path.startswith("app/schemas/"):
            return [_model_name(stem)]
        if path.startswith("app/services/"):
            return [_model_name(stem)]

    return []


def _infer_bundle(blueprint: dict) -> str:
    path = blueprint.get("path", "")
    ftype = blueprint.get("type", "")
    purpose = blueprint.get("purpose", "")

    if ftype == "documentation" or path == "README.md":
        return "docs"
    if ftype == "database":
        return "database"
    if path.startswith("migrations/") or path.startswith("seeds/"):
        return "database"
    if "migration" in purpose.lower() or "seed" in purpose.lower():
        return "database"
    if ftype == "page":
        return "frontend"
    if "frontend" in purpose.lower() or "react" in purpose.lower() or "vue" in purpose.lower():
        return "frontend"
    if path.startswith("frontend/"):
        return "frontend"
    if path.startswith("backend/"):
        return "backend"
    return "backend"


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------


def _auth_is_meaningful(auth_method: str) -> bool:
    """Return True when auth_method is a real value worth generating routes for."""
    val = (auth_method or "").strip().lower()
    return val not in ("", "unknown", "none", "false", "0", "no-auth", "no auth")


def _db_kind(database: str) -> str:
    val = (database or "").strip().lower()
    if "mongo" in val:
        return "mongo"
    if "postgres" in val or "mysql" in val or "sql" in val:
        return "sql"
    return "unknown"

def _get_backend_files(backend_fw: str, database: str, modules: List[str], auth_method: str = "") -> List[Dict[str, str]]:
    modules = _dedup(modules)
    if "express" in backend_fw or "node" in backend_fw:
        return _node_backend_files(modules, database, auth_method)
    if "fastapi" in backend_fw or "python" in backend_fw:
        return _python_backend_files(modules, database, auth_method)
    if "spring" in backend_fw or "java" in backend_fw:
        return _java_backend_files(modules, auth_method)
    return _generic_backend_files(modules, auth_method)


def _build_route_spec(module: str, db_kind: str, auth_enabled: bool) -> dict:
    is_mongo = db_kind == "mongo"
    model_name = _model_name(module)
    operations = (
        ["find", "findById", "create", "findByIdAndUpdate", "findByIdAndDelete"]
        if is_mongo
        else ["query", "queryById", "insert", "updateById", "deleteById"]
    )
    endpoints = [
        {"method": "GET", "path": "/stats", "auth": auth_enabled,
         "description": "Return count of total documents"},
        {"method": "GET", "path": "/", "auth": auth_enabled,
         "description": "Return all documents"},
        {"method": "GET", "path": "/:id", "auth": auth_enabled,
         "description": "Return single document by id or 404"},
        {"method": "POST", "path": "/", "auth": auth_enabled,
         "description": "Create and return new document with 201"},
        {"method": "PUT", "path": "/:id", "auth": auth_enabled,
         "description": "Update by id, return updated document"},
        {"method": "DELETE", "path": "/:id", "auth": auth_enabled,
         "description": "Delete by id, return 204"},
    ]
    if module == "calculator":
        endpoints.append(
            {"method": "POST", "path": "/evaluate", "auth": False,
             "description": "evaluate math expression, return { result: number }"}
        )

    middleware = []
    if auth_enabled:
        middleware.append({
            "name": "authenticateToken",
            "path": "../middleware/auth",
            "apply": "router.use(authenticateToken)",
        })
    return {
        "endpoints": endpoints,
        "middleware": middleware,
        "model": {
            "name": model_name,
            "path": f"../models/{module}",
            "operations": operations,
        },
        "populate": {},
    }


def _node_backend_files(modules: List[str], database: str, auth_method: str = "") -> List[Dict[str, str]]:
    auth_enabled = _auth_is_meaningful(auth_method)
    db_kind = _db_kind(database)
    db_label = "MongoDB" if db_kind == "mongo" else "PostgreSQL" if db_kind == "sql" else "configured database"
    db_dependency = "mongoose" if db_kind == "mongo" else "pg" if db_kind == "sql" else "database client"
    auth_dependencies = ", jsonwebtoken, bcrypt" if auth_enabled else ""
    auth_note = (
        "mounts public auth routes before protected module routes; auth middleware is applied per-router in route files, not globally in app.js"
        if auth_enabled
        else "has no authentication middleware or authentication dependencies"
    )
    db_purpose = (
        "Database connection setup - exports a mongoose connection helper for MongoDB"
        if db_kind == "mongo"
        else "Database connection setup - exports a pg.Pool instance for raw SQL queries"
        if db_kind == "sql"
        else "Database connection setup for the configured database"
    )
    route_purpose = (
        "{module} API routes - uses the {module} model with Mongoose document operations"
        if db_kind == "mongo"
        else "{module} API routes - uses the {module} model with pg.Pool raw SQL queries"
        if db_kind == "sql"
        else "{module} API routes - uses the {module} model for data access"
    )
    model_purpose = (
        "{module} data model - defines and exports a Mongoose schema/model"
        if db_kind == "mongo"
        else "{module} data model - plain JS module exporting functions that query via pg.Pool"
        if db_kind == "sql"
        else "{module} data model for the configured database"
    )

    route_index_deps = []
    for module in modules:
        if auth_enabled and module == "auth":
            continue
        route_index_deps.append(f"backend/src/routes/{module}.js")

    app_deps = ["backend/src/config/index.js", "backend/src/config/database.js", "backend/src/middleware/errorHandler.js", "backend/src/routes/index.js"]
    if auth_enabled:
        app_deps.insert(2, "backend/src/routes/auth.js")
        app_deps.insert(3, "backend/src/middleware/auth.js")

    files = [
        {"path": "backend/.gitignore", "type": "config", "purpose": "Git ignore rules", "depends_on": [], "provides": [], "requirements": []},
        {"path": "backend/.env", "type": "env", "purpose": "Environment variables", "depends_on": [], "provides": [], "requirements": []},
        {"path": "backend/package.json", "type": "config", "purpose": f"Node.js dependencies and scripts - must include express, {db_dependency}, dotenv, cors{auth_dependencies} as dependencies, nodemon as devDependency; start and dev scripts must run backend/src/app.js because no server.js or src/index.js is generated", "depends_on": [], "provides": [], "requirements": []},
        {"path": "backend/src/app.js", "type": "source", "purpose": f"Express application setup and middleware - imports config, {db_label} database, error handler, and routes/index.js at /api; starts the server with app.listen; {auth_note}", "depends_on": app_deps, "provides": [], "requirements": ["middleware setup", "route mounting", "server start"]},
        {"path": "backend/src/config/index.js", "type": "config", "purpose": "Configuration loader", "depends_on": [], "provides": [], "requirements": ["configuration export"]},
        {"path": "backend/src/config/database.js", "type": "config", "purpose": db_purpose, "depends_on": [], "provides": [], "requirements": ["database connection"]},
        {"path": "backend/src/middleware/errorHandler.js", "type": "source", "purpose": "Global error handler", "depends_on": [], "provides": [], "requirements": ["error handling"]},
        {"path": "backend/src/routes/index.js", "type": "source", "purpose": "Route aggregator - imports and mounts exactly the route files listed in depends_on",
         "spec": {"mounts": [{"path": f"/{m}", "router": f"./{m}"} for m in modules if not (auth_enabled and m == "auth")]},
         "depends_on": route_index_deps, "provides": [], "requirements": ["route aggregation"]},
    ]

    if auth_enabled:
        files.append({
            "path": "backend/src/middleware/auth.js",
            "type": "source",
            "purpose": "Authentication middleware - verifies JWT from Authorization header and adds req.user",
            "spec": {
                "jwt_payload": {"id": "user._id", "email": "user.email"},
                "req_user_assignment": "req.user = decoded",
            },
            "depends_on": ["backend/src/config/database.js"],
            "provides": [],
            "requirements": ["JWT verification", "token validation"],
        })
        auth_ops = ["findOne", "create"] if db_kind == "mongo" else ["query", "insert"]
        files.append({
            "path": "backend/src/routes/auth.js",
            "type": "source",
            "purpose": (
                "Authentication routes (login, register, logout) - uses Mongoose user model, bcrypt for passwords, jwt for tokens"
                if db_kind == "mongo"
                else "Authentication routes (login, register, logout) - uses pg.Pool user model, bcrypt for passwords, jwt for tokens"
            ),
            "spec": {
                "endpoints": [
                    {"method": "POST", "path": "/register", "auth": False,
                     "description": "Register a new user, return JWT token with 201"},
                    {"method": "POST", "path": "/login", "auth": False,
                     "description": "Authenticate user by email and password, return JWT token"},
                    {"method": "POST", "path": "/logout", "auth": False,
                     "description": "Logout (client-side token removal)"},
                ],
                "middleware": [],
                "model": {
                    "name": "User",
                    "path": "../models/users",
                    "operations": auth_ops,
                },
                "populate": {},
            },
            "depends_on": ["backend/src/config/database.js", "backend/src/models/users.js"],
            "provides": [],
        })
        if "users" not in modules:
            files.append({
                "path": "backend/src/models/users.js",
                "type": "module",
                "purpose": (
                    "User data model for authentication - defines and exports a Mongoose schema/model"
                    if db_kind == "mongo"
                    else "User data model for authentication - plain JS module exporting functions that query via pg.Pool"
                ),
                "depends_on": [],
                "provides": [],
                "requirements": ["model definition"],
            })

    for module in modules:
        if auth_enabled and module == "auth":
            continue
        route_deps = ["backend/src/config/database.js", f"backend/src/models/{module}.js"]
        if auth_enabled:
            route_deps.insert(0, "backend/src/middleware/auth.js")
        files.append({
            "path": f"backend/src/routes/{module}.js",
            "type": "module",
            "purpose": route_purpose.format(module=module),
            "spec": _build_route_spec(module, db_kind, auth_enabled),
            "depends_on": route_deps,
            "provides": [],
        })
        files.append({
            "path": f"backend/src/models/{module}.js",
            "type": "module",
            "purpose": model_purpose.format(module=module),
            "depends_on": [],
            "provides": [],
            "requirements": ["model definition"],
        })
    return files


def _python_backend_files(modules: List[str], database: str, auth_method: str = "") -> List[Dict[str, str]]:
    auth_enabled = _auth_is_meaningful(auth_method)
    db_kind = _db_kind(database)
    app_main_deps = ["app/core/config.py", "app/db/database.py"]
    if auth_enabled:
        app_main_deps.append("app/core/security.py")

    router_deps = []
    if auth_enabled:
        router_deps.append("app/routers/auth.py")
    for module in modules:
        if auth_enabled and module == "auth":
            continue
        router_deps.append(f"app/routers/{module}.py")
    app_main_deps.extend(router_deps)

    db_purpose = (
        "MongoDB connection using Motor AsyncIOMotorClient"
        if db_kind == "mongo"
        else "SQL database connection using SQLAlchemy engine/session"
        if db_kind == "sql"
        else "Database connection for the configured database"
    )
    model_purpose = (
        "{module} MongoDB document model using Pydantic-compatible fields"
        if db_kind == "mongo"
        else "{module} SQLAlchemy model"
    )
    service_purpose = (
        "{module} business logic using Motor/MongoDB collection operations"
        if db_kind == "mongo"
        else "{module} business logic using SQLAlchemy session operations"
    )

    files = [
        {"path": ".gitignore", "type": "config", "purpose": "Git ignore rules", "depends_on": [], "provides": [], "requirements": []},
        {"path": ".env", "type": "env", "purpose": "Environment variables", "depends_on": [], "provides": [], "requirements": []},
        {"path": "requirements.txt", "type": "config", "purpose": f"Python dependencies for FastAPI and {'Motor MongoDB' if db_kind == 'mongo' else 'SQLAlchemy'}{' with JWT security' if auth_enabled else ''}", "depends_on": [], "provides": [], "requirements": []},
        {"path": "main.py", "type": "source", "purpose": "Application entry point", "depends_on": ["app/main.py"], "provides": [], "requirements": ["app startup"]},
        {"path": "app/__init__.py", "type": "source", "purpose": "App package init", "depends_on": [], "provides": [], "requirements": []},
        {"path": "app/main.py", "type": "source", "purpose": "FastAPI application setup", "depends_on": app_main_deps, "provides": [], "requirements": ["app setup", "router mounting"]},
        {"path": "app/core/config.py", "type": "config", "purpose": "Configuration settings", "depends_on": [], "provides": [], "requirements": ["configuration settings"]},
        {"path": "app/db/database.py", "type": "config", "purpose": db_purpose, "depends_on": [], "provides": [], "requirements": ["database connection"]},
    ]

    if auth_enabled:
        files.append({"path": "app/core/security.py", "type": "source", "purpose": "JWT authentication and password security utilities", "depends_on": ["app/core/config.py"], "provides": [], "requirements": ["security configuration"]})
    if db_kind == "sql":
        files.append({"path": "app/db/base.py", "type": "config", "purpose": "SQLAlchemy declarative base", "depends_on": ["app/db/database.py"], "provides": [], "requirements": ["declarative base"]})
    if auth_enabled:
        files.append({
            "path": "app/routers/auth.py",
            "type": "source",
            "purpose": "Authentication routes (login, register, logout)",
            "depends_on": ["app/db/database.py", "app/models/user.py"],
            "provides": [],
            "requirements": ["login", "register", "logout"],
        })
        if "user" not in modules:
            files.append({
                "path": "app/models/user.py",
                "type": "module",
                "purpose": (
                    "User MongoDB document model for authentication"
                    if db_kind == "mongo"
                    else "User SQLAlchemy model for authentication"
                ),
                "depends_on": [],
                "provides": [],
                "requirements": ["model definition"],
            })

    for module in modules:
        if auth_enabled and module == "auth":
            continue
        files.append({
            "path": f"app/routers/{module}.py",
            "type": "module",
            "purpose": f"{module} API routes",
            "depends_on": [f"app/schemas/{module}.py", f"app/services/{module}.py"],
            "provides": [],
            "requirements": ["list", "create", "update", "delete"],
        })
        files.append({
            "path": f"app/schemas/{module}.py",
            "type": "module",
            "purpose": f"{module} Pydantic schemas",
            "depends_on": [],
            "provides": [],
            "requirements": ["schema definition"],
        })
        files.append({
            "path": f"app/models/{module}.py",
            "type": "module",
            "purpose": model_purpose.format(module=module),
            "depends_on": [],
            "provides": [],
            "requirements": ["model definition"],
        })
        files.append({
            "path": f"app/services/{module}.py",
            "type": "module",
            "purpose": service_purpose.format(module=module),
            "depends_on": [f"app/models/{module}.py"],
            "provides": [],
            "requirements": ["business logic"],
        })
    return files

def _java_backend_files(modules: List[str], auth_method: str = "") -> List[Dict[str, str]]:
    files = [
        {"path": ".gitignore", "type": "config", "purpose": "Git ignore rules", "depends_on": [], "provides": [], "requirements": []},
        {"path": "pom.xml", "type": "config", "purpose": "Maven build configuration", "depends_on": [], "provides": [], "requirements": []},
        {"path": "src/main/resources/application.yml", "type": "config", "purpose": "Application configuration", "depends_on": [], "provides": [], "requirements": []},
        {"path": "src/main/java/com/app/Application.java", "type": "source", "purpose": "Application entry point", "depends_on": [], "provides": [], "requirements": ["application startup"]},
        {"path": "src/main/java/com/app/config/SecurityConfig.java", "type": "source", "purpose": "Security configuration", "depends_on": ["src/main/resources/application.yml"], "provides": [], "requirements": ["security configuration"]},
        {"path": "src/main/java/com/app/config/DatabaseConfig.java", "type": "config", "purpose": "Database configuration", "depends_on": ["src/main/resources/application.yml"], "provides": [], "requirements": ["database configuration"]},
    ]
    if _auth_is_meaningful(auth_method):
        files.append({
            "path": "src/main/java/com/app/controller/AuthController.java",
            "type": "source",
            "purpose": "Authentication REST controller (login, register, logout)",
            "depends_on": [],
            "provides": [],
            "requirements": ["login", "register", "logout"],
        })
    for module in modules:
        base = f"src/main/java/com/app/{module}"
        files.append({
            "path": f"{base}/{module.capitalize()}Controller.java",
            "type": "module",
            "purpose": f"{module} REST controller",
            "depends_on": [f"{base}/{module.capitalize()}Service.java"],
            "provides": [],
            "requirements": ["list", "create", "update", "delete"],
        })
        files.append({
            "path": f"{base}/{module.capitalize()}Service.java",
            "type": "module",
            "purpose": f"{module} service layer",
            "depends_on": [f"{base}/{module.capitalize()}Repository.java"],
            "provides": [],
            "requirements": ["business logic"],
        })
        files.append({
            "path": f"{base}/{module.capitalize()}Repository.java",
            "type": "module",
            "purpose": f"{module} data repository",
            "depends_on": [f"{base}/{module.capitalize()}Entity.java"],
            "provides": [],
            "requirements": ["data access"],
        })
        files.append({
            "path": f"{base}/{module.capitalize()}Entity.java",
            "type": "module",
            "purpose": f"{module} JPA entity",
            "depends_on": [],
            "provides": [],
            "requirements": ["entity definition"],
        })
    return files


def _generic_backend_files(modules: List[str], auth_method: str = "") -> List[Dict[str, str]]:
    files = [
        {"path": "backend/.gitignore", "type": "config", "purpose": "Git ignore rules", "depends_on": [], "provides": [], "requirements": []},
        {"path": "backend/.env", "type": "env", "purpose": "Environment variables", "depends_on": [], "provides": [], "requirements": []},
        {"path": "backend/src/app.js", "type": "source", "purpose": "Application entry point", "depends_on": ["backend/src/config/index.js"], "provides": [], "requirements": ["application setup"]},
        {"path": "backend/src/config/index.js", "type": "config", "purpose": "Configuration loader", "depends_on": [], "provides": [], "requirements": ["configuration export"]},
    ]
    if _auth_is_meaningful(auth_method):
        files.append({
            "path": "backend/src/routes/auth.js",
            "type": "source",
            "purpose": "Authentication routes (login, register, logout)",
            "depends_on": [],
            "provides": [],
            "requirements": ["login", "register", "logout"],
        })
    for module in modules:
        files.append({
            "path": f"backend/src/{module}/index.js",
            "type": "module",
            "purpose": f"{module} module entry",
            "depends_on": [],
            "provides": [],
            "requirements": ["module functions"],
        })
    return files


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------


def _get_frontend_files(frontend_fw: str, pages: List[str], modules: List[str], auth_method: str) -> List[Dict[str, str]]:
    pages = _dedup(pages)
    if "react" in frontend_fw or "next" in frontend_fw:
        return _react_frontend_files(pages, modules, auth_method)
    if "vue" in frontend_fw:
        return _vue_frontend_files(pages)
    return _generic_frontend_files(pages)


def _build_page_api_calls(page_name: str, modules: List[str], auth_method: str) -> List[dict]:
    """Build api_calls spec for a frontend page blueprint."""
    page_lower = page_name.lower().strip()

    if page_lower == "login":
        return [
            {"method": "POST", "endpoint": "/auth/login", "body": ["email", "password"]},
        ]
    if page_lower == "register":
        return [
            {"method": "POST", "endpoint": "/auth/register", "body": ["email", "password", "name"]},
        ]
    if page_lower == "dashboard":
        return [
            {"method": "GET", "endpoint": f"/{m}/stats"} for m in modules
        ]

    for m in modules:
        if m.lower() == page_lower:
            return [
                {"method": "GET", "endpoint": f"/{m}"},
                {"method": "POST", "endpoint": f"/{m}"},
                {"method": "PUT", "endpoint": f"/{m}/:id"},
                {"method": "DELETE", "endpoint": f"/{m}/:id"},
            ]

    return []


def _react_frontend_files(pages: List[str], modules: List[str], auth_method: str) -> List[Dict[str, str]]:
    page_paths = [f"frontend/src/pages/{_sanitize_page_name(p)}.jsx" for p in pages]

    files = [
        {"path": "frontend/package.json", "type": "config", "purpose": "Frontend dependencies and scripts â€” must include react, react-dom, react-router-dom, axios, vite, @vitejs/plugin-react", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/.env", "type": "env", "purpose": "Frontend environment variables - must define VITE_API_BASE_URL=http://localhost:5000/api", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/vite.config.js", "type": "config", "purpose": "Vite build configuration", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/index.html", "type": "source", "purpose": "HTML entry point", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/src/main.jsx", "type": "source", "purpose": "React entry point", "depends_on": ["frontend/src/App.jsx"], "provides": [], "requirements": ["app rendering"]},
        {"path": "frontend/src/App.jsx", "type": "source", "purpose": "Root application component with routing", "depends_on": page_paths, "provides": [], "requirements": ["component export", "route configuration"]},
        {"path": "frontend/src/App.css", "type": "source", "purpose": "Global application styles", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/src/services/api.js", "type": "source", "purpose": "API client configuration using axios â€” uses import.meta.env.VITE_API_BASE_URL (Vite convention, not process.env)", "depends_on": [], "provides": [], "requirements": ["import axios"]},
    ]
    for page in pages:
        safe = _sanitize_page_name(page)
        api_calls = _build_page_api_calls(page, modules, auth_method)
        bp = {
            "path": f"frontend/src/pages/{safe}.jsx",
            "type": "page",
            "purpose": f"{page} page",
            "depends_on": ["frontend/src/services/api.js"],
            "provides": [],
            "requirements": ["component export"],
        }
        if api_calls:
            bp["spec"] = {"api_calls": api_calls}
        files.append(bp)
    return files


def _vue_frontend_files(pages: List[str]) -> List[Dict[str, str]]:
    view_paths = [f"frontend/src/views/{_sanitize_page_name(p)}.vue" for p in pages]

    files = [
        {"path": "frontend/package.json", "type": "config", "purpose": "Frontend dependencies and scripts", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/.env", "type": "env", "purpose": "Frontend environment variables - must define VITE_API_BASE_URL=http://localhost:5000/api", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/vite.config.js", "type": "config", "purpose": "Vite build configuration", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/index.html", "type": "source", "purpose": "HTML entry point", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/src/main.js", "type": "source", "purpose": "Vue entry point", "depends_on": ["frontend/src/App.vue"], "provides": [], "requirements": ["app mounting"]},
        {"path": "frontend/src/App.vue", "type": "source", "purpose": "Root application component", "depends_on": ["frontend/src/router/index.js"], "provides": [], "requirements": ["component export"]},
        {"path": "frontend/src/router/index.js", "type": "source", "purpose": "Vue Router configuration", "depends_on": view_paths, "provides": [], "requirements": ["route configuration"]},
        {"path": "frontend/src/services/api.js", "type": "source", "purpose": "API client configuration using axios â€” uses import.meta.env.VITE_API_BASE_URL", "depends_on": [], "provides": [], "requirements": ["import axios"]},
    ]
    for page in pages:
        safe = _sanitize_page_name(page)
        files.append({
            "path": f"frontend/src/views/{safe}.vue",
            "type": "page",
            "purpose": f"{page} page view",
            "depends_on": ["frontend/src/services/api.js"],
            "provides": [],
            "requirements": ["component export"],
        })
    return files


def _generic_frontend_files(pages: List[str]) -> List[Dict[str, str]]:
    page_paths = [f"frontend/src/pages/{_sanitize_page_name(p)}.js" for p in pages]

    files = [
        {"path": "frontend/package.json", "type": "config", "purpose": "Frontend dependencies and scripts", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/index.html", "type": "source", "purpose": "HTML entry point", "depends_on": [], "provides": [], "requirements": []},
        {"path": "frontend/src/main.js", "type": "source", "purpose": "Application entry point", "depends_on": page_paths, "provides": [], "requirements": ["app rendering"]},
    ]
    for page in pages:
        safe = _sanitize_page_name(page)
        files.append({
            "path": f"frontend/src/pages/{safe}.js",
            "type": "page",
            "purpose": f"{page} page",
            "depends_on": [],
            "provides": [],
            "requirements": ["page content"],
        })
    return files


def _sanitize_page_name(name: str) -> str:
    """Convert a page label like 'Workspace overview' to a safe filename 'WorkspaceOverview'."""
    clean = "".join(part.capitalize() for part in name.split())
    return clean if clean else "Page"


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------


def _get_database_files(database: str, backend_fw: str = "", modules: List[str] = None, auth_method: str = "") -> List[Dict[str, str]]:
    files: List[Dict[str, str]] = []
    db_kind = _db_kind(database)
    backend_val = (backend_fw or "").lower()
    if db_kind == "sql":
        files.append({
            "path": "migrations/001_initial.sql",
            "type": "database",
            "purpose": "Initial SQL database schema migration",
            "depends_on": [],
            "provides": [],
            "requirements": ["schema creation"],
        })
        files.append({
            "path": "seeds/seed.sql",
            "type": "database",
            "purpose": "SQL seed data for development",
            "depends_on": ["migrations/001_initial.sql"],
            "provides": [],
            "requirements": ["seed data"],
        })
    elif db_kind == "mongo":
        seed_path = "seeds/seed.py" if "fastapi" in backend_val or "python" in backend_val else "seeds/seed.js"
        db_dep = "app/db/database.py" if seed_path.endswith(".py") else "backend/src/config/database.js"
        depends_on = [db_dep]
        model_deps = []
        if _auth_is_meaningful(auth_method):
            model_deps.append("app/models/user.py" if seed_path.endswith(".py") else "backend/src/models/users.js")
        for module in (modules or []):
            model_deps.append(f"app/models/{module}.py" if seed_path.endswith(".py") else f"backend/src/models/{module}.js")
        depends_on.extend(_dedup(model_deps))
        files.append({
            "path": seed_path,
            "type": "database",
            "purpose": "MongoDB seed data script for development",
            "depends_on": depends_on,
            "provides": [],
            "requirements": ["seed data"],
        })
    return files


