import logging
from typing import Dict, List
from pydantic import BaseModel
from backend_schemas import BackendArchitecturePlan, AuthenticationStrategy, DatabaseStrategy, APIEndpoint, FolderStructure

logger = logging.getLogger(__name__)


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
        auth_libraries = auth.get("libraries", [])
        if not isinstance(auth_libraries, list):
            auth_libraries = []
        
        security_practices = auth.get("security_best_practices", [])
        if not isinstance(security_practices, list):
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
                        name=str(f.get("name", "folder/")),
                        description=str(f.get("description", "Folder")),
                        children=f.get("children", []) if isinstance(f.get("children"), list) else []
                    )
                )
        
        # Extract dependencies
        core_libs = deps.get("core_libraries", [])
        if not isinstance(core_libs, list):
            core_libs = []
        
        optional_libs = deps.get("optional_libraries", {})
        if not isinstance(optional_libs, dict):
            optional_libs = {}
        
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
            f"   Scaling: {', '.join(db.get('scaling_considerations', [])[:2])}\n\n"
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
        
        logger.info(f"✅ Merged into final plan: {final_plan.framework}")
        
        # Convert to dict
        return final_plan.dict()
        
    except Exception as e:
        logger.error(f"Merger failed: {e}", exc_info=True)
        # Return valid error response
        return {
            "status": "error",
            "framework": "FastAPI",
            "language": "Python",
            "api_style": "REST",
            "authentication": {
                "method": "JWT",
                "storage": "httpOnly cookies",
                "refresh_strategy": "Token rotation",
                "libraries": ["python-jose", "bcryptjs"]
            },
            "database": {
                "type": "PostgreSQL",
                "orm": "SQLAlchemy",
                "connection_pool": True,
                "migration_tool": "Alembic"
            },
            "suggested_endpoints": [],
            "folder_structure": [],
            "core_libraries": [],
            "optional_libraries": {},
            "design_patterns": ["Service Layer"],
            "clarification_questions": [],
            "reasoning": f"❌ ERROR during merge: {str(e)}\n\nPlease check the agent logs above for detailed error information."
        }
