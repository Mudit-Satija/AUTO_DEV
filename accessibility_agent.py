"""Accessibility agent for frontend architecture design.

RULE 9: Accessibility (WCAG 2.1 AA compliance)
RULE 10: Performance considerations for accessibility

Ensures WCAG compliance and accessibility best practices throughout design.
"""

import json
import logging
from llm_client import get_llm_response, CODER_MODEL

logger = logging.getLogger(__name__)

ACCESSIBILITY_AGENT_PROMPT = """You are a frontend accessibility architect. Ensure WCAG 2.1 AA compliance.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}

Design comprehensive accessibility strategy:
1. WCAG 2.1 Level AA requirements
2. Semantic HTML elements
3. ARIA labels and attributes
4. Keyboard navigation
5. Color contrast (4.5:1 minimum)
6. Focus indicators and management
7. Form labels and validation
8. Testing tools and methods

Return ONLY valid JSON with keys:
wcag_level, requirements, testing, tools, reasoning

Be comprehensive. WCAG compliance is non-negotiable."""


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
        
        prompt = ACCESSIBILITY_AGENT_PROMPT.format(
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
                logger.warning("Accessibility agent: No JSON found, using defaults")
                result = _default_accessibility()
        else:
            logger.warning(f"Accessibility agent: Unexpected response type {type(response)}")
            result = _default_accessibility()
            
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
            {"name": "semantic HTML", "importance": "critical", "examples": ["<button>, <nav>, <main>, <section>"]},
            {"name": "ARIA labels", "importance": "critical", "examples": ["aria-label, aria-describedby, aria-live"]},
            {"name": "keyboard navigation", "importance": "critical", "examples": ["Tab, Enter, Escape, Arrow keys"]},
            {"name": "color contrast 4.5:1", "importance": "critical", "level": "AA"},
            {"name": "focus indicators", "importance": "high", "examples": ["visible focus rings"]},
            {"name": "alt text for images", "importance": "critical", "examples": ["descriptive alt text"]},
            {"name": "form labels", "importance": "critical", "examples": ["<label> elements for inputs"]},
            {"name": "skip links", "importance": "high", "examples": ["skip to main content"]},
            {"name": "screen reader support", "importance": "critical", "tools": ["NVDA, JAWS, VoiceOver"]},
            {"name": "text resize support", "importance": "high", "min_zoom": "200%"}
        ],
        "testing": [
            "Keyboard-only navigation test (no mouse)",
            "Screen reader test (NVDA/JAWS on Windows, VoiceOver on macOS)",
            "Color contrast check with WAVE or Lighthouse",
            "Focus management test with Tab key",
            "Mobile screen reader test (TalkBack on Android)",
            "Zoom and text resize test",
            "Automated testing with axe DevTools"
        ],
        "tools": [
            "axe DevTools (browser extension)",
            "WAVE (Web Accessibility Evaluation Tool)",
            "Lighthouse (Chrome DevTools)",
            "NVDA (free screen reader)",
            "Color Contrast Analyzer",
            "ARIA Authoring Practices Guide"
        ],
        "reasoning": "WCAG 2.1 Level AA ensures accessibility for all users including those with disabilities"
    }
