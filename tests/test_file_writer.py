import os
import tempfile
from pathlib import Path

from coding_agent.file_writer import write_file


def _generated_file(path: str = "test.txt", content: str = "hello world"):
    return {"path": path, "content": content}


# ---------------------------------------------------------------------------
# Basic write
# ---------------------------------------------------------------------------


def test_writes_file_to_disk():
    with tempfile.TemporaryDirectory() as tmp:
        result = write_file(_generated_file(), tmp)
        target = Path(tmp) / "test.txt"
        assert target.exists()
        assert target.read_text() == "hello world"


def test_returns_metadata():
    with tempfile.TemporaryDirectory() as tmp:
        result = write_file(_generated_file(), tmp)
        assert "path" in result
        assert "absolute_path" in result
        assert "bytes_written" in result


def test_metadata_path_matches_input():
    with tempfile.TemporaryDirectory() as tmp:
        result = write_file(_generated_file("src/app.js", "content"), tmp)
        assert result["path"] == "src/app.js"


def test_metadata_absolute_path_is_absolute():
    with tempfile.TemporaryDirectory() as tmp:
        result = write_file(_generated_file(), tmp)
        assert os.path.isabs(result["absolute_path"])


def test_metadata_bytes_written_correct():
    with tempfile.TemporaryDirectory() as tmp:
        result = write_file(_generated_file(content="abc"), tmp)
        assert result["bytes_written"] == 3


# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------


def test_content_preserved():
    content = "console.log('hello');\n"
    with tempfile.TemporaryDirectory() as tmp:
        write_file(_generated_file(content=content), tmp)
        assert (Path(tmp) / "test.txt").read_text() == content


def test_empty_content():
    with tempfile.TemporaryDirectory() as tmp:
        write_file(_generated_file(content=""), tmp)
        assert (Path(tmp) / "test.txt").read_text() == ""


def test_unicode_content():
    content = "def greet(name: str) -> str:\n    return f\"Hello, {name}!\"\n"
    with tempfile.TemporaryDirectory() as tmp:
        write_file(_generated_file(content=content), tmp)
        assert (Path(tmp) / "test.txt").read_text() == content


# ---------------------------------------------------------------------------
# Directory creation
# ---------------------------------------------------------------------------


def test_creates_single_nested_directory():
    with tempfile.TemporaryDirectory() as tmp:
        write_file(_generated_file("src/app.js", "content"), tmp)
        assert (Path(tmp) / "src" / "app.js").exists()


def test_creates_deeply_nested_directories():
    with tempfile.TemporaryDirectory() as tmp:
        write_file(_generated_file("a/b/c/d/e/file.txt", "deep"), tmp)
        assert (Path(tmp) / "a" / "b" / "c" / "d" / "e" / "file.txt").exists()


def test_creates_multiple_directories_independently():
    with tempfile.TemporaryDirectory() as tmp:
        write_file(_generated_file("routes/users.js", "a"), tmp)
        write_file(_generated_file("models/user.js", "b"), tmp)
        assert (Path(tmp) / "routes" / "users.js").exists()
        assert (Path(tmp) / "models" / "user.js").exists()


# ---------------------------------------------------------------------------
# Overwrite
# ---------------------------------------------------------------------------


def test_overwrites_existing_file():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "test.txt"
        target.write_text("old content")
        write_file(_generated_file(content="new content"), tmp)
        assert target.read_text() == "new content"


def test_overwrite_updates_bytes_written():
    with tempfile.TemporaryDirectory() as tmp:
        write_file(_generated_file(content="short"), tmp)
        result = write_file(_generated_file(content="longer content"), tmp)
        assert result["bytes_written"] == len("longer content")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_missing_path_falls_back():
    with tempfile.TemporaryDirectory() as tmp:
        result = write_file({"content": "data"}, tmp)
        assert result["path"] == "unknown"
        assert (Path(tmp) / "unknown").exists()


def test_missing_content_writes_empty():
    with tempfile.TemporaryDirectory() as tmp:
        write_file({"path": "empty.txt"}, tmp)
        assert (Path(tmp) / "empty.txt").read_text() == ""


def test_bytes_written_matches_file_size():
    with tempfile.TemporaryDirectory() as tmp:
        result = write_file(_generated_file(content="hello"), tmp)
        file_size = (Path(tmp) / "test.txt").stat().st_size
        assert result["bytes_written"] == file_size


def test_absolute_path_resolves_correctly():
    with tempfile.TemporaryDirectory() as tmp:
        result = write_file(_generated_file("sub/deep/file.ts", "code"), tmp)
        expected = str((Path(tmp) / "sub" / "deep" / "file.ts").resolve())
        assert result["absolute_path"] == expected
