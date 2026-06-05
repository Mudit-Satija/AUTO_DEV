from backend_agents.merger import merge_agent_results
from planning_agents.shared.consistency_validator import ConsistencyValidator


def test_consistency_validator_rejects_cross_ecosystem_libraries():
    validator = ConsistencyValidator(
        {"user_stack": {"backend": "Spring Boot", "database": "MongoDB"}}
    )

    report = validator.inspect_backend_plan(
        {
            "framework": "Spring Boot",
            "language": "Java",
            "authentication": {"method": "JWT", "storage": "httpOnly cookies", "libraries": ["express-jwt"]},
            "database": {"type": "MongoDB", "orm": "Mongoose", "connection_pool": True, "migration_tool": "N/A"},
            "core_libraries": ["express-validator", "dotenv", "mongoose"],
            "optional_libraries": {"joi": "validation", "express-rate-limit": "rate limiting"},
        }
    )

    assert report["is_valid"] is False
    assert report["consistency_score"] < 100
    assert any("express-validator" in item for item in report["conflicts_found"])
    assert any("mongoose" in item.lower() for item in report["conflicts_found"])


def test_merge_agent_results_sanitizes_or_blocks_invalid_backend_ecosystem():
    validation_output = {"user_stack": {"backend": "Spring Boot", "database": "MongoDB"}, "project_type": "web app"}

    result = merge_agent_results(
        {
            "architecture": {"framework": "Spring Boot", "language": "Java", "api_style": "REST", "pattern": "Monolith"},
            "authentication": {"method": "JWT", "storage": "httpOnly cookies", "recommendations": [], "libraries": ["express-jwt"]},
            "endpoints": {"endpoints": []},
            "database": {"type": "MongoDB", "orm": "Mongoose", "cache": "None", "migration_tool": "N/A", "recommendations": []},
            "folder_structure": {"folders": []},
            "dependencies": {"core": ["express-validator", "dotenv", "mongoose"], "optional": {"joi": "validation"}},
        },
        validation_output,
    )

    assert result["status"] == "error"
    assert result["consistency_score"] < 100
    assert result["conflicts_found"]
    assert any("express-validator" in item.lower() or "mongoose" in item.lower() for item in result["conflicts_found"])


def test_consistency_validator_scans_reasoning_and_recommendations():
    validator = ConsistencyValidator(
        {"user_stack": {"backend": "Spring Boot", "database": "MongoDB"}}
    )

    report = validator.inspect_backend_plan(
        {
            "framework": "Spring Boot",
            "language": "Java",
            "authentication": {
                "method": "JWT",
                "storage": "httpOnly cookies",
                "libraries": ["Spring Security"],
                "recommendations": ["Use express-validator and joi"],
                "refresh_strategy": "Use express-jwt",
            },
            "database": {
                "type": "MongoDB",
                "orm": "Mongoose",
                "connection_pool": True,
                "migration_tool": "N/A",
                "recommendations": ["Use dotenv"],
            },
            "core_libraries": ["spring-boot-starter-web"],
            "optional_libraries": {},
            "reasoning": "Avoid express-validator and mongoose in Spring plans.",
        }
    )

    assert report["is_valid"] is False
    assert any("reasoning" in conflict for conflict in report["conflicts_found"])
    assert any("authentication.recommendations" in conflict or "authentication.refresh_strategy" in conflict for conflict in report["conflicts_found"])
    assert any("database.recommendations" in conflict for conflict in report["conflicts_found"])
