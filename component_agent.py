"""Component agent for frontend architecture design.

RULE 4: Component structure (atomic design)
RULE 6: Styling consistency via components

Designs reusable component library using atomic design principles.
"""

import json
import logging
from llm_client import get_llm_response, CODER_MODEL

logger = logging.getLogger(__name__)

COMPONENT_AGENT_PROMPT = """You are a frontend component architect. Design reusable components.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}

Design components following atomic design (atoms→molecules→organisms):
1. List 10-15 reusable components
2. Categorize each: atom, molecule, organism
3. Define props for each component
4. Suggest component library (shadcn/ui, Chakra UI, Material UI)

Return ONLY valid JSON with keys:
components (array), total_components, component_library, reasoning

Atoms: Button, Input, Label, Icon
Molecules: FormField, Card, Badge, Dropdown
Organisms: Modal, Navbar, Form, UserProfile"""


async def component_agent(shared_state: dict) -> dict:
    """Design component architecture and library.
    
    Args:
        shared_state: ProjectState with project details
        
    Returns:
        Dict with components list and library recommendation
    """
    try:
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "intermediate")
        frontend_fw = shared_state.get("user_stack", {}).get("frontend", "React")
        
        prompt = COMPONENT_AGENT_PROMPT.format(
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
                logger.warning("Component agent: No JSON found, using defaults")
                result = _default_components(complexity)
        else:
            logger.warning(f"Component agent: Unexpected response type {type(response)}")
            result = _default_components(complexity)
            
        logger.info(f"✅ Component Agent: {result.get('total_components', 'N/A')} components")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Component agent JSON error: {e}")
        return _default_components(complexity)
    except Exception as e:
        logger.error(f"Component agent error: {e}")
        return _default_components(complexity)


def _default_components(complexity: str) -> dict:
    """Return sensible component defaults."""
    base_components = [
        {"name": "Button", "type": "atom", "variants": ["primary", "secondary", "danger"], "props": ["label", "onClick", "disabled"]},
        {"name": "Input", "type": "atom", "variants": ["text", "email", "password"], "props": ["value", "onChange", "error"]},
        {"name": "Label", "type": "atom", "props": ["htmlFor", "children"]},
        {"name": "Icon", "type": "atom", "props": ["name", "size", "color"]},
        {"name": "Card", "type": "molecule", "purpose": "Reusable content container", "props": ["title", "children", "actions"]},
        {"name": "FormField", "type": "molecule", "purpose": "Label + Input + Error", "props": ["label", "name", "error"]},
        {"name": "Badge", "type": "molecule", "purpose": "Status indicator", "props": ["text", "variant"]},
        {"name": "Dropdown", "type": "molecule", "purpose": "Menu dropdown", "props": ["items", "onSelect"]},
        {"name": "Modal", "type": "organism", "purpose": "Dialog/popup", "props": ["isOpen", "onClose", "title", "children"]},
        {"name": "Navbar", "type": "organism", "purpose": "Navigation bar", "props": ["items", "onNavigate"]},
    ]
    
    if complexity == "advanced":
        advanced = [
            {"name": "Form", "type": "organism", "purpose": "Complex form with validation", "props": ["fields", "onSubmit"]},
            {"name": "UserProfile", "type": "organism", "purpose": "User info display", "props": ["user", "onEdit"]},
            {"name": "DataTable", "type": "organism", "purpose": "Sortable data table", "props": ["data", "columns", "pagination"]},
        ]
        base_components.extend(advanced)
        library = "shadcn/ui"
    else:
        library = "Chakra UI" if complexity == "intermediate" else "plain HTML + CSS"
    
    return {
        "components": base_components,
        "total_components": len(base_components),
        "component_library": library,
        "reasoning": "Component set appropriate for {complexity} complexity projects"
    }
