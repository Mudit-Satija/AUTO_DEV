"""Animation agent for frontend architecture design.

RULE 5: Animations & UX (smooth transitions, loading states)
RULE 10: Performance-aware animations

Designs animations, transitions, loading states, and error handling.
"""

import json
import logging
import asyncio
from llm_client import get_llm_response, PLANNER_MODEL
from planning_agents.shared.domain_intelligence import domain_context_summary
from planning_agents.shared.json_utils import extract_json

logger = logging.getLogger(__name__)

MAX_OUTPUT_CHARS = 300

ANIMATION_AGENT_PROMPT = """You are a frontend motion planner.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}

Return ONLY compact JSON data with keys:
animations, transitions, loading_states, error_states, accessibility.

Constraints:
- max 2 animations
- max 1 transition
- max 1 loading state
- max 1 error state
- max 1 accessibility item
- no explanatory text or reasoning
- output must be <= 300 characters."""


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
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        prompt = ANIMATION_AGENT_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            frontend_framework=frontend_fw
        )
        prompt = prompt + "\n\nDOMAIN CONTEXT:\n" + domain_context_summary(domain_context)
        
        response = await asyncio.to_thread(get_llm_response, prompt, PLANNER_MODEL)
        
        # Extract JSON from response
        if isinstance(response, str):
            try:
                result = extract_json(response)
            except (ValueError, json.JSONDecodeError):
                logger.warning("Animation agent: No JSON found, using defaults")
                result = _default_animations(complexity)
        else:
            logger.warning(f"Animation agent: Unexpected response type {type(response)}")
            result = _default_animations(complexity)

        result = _sanitize_animation(result, complexity)
        result = _enforce_size_limit(result, MAX_OUTPUT_CHARS)
            
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
        {"trigger": "button-hover", "effect": "scale", "duration": "100ms"},
    ]
    
    if complexity == "advanced":
        base_animations[1] = {"trigger": "data-load", "effect": "skeleton", "duration": "200ms"}
    
    return {
        "animations": base_animations,
        "transitions": [
            {"element": "dropdown", "effect": "fade-in", "duration": "150ms"}
        ],
        "loading_states": [
            {"name": "skeleton", "usage": "data loading", "duration": "200ms"}
        ],
        "error_states": [
            {"style": "toast", "duration": "4s", "color": "red"}
        ],
        "accessibility": [
            "prefers-reduced-motion"
        ]
    }


def _sanitize_animation(result: dict, complexity: str) -> dict:
    fallback = _default_animations(complexity)
    sanitized = {
        "animations": result.get("animations", fallback["animations"]),
        "transitions": result.get("transitions", fallback["transitions"]),
        "loading_states": result.get("loading_states", fallback["loading_states"]),
        "error_states": result.get("error_states", fallback["error_states"]),
        "accessibility": result.get("accessibility", fallback["accessibility"]),
    }
    for key, limit in (("animations", 2), ("transitions", 1), ("loading_states", 1), ("error_states", 1), ("accessibility", 1)):
        value = sanitized.get(key, [])
        if isinstance(value, list):
            sanitized[key] = value[:limit]
        else:
            sanitized[key] = fallback[key][:limit]
    return sanitized


def _enforce_size_limit(payload: dict, max_chars: int) -> dict:
    if len(json.dumps(payload, separators=(",", ":"))) <= max_chars:
        return payload

    minimal = {
        "animations": [{"trigger": "page-load", "effect": "fade-in", "duration": "300ms"}],
        "transitions": [{"element": "dropdown", "effect": "fade-in", "duration": "150ms"}],
        "loading_states": [{"name": "skeleton", "usage": "load", "duration": "200ms"}],
        "error_states": [{"style": "toast", "duration": "4s", "color": "red"}],
        "accessibility": ["prefers-reduced-motion"],
    }
    if len(json.dumps(minimal, separators=(",", ":"))) <= max_chars:
        return minimal
    return {
        "animations": [{"trigger": "load", "effect": "fade", "duration": "300ms"}],
        "transitions": [],
        "loading_states": [],
        "error_states": [],
        "accessibility": ["reduced-motion"],
    }
