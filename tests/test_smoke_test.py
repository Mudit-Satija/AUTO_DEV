"""Tests for coding_agent.smoke_test — runtime smoke testing."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_agent.smoke_test import (
    _check_file_imports,
    _collect_file_set,
    _extract_local_imports,
    _import_exists,
    _resolve_relative_path,
    _smoke_test_java,
    _smoke_test_node,
    _smoke_test_python,
    _smoke_test_react,
    _smoke_test_vue,
    run_smoke_tests,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_project():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def _write(root: Path, path: str, content: str = "") -> Path:
    """Write a file under root, creating parent directories."""
    full = root / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    return full


# ---------------------------------------------------------------------------
# run_smoke_tests — integration
# ---------------------------------------------------------------------------


class TestRunSmokeTests:
    def test_nonexistent_directory(self):
        errors = run_smoke_tests("/nonexistent/path", {})
        assert len(errors) == 1
        assert "not found" in errors[0]

    def test_node_backend_all_pass(self, tmp_project):
        _write(tmp_project, "backend/package.json", "{}")
        _write(tmp_project, "backend/src/app.js", "const x = 1;")
        _write(tmp_project, "backend/src/server.js", "const app = require('./app');\nconst x = 1;")
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert errors == []

    def test_node_backend_missing_package_json(self, tmp_project):
        _write(tmp_project, "backend/src/app.js", "const x = 1;")
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert any("package.json not found" in e for e in errors)

    def test_node_backend_missing_import(self, tmp_project):
        _write(tmp_project, "backend/package.json", "{}")
        _write(tmp_project, "backend/src/app.js", "const missing = require('./nonexistent');")
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert any("missing file" in e and "nonexistent" in e for e in errors)

    def test_react_frontend_all_pass(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        _write(tmp_project, "frontend/vite.config.js", "")
        _write(tmp_project, "frontend/index.html", "<html></html>")
        _write(tmp_project, "frontend/src/main.jsx", "import App from './App';\nconst x = 1;")
        _write(tmp_project, "frontend/src/App.jsx", "export default function App() { return null; }")
        rules = {"backend_framework": "Unknown", "frontend_framework": "React"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert errors == []

    def test_react_frontend_missing_package(self, tmp_project):
        _write(tmp_project, "frontend/vite.config.js", "")
        _write(tmp_project, "frontend/index.html", "")
        _write(tmp_project, "frontend/src/App.jsx", "")
        rules = {"backend_framework": "Unknown", "frontend_framework": "React"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert any("package_frontend.json not found" in e for e in errors)

    def test_react_frontend_missing_required_config(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        _write(tmp_project, "frontend/src/App.jsx", "")
        rules = {"backend_framework": "Unknown", "frontend_framework": "React"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert any("vite.config.js" in e for e in errors)
        assert any("index.html" in e for e in errors)

    def test_react_frontend_jsx_import_missing(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        _write(tmp_project, "frontend/vite.config.js", "")
        _write(tmp_project, "frontend/index.html", "")
        _write(tmp_project, "frontend/src/main.jsx", "import Missing from './Missing';")
        rules = {"backend_framework": "Unknown", "frontend_framework": "React"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert any("missing file" in e and "Missing" in e for e in errors)

    def test_react_frontend_jsx_import_resolved(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        _write(tmp_project, "frontend/vite.config.js", "")
        _write(tmp_project, "frontend/index.html", "")
        _write(tmp_project, "frontend/src/main.jsx", "import App from './App';")
        _write(tmp_project, "frontend/src/App.jsx", "export default function App() { return null; }")
        rules = {"backend_framework": "Unknown", "frontend_framework": "React"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert errors == []

    def test_python_backend_all_pass(self, tmp_project):
        _write(tmp_project, "requirements.txt", "fastapi\nuvicorn")
        _write(tmp_project, "main.py", "print('hello')")
        _write(tmp_project, "app/__init__.py", "")
        _write(tmp_project, "app/main.py", "from app.core.config import settings\nx = 1")
        _write(tmp_project, "app/core/config.py", "settings = {}")
        rules = {"backend_framework": "FastAPI", "frontend_framework": "Unknown"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert errors == []

    def test_python_backend_syntax_error(self, tmp_project):
        _write(tmp_project, "requirements.txt", "")
        _write(tmp_project, "main.py", "def broken(")
        rules = {"backend_framework": "FastAPI", "frontend_framework": "Unknown"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert any("Python syntax error" in e for e in errors)

    def test_python_backend_missing_requirements(self, tmp_project):
        _write(tmp_project, "main.py", "x = 1")
        rules = {"backend_framework": "FastAPI", "frontend_framework": "Unknown"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert any("requirements.txt not found" in e for e in errors)

    def test_vue_frontend_all_pass(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        _write(tmp_project, "frontend/src/App.vue", "<template><div>App</div></template>")
        rules = {"backend_framework": "Unknown", "frontend_framework": "Vue.js"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert errors == []

    def test_vue_frontend_missing_vue_files(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        rules = {"backend_framework": "Unknown", "frontend_framework": "Vue.js"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert any("No .vue files found" in e for e in errors)

    def test_unknown_frameworks_no_errors(self, tmp_project):
        _write(tmp_project, "README.md", "# Project")
        rules = {"backend_framework": "Unknown", "frontend_framework": "Unknown"}
        errors = run_smoke_tests(str(tmp_project), rules)
        assert errors == []

    def test_empty_rules_no_backend_frontend(self, tmp_project):
        _write(tmp_project, "README.md", "# Project")
        errors = run_smoke_tests(str(tmp_project), {})
        assert errors == []


# ---------------------------------------------------------------------------
# _smoke_test_node
# ---------------------------------------------------------------------------


class TestSmokeTestNode:
    def test_missing_package_json(self, tmp_project):
        _write(tmp_project, "backend/src/app.js", "const x = 1;")
        errors = _smoke_test_node(tmp_project)
        assert any("package.json not found" in e for e in errors)

    def test_no_js_files(self, tmp_project):
        _write(tmp_project, "backend/package.json", "{}")
        errors = _smoke_test_node(tmp_project)
        assert any("No .js files found" in e for e in errors)

    def test_missing_import_detected(self, tmp_project):
        _write(tmp_project, "backend/package.json", "{}")
        _write(tmp_project, "backend/src/app.js", "const x = require('./missing');")
        errors = _smoke_test_node(tmp_project)
        assert any("missing file" in e and "missing" in e for e in errors)

    def test_valid_import_no_error(self, tmp_project):
        _write(tmp_project, "backend/package.json", "{}")
        _write(tmp_project, "backend/src/app.js", "const config = require('./config');")
        _write(tmp_project, "backend/src/config.js", "module.exports = {};")
        errors = _smoke_test_node(tmp_project)
        assert errors == []

    def test_external_import_ignored(self, tmp_project):
        _write(tmp_project, "backend/package.json", "{}")
        _write(tmp_project, "backend/src/app.js", "const express = require('express');")
        errors = _smoke_test_node(tmp_project)
        assert errors == []

    def test_node_modules_skipped(self, tmp_project):
        _write(tmp_project, "backend/package.json", "{}")
        _write(tmp_project, "backend/src/app.js", "const x = 1;")
        _write(tmp_project, "backend/node_modules/express/index.js", "module.exports = {};")
        errors = _smoke_test_node(tmp_project)
        assert errors == []


# ---------------------------------------------------------------------------
# _smoke_test_react
# ---------------------------------------------------------------------------


class TestSmokeTestReact:
    def test_missing_package_frontend(self, tmp_project):
        errors = _smoke_test_react(tmp_project)
        assert any("package_frontend.json not found" in e for e in errors)

    def test_missing_required_configs(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        errors = _smoke_test_react(tmp_project)
        assert any("vite.config.js" in e for e in errors)
        assert any("index.html" in e for e in errors)

    def test_jsx_import_resolved(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        _write(tmp_project, "frontend/vite.config.js", "")
        _write(tmp_project, "frontend/index.html", "")
        _write(tmp_project, "frontend/src/main.jsx", "import App from './App';\nconst x = 1;")
        _write(tmp_project, "frontend/src/App.jsx", "export default function App() { return null; }")
        errors = _smoke_test_react(tmp_project)
        assert errors == []

    def test_js_import_to_jsx_resolved(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        _write(tmp_project, "frontend/vite.config.js", "")
        _write(tmp_project, "frontend/index.html", "")
        _write(tmp_project, "frontend/src/main.js", "import App from './App';")
        _write(tmp_project, "frontend/src/App.jsx", "export default function App() { return null; }")
        errors = _smoke_test_react(tmp_project)
        assert errors == []


# ---------------------------------------------------------------------------
# _smoke_test_python
# ---------------------------------------------------------------------------


class TestSmokeTestPython:
    def test_valid_python(self, tmp_project):
        _write(tmp_project, "requirements.txt", "")
        _write(tmp_project, "main.py", "print('hello')\nx = 42")
        errors = _smoke_test_python(tmp_project)
        assert errors == []

    def test_syntax_error(self, tmp_project):
        _write(tmp_project, "requirements.txt", "")
        _write(tmp_project, "main.py", "def broken(")
        errors = _smoke_test_python(tmp_project)
        assert any("Python syntax error" in e for e in errors)

    def test_missing_requirements(self, tmp_project):
        _write(tmp_project, "main.py", "x = 1")
        errors = _smoke_test_python(tmp_project)
        assert any("requirements.txt not found" in e for e in errors)

    def test_no_py_files(self, tmp_project):
        _write(tmp_project, "requirements.txt", "")
        errors = _smoke_test_python(tmp_project)
        assert any("No .py files found" in e for e in errors)

    def test_multiple_files_all_valid(self, tmp_project):
        _write(tmp_project, "requirements.txt", "")
        _write(tmp_project, "app/__init__.py", "")
        _write(tmp_project, "app/main.py", "from app.core.config import settings\nx = 1")
        _write(tmp_project, "app/core/config.py", "settings = {'debug': True}")
        errors = _smoke_test_python(tmp_project)
        assert errors == []

    def test_one_bad_file_among_many(self, tmp_project):
        _write(tmp_project, "requirements.txt", "")
        _write(tmp_project, "app/__init__.py", "")
        _write(tmp_project, "app/main.py", "this is not valid python @@@")
        errors = _smoke_test_python(tmp_project)
        assert any("Python syntax error" in e for e in errors)


# ---------------------------------------------------------------------------
# _smoke_test_vue
# ---------------------------------------------------------------------------


class TestSmokeTestVue:
    def test_all_pass(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        _write(tmp_project, "frontend/src/App.vue", "<template><div>App</div></template>")
        errors = _smoke_test_vue(tmp_project)
        assert errors == []

    def test_missing_package(self, tmp_project):
        _write(tmp_project, "frontend/src/App.vue", "")
        errors = _smoke_test_vue(tmp_project)
        assert any("package_frontend.json not found" in e for e in errors)

    def test_no_vue_files(self, tmp_project):
        _write(tmp_project, "frontend/package.json", "{}")
        errors = _smoke_test_vue(tmp_project)
        assert any("No .vue files found" in e for e in errors)


# ---------------------------------------------------------------------------
# _smoke_test_java
# ---------------------------------------------------------------------------


class TestSmokeTestJava:
    def test_missing_pom(self, tmp_project):
        _write(tmp_project, "src/main/java/com/app/Application.java", "class Application {}")
        errors = _smoke_test_java(tmp_project)
        assert any("pom.xml not found" in e for e in errors)

    def test_no_java_files(self, tmp_project):
        _write(tmp_project, "pom.xml", "<project></project>")
        errors = _smoke_test_java(tmp_project)
        assert any("No .java files found" in e for e in errors)

    def test_pom_and_java_skip_compile(self, tmp_project):
        _write(tmp_project, "pom.xml", "<project></project>")
        _write(tmp_project, "src/main/java/com/app/Application.java", "class Application {}")
        errors = _smoke_test_java(tmp_project)
        # Compile may or may not run; just check no unexpected errors
        assert all("not found" not in e for e in errors)


# ---------------------------------------------------------------------------
# _extract_local_imports
# ---------------------------------------------------------------------------


class TestExtractLocalImports:
    def test_require_single_quotes(self):
        assert _extract_local_imports("const x = require('./foo');") == ["./foo"]

    def test_require_double_quotes(self):
        assert _extract_local_imports('const x = require("./foo");') == ["./foo"]

    def test_es_module_import(self):
        assert _extract_local_imports("import x from './foo';") == ["./foo"]

    def test_es_module_double_quotes(self):
        assert _extract_local_imports('import x from "./foo";') == ["./foo"]

    def test_parent_path(self):
        assert _extract_local_imports("const x = require('../models/user');") == ["../models/user"]

    def test_external_import_skipped(self):
        assert _extract_local_imports("const x = require('express');") == []

    def test_multiple_imports(self):
        content = """
        const a = require('./a');
        const b = require('../b');
        import c from './c';
        """
        result = _extract_local_imports(content)
        assert result == ["./a", "../b", "./c"]

    def test_no_imports(self):
        assert _extract_local_imports("const x = 42;") == []

    def test_empty_content(self):
        assert _extract_local_imports("") == []


# ---------------------------------------------------------------------------
# _resolve_relative_path
# ---------------------------------------------------------------------------


class TestResolveRelativePath:
    def test_same_dir(self):
        assert _resolve_relative_path("./app", "src/server.js") == "src/app"

    def test_parent_dir(self):
        assert _resolve_relative_path("../models/user", "src/routes/auth.js") == "src/models/user"

    def test_external_import_returns_none(self):
        assert _resolve_relative_path("express", "src/app.js") is None

    def test_deeply_nested(self):
        assert _resolve_relative_path("../../../lib/utils", "src/a/b/c/d.js") == "src/lib/utils"

    def test_current_dir_dot(self):
        assert _resolve_relative_path("./helper", "src/utils.js") == "src/helper"

    def test_backslash_normalized(self):
        result = _resolve_relative_path("./helper", "src\\utils.js")
        assert result == "src/helper"


# ---------------------------------------------------------------------------
# _import_exists
# ---------------------------------------------------------------------------


class TestImportExists:
    def test_exact_match(self):
        assert _import_exists("src/app", {"src/app.js"}) is True

    def test_extension_match(self):
        assert _import_exists("src/app", {"src/app.jsx"}) is True

    def test_index_match(self):
        assert _import_exists("src/routes", {"src/routes/index.js"}) is True

    def test_not_found(self):
        assert _import_exists("src/missing", {"src/app.js"}) is False

    def test_empty_set(self):
        assert _import_exists("src/app", set()) is False


# ---------------------------------------------------------------------------
# _collect_file_set
# ---------------------------------------------------------------------------


class TestCollectFileSet:
    def test_collects_js_files(self, tmp_project):
        _write(tmp_project, "src/app.js", "")
        _write(tmp_project, "src/config.js", "")
        result = _collect_file_set(tmp_project, {".js"})
        assert result == {"src/app.js", "src/config.js"}

    def test_excludes_node_modules(self, tmp_project):
        _write(tmp_project, "src/app.js", "")
        _write(tmp_project, "node_modules/express/index.js", "")
        result = _collect_file_set(tmp_project, {".js"})
        assert result == {"src/app.js"}

    def test_multiple_extensions(self, tmp_project):
        _write(tmp_project, "src/app.js", "")
        _write(tmp_project, "src/App.jsx", "")
        _write(tmp_project, "README.md", "")
        result = _collect_file_set(tmp_project, {".js", ".jsx"})
        assert result == {"src/app.js", "src/App.jsx"}


# ---------------------------------------------------------------------------
# _check_file_imports
# ---------------------------------------------------------------------------


class TestCheckFileImports:
    def test_no_imports(self, tmp_project):
        f = _write(tmp_project, "src/app.js", "const x = 1;")
        errors = _check_file_imports(f, "src/app.js", {"src/config.js"}, "Import")
        assert errors == []

    def test_valid_import(self, tmp_project):
        f = _write(tmp_project, "src/app.js", "const c = require('./config');")
        errors = _check_file_imports(f, "src/app.js", {"src/config.js"}, "Import")
        assert errors == []

    def test_missing_import(self, tmp_project):
        f = _write(tmp_project, "src/app.js", "const m = require('./missing');")
        errors = _check_file_imports(f, "src/app.js", {"src/config.js"}, "Import")
        assert any("missing file" in e for e in errors)

    def test_external_import_ignored(self, tmp_project):
        f = _write(tmp_project, "src/app.js", "const e = require('express');")
        errors = _check_file_imports(f, "src/app.js", set(), "Import")
        assert errors == []


# ---------------------------------------------------------------------------
# Integration with generate_project
# ---------------------------------------------------------------------------


class TestGenerateProjectIntegration:
    def test_smoke_test_invoked_during_generation(self, tmp_project):
        from coding_agent.project_generator import generate_project

        build_plan = {
            "files": [
                {"path": "backend/package.json", "type": "config", "purpose": "Dependencies"},
                {"path": "backend/src/app.js", "type": "source", "purpose": "App entry", "depends_on": [], "provides": []},
            ],
        }
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}

        mock_llm = Mock(return_value=(
            "===FILE: backend/package.json===\n{}\n===END===\n"
            "===FILE: backend/src/app.js===\nconst x = 1;\n===END==="
        ))
        mock_write = Mock(return_value={"path": "", "absolute_path": str(tmp_project / "x"), "bytes_written": 1})

        with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
             patch("coding_agent.bundle_generator.write_file", mock_write):
            result = generate_project(build_plan, rules, str(tmp_project))

        assert result["files_generated"] == 2

    def test_smoke_test_reports_errors(self, tmp_project):
        from coding_agent.project_generator import generate_project

        build_plan = {
            "files": [
                {"path": "backend/package.json", "type": "config", "purpose": "Dependencies"},
                {"path": "backend/src/app.js", "type": "source", "purpose": "App entry", "depends_on": [], "provides": []},
            ],
        }
        rules = {"backend_framework": "Express.js", "frontend_framework": "Unknown"}

        mock_llm = Mock(return_value=(
            "===FILE: backend/package.json===\nnot-valid-json\n===END===\n"
            "===FILE: backend/src/app.js===\nconst x = require('./missing');\n===END==="
        ))
        mock_write = Mock(return_value={"path": "", "absolute_path": str(tmp_project / "x"), "bytes_written": 1})

        with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
             patch("coding_agent.bundle_generator.write_file", mock_write):
            result = generate_project(build_plan, rules, str(tmp_project))

        assert result["files_generated"] == 2
