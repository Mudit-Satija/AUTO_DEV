"""Public frontend planning entrypoint."""

from .planner import orchestrate_frontend_planning as _orchestrate_frontend_planning


async def orchestrate_frontend_planning(validation_output: dict) -> dict:
    return await _orchestrate_frontend_planning(validation_output)
