"""Tests for the SRS-driven rules engine.

Validates that project_rules are derived from SRS content correctly.
"""

from coding_agent.rules_engine import build_project_rules


def _sample_srs():
    return {
        "project_name": "TestApp",
        "project_description": "A test application",
        "complexity": "intermediate",
        "pages": [
            {"name": "Items", "purpose": "List items", "entities": ["Item"]},
        ],
        "flow": [
            {"name": "Create Item", "steps": ["Fill form", "Save"], "entities": ["Item"]},
        ],
        "entities": [
            {"name": "Item", "fields": ["name", "price"], "description": "An item"},
        ],
        "roles": ["user"],
        "tech_stack": {"backend": "Express.js", "frontend": "React", "database": "MongoDB"},
        "requirements": [],
    }


def test_rules_produces_all_required_keys():
    srs = _sample_srs()
    rules = build_project_rules(srs, srs["tech_stack"])

    assert set(rules.keys()) == {
        "backend_framework",
        "frontend_framework",
        "database",
        "auth_method",
        "deployment",
        "required_pages",
        "required_backend_modules",
        "srs",
    }


def test_backend_framework_from_tech_stack():
    srs = _sample_srs()
    rules = build_project_rules(srs, srs["tech_stack"])
    assert rules["backend_framework"] == "Express.js"


def test_frontend_framework_from_tech_stack():
    srs = _sample_srs()
    rules = build_project_rules(srs, srs["tech_stack"])
    assert rules["frontend_framework"] == "React"


def test_database_from_tech_stack():
    srs = _sample_srs()
    rules = build_project_rules(srs, srs["tech_stack"])
    assert rules["database"] == "MongoDB"


def test_auth_method_empty_by_default():
    srs = _sample_srs()
    rules = build_project_rules(srs, srs["tech_stack"])
    assert rules["auth_method"] == ""


def test_deployment_not_specified_by_default():
    srs = _sample_srs()
    rules = build_project_rules(srs, srs["tech_stack"])
    assert rules["deployment"] == "Not specified"


def test_deployment_from_tech_stack():
    srs = _sample_srs()
    srs["tech_stack"]["deployment"] = "AWS"
    rules = build_project_rules(srs, srs["tech_stack"])
    assert rules["deployment"] == "AWS"


def test_required_pages_from_srs_pages():
    srs = _sample_srs()
    rules = build_project_rules(srs, srs["tech_stack"])
    assert rules["required_pages"] == ["Items"]


def test_required_backend_modules_from_srs_entities():
    srs = _sample_srs()
    rules = build_project_rules(srs, srs["tech_stack"])
    assert rules["required_backend_modules"] == ["item"]


def test_srs_is_preserved_in_rules():
    srs = _sample_srs()
    rules = build_project_rules(srs, srs["tech_stack"])
    assert rules["srs"] is srs


def test_tech_stack_can_be_passed_separately():
    srs = _sample_srs()
    tech_stack = {"backend": "FastAPI", "frontend": "Vue", "database": "PostgreSQL"}
    rules = build_project_rules(srs, tech_stack)
    assert rules["backend_framework"] == "FastAPI"
    assert rules["frontend_framework"] == "Vue"
    assert rules["database"] == "PostgreSQL"
    # Pages still from SRS
    assert rules["required_pages"] == ["Items"]
    # Entities still from SRS
    assert rules["required_backend_modules"] == ["item"]


def test_empty_srs_returns_empty_lists():
    srs = {}
    tech_stack = {}
    rules = build_project_rules(srs, tech_stack)
    assert rules["required_pages"] == []
    assert rules["required_backend_modules"] == []


def test_multiple_entities_produce_multiple_modules():
    srs = _sample_srs()
    srs["entities"] = [
        {"name": "Product", "fields": [], "description": ""},
        {"name": "Category", "fields": [], "description": ""},
        {"name": "Supplier", "fields": [], "description": ""},
    ]
    rules = build_project_rules(srs, srs["tech_stack"])
    assert set(rules["required_backend_modules"]) == {"product", "category", "supplier"}
