"""Layout agent for frontend architecture design.

RULE 1: Context-aware framework selection
RULE 3: Responsive design (mobile-first)
RULE 9: Accessibility in layout

Analyzes project requirements and designs page structure,
responsive breakpoints, and accessibility features.
"""

import json
import logging
import asyncio
from llm_client import get_llm_response, PLANNER_MODEL
from planning_agents.shared.domain_intelligence import domain_context_summary, frontend_hints
from planning_agents.shared.json_utils import extract_json

logger = logging.getLogger(__name__)

MAX_OUTPUT_CHARS = 600

LAYOUT_AGENT_PROMPT = """You are a frontend IA planner.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}
- Realtime: {realtime}

Return ONLY compact JSON data (no prose) with keys:
layout_type, structure, breakpoints, grid_system, accessibility,
routing_structure, navigation_menu, mobile_menu, breadcrumbs, search, total_routes.

Constraints:
- max 3 structure items
- max 5 routes
- max 4 navigation_menu items
- max 3 accessibility items
- output must be <= 600 characters
- no tutorials, no implementation steps, no reasoning text."""


async def layout_agent(shared_state: dict) -> dict:
    """Design responsive page layout and structure.
    
    Args:
        shared_state: ProjectState containing project_type, complexity, user_stack
        
    Returns:
        Dict with layout_type, structure, breakpoints, grid_system, accessibility
    """
    try:
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "intermediate")
        frontend_fw = shared_state.get("user_stack", {}).get("frontend", "React")
        realtime = shared_state.get("user_stack", {}).get("realtime", "No")
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        prompt = LAYOUT_AGENT_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            frontend_framework=frontend_fw,
            realtime=realtime
        )
        prompt = prompt + "\n\nDOMAIN CONTEXT:\n" + domain_context_summary(domain_context)
        
        response = await asyncio.to_thread(get_llm_response, prompt, PLANNER_MODEL)
        
        # Extract JSON from response
        if isinstance(response, str):
            try:
                result = extract_json(response)
            except (ValueError, json.JSONDecodeError):
                logger.warning("Layout agent: No JSON in response, using defaults")
                result = _default_layout(complexity)
        else:
            logger.warning(f"Layout agent: Unexpected response type {type(response)}")
            result = _default_layout(complexity)

        result = _sanitize_layout(result, complexity)
        result = _apply_domain_context(result, domain_context)
        result = _enforce_size_limit(result, _default_layout(complexity), MAX_OUTPUT_CHARS)
            
        logger.info(f"✅ Layout Agent: {result.get('layout_type', 'N/A')}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Layout agent JSON error: {e}")
        return _enforce_size_limit(_default_layout(complexity), _default_layout(complexity), MAX_OUTPUT_CHARS)
    except Exception as e:
        logger.error(f"Layout agent error: {e}")
        return _enforce_size_limit(_default_layout(complexity), _default_layout(complexity), MAX_OUTPUT_CHARS)


