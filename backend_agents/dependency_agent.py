import json
import logging
from llm_client import get_llm_response
from planning_agents.shared.json_utils import extract_json
from planning_agents.shared.rules import RuleManager
from planning_agents.shared.domain_intelligence import domain_context_summary, backend_hints, merge_unique

logger = logging.getLogger(__name__)

DEPENDENCY_PROMPT = """You are a package management expert. Suggest required and optional libraries.

RULES:
- Core: Only essential packages (5-7 max)
- Optional: Nice-to-have packages with descriptions
- Match language/framework: {framework} ({language})
- Return ONLY valid JSON

{rules}

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
            
        backend_stack = validation_output.get("user_stack", {}).get("backend", "Express.js") if isinstance(validation_output, dict) else "Express.js"
        framework = architecture_result.get("framework", backend_stack)
        language = architecture_result.get("language", "JavaScript")
        rules = RuleManager.from_validation_output(validation_output)
        domain_context = validation_output.get("domain_context", {}) if isinstance(validation_output.get("domain_context"), dict) else {}
        hints = backend_hints(domain_context)
        
        prompt = DEPENDENCY_PROMPT.format(
            framework=framework,
            language=language,
            rules=rules.prompt_context("dependencies") + "\n" + domain_context_summary(domain_context),
        )
        logger.info("→ Dependency Agent: Analyzing dependencies...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"core": [], "optional": {}}
        
        result = extract_json(response_text)
        result = _apply_domain_context(result, framework, hints)
        logger.info(f"✓ Dependency Agent: {len(result.get('core', []))} core libraries")
        return result
        
    except Exception as e:
        logger.error(f"Dependency Agent failed: {e}", exc_info=True)
        return _fallback_dependencies(validation_output, architecture_result, domain_context)


def _apply_domain_context(result: dict, framework: str, hints: dict) -> dict:
    core = result.get("core", []) if isinstance(result.get("core", []), list) else []
    optional = result.get("optional", {}) if isinstance(result.get("optional", {}), dict) else {}
    preferred = []
    if framework and "node" in framework.lower():
        preferred = ["express", "jsonwebtoken", "prisma", "cors", "dotenv", "bcrypt"]
    elif framework and "fastapi" in framework.lower():
        preferred = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "passlib[bcrypt]"]
    elif framework and "spring" in framework.lower():
        preferred = ["spring-boot-starter-web", "spring-boot-starter-security", "spring-boot-starter-validation", "spring-boot-starter-data-jpa"]

    preferred.extend(hints.get("dependencies", []))
    result["core"] = merge_unique(core, preferred, limit=8)
    if not optional and hints.get("models"):
        result["optional"] = {"row-level-security": "multi-tenant safeguards"} if framework and "spring" in framework.lower() else {}
    return result


def _fallback_dependencies(validation_output: dict, architecture_result: dict, domain_context: dict) -> dict:
    backend_stack = validation_output.get("user_stack", {}).get("backend", "Express.js") if isinstance(validation_output, dict) else "Express.js"
    framework = architecture_result.get("framework", backend_stack) if isinstance(architecture_result, dict) else backend_stack
    hints = backend_hints(domain_context)
    if framework and "node" in framework.lower():
        core = ["express", "jsonwebtoken", "prisma", "cors", "dotenv", "bcrypt"]
        optional = {"multer": "file uploads", "socket.io": "real-time updates", "zod": "schema validation"}
    elif framework and "fastapi" in framework.lower():
        core = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "passlib[bcrypt]"]
        optional = {"redis": "caching and sessions", "websockets": "real-time features", "pytest": "testing framework"}
    else:
        core = ["spring-boot-starter-web", "spring-boot-starter-security", "spring-boot-starter-data-jpa", "jjwt-api"]
        optional = {"lombok": "boilerplate reduction", "flyway": "migrations", "springdoc-openapi": "api docs"}

    core = merge_unique(core, hints.get("dependencies", []), limit=8)
    return {"core": core, "optional": optional}

