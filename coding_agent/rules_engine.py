"""Rules Engine â€” converts architecture plan into structured project rules."""

from typing import Any, Dict, List


def build_project_rules(architecture_plan: dict) -> dict:
    """Convert merged architecture plan into a project_rules.json structure.

    Args:
        architecture_plan: Output from master_merger.merge_backend_and_frontend()

    Returns:
        Dict with keys: backend_framework, frontend_framework, database,
        auth_method, deployment, required_pages, required_backend_modules
    """
    backend = architecture_plan.get("backend_architecture", {})
    frontend = architecture_plan.get("frontend_architecture", {})
    validation = architecture_plan.get("validation", {})
    explicit = architecture_plan.get("project_rules", {})
    if not isinstance(explicit, dict):
        explicit = {}

    backend_framework = explicit.get("backend_framework") or _resolve_backend_framework(backend)
    frontend_framework = explicit.get("frontend_framework") or _resolve_frontend_framework(frontend)
    database = explicit.get("database") or _resolve_database(backend)
    auth_method = explicit.get("auth_method") or _resolve_auth_method(backend)
    deployment = explicit.get("deployment") or _resolve_deployment(validation)
    required_pages = _first_explicit_list(explicit, validation, key="required_pages")
    if required_pages is None:
        required_pages = _extract_required_pages(frontend)
    required_backend_modules = _first_explicit_list(explicit, validation, key="required_backend_modules")
    if required_backend_modules is None:
        required_backend_modules = _extract_required_backend_modules(backend)

    return {
        "backend_framework": backend_framework,
        "frontend_framework": frontend_framework,
        "database": database,
        "auth_method": auth_method,
        "deployment": deployment,
        "required_pages": required_pages,
        "required_backend_modules": required_backend_modules,
    }

def _normalise_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    result: List[str] = []
    seen: set = set()
    for item in value:
        clean = str(item).strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def _first_explicit_list(*sources: dict, key: str) -> List[str] | None:
    for source in sources:
        if not isinstance(source, dict):
            continue
        if key in source:
            return _normalise_list(source.get(key))
        nested = source.get("project_rules")
        if isinstance(nested, dict) and key in nested:
            return _normalise_list(nested.get(key))
    return None

def _resolve_backend_framework(backend: dict) -> str:
    raw = backend.get("framework", "")
    if not raw:
        return "Unknown"
    return raw.split(" ")[0] if " " in raw else raw


def _resolve_frontend_framework(frontend: dict) -> str:
    return frontend.get("framework", "Unknown")


def _resolve_database(backend: dict) -> str:
    db = backend.get("database", {})
    if isinstance(db, dict):
        return db.get("type", "Unknown")
    return str(db)


def _resolve_auth_method(backend: dict) -> str:
    auth = backend.get("authentication", {})
    if isinstance(auth, dict):
        return auth.get("method", "Unknown")
    return str(auth)


def _resolve_deployment(validation: dict) -> str:
    user_stack = validation.get("user_stack", {})
    if isinstance(user_stack, dict):
        dep = user_stack.get("deployment")
        if dep:
            return str(dep)

    recommended = validation.get("recommended_stack", {})
    if isinstance(recommended, dict):
        devops = recommended.get("devops", [])
        if isinstance(devops, list) and devops:
            return devops[0]
        if isinstance(devops, str):
            return devops

    return "Not specified"


def _extract_required_pages(frontend: dict) -> List[str]:
    pages: set = set()

    routing = frontend.get("routing", {})
    if isinstance(routing, dict):
        for name in routing.values():
            if isinstance(name, str) and name:
                pages.add(name)

    navigation = frontend.get("navigation", [])
    if isinstance(navigation, list):
        for item in navigation:
            if isinstance(item, dict):
                label = item.get("label", "")
                if label:
                    pages.add(label)

    return sorted(pages)


def _extract_required_backend_modules(backend: dict) -> List[str]:
    modules: set = set()
    skip_parts = {"src", "core", "tests", "config", "domains", "api", "auth"}

    endpoints = backend.get("suggested_endpoints", [])
    if isinstance(endpoints, list):
        for ep in endpoints:
            if isinstance(ep, dict):
                path = ep.get("path", "")
                parts = [part.strip().lower() for part in path.strip("/").split("/") if part.strip()]
                if len(parts) >= 2 and parts[0] == "api":
                    candidate = parts[1]
                    if candidate not in skip_parts:
                        modules.add(candidate)

    return sorted(modules)