def _default_layout(complexity: str) -> dict:
    """Return sensible layout defaults based on complexity."""
    if complexity == "beginner":
        return {
            "layout_type": "single-page",
            "structure": [
                {"name": "Header", "description": "Top nav", "responsive": True},
                {"name": "Main", "description": "Primary content", "responsive": True},
                {"name": "Footer", "description": "Utility links", "responsive": True}
            ],
            "breakpoints": {"mobile": "320px", "tablet": "768px", "desktop": "1024px"},
            "grid_system": "12-column",
            "accessibility": ["semantic HTML", "ARIA labels", "keyboard nav"],
            "routing_structure": {
                "/": "Home",
                "/auth/login": "Login",
                "/dashboard": "Dashboard",
                "/profile": "Profile"
            },
            "navigation_menu": [
                {"label": "Home", "path": "/", "icon": "home"},
                {"label": "Dashboard", "path": "/dashboard", "icon": "dashboard", "auth": True},
                {"label": "Profile", "path": "/profile", "icon": "user", "auth": True}
            ],
            "mobile_menu": "hamburger",
            "breadcrumbs": False,
            "search": {"enabled": True, "where": "header"},
            "total_routes": 4
        }
    elif complexity == "advanced":
        return {
            "layout_type": "single-page",
            "structure": [
                {"name": "Header", "description": "Top nav", "responsive": True},
                {"name": "Sidebar", "description": "Desktop nav", "responsive": True},
                {"name": "Main", "description": "Primary content", "responsive": True}
            ],
            "breakpoints": {"mobile": "320px", "tablet": "768px", "desktop": "1024px"},
            "grid_system": "12-column",
            "accessibility": ["semantic HTML", "ARIA labels", "keyboard nav"],
            "routing_structure": {
                "/": "Home",
                "/auth/login": "Login",
                "/dashboard": "Dashboard",
                "/projects": "Projects",
                "/settings": "Settings"
            },
            "navigation_menu": [
                {"label": "Home", "path": "/", "icon": "home"},
                {"label": "Dashboard", "path": "/dashboard", "icon": "dashboard", "auth": True},
                {"label": "Projects", "path": "/projects", "icon": "folder", "auth": True},
                {"label": "Settings", "path": "/settings", "icon": "settings", "auth": True}
            ],
            "mobile_menu": "bottom-tabs",
            "breadcrumbs": True,
            "search": {"enabled": True, "where": "header"},
            "total_routes": 5
        }
    else:
        return {
            "layout_type": "single-page",
            "structure": [
                {"name": "Header", "description": "Top nav", "responsive": True},
                {"name": "Main", "description": "Primary content", "responsive": True},
                {"name": "Footer", "description": "Utility links", "responsive": True}
            ],
            "breakpoints": {"mobile": "320px", "tablet": "768px", "desktop": "1024px"},
            "grid_system": "12-column",
            "accessibility": ["semantic HTML", "ARIA labels", "keyboard nav"],
            "routing_structure": {
                "/": "Home",
                "/auth/login": "Login",
                "/dashboard": "Dashboard",
                "/projects": "Projects",
                "/settings": "Settings"
            },
            "navigation_menu": [
                {"label": "Home", "path": "/", "icon": "home"},
                {"label": "Dashboard", "path": "/dashboard", "icon": "dashboard", "auth": True},
                {"label": "Projects", "path": "/projects", "icon": "folder", "auth": True},
                {"label": "Settings", "path": "/settings", "icon": "settings", "auth": True}
            ],
            "mobile_menu": "bottom-tabs",
            "breadcrumbs": True,
            "search": {"enabled": True, "where": "header"},
            "total_routes": 5
        }


def _apply_domain_context(result: dict, domain_context: dict) -> dict:
    if domain_context.get("domain") != "project_management":
        return result

    hints = frontend_hints(domain_context)
    routing_structure = {
        "/workspaces": "Workspace overview",
        "/projects": "Projects",
        "/boards": "Kanban board",
        "/tasks": "Task details",
        "/activity": "Activity feed",
        "/notifications": "Notifications",
    }
    for path in hints.get("routes", []):
        routing_structure.setdefault(path, path.rsplit("/", 1)[-1].replace("-", " ").title())

    navigation_menu = [
        {"label": "Workspaces", "path": "/workspaces", "icon": "spaces", "auth": True},
        {"label": "Projects", "path": "/projects", "icon": "folder", "auth": True},
        {"label": "Boards", "path": "/boards", "icon": "kanban", "auth": True},
        {"label": "Activity", "path": "/activity", "icon": "activity", "auth": True},
    ]

    structure = [
        {"name": "WorkspaceSidebar", "description": "Switch workspaces and projects", "responsive": True},
        {"name": "ProjectBoard", "description": "Board-centric task workflow", "responsive": True},
        {"name": "TaskDetailsDrawer", "description": "Task metadata, comments, and attachments", "responsive": True},
    ]

    result["routing_structure"] = routing_structure
    result["navigation_menu"] = navigation_menu
    result["structure"] = structure
    result["breadcrumbs"] = True
    result["search"] = {"enabled": True, "where": "workspace header"}
    result["total_routes"] = len(routing_structure)
    return result


