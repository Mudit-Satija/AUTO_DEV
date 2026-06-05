import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from coding_agent.dependency_graph import (
    DependencyGraph,
    _extract_local_imports,
    _resolve_local_import,
    validate_graph,
    validate_imports,
)
from coding_agent.project_generator import generate_project


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bp(path, type_="source", purpose="", depends_on=None, provides=None):
    return {
        "path": path,
        "type": type_,
        "purpose": purpose or path,
        "depends_on": depends_on or [],
        "provides": provides or [],
    }


# ---------------------------------------------------------------------------
# DependencyGraph
# ---------------------------------------------------------------------------


class TestDependencyGraph:
    def test_get_all_paths(self):
        bps = [_bp("a.js"), _bp("b.js")]
        g = DependencyGraph(bps)
        assert g.get_all_paths() == {"a.js", "b.js"}

    def test_get_dependencies(self):
        bps = [_bp("a.js", depends_on=["b.js"])]
        g = DependencyGraph(bps)
        assert g.get_dependencies("a.js") == ["b.js"]

    def test_get_dependencies_missing_path(self):
        g = DependencyGraph([])
        assert g.get_dependencies("nonexistent.js") == []

    def test_get_provided(self):
        bps = [_bp("a.js", provides=["api"])]
        g = DependencyGraph(bps)
        assert g.get_provided("a.js") == ["api"]

    def test_get_provided_missing_path(self):
        g = DependencyGraph([])
        assert g.get_provided("nonexistent.js") == []


# ---------------------------------------------------------------------------
# validate_graph
# ---------------------------------------------------------------------------


class TestValidateGraph:
    def test_valid_graph_returns_empty_list(self):
        plan = {
            "files": [
                _bp("src/app.js", depends_on=["src/config.js"]),
                _bp("src/config.js"),
            ],
        }
        assert validate_graph(plan) == []

    def test_missing_dependency_detected(self):
        plan = {
            "files": [
                _bp("src/routes/auth.js", depends_on=["src/models/users.js", "src/config/database.js"]),
                _bp("src/config/database.js"),
            ],
        }
        errors = validate_graph(plan)
        assert len(errors) == 1
        assert "Missing Blueprint" in errors[0]
        assert "src/models/users.js" in errors[0]
        assert "src/routes/auth.js" in errors[0]

    def test_multiple_missing_dependencies(self):
        plan = {
            "files": [
                _bp("a.js", depends_on=["b.js", "c.js", "d.js"]),
                _bp("b.js"),
            ],
        }
        errors = validate_graph(plan)
        assert len(errors) == 2
        assert all("Missing Blueprint" in e for e in errors)

    def test_no_depends_on_is_tolerated(self):
        plan = {"files": [{"path": "a.js", "type": "source", "purpose": "A"}]}
        assert validate_graph(plan) == []

    def test_empty_build_plan(self):
        assert validate_graph({"files": []}) == []

    def test_missing_files_key(self):
        assert validate_graph({}) == []

    def test_backward_compatible_blueprint(self):
        plan = {
            "files": [
                {"path": "old.js", "type": "source", "purpose": "Legacy"},
                {"path": "new.js", "type": "source", "purpose": "New", "depends_on": ["old.js"]},
            ],
        }
        assert validate_graph(plan) == []

    def test_circular_dependency_not_blocked(self):
        plan = {
            "files": [
                _bp("a.js", depends_on=["b.js"]),
                _bp("b.js", depends_on=["a.js"]),
            ],
        }
        assert validate_graph(plan) == []


# ---------------------------------------------------------------------------
# _extract_local_imports
# ---------------------------------------------------------------------------


class TestExtractLocalImports:
    def test_require_single_quotes(self):
        content = "const x = require('./foo');"
        assert _extract_local_imports(content) == ["./foo"]

    def test_require_double_quotes(self):
        content = 'const x = require("./foo");'
        assert _extract_local_imports(content) == ["./foo"]

    def test_es_module_import(self):
        content = "import x from './foo';"
        assert _extract_local_imports(content) == ["./foo"]

    def test_es_module_from_double_quotes(self):
        content = 'import x from "./foo";'
        assert _extract_local_imports(content) == ["./foo"]

    def test_require_parent_path(self):
        content = "const x = require('../models/user');"
        assert _extract_local_imports(content) == ["../models/user"]

    def test_external_import_skipped(self):
        content = "const x = require('express');"
        assert _extract_local_imports(content) == []

    def test_multiple_imports(self):
        content = """
        const a = require('./a');
        const b = require('../b');
        import c from './c';
        """
        result = _extract_local_imports(content)
        assert result == ["./a", "../b", "./c"]

    def test_no_imports(self):
        content = "const x = 42;"
        assert _extract_local_imports(content) == []

    def test_empty_content(self):
        assert _extract_local_imports("") == []


# ---------------------------------------------------------------------------
# _resolve_local_import
# ---------------------------------------------------------------------------


