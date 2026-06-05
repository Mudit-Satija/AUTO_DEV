import json
import logging
from typing import Dict
from backend_schemas import BackendArchitecturePlan, AuthenticationStrategy, DatabaseStrategy, APIEndpoint, FolderStructure
from planning_agents.shared.rules import RuleManager
from planning_agents.shared.consistency_validator import ConsistencyValidator
from planning_agents.shared.domain_intelligence import build_domain_context

logger = logging.getLogger(__name__)


def merge_agent_results(all_results: Dict, validation_output: Dict) -> Dict:
    """
    Merge all agent results into single BackendArchitecturePlan JSON.
    """
    
    try:
        rules = RuleManager.from_validation_output(validation_output)
        domain_context = build_domain_context(validation_output)
        validator = ConsistencyValidator(validation_output)

        # Safely extract each result, ensuring they're dicts
        arch = all_results.get("architecture", {})
        if not isinstance(arch, dict):
            logger.warning(f"Architecture result is not dict: {type(arch)}")
            arch = {}
        
        auth = all_results.get("authentication", {})
        if not isinstance(auth, dict):
            logger.warning(f"Auth result is not dict: {type(auth)}")
            auth = {}
        
        endpoints = all_results.get("endpoints", {})
        if not isinstance(endpoints, dict):
            logger.warning(f"Endpoints result is not dict: {type(endpoints)}")
            endpoints = {}
        
        db = all_results.get("database", {})
        if not isinstance(db, dict):
            logger.warning(f"Database result is not dict: {type(db)}")
            db = {}
        
        folders = all_results.get("folder_structure", {})
        if not isinstance(folders, dict):
            logger.warning(f"Folders result is not dict: {type(folders)}")
            folders = {}
        
        deps = all_results.get("dependencies", {})
        if not isinstance(deps, dict):
            logger.warning(f"Dependencies result is not dict: {type(deps)}")
            deps = {}
        
        logger.info("Merging agent results... domain=%s", domain_context.get("domain"))
        
        # Build authentication strategy with defaults
        auth_strategy = AuthenticationStrategy(
            method=auth.get("method", "JWT") if isinstance(auth.get("method"), str) else "JWT",
            storage=auth.get("storage", "httpOnly cookies") if isinstance(auth.get("storage"), str) else "httpOnly cookies",
            refresh_strategy=auth.get("recommendations", ["Implement token rotation"])[0] if auth.get("recommendations") else "Token rotation",
            libraries=auth.get("libraries", []) if isinstance(auth.get("libraries"), list) else []
        )
        
        # Build database strategy with defaults
        db_strategy = DatabaseStrategy(
            type=db.get("type", "PostgreSQL") if isinstance(db.get("type"), str) else "PostgreSQL",
            orm=db.get("orm", "Unknown") if isinstance(db.get("orm"), str) else "Unknown",
            connection_pool=True,
            migration_tool=db.get("migration_tool", "N/A") if isinstance(db.get("migration_tool"), str) else "N/A"
        )
        
        # Build endpoints from agent output
        endpoint_list = endpoints.get("endpoints", []) if isinstance(endpoints, dict) else []
        if not isinstance(endpoint_list, list):
            endpoint_list = []
        
        api_endpoints = []
        for ep in endpoint_list[:10]:
            if isinstance(ep, dict):
                api_endpoints.append(
                    APIEndpoint(
                        method=ep.get("method", "GET"),
                        path=ep.get("path", "/"),
                        description=ep.get("description", "API endpoint"),
                        auth_required=ep.get("auth_required", False)
                    )
                )
        
        # Build folder structure
        folder_list = folders.get("folders", []) if isinstance(folders, dict) else []
        if not isinstance(folder_list, list):
            folder_list = []
        
        folder_structures = []
        for f in folder_list:
            if isinstance(f, dict):
                folder_structures.append(
                    FolderStructure(
                        name=f.get("name", "folder/"),
                        description=f.get("description", "Folder"),
                        children=[]
                    )
                )
        
        # Combine reasoning from all agents
        core_libs = deps.get('core', []) if isinstance(deps.get('core'), list) else []
        combined_reasoning = (
            f"Architecture: {arch.get('framework', 'Unknown')} ({arch.get('language', 'Unknown')}). "
            f"Authentication: {auth.get('method', 'JWT')}. "
            f"Database: {db.get('type', 'PostgreSQL')} with {db.get('orm', 'Unknown')}. "
            f"Endpoints: {len(api_endpoints)} REST endpoints. "
            f"Core dependencies: {', '.join(core_libs[:3]) if core_libs else 'None specified'}."
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
            optional_libraries=deps.get("optional", {}) if isinstance(deps.get("optional"), dict) else {},
            design_patterns=["MVC", arch.get("pattern", "Monolith")],
            clarification_questions=[],
            reasoning=combined_reasoning
        )

        pre_validation_plan = final_plan.dict()
        logger.info("[PRE-VALIDATION PLAN]\n%s", json.dumps(pre_validation_plan, indent=2, default=str))
        logger.info("BACKEND PLANNING PATH: Validation -> ProjectState -> Rules Engine -> Backend Planner -> Consistency Validator -> Final Output")
        logger.info("CONSISTENCY VALIDATOR STARTED")
        sanitized_plan, report = validator.enforce_backend_plan(pre_validation_plan)
        logger.info("[CONFLICT DETECTED]\n%s", json.dumps(report.get("conflicts_found", []), indent=2, default=str))
        logger.info("[REPLACEMENT]\n%s", json.dumps(report.get("corrections_made", []), indent=2, default=str))
        logger.info("Consistency Score: %s", report.get("consistency_score", 0))
        logger.info("[POST-VALIDATION PLAN]\n%s", json.dumps(sanitized_plan, indent=2, default=str))
        if not report.get("is_valid", False):
            logger.error(
                "Consistency validation failed: %s",
                "; ".join(report.get("conflicts_found", [])) or "unknown conflicts",
            )
            return {
                "status": "error",
                "reasoning": "Consistency validation failed: " + "; ".join(report.get("conflicts_found", [])),
                "consistency_score": report.get("consistency_score", 0),
                "conflicts_found": report.get("conflicts_found", []),
            }

        sanitized_plan["consistency_score"] = report.get("consistency_score", 100)
        sanitized_plan["conflicts_found"] = report.get("conflicts_found", [])
        final_plan = BackendArchitecturePlan(**sanitized_plan)
        
        logger.info(f"✓ Merged into final plan: {final_plan.framework}")
        
        # Convert to dict
        return final_plan.dict()
        
    except Exception as e:
        logger.error(f"Merger failed: {e}", exc_info=True)
        # Return valid plan even on error
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
            "status": "success",
            "framework": framework,
            "language": language,
            "api_style": "REST",
            "authentication": {
                "method": "JWT",
                "storage": "httpOnly cookies",
                "refresh_strategy": "Token rotation",
                "libraries": auth_libraries,
            },
            "database": {
                "type": "PostgreSQL",
                "orm": database_orm,
                "connection_pool": True,
                "migration_tool": "N/A"
            },
            "suggested_endpoints": [],
            "folder_structure": [],
            "core_libraries": core_libraries,
            "optional_libraries": {},
            "design_patterns": ["MVC"],
            "clarification_questions": [],
            "reasoning": f"Error during merge: {str(e)}"
        }


