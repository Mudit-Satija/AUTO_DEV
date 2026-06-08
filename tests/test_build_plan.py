from coding_agent.build_plan import generate_build_plan


def test_readme_always_included():
    plan = generate_build_plan(_node_react_postgres_rules())
    paths = [f["path"] for f in plan["files"]]
    assert "README.md" in paths


def test_node_backend_core_files():
    plan = generate_build_plan(_node_react_postgres_rules())
    paths = [f["path"] for f in plan["files"]]
    assert "backend/package.json" in paths
    assert "backend/src/app.js" in paths
    assert "backend/src/config/index.js" in paths
    assert "backend/src/config/database.js" in paths
    assert "backend/src/middleware/auth.js" in paths
    assert "backend/src/middleware/errorHandler.js" in paths
    assert "backend/src/routes/index.js" in paths


def test_node_backend_module_files():
    plan = generate_build_plan(_node_react_postgres_rules())
    paths = [f["path"] for f in plan["files"]]
    assert "backend/src/routes/workspaces.js" in paths
    assert "backend/src/models/workspaces.js" in paths
    assert "backend/src/routes/projects.js" in paths
    assert "backend/src/models/projects.js" in paths
    assert "backend/src/routes/tasks.js" in paths
    assert "backend/src/models/tasks.js" in paths


def test_react_frontend_core_files():
    plan = generate_build_plan(_node_react_postgres_rules())
    paths = [f["path"] for f in plan["files"]]
    assert "frontend/package.json" in paths
    assert "frontend/.env" in paths
    assert "frontend/vite.config.js" in paths
    assert "frontend/index.html" in paths
    assert "frontend/src/main.jsx" in paths
    assert "frontend/src/App.jsx" in paths
    assert "frontend/src/App.css" in paths
    assert "frontend/src/services/api.js" in paths


def test_react_frontend_page_files():
    plan = generate_build_plan(_node_react_postgres_rules())
    paths = [f["path"] for f in plan["files"]]
    assert "frontend/src/pages/Home.jsx" in paths
    assert "frontend/src/pages/Login.jsx" in paths
    assert "frontend/src/pages/Dashboard.jsx" in paths
    assert "frontend/src/pages/Settings.jsx" in paths


def test_postgres_database_files():
    plan = generate_build_plan(_node_react_postgres_rules())
    paths = [f["path"] for f in plan["files"]]
    assert "migrations/001_initial.sql" in paths
    assert "seeds/seed.sql" in paths


def test_empty_modules_and_pages():
    rules = {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "JWT",
        "deployment": "AWS",
        "required_pages": [],
        "required_backend_modules": [],
    }
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "README.md" in paths
    assert "backend/src/app.js" in paths
    assert "frontend/src/main.jsx" in paths
    assert "migrations/001_initial.sql" in paths
    route_paths = [f["path"] for f in plan["files"] if f["path"].startswith("backend/src/routes/") and f["path"] not in ("backend/src/routes/index.js", "backend/src/routes/auth.js")]
    assert not route_paths, f"Unexpected route files: {route_paths}"


def test_python_fastapi_backend():
    rules = _fastapi_vue_postgres_rules()
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "requirements.txt" in paths
    assert "main.py" in paths
    assert "app/__init__.py" in paths
    assert "app/main.py" in paths
    assert "app/core/config.py" in paths
    assert "app/core/security.py" in paths
    assert "app/db/database.py" in paths
    assert "app/routers/workspaces.py" in paths
    assert "app/schemas/workspaces.py" in paths
    assert "app/models/workspaces.py" in paths
    assert "app/services/workspaces.py" in paths


def test_vue_frontend():
    rules = _fastapi_vue_postgres_rules()
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "frontend/src/main.js" in paths
    assert "frontend/src/App.vue" in paths
    assert "frontend/src/router/index.js" in paths
    assert "frontend/src/views/Home.vue" in paths
    assert "frontend/src/views/Dashboard.vue" in paths


def test_java_spring_backend():
    rules = _spring_react_mysql_rules()
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "pom.xml" in paths
    assert "src/main/resources/application.yml" in paths
    assert "src/main/java/com/app/Application.java" in paths
    assert "src/main/java/com/app/config/SecurityConfig.java" in paths
    files = plan["files"]
    controller_files = [f for f in files if f["path"].endswith("Controller.java")]
    assert any("workspaces" in f["path"].lower() for f in controller_files)


