"""Navigation agent for frontend architecture design.

No hardcoded auth routes (login, register).
No hardcoded default pages (dashboard, projects, settings).
Driven entirely by SRS page definitions.
"""

import json
import logging
import asyncio
from llm_client import get_llm_response, PLANNER_MODEL
from planning_agents.shared.json_utils import extract_json

logger = logging.getLogger(__name__)

NAVIGATION_AGENT_PROMPT = """You are a frontend navigational architect. Design routing and navigation.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}
- Pages: {pages}

Design complete navigation architecture:
1. Routing structure (routes and paths) based ONLY on the listed pages
2. Navigation menu items with icons
3. Mobile menu type
4. Breadcrumbs needed?

Return ONLY valid JSON with keys:
routing_structure, navigation_menu, mobile_menu, breadcrumbs, search, total_routes, reasoning"""


async def navigation_agent(shared_state: dict) -> dict:
    try:
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "intermediate")
        frontend_fw = shared_state.get("user_stack", {}).get("frontend", "React")

        pages = shared_state.get("required_pages", [])
        pages_str = ", ".join(pages) if pages else "none specified"

        prompt = NAVIGATION_AGENT_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            frontend_framework=frontend_fw,
            pages=pages_str,
        )

        response = await asyncio.to_thread(get_llm_response, prompt, PLANNER_MODEL)

        if isinstance(response, str):
            try:
                result = extract_json(response)
            except (ValueError, json.JSONDecodeError):
                logger.warning("Navigation agent: No JSON found, using empty defaults")
                result = _empty_navigation()
        else:
            logger.warning("Navigation agent: Unexpected response type %s", type(response))
            result = _empty_navigation()

        logger.info("Navigation Agent: %d routes", result.get("total_routes", 0))
        return result

    except Exception as e:
        logger.error("Navigation agent error: %s", e)
        return _empty_navigation()


def _empty_navigation() -> dict:
    return {
        "routing_structure": {},
        "navigation_menu": [],
        "mobile_menu": "hamburger",
        "breadcrumbs": False,
        "search": {"enabled": False, "where": ""},
        "total_routes": 0,
        "reasoning": "No SRS pages defined; navigation generated from user input"
    }

# Backward compatibility alias for deprecated pipeline
_default_navigation = _empty_navigation
