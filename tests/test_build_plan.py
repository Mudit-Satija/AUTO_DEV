"""Tests for the SRS-driven build plan generator.

Validates:
- Requirement lineage on every file
- Pages come ONLY from SRS.pages
- Entities come ONLY from SRS.entities
- No hardcoded auth files
- No hardcoded entity names
"""

from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules


def _sample_srs_inventory():
    return {
        "project_name": "Inventory Manager",
        "project_description": "Track inventory items",
        "complexity": "intermediate",
        "pages": [
            {"name": "Items", "purpose": "List inventory items", "entities": ["Item"]},
            {"name": "Stock In", "purpose": "Record incoming stock", "entities": ["Item", "Supplier"]},
        ],
        "flow": [
            {"name": "Receive Stock", "steps": ["Item arrives", "Record quantity"], "entities": ["Item", "Supplier"]},
        ],
        "entities": [
            {"name": "Item", "fields": ["sku", "name", "quantity"], "description": "Inventory item"},
            {"name": "Supplier", "fields": ["name", "email"], "description": "Supplier"},
        ],
        "roles": ["admin"],
        "tech_stack": {"backend": "Express.js", "frontend": "React", "database": "MongoDB"},
        "requirements": [],
    }


def _make_rules(srs_override=None):
    srs = _sample_srs_inventory()
    if srs_override:
        srs.update(srs_override)
    tech_stack = srs.get("tech_stack", {})
    return build_project_rules(srs, tech_stack)


def test_readme_always_included():
    rules = _make_rules()
    plan = generate_build_plan(rules)
    paths = {f["path"] for f in plan["files"]}
    assert "README.md" in paths


def test_pages_come_only_from_srs():
    rules = _make_rules()
    plan = generate_build_plan(rules)
    page_files = [f for f in plan["files"] if f["type"] == "page"]
    page_names = {f["source_page"] for f in page_files}
    # Only Items and Stock In — no Login, Register, Dashboard, Settings, Profile
    assert page_names == {"Items", "Stock In"}, f"Got pages: {page_names}"


def test_no_auth_artifacts():
    rules = _make_rules()
    plan = generate_build_plan(rules)
    paths = {f["path"] for f in plan["files"]}
    forbidden = {"backend/src/middleware/auth.js", "backend/src/routes/auth.js",
                 "backend/src/models/users.js", "app/core/security.py",
                 "app/routers/auth.py", "app/models/user.py"}
    assert not (paths & forbidden), f"Auth artifacts found: {paths & forbidden}"


def test_no_hardcoded_entities():
    rules = _make_rules()
    plan = generate_build_plan(rules)
    model_paths = [f["path"] for f in plan["files"] if "models/" in f["path"]]
    # Should only have Item and Supplier models — no workspaces, projects, tasks, users
    model_names = {p.split("/")[-1].replace(".js", "") for p in model_paths}
    assert model_names == {"item", "supplier"}, f"Got models: {model_names}"


def test_no_hardcoded_pages():
    rules = _make_rules()
    plan = generate_build_plan(rules)
    page_paths = [f["path"].lower() for f in plan["files"] if f["type"] == "page"]
    hardcoded = {"login", "register", "dashboard", "profile", "settings"}
    for hp in hardcoded:
        assert not any(hp in p for p in page_paths), f"Hardcoded page '{hp}' found in {page_paths}"


def test_every_file_has_lineage():
    rules = _make_rules()
    plan = generate_build_plan(rules)
    for f in plan["files"]:
        assert f.get("reason_for_existence"), f"No reason_for_existence in {f['path']}"
        has_lineage = bool(f.get("source_requirement") or f.get("source_page") or f.get("source_entity") or f.get("source_flow"))
        if f["type"] not in ("documentation", "config", "env", "database"):
            assert has_lineage, f"No lineage in {f['path']} of type {f['type']}"


def test_entities_in_srs_match_build_plan():
    rules = _make_rules()
    plan = generate_build_plan(rules)
    srs_entities = {"item", "supplier"}
    for f in plan["files"]:
        if f.get("source_entity"):
            for ent in f["source_entity"].split("; "):
                ent_clean = ent.strip().lower()
                if ent_clean:
                    assert ent_clean in srs_entities, f"Entity '{ent_clean}' not in SRS entities"


def test_fastapi_python_backend():
    srs = _sample_srs_inventory()
    srs["tech_stack"] = {"backend": "FastAPI", "frontend": "React", "database": "PostgreSQL"}
    rules = _make_rules(srs)
    plan = generate_build_plan(rules)
    paths = {f["path"] for f in plan["files"]}
    assert "requirements.txt" in paths
    assert "app/main.py" in paths
    assert "app/db/database.py" in paths
    assert "app/routers/item.py" in paths
    assert "app/models/item.py" in paths


def test_no_hardcoded_domain_hints():
    """Verify no workspaces/tasks appear as module paths."""
    rules = _make_rules()
    plan = generate_build_plan(rules)
    hardcoded_modules = {"workspace", "task"}
    for f in plan["files"]:
        path_lower = f["path"].lower()
        for hd in hardcoded_modules:
            assert hd not in path_lower, f"Hardcoded '{hd}' in path {f['path']}"


def test_vue_frontend_files():
    srs = _sample_srs_inventory()
    srs["tech_stack"] = {"backend": "Express.js", "frontend": "Vue", "database": "MongoDB"}
    rules = _make_rules(srs)
    plan = generate_build_plan(rules)
    paths = {f["path"] for f in plan["files"]}
    assert "frontend/src/App.vue" in paths
    assert "frontend/src/router/index.js" in paths
    assert "frontend/src/views/Items.vue" in paths
    assert "frontend/src/views/StockIn.vue" in paths


def test_database_files_for_sql():
    srs = _sample_srs_inventory()
    srs["tech_stack"] = {"backend": "Express.js", "frontend": "React", "database": "PostgreSQL"}
    rules = _make_rules(srs)
    plan = generate_build_plan(rules)
    paths = {f["path"] for f in plan["files"]}
    assert "migrations/001_initial.sql" in paths
    assert "seeds/seed.sql" in paths


def test_database_files_for_mongo():
    rules = _make_rules()
    plan = generate_build_plan(rules)
    paths = {f["path"] for f in plan["files"]}
    assert "seeds/seed.js" in paths
