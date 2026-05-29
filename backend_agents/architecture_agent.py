import json
import logging
from llm_client import get_llm_response

logger = logging.getLogger(__name__)

ARCHITECTURE_PROMPT = """You are a backend architecture expert. Analyze the project type and suggest the best framework.

STRICT RULES:
- Match the user's chosen backend framework EXACTLY
- Return ONLY valid JSON with these exact fields: framework, language, api_style, pattern

PROJECT CONTEXT:
{context}

Return this JSON structure (NO other text):
{{
    "framework": "framework name",
    "language": "programming language",
    "api_style": "REST or GraphQL",
    "pattern": "MVC or Microservices or Monolith"
}}"""


def analyze_architecture(validation_output: dict) -> dict:
    """Analyze project and suggest backend architecture"""
    try:
        if not isinstance(validation_output, dict):
            validation_output = {}
            
        backend = validation_output.get("user_stack", {}).get("backend", "Unknown")
        project_type = validation_output.get("project_type", "web app")
        
        context = f"Backend: {backend}, Project Type: {project_type}"
        prompt = ARCHITECTURE_PROMPT.format(context=context)
        
        logger.info("→ Architecture Agent: Analyzing architecture...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"framework": backend, "language": "Unknown", "api_style": "REST", "pattern": "MVC"}
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON in architecture response")
            return {"framework": backend, "language": "Unknown", "api_style": "REST", "pattern": "MVC"}
        
        result = json.loads(response_text[start:end])
        logger.info(f"✓ Architecture Agent: {result.get('framework', 'Unknown')}")
        return result
        
    except Exception as e:
        logger.error(f"Architecture Agent failed: {e}", exc_info=True)
        return {"framework": "Unknown", "language": "Unknown", "api_style": "REST", "pattern": "MVC"}

