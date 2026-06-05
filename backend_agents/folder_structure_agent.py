import json
import logging
from llm_client import get_llm_response
from planning_agents.shared.json_utils import extract_json
from planning_agents.shared.rules import RuleManager
from planning_agents.shared.domain_intelligence import domain_context_summary, backend_hints, merge_unique

logger = logging.getLogger(__name__)

FOLDER_PROMPT = """You are a code organization expert. Suggest modular folder structure for scalability.

RULES:
- Design for separation of concerns
- Return ONLY valid JSON array
- Each folder must have: name, description

FRAMEWORK: {framework}

{rules}

Return this JSON array (NO other text):
[
    {{"name": "routes/", "description": "API route definitions"}},
    {{"name": "services/", "description": "Business logic layer"}},
    {{"name": "models/", "description": "Data models"}},
    {{"name": "middleware/", "description": "Request/response middleware"}},
    {{"name": "utils/", "description": "Utility functions"}}
]"""


def analyze_folder_structure(validation_output: dict, architecture_result: dict) -> dict:
    """Suggest modular folder structure"""
    try:
        if not isinstance(architecture_result, dict):
            architecture_result = {}
            
        framework = architecture_result.get("framework", "Express.js")
        rules = RuleManager.from_validation_output(validation_output)
        domain_context = validation_output.get("domain_context", {}) if isinstance(validation_output.get("domain_context"), dict) else {}
        
        prompt = FOLDER_PROMPT.format(
            framework=framework,
            rules=rules.prompt_context("folder_structure") + "\n" + domain_context_summary(domain_context),
        )
        logger.info("→ Folder Structure Agent: Designing folder structure...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"folders": []}
        
        folders = extract_json(response_text)
        folders = _apply_domain_context(folders, domain_context)
        logger.info(f"✓ Folder Structure Agent: {len(folders)} folders")
        return {"folders": folders}
        
    except Exception as e:
        logger.error(f"Folder Structure Agent failed: {e}", exc_info=True)
        return {"folders": []}


def _apply_domain_context(folders: list, domain_context: dict) -> list:
    if not isinstance(folders, list):
        folders = []
    hints = backend_hints(domain_context)
    preferred_modules = hints.get("modules", [])
    if domain_context.get("domain") == "project_management" and preferred_modules:
        preferred_folders = [
            {"name": "src/domains/workspaces/", "description": "Workspace domain modules"},
            {"name": "src/domains/projects/", "description": "Project domain modules"},
            {"name": "src/domains/tasks/", "description": "Task and board modules"},
            {"name": "src/domains/activity/", "description": "Activity log modules"},
            {"name": "src/domains/notifications/", "description": "Notification modules"},
        ]
        merged = preferred_folders + [item for item in folders if isinstance(item, dict)]
        seen = set()
        result = []
        for folder in merged:
            name = str(folder.get("name") or folder.get("path") or "").strip().lower()
            if not name or name in seen:
                continue
            seen.add(name)
            result.append(folder)
        return result[:8]
    return folders

