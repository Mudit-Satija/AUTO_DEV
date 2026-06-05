import asyncio
import pytest

from frontend_agents.planner import orchestrate_frontend_planning
from frontend_agents import reliability


def test_malformed_json_fallback(monkeypatch):
    # layout_agent returns malformed (string) -> should trigger fallback
    async def fake_layout(shared_state):
        return "not a json"

    monkeypatch.setattr("frontend_agents.planner.layout_agent", fake_layout)

    res = asyncio.run(orchestrate_frontend_planning({"project_type": "web app", "complexity": "intermediate", "user_stack": {"frontend": "React"}}))
    assert res.get("status") == "success"
    metrics = reliability.get_metrics()
    assert metrics["agent_fallbacks"].get("Layout Agent", 0) >= 1


def test_missing_fields_triggers_fallback(monkeypatch):
    # component_agent returns dict missing required fields
    async def bad_component(shared_state):
        return {"total_components": 0}

    monkeypatch.setattr("frontend_agents.planner.component_agent", bad_component)

    res = asyncio.run(orchestrate_frontend_planning({"project_type": "web app", "complexity": "intermediate", "user_stack": {"frontend": "React"}}))
    assert res.get("status") == "success"
    metrics = reliability.get_metrics()
    assert metrics["agent_fallbacks"].get("Component Agent", 0) >= 1


def test_agent_crash_uses_fallback(monkeypatch):
    async def crash_animation(shared_state):
        raise RuntimeError("boom")

    monkeypatch.setattr("frontend_agents.planner.animation_agent", crash_animation)

    res = asyncio.run(orchestrate_frontend_planning({"project_type": "web app", "complexity": "intermediate", "user_stack": {"frontend": "React"}}))
    assert res.get("status") == "success"
    metrics = reliability.get_metrics()
    assert metrics["agent_fallbacks"].get("Animation Agent", 0) >= 1
