import json
import logging
from llm_client import get_llm_response

logger = logging.getLogger(__name__)

ENDPOINT_PROMPT = """You are an API design expert. Suggest 5-7 practical REST endpoints for this project.

RULES:
- Include auth endpoints (register, login)
- Include resource endpoints (CRUD)
- Return ONLY valid JSON array
- Each endpoint must have: method, path, description, auth_required

PROJECT TYPE: {project_type}

Return this JSON array (NO other text):
[
    {{"method": "POST", "path": "/api/auth/register", "description": "Register user", "auth_required": false}},
    {{"method": "POST", "path": "/api/auth/login", "description": "Login user", "auth_required": false}},
    {{"method": "GET", "path": "/api/users/me", "description": "Get current user", "auth_required": true}}
]"""


def analyze_endpoints(validation_output: dict) -> dict:
    """Generate practical REST endpoints"""
    try:
        if not isinstance(validation_output, dict):
            validation_output = {}
            
        project_type = validation_output.get("project_type", "web app")
        
        prompt = ENDPOINT_PROMPT.format(project_type=project_type)
        logger.info("→ Endpoint Agent: Generating endpoints...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"endpoints": []}
        
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON array in endpoint response")
            return {"endpoints": []}
        
        endpoints = json.loads(response_text[start:end])
        logger.info(f"✓ Endpoint Agent: Generated {len(endpoints)} endpoints")
        return {"endpoints": endpoints}
        
    except Exception as e:
        logger.error(f"Endpoint Agent failed: {e}", exc_info=True)
        return {"endpoints": []}