def test_project_management_scenario():
    rules = _pm_rules()
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "README.md" in paths
    assert "frontend/src/App.jsx" in paths
    assert "frontend/src/pages/Workspaces.jsx" in paths
    assert "frontend/src/pages/Boards.jsx" in paths
    assert "frontend/src/pages/Tasks.jsx" in paths
    assert "frontend/src/pages/Activity.jsx" in paths
    assert "backend/src/routes/workspaces.js" in paths
    assert "backend/src/routes/projects.js" in paths
    assert "backend/src/routes/tasks.js" in paths
    assert "backend/src/routes/activity.js" in paths
    assert "backend/src/routes/notifications.js" in paths
    assert "migrations/001_initial.sql" in paths


def test_each_file_has_required_keys():
    plan = generate_build_plan(_node_react_postgres_rules())
    for f in plan["files"]:
        assert "path" in f, f"Missing 'path' in {f}"
        assert "type" in f, f"Missing 'type' in {f}"
        assert "purpose" in f, f"Missing 'purpose' in {f}"
        assert "depends_on" in f, f"Missing 'depends_on' in {f}"
        assert "provides" in f, f"Missing 'provides' in {f}"


def test_output_has_files_key():
    plan = generate_build_plan(_node_react_postgres_rules())
    assert "files" in plan
    assert isinstance(plan["files"], list)


def test_deterministic_output():
    rules = _node_react_postgres_rules()
    plan1 = generate_build_plan(rules)
    plan2 = generate_build_plan(rules)
    assert plan1 == plan2


def test_mongodb_files():
    rules = _node_react_mongo_rules()
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "backend/src/config/database.js" in paths
    assert "backend/src/config/mongodb.js" not in paths
    assert "seeds/seed.js" in paths
    assert "migrations/001_initial.sql" not in paths
    purposes = "\n".join(f["purpose"] for f in plan["files"])
    assert "pg.Pool" not in purposes
    assert "SQLAlchemy" not in purposes


def test_unknown_framework_fallback():
    rules = {
        "backend_framework": "Unknown",
        "frontend_framework": "Unknown",
        "database": "Unknown",
        "auth_method": "Unknown",
        "deployment": "Not specified",
        "required_pages": ["Home"],
        "required_backend_modules": ["orders"],
    }
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "README.md" in paths
    assert "backend/src/app.js" in paths
    assert "frontend/src/main.js" in paths
    assert "backend/src/orders/index.js" in paths
    assert "frontend/src/pages/Home.js" in paths


def test_package_json_no_overwrite():
    """Both backend and frontend package.json blueprints exist with unique paths."""
    plan = generate_build_plan(_node_react_postgres_rules())
    paths = [f["path"] for f in plan["files"]]
    backend_count = sum(1 for p in paths if p == "backend/package.json")
    frontend_count = sum(1 for p in paths if p == "frontend/package.json")
    assert "backend/package.json" in paths, "Backend package.json missing"
    assert "frontend/package.json" in paths, "Frontend package.json missing"
    assert backend_count == 1, f"Expected 1 backend package.json, got {backend_count}"
    assert frontend_count == 1, f"Expected 1 frontend package.json, got {frontend_count}"
    total_package = sum(1 for p in paths if "package" in p)
    assert total_package == 2, f"Expected exactly 2 package files, got {total_package}"


def test_no_duplicate_paths():
    """Every file blueprint must have a unique path â€” no overwrites possible."""
    plan = generate_build_plan(_node_react_postgres_rules())
    paths = [f["path"] for f in plan["files"]]
    assert len(paths) == len(set(paths)), f"Duplicate paths detected: {[p for p in paths if paths.count(p) > 1]}"


def test_auth_auto_generates_user_model_node():
    """JWT auth without 'users' module should auto-generate User model in Node/Express."""
    rules = {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "JWT",
        "deployment": "AWS",
        "required_pages": ["Login"],
        "required_backend_modules": ["workspaces"],
    }
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "backend/src/models/users.js" in paths, "User model should be auto-generated when auth is meaningful"


def test_auth_auto_generates_user_model_python():
    """JWT auth without 'user' module should auto-generate User model in Python/FastAPI."""
    rules = {
        "backend_framework": "FastAPI",
        "frontend_framework": "Vue.js",
        "database": "PostgreSQL",
        "auth_method": "JWT",
        "deployment": "Docker",
        "required_pages": ["Login"],
        "required_backend_modules": ["workspaces"],
    }
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "app/models/user.py" in paths, "User model should be auto-generated when auth is meaningful in FastAPI"


