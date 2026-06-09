"""Tests for the requirement validator - checks SRS coverage in generated code."""

from coding_agent.requirement_validator import validate_requirements


def _make_build_plan(files):
    return {"files": files}


def _make_blueprint(path, requirements=None, purpose="", spec=None):
    bp = {
        "path": path,
        "type": "source" if not path.endswith(".md") else "documentation",
        "purpose": purpose,
        "depends_on": [],
        "provides": [],
        "requirements": requirements or [],
    }
    if spec:
        bp["spec"] = spec
    return bp


def test_empty_project_dir_returns_error(tmp_path):
    result = validate_requirements(str(tmp_path / "nonexistent"), _make_build_plan([]))
    assert result["success"] is False
    assert len(result["errors"]) == 1
    assert "not found" in result["errors"][0]["error"]


def test_missing_file_reported(tmp_path):
    bp = _make_blueprint("src/app.js", requirements=["app setup"])
    plan = _make_build_plan([bp])
    result = validate_requirements(str(tmp_path), plan)
    assert result["success"] is False
    assert any("not generated" in e["error"] for e in result["errors"])


def test_export_requirement_satisfied(tmp_path):
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "component.jsx").write_text("export default function App() {}", encoding="utf-8")

    bp = _make_blueprint("src/component.jsx", requirements=["component export"])
    plan = _make_build_plan([bp])
    result = validate_requirements(str(tmp_path), plan)
    assert result["success"] is True


def test_export_requirement_missing(tmp_path):
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "component.jsx").write_text("const x = 1;", encoding="utf-8")

    bp = _make_blueprint("src/component.jsx", requirements=["component export"])
    plan = _make_build_plan([bp])
    result = validate_requirements(str(tmp_path), plan)
    assert result["success"] is False


def test_server_start_requirement(tmp_path):
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "app.js").write_text(
        "const express = require('express');\nconst app = express();\napp.listen(3000);",
        encoding="utf-8",
    )
    bp = _make_blueprint("src/app.js", requirements=["server start"])
    plan = _make_build_plan([bp])
    result = validate_requirements(str(tmp_path), plan)
    assert result["success"] is True


def test_multiple_requirements_all_pass(tmp_path):
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "app.js").write_text(
        "const express = require('express');\nconst app = express();\n"
        "app.use('/api', router);\napp.listen(3000);\n"
        "app.use((err, req, res, next) => {});",
        encoding="utf-8",
    )
    bp = _make_blueprint("src/app.js", requirements=["app setup", "server start", "route mounting", "error handling"])
    plan = _make_build_plan([bp])
    result = validate_requirements(str(tmp_path), plan)
    assert result["success"] is True


def test_no_requirements_passes(tmp_path):
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "random.js").write_text("anything", encoding="utf-8")
    bp = _make_blueprint("src/random.js", requirements=[])
    plan = _make_build_plan([bp])
    result = validate_requirements(str(tmp_path), plan)
    assert result["success"] is True


def test_python_model_definition(tmp_path):
    app = tmp_path / "app"
    app.mkdir(parents=True)
    (app / "models.py").write_text(
        "from sqlalchemy import Column, Integer, String\nclass Item(Base):\n    __tablename__ = 'items'",
        encoding="utf-8",
    )
    bp = _make_blueprint("app/models.py", requirements=["model definition"])
    plan = _make_build_plan([bp])
    result = validate_requirements(str(tmp_path), plan)
    assert result["success"] is True


def test_database_schema_creation(tmp_path):
    (tmp_path / "migrations").mkdir(parents=True)
    (tmp_path / "migrations" / "001.sql").write_text(
        "CREATE TABLE items (id INT PRIMARY KEY);", encoding="utf-8"
    )
    bp = _make_blueprint("migrations/001.sql", requirements=["schema creation"])
    plan = _make_build_plan([bp])
    result = validate_requirements(str(tmp_path), plan)
    assert result["success"] is True
