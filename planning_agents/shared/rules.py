"""Deterministic rules for stack-consistent planning outputs."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any, Dict, List, Tuple


SPRING_RULES = {
    "framework": "Spring Boot",
    "language": "Java",
    "allowed_auth": ["Spring Security", "JWT"],
    "allowed_orm": ["Hibernate", "Spring Data JPA", "Spring Data MongoDB", "MongoTemplate"],
    "allowed_dependencies": [
        "spring-boot-starter-web",
        "spring-boot-starter-security",
        "spring-boot-starter-validation",
        "spring-boot-starter-data-jpa",
        "spring-boot-starter-data-mongodb",
        "spring-boot-starter-actuator",
        "spring-boot-starter-logging",
        "org.postgresql:postgresql",
        "jjwt-api",
        "lombok",
    ],
    "disallowed": [
        "express",
        "Express.js",
        "express-validator",
        "express-jwt",
        "express-rate-limit",
        "http-server",
        "winston",
        "morgan",
        "pg",
        "Mongoose",
        "mongoose",
        "sequelize",
        "dotenv",
        "joi",
        "jsonwebtoken",
        "Node.js",
    ],
    "database_orm_by_family": {
        "mongodb": ["Spring Data MongoDB", "MongoTemplate"],
        "sql": ["Hibernate", "Spring Data JPA"],
    },
    "dependency_replacements": {
        "express.js": "spring-boot-starter-web",
        "express": "spring-boot-starter-web",
        "express-validator": "spring-boot-starter-validation",
        "express-jwt": "spring-security",
        "express-rate-limit": "bucket4j",
        "http-server": "spring-boot-starter-web",
        "winston": "spring-boot-starter-logging",
        "morgan": "spring-boot-starter-logging",
        "pg": "org.postgresql:postgresql",
        "mongoose": "spring-boot-starter-data-mongodb",
        "sequelize": "spring-boot-starter-data-jpa",
        "dotenv": "application.yml",
        "joi": "jakarta validation",
        "jsonwebtoken": "spring-security",
        "node.js": "spring-boot-starter-web",
    },
}

FASTAPI_RULES = {
    "framework": "FastAPI",
    "language": "Python",
    "allowed_auth": ["python-jose", "JWT"],
    "allowed_orm": ["SQLAlchemy", "Motor", "Beanie", "SQLModel"],
    "allowed_dependencies": [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "motor",
        "beanie",
        "python-jose",
        "passlib[bcrypt]",
        "alembic",
    ],
    "disallowed": [
        "express",
        "Express.js",
        "express-validator",
        "express-jwt",
        "express-rate-limit",
        "Mongoose",
        "mongoose",
        "sequelize",
        "prisma",
        "bcryptjs",
        "cors",
        "jsonwebtoken",
        "Spring Security",
        "spring-boot",
        "Hibernate",
        "Spring Data JPA",
        "Spring Data MongoDB",
        "Node.js",
        "node.js",
    ],
    "database_orm_by_family": {
        "mongodb": ["Motor", "Beanie"],
        "sql": ["SQLAlchemy", "SQLModel"],
    },
    "dependency_replacements": {
        "express.js": "fastapi",
        "express": "fastapi",
        "express-validator": "pydantic",
        "express-jwt": "python-jose",
        "express-rate-limit": "slowapi",
        "mongoose": "motor",
        "sequelize": "sqlalchemy",
        "jsonwebtoken": "python-jose",
        "spring security": "python-jose",
        "spring-boot": "fastapi",
        "hibernate": "sqlalchemy",
        "spring data jpa": "sqlalchemy",
        "spring data mongodb": "motor",
        "prisma": "sqlalchemy",
        "bcryptjs": "passlib[bcrypt]",
        "cors": "fastapi.middleware.cors",
        "node.js": "fastapi",
    },
}

NODE_RULES = {
    "framework": "Node.js",
    "language": "JavaScript",
    "allowed_auth": ["jsonwebtoken"],
    "allowed_orm": ["mongoose", "prisma", "sequelize"],
    "allowed_dependencies": [
        "express",
        "jsonwebtoken",
        "mongoose",
        "prisma",
        "sequelize",
        "cors",
        "dotenv",
        "bcrypt",
    ],
    "disallowed": [
        "Spring Security",
        "spring-boot",
        "Spring Data JPA",
        "Hibernate",
        "FastAPI",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "alembic",
        "python-jose",
        "passlib",
        "motor",
        "beanie",
        "django",
        "flask",
    ],
    "database_orm_by_family": {
        "mongodb": ["mongoose", "prisma"],
        "sql": ["prisma", "sequelize"],
    },
    "dependency_replacements": {
        "spring security": "jsonwebtoken",
        "spring-boot": "express",
        "spring data jpa": "prisma",
        "hibernate": "prisma",
        "fastapi": "express",
        "uvicorn": "express",
        "pydantic": "zod",
        "python-jose": "jsonwebtoken",
        "sqlalchemy": "prisma",
        "alembic": "prisma migrate",
        "passlib": "bcrypt",
        "motor": "mongoose",
        "beanie": "mongoose",
        "django": "express",
        "flask": "express",
    },
}

STACK_RULES = {
    "spring": SPRING_RULES,
    "fastapi": FASTAPI_RULES,
    "node": NODE_RULES,
}

STACK_ALIASES = {
    "spring": "spring",
    "spring boot": "spring",
    "springboot": "spring",
    "fastapi": "fastapi",
    "fast api": "fastapi",
    "node": "node",
    "node.js": "node",
    "nodejs": "node",
    "express": "node",
    "express.js": "node",
    "javascript": "node",
}

DATABASE_ALIASES = {
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "mongo db": "mongodb",
    "postgres": "sql",
    "postgresql": "sql",
    "mysql": "sql",
    "sqlite": "sql",
    "sql": "sql",
}


def _normalize(text: Any) -> str:
    value = str(text or "").strip().lower()
    value = value.replace("_", " ")
    value = re.sub(r"[^a-z0-9\-\.\+\[\]]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _normalize_key(text: Any) -> str:
    return _normalize(text).replace(".", " ").replace("-", " ")


def _resolve_stack_key(value: Any) -> str:
    normalized = _normalize_key(value)
    for alias, key in STACK_ALIASES.items():
        if alias in normalized:
            return key
    return "spring"


def _resolve_database_family(value: Any) -> str:
    normalized = _normalize_key(value)
    for alias, key in DATABASE_ALIASES.items():
        if alias in normalized:
            return key
    return "sql"


def _unique(items: List[str]) -> List[str]:
    seen = set()
    cleaned = []
    for item in items:
        normalized = _normalize_key(item)
        if normalized and normalized not in seen:
            seen.add(normalized)
            cleaned.append(item)
    return cleaned


@dataclass
class RuleManager:
    """Load and apply stack rules for deterministic planning."""

    backend_key: str
    database_family: str
    raw_backend: str
    raw_database: str

    @classmethod
    def from_validation_output(cls, validation_output: Dict[str, Any] | None) -> "RuleManager":
        validation_output = validation_output or {}
        if isinstance(validation_output, dict) and isinstance(validation_output.get("planning_rules"), dict):
            planning_rules = validation_output["planning_rules"]
            backend_key = str(planning_rules.get("backend_key", "spring"))
            database_family = str(planning_rules.get("database_family", "sql"))
            raw_backend = str(planning_rules.get("raw_backend", validation_output.get("user_stack", {}).get("backend", "Spring Boot")))
            raw_database = str(planning_rules.get("raw_database", validation_output.get("user_stack", {}).get("database", "PostgreSQL")))
            return cls(backend_key=backend_key, database_family=database_family, raw_backend=raw_backend, raw_database=raw_database)

        user_stack = validation_output.get("user_stack", {}) if isinstance(validation_output, dict) else {}
        raw_backend = str(user_stack.get("backend", "Spring Boot"))
        raw_database = str(user_stack.get("database", "PostgreSQL"))
        backend_key = _resolve_stack_key(raw_backend)
        database_family = _resolve_database_family(raw_database)
        return cls(backend_key=backend_key, database_family=database_family, raw_backend=raw_backend, raw_database=raw_database)

    @property
    def rules(self) -> Dict[str, Any]:
        return STACK_RULES[self.backend_key]

    @property
    def framework(self) -> str:
        return self.rules["framework"]

    @property
    def language(self) -> str:
        return self.rules["language"]

    def attach_to_validation_output(self, validation_output: Dict[str, Any]) -> Dict[str, Any]:
        payload = deepcopy(validation_output or {})
        payload["planning_rules"] = {
            "backend_key": self.backend_key,
            "database_family": self.database_family,
            "raw_backend": self.raw_backend,
            "raw_database": self.raw_database,
        }
        return payload

    def prompt_context(self, agent_name: str) -> str:
        rules = self.rules
        database_options = rules.get("database_orm_by_family", {}).get(self.database_family, rules.get("allowed_orm", []))
        prompt_lines = [
            "RULE ENGINE CONTEXT:",
            f"- Selected backend stack: {self.framework} ({self.language})",
            f"- Selected database family: {self.raw_database} -> {self.database_family.upper()}",
            f"- Allowed auth: {', '.join(rules.get('allowed_auth', []))}",
            f"- Allowed ORM/data access: {', '.join(database_options)}",
            f"- Allowed dependencies: {', '.join(rules.get('allowed_dependencies', []))}",
            f"- Disallowed technologies: {', '.join(rules.get('disallowed', [])) if rules.get('disallowed') else 'none'}",
            "- If a recommendation conflicts with the selected stack, replace it with a valid stack-specific alternative.",
            f"- {agent_name} must not introduce packages from another ecosystem.",
        ]
        return "\n".join(prompt_lines)

    def validate_technology(self, tech: str, category: str | None = None) -> Tuple[bool, str]:
        normalized = _normalize_key(tech)
        rules = self.rules
        disallowed = [_normalize_key(item) for item in rules.get("disallowed", [])]
        if any(blocked and blocked in normalized for blocked in disallowed):
            return False, f"{tech} conflicts with the {self.framework} stack"

        if category == "auth":
            allowed = [_normalize_key(item) for item in rules.get("allowed_auth", [])]
        elif category == "orm":
            allowed = [_normalize_key(item) for item in rules.get("database_orm_by_family", {}).get(self.database_family, rules.get("allowed_orm", []))]
        else:
            allowed = [_normalize_key(item) for item in rules.get("allowed_dependencies", [])]

        if allowed and any(token in normalized for token in allowed):
            return True, "allowed"

        if category in {"auth", "orm"}:
            return False, f"{tech} is not valid for {self.framework}"

        return True, "allowed"

    def validate_backend_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        candidate = plan or {}

        framework = str(candidate.get("framework", ""))
        if _normalize_key(framework) and _normalize_key(framework) != _normalize_key(self.framework):
            violations.append({
                "field": "framework",
                "value": framework,
                "message": f"Expected {self.framework}",
            })

        language = str(candidate.get("language", ""))
        if _normalize_key(language) and _normalize_key(language) != _normalize_key(self.language):
            violations.append({
                "field": "language",
                "value": language,
                "message": f"Expected {self.language}",
            })

        auth = candidate.get("authentication", {}) if isinstance(candidate.get("authentication"), dict) else {}
        auth_libraries = auth.get("libraries", []) if isinstance(auth.get("libraries"), list) else []
        for library in auth_libraries:
            valid, message = self.validate_technology(str(library), category="auth")
            if not valid:
                violations.append({"field": "authentication.libraries", "value": library, "message": message})

        database = candidate.get("database", {}) if isinstance(candidate.get("database"), dict) else {}
        orm = str(database.get("orm", ""))
        if orm:
            valid, message = self.validate_technology(orm, category="orm")
            if not valid:
                violations.append({"field": "database.orm", "value": orm, "message": message})

        for library in candidate.get("core_libraries", []) if isinstance(candidate.get("core_libraries"), list) else []:
            valid, message = self.validate_technology(str(library))
            if not valid:
                violations.append({"field": "core_libraries", "value": library, "message": message})

        optional_libraries = candidate.get("optional_libraries", {}) if isinstance(candidate.get("optional_libraries"), dict) else {}
        for library_name in optional_libraries.keys():
            valid, message = self.validate_technology(str(library_name))
            if not valid:
                violations.append({"field": "optional_libraries", "value": library_name, "message": message})

        return violations

    def _replacement_for(self, technology: str) -> str | None:
        normalized = _normalize_key(technology)
        replacements = self.rules.get("dependency_replacements", {})
        for needle, replacement in sorted(replacements.items(), key=lambda item: len(_normalize_key(item[0])), reverse=True):
            normalized_needle = _normalize_key(needle)
            if normalized_needle and (normalized == normalized_needle or normalized_needle in normalized):
                return replacement
        return None

    def _preferred_database_orm(self) -> str:
        allowed = self.rules.get("database_orm_by_family", {}).get(self.database_family, self.rules.get("allowed_orm", []))
        return allowed[0] if allowed else "Unknown"

    def _preferred_auth_library(self) -> str:
        allowed = self.rules.get("allowed_auth", [])
        return allowed[0] if allowed else "JWT"

    def _preferred_migration_tool(self) -> str:
        if self.backend_key == "node":
            return "Prisma Migrate"
        if self.backend_key == "fastapi":
            return "Alembic"
        if self.backend_key == "spring":
            return "Liquibase"
        return "N/A"

    def _sanitize_library_list(self, values: List[Any], category: str | None = None) -> Tuple[List[str], List[str]]:
        sanitized: List[str] = []
        corrections: List[str] = []
        for value in values:
            library = str(value).strip()
            if not library:
                continue
            valid, _ = self.validate_technology(library, category=category)
            if valid:
                sanitized.append(library)
                continue

            replacement = self._replacement_for(library)
            if replacement:
                sanitized.append(replacement)
                corrections.append(f"{library} -> {replacement}")

        return _unique(sanitized), corrections

    def sanitize_backend_plan(self, plan: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        sanitized = deepcopy(plan or {})
        corrections: List[str] = []

        sanitized["framework"] = self.framework
        sanitized["language"] = self.language

        auth = sanitized.get("authentication", {}) if isinstance(sanitized.get("authentication"), dict) else {}
        auth_libraries = auth.get("libraries", []) if isinstance(auth.get("libraries"), list) else []
        cleaned_auth, auth_corrections = self._sanitize_library_list(auth_libraries, category="auth")
        cleaned_auth = [library for library in cleaned_auth if self.validate_technology(library, category="auth")[0]]
        if not cleaned_auth:
            cleaned_auth = [self._preferred_auth_library()]
        auth["libraries"] = cleaned_auth
        auth_method = str(auth.get("method", "JWT"))
        if _normalize_key(auth_method) not in {"jwt", "oauth", "session", "session based"}:
            auth["method"] = "JWT"
            corrections.append(f"authentication.method -> JWT")
        auth["storage"] = auth.get("storage", "httpOnly cookies") or "httpOnly cookies"
        sanitized["authentication"] = auth
        corrections.extend(auth_corrections)

        database = sanitized.get("database", {}) if isinstance(sanitized.get("database"), dict) else {}
        database["type"] = database.get("type") or self.raw_database or self.framework
        orm = str(database.get("orm", "")).strip()
        valid_orms = self.rules.get("database_orm_by_family", {}).get(self.database_family, self.rules.get("allowed_orm", []))
        if orm and any(_normalize_key(option) in _normalize_key(orm) for option in valid_orms):
            database["orm"] = orm
        else:
            database["orm"] = self._preferred_database_orm()
            if orm:
                corrections.append(f"database.orm -> {database['orm']} (replaced {orm})")
        database["connection_pool"] = bool(database.get("connection_pool", True))
        migration_tool = str(database.get("migration_tool", "N/A") or "N/A").strip()
        preferred_migration_tool = self._preferred_migration_tool()
        if migration_tool and preferred_migration_tool != "N/A":
            if _normalize_key(migration_tool) != _normalize_key(preferred_migration_tool):
                database["migration_tool"] = preferred_migration_tool
                corrections.append(f"database.migration_tool -> {preferred_migration_tool} (replaced {migration_tool})")
            else:
                database["migration_tool"] = migration_tool
        else:
            database["migration_tool"] = preferred_migration_tool
        sanitized["database"] = database

        core_libraries = sanitized.get("core_libraries", []) if isinstance(sanitized.get("core_libraries"), list) else []
        cleaned_core, core_corrections = self._sanitize_library_list(core_libraries)
        if not cleaned_core:
            cleaned_core = [self.rules.get("allowed_dependencies", ["docker"])[0]]
        sanitized["core_libraries"] = cleaned_core
        corrections.extend(core_corrections)

        optional_libraries = sanitized.get("optional_libraries", {}) if isinstance(sanitized.get("optional_libraries"), dict) else {}
        cleaned_optional: Dict[str, str] = {}
        for key, value in optional_libraries.items():
            replacement = self._replacement_for(str(key))
            target_key = replacement or str(key).strip()
            if not target_key:
                continue
            cleaned_optional[target_key] = str(value)
            if replacement and replacement != key:
                corrections.append(f"optional_libraries.{key} -> {replacement}")
        sanitized["optional_libraries"] = cleaned_optional

        if corrections:
            reasoning = str(sanitized.get("reasoning", "")).strip()
            correction_text = f"Rules engine corrections applied: {len(_unique(corrections))} adjustment(s)."
            sanitized["reasoning"] = (
                f"{reasoning}\nRules engine corrections: {correction_text}".strip()
                if reasoning
                else f"Rules engine corrections: {correction_text}"
            )

        return sanitized, _unique(corrections)
