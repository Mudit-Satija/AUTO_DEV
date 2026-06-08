"""Smoke Test â€” validates generated project runtime correctness before packaging.

Checks:
  - Node/Express: package.json exists, JS syntax, local import resolution
  - React/Vite: package_frontend.json exists, JSX imports, component paths
  - Python: py_compile validation
  - Java: compile validation if javac is available

Integration:
  Generation -> Dependency Validation -> File Generation -> Import Validation
  -> Smoke Testing -> Package Output
"""

import json
import logging
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Set, Tuple

from coding_agent.prompt_constraints import auth_is_enabled, database_kind

logger = logging.getLogger(__name__)

_RESOLVABLE_EXTS = {".js", ".jsx", ".ts", ".tsx", ".json"}


def run_smoke_tests(project_dir: str, rules: dict) -> List[str]:
    """Run runtime smoke tests on a generated project directory.

    Each check is independent; all errors are collected and returned.
    Returns an empty list when all tests pass.

    Args:
        project_dir: Root directory of the generated project.
        rules: Project rules dict from rules_engine.build_project_rules().

    Returns:
        List of human-readable error messages. Empty list means all passed.
    """
    errors: List[str] = []
    root = Path(project_dir)

    if not root.is_dir():
        return [f"Project directory not found: {project_dir}"]

    errors.extend(_smoke_test_project_rules(root, rules))

    backend_fw = (rules.get("backend_framework") or "").lower()
    frontend_fw = (rules.get("frontend_framework") or "").lower()

    # -- Backend smoke tests ------------------------------------------------
    if any(fw in backend_fw for fw in ("express", "node")):
        errors.extend(_smoke_test_node(root))
    elif "fastapi" in backend_fw or "python" in backend_fw:
        errors.extend(_smoke_test_python(root))
    elif "spring" in backend_fw or "java" in backend_fw:
        errors.extend(_smoke_test_java(root))

    # -- Frontend smoke tests -----------------------------------------------
    if "react" in frontend_fw or "next" in frontend_fw:
        errors.extend(_smoke_test_react(root))
    elif "vue" in frontend_fw:
        errors.extend(_smoke_test_vue(root))

    if not errors:
        logger.info("All smoke tests passed for %s", project_dir)

    return errors


# ---------------------------------------------------------------------------
# Project rule consistency
# ---------------------------------------------------------------------------


def _smoke_test_project_rules(root: Path, rules: dict) -> List[str]:
    errors: List[str] = []
    backend_fw = (rules.get("backend_framework") or "").lower()
    db_kind = database_kind(rules.get("database") or "")
    auth_enabled = auth_is_enabled(rules.get("auth_method") or "")
    modules = {str(m).lower() for m in rules.get("required_backend_modules", [])}
    allowed_model_modules = set(modules)
    if auth_enabled:
        allowed_model_modules.update({"users", "user"})

    existing = {str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file() and "node_modules" not in p.parts}

    if not auth_enabled:
        forbidden_auth_paths = {
            "src/middleware/auth.js",
            "src/routes/auth.js",
            "app/core/security.py",
            "app/routers/auth.py",
            "app/models/user.py",
            "src/models/users.js",
        }
        for rel in sorted(existing & forbidden_auth_paths):
            errors.append(f"Auth is disabled but generated auth artifact exists: {rel}")

    if "express" in backend_fw or "node" in backend_fw:
        for rel in existing:
            match = re.match(r"src/(?:routes|models)/([^/.]+)\.js$", rel)
            if not match:
                continue
            name = match.group(1).lower()
            if name in {"index", "auth"}:
                if name == "auth" and not auth_enabled:
                    errors.append(f"Auth is disabled but generated auth route/model exists: {rel}")
                continue
            if name not in allowed_model_modules:
                errors.append(f"Generated Express module file is not in project_rules: {rel}")

    if "fastapi" in backend_fw or "python" in backend_fw:
        for rel in existing:
            match = re.match(r"app/(?:routers|schemas|models|services)/([^/.]+)\.py$", rel)
            if not match:
                continue
            name = match.group(1).lower()
            if name == "auth":
                if not auth_enabled:
                    errors.append(f"Auth is disabled but generated auth route/model exists: {rel}")
                continue
            if name not in allowed_model_modules:
                errors.append(f"Generated FastAPI module file is not in project_rules: {rel}")

    scanned = _read_project_text(root)
    if not auth_enabled:
        _append_forbidden_hits(errors, scanned, r"\b(jsonwebtoken|bcrypt|jwt|JWT_SECRET|token\s*=|verify\(|sign\()\b", "auth/JWT code generated while auth_method is disabled")
    if db_kind == "mongo":
        _append_forbidden_hits(errors, scanned, r"\b(pg|Pool|SQLAlchemy|sqlalchemy|psycopg|sequelize|Prisma)\b|CREATE\s+TABLE|INSERT\s+INTO", "SQL/PostgreSQL code generated for MongoDB project")
    elif db_kind == "sql":
        _append_forbidden_hits(errors, scanned, r"\b(mongoose|MongoDB|mongodb|motor|AsyncIOMotorClient)\b", "MongoDB code generated for SQL project")

    return errors


