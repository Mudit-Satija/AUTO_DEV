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
import time
from .layout_agent import layout_agent, _default_layout
from .component_agent import component_agent, _default_components
from .styling_agent import styling_agent, _default_styling
from .navigation_agent import navigation_agent, _default_navigation
from .animation_agent import animation_agent, _default_animations
from .accessibility_agent import accessibility_agent, _default_accessibility
from . import reliability
from planning_agents.shared.domain_intelligence import build_domain_context

logger = logging.getLogger(__name__)


def _output_metrics(payload):
    serialized = str(payload)
    return {
        "output_character_count": len(serialized),
        "output_word_count": len(serialized.split()),
    }


async def _run_profiled_agent(agent_name: str, coro_func, required_fields, fallback_func):
    start = time.perf_counter()
    # Use reliability wrapper which handles retries, validation and fallback
    result = await reliability.call_with_retries(coro_func, agent_name, required_fields, fallback_func)
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    metrics = _output_metrics(result)
    logger.info(
        "[PERF]\n%s: %d ms\nOutput Size: %d chars\nOutput Words: %d",
        agent_name,
        elapsed_ms,
        metrics["output_character_count"],
        metrics["output_word_count"],
    )
    return result, {
        "agent": agent_name,
        "execution_time_ms": elapsed_ms,
        **metrics,
    }


async def orchestrate_frontend_planning(validation_output: dict) -> dict:
    """Run all 6 frontend agents in parallel.

    Args:
        validation_output: ValidationOutput with project requirements

    Returns:
        Merged frontend architecture plan
    """
    request_start = time.perf_counter()
    shared_state = dict(validation_output or {})
    shared_state["domain_context"] = build_domain_context(shared_state)

    logger.info("=" * 60)
    logger.info("🎨 FRONTEND ORCHESTRATOR STARTING (PARALLEL MODE)")
    logger.info("=" * 60)

    try:
        # Run all agents concurrently (not sequentially)
        logger.info("🚀 Launching 6 frontend agents in parallel...")

        results = await asyncio.wait_for(
            asyncio.gather(
                _run_profiled_agent(
                    "Layout Agent",
                    lambda: layout_agent(shared_state),
                    ("layout_type", "structure", "routing_structure"),
                    lambda: _default_layout(shared_state.get("complexity", "intermediate")),
                ),
                _run_profiled_agent(
                    "Component Agent",
                    lambda: component_agent(shared_state),
                    ("components", "total_components"),
                    lambda: _default_components(shared_state.get("complexity", "intermediate")),
                ),
                _run_profiled_agent(
                    "Styling Agent",
                    lambda: styling_agent(shared_state),
                    ("styling_approach", "design_system"),
                    lambda: _default_styling(shared_state.get("complexity", "intermediate")),
                ),
                _run_profiled_agent(
                    "Navigation Agent",
                    lambda: navigation_agent(shared_state),
                    ("navigation_menu", "routing_structure"),
                    lambda: _default_navigation(shared_state.get("complexity", "intermediate")),
                ),
                _run_profiled_agent(
                    "Animation Agent",
                    lambda: animation_agent(shared_state),
                    ("animations",),
                    lambda: _default_animations(shared_state.get("complexity", "intermediate")),
                ),
                _run_profiled_agent(
                    "Accessibility Agent",
                    lambda: accessibility_agent(shared_state),
                    ("wcag_level", "requirements"),
                    lambda: _default_accessibility(),
                ),
            ),
            timeout=75,
        )

        (layout, layout_perf), (components, component_perf), (styling, styling_perf), (navigation, navigation_perf), (animation, animation_perf), (accessibility, accessibility_perf) = results
        frontend_perf = [layout_perf, component_perf, styling_perf, navigation_perf, animation_perf, accessibility_perf]

        logger.info("✅ All 6 agents completed successfully")

        # Import merger and combine results
        from .merger import merge_agent_results
        merge_start = time.perf_counter()
        final = merge_agent_results(layout, components, styling, navigation, animation, accessibility)
        merge_time_ms = int((time.perf_counter() - merge_start) * 1000)
        pipeline_total_ms = int((time.perf_counter() - request_start) * 1000)

        logger.info("[PERF]\nFrontend Merge Time: %d ms", merge_time_ms)
        logger.info("[PERF]\nFrontend Pipeline Total: %d ms", pipeline_total_ms)
        logger.info("=========================\nPERFORMANCE SUMMARY\n=========================")
        logger.info("Frontend:")
        for item in frontend_perf:
            logger.info("- %s: %.2fs", item["agent"], item["execution_time_ms"] / 1000)
        logger.info("Merge: %.2fs", merge_time_ms / 1000)
        logger.info("TOTAL: %.2fs", pipeline_total_ms / 1000)

        if isinstance(final, dict):
            final["_perf"] = {
                "pipeline_total_ms": pipeline_total_ms,
                "merge_time_ms": merge_time_ms,
                "agents": frontend_perf,
            }
        
        logger.info("=" * 60)
        logger.info("✨ FRONTEND ARCHITECTURE PLAN COMPLETE")
        logger.info("=" * 60)
        
        return final
        
    except asyncio.TimeoutError as e:
        logger.error(f"❌ Frontend planning timed out: {e}")
        return {
            "status": "error",
            "error": "Frontend planning agents timed out (75s limit)",
            "agents_completed": 0
        }
    except Exception as e:
        logger.error(f"❌ Frontend orchestration failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Frontend orchestration failed: {str(e)}"
        }
