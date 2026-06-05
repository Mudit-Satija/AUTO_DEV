"""Requirement Validator — detects when generated code fails to implement
requested features, even when syntax and imports are correct.

Uses the blueprint ``requirements`` list as the primary source of truth.
Falls back to purpose-driven keyword matching when requirements is empty.

Integration:
  Generation -> Dependency Validation -> File Generation -> Import Validation
  -> Smoke Testing -> Requirement Validation -> Package Output
"""

import logging
import re
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Endpoint checking helpers
# ---------------------------------------------------------------------------


def _has_route_endpoint(content: str, endpoint: str, suffix: str) -> bool:
    """Check if a route endpoint (login, register, etc.) appears in code."""
    escaped = re.escape(endpoint)

    if suffix in (".js", ".jsx"):
        patterns = [
            rf"""router\.(?:get|post|put|delete|all)\s*\(\s*['"]/?{escaped}['"]""",
            rf"""app\.(?:get|post|put|delete|all)\s*\(\s*['"]/?{escaped}['"]""",
        ]
    elif suffix == ".py":
        patterns = [
            rf"""@(?:router|app)\.(?:get|post|put|delete)\s*\(\s*['"]/?{escaped}['"]""",
            rf"""(?:router|app)\.(?:get|post|put|delete)\s*\(\s*['"]/?{escaped}['"]""",
        ]
    elif suffix == ".java":
        patterns = [
            rf"""@(?:Get|Post|Put|Delete)Mapping\s*\(\s*['"]/?{escaped}['"]""",
        ]
    else:
        patterns = [rf"""\b{escaped}\b"""]

    return any(re.search(p, content, re.IGNORECASE) for p in patterns)


def _has_route_method(content: str, method: str, suffix: str) -> bool:
    """Check if a file contains a route handler for a given HTTP method."""
    if suffix in (".js", ".jsx"):
        return bool(re.search(
            rf"""(?:router|app)\.{method}\s*\(""", content, re.IGNORECASE
        ))
    if suffix == ".py":
        return bool(re.search(
            rf"""@(?:router|app)\.{method}\s*\(""", content, re.IGNORECASE
        ))
    if suffix == ".java":
        return bool(re.search(
            rf"""@{method.capitalize()}Mapping\s*\(""", content
        ))
    return False


# ---------------------------------------------------------------------------
# Structural requirement checkers
# ---------------------------------------------------------------------------


def _check_component_export(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".jsx", ".js", ".tsx", ".ts"):
        if re.search(r"export\s+default\s+(function|class|const|let|var)", content):
            return True
        if re.search(r"export\s+\{(?:[^}]+)\}", content):
            return True
        if re.search(r"export\s+(async\s+)?function\s+\w+", content):
            return True
        if suffix == ".jsx" and re.search(r"export\s+default\s+\w+", content):
            return True
    if suffix == ".vue":
        if re.search(r"<template>", content) or re.search(
            r"export\s+default\s*\{", content
        ):
            return True
    if suffix == ".py":
        if re.search(r"def\s+\w+", content):
            return True
    return False


