"""Animation agent for frontend architecture design.

RULE 5: Animations & UX (smooth transitions, loading states)
RULE 10: Performance-aware animations

Designs animations, transitions, loading states, and error handling.
"""

import json
import logging
from llm_client import get_llm_response, CODER_MODEL

logger = logging.getLogger(__name__)

ANIMATION_AGENT_PROMPT = """You are a frontend motion designer. Design animations and transitions.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}

Design animation strategy:
1. Page/component animations (fade-in, slide, scale)
2. Interactive transitions (hover, click, focus)
3. Loading states (skeleton, spinner, progress)
4. Error states (toast, inline messages)
5. Accessibility (respect prefers-reduced-motion)
6. Durations (100ms for micro, 300ms for major)

Return ONLY valid JSON with keys:
animations, transitions, loading_states, error_states, accessibility, reasoning

Keep durations reasonable. Don't over-animate."""


async def animation_agent(shared_state: dict) -> dict:
    """Design animation and transition strategy.
    
    Args:
        shared_state: ProjectState with project details
        
    Returns:
        Dict with animations, transitions, loading states, error handling
    """
    try:
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "intermediate")
        frontend_fw = shared_state.get("user_stack", {}).get("frontend", "React")
        
        prompt = ANIMATION_AGENT_PROMPT.format(
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
                logger.warning("Animation agent: No JSON found, using defaults")
                result = _default_animations(complexity)
        else:
            logger.warning(f"Animation agent: Unexpected response type {type(response)}")
            result = _default_animations(complexity)
            
        logger.info(f"✅ Animation Agent: Designed animation strategy")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Animation agent JSON error: {e}")
        return _default_animations(complexity)
    except Exception as e:
        logger.error(f"Animation agent error: {e}")
        return _default_animations(complexity)


def _default_animations(complexity: str) -> dict:
    """Return sensible animation defaults."""
    base_animations = [
        {"trigger": "page-load", "effect": "fade-in", "duration": "300ms"},
        {"trigger": "button-hover", "effect": "subtle-scale", "duration": "100ms"},
        {"trigger": "modal-open", "effect": "fade-in + slide-down", "duration": "200ms"},
    ]
    
    if complexity == "advanced":
        base_animations.extend([
            {"trigger": "form-submit", "effect": "loading-spinner", "duration": "ongoing"},
            {"trigger": "data-load", "effect": "skeleton-pulse", "duration": "200ms"},
        ])
    
    return {
        "animations": base_animations,
        "transitions": [
            {"element": "sidebar", "effect": "slide-in-left", "duration": "200ms"},
            {"element": "dropdown", "effect": "fade-in", "duration": "150ms"},
            {"element": "toast", "effect": "slide-up", "duration": "200ms"}
        ],
        "loading_states": [
            {"name": "skeleton", "usage": "data loading", "duration": "200ms"},
            {"name": "spinner", "usage": "async operations", "size": "24px"},
            {"name": "progress-bar", "usage": "file uploads", "animated": True}
        ],
        "error_states": [
            {"style": "toast notification", "duration": "4 seconds", "color": "red"},
            {"style": "inline error message", "color": "red", "icon": "alert"}
        ],
        "accessibility": [
            "Respect prefers-reduced-motion media query",
            "Skip animations for keyboard users",
            "Animations should not distract from content"
        ],
        "reasoning": f"Animation strategy for {complexity} complexity, balance visual appeal with performance"
    }
