import json
import logging
from llm_client import get_llm_response
from planning_agents.shared.json_utils import extract_json
from planning_agents.shared.rules import RuleManager
from planning_agents.shared.domain_intelligence import domain_context_summary

logger = logging.getLogger(__name__)

AUTH_PROMPT = """You are a security expert. Suggest authentication approach for this project.

RULES:
- Recommend JWT by default for REST APIs
- Return ONLY valid JSON with: method, storage, libraries, recommendations

PROJECT TYPE: {project_type}

{rules}

Return this JSON (NO other text):
{{
    "method": "JWT or OAuth or Session",
    "storage": "httpOnly cookies or localStorage or server session",
    "libraries": ["lib1", "lib2"],
    "recommendations": ["tip1", "tip2"]
}}"""


def analyze_authentication(validation_output: dict) -> dict:
    """Suggest authentication strategy"""
    try:
        if not isinstance(validation_output, dict):
            validation_output = {}
            
        project_type = validation_output.get("project_type", "web app")
        domain_context = validation_output.get("domain_context", {}) if isinstance(validation_output.get("domain_context"), dict) else {}
        rules = RuleManager.from_validation_output(validation_output)
        
        prompt = AUTH_PROMPT.format(
            project_type=project_type,
            rules=rules.prompt_context("authentication") + "\n" + domain_context_summary(domain_context),
        )
        logger.info("→ Auth Agent: Analyzing authentication...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"method": "JWT", "storage": "httpOnly cookies", "libraries": [], "recommendations": []}
        
        result = extract_json(response_text)
        logger.info(f"✓ Auth Agent: {result.get('method', 'JWT')}")
        return result
        
    except Exception as e:
        logger.error(f"Auth Agent failed: {e}", exc_info=True)
        return {"method": "JWT", "storage": "httpOnly cookies", "libraries": [], "recommendations": []}
