"""Rules Engine — converts SRS + tech stack into structured project rules.

No longer extracts from architecture plan. Uses SRS as direct input.
"""

from typing import Any, Dict, List


def build_project_rules(srs: dict, tech_stack: dict = None) -> dict:
    """Convert SRS + tech stack into project_rules for the build plan.

    Args:
        srs: SRS dict from schemas.SRSDocument format.
        tech_stack: Optional tech stack dict with backend/frontend/database keys.
                    Falls back to srs.tech_stack if not provided.

    Returns:
        Dict with keys: backend_framework, frontend_framework, database,
        srs (original SRS), required_backend_modules (from entities),
        required_pages (from pages).
    """
    if tech_stack is None:
        tech_stack = srs.get("tech_stack", {})
    if not isinstance(tech_stack, dict):
        tech_stack = {}

    backend = tech_stack.get("backend", "")
    frontend = tech_stack.get("frontend", "")
    database = tech_stack.get("database", "")

    entities = srs.get("entities", []) or []
    pages = srs.get("pages", []) or []

    # required_backend_modules derived from entities
    modules = []
    for e in entities:
        name = e.get("name", "")
        if name:
            modules.append(name.lower().replace(" ", "-"))

    # required_pages derived from pages
    page_names = []
    for p in pages:
        name = p.get("name", "")
        if name:
            page_names.append(name)

    return {
        "backend_framework": backend,
        "frontend_framework": frontend,
        "database": database,
        "auth_method": "",
        "deployment": tech_stack.get("deployment", "Not specified"),
        "required_pages": page_names,
        "required_backend_modules": modules,
        "srs": srs,
    }
