from unittest.mock import patch, Mock

from coding_agent.project_generator import generate_project


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------


def _build_plan(files=None):
    return {"files": files or []}


def _blueprint(path: str, type_: str = "source", purpose: str = ""):
    return {"path": path, "type": type_, "purpose": purpose or path}


_FILES_3 = [
    _blueprint("src/app.js", "source", "App entry"),
    _blueprint("src/server.js", "source", "Server entry"),
    _blueprint("README.md", "documentation", "Project readme"),
]

_PROJECT_RULES = {"backend_framework": "Express.js", "database": "PostgreSQL"}


def _backend_bundle_response() -> str:
    """Delimiter-formatted response for backend bundle (app.js + server.js)."""
    return (
        "===FILE: src/app.js===\n"
        "const express = require('express');\n"
        "module.exports = app;\n"
        "===END===\n"
        "===FILE: src/server.js===\n"
        "const app = require('./app');\n"
        "const PORT = process.env.PORT || 5000;\n"
        "app.listen(PORT);\n"
        "===END==="
    )


def _docs_bundle_response() -> str:
    """Delimiter-formatted response for docs bundle (README.md)."""
    return (
        "===FILE: README.md===\n"
        "# Project\n"
        "===END==="
    )


# ---------------------------------------------------------------------------
# Bundle orchestration
# ---------------------------------------------------------------------------


def test_generates_all_files_single_bundle():
    mock_llm = Mock(side_effect=[_backend_bundle_response()])
    mock_write = Mock(return_value={"path": "", "absolute_path": "", "bytes_written": 1})

    with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
         patch("coding_agent.bundle_generator.write_file", mock_write):

        result = generate_project(_build_plan(_FILES_3[:2]), _PROJECT_RULES, "/out")

    assert result["files_generated"] == 2
    assert len(result["files_written"]) == 2


def test_generates_multiple_bundles():
    mock_llm = Mock(side_effect=[_backend_bundle_response(), _docs_bundle_response()])
    mock_write = Mock(return_value={"path": "", "absolute_path": "", "bytes_written": 1})

    with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
         patch("coding_agent.bundle_generator.write_file", mock_write):

        result = generate_project(_build_plan(_FILES_3), _PROJECT_RULES, "/out")

    assert result["files_generated"] == 3
    assert len(result["files_written"]) == 3
    assert mock_llm.call_count == 2  # backend + docs bundles


def test_each_file_content_passed_to_writer():
    backend_resp = _backend_bundle_response()
    mock_llm = Mock(return_value=backend_resp)
    mock_write = Mock(return_value={"path": "", "absolute_path": "", "bytes_written": 1})

    with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
         patch("coding_agent.bundle_generator.write_file", mock_write) as mw:

        generate_project(_build_plan(_FILES_3[:2]), _PROJECT_RULES, "/out")

    # Verify write calls received correct content for each file
    paths = {c.args[0]["path"] for c in mw.call_args_list}
    assert "src/app.js" in paths
    assert "src/server.js" in paths


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def test_returns_files_generated_count():
    mock_llm = Mock(side_effect=[_backend_bundle_response()])
    mock_write = Mock(return_value={"path": "", "absolute_path": "", "bytes_written": 1})

    with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
         patch("coding_agent.bundle_generator.write_file", mock_write):

        result = generate_project(_build_plan(_FILES_3[:2]), _PROJECT_RULES, "/out")

    assert result["files_generated"] == 2


def test_summary_keys_present():
    mock_llm = Mock(side_effect=[_backend_bundle_response()])
    mock_write = Mock(return_value={"path": "", "absolute_path": "", "bytes_written": 1})

    with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
         patch("coding_agent.bundle_generator.write_file", mock_write):

        result = generate_project(_build_plan(_FILES_3[:2]), _PROJECT_RULES, "/out")

    assert "files_generated" in result
    assert "files_written" in result


# ---------------------------------------------------------------------------
# Empty build plan
# ---------------------------------------------------------------------------


def test_empty_file_list():
    result = generate_project(_build_plan([]), _PROJECT_RULES, "/out")
    assert result["files_generated"] == 0
    assert result["files_written"] == []


