"""Styling agent for frontend architecture design.

RULE 1: Context-aware framework (Tailwind vs styled-components)
RULE 6: Styling strategy and design system
RULE 10: Performance-aware bundle sizing

Designs design system, styling approach, and theme support.
"""

import json
import logging
from llm_client import get_llm_response, CODER_MODEL

logger = logging.getLogger(__name__)

STYLING_AGENT_PROMPT = """You are a frontend design system architect. Design styling strategy.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}

Design a complete design system:
1. Styling approach (tailwind, styled-components, CSS modules)
2. Color palette (primary, secondary, danger, success)
3. Typography scale (heading-1, body, caption)
4. Spacing system (8px base unit)
5. Border radius values
6. Theme support (light, dark, or both)
7. Common animations (fade-in, slide-down, etc)
8. Bundle size estimate

Return ONLY valid JSON with keys:
styling_approach, design_system, theme_support, animations, css_architecture, bundle_impact, reasoning"""


async def styling_agent(shared_state: dict) -> dict:
    """Design styling approach and design system.
    
    Args:
        shared_state: ProjectState with project details
        
    Returns:
        Dict with styling_approach, design_system, animations, theme support
    """
    try:
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "intermediate")
        frontend_fw = shared_state.get("user_stack", {}).get("frontend", "React")
        
        prompt = STYLING_AGENT_PROMPT.format(
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
                logger.warning("Styling agent: No JSON found, using defaults")
                result = _default_styling(complexity)
        else:
            logger.warning(f"Styling agent: Unexpected response type {type(response)}")
            result = _default_styling(complexity)
            
        logger.info(f"✅ Styling Agent: {result.get('styling_approach', 'N/A')}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Styling agent JSON error: {e}")
        return _default_styling(complexity)
    except Exception as e:
        logger.error(f"Styling agent error: {e}")
        return _default_styling(complexity)


def _default_styling(complexity: str) -> dict:
    """Return sensible styling defaults."""
    if complexity == "beginner":
        approach = "vanilla CSS"
        bundle_impact = "~5KB"
    elif complexity == "advanced":
        approach = "tailwind"
        bundle_impact = "~15KB (with PurgeCSS)"
    else:
        approach = "tailwind"
        bundle_impact = "~15KB (with PurgeCSS)"
    
    return {
        "styling_approach": approach,
        "design_system": {
            "colors": [
                {"name": "primary", "value": "#3B82F6"},
                {"name": "secondary", "value": "#10B981"},
                {"name": "danger", "value": "#EF4444"},
                {"name": "warning", "value": "#F59E0B"},
                {"name": "info", "value": "#06B6D4"},
                {"name": "success", "value": "#10B981"}
            ],
            "typography": [
                {"name": "heading-1", "size": "32px", "weight": 700, "line_height": "1.2"},
                {"name": "heading-2", "size": "24px", "weight": 700, "line_height": "1.3"},
                {"name": "body", "size": "16px", "weight": 400, "line_height": "1.5"},
                {"name": "caption", "size": "12px", "weight": 400, "line_height": "1.4"}
            ],
            "spacing": "8px base unit (8, 16, 24, 32, 40, 48, 56, 64px)",
            "border_radius": [4, 8, 12, 16, "full"]
        },
        "theme_support": "light/dark",
        "animations": [
            {"name": "fade-in", "duration": "200ms", "easing": "ease-in-out"},
            {"name": "slide-down", "duration": "300ms", "easing": "ease-out"},
            {"name": "slide-up", "duration": "300ms", "easing": "ease-out"},
            {"name": "scale-in", "duration": "200ms", "easing": "ease-out"}
        ],
        "css_architecture": "CSS variables with fallbacks for theming",
        "bundle_impact": bundle_impact,
        "reasoning": f"Design system optimized for {complexity} complexity projects"
    }
