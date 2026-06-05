from coding_agent.prompt_builder import build_file_prompt


def test_prompt_contains_context_section():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "Context:" in prompt


def test_prompt_contains_file_section():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "File to generate:" in prompt


def test_prompt_contains_instructions_section():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "Instructions:" in prompt


def test_prompt_includes_backend_framework():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "Express.js" in prompt


def test_prompt_includes_frontend_framework():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "React" in prompt


def test_prompt_includes_database():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "PostgreSQL" in prompt


def test_prompt_includes_auth_method():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "JWT" in prompt


def test_prompt_includes_file_path():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "src/routes/workspaces.js" in prompt


def test_prompt_includes_file_purpose():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "workspaces API routes" in prompt


def test_prompt_includes_file_type():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "module" in prompt


def test_instructions_require_raw_code():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "raw source code" in prompt


def test_instructions_forbid_markdown_blocks():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "Do NOT wrap the code in markdown code blocks" in prompt


def test_instructions_forbid_explanations():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "Do NOT include any explanations" in prompt


def test_instructions_forbid_additional_files():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "do not suggest or create additional files" in prompt


def test_instructions_require_complete_code():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert "complete, functional" in prompt


def test_node_source_file():
    blueprint = {"path": "src/app.js", "type": "source", "purpose": "Express application setup and middleware"}
    prompt = build_file_prompt(blueprint, _node_react_jwt_rules())
    assert "src/app.js" in prompt
    assert "Express.js" in prompt


def test_react_page_file():
    blueprint = {"path": "src/pages/Home.jsx", "type": "page", "purpose": "Home page"}
    prompt = build_file_prompt(blueprint, _node_react_jwt_rules())
    assert "src/pages/Home.jsx" in prompt
    assert "Home page" in prompt


def test_config_file():
    blueprint = {"path": "package.json", "type": "config", "purpose": "Node.js dependencies and scripts"}
    prompt = build_file_prompt(blueprint, _node_react_jwt_rules())
    assert "package.json" in prompt
    assert "config" in prompt


def test_database_migration_file():
    blueprint = {"path": "migrations/001_initial.sql", "type": "database", "purpose": "Initial database schema migration"}
    prompt = build_file_prompt(blueprint, _node_react_jwt_rules())
    assert "migrations/001_initial.sql" in prompt
    assert "database" in prompt


def test_documentation_file():
    blueprint = {"path": "README.md", "type": "documentation", "purpose": "Project overview and setup instructions"}
    prompt = build_file_prompt(blueprint, _node_react_jwt_rules())
    assert "README.md" in prompt
    assert "documentation" in prompt


def test_missing_file_path_falls_back():
    prompt = build_file_prompt({}, _node_react_jwt_rules())
    assert "unknown" in prompt


def test_missing_project_rules_uses_defaults():
    prompt = build_file_prompt(_node_route_blueprint(), {})
    assert "Unknown" in prompt


def test_deterministic_output():
    blueprint = _node_route_blueprint()
    rules = _node_react_jwt_rules()
    prompt1 = build_file_prompt(blueprint, rules)
    prompt2 = build_file_prompt(blueprint, rules)
    assert prompt1 == prompt2


def test_prompt_starts_with_role():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert prompt.startswith("You are a code generation assistant.")


def test_prompt_ends_with_instructions():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    assert prompt.endswith("like 'config/database'.")


def test_all_context_fields_listed():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    for label in ("Backend framework:", "Frontend framework:", "Database:", "Auth method:"):
        assert label in prompt


def test_all_file_fields_listed():
    prompt = build_file_prompt(_node_route_blueprint(), _node_react_jwt_rules())
    for label in ("Path:", "Purpose:", "Type:"):
        assert label in prompt


def test_fastapi_react_mongo_rules():
    rules = {
        "backend_framework": "FastAPI",
        "frontend_framework": "React",
        "database": "MongoDB",
        "auth_method": "OAuth2",
        "deployment": "Docker",
    }
    blueprint = {"path": "app/routers/users.py", "type": "module", "purpose": "users API routes"}
    prompt = build_file_prompt(blueprint, rules)
    assert "FastAPI" in prompt
    assert "MongoDB" in prompt
    assert "OAuth2" in prompt
    assert "app/routers/users.py" in prompt


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------


def _node_route_blueprint():
    return {
        "path": "src/routes/workspaces.js",
        "type": "module",
        "purpose": "workspaces API routes",
    }


def _node_react_jwt_rules():
    return {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "JWT",
        "deployment": "AWS",
        "required_pages": ["Home", "Login", "Dashboard", "Settings"],
        "required_backend_modules": ["workspaces", "projects", "tasks"],
    }
