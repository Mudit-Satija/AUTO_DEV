from planning_agents.shared.rules import RuleManager


def test_rules_manager_flags_cross_stack_dependency():
    rules = RuleManager.from_validation_output(
        {
            "user_stack": {
                "backend": "Spring Boot",
                "database": "MongoDB",
            }
        }
    )

    violations = rules.validate_backend_plan(
        {
            "framework": "Spring Boot",
            "language": "Java",
            "authentication": {"method": "JWT", "storage": "httpOnly cookies", "libraries": ["Spring Security"]},
            "database": {"type": "MongoDB", "orm": "Mongoose", "connection_pool": True, "migration_tool": "N/A"},
            "core_libraries": ["express-validator", "spring-boot-starter-web"],
            "optional_libraries": {"mongoose": "Mongo helper"},
        }
    )

    assert any(item["field"] == "database.orm" for item in violations)
    assert any(item["field"] == "core_libraries" for item in violations)


def test_rules_manager_sanitizes_conflicting_dependencies():
    rules = RuleManager.from_validation_output(
        {
            "user_stack": {
                "backend": "Spring Boot",
                "database": "MongoDB",
            }
        }
    )

    sanitized, corrections = rules.sanitize_backend_plan(
        {
            "status": "success",
            "framework": "Express.js",
            "language": "JavaScript",
            "authentication": {"method": "JWT", "storage": "httpOnly cookies", "libraries": ["jsonwebtoken"]},
            "database": {"type": "MongoDB", "orm": "Mongoose", "connection_pool": True, "migration_tool": "N/A"},
            "core_libraries": ["express-validator", "mongoose"],
            "optional_libraries": {"express.js": "Web framework"},
            "reasoning": "Original plan",
        }
    )

    assert sanitized["framework"] == "Spring Boot"
    assert sanitized["language"] == "Java"
    assert sanitized["database"]["orm"] in {"Spring Data MongoDB", "MongoTemplate"}
    assert "spring-boot-starter-validation" in sanitized["core_libraries"] or "spring-boot-starter-web" in sanitized["core_libraries"]
    assert corrections
