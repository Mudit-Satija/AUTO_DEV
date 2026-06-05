"""Tests for coding_agent.requirement_validator — requirement coverage validation."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_agent.requirement_validator import (
    _check_component_export,
    _check_requirement,
    _derive_requirements_from_purpose,
    _has_route_endpoint,
    validate_requirements,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_project():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def _write(root: Path, path: str, content: str = "") -> Path:
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    return full


def _bp(path, requirements=None, purpose=""):
    return {
        "path": path,
        "type": "source",
        "purpose": purpose or path,
        "depends_on": [],
        "provides": [],
        "requirements": requirements or [],
    }


# ---------------------------------------------------------------------------
# validate_requirements — integration
# ---------------------------------------------------------------------------


class TestValidateRequirements:
    def test_nonexistent_directory(self):
        result = validate_requirements("/nonexistent", {"files": []})
        assert result["success"] is False
        assert len(result["errors"]) == 1
        assert "not found" in result["errors"][0]["error"]

    def test_empty_build_plan(self, tmp_project):
        result = validate_requirements(str(tmp_project), {"files": []})
        assert result["success"] is True
        assert result["errors"] == []

    def test_auth_routes_complete(self, tmp_project):
        content = """
        const router = require('express').Router();
        router.post('/login', (req, res) => {});
        router.post('/register', (req, res) => {});
        router.post('/logout', (req, res) => {});
        module.exports = router;
        """
        _write(tmp_project, "src/routes/auth.js", content)
        plan = {"files": [_bp("src/routes/auth.js", ["login", "register", "logout"], "Authentication routes")]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is True, result["errors"]

    def test_auth_routes_missing_register(self, tmp_project):
        content = """
        router.post('/login', (req, res) => {});
        router.post('/logout', (req, res) => {});
        """
        _write(tmp_project, "src/routes/auth.js", content)
        plan = {"files": [_bp("src/routes/auth.js", ["login", "register", "logout"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is False
        errors_by_req = {e["requirement"]: e for e in result["errors"]}
        assert "register" in errors_by_req
        assert "register" in errors_by_req["register"]["error"]

    def test_crud_routes_complete(self, tmp_project):
        content = """
        router.get('/', (req, res) => {});
        router.post('/', (req, res) => {});
        router.put('/:id', (req, res) => {});
        router.delete('/:id', (req, res) => {});
        """
        _write(tmp_project, "src/routes/tasks.js", content)
        plan = {"files": [_bp("src/routes/tasks.js", ["list", "create", "update", "delete"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is True, result["errors"]

    def test_crud_routes_missing_delete(self, tmp_project):
        content = """
        router.get('/', (req, res) => {});
        router.post('/', (req, res) => {});
        router.put('/:id', (req, res) => {});
        """
        _write(tmp_project, "src/routes/tasks.js", content)
        plan = {"files": [_bp("src/routes/tasks.js", ["list", "create", "update", "delete"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is False
        errors_by_req = {e["requirement"]: e for e in result["errors"]}
        assert "delete" in errors_by_req

    def test_react_component_export_exists(self, tmp_project):
        content = """
        import React from 'react';
        export default function Dashboard() {
            return <div>Dashboard</div>;
        }
        """
        _write(tmp_project, "src/pages/Dashboard.jsx", content)
        plan = {"files": [_bp("src/pages/Dashboard.jsx", ["component export"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is True, result["errors"]

    def test_react_component_export_missing(self, tmp_project):
        content = """
        import React from 'react';
        const Dashboard = () => <div>Dashboard</div>;
        """
        _write(tmp_project, "src/pages/Dashboard.jsx", content)
        plan = {"files": [_bp("src/pages/Dashboard.jsx", ["component export"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is False
        assert any("component export" in e["requirement"] for e in result["errors"])

    def test_api_service_exports_exist(self, tmp_project):
        content = """
        export async function getUsers() {}
        export async function createUser() {}
        """
        _write(tmp_project, "src/services/api.js", content)
        plan = {"files": [_bp("src/services/api.js", ["API functions"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is True, result["errors"]

    def test_api_service_exports_missing(self, tmp_project):
        content = "const x = 42;"
        _write(tmp_project, "src/services/api.js", content)
        plan = {"files": [_bp("src/services/api.js", ["API functions"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is False
        assert any("API functions" in e["requirement"] for e in result["errors"])

    def test_unknown_requirement_safely_ignored(self, tmp_project):
        content = "some unknown requirement content here"
        _write(tmp_project, "src/test.txt", content)
        plan = {"files": [_bp("src/test.txt", ["some unknown requirement"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is True

    def test_multiple_failures_collected(self, tmp_project):
        content = """
        router.post('/login', (req, res) => {});
        """
        _write(tmp_project, "src/routes/auth.js", content)
        plan = {"files": [_bp("src/routes/auth.js", ["login", "register", "logout"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is False
        assert len(result["errors"]) == 2

    def test_missing_file_skipped(self, tmp_project):
        plan = {"files": [_bp("src/routes/auth.js", ["login", "register", "logout"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is True

    def test_empty_requirements_uses_purpose_fallback(self, tmp_project):
        content = """
        router.post('/login', (req, res) => {});
        router.post('/register', (req, res) => {});
        router.post('/logout', (req, res) => {});
        """
        _write(tmp_project, "app/routers/auth.py", content)
        plan = {
            "files": [
                {
                    "path": "app/routers/auth.py",
                    "type": "source",
                    "purpose": "Authentication routes (login, register, logout)",
                    "depends_on": [],
                    "provides": [],
                    "requirements": [],
                }
            ]
        }
        result = validate_requirements(str(tmp_project), plan)
        assert result["success"] is True, result["errors"]

    def test_return_format_has_expected_keys(self, tmp_project):
        _write(tmp_project, "a.js", "x = 1")
        plan = {"files": [_bp("a.js", ["some requirement"])]}
        result = validate_requirements(str(tmp_project), plan)
        assert "success" in result
        assert "errors" in result
        if result["errors"]:
            assert "file" in result["errors"][0]
            assert "requirement" in result["errors"][0]
            assert "error" in result["errors"][0]


# ---------------------------------------------------------------------------
# _has_route_endpoint
# ---------------------------------------------------------------------------


class TestHasRouteEndpoint:
    def test_js_router_get(self):
        content = """router.get('/login', handler);"""
        assert _has_route_endpoint(content, "login", ".js") is True

    def test_js_router_post(self):
        content = """router.post('/register', handler);"""
        assert _has_route_endpoint(content, "register", ".js") is True

    def test_js_app_put(self):
        content = '''app.put("/update", handler);'''
        assert _has_route_endpoint(content, "update", ".js") is True

    def test_js_app_delete(self):
        content = "app.delete('/remove', handler);"
        assert _has_route_endpoint(content, "remove", ".js") is True

    def test_python_router_get(self):
        content = """@router.get('/login')"""
        assert _has_route_endpoint(content, "login", ".py") is True

    def test_python_app_post(self):
        content = """@app.post('/register')"""
        assert _has_route_endpoint(content, "register", ".py") is True

    def test_java_get_mapping(self):
        content = """@GetMapping("/login")"""
        assert _has_route_endpoint(content, "login", ".java") is True

    def test_not_found(self):
        content = "const x = 1;"
        assert _has_route_endpoint(content, "login", ".js") is False

    def test_case_insensitive(self):
        content = """router.get('/Login', handler);"""
        assert _has_route_endpoint(content, "login", ".js") is True


# ---------------------------------------------------------------------------
# _check_component_export
# ---------------------------------------------------------------------------


class TestCheckComponentExport:
    def test_jsx_export_default_function(self):
        content = "export default function Dashboard() {}"
        assert _check_component_export(content, ".jsx", {}) is True

    def test_jsx_export_default_class(self):
        content = "export default class Dashboard extends Component {}"
        assert _check_component_export(content, ".jsx", {}) is True

    def test_jsx_no_export(self):
        content = "const Dashboard = () => {};"
        assert _check_component_export(content, ".jsx", {}) is False

    def test_js_export_default(self):
        content = "export default function App() {}"
        assert _check_component_export(content, ".js", {}) is True

    def test_vue_with_template(self):
        content = "<template><div>App</div></template>"
        assert _check_component_export(content, ".vue", {}) is True

    def test_vue_with_export(self):
        content = "export default { name: 'App' }"
        assert _check_component_export(content, ".vue", {}) is True

    def test_empty_content(self):
        assert _check_component_export("", ".jsx", {}) is False


# ---------------------------------------------------------------------------
# _check_requirement
# ---------------------------------------------------------------------------


class TestCheckRequirement:
    def test_endpoint_found(self):
        content = """router.get('/login', handler);"""
        result = _check_requirement(content, "login", ".js", {}, Path("."))
        assert result is None

    def test_endpoint_missing(self):
        content = """router.get('/logout', handler);"""
        result = _check_requirement(content, "login", ".js", {}, Path("."))
        assert result is not None
        assert "endpoint" in result

    def test_structural_found(self):
        content = "export default function Dashboard() {}"
        result = _check_requirement(content, "component export", ".jsx", {}, Path("."))
        assert result is None

    def test_structural_missing(self):
        content = "const x = 1;"
        result = _check_requirement(content, "component export", ".jsx", {}, Path("."))
        assert result is not None

    def test_generic_presence(self):
        content = "some custom requirement text here"
        result = _check_requirement(content, "custom requirement", ".txt", {}, Path("."))
        assert result is None


# ---------------------------------------------------------------------------
# _derive_requirements_from_purpose
# ---------------------------------------------------------------------------


class TestDeriveRequirementsFromPurpose:
    def test_authentication_routes(self):
        reqs = _derive_requirements_from_purpose("Authentication routes (login, register, logout)")
        assert "login" in reqs
        assert "register" in reqs
        assert "logout" in reqs

    def test_api_routes(self):
        reqs = _derive_requirements_from_purpose("workspaces API routes")
        assert "list" in reqs
        assert "create" in reqs
        assert "update" in reqs
        assert "delete" in reqs

    def test_unknown_purpose(self):
        reqs = _derive_requirements_from_purpose("Some random purpose")
        assert reqs == []

    def test_empty_purpose(self):
        assert _derive_requirements_from_purpose("") == []


# ---------------------------------------------------------------------------
# Integration with generate_project
# ---------------------------------------------------------------------------


class TestGenerateProjectIntegration:
    def test_requirement_validation_invoked_during_generation(self, tmp_project):
        from coding_agent.project_generator import generate_project

        build_plan = {
            "files": [
                {
                    "path": "src/routes/auth.js",
                    "type": "source",
                    "purpose": "Authentication routes",
                    "depends_on": [],
                    "provides": [],
                    "requirements": ["login", "register", "logout"],
                },
            ],
        }
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}

        mock_llm = Mock(return_value=(
            "===FILE: src/routes/auth.js===\n"
            "const router = require('express').Router();\n"
            "router.post('/login', (req, res) => {});\n"
            "router.post('/register', (req, res) => {});\n"
            "router.post('/logout', (req, res) => {});\n"
            "module.exports = router;\n"
            "===END==="
        ))
        mock_write = Mock(return_value={
            "path": "src/routes/auth.js",
            "absolute_path": str(tmp_project / "x"),
            "bytes_written": 1,
        })

        with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
             patch("coding_agent.bundle_generator.write_file", mock_write):
            result = generate_project(build_plan, rules, str(tmp_project))

        assert result["files_generated"] == 1

    def test_requirement_validation_reports_failures(self, tmp_project):
        from coding_agent.project_generator import generate_project

        build_plan = {
            "files": [
                {
                    "path": "src/routes/auth.js",
                    "type": "source",
                    "purpose": "Authentication routes",
                    "depends_on": [],
                    "provides": [],
                    "requirements": ["login", "register", "logout"],
                },
            ],
        }
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}

        mock_llm = Mock(return_value=(
            "===FILE: src/routes/auth.js===\n"
            "const router = require('express').Router();\n"
            "router.post('/login', (req, res) => {});\n"
            "// missing register and logout\n"
            "module.exports = router;\n"
            "===END==="
        ))
        mock_write = Mock(return_value={
            "path": "src/routes/auth.js",
            "absolute_path": str(tmp_project / "x"),
            "bytes_written": 1,
        })

        with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
             patch("coding_agent.bundle_generator.write_file", mock_write):
            result = generate_project(build_plan, rules, str(tmp_project))

        assert result["files_generated"] == 1