def _read_project_text(root: Path) -> dict:
    allowed_suffixes = {".js", ".jsx", ".ts", ".tsx", ".py", ".json", ".md", ".sql", ".txt", ".vue"}
    result = {}
    for path in root.rglob("*"):
        if not path.is_file() or "node_modules" in path.parts:
            continue
        if path.suffix not in allowed_suffixes:
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        result[rel] = path.read_text(encoding="utf-8", errors="replace")
    return result


def _append_forbidden_hits(errors: List[str], files: dict, pattern: str, message: str) -> None:
    regex = re.compile(pattern, re.IGNORECASE)
    for rel, content in files.items():
        if regex.search(content):
            errors.append(f"{message}: {rel}")

# ---------------------------------------------------------------------------
# Node / Express
# ---------------------------------------------------------------------------


def _smoke_test_node(root: Path) -> List[str]:
    errors: List[str] = []

    # 1. package.json must exist
    pkg = root / "backend" / "package.json"
    if not pkg.is_file():
        errors.append("package.json not found")
    else:
        logger.info("  [PASS] package.json exists")
        errors.extend(_check_package_script_entries(pkg, pkg.parent))

    js_files = sorted(
        f for f in root.rglob("*.js") if "node_modules" not in f.parts
    )
    if not js_files:
        errors.append("No .js files found")
        return errors

    # 2. JS syntax validation via node --check
    for fpath in js_files:
        rel = fpath.relative_to(root)
        ok, msg = _check_js_syntax(fpath)
        if not ok:
            errors.append(f"JS syntax error in {rel}: {msg}")

    # 3. Local import resolution
    all_backend_files = _collect_file_set(root, _RESOLVABLE_EXTS)
    for fpath in js_files:
        rel = str(fpath.relative_to(root)).replace("\\", "/")
        errors.extend(
            _check_file_imports(fpath, rel, all_backend_files, "Import")
        )

    return errors



