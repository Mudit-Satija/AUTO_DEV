"""Minimal deterministic orchestrator test."""

import backend_agents.architecture_agent as architecture_agent
import backend_agents.auth_agent as auth_agent
import backend_agents.database_agent as database_agent
import backend_agents.dependency_agent as dependency_agent
import backend_agents.endpoint_agent as endpoint_agent
import backend_agents.folder_structure_agent as folder_structure_agent
from backend_agents.orchestrator import orchestrate_backend_planning
from backend_schemas import BackendArchitecturePlan


def _arch_stub(_validation_output):
    return {
        "framework": "Node.js",
        "language": "JavaScript",
        "api_style": "REST",
        "pattern": "Monolith",
    }


def _auth_stub(_validation_output):
    return {
        "method": "JWT",
        "storage": "httpOnly cookies",
        "libraries": ["jsonwebtoken"],
        "recommendations": ["Use refresh-token rotation"],
    }


def _endpoint_stub(_validation_output):
    return {
        "endpoints": [
            {
                "method": "POST",
                "path": "/api/todos",
                "description": "Create todo",
                "auth_required": True,
            }
        ]
    }


def _db_stub(_validation_output):
    return {
        "type": "PostgreSQL",
        "orm": "prisma",
        "migration_tool": "prisma migrate",
    }


def _folder_stub(_validation_output, _arch):
    return {
        "folders": [
            {"name": "src/", "description": "Source code", "children": []},
            {"name": "tests/", "description": "Automated tests", "children": []},
        ]
    }


def _dependency_stub(_validation_output, _arch, _db):
    return {
        "core": ["express", "jsonwebtoken", "prisma", "cors", "dotenv", "bcrypt"],
        "optional": {},
    }


def test_minimal_orchestrator(monkeypatch):
    monkeypatch.setattr(architecture_agent, "analyze_architecture", _arch_stub)
    monkeypatch.setattr(auth_agent, "analyze_authentication", _auth_stub)
    monkeypatch.setattr(endpoint_agent, "analyze_endpoints", _endpoint_stub)
    monkeypatch.setattr(database_agent, "analyze_database", _db_stub)
    monkeypatch.setattr(folder_structure_agent, "analyze_folder_structure", _folder_stub)
    monkeypatch.setattr(dependency_agent, "analyze_dependencies", _dependency_stub)

    validation_output = {
        "project_type": "web app",
        "user_stack": {
            "backend": "Node.js",
            "database": "PostgreSQL",
        },
        "feedback": "Build a todo app",
    }

    result = orchestrate_backend_planning(validation_output)

    assert result["status"] == "success"
    assert isinstance(result, dict)
    assert isinstance(result.get("authentication"), dict)
    assert isinstance(result.get("database"), dict)

    plan = BackendArchitecturePlan(**result)
    assert plan.framework == "Node.js"