def _sanitize_layout(result: dict, complexity: str) -> dict:
    fallback = _default_layout(complexity)
    sanitized = {
        "layout_type": str(result.get("layout_type", fallback["layout_type"])),
        "structure": result.get("structure", fallback["structure"]),
        "breakpoints": result.get("breakpoints", fallback["breakpoints"]),
        "grid_system": result.get("grid_system", fallback["grid_system"]),
        "accessibility": result.get("accessibility", fallback["accessibility"]),
        "routing_structure": result.get("routing_structure", fallback["routing_structure"]),
        "navigation_menu": result.get("navigation_menu", fallback["navigation_menu"]),
        "mobile_menu": result.get("mobile_menu", fallback["mobile_menu"]),
        "breadcrumbs": result.get("breadcrumbs", fallback["breadcrumbs"]),
        "search": result.get("search", fallback["search"]),
        "total_routes": result.get("total_routes", fallback["total_routes"]),
    }
    sanitized["structure"] = (sanitized["structure"] or [])[:3]
    sanitized["accessibility"] = (sanitized["accessibility"] or [])[:3]

    routes = sanitized["routing_structure"] or {}
    if isinstance(routes, dict):
        sanitized["routing_structure"] = dict(list(routes.items())[:5])
    else:
        sanitized["routing_structure"] = fallback["routing_structure"]

    nav = sanitized["navigation_menu"] or []
    if isinstance(nav, list):
        compact_nav = []
        for item in nav[:4]:
            if isinstance(item, dict):
                compact_nav.append({
                    "label": item.get("label", "Item"),
                    "path": item.get("path", "/"),
                    "icon": item.get("icon", "dot"),
                    "auth": bool(item.get("auth", False)),
                })
        sanitized["navigation_menu"] = compact_nav or fallback["navigation_menu"]
    else:
        sanitized["navigation_menu"] = fallback["navigation_menu"]

    search_data = sanitized.get("search")
    if not isinstance(search_data, dict):
        search_data = {"enabled": True, "where": "header"}
    sanitized["search"] = {
        "enabled": bool(search_data.get("enabled", True)),
        "where": str(search_data.get("where", "header"))
    }
    sanitized["total_routes"] = len(sanitized["routing_structure"])
    return sanitized


def _enforce_size_limit(payload: dict, fallback: dict, max_chars: int) -> dict:
    if len(str(payload)) <= max_chars:
        return payload

    compact = dict(payload)
    compact["navigation_menu"] = compact.get("navigation_menu", [])[:3]
    compact["structure"] = compact.get("structure", [])[:2]
    compact["accessibility"] = compact.get("accessibility", [])[:2]
    compact["routing_structure"] = dict(list((compact.get("routing_structure") or {}).items())[:4])
    compact["total_routes"] = len(compact["routing_structure"])
    if len(str(compact)) <= max_chars:
        return compact

    minimal = {
        "layout_type": compact.get("layout_type", "single-page"),
        "structure": [{"name": "Main", "description": "Content", "responsive": True}],
        "breakpoints": {"mobile": "320px", "tablet": "768px", "desktop": "1024px"},
        "grid_system": "12-column",
        "accessibility": ["semantic HTML", "keyboard nav"],
        "routing_structure": dict(list((compact.get("routing_structure") or {"/": "Home", "/dashboard": "Dashboard"}).items())[:3]),
        "navigation_menu": [{"label": "Home", "path": "/", "icon": "home", "auth": False}, {"label": "Dash", "path": "/dashboard", "icon": "grid", "auth": True}],
        "mobile_menu": compact.get("mobile_menu", "hamburger"),
        "breadcrumbs": bool(compact.get("breadcrumbs", False)),
        "search": {"enabled": True, "where": "header"},
        "total_routes": 0,
    }
    minimal["total_routes"] = len(minimal["routing_structure"])
    if len(str(minimal)) <= max_chars:
        return minimal
    return {
        "layout_type": "single-page",
        "structure": [{"name": "Main", "description": "Content", "responsive": True}],
        "breakpoints": {"mobile": "320px", "tablet": "768px", "desktop": "1024px"},
        "grid_system": "12-column",
        "accessibility": ["semantic HTML"],
        "routing_structure": {"/": "Home", "/dashboard": "Dashboard"},
        "navigation_menu": [{"label": "Home", "path": "/", "icon": "home", "auth": False}],
        "mobile_menu": "hamburger",
        "breadcrumbs": False,
        "search": {"enabled": True, "where": "header"},
        "total_routes": 2,
    }