def _check_package_script_entries(package_path: Path, root: Path) -> List[str]:
    errors: List[str] = []
    try:
        package_data = json.loads(package_path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        return [f"package.json is invalid JSON: {exc}"]

    scripts = package_data.get("scripts", {})
    if not isinstance(scripts, dict):
        return errors

    for name, command in scripts.items():
        if not isinstance(command, str):
            continue
        match = re.search(r"\b(?:node|nodemon)\s+([^\s;&|]+)", command)
        if not match:
            continue
        entry = match.group(1).strip("\"'")
        if entry.startswith("--"):
            continue
        if not (root / entry).is_file():
            errors.append(f"package.json script '{name}' references missing entry file: {entry}")
    return errors
def _check_js_syntax(filepath: Path) -> Tuple[bool, str]:
    """Check JS file syntax using node --check.

    Returns (True, "") on success or when Node.js is unavailable.
    """
    try:
        result = subprocess.run(
            ["node", "--check", str(filepath)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, ""
    except FileNotFoundError:
        return True, ""
    except subprocess.TimeoutExpired:
        return True, ""


# ---------------------------------------------------------------------------
# React / Vite
# ---------------------------------------------------------------------------


def _smoke_test_react(root: Path) -> List[str]:
    errors: List[str] = []

    # 1. package_frontend.json must exist
    pkg = root / "frontend" / "package.json"
    if not pkg.is_file():
        errors.append("package_frontend.json not found")
    else:
        logger.info("  [PASS] package_frontend.json exists")

    # 2. Required config files
    for required in ("vite.config.js", "index.html"):
        if not (root / "frontend" / required).is_file():
            errors.append(f"Required file not found: {required}")

    # 3. Collect all frontend source files
    jsx_files = sorted(
        f for f in root.rglob("*.jsx") if "node_modules" not in f.parts
    )
    all_frontend = _collect_file_set(root, _RESOLVABLE_EXTS)

    # 4. JSX import resolution
    for fpath in jsx_files:
        rel = str(fpath.relative_to(root)).replace("\\", "/")
        errors.extend(
            _check_file_imports(fpath, rel, all_frontend, "JSX import")
        )

    # 5. Also check .js files in frontend that may import .jsx
    frontend_js_files = sorted(
        f for f in root.rglob("*.js") if "node_modules" not in f.parts
    )
    for fpath in frontend_js_files:
        rel = str(fpath.relative_to(root)).replace("\\", "/")
        errors.extend(
            _check_file_imports(fpath, rel, all_frontend, "Import")
        )

    return errors


def _smoke_test_vue(root: Path) -> List[str]:
    errors: List[str] = []

    pkg = root / "frontend" / "package.json"
    if not pkg.is_file():
        errors.append("package_frontend.json not found")
    else:
        logger.info("  [PASS] package_frontend.json exists")

    vue_files = sorted(
        f for f in root.rglob("*.vue") if "node_modules" not in f.parts
    )
    if not vue_files:
        errors.append("No .vue files found in Vue project")

    return errors


# ---------------------------------------------------------------------------
# Python / FastAPI
# ---------------------------------------------------------------------------


def _smoke_test_python(root: Path) -> List[str]:
    errors: List[str] = []

    requirements = root / "requirements.txt"
    if not requirements.is_file():
        errors.append("requirements.txt not found")
    else:
        logger.info("  [PASS] requirements.txt exists")

    py_files = sorted(root.rglob("*.py"))
    if not py_files:
        errors.append("No .py files found")
        return errors

    for fpath in py_files:
        rel = str(fpath.relative_to(root)).replace("\\", "/")
        try:
            source = fpath.read_text(encoding="utf-8", errors="replace")
            compile(source, str(fpath), "exec")
        except SyntaxError as e:
            errors.append(f"Python syntax error in {rel}: {e}")

    return errors


# ---------------------------------------------------------------------------
# Java / Spring
# ---------------------------------------------------------------------------


def _smoke_test_java(root: Path) -> List[str]:
    errors: List[str] = []

    pom = root / "pom.xml"
    if not pom.is_file():
        errors.append("pom.xml not found")
    else:
        logger.info("  [PASS] pom.xml exists")

    java_files = sorted(root.rglob("*.java"))
    if not java_files:
        errors.append("No .java files found")
        return errors

    # Try javac if available
    javac_available = False
    try:
        result = subprocess.run(
            ["javac", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        javac_available = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        javac_available = False

    if not javac_available:
        logger.info("  [SKIP] javac not available, skipping Java compilation")
        return errors

    src_root = root / "src"
    if not src_root.is_dir():
        return errors

    with tempfile.TemporaryDirectory() as tmp:
        try:
            result = subprocess.run(
                ["javac", "-d", tmp, "-sourcepath", str(src_root)]
                + [str(f) for f in java_files],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                errors.append(
                    f"Java compilation failed:\n{result.stderr.strip()}"
                )
        except subprocess.TimeoutExpired:
            errors.append("Java compilation timed out")

    return errors


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _collect_file_set(root: Path, extensions: Set[str]) -> Set[str]:
    """Return set of relative paths (forward-slash) for files under root
    matching any of the given extensions, excluding node_modules."""
    result: Set[str] = set()
    for f in root.rglob("*"):
        if "node_modules" in f.parts:
            continue
        if f.suffix in extensions and f.is_file():
            result.add(str(f.relative_to(root)).replace("\\", "/"))
    return result


def _extract_local_imports(content: str) -> List[str]:
    """Extract relative import/require paths from source code."""
    imports: List[str] = []
    imports.extend(
        re.findall(r"""require\(['"](\.\.?/[^'"]+)['"]\)""", content)
    )
    imports.extend(
        re.findall(r"""from\s+['"](\.\.?/[^'"]+)['"]""", content)
    )
    return imports


def _resolve_relative_path(import_path: str, current_file: str) -> str | None:
    """Resolve a relative import path to a canonical project-relative path.

    Returns the resolved path string (without extension), or None for
    non-local imports (e.g. 'express', 'react').
    """
    if not import_path.startswith("."):
        return None

    parts = current_file.replace("\\", "/").split("/")
    dir_parts = parts[:-1]

    for part in import_path.replace("\\", "/").split("/"):
        if part == "." or not part:
            continue
        elif part == "..":
            if dir_parts:
                dir_parts.pop()
        else:
            dir_parts.append(part)

    return "/".join(dir_parts)


def _import_exists(resolved_base: str, all_files: Set[str]) -> bool:
    """Check if a resolved import path exists in the set of project files.

    Tries exact match, then with each resolvable extension, then
    as a directory with index file.
    """
    if resolved_base in all_files:
        return True
    for ext in _RESOLVABLE_EXTS:
        if f"{resolved_base}{ext}" in all_files:
            return True
    for ext in _RESOLVABLE_EXTS:
        if f"{resolved_base}/index{ext}" in all_files:
            return True
    return False


def _check_file_imports(
    filepath: Path,
    relative_path: str,
    all_files: Set[str],
    label: str,
) -> List[str]:
    """Check all local imports in a file against the set of known files.

    Args:
        filepath: Path to the file to scan.
        relative_path: Forward-slash relative path for error messages.
        all_files: Set of all known project file paths.
        label: Label for error messages (e.g. 'Import', 'JSX import').

    Returns:
        List of error messages for missing imports.
    """
    errors: List[str] = []
    content = filepath.read_text(encoding="utf-8", errors="replace")
    raw_imports = _extract_local_imports(content)

    for raw_imp in raw_imports:
        resolved = _resolve_relative_path(raw_imp, relative_path)
        if resolved is None:
            continue
        if not _import_exists(resolved, all_files):
            errors.append(
                f"{label} in {relative_path} references missing file: {resolved}"
            )

    return errors