def test_auth_user_model_resolves_dependency():
    """When auth is meaningful, the User model dependency should be resolved."""
    rules = {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "JWT",
        "deployment": "AWS",
        "required_pages": ["Login"],
        "required_backend_modules": ["workspaces"],
    }
    plan = generate_build_plan(rules)
    from coding_agent.dependency_graph import validate_graph
    errors = validate_graph(plan)
    assert not errors, f"Unresolved dependencies: {errors}"


def test_no_duplicate_user_model_when_users_in_modules():
    """When 'users' is in modules, the model comes from the module loop â€” no duplicate."""
    rules = {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "MongoDB",
        "auth_method": "JWT",
        "deployment": "AWS",
        "required_pages": ["Login"],
        "required_backend_modules": ["users", "posts"],
    }
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    user_model_count = sum(1 for p in paths if p == "backend/src/models/users.js")
    assert user_model_count == 1, f"Expected exactly 1 users model, got {user_model_count}"


def test_auth_user_model_not_added_without_auth():
    """When auth is not meaningful, no User model should be auto-generated."""
    rules = {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "None",
        "deployment": "AWS",
        "required_pages": ["Home"],
        "required_backend_modules": ["workspaces"],
    }
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    assert "backend/src/models/users.js" not in paths
    assert "backend/src/middleware/auth.js" not in paths
    assert "backend/src/routes/auth.js" not in paths


# ---------------------------------------------------------------------------
# Sample rule sets
# ---------------------------------------------------------------------------


def _node_react_postgres_rules():
    return {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "JWT",
        "deployment": "AWS",
        "required_pages": ["Home", "Login", "Dashboard", "Settings"],
        "required_backend_modules": ["workspaces", "projects", "tasks"],
    }


def _fastapi_vue_postgres_rules():
    return {
        "backend_framework": "FastAPI",
        "frontend_framework": "Vue.js",
        "database": "PostgreSQL",
        "auth_method": "JWT",
        "deployment": "Docker",
        "required_pages": ["Home", "Dashboard", "Settings"],
        "required_backend_modules": ["workspaces", "projects", "tasks"],
    }


def _spring_react_mysql_rules():
    return {
        "backend_framework": "Spring Boot",
        "frontend_framework": "React",
        "database": "MySQL",
        "auth_method": "OAuth2",
        "deployment": "AWS",
        "required_pages": ["Home", "Dashboard", "Admin"],
        "required_backend_modules": ["workspaces", "projects"],
    }


def _pm_rules():
    return {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "JWT",
        "deployment": "AWS",
        "required_pages": [
            "Workspaces", "Projects", "Boards", "Tasks",
            "Activity", "Notifications",
        ],
        "required_backend_modules": [
            "workspaces", "projects", "tasks",
            "activity", "notifications",
        ],
    }


def _node_react_mongo_rules():
    return {
        "backend_framework": "Node.js",
        "frontend_framework": "React",
        "database": "MongoDB",
        "auth_method": "JWT",
        "deployment": "AWS",
        "required_pages": ["Home", "Dashboard"],
        "required_backend_modules": ["users", "posts"],
    }


def test_fastapi_mongodb_uses_motor_shape_not_sqlalchemy():
    rules = {
        "backend_framework": "FastAPI",
        "frontend_framework": "React",
        "database": "MongoDB",
        "auth_method": "JWT",
        "deployment": "Docker",
        "required_pages": ["Login"],
        "required_backend_modules": ["todos"],
    }
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    purposes = "\n".join(f["purpose"] for f in plan["files"])
    assert "app/db/database.py" in paths
    assert "app/db/base.py" not in paths
    assert "seeds/seed.py" in paths
    assert "src/config/mongodb.js" not in paths
    assert "SQLAlchemy" not in purposes
    assert "Motor" in purposes


def test_express_no_auth_has_no_auth_artifacts():
    rules = {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "None",
        "deployment": "AWS",
        "required_pages": ["Home"],
        "required_backend_modules": ["items"],
    }
    plan = generate_build_plan(rules)
    paths = [f["path"] for f in plan["files"]]
    purposes = "\n".join(f["purpose"] for f in plan["files"])
    assert "backend/src/middleware/auth.js" not in paths
    assert "backend/src/routes/auth.js" not in paths
    assert "backend/src/models/users.js" not in paths
    assert "jsonwebtoken" not in purposes
    assert "bcrypt" not in purposes
