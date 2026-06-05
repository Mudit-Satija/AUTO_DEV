import json
import logging
from llm_client import get_llm_response
from planning_agents.shared.json_utils import extract_json
from planning_agents.shared.rules import RuleManager
from planning_agents.shared.domain_intelligence import domain_context_summary

logger = logging.getLogger(__name__)

DATABASE_PROMPT = """You are a database architect. Suggest database setup for this project.

RULES:
- Match user's chosen database: {database}
- Recommend appropriate ORM
- Consider caching strategy
- Return ONLY valid JSON

{rules}

Return this JSON (NO other text):
{{
    "type": "{database}",
    "orm": "recommended ORM or N/A",
    "cache": "Redis or Memcached or None",
    "migration_tool": "tool name or N/A",
    "recommendations": ["tip1", "tip2"]
}}"""


def analyze_database(validation_output: dict) -> dict:
    """Suggest database architecture"""
    try:
        if not isinstance(validation_output, dict):
            validation_output = {}
            
        database = validation_output.get("user_stack", {}).get("database", "PostgreSQL")
        domain_context = validation_output.get("domain_context", {}) if isinstance(validation_output.get("domain_context"), dict) else {}
        rules = RuleManager.from_validation_output(validation_output)
        
        prompt = DATABASE_PROMPT.format(
            database=database,
            rules=rules.prompt_context("database") + "\n" + domain_context_summary(domain_context),
        )
        logger.info(f"→ Database Agent: Analyzing {database}...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"type": database, "orm": "Unknown", "cache": "None", "migration_tool": "N/A", "recommendations": []}
        
        result = extract_json(response_text)
        if domain_context.get("backend"):
            result["reasoning"] = (
                f"{result.get('reasoning', '')}\nDomain models: {', '.join(domain_context.get('database', {}).get('preferred_tables', [])[:8])}".strip()
            )
        logger.info(f"✓ Database Agent: {result.get('type', 'Unknown')} + {result.get('orm', 'Unknown')}")
        return result
        
    except Exception as e:
        logger.error(f"Database Agent failed: {e}", exc_info=True)
        database = validation_output.get("user_stack", {}).get("database", "PostgreSQL") if isinstance(validation_output, dict) else "PostgreSQL"
        return {"type": database, "orm": "Unknown", "cache": "None", "migration_tool": "N/A", "recommendations": []}
