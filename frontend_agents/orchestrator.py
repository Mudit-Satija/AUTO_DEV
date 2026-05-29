"""Compatibility wrapper for the existing frontend orchestrator.

The master orchestrator imports frontend_agents.orchestrator to match the
requested architecture, while the actual implementation continues to live in
frontend_orchestrator.py.
"""

from frontend_orchestrator import orchestrate_frontend_planning as _orchestrate_frontend_planning


async def orchestrate_frontend_planning(validation_output: dict) -> dict:
    return await _orchestrate_frontend_planning(validation_output)
