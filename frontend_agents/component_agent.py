"""Component agent for frontend architecture design.

RULE 4: Component structure (atomic design)
RULE 6: Styling consistency via components

Designs reusable component library using atomic design principles.
"""

import json
import logging
import asyncio
from llm_client import get_llm_response, PLANNER_MODEL
from planning_agents.shared.domain_intelligence import domain_context_summary, frontend_hints
from planning_agents.shared.json_utils import extract_json

logger = logging.getLogger(__name__)

MAX_OUTPUT_CHARS = 800

COMPONENT_AGENT_PROMPT = """You are a frontend component planner.

Project Context:
- Type: {project_type}
- Complexity: {complexity}
- Frontend: {frontend_framework}

Return ONLY compact JSON data with keys:
components, total_components, component_library.

Constraints:
- max 8 components
- each component keys: name, type, props
- no explanations, no guides, no reasoning text
- output must be <= 800 characters."""


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
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        prompt = COMPONENT_AGENT_PROMPT.format(
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
                logger.warning("Component agent: No JSON found, using defaults")
                result = _default_components(complexity)
        else:
            logger.warning(f"Component agent: Unexpected response type {type(response)}")
            result = _default_components(complexity)

        result = _sanitize_components(result, complexity)
        result = _apply_domain_context(result, domain_context)
        result = _enforce_size_limit(result, _default_components(complexity), MAX_OUTPUT_CHARS)
            
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
        {"name": "Button", "type": "atom", "props": ["label", "onClick", "disabled"]},
        {"name": "Input", "type": "atom", "props": ["value", "onChange", "error"]},
        {"name": "Label", "type": "atom", "props": ["htmlFor", "children"]},
        {"name": "Card", "type": "molecule", "props": ["title", "children"]},
        {"name": "FormField", "type": "molecule", "props": ["label", "name", "error"]},
        {"name": "Badge", "type": "molecule", "props": ["text", "variant"]},
        {"name": "Modal", "type": "organism", "props": ["isOpen", "onClose", "children"]},
        {"name": "Navbar", "type": "organism", "props": ["items", "onNavigate"]},
    ]
    
    if complexity == "advanced":
        base_components[-1] = {"name": "DataTable", "type": "organism", "props": ["data", "columns", "onSort"]}
        library = "shadcn/ui"
    else:
        library = "Chakra UI" if complexity == "intermediate" else "plain HTML + CSS"
    
    return {
        "components": base_components,
        "total_components": len(base_components),
        "component_library": library
    }


def _apply_domain_context(result: dict, domain_context: dict) -> dict:
    if domain_context.get("domain") != "project_management":
        return result

    hints = frontend_hints(domain_context)
    domain_components = [
        {"name": "WorkspaceSidebar", "type": "organism", "props": ["workspace", "project", "onNavigate"]},
        {"name": "ProjectBoard", "type": "organism", "props": ["columns", "onReorder", "filters"]},
        {"name": "KanbanColumn", "type": "molecule", "props": ["status", "tasks", "onAddTask"]},
        {"name": "TaskCard", "type": "molecule", "props": ["task", "assignee", "dueDate"]},
        {"name": "TaskDetailsPanel", "type": "organism", "props": ["task", "comments", "attachments"]},
        {"name": "ActivityFeed", "type": "organism", "props": ["events", "filters"]},
        {"name": "NotificationCenter", "type": "organism", "props": ["notifications", "markRead"]},
        {"name": "TeamMemberList", "type": "molecule", "props": ["members", "roles"]},
    ]

    preferred_names = {str(item.get("name", "")).lower() for item in domain_components}
    existing = result.get("components", []) if isinstance(result.get("components"), list) else []
    merged = []
    seen = set()
    for component in domain_components + existing:
        if not isinstance(component, dict):
            continue
        name = str(component.get("name", "")).strip().lower()
        if not name or name in seen:
            continue
        seen.add(name)
        props = component.get("props", []) if isinstance(component.get("props", []), list) else []
        merged.append({
            "name": str(component.get("name", "Component")),
            "type": str(component.get("type", "molecule")),
            "props": [str(prop) for prop in props[:3]],
        })

    result["components"] = merged[:8]
    result["total_components"] = len(result["components"])
    result["component_library"] = result.get("component_library", "shadcn/ui")
    return result


def _sanitize_components(result: dict, complexity: str) -> dict:
    fallback = _default_components(complexity)
    components = result.get("components", fallback["components"])
    clean_components = []
    if isinstance(components, list):
        for item in components[:8]:
            if isinstance(item, dict):
                props = item.get("props", [])
                if not isinstance(props, list):
                    props = []
                clean_components.append({
                    "name": str(item.get("name", "Component")),
                    "type": str(item.get("type", "molecule")),
                    "props": [str(p) for p in props[:3]],
                })

    sanitized = {
        "components": clean_components or fallback["components"],
        "total_components": len(clean_components or fallback["components"]),
        "component_library": str(result.get("component_library", fallback["component_library"])),
    }
    return sanitized


def _enforce_size_limit(payload: dict, fallback: dict, max_chars: int) -> dict:
    if len(json.dumps(payload, separators=(",", ":"))) <= max_chars:
        return payload

    compact = dict(payload)
    compact["components"] = compact.get("components", [])[:6]
    compact["total_components"] = len(compact["components"])
    if len(json.dumps(compact, separators=(",", ":"))) <= max_chars:
        return compact

    minimal = {
        "components": [
            {"name": "Button", "type": "atom", "props": ["label", "onClick"]},
            {"name": "Input", "type": "atom", "props": ["value", "onChange"]},
            {"name": "Card", "type": "molecule", "props": ["title", "children"]},
            {"name": "Navbar", "type": "organism", "props": ["items", "onNavigate"]},
        ],
        "total_components": 4,
        "component_library": compact.get("component_library", "shadcn/ui"),
    }
    if len(json.dumps(minimal, separators=(",", ":"))) <= max_chars:
        return minimal
    return _sanitize_components(fallback, "intermediate")
