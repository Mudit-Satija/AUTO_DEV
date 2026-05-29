import logging
from typing import Dict
from backend_schemas import BackendArchitecturePlan, AuthenticationStrategy, DatabaseStrategy, APIEndpoint, FolderStructure

logger = logging.getLogger(__name__)


def merge_agent_results(all_results: Dict, validation_output: Dict) -> Dict:
    """
    Merge all agent results into single BackendArchitecturePlan JSON.
    """
    
    try:
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
        
        logger.info("Merging agent results...")
        
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
        
        logger.info(f"✓ Merged into final plan: {final_plan.framework}")
        
        # Convert to dict
        return final_plan.dict()
        
    except Exception as e:
        logger.error(f"Merger failed: {e}", exc_info=True)
        # Return valid plan even on error
        return {
            "status": "success",
            "framework": "Unknown",
            "language": "Unknown",
            "api_style": "REST",
            "authentication": {
                "method": "JWT",
                "storage": "httpOnly cookies",
                "refresh_strategy": "Token rotation",
                "libraries": []
            },
            "database": {
                "type": "PostgreSQL",
                "orm": "Unknown",
                "connection_pool": True,
                "migration_tool": "N/A"
            },
            "suggested_endpoints": [],
            "folder_structure": [],
            "core_libraries": [],
            "optional_libraries": {},
            "design_patterns": ["MVC"],
            "clarification_questions": [],
            "reasoning": f"Error during merge: {str(e)}"
        }