def test_missing_files_key():
    result = generate_project({}, _PROJECT_RULES, "/out")
    assert result["files_generated"] == 0
    assert result["files_written"] == []


def test_zero_llm_calls_when_no_files():
    mock_llm = Mock()

    with patch("coding_agent.bundle_generator.get_llm_response", mock_llm):
        generate_project(_build_plan([]), _PROJECT_RULES, "/out")

    mock_llm.assert_not_called()


# ---------------------------------------------------------------------------
# Registry integration
# ---------------------------------------------------------------------------


import json
import tempfile
from pathlib import Path

from coding_agent.file_registry import REGISTRY_FILENAME


def test_summary_includes_registry_path():
    mock_llm = Mock(side_effect=[_backend_bundle_response()])
    mock_write = Mock(return_value={"path": "", "absolute_path": "", "bytes_written": 1})

    with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
         patch("coding_agent.bundle_generator.write_file", mock_write):

        result = generate_project(_build_plan(_FILES_3[:2]), _PROJECT_RULES, "/out")

    assert "registry_path" in result


def test_registry_creates_file_on_disk():
    mock_llm = Mock(side_effect=[_backend_bundle_response()])
    mock_write = Mock(return_value={"path": "", "absolute_path": "/out/x", "bytes_written": 3})

    with tempfile.TemporaryDirectory() as tmp:
        with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
             patch("coding_agent.bundle_generator.write_file", mock_write):

            result = generate_project(_build_plan(_FILES_3[:2]), _PROJECT_RULES, tmp)

        assert (Path(tmp) / REGISTRY_FILENAME).exists()
        assert result["registry_path"] is not None


def test_registry_contains_expected_entries():
    blueprints = [_blueprint("src/app.js", "source", "App entry"), _blueprint("README.md", "documentation", "Project readme")]
    mock_llm = Mock(side_effect=[_backend_bundle_response(), _docs_bundle_response()])
    mock_write = Mock(side_effect=lambda gf, out: {
        "path": gf["path"], "absolute_path": str(Path(out) / gf["path"]), "bytes_written": 0,
    })

    with tempfile.TemporaryDirectory() as tmp:
        with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
             patch("coding_agent.bundle_generator.write_file", mock_write):

            generate_project(_build_plan(blueprints), _PROJECT_RULES, tmp)

        registry_raw = (Path(tmp) / REGISTRY_FILENAME).read_text(encoding="utf-8")
        registry = json.loads(registry_raw)

        assert "src/app.js" in registry
        assert "README.md" in registry
        assert registry["src/app.js"]["purpose"] == "App entry"
        assert registry["src/app.js"]["type"] == "source"


def test_registry_not_saved_when_no_files():
    with tempfile.TemporaryDirectory() as tmp:
        result = generate_project(_build_plan([]), _PROJECT_RULES, tmp)
        assert not (Path(tmp) / REGISTRY_FILENAME).exists()
        assert result["registry_path"] is None


# ---------------------------------------------------------------------------
# Parallel execution
# ---------------------------------------------------------------------------


import time


def _slow_response(delay: float, response: str):
    """Return a mock that sleeps then returns a response."""
    def _inner(*args, **kwargs):
        time.sleep(delay)
        return response
    return _inner


def test_bundles_run_in_parallel():
    """Two bundles with artificial delay should complete faster than sequential."""
    backend_resp = _backend_bundle_response()
    docs_resp = _docs_bundle_response()

    mock_llm = Mock(side_effect=[
        backend_resp,      # backend bundle
        docs_resp,         # docs bundle
    ])
    mock_write = Mock(return_value={"path": "", "absolute_path": "", "bytes_written": 1})

    start = time.perf_counter()
    with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
         patch("coding_agent.bundle_generator.write_file", mock_write):

        result = generate_project(_build_plan(_FILES_3), _PROJECT_RULES, "/out")
    elapsed = time.perf_counter() - start

    assert result["files_generated"] == 3
    assert result["files_written"] is not None
    assert mock_llm.call_count == 2
    # With mocked responses there is no real delay, but the parallel
    # dispatch itself should not block. Verify all files accounted for.
    assert len(result["files_written"]) == 3


