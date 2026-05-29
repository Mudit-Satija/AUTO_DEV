"""Layout agent for frontend architecture design.

RULE 1: Context-aware framework selection
RULE 3: Responsive design (mobile-first)
RULE 9: Accessibility in layout

Analyzes project requirements and designs page structure,
responsive breakpoints, and accessibility features.
"""

import json
import logging
from llm_client import get_llm_response, CODER_MODEL

logger = logging.getLogger(__name__)

LAYOUT_AGENT_PROMPT = """You are a frontend layout architect. Analyze the project and design responsive page structure.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}
- Realtime: {realtime}

Design the layout with:
1. Layout type (single-page, multi-page, PWA)
2. Responsive structure with semantic sections
3. Mobile-first breakpoints (320, 768, 1024px)
4. Grid system (usually 12-column)
5. Accessibility features in layout

Return ONLY valid JSON with keys:
layout_type, structure, breakpoints, grid_system, accessibility, reasoning

Be concise. Use realistic values."""


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
        
        prompt = LAYOUT_AGENT_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            frontend_framework=frontend_fw,
            realtime=realtime
        )
        
        response = await get_llm_response(prompt, CODER_MODEL)
        
        # Extract JSON from response
        if isinstance(response, str):
            # Find JSON in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                result = json.loads(json_str)
            else:
                logger.warning("Layout agent: No JSON in response, using defaults")
                result = _default_layout(complexity)
        else:
            logger.warning(f"Layout agent: Unexpected response type {type(response)}")
            result = _default_layout(complexity)
            
        logger.info(f"✅ Layout Agent: {result.get('layout_type', 'N/A')}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Layout agent JSON error: {e}")
        return _default_layout(complexity)
    except Exception as e:
        logger.error(f"Layout agent error: {e}")
        return _default_layout(complexity)


def _default_layout(complexity: str) -> dict:
    """Return sensible layout defaults based on complexity."""
    if complexity == "beginner":
        return {
            "layout_type": "single-page",
            "structure": [
                {"name": "Header", "description": "Navigation and branding", "responsive": True},
                {"name": "Main Content", "description": "Page content area", "responsive": True},
                {"name": "Footer", "description": "Footer links", "responsive": True}
            ],
            "breakpoints": {"mobile": "320px", "tablet": "768px", "desktop": "1024px"},
            "grid_system": "12-column",
            "accessibility": ["semantic HTML", "ARIA labels", "keyboard navigation"],
            "reasoning": "Simple layout for beginner projects"
        }
    elif complexity == "advanced":
        return {
            "layout_type": "single-page",
            "structure": [
                {"name": "Header", "description": "Navigation bar, branding", "responsive": True},
                {"name": "Sidebar", "description": "Navigation menu (hidden on mobile)", "responsive": True},
                {"name": "Main Content", "description": "Page content area", "responsive": True},
                {"name": "Footer", "description": "Footer links, copyright", "responsive": True}
            ],
            "breakpoints": {"mobile": "320px", "tablet": "768px", "desktop": "1024px"},
            "grid_system": "12-column",
            "accessibility": ["semantic HTML", "ARIA labels", "keyboard navigation", "focus indicators"],
            "reasoning": "Complex layout with sidebar for advanced projects"
        }
    else:
        return {
            "layout_type": "single-page",
            "structure": [
                {"name": "Header", "description": "Navigation and branding", "responsive": True},
                {"name": "Main Content", "description": "Page content area", "responsive": True},
                {"name": "Footer", "description": "Footer links", "responsive": True}
            ],
            "breakpoints": {"mobile": "320px", "tablet": "768px", "desktop": "1024px"},
            "grid_system": "12-column",
            "accessibility": ["semantic HTML", "ARIA labels", "keyboard navigation"],
            "reasoning": "Standard layout for intermediate projects"
        }
