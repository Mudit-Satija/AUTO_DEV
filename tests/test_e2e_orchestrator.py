"""End-to-end shape test for backend orchestration."""

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
        "pattern": "MVC",
    }


def _auth_stub(_validation_output):
    return {
        "method": "JWT",
        "storage": "httpOnly cookies",
        "libraries": ["jsonwebtoken"],
        "recommendations": ["Rotate refresh tokens"],
    }


def _endpoint_stub(_validation_output):
    return {
        "endpoints": [
            {
                "method": "POST",
                "path": "/api/auth/login",
                "description": "Login",
                "auth_required": False,
            },
            {
                "method": "GET",
                "path": "/api/todos",
                "description": "List todos",
                "auth_required": True,
            },
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
            {"name": "src/", "description": "Application source", "children": []},
            {"name": "prisma/", "description": "Schema and migrations", "children": []},
        ]
    }


def _dependency_stub(_validation_output, _arch, _db):
    return {
        "core": ["express", "jsonwebtoken", "prisma", "cors", "dotenv", "bcrypt"],
        "optional": {"helmet": "security headers"},
    }


def test_backend_orchestrator_returns_valid_plan_shape(monkeypatch):
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
            "frontend": "React",
        },
        "feedback": "Building a collaborative todo app with real-time sync",
        "alignment_score": 90,
        "complexity": "medium",
    }

    result = orchestrate_backend_planning(validation_output)

    required_fields = [
        "status",
        "framework",
        "language",
        "api_style",
        "authentication",
        "database",
        "suggested_endpoints",
        "folder_structure",
        "core_libraries",
        "optional_libraries",
        "design_patterns",
        "clarification_questions",
        "reasoning",
    ]
    for field in required_fields:
        assert field in result

    assert isinstance(result["authentication"], dict)
    assert isinstance(result["database"], dict)

    BackendArchitecturePlan(**result)
