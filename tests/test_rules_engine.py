from coding_agent.rules_engine import build_project_rules


def test_rules_engine_produces_all_required_keys():
    plan = _sample_merged_plan()
    rules = build_project_rules(plan)

    assert set(rules.keys()) == {
        "backend_framework",
        "frontend_framework",
        "database",
        "auth_method",
        "deployment",
        "required_pages",
        "required_backend_modules",
    }


def test_backend_framework_extracted():
    rules = build_project_rules(_sample_merged_plan())
    assert rules["backend_framework"] == "Express.js"


def test_backend_framework_strips_version():
    plan = _sample_merged_plan()
    plan["backend_architecture"]["framework"] = "Express.js 4.18"
    rules = build_project_rules(plan)
    assert rules["backend_framework"] == "Express.js"


def test_frontend_framework_extracted():
    rules = build_project_rules(_sample_merged_plan())
    assert rules["frontend_framework"] == "React"


def test_database_extracted():
    rules = build_project_rules(_sample_merged_plan())
    assert rules["database"] == "PostgreSQL"


def test_auth_method_extracted():
    rules = build_project_rules(_sample_merged_plan())
    assert rules["auth_method"] == "JWT"


def test_deployment_from_user_stack():
    plan = _sample_merged_plan()
    plan["validation"]["user_stack"]["deployment"] = "AWS"
    rules = build_project_rules(plan)
    assert rules["deployment"] == "AWS"


def test_deployment_falls_back_to_recommended_stack():
    plan = _sample_merged_plan()
    plan["validation"]["user_stack"] = {}
    plan["validation"]["recommended_stack"]["devops"] = ["Docker", "Kubernetes"]
    rules = build_project_rules(plan)
    assert rules["deployment"] == "Docker"


def test_deployment_not_specified_when_missing():
    plan = _sample_merged_plan()
    plan["validation"]["user_stack"] = {}
    plan["validation"]["recommended_stack"] = {}
    rules = build_project_rules(plan)
    assert rules["deployment"] == "Not specified"


def test_required_pages_from_routing_and_navigation():
    plan = _sample_merged_plan()
    rules = build_project_rules(plan)
    assert "Home" in rules["required_pages"]
    assert "Projects" in rules["required_pages"]
    assert "Login" in rules["required_pages"]


def test_required_backend_modules_from_folders_and_endpoints():
    plan = _sample_merged_plan()
    rules = build_project_rules(plan)
    assert "workspaces" in rules["required_backend_modules"]
    assert "projects" in rules["required_backend_modules"]
    assert "tasks" in rules["required_backend_modules"]


def test_required_backend_modules_no_skip_parts():
    plan = _sample_merged_plan()
    rules = build_project_rules(plan)
    for skip in ("src", "core", "tests", "config", "domains", "api", "auth"):
        assert skip not in rules["required_backend_modules"]


def test_empty_plan_returns_safe_defaults():
    rules = build_project_rules({})
    assert rules["backend_framework"] == "Unknown"
    assert rules["frontend_framework"] == "Unknown"
    assert rules["database"] == "Unknown"
    assert rules["auth_method"] == "Unknown"
    assert rules["deployment"] == "Not specified"
    assert rules["required_pages"] == []
    assert rules["required_backend_modules"] == []


def test_project_management_domain_pages():
    plan = _pm_merged_plan()
    rules = build_project_rules(plan)
    assert "Workspaces" in rules["required_pages"]
    assert "Boards" in rules["required_pages"]
    assert "Activity" in rules["required_pages"]


def test_project_management_backend_modules():
    plan = _pm_merged_plan()
    rules = build_project_rules(plan)
    assert "workspaces" in rules["required_backend_modules"]
    assert "projects" in rules["required_backend_modules"]
    assert "tasks" in rules["required_backend_modules"]
    assert "activity" in rules["required_backend_modules"]
    assert "notifications" in rules["required_backend_modules"]


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------


