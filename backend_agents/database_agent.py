import json
import logging
from llm_client import get_llm_response

logger = logging.getLogger(__name__)

DATABASE_PROMPT = """You are a database architect. Suggest database setup for this project.

RULES:
- Match user's chosen database: {database}
- Recommend appropriate ORM
- Consider caching strategy
- Return ONLY valid JSON

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
        
        prompt = DATABASE_PROMPT.format(database=database)
        logger.info(f"→ Database Agent: Analyzing {database}...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"type": database, "orm": "Unknown", "cache": "None", "migration_tool": "N/A", "recommendations": []}
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON in database response")
            return {"type": database, "orm": "Unknown", "cache": "None", "migration_tool": "N/A", "recommendations": []}
        
        result = json.loads(response_text[start:end])
        logger.info(f"✓ Database Agent: {result.get('type', 'Unknown')} + {result.get('orm', 'Unknown')}")
        return result
        
    except Exception as e:
        logger.error(f"Database Agent failed: {e}", exc_info=True)
        database = validation_output.get("user_stack", {}).get("database", "PostgreSQL") if isinstance(validation_output, dict) else "PostgreSQL"
        return {"type": database, "orm": "Unknown", "cache": "None", "migration_tool": "N/A", "recommendations": []}
