"""Master orchestrator that runs backend and frontend planning in parallel."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from backend_agents.orchestrator import orchestrate_backend_planning
from frontend_agents.orchestrator import orchestrate_frontend_planning
from master_merger import merge_backend_and_frontend

logger = logging.getLogger(__name__)


async def orchestrate_full_architecture(validation_output: Dict[str, Any]) -> Dict[str, Any]:
    """Run backend and frontend planning pipelines at the same time.

    The backend pipeline is synchronous, so it is executed in a worker thread.
    The frontend pipeline is already async.
    """

    shared_state = dict(validation_output or {})

    logger.info("=" * 80)
    logger.info("MASTER ORCHESTRATOR STARTING PARALLEL FULL ARCHITECTURE PLANNING")
    logger.info("Validation keys: %s", list(shared_state.keys()))
    logger.info("=" * 80)

    backend_coro = asyncio.wait_for(
        asyncio.to_thread(orchestrate_backend_planning, shared_state),
        timeout=180,
    )
    frontend_coro = asyncio.wait_for(
        orchestrate_frontend_planning(shared_state),
        timeout=180,
    )

    backend_result, frontend_result = await asyncio.gather(
        backend_coro,
        frontend_coro,
        return_exceptions=True,
    )

    backend_payload = _normalize_result("backend", backend_result)
    frontend_payload = _normalize_result("frontend", frontend_result)

    logger.info("Backend result status: %s", backend_payload.get("status"))
    logger.info("Frontend result status: %s", frontend_payload.get("status"))

    final_architecture = merge_backend_and_frontend(
        backend_payload,
        frontend_payload,
        shared_state,
    )

    logger.info("Master orchestration complete: %s", final_architecture.get("status"))
    return final_architecture


def _normalize_result(label: str, result: Any) -> Dict[str, Any]:
    if isinstance(result, Exception):
        logger.error("%s pipeline failed: %s", label.capitalize(), result, exc_info=True)
        return {
            "status": "error",
            "error": str(result),
            "reasoning": f"{label.capitalize()} pipeline failed",
        }

    if isinstance(result, dict):
        return result

    logger.error("%s pipeline returned unexpected type: %s", label.capitalize(), type(result).__name__)
    return {
        "status": "error",
        "error": f"Unexpected {label} result type: {type(result).__name__}",
        "reasoning": f"{label.capitalize()} pipeline returned an invalid result type",
    }