def _sample_merged_plan():
    return {
        "status": "success",
        "validation": {
            "project_type": "web app",
            "complexity": "intermediate",
            "user_stack": {
                "backend": "Node.js",
                "frontend": "React",
                "database": "PostgreSQL",
            },
            "recommended_stack": {
                "backend": ["Node.js"],
                "frontend": ["React"],
                "database": ["PostgreSQL"],
                "devops": ["Docker"],
            },
        },
        "backend_architecture": {
            "framework": "Express.js",
            "language": "JavaScript",
            "api_style": "REST",
            "authentication": {
                "method": "JWT",
                "storage": "httpOnly cookies",
                "refresh_strategy": "Rotate refresh tokens",
                "libraries": ["jsonwebtoken"],
            },
            "database": {
                "type": "PostgreSQL",
                "orm": "Prisma",
                "connection_pool": True,
                "migration_tool": "Prisma Migrate",
            },
            "suggested_endpoints": [
                {"method": "GET", "path": "/api/workspaces", "description": "List", "auth_required": True},
                {"method": "POST", "path": "/api/workspaces", "description": "Create", "auth_required": True},
                {"method": "GET", "path": "/api/projects", "description": "List", "auth_required": True},
                {"method": "POST", "path": "/api/tasks", "description": "Create", "auth_required": True},
                {"method": "POST", "path": "/api/auth/login", "description": "Login", "auth_required": False},
            ],
            "folder_structure": [
                {"name": "src/", "description": "source", "children": []},
                {"name": "src/domains/workspaces/", "description": "workspace modules", "children": []},
                {"name": "src/domains/projects/", "description": "project modules", "children": []},
                {"name": "src/domains/tasks/", "description": "task modules", "children": []},
                {"name": "tests/", "description": "tests", "children": []},
            ],
            "dependencies": {
                "core_libraries": ["express", "jsonwebtoken", "prisma"],
                "optional_libraries": {},
                "design_patterns": ["MVC", "Service Layer"],
            },
            "reasoning": "Node.js + Express is ideal",
        },
        "frontend_architecture": {
            "framework": "React",
            "language": "TypeScript",
            "styling": "tailwind",
            "routing": {
                "/": "Home",
                "/auth/login": "Login",
                "/dashboard": "Dashboard",
                "/projects": "Projects",
                "/settings": "Settings",
            },
            "navigation": [
                {"label": "Home", "path": "/", "icon": "home"},
                {"label": "Dashboard", "path": "/dashboard", "icon": "dashboard", "auth": True},
                {"label": "Projects", "path": "/projects", "icon": "folder", "auth": True},
            ],
            "mobile_menu": "bottom-tabs",
        },
    }


def _pm_merged_plan():
    plan = _sample_merged_plan()
    plan["frontend_architecture"]["routing"] = {
        "/workspaces": "Workspaces",
        "/projects": "Projects",
        "/boards": "Boards",
        "/tasks": "Tasks",
        "/activity": "Activity",
        "/notifications": "Notifications",
    }
    plan["frontend_architecture"]["navigation"] = [
        {"label": "Workspaces", "path": "/workspaces", "icon": "spaces", "auth": True},
        {"label": "Projects", "path": "/projects", "icon": "folder", "auth": True},
        {"label": "Boards", "path": "/boards", "icon": "kanban", "auth": True},
        {"label": "Activity", "path": "/activity", "icon": "activity", "auth": True},
    ]
    plan["backend_architecture"]["folder_structure"] = [
        {"name": "src/", "description": "source", "children": []},
        {"name": "src/domains/workspaces/", "description": "workspaces", "children": []},
        {"name": "src/domains/projects/", "description": "projects", "children": []},
        {"name": "src/domains/tasks/", "description": "tasks", "children": []},
        {"name": "src/domains/activity/", "description": "activity", "children": []},
        {"name": "src/domains/notifications/", "description": "notifications", "children": []},
    ]
    plan["backend_architecture"]["suggested_endpoints"] = [
        {"method": "GET", "path": "/api/workspaces", "description": "List", "auth_required": True},
        {"method": "POST", "path": "/api/workspaces", "description": "Create", "auth_required": True},
        {"method": "GET", "path": "/api/projects", "description": "List", "auth_required": True},
        {"method": "POST", "path": "/api/projects", "description": "Create", "auth_required": True},
        {"method": "GET", "path": "/api/tasks", "description": "List", "auth_required": True},
        {"method": "POST", "path": "/api/tasks", "description": "Create", "auth_required": True},
        {"method": "GET", "path": "/api/activity", "description": "List", "auth_required": True},
        {"method": "GET", "path": "/api/notifications", "description": "List", "auth_required": True},
    ]
    return plan


def test_explicit_project_rules_take_precedence():
    plan = _sample_merged_plan()
    plan["project_rules"] = {
        "backend_framework": "FastAPI",
        "frontend_framework": "Vue.js",
        "database": "MongoDB",
        "auth_method": "None",
        "deployment": "Render",
        "required_pages": ["Login", "Settings"],
        "required_backend_modules": ["accounts"],
    }
    rules = build_project_rules(plan)
    assert rules["backend_framework"] == "FastAPI"
    assert rules["frontend_framework"] == "Vue.js"
    assert rules["database"] == "MongoDB"
    assert rules["auth_method"] == "None"
    assert rules["deployment"] == "Render"
    assert rules["required_pages"] == ["Login", "Settings"]
    assert rules["required_backend_modules"] == ["accounts"]


def test_backend_modules_do_not_come_from_folder_names():
    plan = _sample_merged_plan()
    plan["backend_architecture"]["suggested_endpoints"] = []
    plan["backend_architecture"]["folder_structure"] = [
        {"name": "src/services/", "description": "service helpers", "children": []},
        {"name": "src/components/dashboard/", "description": "not backend modules", "children": []},
        {"name": "src/models/", "description": "models folder", "children": []},
    ]
    rules = build_project_rules(plan)
    assert rules["required_backend_modules"] == []
