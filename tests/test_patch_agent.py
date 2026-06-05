import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from coding_agent.file_registry import save_registry
from coding_agent.patch_agent import patch_file


MOCK_FIXED_CONTENT = "console.log('fixed');"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_project(tmp: str, files: dict) -> None:
    """Create a minimal project with files and a registry on disk."""
    registry = {}
    for rel_path, content in files.items():
        abs_path = Path(tmp) / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(content, encoding="utf-8")
        registry[rel_path] = {
            "absolute_path": str(abs_path.resolve()),
            "purpose": "",
            "type": "",
        }
    save_registry(registry, tmp)


# ---------------------------------------------------------------------------
# Registry lookup
# ---------------------------------------------------------------------------


def test_returns_error_when_file_not_in_registry():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/other.js": "content"})
        result = patch_file("src/app.js", "bug description", tmp)
    assert result["status"] == "error"
    assert "not found in project registry" in result["error"]


def test_returns_error_when_registry_missing():
    # tmp has no .autodev_registry.json → empty registry
    with tempfile.TemporaryDirectory() as tmp:
        result = patch_file("src/app.js", "bug", tmp)
    assert result["status"] == "error"


def test_returns_error_when_file_missing_on_disk():
    with tempfile.TemporaryDirectory() as tmp:
        registry = {
            "missing.js": {
                "absolute_path": str(Path(tmp) / "missing.js"),
                "purpose": "",
                "type": "",
            }
        }
        save_registry(registry, tmp)
        # Don't create missing.js on disk
        result = patch_file("missing.js", "bug", tmp)
    assert result["status"] == "error"
    assert "does not exist on disk" in result["error"]


# ---------------------------------------------------------------------------
# Successful patch
# ---------------------------------------------------------------------------


def test_returns_patched_status():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT):
            result = patch_file("src/app.js", "bug", tmp)
    assert result["status"] == "patched"


def test_overwrites_file_content():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT):
            patch_file("src/app.js", "bug", tmp)
        actual = (Path(tmp) / "src" / "app.js").read_text(encoding="utf-8")
    assert actual == MOCK_FIXED_CONTENT


def test_only_target_file_modified():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {
            "src/app.js": "old app",
            "src/server.js": "old server",
        })
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT):
            patch_file("src/app.js", "bug", tmp)
        assert (Path(tmp) / "src" / "app.js").read_text(encoding="utf-8") == MOCK_FIXED_CONTENT
        assert (Path(tmp) / "src" / "server.js").read_text(encoding="utf-8") == "old server"


# ---------------------------------------------------------------------------
# Qwen invocation
# ---------------------------------------------------------------------------


def test_llm_called_once():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT) as mock:
            patch_file("src/app.js", "bug", tmp)
    mock.assert_called_once()


def test_llm_called_with_coder_model():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT) as mock:
            patch_file("src/app.js", "bug", tmp)
    _, kwargs = mock.call_args
    assert kwargs.get("model") == "qwen/qwen3-next-80b-a3b-instruct"


def test_llm_not_called_when_file_missing():
    with tempfile.TemporaryDirectory() as tmp:
        with patch("coding_agent.patch_agent.get_llm_response") as mock:
            patch_file("nonexistent.js", "bug", tmp)
    mock.assert_not_called()


# ---------------------------------------------------------------------------
# Prompt contents
# ---------------------------------------------------------------------------


def test_prompt_contains_file_path():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT) as mock:
            patch_file("src/app.js", "bug", tmp)
    prompt = mock.call_args[0][0]
    assert "src/app.js" in prompt


def test_prompt_contains_error_description():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT) as mock:
            patch_file("src/app.js", "Database query returns undefined", tmp)
    prompt = mock.call_args[0][0]
    assert "Database query returns undefined" in prompt


def test_prompt_contains_current_content():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "OLD_CODE_HERE"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT) as mock:
            patch_file("src/app.js", "bug", tmp)
    prompt = mock.call_args[0][0]
    assert "OLD_CODE_HERE" in prompt


def test_prompt_instructs_fix_only_this_file():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT) as mock:
            patch_file("src/app.js", "bug", tmp)
    prompt = mock.call_args[0][0]
    assert "Fix only this file" in prompt


def test_prompt_instructs_no_markdown():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT) as mock:
            patch_file("src/app.js", "bug", tmp)
    prompt = mock.call_args[0][0]
    assert "Do NOT wrap the code in markdown code blocks" in prompt


def test_prompt_instructs_no_explanations():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT) as mock:
            patch_file("src/app.js", "bug", tmp)
    prompt = mock.call_args[0][0]
    assert "Do NOT include any explanations" in prompt


def test_prompt_instructs_complete_code():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT) as mock:
            patch_file("src/app.js", "bug", tmp)
    prompt = mock.call_args[0][0]
    assert "complete and functional" in prompt


# ---------------------------------------------------------------------------
# Return value
# ---------------------------------------------------------------------------


def test_returns_file_path():
    with tempfile.TemporaryDirectory() as tmp:
        _create_project(tmp, {"src/app.js": "old code"})
        with patch("coding_agent.patch_agent.get_llm_response", return_value=MOCK_FIXED_CONTENT):
            result = patch_file("src/app.js", "bug", tmp)
    assert result["file_path"] == "src/app.js"
