import json
import logging
from llm_client import get_llm_response
from planning_agents.shared.json_utils import extract_json
from planning_agents.shared.rules import RuleManager
from planning_agents.shared.domain_intelligence import domain_context_summary

logger = logging.getLogger(__name__)

ARCHITECTURE_PROMPT = """You are a backend architecture expert. Analyze the project type and suggest the best framework.

STRICT RULES:
- Match the user's chosen backend framework EXACTLY
- Return ONLY valid JSON with these exact fields: framework, language, api_style, pattern

PROJECT CONTEXT:
{context}

{rules}

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
        domain_context = validation_output.get("domain_context", {}) if isinstance(validation_output.get("domain_context"), dict) else {}
        rules = RuleManager.from_validation_output(validation_output)
        
        context = f"Backend: {backend}, Project Type: {project_type}\n{domain_context_summary(domain_context)}"
        prompt = ARCHITECTURE_PROMPT.format(context=context, rules=rules.prompt_context("architecture"))
        
        logger.info("→ Architecture Agent: Analyzing architecture...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"framework": backend, "language": "Unknown", "api_style": "REST", "pattern": "MVC"}
        
        result = extract_json(response_text)
        logger.info(f"✓ Architecture Agent: {result.get('framework', 'Unknown')}")
        return result
        
    except Exception as e:
        logger.error(f"Architecture Agent failed: {e}", exc_info=True)
        return {"framework": "Unknown", "language": "Unknown", "api_style": "REST", "pattern": "MVC"}

