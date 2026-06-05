"""Styling agent for frontend architecture design.

RULE 1: Context-aware framework (Tailwind vs styled-components)
RULE 6: Styling strategy and design system
RULE 10: Performance-aware bundle sizing

Designs design system, styling approach, and theme support.
"""

import json
import logging
import asyncio
from llm_client import get_llm_response, PLANNER_MODEL
from planning_agents.shared.domain_intelligence import domain_context_summary
from planning_agents.shared.json_utils import extract_json

logger = logging.getLogger(__name__)

MAX_OUTPUT_CHARS = 500

STYLING_AGENT_PROMPT = """You are a frontend styling planner.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}

Return ONLY compact JSON data with keys:
styling_approach, design_system, theme_support, animations, css_architecture, bundle_impact.

Constraints:
- max 4 colors
- max 2 typography entries
- max 2 animations
- no tutorials, no best-practice essays, no reasoning text
- output must be <= 500 characters."""


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
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        prompt = STYLING_AGENT_PROMPT.format(
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
                logger.warning("Styling agent: No JSON found, using defaults")
                result = _default_styling(complexity)
        else:
            logger.warning(f"Styling agent: Unexpected response type {type(response)}")
            result = _default_styling(complexity)

        result = _sanitize_styling(result, complexity)
        result = _enforce_size_limit(result, _default_styling(complexity), MAX_OUTPUT_CHARS)
            
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
                {"name": "neutral", "value": "#64748B"}
            ],
            "typography": [
                {"name": "heading", "size": "28px", "weight": 700},
                {"name": "body", "size": "16px", "weight": 400}
            ],
            "spacing": "8px",
            "border_radius": [4, 8, 12]
        },
        "theme_support": "light/dark",
        "animations": [
            {"name": "fade-in", "duration": "200ms", "easing": "ease-in-out"},
            {"name": "slide-down", "duration": "300ms", "easing": "ease-out"}
        ],
        "css_architecture": "CSS variables with fallbacks for theming",
        "bundle_impact": bundle_impact
    }


def _sanitize_styling(result: dict, complexity: str) -> dict:
    fallback = _default_styling(complexity)
    ds = result.get("design_system", {}) if isinstance(result.get("design_system", {}), dict) else {}
    colors = ds.get("colors", fallback["design_system"]["colors"])
    typography = ds.get("typography", fallback["design_system"]["typography"])
    animations = result.get("animations", fallback["animations"])

    sanitized = {
        "styling_approach": str(result.get("styling_approach", fallback["styling_approach"])),
        "design_system": {
            "colors": (colors if isinstance(colors, list) else fallback["design_system"]["colors"])[:4],
            "typography": (typography if isinstance(typography, list) else fallback["design_system"]["typography"])[:2],
            "spacing": str(ds.get("spacing", fallback["design_system"]["spacing"])),
            "border_radius": ds.get("border_radius", fallback["design_system"]["border_radius"]),
        },
        "theme_support": str(result.get("theme_support", fallback["theme_support"])),
        "animations": (animations if isinstance(animations, list) else fallback["animations"])[:2],
        "css_architecture": str(result.get("css_architecture", fallback["css_architecture"])),
        "bundle_impact": str(result.get("bundle_impact", fallback["bundle_impact"])),
    }
    return sanitized


def _enforce_size_limit(payload: dict, fallback: dict, max_chars: int) -> dict:
    if len(str(payload)) <= max_chars:
        return payload

    compact = dict(payload)
    compact["design_system"] = {
        "colors": compact.get("design_system", {}).get("colors", [])[:3],
        "typography": compact.get("design_system", {}).get("typography", [])[:1],
        "spacing": "8px",
        "border_radius": [4, 8],
    }
    compact["animations"] = compact.get("animations", [])[:1]
    if len(str(compact)) <= max_chars:
        return compact

    minimal = {
        "styling_approach": "tailwind",
        "design_system": {
            "colors": [{"name": "primary", "value": "#3B82F6"}, {"name": "danger", "value": "#EF4444"}],
            "typography": [{"name": "body", "size": "16px", "weight": 400}],
            "spacing": "8px",
            "border_radius": [4, 8],
        },
        "theme_support": "light/dark",
        "animations": [{"name": "fade-in", "duration": "200ms", "easing": "ease-in-out"}],
        "css_architecture": "CSS variables",
        "bundle_impact": "~15KB",
    }
    if len(str(minimal)) <= max_chars:
        return minimal
    return {
        "styling_approach": "tailwind",
        "design_system": {"colors": [{"name": "primary", "value": "#3B82F6"}], "typography": [{"name": "body", "size": "16px", "weight": 400}], "spacing": "8px", "border_radius": [4]},
        "theme_support": "light",
        "animations": [],
        "css_architecture": "CSS vars",
        "bundle_impact": "~15KB",
    }
