"""Requirement Validator — verifies generated code implements SRS requirements.

Checks requirement coverage:
  SRS → Build Plan → Generated Files

No hardcoded endpoint constants (login, register).
No hardcoded entity names (users, products).
No framework-specific syntax checks.

Uses blueprint requirement lineage (source_requirement, source_page,
source_entity, source_flow) to trace what was supposed to be generated
and verify it exists in the output.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def _has_export(content: str, suffix: str) -> bool:
    if suffix in (".js", ".jsx", ".ts", ".tsx"):
        if re.search(r"export\s+default\s+(function|class|const|let|var|\w+)", content):
            return True
        if re.search(r"module\.exports\s*=", content):
            return True
        if re.search(r"export\s+\{", content):
            return True
        if re.search(r"export\s+(const|let|var|function|class|type|interface)\s+", content):
            return True
    if suffix == ".py":
        if re.search(r"(def\s+\w+|class\s+\w+)", content):
            return True
    return False


def _has_route_method(content: str, method: str, suffix: str) -> bool:
    if suffix in (".js", ".jsx", ".ts", ".tsx"):
        return bool(re.search(rf"""(?:router|app)\.{method}\s*\(""", content, re.IGNORECASE))
    if suffix == ".py":
        return bool(re.search(rf"""@(?:router|app)\.{method}\s*\(""", content, re.IGNORECASE))
    return False


def _has_db_connection(content: str, suffix: str) -> bool:
    if suffix in (".js", ".jsx", ".ts", ".tsx"):
        return bool(re.search(r"(connect|pool|client|mongoose|sequelize|createConnection)\s*\(", content, re.IGNORECASE))
    if suffix == ".py":
        return bool(re.search(r"(create_engine|SessionLocal|connection|engine|database)", content, re.IGNORECASE))
    return False


_STRUCTURAL_REQUIREMENTS = {
    "component export": lambda c, s, _: _has_export(c, s),
    "app rendering": lambda c, s, _: bool(re.search(r"(render|createRoot|mount|hydrate)\s*\(", c)) if s in (".js", ".jsx", ".ts", ".tsx", ".html") else False,
    "server start": lambda c, s, _: bool(re.search(r"\.listen\s*\(", c)) if s in (".js", ".jsx", ".ts", ".tsx") else bool(re.search(r"uvicorn\.run", c)) if s == ".py" else False,
    "app setup": lambda c, s, _: bool(re.search(r"(express\(|FastAPI\(|app\s*=)", c)) if s in (".js", ".jsx", ".ts", ".tsx", ".py") else False,
    "middleware setup": lambda c, s, _: bool(re.search(r"app\.use\s*\(", c)) if s in (".js", ".jsx", ".ts", ".tsx") else bool(re.search(r"add_middleware", c)) if s == ".py" else False,
    "route mounting": lambda c, s, _: bool(re.search(r"""app\.(?:use|get|post)\s*\(\s*['"]/""", c)) if s in (".js", ".jsx", ".ts", ".tsx") else bool(re.search(r"app\.include_router", c)) if s == ".py" else False,
    "database connection": lambda c, s, _: _has_db_connection(c, s),
    "model definition": lambda c, s, _: bool(re.search(r"(Schema|model|mongoose\.model|class\s+\w+|Column\s*=|Table|type\s+|interface\s+)", c, re.IGNORECASE)) if s in (".js", ".jsx", ".ts", ".tsx", ".py") else False,
    "schema definition": lambda c, s, _: bool(re.search(r"(Schema|pydantic|BaseModel)", c)) if s == ".py" else bool(re.search(r"(type\s+|interface\s+)", c)) if s in (".ts", ".tsx") else False,
    "schema creation": lambda c, s, _: bool(re.search(r"(CREATE\s+TABLE|CREATE\s+INDEX)", c, re.IGNORECASE)) if s == ".sql" else False,
    "seed data": lambda c, s, _: bool(re.search(r"(INSERT\s+INTO|insert\s*\(|seed|\.insert_one|\.insert_many|\.create\s*\()", c, re.IGNORECASE)),
    "configuration export": lambda c, s, _: bool(re.search(r"(module\.exports|export\s+|Settings|Config|BaseSettings)", c)) if s in (".js", ".jsx", ".ts", ".tsx", ".py") else False,
    "error handling": lambda c, s, _: bool(re.search(r"(errorHandler|err,\s*req|app\.use\s*\(\s*\(?\s*err|HTTPException)", c)),
    "api client": lambda c, s, _: bool(re.search(r"(axios|fetch|create\s*\()", c)) if s in (".js", ".jsx", ".ts", ".tsx") else False,
    "business logic": lambda c, s, _: bool(re.search(r"(async\s+)?def\s+\w+", c)) if s == ".py" else False,
    "route aggregation": lambda c, s, _: bool(re.search(r"require\s*\(\s*['\"]\./|from\s+['\"]\./", c)) if s in (".js", ".jsx", ".ts", ".tsx") else False,
    "route configuration": lambda c, s, _: bool(re.search(r"(routes?|Router|createBrowserRouter)", c)) if s in (".js", ".jsx", ".ts", ".tsx") else False,
    "list": lambda c, s, _: _has_route_method(c, "get", s),
    "create": lambda c, s, _: _has_route_method(c, "post", s),
    "update": lambda c, s, _: _has_route_method(c, "put", s),
    "delete": lambda c, s, _: _has_route_method(c, "delete", s),
}


def _check_requirement(content: str, requirement: str, suffix: str, bp: dict) -> Optional[str]:
    req_lower = requirement.lower().strip()
    file_ref = bp.get("path", "unknown")

    checker = _STRUCTURAL_REQUIREMENTS.get(req_lower)
    if checker is not None:
        if checker(content, suffix, bp):
            return None
        return f"'{requirement}' not found in {file_ref}"

    if re.search(rf"""\b{re.escape(req_lower)}\b""", content, re.IGNORECASE):
        return None

    return f"'{requirement}' not found in {file_ref}"


def validate_requirements(project_dir: str, build_plan: dict) -> dict:
    """Validate generated files against their blueprint requirements.

    Uses the 'requirements' list from each blueprint as the source of truth.
    No fallback to purpose-driven keyword matching.
    No hardcoded endpoint/entity constants.

    Args:
        project_dir: Root directory of the generated project.
        build_plan: Output from build_plan.generate_build_plan().

    Returns:
        Dict with keys: success (bool), errors (list[dict]).
    """
    root = Path(project_dir)
    if not root.is_dir():
        return {
            "success": False,
            "errors": [{
                "file": project_dir,
                "requirement": "project directory",
                "error": "Project directory not found",
            }],
        }

    errors: List[dict] = []
    blueprints = build_plan.get("files", [])

    for bp in blueprints:
        filepath = root / bp["path"]
        if not filepath.is_file():
            errors.append({
                "file": bp["path"],
                "requirement": "file_exists",
                "error": f"File not generated: {bp['path']}",
            })
            continue

        content = filepath.read_text(encoding="utf-8", errors="replace")
        
        # --- Check for missing routing/symbol registration ---
        path_str = bp["path"].replace("\\", "/")
        depends_on = bp.get("depends_on", [])
        
        if path_str in ("frontend/src/App.jsx", "frontend/src/App.tsx", "frontend/src/App.vue"):
            for dep_path in depends_on:
                dep_str = dep_path.replace("\\", "/")
                if "/pages/" in dep_str or "/views/" in dep_str:
                    stem = Path(dep_str).stem
                    parts = re.split(r"[-_\s]", stem)
                    comp_name = "".join(p[0].upper() + p[1:] if p else "" for p in parts)
                    if not re.search(rf"\b{comp_name}\b", content):
                        errors.append({
                            "file": bp["path"],
                            "requirement": "route_registration",
                            "error": f"Page component '{comp_name}' (from {dep_str}) is not imported or registered in App component",
                        })

        elif path_str == "backend/src/routes/index.js":
            for dep_path in depends_on:
                dep_str = dep_path.replace("\\", "/")
                if "/routes/" in dep_str and dep_str != "backend/src/routes/index.js":
                    stem = Path(dep_str).stem
                    if stem not in content:
                        errors.append({
                            "file": bp["path"],
                            "requirement": "route_mounting",
                            "error": f"Route '{stem}' (from {dep_str}) is not imported or mounted in routes aggregator",
                        })

        elif path_str == "app/main.py":
            for dep_path in depends_on:
                dep_str = dep_path.replace("\\", "/")
                if "/routers/" in dep_str:
                    stem = Path(dep_str).stem
                    if stem not in content:
                        errors.append({
                            "file": bp["path"],
                            "requirement": "router_mounting",
                            "error": f"Router '{stem}' (from {dep_str}) is not imported or registered in main app",
                        })

        requirements = bp.get("requirements", [])

        if not requirements:
            continue

        for req in requirements:
            error = _check_requirement(content, req, filepath.suffix, bp)
            if error is not None:
                errors.append({
                    "file": bp["path"],
                    "requirement": req,
                    "error": error,
                })

    return {"success": len(errors) == 0, "errors": errors}



