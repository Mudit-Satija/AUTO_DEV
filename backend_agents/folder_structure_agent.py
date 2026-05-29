import json
import logging
from llm_client import get_llm_response

logger = logging.getLogger(__name__)

FOLDER_PROMPT = """You are a code organization expert. Suggest modular folder structure for scalability.

RULES:
- Design for separation of concerns
- Return ONLY valid JSON array
- Each folder must have: name, description

FRAMEWORK: {framework}

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
        
        prompt = FOLDER_PROMPT.format(framework=framework)
        logger.info("→ Folder Structure Agent: Designing folder structure...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"folders": []}
        
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON array in folder structure response")
            return {"folders": []}
        
        folders = json.loads(response_text[start:end])
        logger.info(f"✓ Folder Structure Agent: {len(folders)} folders")
        return {"folders": folders}
        
    except Exception as e:
        logger.error(f"Folder Structure Agent failed: {e}", exc_info=True)
        return {"folders": []}

