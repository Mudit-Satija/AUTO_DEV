import json
import tempfile
from pathlib import Path

from coding_agent.file_registry import register_file, save_registry, load_registry, REGISTRY_FILENAME


# ---------------------------------------------------------------------------
# register_file
# ---------------------------------------------------------------------------


def _blueprint(path="src/app.js", type_="source", purpose="App entry"):
    return {"path": path, "type": type_, "purpose": purpose}


def _metadata(path="src/app.js", absolute_path="/out/src/app.js", bytes_written=42):
    return {"path": path, "absolute_path": absolute_path, "bytes_written": bytes_written}


def test_register_adds_entry():
    registry = {}
    result = register_file(registry, _blueprint(), _metadata())
    assert "src/app.js" in result


def test_register_returns_registry():
    registry = {}
    result = register_file(registry, _blueprint(), _metadata())
    assert result is registry


def test_register_stores_purpose():
    registry = {}
    register_file(registry, _blueprint(purpose="API routes"), _metadata())
    assert registry["src/app.js"]["purpose"] == "API routes"


def test_register_stores_type():
    registry = {}
    register_file(registry, _blueprint(type_="source"), _metadata())
    assert registry["src/app.js"]["type"] == "source"


def test_register_stores_absolute_path():
    registry = {}
    register_file(registry, _blueprint(), _metadata(absolute_path="/project/src/app.js"))
    assert registry["src/app.js"]["absolute_path"] == "/project/src/app.js"


def test_register_multiple_files():
    registry = {}
    register_file(registry, _blueprint("a.js"), _metadata("a.js"))
    register_file(registry, _blueprint("b.js"), _metadata("b.js"))
    assert set(registry.keys()) == {"a.js", "b.js"}


def test_register_overwrites_existing_key():
    registry = {}
    register_file(registry, _blueprint("same.js", purpose="old"), _metadata("same.js"))
    register_file(registry, _blueprint("same.js", purpose="new"), _metadata("same.js"))
    assert registry["same.js"]["purpose"] == "new"


def test_register_missing_path_falls_back():
    registry = {}
    register_file(registry, {}, _metadata())
    assert "unknown" in registry


# ---------------------------------------------------------------------------
# save_registry / load_registry
# ---------------------------------------------------------------------------


def test_save_registry_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        registry = {"f.js": {"purpose": "test", "type": "source", "absolute_path": str(Path(tmp) / "f.js")}}
        save_registry(registry, tmp)
        assert (Path(tmp) / REGISTRY_FILENAME).exists()


def test_save_registry_returns_path():
    with tempfile.TemporaryDirectory() as tmp:
        path = save_registry({}, tmp)
        assert path.endswith(REGISTRY_FILENAME)


def test_save_and_load_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        original = {
            "src/app.js": {"purpose": "App entry", "type": "source", "absolute_path": str(Path(tmp) / "src" / "app.js")},
            "README.md": {"purpose": "Documentation", "type": "documentation", "absolute_path": str(Path(tmp) / "README.md")},
        }
        save_registry(original, tmp)
        loaded = load_registry(tmp)
        assert loaded == original


def test_save_registry_is_valid_json():
    with tempfile.TemporaryDirectory() as tmp:
        registry = {"f.js": {"purpose": "", "type": "", "absolute_path": ""}}
        save_registry(registry, tmp)
        data = json.loads((Path(tmp) / REGISTRY_FILENAME).read_text(encoding="utf-8"))
        assert data == registry


def test_load_registry_returns_empty_dict_when_missing():
    with tempfile.TemporaryDirectory() as tmp:
        result = load_registry(tmp)
        assert result == {}


def test_load_registry_nonexistent_directory():
    with tempfile.TemporaryDirectory() as tmp:
        nonexistent = Path(tmp) / "does_not_exist"
        result = load_registry(str(nonexistent))
        assert result == {}


def test_save_registry_indented():
    with tempfile.TemporaryDirectory() as tmp:
        save_registry({"k": {"purpose": "v", "type": "t", "absolute_path": "/a"}}, tmp)
        content = (Path(tmp) / REGISTRY_FILENAME).read_text(encoding="utf-8")
        assert content.startswith("{")
        assert "  " in content


# ---------------------------------------------------------------------------
# REGISTRY_FILENAME constant
# ---------------------------------------------------------------------------


def test_registry_filename_constant():
    assert REGISTRY_FILENAME == ".autodev_registry.json"
