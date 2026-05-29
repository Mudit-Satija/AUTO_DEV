import asyncio
import logging
from typing import Dict, Any
from orchestrator_parallel import orchestrate_backend_planning

logger = logging.getLogger(__name__)

# Backend planning now uses multi-agent pipeline for faster processing


def plan_backend(validation_output: dict = None, project_type: str = None, user_stack: dict = None, additional_context: str = None) -> Dict[str, Any]:
    """Generate backend architecture plan using PARALLEL multi-agent pipeline
    
    This function runs 6 agents IN PARALLEL (async/concurrent):
    - architecture_agent
    - auth_agent
    - endpoint_agent
    - database_agent
    - folder_structure_agent
    - dependency_agent
    
    All agents run concurrently with intelligent rules/constraints.
    Expected time: 30-45 seconds (not 3-5 minutes!)
    
    Args:
        validation_output: Output from validation agent (preferred) or dict with project_type, user_stack, feedback
        project_type: Project type if not using validation_output
        user_stack: User's tech stack if not using validation_output
        additional_context: Additional context for planning
    
    Returns:
        dict: BackendArchitecturePlan JSON
    """
    
    try:
        # Use validation_output if provided, otherwise build from individual params
        if validation_output:
            input_data = validation_output
        else:
            input_data = {
                "project_type": project_type or "web app",
                "user_stack": user_stack or {},
                "feedback": additional_context or ""
            }
        
        # Ensure input_data is a dict
        if not isinstance(input_data, dict):
            logger.error(f"validation_output is not a dict: {type(input_data)}")
            input_data = {
                "project_type": "web app",
                "user_stack": {},
                "feedback": ""
            }
        
        logger.info(f"Backend Planning: Starting PARALLEL multi-agent pipeline for {input_data.get('project_type')}")
        logger.info("Running 6 agents concurrently (async) - Expected time: 30-45 seconds")
        
        # Run orchestrator (which is async)
        # Create a new event loop or use existing one
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(orchestrate_backend_planning(input_data))
            loop.close()
        else:
            # Running loop exists, use run_coroutine_threadsafe
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    orchestrate_backend_planning(input_data)
                )
                result = future.result(timeout=300)  # 5 min timeout
        
        logger.info("Backend Planning: Parallel pipeline complete")
        return result
        
    except Exception as e:
        logger.error(f"Backend planning error: {e}", exc_info=True)
        return error_response(f"Planning failed: {str(e)}")


def error_response(feedback: str) -> Dict[str, Any]:
    """Return error response"""
    return {
        "status": "error",
        "framework": "Unknown",
        "language": "Unknown",
        "api_style": "REST",
        "reasoning": feedback
    }
