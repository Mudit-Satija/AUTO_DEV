import logging
from typing import Dict
from . import architecture_agent, auth_agent, endpoint_agent, database_agent, folder_structure_agent, dependency_agent
from .merger import merge_agent_results
from planning_agents.shared.domain_intelligence import build_domain_context

logger = logging.getLogger(__name__)


def orchestrate_backend_planning(validation_output: Dict) -> Dict:
    """
    Orchestrate multi-agent backend planning pipeline.
    
    Flow:
    1. Architecture Agent → framework, language, api_style, pattern
    2. Auth Agent → authentication strategy
    3. Endpoint Agent → REST endpoints
    4. Database Agent → database, ORM, caching
    5. Folder Structure Agent → folder layout
    6. Dependency Agent → core and optional libraries
    7. Merger → combines all results into final JSON
    """
    
    logger.info("\n" + "="*60)
    logger.info("STARTING MULTI-AGENT BACKEND PLANNING PIPELINE")
    logger.info("="*60)
    
    try:
        shared_state = dict(validation_output or {})
        shared_state["domain_context"] = build_domain_context(shared_state)

        # Step 1: Architecture Analysis
        logger.info("\n[1/6] Architecture Agent...")
        arch_result = architecture_agent.analyze_architecture(shared_state)
        
        # Step 2: Authentication Analysis
        logger.info("\n[2/6] Authentication Agent...")
        auth_result = auth_agent.analyze_authentication(shared_state)
        
        # Step 3: Endpoint Design
        logger.info("\n[3/6] Endpoint Agent...")
        endpoint_result = endpoint_agent.analyze_endpoints(shared_state)
        
        # Step 4: Database Analysis
        logger.info("\n[4/6] Database Agent...")
        db_result = database_agent.analyze_database(shared_state)
        
        # Step 5: Folder Structure
        logger.info("\n[5/6] Folder Structure Agent...")
        folder_result = folder_structure_agent.analyze_folder_structure(shared_state, arch_result)
        
        # Step 6: Dependencies
        logger.info("\n[6/6] Dependency Agent...")
        dep_result = dependency_agent.analyze_dependencies(shared_state, arch_result, db_result)
        
        # Collect all results
        all_results = {
            "architecture": arch_result,
            "authentication": auth_result,
            "endpoints": endpoint_result,
            "database": db_result,
            "folder_structure": folder_result,
            "dependencies": dep_result,
        }
        
        logger.info("\n" + "="*60)
        logger.info("ALL AGENTS COMPLETE - MERGING RESULTS...")
        logger.info("="*60)
        
        # Merge all results into final output
        final_result = merge_agent_results(all_results, shared_state)
        
        logger.info("\n" + "="*60)
        logger.info("✓ PIPELINE COMPLETE - RETURNING FINAL ARCHITECTURE PLAN")
        logger.info("="*60 + "\n")
        
        return final_result
        
    except Exception as e:
        logger.error(f"✗ Pipeline failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "framework": "Unknown",
            "language": "Unknown",
            "api_style": "REST",
            "reasoning": "Pipeline execution failed"
        }
