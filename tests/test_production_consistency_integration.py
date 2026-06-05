import asyncio
import logging

import pytest

import backend_agents.orchestrator_parallel as orchestrator_parallel


async def _architecture_stub(shared_state):
    return {
        "framework": "Spring Boot",
        "language": "Java",
        "api_style": "REST",
        "architecture_pattern": "Monolith",
        "reasoning": "Spring Boot for enterprise backend",
    }


async def _auth_stub(shared_state):
    return {
        "method": "JWT",
        "storage": "httpOnly cookies",
        "libraries": ["Spring Security", "express-jwt"],
        "security_best_practices": ["Use HTTPS"],
        "reasoning": "JWT security for Spring",
    }


async def _endpoint_stub(shared_state):
    return {
        "endpoints": [
            {"method": "POST", "path": "/api/auth/register", "description": "Register user", "auth_required": False},
            {"method": "POST", "path": "/api/auth/login", "description": "Login user", "auth_required": False},
        ],
        "total_count": 2,
    }


async def _database_stub(shared_state):
    return {
        "type": "MongoDB",
        "orm": "Mongoose",
        "cache": "None",
        "migration_tool": "N/A",
        "reasoning": "Mongoose for MongoDB",
    }


async def _folder_stub(shared_state):
    return {
        "folders": [
            {"name": "src/", "description": "Source code", "children": []},
            {"name": "config/", "description": "Config files", "children": []},
        ],
        "structure_type": "modular",
        "reasoning": "Standard modular structure",
    }


async def _dependency_stub(shared_state, architecture_data):
    return {
        "core_libraries": ["express", "http-server", "winston", "mongoose", "pg"],
        "optional_libraries": {"joi": "validation"},
        "total_core": 5,
        "total_optional": 1,
        "reasoning": "Node dependencies were suggested",
    }


def test_production_path_routes_through_validator_and_returns_validated_plan(monkeypatch, caplog):
    monkeypatch.setattr(orchestrator_parallel, "architecture_agent", _architecture_stub)
    monkeypatch.setattr(orchestrator_parallel, "auth_agent", _auth_stub)
    monkeypatch.setattr(orchestrator_parallel, "endpoint_agent", _endpoint_stub)
    monkeypatch.setattr(orchestrator_parallel, "database_agent", _database_stub)
    monkeypatch.setattr(orchestrator_parallel, "folder_structure_agent", _folder_stub)
    monkeypatch.setattr(orchestrator_parallel, "dependency_agent", _dependency_stub)

    caplog.set_level(logging.INFO)
    validation_output = {
        "project_type": "web app",
        "complexity": "intermediate",
        "user_stack": {"backend": "Spring Boot", "database": "MongoDB"},
    }

    result = asyncio.run(orchestrator_parallel.orchestrate_backend_planning(validation_output))

    assert result["status"] == "success"
    assert result["framework"] == "Spring Boot"
    assert result["language"] == "Java"
    assert "CONSISTENCY VALIDATOR STARTED" in caplog.text
    assert "[MERGE COMPLETE]" in caplog.text
    assert "[RETURNING VALIDATED PLAN]" in caplog.text

    result_text = str(result).lower()
    assert "express" not in result_text
    assert "http-server" not in result_text
    assert "winston" not in result_text
    assert "express-jwt" not in result_text
    assert "mongoose" not in result_text
    assert result.get("reasoning") != "Validated backend plan"
    assert "spring" in result.get("reasoning", "").lower()
