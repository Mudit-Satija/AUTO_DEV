import json
import logging
from typing import Dict, List
from pydantic import BaseModel
from backend_schemas import BackendArchitecturePlan, AuthenticationStrategy, DatabaseStrategy, APIEndpoint, FolderStructure
from planning_agents.shared.consistency_validator import ConsistencyValidator
from planning_agents.shared.rules import RuleManager

logger = logging.getLogger(__name__)


def _build_validated_reasoning(plan: Dict, validation_output: Dict) -> str:
    """Generate stack-specific detailed reasoning from validated plan data."""
    framework = str(plan.get("framework", "Unknown"))
    language = str(plan.get("language", "Unknown"))
    project_type = str((validation_output or {}).get("project_type", "software project"))

    auth = plan.get("authentication", {}) if isinstance(plan.get("authentication"), dict) else {}
    database = plan.get("database", {}) if isinstance(plan.get("database"), dict) else {}
    core = plan.get("core_libraries", []) if isinstance(plan.get("core_libraries"), list) else []
    optional = plan.get("optional_libraries", {}) if isinstance(plan.get("optional_libraries"), dict) else {}
    patterns = plan.get("design_patterns", []) if isinstance(plan.get("design_patterns"), list) else []

    stack_note = ""
    lower_framework = framework.lower()
    if "spring" in lower_framework:
        stack_note = "This plan stays within the Java/Spring ecosystem and uses Spring-compatible libraries."
    elif "fastapi" in lower_framework:
        stack_note = "This plan stays within the Python/FastAPI ecosystem and uses Python-native backend tooling."
    elif "node" in lower_framework or "express" in lower_framework:
        stack_note = "This plan stays within the Node.js ecosystem and uses JavaScript-native backend tooling."

    return (
        f"Architecture rationale for {project_type}: {framework} ({language}) was selected to align with the validated stack and API style.\n"
        f"Authentication uses {auth.get('method', 'JWT')} with libraries: {', '.join(auth.get('libraries', [])) or 'N/A'}.\n"
        f"Database strategy uses {database.get('type', 'N/A')} with {database.get('orm', 'N/A')} for persistence alignment.\n"
        f"Core libraries selected: {', '.join(core) if core else 'N/A'}.\n"
        f"Optional libraries selected: {', '.join(optional.keys()) if optional else 'N/A'}.\n"
        f"Design patterns applied: {', '.join(patterns) if patterns else 'N/A'}.\n"
        f"{stack_note}".strip()
    )


def _normalize_string_list(value) -> List[str]:
    """Normalize model output into a list of strings."""
    if not isinstance(value, list):
        return []

    normalized = []
    for item in value:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict):
            name = (
                item.get("library_name")
                or item.get("name")
                or item.get("package")
                or item.get("tool")
            )
            normalized.append(str(name or item))
        else:
            normalized.append(str(item))

    return normalized


def _normalize_optional_libraries(value) -> Dict[str, str]:
    """Normalize optional libraries into {package: description}."""
    if isinstance(value, list):
        return {
            item: "Optional dependency"
            for item in _normalize_string_list(value)
        }

    if not isinstance(value, dict):
        return {}

    normalized = {}
    for key, item in value.items():
        if isinstance(item, str):
            normalized[str(key)] = item
        elif isinstance(item, dict):
            name = (
                item.get("library_name")
                or item.get("name")
                or item.get("package")
                or key
            )
            description = (
                item.get("purpose")
                or item.get("description")
                or item.get("reason")
                or "Optional dependency"
            )
            normalized[str(name)] = str(description)
        else:
            normalized[str(key)] = str(item)

    return normalized