class TestResolveLocalImport:
    def test_exact_match(self):
        result = _resolve_local_import("./app", "src/server.js", {"src/app.js"})
        assert result is None

    def test_with_extension(self):
        result = _resolve_local_import("./config/database", "src/app.js", {"src/config/database.js"})
        assert result is None

    def test_parent_path(self):
        result = _resolve_local_import("../models/users", "src/routes/auth.js", {"src/models/users.js"})
        assert result is None

    def test_index_file(self):
        result = _resolve_local_import("./routes", "src/app.js", {"src/routes/index.js"})
        assert result is None

    def test_not_found(self):
        result = _resolve_local_import("../models/users", "src/routes/auth.js", {"src/config.js"})
        assert result == "src/models/users"

    def test_external_import_returns_none(self):
        result = _resolve_local_import("express", "src/app.js", set())
        assert result is None

    def test_same_dir(self):
        result = _resolve_local_import("./helper", "src/utils.js", {"src/helper.js"})
        assert result is None

    def test_deeply_nested(self):
        result = _resolve_local_import("../../../lib/utils", "src/a/b/c/d.js", {"src/lib/utils.js"})
        assert result is None


# ---------------------------------------------------------------------------
# validate_imports
# ---------------------------------------------------------------------------


class TestValidateImports:
    def test_valid_imports_no_errors(self):
        plan = {"files": [_bp("a.js"), _bp("b.js")]}
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp / Path("a.js")).write_text("const b = require('./b');", encoding="utf-8")
            Path(tmp / Path("b.js")).write_text("", encoding="utf-8")
            errors = validate_imports(plan, tmp)
            assert errors == []

    def test_missing_import_detected(self):
        plan = {"files": [_bp("a.js")]}
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp / Path("a.js")).write_text("const b = require('./b');", encoding="utf-8")
            errors = validate_imports(plan, tmp)
            assert len(errors) == 1
            assert "Import Validation Failed" in errors[0]
            assert "a.js" in errors[0]
            assert "b" in errors[0]

    def test_external_import_ignored(self):
        plan = {"files": [_bp("a.js")]}
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp / Path("a.js")).write_text("const http = require('http');", encoding="utf-8")
            errors = validate_imports(plan, tmp)
            assert errors == []

    def test_import_resolved_to_existing_blueprint(self):
        plan = {"files": [_bp("a.js"), _bp("b.js")]}
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp / Path("a.js")).write_text("const b = require('./b');", encoding="utf-8")
            errors = validate_imports(plan, tmp)
            assert errors == []

    def test_no_files_on_disk(self):
        plan = {"files": [_bp("a.js")]}
        with tempfile.TemporaryDirectory() as tmp:
            errors = validate_imports(plan, tmp)
            assert errors == []

    def test_multiple_imports_in_one_file(self):
        plan = {"files": [_bp("a.js"), _bp("lib.js")]}
        with tempfile.TemporaryDirectory() as tmp:
            content = """
            const lib = require('./lib');
            const missing = require('./missing');
            """
            Path(tmp / Path("a.js")).write_text(content, encoding="utf-8")
            Path(tmp / Path("lib.js")).write_text("", encoding="utf-8")
            errors = validate_imports(plan, tmp)
            assert len(errors) == 1
            assert "missing" in errors[0]

    def test_empty_build_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            assert validate_imports({"files": []}, tmp) == []


# ---------------------------------------------------------------------------
# Integration: generation blocked on invalid graph
# ---------------------------------------------------------------------------


class TestGenerationBlocked:
    def test_generation_raises_on_missing_dependency(self):
        plan = {
            "files": [
                _bp("src/routes/auth.js", depends_on=["src/models/users.js"]),
            ],
        }
        with patch("coding_agent.bundle_generator.get_llm_response") as mock_llm:
            with pytest.raises(ValueError, match="Dependency Validation Failed"):
                generate_project(plan, {}, "/tmp/out")
            mock_llm.assert_not_called()

    def test_generation_proceeds_on_valid_graph(self):
        plan = {
            "files": [
                _bp("src/app.js", depends_on=["src/server.js"]),
                _bp("src/server.js"),
            ],
        }
        mock_llm = Mock(return_value="===FILE: src/app.js===\ncontent\n===END===\n===FILE: src/server.js===\ncontent\n===END===")
        mock_write = Mock(return_value={"path": "", "absolute_path": "", "bytes_written": 1})

        with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
             patch("coding_agent.bundle_generator.write_file", mock_write):
            result = generate_project(plan, {}, "/tmp/out")
            assert result["files_generated"] == 2

    def test_error_message_contains_missing_path(self):
        plan = {
            "files": [
                _bp("consumer.js", depends_on=["nonexistent.js"]),
            ],
        }
        with patch("coding_agent.bundle_generator.get_llm_response"):
            with pytest.raises(ValueError) as exc:
                generate_project(plan, {}, "/tmp/out")
            assert "nonexistent.js" in str(exc.value)
            assert "consumer.js" in str(exc.value)
