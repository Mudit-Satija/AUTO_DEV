"""End-to-end generation test — exercises the full pipeline from build plan
through generation, validation, repair, and ZIP export.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_agent.build_plan import generate_build_plan
from coding_agent.bundle_generator import group_and_partition_files
from coding_agent.project_generator import generate_project
from coding_agent.zip_export import export_to_zip
from coding_agent.file_registry import load_registry


# ---------------------------------------------------------------------------
# Helper: build mock responses that match the actual bundle partition
# ---------------------------------------------------------------------------


def _mock_response_for_bundle(file_blueprints):
    """Generate a delimiter-formatted mock response from blueprints.

    Each file gets minimal content based on its path/suffix so that
    import, smoke, and requirement validations pass.
    """
    parts = []
    for bp in file_blueprints:
        path = bp.get("path", "unknown")
        suf = Path(path).suffix
        content = _minimal_content(path, suf, bp)
        parts.append(f"===FILE: {path}===\n{content}\n===END===")
    return "\n".join(parts)


def _minimal_content(path, suffix, bp):
    """Return the shortest valid content for a given file type."""
    reqs = [r.lower().strip() for r in bp.get("requirements", [])]

    if suffix == ".json":
        return '{"name":"test"}'
    if suffix == ".md":
        return "# Project"
    if suffix == ".sql":
        if "create" in path.lower():
            return "CREATE TABLE test (id INT);"
        return "INSERT INTO test VALUES (1);"
    if suffix == ".css":
        return "body{}"

    if suffix in (".js", ".jsx"):
        # For requirement validation purposes
        has_middleware = "middleware" in reqs
        has_mounting = "route" in reqs or "mounting" in reqs
        has_export = "export" in reqs or "component" in reqs
        has_list = "list" in reqs
        has_create = "create" in reqs
        has_update = "update" in reqs
        has_delete = "delete" in reqs
        has_server = "server" in reqs or "start" in reqs

        lines = []

        if "routes/auth" in path and not suffix == ".sql":
            for endpoint in reqs:
                if endpoint in ("login", "register", "logout"):
                    lines.append(
                        f"router.post('/{endpoint}', (req, res) => {{}});"
                    )
            if lines:
                lines.insert(0, "const router = require('express').Router();")
                lines.append("module.exports = router;")
            elif "route" in path:
                lines = [
                    "const router = require('express').Router();",
                    "module.exports = router;",
                ]

        if not lines:
            if "app.js" in path or "app" in path.split("/")[-1]:
                lines = ["const express = require('express');",
                         "const app = express();",
                         "const connectDB = () => Promise.resolve();",
                         "connectDB().then(() => {",
                         "  app.use(express.json());",
                         "  app.listen(5000);",
                         "});",
                         "module.exports = app;"]
            elif "server.js" in path:
                lines = ["const app = require('./app');",
                         "const PORT = process.env.PORT || 5000;",
                         "app.listen(PORT);"]
            elif "middleware" in path:
                lines = ["module.exports = (req, res, next) => next();"]
            elif "controller" in path:
                lines = ["exports.list = (r, s) => s.json([]);",
                         "exports.create = (r, s) => s.status(201).json(r.body);",
                         "exports.update = (r, s) => s.json(r.body);",
                         "exports.delete = (r, s) => s.status(204).end();"]
            elif "model" in path:
                lines = [f"module.exports = (seq) => seq.define('{Path(path).stem}', {{}});"]
            elif "routes/" in path:
                lines = ["const router = require('express').Router();",
                         "module.exports = router;"]
            elif "config" in path or path.endswith("index.js"):
                lines = ["module.exports = {};"]
            elif "main.jsx" in path:
                lines = ["import React from 'react';",
                         "import ReactDOM from 'react-dom/client';",
                         "import App from './App';",
                         "ReactDOM.createRoot(document.getElementById('root')).render(<App />);"]
            elif "App.jsx" in path:
                lines = ["import React from 'react';",
                         "import { BrowserRouter, Routes, Route } from 'react-router-dom';",
                         "export default function App() { return <BrowserRouter><Routes><Route path='/' /></Routes></BrowserRouter>; }"]
            elif "pages/" in path or "views/" in path:
                lines = ["import React from 'react';",
                         f"export default function {Path(path).stem}() {{ return <div>{Path(path).stem}</div>; }}"]
            elif "services/" in path:
                lines = ["export async function fetchData() { return []; }"]
            elif "api" in path and suffix == ".js":
                lines = ["export async function getItems() { return []; }"]
            elif path.endswith(".jsx"):
                lines = ["import React from 'react';",
                         f"export default function {Path(path).stem}() {{ return null; }}"]
            else:
                lines = ["module.exports = {};"]

        if not lines:
            lines = ["// placeholder"]

        return "\n".join(lines)

    if suffix == ".py":
        lines = []
        if "routes/auth" in path:
            for ep in ("login", "register", "logout"):
                if ep in reqs:
                    lines.append(f"@router.post('/{ep}')")
                    lines.append(f"async def {ep}(): pass")
            if not lines:
                lines = ["from fastapi import APIRouter",
                         "router = APIRouter()"]
        elif "main.py" in path or "__init__" in path:
            lines = ["from fastapi import FastAPI",
                     "app = FastAPI()"]
        else:
            lines = ["# placeholder"]
        return "\n".join(lines)

    if suffix == ".vue":
        return "<template><div>App</div></template>"

    if suffix == ".html":
        return "<!DOCTYPE html><html><body></body></html>"

    if path == ".env":
        return "PORT=5000\nDATABASE_URL=postgres://..."
    if path == ".gitignore":
        return "node_modules/\n.env"

    return "// placeholder"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


def _write_side_effect(gf, out_dir):
    path = Path(out_dir) / gf["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(gf.get("content", ""), encoding="utf-8")
    return {
        "path": gf["path"],
        "absolute_path": str(path.resolve()),
        "bytes_written": len(gf.get("content", "").encode("utf-8")),
    }


def _run_with_mocks(build_plan, project_rules, output_dir, max_repair_attempts=3):
    """Run generate_project with automatically-generated mock LLM responses
    that match the actual bundle partition exactly."""
    bundles = group_and_partition_files(build_plan.get("files", []))
    responses = [_mock_response_for_bundle(bundles[name])
                 for name in sorted(bundles.keys())]

    mock_llm = Mock(side_effect=responses)
    mock_repair = Mock(return_value="// repaired")

    with (patch("coding_agent.bundle_generator.get_llm_response", mock_llm),
          patch("coding_agent.project_generator.get_llm_response", mock_repair),
          patch("coding_agent.bundle_generator.write_file", _write_side_effect),
          patch("coding_agent.file_generator.get_llm_response", mock_repair)):
        return generate_project(build_plan, project_rules, str(output_dir),
                                max_repair_attempts=max_repair_attempts)


# ---------------------------------------------------------------------------
# Full Pipeline
# ---------------------------------------------------------------------------


class TestE2EFullPipeline:
    def test_generates_all_files(self, tmp_dir):
        plan = {"files": [
            {"path": "backend/package.json", "type": "config", "purpose": "Deps",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "backend/src/app.js", "type": "source", "purpose": "App",
             "depends_on": [], "provides": [], "requirements": ["middleware setup"]},
            {"path": "README.md", "type": "documentation", "purpose": "Readme",
             "depends_on": [], "provides": [], "requirements": []},
        ]}
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}
        result = _run_with_mocks(plan, rules, tmp_dir)
        assert result["files_generated"] == 3
        assert len(result["files_written"]) == 3
        assert result["all_validations_pass"] is True

    def test_files_on_disk(self, tmp_dir):
        plan = {"files": [
            {"path": "backend/package.json", "type": "config", "purpose": "Deps",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "README.md", "type": "documentation", "purpose": "Readme",
             "depends_on": [], "provides": [], "requirements": []},
        ]}
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}
        result = _run_with_mocks(plan, rules, tmp_dir)
        for meta in result["files_written"]:
            assert Path(meta["absolute_path"]).exists()

    def test_registry_saved(self, tmp_dir):
        plan = {"files": [
            {"path": "a.js", "type": "source", "purpose": "File A",
             "depends_on": [], "provides": [], "requirements": []},
            {"path": "b.md", "type": "documentation", "purpose": "File B",
             "depends_on": [], "provides": [], "requirements": []},
        ]}
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}
        result = _run_with_mocks(plan, rules, tmp_dir)
        assert result["registry_path"] is not None
        assert Path(result["registry_path"]).exists()
        reg = load_registry(str(tmp_dir))
        assert len(reg) == 2

    def test_zip_export(self, tmp_dir):
        (tmp_dir / "x.txt").write_text("data")
        zip_path = export_to_zip(str(tmp_dir))
        assert Path(zip_path).exists()
        assert zip_path.endswith(".zip")
        assert Path(zip_path).stat().st_size > 0

    def test_zip_export_custom_path(self, tmp_dir):
        (tmp_dir / "x.txt").write_text("data")
        custom = str(tmp_dir / "out.zip")
        result = export_to_zip(str(tmp_dir), output_path=custom)
        assert result == str(Path(custom).resolve())

    def test_zip_export_missing_dir(self):
        with pytest.raises(ValueError, match="not found"):
            export_to_zip("/nonexistent/foo")

    def test_empty_plan_returns_early(self, tmp_dir):
        result = generate_project({"files": []}, {}, str(tmp_dir))
        assert result["files_generated"] == 0

    def test_result_keys(self, tmp_dir):
        plan = {"files": [
            {"path": "a.js", "type": "source", "purpose": "A",
             "depends_on": [], "provides": [], "requirements": []},
        ]}
        rules = {"backend_framework": "Express.js"}
        result = _run_with_mocks(plan, rules, tmp_dir)
        for key in ("files_generated", "files_written", "registry_path",
                    "repair_attempts", "all_validations_pass"):
            assert key in result


# ---------------------------------------------------------------------------
# Repair Loop
# ---------------------------------------------------------------------------


class TestE2ERepairLoop:
    def test_repair_fixes_requirement_error(self, tmp_dir):
        """Auth route missing 'logout' — repair regenerates it."""
        plan = {
            "files": [
                {"path": "backend/package.json", "type": "config", "purpose": "Deps",
                 "depends_on": [], "provides": [], "requirements": []},
                {"path": "backend/src/routes/auth.js", "type": "source",
                 "purpose": "Authentication routes",
                 "depends_on": [], "provides": [],
                 "requirements": ["login", "register", "logout"]},
                {"path": "README.md", "type": "documentation", "purpose": "Readme",
                 "depends_on": [], "provides": [], "requirements": []},
            ],
        }
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}

        bundles = group_and_partition_files(plan["files"])
        mock_responses = []
        for name in sorted(bundles.keys()):
            bps = bundles[name]
            if any("auth.js" in bp["path"] for bp in bps):
                # Auth route MISSING logout
                lines = []
                for bp in bps:
                    if "auth.js" in bp["path"]:
                        lines.append(
                            "===FILE: backend/src/routes/auth.js===\n"
                            "const router = require('express').Router();\n"
                            "router.post('/login', (req, res) => {});\n"
                            "router.post('/register', (req, res) => {});\n"
                            "// missing logout\n"
                            "module.exports = router;\n===END==="
                        )
                    else:
                        lines.append(
                            f"===FILE: {bp['path']}===\n"
                            f"{_minimal_content(bp['path'], Path(bp['path']).suffix, bp)}\n===END==="
                        )
                mock_responses.append("\n".join(lines))
            else:
                mock_responses.append(_mock_response_for_bundle(bps))

        good_auth = (
            "const router = require('express').Router();\n"
            "router.post('/login', (req, res) => {});\n"
            "router.post('/register', (req, res) => {});\n"
            "router.post('/logout', (req, res) => {});\n"
            "module.exports = router;\n"
        )
        mock_repair = Mock(return_value=good_auth)

        with (patch("coding_agent.bundle_generator.get_llm_response", Mock(side_effect=mock_responses)),
              patch("coding_agent.project_generator.get_llm_response", mock_repair),
              patch("coding_agent.bundle_generator.write_file", _write_side_effect),
              patch("coding_agent.file_generator.get_llm_response", mock_repair)):
            result = generate_project(plan, rules, str(tmp_dir), max_repair_attempts=2)

        assert result["all_validations_pass"] is True, result

    def test_repair_exhausts_on_stubborn_file(self, tmp_dir):
        always_bad = "const x = 1;\n"
        plan = {
            "files": [
                {"path": "src/routes/auth.js", "type": "source",
                 "purpose": "Authentication routes",
                 "depends_on": [], "provides": [],
                 "requirements": ["login", "register", "logout"]},
            ],
        }
        rules = {"backend_framework": "Express.js"}

        mock_llm = Mock(return_value="===FILE: src/routes/auth.js===\nconst x = 1;\n===END===")
        mock_repair = Mock(return_value=always_bad)

        with (patch("coding_agent.bundle_generator.get_llm_response", mock_llm),
              patch("coding_agent.project_generator.get_llm_response", mock_repair),
              patch("coding_agent.bundle_generator.write_file", _write_side_effect),
              patch("coding_agent.file_generator.get_llm_response", mock_repair)):
            result = generate_project(plan, rules, str(tmp_dir), max_repair_attempts=2)

        assert result["all_validations_pass"] is False
        assert result["repair_attempts"] == 2


# ---------------------------------------------------------------------------
# Real Build Plan
# ---------------------------------------------------------------------------


class TestE2EWithRealBuildPlan:
    """Use generate_build_plan() output — dynamic mock matching.

    Validators are patched to always pass so these tests verify
    the generation pipeline runs correctly for different configs
    without needing mock content to satisfy complex requirements.
    """

    MINIMAL = {
        "backend_framework": "Express.js",
        "frontend_framework": "React",
        "database": "PostgreSQL",
        "auth_method": "",
        "deployment": "AWS",
        "required_backend_modules": ["items"],
        "required_pages": ["Home"],
    }

    def _run_patched(self, plan, rules, output_dir):
        """Run with validators patched to pass."""
        bundles = group_and_partition_files(plan.get("files", []))
        responses = [_mock_response_for_bundle(bundles[name])
                     for name in sorted(bundles.keys())]

        mock_llm = Mock(side_effect=responses)
        mock_repair = Mock(return_value="// placeholder")

        with (patch("coding_agent.bundle_generator.get_llm_response", mock_llm),
              patch("coding_agent.project_generator.get_llm_response", mock_repair),
              patch("coding_agent.bundle_generator.write_file", _write_side_effect),
              patch("coding_agent.file_generator.get_llm_response", mock_repair),
              patch("coding_agent.dependency_graph.validate_imports",
                    Mock(return_value=[])),
              patch("coding_agent.smoke_test.run_smoke_tests",
                    Mock(return_value=[])),
              patch("coding_agent.requirement_validator.validate_requirements",
                    Mock(return_value={"success": True, "errors": []}))):
            return generate_project(plan, rules, str(output_dir),
                                    max_repair_attempts=1)

    def test_build_plan_to_generation(self, tmp_dir):
        rules = self.MINIMAL
        plan = generate_build_plan(rules)
        result = self._run_patched(plan, rules, tmp_dir)
        assert result["files_generated"] == len(plan["files"])

    def test_with_auth(self, tmp_dir):
        rules = dict(self.MINIMAL)
        rules["auth_method"] = "JWT"
        plan = generate_build_plan(rules)
        result = self._run_patched(plan, rules, tmp_dir)
        assert result["files_generated"] == len(plan["files"])

    def test_multiple_modules(self, tmp_dir):
        rules = dict(self.MINIMAL)
        rules["required_backend_modules"] = ["users", "posts", "comments"]
        rules["required_pages"] = ["Login", "Feed", "Profile"]
        plan = generate_build_plan(rules)
        result = self._run_patched(plan, rules, tmp_dir)
        assert result["files_generated"] == len(plan["files"])

    def test_vue_frontend(self, tmp_dir):
        rules = dict(self.MINIMAL)
        rules["frontend_framework"] = "Vue"
        rules["required_backend_modules"] = ["todos"]
        rules["required_pages"] = ["Home", "About"]
        plan = generate_build_plan(rules)
        result = self._run_patched(plan, rules, tmp_dir)
        assert result["files_generated"] == len(plan["files"])

    def test_python_backend(self, tmp_dir):
        rules = dict(self.MINIMAL)
        rules["backend_framework"] = "FastAPI"
        rules["required_backend_modules"] = ["items"]
        rules["required_pages"] = ["Home"]
        rules["auth_method"] = "JWT"
        plan = generate_build_plan(rules)
        result = self._run_patched(plan, rules, tmp_dir)
        assert result["files_generated"] == len(plan["files"])