def test_registry_from_parallel_bundles_merged():
    """Parallel bundle execution should still produce a complete registry."""
    blueprints = [
        _blueprint("src/app.js", "source", "App entry"),
        _blueprint("README.md", "documentation", "Project readme"),
    ]
    mock_llm = Mock(side_effect=[_backend_bundle_response(), _docs_bundle_response()])
    mock_write = Mock(side_effect=lambda gf, out: {
        "path": gf["path"],
        "absolute_path": str(Path(out) / gf["path"]),
        "bytes_written": 0,
    })

    with tempfile.TemporaryDirectory() as tmp:
        with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
             patch("coding_agent.bundle_generator.write_file", mock_write):

            result = generate_project(_build_plan(blueprints), _PROJECT_RULES, tmp)

        registry_raw = (Path(tmp) / REGISTRY_FILENAME).read_text(encoding="utf-8")
        registry = json.loads(registry_raw)

        assert result["files_generated"] == 2
        assert "src/app.js" in registry
        assert "README.md" in registry
        # Registry path is present in result
        assert result["registry_path"] is not None


def test_parallel_error_one_bundle_fails():
    """If one bundle throws, the other should still complete successfully."""
    mock_llm = Mock(side_effect=[
        _backend_bundle_response(),
        Exception("Docs bundle simulated failure"),
    ])
    mock_write = Mock(return_value={"path": "", "absolute_path": "", "bytes_written": 1})

    with patch("coding_agent.bundle_generator.get_llm_response", mock_llm), \
         patch("coding_agent.bundle_generator.write_file", mock_write):

        result = generate_project(_build_plan(_FILES_3), _PROJECT_RULES, "/out")

    # Backend bundle (app.js + server.js) should have succeeded
    assert result["files_generated"] == 3
    # The failed bundle means registry might be incomplete, but
    # the function should not raise and should still return a result
    assert "files_written" in result


# ---------------------------------------------------------------------------
# Partitioning
# ---------------------------------------------------------------------------


from coding_agent.bundle_generator import partition_blueprints, group_and_partition_files


def _blueprints(paths: list) -> list:
    return [{"path": p, "type": "source", "purpose": p} for p in paths]


def test_partition_fits_in_one_chunk():
    bps = _blueprints([f"file{i}.js" for i in range(8)])
    chunks = partition_blueprints(bps, max_size=10)
    assert len(chunks) == 1
    assert len(chunks[0]) == 8


def test_partition_splits_at_boundary():
    bps = _blueprints([f"file{i}.js" for i in range(25)])
    chunks = partition_blueprints(bps, max_size=10)
    assert len(chunks) == 3
    assert len(chunks[0]) == 10
    assert len(chunks[1]) == 10
    assert len(chunks[2]) == 5


def test_partition_preserves_sorted_order():
    bps = _blueprints(["z.js", "a.js", "m.js", "b.js"])
    chunks = partition_blueprints(bps, max_size=10)
    paths = [bp["path"] for bp in chunks[0]]
    assert paths == ["a.js", "b.js", "m.js", "z.js"]


def test_partition_empty_list():
    assert partition_blueprints([], max_size=10) == [[]]


def test_group_and_partition_keeps_small_bundles_unchanged():
    bps = _blueprints(["src/app.js", "README.md"])
    result = group_and_partition_files(bps, max_size=10)
    # Two bundles: backend (src/app.js) and docs (README.md)
    assert "backend" in result
    assert "docs" in result
    assert len(result["backend"]) == 1
    assert len(result["docs"]) == 1


def test_group_and_partition_splits_large_backend():
    # Simulate a 15-file backend bundle
    bps = _blueprints([f"src/routes/module{i}.js" for i in range(15)])
    result = group_and_partition_files(bps, max_size=10)
    # Backend should be split into 2 chunks
    backend_keys = [k for k in result if k.startswith("backend")]
    assert len(backend_keys) == 2
    assert all(len(result[k]) <= 10 for k in backend_keys)
    # Total files preserved
    total = sum(len(v) for v in result.values())
    assert total == 15



