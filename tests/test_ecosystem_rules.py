from planning_agents.shared.consistency_validator import ConsistencyValidator


def test_node_plan_blocks_python_leaks():
    validation_output = {"user_stack": {"backend": "Node.js", "database": "PostgreSQL"}}
    plan = {
        "framework": "Node.js",
        "language": "JavaScript",
        "api_style": "REST",
        "authentication": {
            "method": "JWT",
            "storage": "httpOnly cookies",
            "refresh_strategy": "Token rotation",
            "libraries": ["uvicorn", "pydantic"],
        },
        "database": {
            "type": "PostgreSQL",
            "orm": "SQLAlchemy",
            "connection_pool": True,
            "migration_tool": "Alembic",
        },
        "suggested_endpoints": [],
        "folder_structure": [],
        "core_libraries": ["uvicorn", "pydantic", "sqlalchemy"],
        "optional_libraries": {},
        "design_patterns": ["MVC"],
        "clarification_questions": [],
        "reasoning": "Node backend",
    }

    validator = ConsistencyValidator(validation_output)
    sanitized, report = validator.enforce_backend_plan(plan)

    assert report["is_valid"]
    assert "uvicorn" not in str(sanitized).lower()
    assert "pydantic" not in str(sanitized).lower()
    assert "sqlalchemy" not in str(sanitized).lower()
    assert "express" in str(sanitized).lower() or "prisma" in str(sanitized).lower()


def test_fastapi_plan_blocks_spring_leaks():
    validation_output = {"user_stack": {"backend": "FastAPI", "database": "PostgreSQL"}}
    plan = {
        "framework": "FastAPI",
        "language": "Python",
        "api_style": "REST",
        "authentication": {
            "method": "JWT",
            "storage": "httpOnly cookies",
            "refresh_strategy": "Token rotation",
            "libraries": ["Spring Security"],
        },
        "database": {
            "type": "PostgreSQL",
            "orm": "Hibernate",
            "connection_pool": True,
            "migration_tool": "Liquibase",
        },
        "suggested_endpoints": [],
        "folder_structure": [],
        "core_libraries": ["Spring Security", "Hibernate"],
        "optional_libraries": {},
        "design_patterns": ["Service Layer"],
        "clarification_questions": [],
        "reasoning": "FastAPI backend",
    }

    validator = ConsistencyValidator(validation_output)
    sanitized, report = validator.enforce_backend_plan(plan)

    assert report["is_valid"]
    assert "spring security" not in str(sanitized).lower()
    assert "hibernate" not in str(sanitized).lower()
    assert "fastapi" in str(sanitized).lower() or "sqlalchemy" in str(sanitized).lower()


def test_spring_plan_blocks_express_leaks():
    validation_output = {"user_stack": {"backend": "Spring Boot", "database": "PostgreSQL"}}
    plan = {
        "framework": "Spring Boot",
        "language": "Java",
        "api_style": "REST",
        "authentication": {
            "method": "JWT",
            "storage": "httpOnly cookies",
            "refresh_strategy": "Token rotation",
            "libraries": ["express", "express-jwt"],
        },
        "database": {
            "type": "PostgreSQL",
            "orm": "mongoose",
            "connection_pool": True,
            "migration_tool": "N/A",
        },
        "suggested_endpoints": [],
        "folder_structure": [],
        "core_libraries": ["express", "mongoose"],
        "optional_libraries": {},
        "design_patterns": ["MVC"],
        "clarification_questions": [],
        "reasoning": "Spring backend",
    }

    validator = ConsistencyValidator(validation_output)
    sanitized, report = validator.enforce_backend_plan(plan)

    assert report["is_valid"]
    assert "express" not in str(sanitized).lower()
    assert "mongoose" not in str(sanitized).lower()
    assert "spring" in str(sanitized).lower()