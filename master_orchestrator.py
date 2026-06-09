"""Master orchestrator that runs backend and frontend planning in parallel.

No hardcoded auth assumptions.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict

from backend_agents.planning_agent import plan_backend
from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules
from frontend_agents.orchestrator import orchestrate_frontend_planning
from master_merger import merge_backend_and_frontend

logger = logging.getLogger(__name__)


async def orchestrate_full_architecture(validation_output: Dict[str, Any]) -> Dict[str, Any]:
    request_start = time.perf_counter()
    shared_state = dict(validation_output or {})

    logger.info("=" * 80)
    logger.info("MASTER ORCHESTRATOR STARTING PARALLEL FULL ARCHITECTURE PLANNING")
    logger.info("=" * 80)

    backend_coro = asyncio.wait_for(
        asyncio.to_thread(plan_backend, validation_output=shared_state),
        timeout=90,
    )
    frontend_coro = asyncio.wait_for(
        orchestrate_frontend_planning(shared_state),
        timeout=90,
    )

    backend_start = time.perf_counter()
    frontend_start = time.perf_counter()

    async def _timed(coro, started_at):
        try:
            result = await coro
        except Exception as exc:
            result = exc
        return result, int((time.perf_counter() - started_at) * 1000)

    (backend_result, backend_total_ms), (frontend_result, frontend_total_ms) = await asyncio.gather(
        _timed(backend_coro, backend_start),
        _timed(frontend_coro, frontend_start),
    )

    backend_payload = _normalize_result("backend", backend_result)
    frontend_payload = _normalize_result("frontend", frontend_result)

    backend_perf = backend_payload.pop("_perf", {}) if isinstance(backend_payload, dict) else {}
    frontend_perf = frontend_payload.pop("_perf", {}) if isinstance(frontend_payload, dict) else {}

    merge_start = time.perf_counter()
    final_architecture = merge_backend_and_frontend(
        backend_payload,
        frontend_payload,
        shared_state,
    )
    merge_time_ms = int((time.perf_counter() - merge_start) * 1000)

    if final_architecture.get("status") == "success":
        project_rules = build_project_rules(final_architecture)
        build_plan = generate_build_plan(project_rules)
        final_architecture["project_rules"] = project_rules
        final_architecture["build_plan"] = build_plan

    total_request_ms = int((time.perf_counter() - request_start) * 1000)

    logger.info("[PERF] Backend: %dms, Frontend: %dms, Merge: %dms, Total: %dms",
                backend_total_ms, frontend_total_ms, merge_time_ms, total_request_ms)

    return final_architecture


def _normalize_result(label: str, result: Any) -> Dict[str, Any]:
    if isinstance(result, Exception):
        logger.error("%s pipeline failed: %s", label.capitalize(), result, exc_info=True)
        return {"status": "error", "error": str(result), "reasoning": f"{label.capitalize()} pipeline failed"}
    if isinstance(result, dict):
        return result
    logger.error("%s pipeline returned unexpected type: %s", label.capitalize(), type(result).__name__)
    return {"status": "error", "error": f"Unexpected {label} result type: {type(result).__name__}"}
