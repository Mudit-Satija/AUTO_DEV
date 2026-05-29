"""Navigation agent for frontend architecture design.

RULE 8: Navigation (clear IA, mobile-friendly)
RULE 7: Form handling and search integration

Designs routing structure and navigation menu layout.
"""

import json
import logging
from llm_client import get_llm_response, CODER_MODEL

logger = logging.getLogger(__name__)

NAVIGATION_AGENT_PROMPT = """You are a frontend navigation architect. Design routing and navigation.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}

Design complete navigation architecture:
1. Routing structure (routes and paths)
2. Navigation menu items with icons
3. Mobile menu type (hamburger, bottom-tabs, drawer)
4. Breadcrumbs needed? (for complex apps)
5. Search/filter feature placement
6. Protected routes (with auth)

Return ONLY valid JSON with keys:
routing_structure, navigation_menu, mobile_menu, breadcrumbs, search, total_routes, reasoning

Include 7-12 routes for typical app (auth, dashboard, main features, settings)."""


async def navigation_agent(shared_state: dict) -> dict:
    """Design routing structure and navigation menu.
    
    Args:
        shared_state: ProjectState with project details
        
    Returns:
        Dict with routing_structure, navigation_menu, mobile_menu setup
    """
    try:
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "intermediate")
        frontend_fw = shared_state.get("user_stack", {}).get("frontend", "React")
        
        prompt = NAVIGATION_AGENT_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            frontend_framework=frontend_fw
        )
        
        response = await get_llm_response(prompt, CODER_MODEL)
        
        # Extract JSON from response
        if isinstance(response, str):
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                logger.warning("Navigation agent: No JSON found, using defaults")
                result = _default_navigation(complexity)
        else:
            logger.warning(f"Navigation agent: Unexpected response type {type(response)}")
            result = _default_navigation(complexity)
            
        logger.info(f"✅ Navigation Agent: {result.get('total_routes', 'N/A')} routes")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Navigation agent JSON error: {e}")
        return _default_navigation(complexity)
    except Exception as e:
        logger.error(f"Navigation agent error: {e}")
        return _default_navigation(complexity)


def _default_navigation(complexity: str) -> dict:
    """Return sensible navigation defaults."""
    base_routes = {
        "/": "Home",
        "/auth/login": "Login",
        "/auth/register": "Register",
    }
    
    if complexity == "beginner":
        base_routes.update({
            "/dashboard": "Dashboard",
            "/profile": "Profile",
        })
        menu_items = [
            {"label": "Home", "path": "/", "icon": "home"},
            {"label": "Dashboard", "path": "/dashboard", "icon": "dashboard", "auth": True},
            {"label": "Profile", "path": "/profile", "icon": "user", "auth": True},
        ]
        breadcrumbs = False
    else:
        base_routes.update({
            "/dashboard": "Dashboard",
            "/projects": "Projects list",
            "/projects/:id": "Project detail",
            "/settings": "User settings",
            "/admin": "Admin panel"
        })
        menu_items = [
            {"label": "Home", "path": "/", "icon": "home"},
            {"label": "Dashboard", "path": "/dashboard", "icon": "dashboard", "auth": True},
            {"label": "Projects", "path": "/projects", "icon": "folder", "auth": True},
            {"label": "Settings", "path": "/settings", "icon": "settings", "auth": True},
        ]
        breadcrumbs = True
    
    return {
        "routing_structure": base_routes,
        "navigation_menu": menu_items,
        "mobile_menu": "hamburger" if complexity == "beginner" else "bottom-tabs",
        "breadcrumbs": breadcrumbs,
        "search": {"enabled": True, "where": "header"},
        "total_routes": len(base_routes),
        "reasoning": f"Navigation optimized for {complexity} complexity projects"
    }