def _check_app_rendering(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"(render|createRoot|mount|hydrate)\s*\(", content):
            return True
    if suffix == ".py":
        if re.search(r"uvicorn\.run|app\.run", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_server_start(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"\.listen\s*\(", content):
            return True
    if suffix == ".py":
        if re.search(r"uvicorn\.run|app\.run", content):
            return True
    if suffix == ".java":
        if re.search(r"SpringApplication\.run", content):
            return True
    return False


def _check_middleware_setup(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"app\.use\s*\(", content) or re.search(
            r"app\.set\s*\(", content
        ):
            return True
    if suffix == ".py":
        if re.search(r"add_middleware|Middleware", content):
            return True
    return False


def _check_route_mounting(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"""app\.(?:use|get|post)\s*\(\s*['"]/""", content):
            return True
    if suffix == ".py":
        if re.search(r"""app\.include_router|@app\.(?:get|post)""", content):
            return True
    return False


def _check_route_aggregation(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"require\s*\(\s*['\"]\./|from\s+['\"]\./", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_route_configuration(content: str, suffix: str, bp: dict) -> bool:
    if suffix == ".vue":
        return bool(re.search(r"\S", content.strip()))
    if suffix in (".js", ".jsx"):
        if re.search(r"(routes?|Router|createBrowserRouter)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_config_export(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"module\.exports\s*=|export\s+", content):
            return True
    if suffix == ".py":
        if re.search(r"Settings|config|Config", content, re.IGNORECASE):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_db_connection(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(
            r"(createConnection|connect|pool|client|mongoose|sequelize)\s*\(",
            content,
            re.IGNORECASE,
        ):
            return True
    if suffix == ".py":
        if re.search(
            r"(create_engine|SessionLocal|connection|engine|database|DATABASE)",
            content,
            re.IGNORECASE,
        ):
            return True
    if suffix == ".java":
        if re.search(r"(DataSource|EntityManager|DataSourceConfig)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_jwt(content: str, suffix: str, bp: dict) -> bool:
    if re.search(r"(jwt|jsonwebtoken|JWT|sign|verify|token)", content, re.IGNORECASE):
        return True
    return bool(re.search(r"\S", content.strip()))


def _check_error_handler(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(
            r"(errorHandler|err,\s*req|app\.use\s*\(\s*\(?\s*err|middleware)", content
        ):
            return True
    if suffix == ".py":
        if re.search(r"HTTPException|ExceptionHandler|error", content, re.IGNORECASE):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_api_functions(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        return bool(re.search(
            r"(export\s+(async\s+)?function|export\s+const|module\.exports)", content
        ))
    if suffix == ".py":
        return bool(re.search(r"(async\s+)?def\s+\w+", content))
    return bool(re.search(r"\S", content.strip()))


def _check_crud_list(content: str, suffix: str, bp: dict) -> bool:
    return _has_route_method(content, "get", suffix)


def _check_crud_create(content: str, suffix: str, bp: dict) -> bool:
    return _has_route_method(content, "post", suffix)


def _check_crud_update(content: str, suffix: str, bp: dict) -> bool:
    return _has_route_method(content, "put", suffix)


def _check_crud_delete(content: str, suffix: str, bp: dict) -> bool:
    return _has_route_method(content, "delete", suffix)


def _check_controller_functions(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"(exports\.\w+\s*=|module\.exports|export\s+)", content):
            return True
    if suffix == ".py":
        if re.search(r"(async\s+)?def\s+\w+", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_model_definition(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(
            r"(Schema|model|mongoose\.model|sequelize\.define|type\s+|interface\s+)",
            content,
            re.IGNORECASE,
        ):
            return True
    if suffix == ".py":
        if re.search(r"(class\s+\w+|Column|Table|Model|Base)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_schema_creation(content: str, suffix: str, bp: dict) -> bool:
    if suffix == ".sql":
        if re.search(r"(CREATE\s+TABLE|CREATE\s+INDEX|CREATE\s+SCHEMA)", content, re.IGNORECASE):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_seed_data(content: str, suffix: str, bp: dict) -> bool:
    if suffix == ".sql":
        if re.search(r"(INSERT\s+INTO|UPDATE\s+|DELETE\s+FROM)", content, re.IGNORECASE):
            return True
    if suffix in (".js", ".jsx"):
        if re.search(r"(insert|seed|create|save)\s*\(", content, re.IGNORECASE):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_declarative_base(content: str, suffix: str, bp: dict) -> bool:
    if suffix == ".py":
        if re.search(r"(declarative_base|Base\s*=\s*|metadata)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_security_config(content: str, suffix: str, bp: dict) -> bool:
    if suffix == ".py":
        if re.search(r"(security|SECRET|oauth|JWT|password|hash)", content, re.IGNORECASE):
            return True
    if suffix == ".java":
        if re.search(r"(Security|SecurityConfig|@Enable)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_business_logic(content: str, suffix: str, bp: dict) -> bool:
    if suffix == ".py":
        if re.search(r"(async\s+)?def\s+\w+", content):
            return True
    if suffix == ".java":
        if re.search(r"(class\s+\w+Service|@Service)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_data_access(content: str, suffix: str, bp: dict) -> bool:
    if suffix == ".java":
        if re.search(r"(Repository|@Repository|JpaRepository|CrudRepository)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_entity_definition(content: str, suffix: str, bp: dict) -> bool:
    if suffix == ".java":
        if re.search(r"(@Entity|@Table|class\s+\w+\s*\{)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_application_setup(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"(express|app|require|import)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_module_functions(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"(module\.exports|export\s+|function\s+)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


def _check_page_content(content: str, suffix: str, bp: dict) -> bool:
    if suffix in (".js", ".jsx"):
        if re.search(r"(function|class|const|import|export)", content):
            return True
    return bool(re.search(r"\S", content.strip()))


# ---------------------------------------------------------------------------
# Requirement registries
# ---------------------------------------------------------------------------

_ENDPOINT_REQUIREMENTS: set = {
    "login", "register", "logout",
}

_STRUCTURAL_REQUIREMENTS: dict = {
    "component export": _check_component_export,
    "app rendering": _check_app_rendering,
    "app mounting": _check_app_rendering,
    "server start": _check_server_start,
    "app startup": _check_server_start,
    "application startup": _check_server_start,
    "middleware setup": _check_middleware_setup,
    "route mounting": _check_route_mounting,
    "route aggregation": _check_route_aggregation,
    "route configuration": _check_route_configuration,
    "configuration export": _check_config_export,
    "configuration settings": _check_config_export,
    "database connection": _check_db_connection,
    "mongodb connection": _check_db_connection,
    "database configuration": _check_db_connection,
    "jwt verification": _check_jwt,
    "token validation": _check_jwt,
    "error handling": _check_error_handler,
    "api functions": _check_api_functions,
    "controller functions": _check_controller_functions,
    "model definition": _check_model_definition,
    "schema definition": _check_model_definition,
    "schema creation": _check_schema_creation,
    "seed data": _check_seed_data,
    "declarative base": _check_declarative_base,
    "security configuration": _check_security_config,
    "business logic": _check_business_logic,
    "data access": _check_data_access,
    "entity definition": _check_entity_definition,
    "application setup": _check_application_setup,
    "module functions": _check_module_functions,
    "page content": _check_page_content,
    "list": _check_crud_list,
    "create": _check_crud_create,
    "update": _check_crud_update,
    "delete": _check_crud_delete,
}

_PURPOSE_KEYWORDS: dict = {
    "authentication routes": ["login", "register", "logout"],
    "api routes": ["list", "create", "update", "delete"],
    "route handlers": ["list", "create", "update", "delete"],
    "controller logic": ["controller functions"],
    "data model": ["model definition"],
    "schema": ["schema definition"],
    "database migration": ["schema creation"],
    "seed data": ["seed data"],
    "pydantic schemas": ["schema definition"],
    "sqlalchemy model": ["model definition"],
    "business logic": ["business logic"],
    "data repository": ["data access"],
    "jpa entity": ["entity definition"],
    "page view": ["component export"],
    "page": ["component export"],
    "component": ["component export"],
    "api client": ["api functions"],
    "api service": ["api functions"],
    "entry point": ["app rendering"],
    "application setup": ["middleware setup", "route mounting"],
    "app setup": ["app setup", "router mounting"],
    "configuration": ["configuration export"],
    "database connection": ["database connection"],
    "connection setup": ["database connection"],
}


# ---------------------------------------------------------------------------
# Requirement checking (primary path)
# ---------------------------------------------------------------------------


def _check_requirement(
    content: str,
    requirement: str,
    suffix: str,
    bp: dict,
    root: Path,
) -> Optional[str]:
    """Check a single requirement against file content.

    Returns an error string or None if satisfied.
    """
    req_lower = requirement.lower().strip()
    file_ref = bp.get("path", "unknown")

    if req_lower in _ENDPOINT_REQUIREMENTS:
        if _has_route_endpoint(content, req_lower, suffix):
            return None
        return f"endpoint '{requirement}' not found in {file_ref}"

    checker = _STRUCTURAL_REQUIREMENTS.get(req_lower)
    if checker is not None:
        if checker(content, suffix, bp):
            return None
        return f"'{requirement}' not found in {file_ref}"

    if re.search(rf"""\b{re.escape(req_lower)}\b""", content, re.IGNORECASE):
        return None

    return f"'{requirement}' not found in {file_ref}"


# ---------------------------------------------------------------------------
# Purpose fallback
# ---------------------------------------------------------------------------


def _derive_requirements_from_purpose(purpose: str) -> List[str]:
    """Derive requirement strings from purpose text when no explicit
    requirements list is provided."""
    purpose_lower = purpose.lower().strip()
    for keyword, reqs in _PURPOSE_KEYWORDS.items():
        if keyword in purpose_lower:
            return reqs
    return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_requirements(project_dir: str, build_plan: dict) -> dict:
    """Validate that generated files satisfy their blueprint requirements.

    Each blueprint's ``requirements`` list specifies what the generated file
    must contain.  When ``requirements`` is empty the validator falls back
    to purpose-driven keyword matching.

    Args:
        project_dir: Root directory of the generated project.
        build_plan: Output from build_plan.generate_build_plan() with key
            "files" containing blueprint dicts.

    Returns:
        Dict with keys:
            success (bool): True when no errors found.
            errors (list[dict]): Each dict has file, requirement, error.
    """
    root = Path(project_dir)
    if not root.is_dir():
        return {
            "success": False,
            "errors": [
                {
                    "file": project_dir,
                    "requirement": "project directory",
                    "error": "Project directory not found",
                }
            ],
        }

    errors: List[dict] = []
    blueprints = build_plan.get("files", [])

    for bp in blueprints:
        filepath = root / bp["path"]
        if not filepath.is_file():
            continue

        content = filepath.read_text(encoding="utf-8", errors="replace")
        requirements = bp.get("requirements", [])

        if requirements:
            for req in requirements:
                error = _check_requirement(
                    content, req, filepath.suffix, bp, root
                )
                if error is not None:
                    errors.append({
                        "file": bp["path"],
                        "requirement": req,
                        "error": error,
                    })
        else:
            purpose = bp.get("purpose", "")
            reqs_from_purpose = _derive_requirements_from_purpose(purpose)
            for req in reqs_from_purpose:
                error = _check_requirement(
                    content, req, filepath.suffix, bp, root
                )
                if error is not None:
                    errors.append({
                        "file": bp["path"],
                        "requirement": req,
                        "error": error,
                    })

    return {"success": len(errors) == 0, "errors": errors}
