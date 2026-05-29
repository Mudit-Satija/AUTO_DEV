"""Merger for frontend planning agents.

Combines outputs from all 6 frontend agents into one final FrontendArchitecturePlan.
Includes comprehensive type-checking and error recovery.
"""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


def merge_agent_results(
    layout: Dict[str, Any],
    components: Dict[str, Any],
    styling: Dict[str, Any],
    navigation: Dict[str, Any],
    animation: Dict[str, Any],
    accessibility: Dict[str, Any]
) -> Dict[str, Any]:
    """Merge all 6 frontend agent outputs into one final plan.
    
    Args:
        layout: Output from layout_agent
        components: Output from component_agent
        styling: Output from styling_agent
        navigation: Output from navigation_agent
        animation: Output from animation_agent
        accessibility: Output from accessibility_agent
        
    Returns:
        Merged FrontendArchitecturePlan dict
    """
    
    logger.info("🔀 MERGING FRONTEND AGENT RESULTS")
    
    try:
        # Type-check all inputs and provide defaults if needed
        layout = _ensure_dict(layout, "layout_agent")
        components = _ensure_dict(components, "component_agent")
        styling = _ensure_dict(styling, "styling_agent")
        navigation = _ensure_dict(navigation, "navigation_agent")
        animation = _ensure_dict(animation, "animation_agent")
        accessibility = _ensure_dict(accessibility, "accessibility_agent")
        
        # Extract values with safe defaults
        framework = styling.get("styling_approach", "tailwind")
        styling_approach = styling.get("styling_approach", "tailwind")
        layout_type = layout.get("layout_type", "single-page")
        
        # Determine framework from layout and styling
        frontend_framework = "React"  # Default
        if layout.get("layout_type") == "multi-page":
            frontend_framework = "Next.js"
        
        # Build the merged result
        result = {
            "status": "success",
            "frontend_architecture": {
                "framework": frontend_framework,
                "language": "TypeScript",
                "styling": styling_approach,
                "layout_type": layout_type
            },
            "design_system": styling.get("design_system", {}),
            "layout": layout.get("structure", []),
            "breakpoints": layout.get("breakpoints", {}),
            "grid_system": layout.get("grid_system", "12-column"),
            "components": components.get("components", []),
            "component_library": components.get("component_library", "shadcn/ui"),
            "navigation": navigation.get("navigation_menu", []),
            "routing": navigation.get("routing_structure", {}),
            "mobile_menu": navigation.get("mobile_menu", "hamburger"),
            "animations": animation.get("animations", []),
            "transitions": animation.get("transitions", []),
            "loading_states": animation.get("loading_states", []),
            "error_states": animation.get("error_states", []),
            "accessibility": {
                "wcag_level": accessibility.get("wcag_level", "AA"),
                "requirements": accessibility.get("requirements", []),
                "testing": accessibility.get("testing", []),
                "tools": accessibility.get("tools", [])
            },
            "theme_support": styling.get("theme_support", "light/dark"),
            "total_components": components.get("total_components", 0),
            "total_routes": navigation.get("total_routes", 0),
            "combined_reasoning": _combine_reasoning(
                layout.get("reasoning", ""),
                components.get("reasoning", ""),
                styling.get("reasoning", ""),
                navigation.get("reasoning", ""),
                animation.get("reasoning", ""),
                accessibility.get("reasoning", "")
            )
        }
        
        logger.info(f"✅ Merged: {result['frontend_architecture']['framework']} + {result['component_library']}")
        logger.info(f"✅ Merged: {result['total_components']} components, {result['total_routes']} routes")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Merger error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Failed to merge frontend results: {str(e)}"
        }


def _ensure_dict(value: Any, agent_name: str) -> Dict[str, Any]:
    """Ensure value is a dict, log warnings if not."""
    if isinstance(value, dict):
        return value
    elif isinstance(value, str):
        logger.warning(f"⚠️  {agent_name} returned string, not dict: {value[:50]}")
        return {}
    elif value is None:
        logger.warning(f"⚠️  {agent_name} returned None")
        return {}
    else:
        logger.warning(f"⚠️  {agent_name} returned {type(value).__name__}")
        return {}


def _combine_reasoning(*reasoning_parts: str) -> str:
    """Combine reasoning from all agents."""
    combined = "\n".join([
        f"• {part.strip()}"
        for part in reasoning_parts
        if part and part.strip()
    ])
    return combined if combined else "Optimized frontend architecture based on project requirements"
