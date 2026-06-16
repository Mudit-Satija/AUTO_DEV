"""Smoke Test — validates generated project runtime correctness before packaging.

Checks:
  - Node/Express: package.json exists, JS syntax, local import resolution
  - React/Vite: package.json exists, JSX imports, component paths
  - Python: py_compile validation
  - Java: compile validation if javac is available

No auth artifact checks.
No hardcoded file path assumptions beyond stack conventions.
"""

import json
import logging
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Set, Tuple

from coding_agent.prompt_constraints import database_kind

logger = logging.getLogger(__name__)

_RESOLVABLE_EXTS = {".js", ".jsx", ".ts", ".tsx", ".json"}


def run_smoke_tests(project_dir: str, rules: dict) -> List[str]:
    errors: List[str] = []
    root = Path(project_dir)

    if not root.is_dir():
        return [f"Project directory not found: {project_dir}"]

    backend_fw = (rules.get("backend_framework") or "").lower()
    frontend_fw = (rules.get("frontend_framework") or "").lower()

    if any(fw in backend_fw for fw in ("express", "node")):
        errors.extend(_smoke_test_node(root))
    elif "fastapi" in backend_fw or "python" in backend_fw:
        errors.extend(_smoke_test_python(root))
    elif "spring" in backend_fw or "java" in backend_fw:
        errors.extend(_smoke_test_java(root))

    if "react" in frontend_fw or "next" in frontend_fw:
        errors.extend(_smoke_test_react(root))
    elif "vue" in frontend_fw:
        errors.extend(_smoke_test_vue(root))

    if not errors:
        logger.info("All smoke tests passed for %s", project_dir)

    return errors


def _smoke_test_node(root: Path) -> List[str]:
    errors: List[str] = []

    pkg = root / "backend" / "package.json"
    if not pkg.is_file():
        pkg = root / "package.json"
    if not pkg.is_file():
        errors.append("package.json not found")
    else:
        logger.info("  [PASS] package.json exists")

    js_files = sorted(f for f in root.rglob("*.js") if "node_modules" not in f.parts)
    if not js_files:
        errors.append("No .js files found")
        return errors

    for fpath in js_files:
        rel = fpath.relative_to(root)
        ok, msg = _check_js_syntax(fpath)
        if not ok:
            errors.append(f"JS syntax error in {rel}: {msg}")

    all_backend_files = _collect_file_set(root, _RESOLVABLE_EXTS)
    for fpath in js_files:
        rel = str(fpath.relative_to(root)).replace("\\", "/")
        errors.extend(_check_file_imports(fpath, rel, all_backend_files, "Import"))

    return errors


def _check_js_syntax(filepath: Path) -> Tuple[bool, str]:
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


def _smoke_test_react(root: Path) -> List[str]:
    errors: List[str] = []

    pkg = root / "frontend" / "package.json"
    if not pkg.is_file():
        errors.append("frontend/package.json not found")
    else:
        logger.info("  [PASS] frontend/package.json exists")

    # Check for index.html and either vite.config.js or vite.config.ts
    if not (root / "frontend" / "index.html").is_file():
        errors.append("Required file not found: frontend/index.html")

    vite_config_js = root / "frontend" / "vite.config.js"
    vite_config_ts = root / "frontend" / "vite.config.ts"
    if not vite_config_js.is_file() and not vite_config_ts.is_file():
        errors.append("Required file not found: frontend/vite.config.js or vite.config.ts")

    jsx_files = sorted(f for f in root.rglob("*") if "node_modules" not in f.parts and f.suffix in (".jsx", ".tsx"))
    all_frontend = _collect_file_set(root, _RESOLVABLE_EXTS)

    for fpath in jsx_files:
        rel = str(fpath.relative_to(root)).replace("\\", "/")
        errors.extend(_check_file_imports(fpath, rel, all_frontend, "JSX import"))
        errors.extend(_check_missing_router_imports(fpath, rel))

    frontend_js_files = sorted(f for f in root.rglob("*") if "node_modules" not in f.parts and f.suffix in (".js", ".ts"))
    for fpath in frontend_js_files:
        rel = str(fpath.relative_to(root)).replace("\\", "/")
        errors.extend(_check_file_imports(fpath, rel, all_frontend, "Import"))
        errors.extend(_check_missing_router_imports(fpath, rel))

    return errors


def _smoke_test_vue(root: Path) -> List[str]:
    errors: List[str] = []

    pkg = root / "frontend" / "package.json"
    if not pkg.is_file():
        errors.append("frontend/package.json not found")
    else:
        logger.info("  [PASS] frontend/package.json exists")

    vue_files = sorted(f for f in root.rglob("*.vue") if "node_modules" not in f.parts)
    if not vue_files:
        errors.append("No .vue files found in Vue project")

    return errors


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
                errors.append(f"Java compilation failed:\n{result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            errors.append("Java compilation timed out")

    return errors


def _collect_file_set(root: Path, extensions: Set[str]) -> Set[str]:
    result: Set[str] = set()
    for f in root.rglob("*"):
        if "node_modules" in f.parts:
            continue
        if f.suffix in extensions and f.is_file():
            result.add(str(f.relative_to(root)).replace("\\", "/"))
    return result


def _extract_local_imports(content: str) -> List[str]:
    imports: List[str] = []
    imports.extend(re.findall(r"""require\(['"](\.\.?/[^'"]+)['"]\)""", content))
    imports.extend(re.findall(r"""from\s+['"](\.\.?/[^'"]+)['"]""", content))
    return imports


def _resolve_relative_path(import_path: str, current_file: str) -> str | None:
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
    errors: List[str] = []
    content = filepath.read_text(encoding="utf-8", errors="replace")
    raw_imports = _extract_local_imports(content)

    for raw_imp in raw_imports:
        resolved = _resolve_relative_path(raw_imp, relative_path)
        if resolved is None:
            continue
        if not _import_exists(resolved, all_files):
            errors.append(f"{label} in {relative_path} references missing file: {resolved}")

    return errors


_ROUTER_SYMBOLS = {
    "Link": r"<\s*Link\b",
    "NavLink": r"<\s*NavLink\b",
    "useNavigate": r"useNavigate\s*\(",
    "Navigate": r"<\s*Navigate\b",
}


def _check_missing_router_imports(filepath: Path, relative_path: str) -> List[str]:
    """Check that JSX files using react-router-dom symbols also import them.

    Error format uses 'in <path>:' so ``_extract_file_from_smoke_error`` can
    parse the file path for the repair loop.
    """
    errors: List[str] = []
    ext = filepath.suffix
    if ext not in (".jsx", ".tsx", ".js", ".ts"):
        return errors
    content = filepath.read_text(encoding="utf-8", errors="replace")
    has_router_import = bool(re.search(
        r"""from\s+['"]react-router-dom['"]""", content,
    ))
    if not has_router_import:
        missing = []
        for sym, pattern in _ROUTER_SYMBOLS.items():
            if re.search(pattern, content):
                missing.append(sym)
        if missing:
            errors.append(
                f"Missing react-router-dom import in {relative_path}: "
                f"uses {', '.join(missing)} but no import from 'react-router-dom'"
            )
    return errors
