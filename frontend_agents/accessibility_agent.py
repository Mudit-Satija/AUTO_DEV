"""Accessibility agent for frontend architecture design.

RULE 9: Accessibility (WCAG 2.1 AA compliance)
RULE 10: Performance considerations for accessibility

Ensures WCAG compliance and accessibility best practices throughout design.
"""

import json
import logging
import asyncio
from llm_client import get_llm_response, PLANNER_MODEL
from planning_agents.shared.domain_intelligence import domain_context_summary
from planning_agents.shared.json_utils import extract_json

logger = logging.getLogger(__name__)

MAX_OUTPUT_CHARS = 500

ACCESSIBILITY_AGENT_PROMPT = """You are a frontend accessibility planner.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}

Return ONLY compact JSON data with keys:
wcag_level, requirements, testing, tools.

Constraints:
- max 5 requirements
- max 3 testing items
- max 3 tools
- no prose, no tutorials, no implementation guides, no reasoning text
- output must be <= 500 characters."""


async def accessibility_agent(shared_state: dict) -> dict:
    """Design accessibility strategy and WCAG compliance.
    
    Args:
        shared_state: ProjectState with project details
        
    Returns:
        Dict with WCAG requirements, testing strategy, accessibility tools
    """
    try:
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "intermediate")
        frontend_fw = shared_state.get("user_stack", {}).get("frontend", "React")
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        prompt = ACCESSIBILITY_AGENT_PROMPT.format(
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
                logger.warning("Accessibility agent: No JSON found, using defaults")
                result = _default_accessibility()
        else:
            logger.warning(f"Accessibility agent: Unexpected response type {type(response)}")
            result = _default_accessibility()

        result = _sanitize_accessibility(result)
        result = _enforce_size_limit(result, _default_accessibility(), MAX_OUTPUT_CHARS)
            
        logger.info(f"✅ Accessibility Agent: {result.get('wcag_level', 'N/A')} compliance")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Accessibility agent JSON error: {e}")
        return _default_accessibility()
    except Exception as e:
        logger.error(f"Accessibility agent error: {e}")
        return _default_accessibility()


def _default_accessibility() -> dict:
    """Return comprehensive accessibility defaults."""
    return {
        "wcag_level": "AA",
        "requirements": [
            {"name": "semantic HTML", "importance": "critical"},
            {"name": "ARIA labels", "importance": "critical"},
            {"name": "keyboard navigation", "importance": "critical"},
            {"name": "color contrast 4.5:1", "importance": "critical"},
            {"name": "focus indicators", "importance": "high"}
        ],
        "testing": [
            "Keyboard-only navigation",
            "Screen reader check",
            "Contrast check"
        ],
        "tools": [
            "axe DevTools",
            "Lighthouse",
            "WAVE"
        ]
    }


def _sanitize_accessibility(result: dict) -> dict:
    fallback = _default_accessibility()
    requirements = result.get("requirements", fallback["requirements"])
    clean_reqs = []
    if isinstance(requirements, list):
        for item in requirements[:5]:
            if isinstance(item, dict):
                clean_reqs.append({
                    "name": str(item.get("name", "requirement")),
                    "importance": str(item.get("importance", "high")),
                })
            else:
                clean_reqs.append({"name": str(item), "importance": "high"})

    testing = result.get("testing", fallback["testing"])
    tools = result.get("tools", fallback["tools"])

    return {
        "wcag_level": str(result.get("wcag_level", fallback["wcag_level"])),
        "requirements": clean_reqs or fallback["requirements"],
        "testing": [str(x) for x in (testing if isinstance(testing, list) else fallback["testing"])[:3]],
        "tools": [str(x) for x in (tools if isinstance(tools, list) else fallback["tools"])[:3]],
    }


def _enforce_size_limit(payload: dict, fallback: dict, max_chars: int) -> dict:
    if len(str(payload)) <= max_chars:
        return payload

    compact = dict(payload)
    compact["requirements"] = compact.get("requirements", [])[:3]
    compact["testing"] = compact.get("testing", [])[:2]
    compact["tools"] = compact.get("tools", [])[:2]
    if len(str(compact)) <= max_chars:
        return compact

    minimal = {
        "wcag_level": "AA",
        "requirements": [{"name": "semantic HTML", "importance": "critical"}, {"name": "keyboard navigation", "importance": "critical"}],
        "testing": ["Keyboard-only navigation"],
        "tools": ["axe DevTools"],
    }
    if len(str(minimal)) <= max_chars:
        return minimal
    return {
        "wcag_level": "AA",
        "requirements": [{"name": "semantic HTML", "importance": "critical"}],
        "testing": [],
        "tools": [],
    }