def merge_agent_results(all_results: Dict, validation_output: Dict) -> Dict:
    """
    Merge all 6 parallel agent results into a single BackendArchitecturePlan.
    
    Each agent returns a dict, and we combine them into the final structure.
    All results are type-checked and default-protected.
    """
    
    try:
        # Safely extract each agent result
        arch = all_results.get("architecture", {})
        auth = all_results.get("authentication", {})
        endpoints_data = all_results.get("endpoints", {})
        db = all_results.get("database", {})
        folder = all_results.get("folder_structure", {})
        deps = all_results.get("dependencies", {})
        
        # Type check and normalize each result
        if not isinstance(arch, dict):
            logger.warning(f"Architecture result is not dict: {type(arch)}")
            arch = {}
        if not isinstance(auth, dict):
            logger.warning(f"Auth result is not dict: {type(auth)}")
            auth = {}
        if not isinstance(endpoints_data, dict):
            logger.warning(f"Endpoints result is not dict: {type(endpoints_data)}")
            endpoints_data = {}
        if not isinstance(db, dict):
            logger.warning(f"Database result is not dict: {type(db)}")
            db = {}
        if not isinstance(folder, dict):
            logger.warning(f"Folder result is not dict: {type(folder)}")
            folder = {}
        if not isinstance(deps, dict):
            logger.warning(f"Dependencies result is not dict: {type(deps)}")
            deps = {}
        
        logger.info("Merging 6 parallel agent results...")
        
        # Build authentication strategy
        auth_libraries = _normalize_string_list(auth.get("libraries", []))
        
        security_practices = _normalize_string_list(auth.get("security_best_practices", []))
        if not security_practices:
            security_practices = ["Use HTTPS", "Implement rate limiting", "Use secure password hashing"]
        
        auth_strategy = AuthenticationStrategy(
            method=str(auth.get("method", "JWT")).strip(),
            storage=str(auth.get("storage", "httpOnly cookies")).strip(),
            refresh_strategy=(
                auth.get("security_best_practices", ["Token rotation"])[0]
                if auth.get("security_best_practices")
                else "Token rotation"
            ),
            libraries=auth_libraries
        )
        
        # Build database strategy
        db_type = str(db.get("type", "PostgreSQL")).strip()
        db_orm = str(db.get("orm", "Unknown")).strip()
        db_pool = db.get("connection_pool", True)
        db_migration = str(db.get("migration_tool", "N/A")).strip()
        
        db_strategy = DatabaseStrategy(
            type=db_type,
            orm=db_orm,
            connection_pool=db_pool if isinstance(db_pool, bool) else True,
            migration_tool=db_migration
        )
        
        # Build endpoints list
        endpoint_list = endpoints_data.get("endpoints", [])
        if not isinstance(endpoint_list, list):
            endpoint_list = []
        
        api_endpoints = []
        for ep in endpoint_list[:30]:  # Limit to 30
            if isinstance(ep, dict):
                api_endpoints.append(
                    APIEndpoint(
                        method=str(ep.get("method", "GET")).upper(),
                        path=str(ep.get("path", "/")),
                        description=str(ep.get("description", "API endpoint")),
                        auth_required=bool(ep.get("auth_required", False))
                    )
                )
        
        # Build folder structure
        folder_list = folder.get("folders", [])
        if not isinstance(folder_list, list):
            folder_list = []
        
        folder_structures = []
        for f in folder_list:
            if isinstance(f, dict):
                folder_structures.append(
                    FolderStructure(
                        name=str(f.get("name") or f.get("path") or "folder/"),
                        description=str(f.get("description") or f.get("purpose") or "Folder"),
                        children=f.get("children", []) if isinstance(f.get("children"), list) else []
                    )
                )
        
        # Extract dependencies
        core_libs = _normalize_string_list(deps.get("core_libraries", []))
        
        optional_libs = _normalize_optional_libraries(deps.get("optional_libraries", {}))
        
        # Build combined reasoning
        combined_reasoning = (
            f"\n🏗️  ARCHITECTURE: {arch.get('framework', 'Unknown')} "
            f"({arch.get('language', 'Unknown')}) - {arch.get('architecture_pattern', 'Unknown')} pattern\n"
            f"   Reasoning: {arch.get('reasoning', 'N/A')}\n\n"
            f"🔐 AUTHENTICATION: {auth.get('method', 'JWT')}\n"
            f"   Reasoning: {auth.get('reasoning', 'N/A')}\n"
            f"   Best Practices: {', '.join(security_practices[:3])}\n\n"
            f"📡 API DESIGN: {len(api_endpoints)} endpoints (not just CRUD)\n"
            f"   Reasoning: {endpoints_data.get('reasoning', 'N/A')}\n\n"
            f"💾 DATABASE: {db.get('type', 'PostgreSQL')} + {db.get('orm', 'Unknown')}\n"
            f"   Reasoning: {db.get('reasoning', 'N/A')}\n"
            f"   Scaling: {', '.join(_normalize_string_list(db.get('scaling_considerations', []))[:2])}\n\n"
            f"📁 FOLDER STRUCTURE: {folder.get('structure_type', 'modular')}\n"
            f"   Reasoning: {folder.get('reasoning', 'N/A')}\n\n"
            f"📦 DEPENDENCIES: {len(core_libs)} core + {len(optional_libs)} optional\n"
            f"   Reasoning: {deps.get('reasoning', 'N/A')}\n"
        )
        
        # Create final BackendArchitecturePlan
        final_plan = BackendArchitecturePlan(
            status="success",
            framework=arch.get("framework", "Unknown"),
            language=arch.get("language", "Unknown"),
            api_style=arch.get("api_style", "REST"),
            authentication=auth_strategy,
            database=db_strategy,
            suggested_endpoints=api_endpoints,
            folder_structure=folder_structures,
            core_libraries=core_libs,
            optional_libraries=optional_libs,
            design_patterns=[arch.get("architecture_pattern", "Service Layer")],
            clarification_questions=[],
            reasoning=combined_reasoning
        )
        
        logger.info("[MERGE COMPLETE]")

        merged_plan = final_plan.dict()
        logger.info("[PRE-VALIDATION PLAN]\n%s", json.dumps(merged_plan, indent=2, default=str))

        validator = ConsistencyValidator(validation_output)
        logger.info("[CONSISTENCY VALIDATOR STARTED]")
        validated_plan, report = validator.enforce_backend_plan(merged_plan)
        logger.info("[CONFLICTS DETECTED]\n%s", json.dumps(report.get("conflicts_found", []), indent=2, default=str))
        logger.info("[REPLACEMENTS APPLIED]\n%s", json.dumps(report.get("corrections_made", []), indent=2, default=str))
        logger.info("[FINAL CONSISTENCY SCORE] %s", report.get("consistency_score", 0))

        validated_plan["reasoning"] = _build_validated_reasoning(validated_plan, validation_output)

        # Re-check after reasoning synthesis to ensure text remains ecosystem-consistent.
        post_reasoning_report = validator.inspect_backend_plan(validated_plan)
        validated_plan["consistency_score"] = post_reasoning_report.get("consistency_score", report.get("consistency_score", 100))
        validated_plan["conflicts_found"] = post_reasoning_report.get("conflicts_found", [])

        logger.info("[POST-VALIDATION PLAN]\n%s", json.dumps(validated_plan, indent=2, default=str))
        logger.info("[RETURNING VALIDATED PLAN]")

        # Convert to dict
        return BackendArchitecturePlan(**validated_plan).dict()
        
    except Exception as e:
        logger.error(f"Merger failed: {e}", exc_info=True)
        # Return valid error response
        rules = RuleManager.from_validation_output(validation_output)
        framework = rules.framework
        language = rules.language
        if framework == "Node.js":
            auth_libraries = ["jsonwebtoken", "bcrypt"]
            database_orm = "Prisma"
            core_libraries = ["express", "jsonwebtoken", "prisma", "cors", "dotenv", "bcrypt"]
        elif framework == "FastAPI":
            auth_libraries = ["python-jose", "passlib[bcrypt]"]
            database_orm = "SQLAlchemy"
            core_libraries = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "passlib[bcrypt]"]
        else:
            auth_libraries = ["Spring Security", "jjwt-api"]
            database_orm = "Spring Data JPA"
            core_libraries = ["spring-boot-starter-web", "spring-boot-starter-security", "spring-boot-starter-data-jpa"]
        return {
            "status": "error",
            "framework": framework,
            "language": language,
            "api_style": "REST",
            "authentication": {
                "method": "JWT",
                "storage": "httpOnly cookies",
                "refresh_strategy": "Token rotation",
                "libraries": auth_libraries
            },
            "database": {
                "type": "PostgreSQL",
                "orm": database_orm,
                "connection_pool": True,
                "migration_tool": "Alembic"
            },
            "suggested_endpoints": [],
            "folder_structure": [],
            "core_libraries": core_libraries,
            "optional_libraries": {},
            "design_patterns": ["Service Layer"],
            "clarification_questions": [],
            "reasoning": f"❌ ERROR during merge: {str(e)}\n\nPlease check the agent logs above for detailed error information."
        }
