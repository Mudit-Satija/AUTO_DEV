"""Orchestrator for parallel frontend planning agents.

Coordinates 6 frontend agents to run concurrently using asyncio.gather():
- layout_agent
- component_agent
- styling_agent
- navigation_agent
- animation_agent
- accessibility_agent

All agents receive shared ProjectState and return merged result.
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layout_agent import layout_agent
from component_agent import component_agent
from styling_agent import styling_agent
from navigation_agent import navigation_agent
from animation_agent import animation_agent
from accessibility_agent import accessibility_agent

logger = logging.getLogger(__name__)


async def orchestrate_frontend_planning(validation_output: dict) -> dict:
    """Run all 6 frontend agents in parallel.
    
    Args:
        validation_output: ValidationOutput with project requirements
        
    Returns:
        Merged frontend architecture plan
    """
    shared_state = validation_output
    
    logger.info("=" * 60)
    logger.info("🎨 FRONTEND ORCHESTRATOR STARTING (PARALLEL MODE)")
    logger.info("=" * 60)
    
    try:
        # Run all agents concurrently (not sequentially)
        logger.info("🚀 Launching 6 frontend agents in parallel...")

        results = await asyncio.wait_for(
            asyncio.gather(
                layout_agent(shared_state),
                component_agent(shared_state),
                styling_agent(shared_state),
                navigation_agent(shared_state),
                animation_agent(shared_state),
                accessibility_agent(shared_state),
            ),
            timeout=120,  # 2 minute timeout for the whole frontend pipeline
        )
        
        layout, components, styling, navigation, animation, accessibility = results
        
        logger.info("✅ All 6 agents completed successfully")
        
        # Import merger and combine results
        from frontend_merger import merge_agent_results
        final = merge_agent_results(
            layout, components, styling, navigation, animation, accessibility
        )
        
        logger.info("=" * 60)
        logger.info("✨ FRONTEND ARCHITECTURE PLAN COMPLETE")
        logger.info("=" * 60)
        
        return final
        
    except asyncio.TimeoutError as e:
        logger.error(f"❌ Frontend planning timed out: {e}")
        return {
            "status": "error",
            "error": "Frontend planning agents timed out (120s limit)",
            "agents_completed": 0
        }
    except Exception as e:
        logger.error(f"❌ Frontend orchestration failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Frontend orchestration failed: {str(e)}"
        }
