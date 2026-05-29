import json
import logging
from llm_client import get_llm_response

logger = logging.getLogger(__name__)

DEPENDENCY_PROMPT = """You are a package management expert. Suggest required and optional libraries.

RULES:
- Core: Only essential packages (5-7 max)
- Optional: Nice-to-have packages with descriptions
- Match language/framework: {framework} ({language})
- Return ONLY valid JSON

Return this JSON (NO other text):
{{
    "core": ["pkg1", "pkg2", "pkg3"],
    "optional": {{"redis": "caching", "pytest": "testing"}}
}}"""


def analyze_dependencies(validation_output: dict, architecture_result: dict, database_result: dict) -> dict:
    """Suggest required and optional libraries"""
    try:
        if not isinstance(architecture_result, dict):
            architecture_result = {}
            
        framework = architecture_result.get("framework", "Express.js")
        language = architecture_result.get("language", "JavaScript")
        
        prompt = DEPENDENCY_PROMPT.format(framework=framework, language=language)
        logger.info("→ Dependency Agent: Analyzing dependencies...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"core": [], "optional": {}}
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON in dependency response")
            return {"core": [], "optional": {}}
        
        result = json.loads(response_text[start:end])
        logger.info(f"✓ Dependency Agent: {len(result.get('core', []))} core libraries")
        return result
        
    except Exception as e:
        logger.error(f"Dependency Agent failed: {e}", exc_info=True)
        return {"core": [], "optional": {}}

