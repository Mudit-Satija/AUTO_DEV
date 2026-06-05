import asyncio
import json
import logging
import time
from typing import Dict, List
from llm_client import get_llm_response
from planning_agents.shared.domain_intelligence import build_domain_context, domain_context_summary, backend_hints, merge_unique
from planning_agents.shared.json_utils import extract_json

logger = logging.getLogger(__name__)


def _output_metrics(payload) -> Dict:
    serialized = json.dumps(payload, default=str)
    return {
        "output_character_count": len(serialized),
        "output_word_count": len(serialized.split()),
    }


async def _run_profiled_agent(agent_name: str, coro):
    start = time.perf_counter()
    result = await coro
    elapsed_ms = int((time.perf_counter() - start) * 1000)
    metrics = _output_metrics(result)
    logger.info(
        "[PERF]\n%s: %d ms\nOutput Size: %d chars\nOutput Words: %d",
        agent_name,
        elapsed_ms,
        metrics["output_character_count"],
        metrics["output_word_count"],
    )
    return result, {
        "agent": agent_name,
        "execution_time_ms": elapsed_ms,
        **metrics,
    }

# Architecture Agent - Context-aware framework selection with rules
ARCHITECTURE_PROMPT = """You are a backend architecture expert. Analyze the project and recommend the BEST framework based on project type and complexity.

RULES:
- For "real-time" projects: FastAPI + async (better than Express)
- For "AI system": Python async framework (FastAPI, must support async/await)
- For "SaaS": Use framework that supports multi-tenancy (FastAPI, Node.js)
- For "simple CRUD": Express.js or FastAPI is fine
- PATTERN SELECTION:
  * Simple CRUD → MVC pattern
  * Real-time → Service Layer + Event-driven
  * AI System → Service Layer + Async Pipelines
  * SaaS → Microservices-ready + Event-driven
  * High-load → CQRS + Event Sourcing concepts

PROJECT CONTEXT:
- Type: {project_type}
- Complexity: {complexity}
- Backend: {backend}
- Real-time needed: {realtime}

Return ONLY this JSON (NO other text):
{{
  "framework": "framework name with version",
  "language": "programming language",
  "api_style": "REST|REST+WebSocket|GraphQL|gRPC",
  "architecture_pattern": "pattern name with explanation",
  "async_required": true|false,
  "reasoning": "why this choice matches project needs"
}}"""


async def architecture_agent(shared_state: Dict) -> Dict:
    """Recommend backend framework and architecture pattern"""
    try:
        logger.info("🏗️  [PARALLEL] Architecture Agent starting...")
        
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "beginner")
        backend = shared_state.get("user_stack", {}).get("backend", "Node.js")
        realtime = shared_state.get("user_stack", {}).get("realtime", "No")
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        prompt = ARCHITECTURE_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            backend=backend,
            realtime=realtime
        )
        prompt = prompt + "\n\nDOMAIN CONTEXT:\n" + domain_context_summary(domain_context)
        
        response_text = await asyncio.to_thread(get_llm_response, prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        result = extract_json(response_text)
        logger.info(f"✅ Architecture Agent: {result.get('framework')} + {result.get('architecture_pattern')}")
        return result
        
    except Exception as e:
        logger.error(f"Architecture Agent failed: {e}", exc_info=True)
        return {
            "framework": "FastAPI" if shared_state.get("user_stack", {}).get("backend") == "Python" else "Express.js",
            "language": "Python" if shared_state.get("user_stack", {}).get("backend") == "Python" else "JavaScript",
            "api_style": "REST",
            "architecture_pattern": "Service Layer",
            "async_required": True,
            "reasoning": f"Default due to error: {str(e)}"
        }


# Authentication Agent - Security-first with multiple strategies
AUTH_PROMPT = """You are a security expert. Design authentication for this project with security best practices.

RULES (MUST FOLLOW):
- NEVER suggest plaintext passwords
- ALWAYS recommend JWT + refresh tokens OR OAuth2
- ALWAYS recommend HTTPS, CORS, rate limiting
- ALWAYS recommend input validation libraries
- ALWAYS recommend secrets management

SECURITY REQUIREMENTS BY PROJECT TYPE:
- "SaaS": Add multi-tenancy auth, audit logging
- "AI system": Add API key option, usage tracking
- "real-time": Add session-based auth, presence tracking
- All: rate limiting, CSRF protection, secure password hashing

PROJECT CONTEXT:
- Type: {project_type}
- Framework: {framework}
- Language: {language}

Return ONLY this JSON (NO other text):
{{
  "method": "JWT|OAuth2|Session-based|Multi-factor",
  "storage": "httpOnly cookies|localStorage|server session",
  "libraries": ["lib1", "lib2", "lib3"],
  "security_best_practices": [
    "practice 1",
    "practice 2",
    "practice 3",
    "practice 4",
    "practice 5"
  ],
  "reasoning": "why this auth approach matches project security needs"
}}"""


async def auth_agent(shared_state: Dict) -> Dict:
    """Design authentication and security strategy"""
    try:
        logger.info("🔐 [PARALLEL] Auth Agent starting...")
        
        project_type = shared_state.get("project_type", "web app")
        framework = shared_state.get("_framework", "Express.js")  # Will be set by architecture agent
        language = shared_state.get("_language", "JavaScript")
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        prompt = AUTH_PROMPT.format(
            project_type=project_type,
            framework=framework,
            language=language
        )
        prompt = prompt + "\n\nDOMAIN CONTEXT:\n" + domain_context_summary(domain_context)
        
        response_text = await asyncio.to_thread(get_llm_response, prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        result = extract_json(response_text)
        logger.info(f"✅ Auth Agent: {result.get('method')} authentication")
        return result
        
    except Exception as e:
        logger.error(f"Auth Agent failed: {e}", exc_info=True)
        return {
            "method": "JWT",
            "storage": "httpOnly cookies",
            "libraries": ["jsonwebtoken", "bcrypt"],
            "security_best_practices": [
                "Use HTTPS only",
                "Implement rate limiting on auth endpoints",
                "Use secure password hashing (bcrypt)",
                "Add CSRF protection",
                "Implement account lockout after failed attempts"
            ],
            "reasoning": f"Default JWT security due to error: {str(e)}"
        }


# Endpoint Agent - Smart, NOT just CRUD
ENDPOINT_PROMPT = """You are an API design expert. Design REST endpoints that are SMART, not just basic CRUD.

RULES (MUST FOLLOW):
- NEVER generate just CRUD endpoints
- "Simple todo app" → 10-15 endpoints (auth + CRUD + notifications)
- "Real-time chat" → 20+ endpoints (auth + chat + presence + notifications + typing)
- "AI system" → 30+ endpoints (auth + generation + conversation + monitoring + webhooks)
- Add advanced features: webhooks, batch operations, async jobs, analytics
- Include WebSocket endpoints for real-time features

ENDPOINT CATEGORIES:
1. Authentication (register, login, refresh, logout)
2. Main Resources (CRUD operations)
3. Advanced Features (depends on project type)
4. Notifications/Webhooks
5. Analytics/Monitoring
6. Batch Operations (if needed)
7. Real-time (WebSocket if needed)

PROJECT CONTEXT:
- Type: {project_type}
- Complexity: {complexity}
- Real-time: {realtime}

Generate {endpoint_count} endpoints total.

Return ONLY this JSON (NO other text):
[
  {{"method": "POST", "path": "/api/auth/register", "description": "Register new user", "auth_required": false, "category": "authentication"}},
  {{"method": "POST", "path": "/api/auth/login", "description": "Login user", "auth_required": false, "category": "authentication"}},
  {{"method": "GET", "path": "/api/users/me", "description": "Get current user", "auth_required": true, "category": "user"}},
  ...more endpoints...
]"""


async def endpoint_agent(shared_state: Dict) -> Dict:
    """Design REST API endpoints (not just CRUD)"""
    try:
        logger.info("📡 [PARALLEL] Endpoint Agent starting...")
        
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "beginner")
        realtime = shared_state.get("user_stack", {}).get("realtime", "No")
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        # Determine endpoint count based on complexity
        if project_type == "simple CRUD" or complexity == "beginner":
            endpoint_count = 12
        elif project_type == "real-time" or complexity == "advanced":
            endpoint_count = 25
        elif "AI" in project_type or "automation" in project_type:
            endpoint_count = 30
        else:
            endpoint_count = 15
        
        prompt = ENDPOINT_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            realtime=realtime,
            endpoint_count=endpoint_count
        )
        prompt = prompt + "\n\nDOMAIN CONTEXT:\n" + domain_context_summary(domain_context)
        
        response_text = await asyncio.to_thread(get_llm_response, prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        endpoints = extract_json(response_text)
        endpoints = _apply_domain_context_to_endpoints(endpoints, domain_context)
        logger.info(f"✅ Endpoint Agent: {len(endpoints)} endpoints designed")
        return {"endpoints": endpoints, "total_count": len(endpoints)}
        
    except Exception as e:
        logger.error(f"Endpoint Agent failed: {e}", exc_info=True)
        return _fallback_endpoints(shared_state)


def _apply_domain_context_to_endpoints(endpoints: list, domain_context: dict) -> list:
    if not isinstance(endpoints, list):
        return []

    if domain_context.get("domain") != "project_management":
        return endpoints

    domain_endpoints = [
        {"method": "GET", "path": "/api/workspaces", "description": "List workspaces", "auth_required": True, "category": "main_resources"},
        {"method": "POST", "path": "/api/workspaces", "description": "Create workspace", "auth_required": True, "category": "main_resources"},
        {"method": "GET", "path": "/api/projects", "description": "List projects", "auth_required": True, "category": "main_resources"},
        {"method": "POST", "path": "/api/projects", "description": "Create project", "auth_required": True, "category": "main_resources"},
        {"method": "GET", "path": "/api/tasks", "description": "List tasks", "auth_required": True, "category": "main_resources"},
        {"method": "POST", "path": "/api/tasks", "description": "Create task", "auth_required": True, "category": "main_resources"},
        {"method": "GET", "path": "/api/comments", "description": "List comments", "auth_required": True, "category": "main_resources"},
        {"method": "POST", "path": "/api/comments", "description": "Add comment", "auth_required": True, "category": "main_resources"},
        {"method": "GET", "path": "/api/activity", "description": "View activity log", "auth_required": True, "category": "analytics"},
        {"method": "GET", "path": "/api/notifications", "description": "List notifications", "auth_required": True, "category": "notifications"},
    ]

    merged = []
    seen = set()
    allowed_auth = {"/api/auth/login", "/api/auth/register"}
    for endpoint in domain_endpoints + endpoints:
        if not isinstance(endpoint, dict):
            continue
        path = str(endpoint.get("path", "")).strip().lower()
        if not path or path in seen:
            continue
        if (path.startswith("/api/auth") or path.startswith("/api/users")) and path not in allowed_auth:
            continue
        seen.add(path)
        merged.append({
            "method": str(endpoint.get("method", "GET")).upper(),
            "path": str(endpoint.get("path", "/api")),
            "description": str(endpoint.get("description", "API endpoint")),
            "auth_required": bool(endpoint.get("auth_required", True)),
            "category": str(endpoint.get("category", "main_resources")),
        })

    return merged[:15]


def _fallback_endpoints(shared_state: dict) -> dict:
    domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
    if domain_context.get("domain") == "project_management":
        return {
            "endpoints": [
                {"method": "GET", "path": "/api/workspaces", "description": "List workspaces", "auth_required": True, "category": "main_resources"},
                {"method": "POST", "path": "/api/workspaces", "description": "Create workspace", "auth_required": True, "category": "main_resources"},
                {"method": "GET", "path": "/api/projects", "description": "List projects", "auth_required": True, "category": "main_resources"},
                {"method": "POST", "path": "/api/projects", "description": "Create project", "auth_required": True, "category": "main_resources"},
                {"method": "GET", "path": "/api/tasks", "description": "List tasks", "auth_required": True, "category": "main_resources"},
                {"method": "POST", "path": "/api/tasks", "description": "Create task", "auth_required": True, "category": "main_resources"},
                {"method": "GET", "path": "/api/comments", "description": "List comments", "auth_required": True, "category": "main_resources"},
                {"method": "POST", "path": "/api/comments", "description": "Add comment", "auth_required": True, "category": "main_resources"},
                {"method": "GET", "path": "/api/activity", "description": "View activity log", "auth_required": True, "category": "analytics"},
                {"method": "GET", "path": "/api/notifications", "description": "List notifications", "auth_required": True, "category": "notifications"},
            ],
            "total_count": 10,
        }
    return {
        "endpoints": [
            {"method": "POST", "path": "/api/auth/register", "description": "Register user", "auth_required": False, "category": "auth"},
            {"method": "POST", "path": "/api/auth/login", "description": "Login user", "auth_required": False, "category": "auth"},
            {"method": "GET", "path": "/api/users/me", "description": "Get current user", "auth_required": True, "category": "user"},
        ],
        "total_count": 3,
    }


# Database Agent - Smart schema and scaling
DATABASE_PROMPT = """You are a database architect. Design database strategy that scales with the project.

RULES (MUST FOLLOW):
- Match ORM to database choice
- If high-load/SaaS → recommend caching strategy (Redis)
- If SaaS → recommend multi-tenancy schema
- ALWAYS recommend connection pooling
- ALWAYS recommend indexing strategy
- ALWAYS recommend query optimization for complex apps

SCALING STRATEGIES:
- Simple app: Basic indexes, simple caching
- Real-time: Redis for sessions, pub-sub for messaging
- AI System: Connection pooling, query optimization, async queries
- SaaS: Multi-tenancy schema, row-level security, audit trails
- High-load: Caching layers, read replicas, query optimization, sharding

PROJECT CONTEXT:
- Type: {project_type}
- Database: {database}
- Complexity: {complexity}

Return ONLY this JSON (NO other text):
{{
  "type": "database name",
  "orm": "ORM library",
  "connection_pool": true,
  "connection_pool_size": 20,
  "migration_tool": "migration tool",
  "caching_strategy": "Redis or None",
  "indexing_strategy": ["index1", "index2", "index3"],
  "scaling_considerations": [
    "consideration1",
    "consideration2",
    "consideration3"
  ],
  "reasoning": "why this database strategy matches project needs"
}}"""


async def database_agent(shared_state: Dict) -> Dict:
    """Design database architecture and scaling strategy"""
    try:
        logger.info("💾 [PARALLEL] Database Agent starting...")
        
        project_type = shared_state.get("project_type", "web app")
        database = shared_state.get("user_stack", {}).get("database", "PostgreSQL")
        complexity = shared_state.get("complexity", "beginner")
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        prompt = DATABASE_PROMPT.format(
            project_type=project_type,
            database=database,
            complexity=complexity
        )
        prompt = prompt + "\n\nDOMAIN CONTEXT:\n" + domain_context_summary(domain_context)
        
        response_text = await asyncio.to_thread(get_llm_response, prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        result = extract_json(response_text)
        logger.info(f"✅ Database Agent: {result.get('type')} + {result.get('orm')}")
        return result
        
    except Exception as e:
        logger.error(f"Database Agent failed: {e}", exc_info=True)
        return {
            "type": "PostgreSQL",
            "orm": "SQLAlchemy",
            "connection_pool": True,
            "connection_pool_size": 20,
            "migration_tool": "Alembic",
            "caching_strategy": "Redis",
            "indexing_strategy": ["user_id", "created_at", "status"],
            "scaling_considerations": [
                "Connection pooling for concurrent requests",
                "Proper indexing for query performance",
                "Redis caching for frequently accessed data"
            ],
            "reasoning": f"Default strategy due to error: {str(e)}"
        }


# Folder Structure Agent - Scalable architecture
FOLDER_PROMPT = """You are a code organization expert. Design folder structure that scales from startup to enterprise.

RULES (MUST FOLLOW):
- Simple app → flat structure (but still organized)
- Complex app → domain-driven structure
- ALWAYS include: tests/, config/, utils/, middleware/
- Make room for growth even in simple apps
- Use modular, domain-driven approach for complex projects

STRUCTURE RECOMMENDATIONS:
- Simple: src/routes, src/controllers, src/models, src/middleware, src/utils
- Complex: src/domains/{{domain}}/routes, src/domains/{{domain}}/services, src/domains/{{domain}}/models
- Advanced: src/core/, src/domains/, src/shared/, src/infrastructure/

PROJECT CONTEXT:
- Type: {project_type}
- Complexity: {complexity}
- Language: {language}

Return ONLY this JSON (NO other text):
{{
  "folders": [
    {{"path": "src/", "type": "directory", "purpose": "main source code"}},
    {{"path": "src/core/", "type": "directory", "purpose": "shared utilities, config, security"}},
    {{"path": "src/domains/", "type": "directory", "purpose": "domain-driven structure"}},
    {{"path": "tests/", "type": "directory", "purpose": "unit and integration tests"}},
    {{"path": "config/", "type": "directory", "purpose": "configuration files"}}
  ],
  "total_directories": 5,
  "structure_type": "flat|modular|domain-driven",
  "reasoning": "why this structure matches project complexity"
}}"""


async def folder_structure_agent(shared_state: Dict) -> Dict:
    """Design scalable folder structure"""
    try:
        logger.info("📁 [PARALLEL] Folder Structure Agent starting...")
        
        project_type = shared_state.get("project_type", "web app")
        complexity = shared_state.get("complexity", "beginner")
        language = shared_state.get("user_stack", {}).get("backend", "JavaScript")
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        
        prompt = FOLDER_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            language=language
        )
        prompt = prompt + "\n\nDOMAIN CONTEXT:\n" + domain_context_summary(domain_context)
        
        response_text = await asyncio.to_thread(get_llm_response, prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        result = extract_json(response_text)
        result["folders"] = _apply_domain_context_to_folders(result.get("folders", []), domain_context)
        result["total_directories"] = len(result["folders"])
        logger.info(f"✅ Folder Structure Agent: {result.get('structure_type')} structure")
        return result
        
    except Exception as e:
        logger.error(f"Folder Structure Agent failed: {e}", exc_info=True)
        return _fallback_folder_structure(shared_state)


def _apply_domain_context_to_folders(folders: list, domain_context: dict) -> list:
    if not isinstance(folders, list):
        return []
    hints = backend_hints(domain_context)
    preferred_modules = hints.get("modules", [])
    if domain_context.get("domain") == "project_management" and preferred_modules:
        preferred_folders = [
            {"path": "src/domains/workspaces/", "type": "directory", "purpose": "Workspace domain modules"},
            {"path": "src/domains/projects/", "type": "directory", "purpose": "Project domain modules"},
            {"path": "src/domains/tasks/", "type": "directory", "purpose": "Task and board modules"},
            {"path": "src/domains/activity/", "type": "directory", "purpose": "Activity log modules"},
            {"path": "src/domains/notifications/", "type": "directory", "purpose": "Notification modules"},
        ]
        merged = preferred_folders + [item for item in folders if isinstance(item, dict)]
        seen = set()
        result = []
        for folder in merged:
            path = str(folder.get("path") or "").strip().lower()
            if not path or path in seen:
                continue
            seen.add(path)
            result.append(folder)
        return result[:8]
    return folders


def _fallback_folder_structure(shared_state: dict) -> dict:
    domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
    if domain_context.get("domain") == "project_management":
        return {
            "folders": [
                {"path": "src/", "type": "directory", "purpose": "main source code"},
                {"path": "src/domains/workspaces/", "type": "directory", "purpose": "Workspace domain modules"},
                {"path": "src/domains/projects/", "type": "directory", "purpose": "Project domain modules"},
                {"path": "src/domains/tasks/", "type": "directory", "purpose": "Task and board modules"},
                {"path": "src/domains/activity/", "type": "directory", "purpose": "Activity log modules"},
                {"path": "src/domains/notifications/", "type": "directory", "purpose": "Notification modules"},
                {"path": "tests/", "type": "directory", "purpose": "test files"},
                {"path": "config/", "type": "directory", "purpose": "configuration"},
            ],
            "total_directories": 8,
            "structure_type": "domain-driven",
            "reasoning": "Fallback: project management structure applied after error",
        }
    return {
        "folders": [
            {"path": "src/", "type": "directory", "purpose": "main source code"},
            {"path": "src/core/", "type": "directory", "purpose": "shared utilities"},
            {"path": "src/domains/", "type": "directory", "purpose": "domain-driven modules"},
            {"path": "tests/", "type": "directory", "purpose": "test files"},
            {"path": "config/", "type": "directory", "purpose": "configuration"},
        ],
        "total_directories": 5,
        "structure_type": "modular",
        "reasoning": "Fallback: generic structure applied after error",
    }


# Dependency Agent - Smart, not bloated
DEPENDENCY_PROMPT = """You are a package management expert. Recommend dependencies (core + optional) that are MINIMAL but COMPLETE.

RULES (MUST FOLLOW):
- Include ONLY necessary dependencies
- If async → add async libraries
- If real-time → add WebSocket libraries
- If queue needed → add Celery/RQ
- ALWAYS include: security, logging, testing, validation
- Separate core (essential) vs optional (nice-to-have)

CORE LIBRARIES (ALWAYS INCLUDE):
- Framework (FastAPI, Express, etc)
- Web server (Uvicorn, etc)
- Database ORM
- Validation (Pydantic, Joi, etc)
- Security (JWT, bcrypt, etc)
- Environment (python-dotenv, etc)

OPTIONAL (depends on project):
- Async: aiohttp, asyncpg, motor
- Real-time: websockets, socket.io
- Queue: celery, rq, bull
- Testing: pytest, jest, mocha
- Code quality: black, pylint, eslint
- Monitoring: sentry, datadog, prometheus

PROJECT CONTEXT:
- Type: {project_type}
- Language: {language}
- Framework: {framework}
- Async required: {async_required}

Return ONLY this JSON (NO other text):
{{
  "core_libraries": ["lib1", "lib2", "lib3"],
  "optional_libraries": {{
    "library_name": "purpose/description",
    "library_name2": "purpose/description"
  }},
  "total_core": 8,
  "total_optional": 6,
  "reasoning": "why these dependencies match project needs"
}}"""


async def dependency_agent(shared_state: Dict, architecture_data: Dict) -> Dict:
    """Recommend minimal, complete set of dependencies"""
    try:
        logger.info("📦 [PARALLEL] Dependency Agent starting...")
        
        project_type = shared_state.get("project_type", "web app")
        language = architecture_data.get("language", "JavaScript")
        framework = architecture_data.get("framework", "Express.js")
        async_required = architecture_data.get("async_required", False)
        domain_context = shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {}
        hints = backend_hints(domain_context)
        
        prompt = DEPENDENCY_PROMPT.format(
            project_type=project_type,
            language=language,
            framework=framework,
            async_required=str(async_required)
        )
        prompt = prompt + "\n\nDOMAIN CONTEXT:\n" + domain_context_summary(domain_context)
        
        response_text = await asyncio.to_thread(get_llm_response, prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        result = extract_json(response_text)
        result = _apply_domain_context_to_deps(result, framework, hints)
        logger.info(f"✅ Dependency Agent: {result.get('total_core')} core + {result.get('total_optional')} optional")
        return result
        
    except Exception as e:
        logger.error(f"Dependency Agent failed: {e}", exc_info=True)
        return _fallback_dependency_context(
            architecture_data.get("framework", "Express.js"),
            shared_state.get("domain_context", {}) if isinstance(shared_state.get("domain_context"), dict) else {},
        )


def _apply_domain_context_to_deps(result: dict, framework: str, hints: dict) -> dict:
    core = result.get("core_libraries", []) if isinstance(result.get("core_libraries", []), list) else []
    optional = result.get("optional_libraries", {}) if isinstance(result.get("optional_libraries", {}), dict) else {}
    preferred = []
    if framework and "node" in framework.lower():
        preferred = ["express", "jsonwebtoken", "prisma", "cors", "dotenv", "bcrypt"]
    elif framework and "fastapi" in framework.lower():
        preferred = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "passlib[bcrypt]"]
    elif framework and "spring" in framework.lower():
        preferred = ["spring-boot-starter-web", "spring-boot-starter-security", "spring-boot-starter-validation", "spring-boot-starter-data-jpa"]

    preferred.extend(hints.get("dependencies", []))
    result["core_libraries"] = merge_unique(core, preferred, limit=8)
    if not optional and hints.get("models"):
        result["optional_libraries"] = {"row-level-security": "multi-tenant safeguards"} if framework and "spring" in framework.lower() else {}
    return result


def _fallback_dependency_context(framework: str, domain_context: dict) -> dict:
    hints = backend_hints(domain_context)
    if framework and "node" in framework.lower():
        core = ["express", "jsonwebtoken", "prisma", "cors", "dotenv", "bcrypt"]
        optional = {"multer": "file uploads", "socket.io": "real-time updates", "zod": "schema validation"}
    elif framework and "fastapi" in framework.lower():
        core = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "passlib[bcrypt]"]
        optional = {"redis": "caching and sessions", "websockets": "real-time features", "pytest": "testing framework"}
    else:
        core = ["spring-boot-starter-web", "spring-boot-starter-security", "spring-boot-starter-data-jpa", "jjwt-api"]
        optional = {"lombok": "boilerplate reduction", "flyway": "migrations", "springdoc-openapi": "api docs"}

    core = merge_unique(core, hints.get("dependencies", []), limit=8)
    return {
        "core_libraries": core,
        "optional_libraries": optional,
        "total_core": len(core),
        "total_optional": len(optional),
        "reasoning": "Fallback: domain-aware defaults applied after error",
    }


async def orchestrate_backend_planning(validation_output: Dict) -> Dict:
    """
    Run all 6 agents IN PARALLEL for fast, intelligent backend planning.
    
    Flow:
    1. Pass shared_state to all agents
    2. Run concurrently with a shared 75s timeout
    3. Collect results
    4. Merge into final BackendArchitecturePlan
    """
    
    request_start = time.perf_counter()
    shared_state = dict(validation_output or {})
    shared_state["domain_context"] = build_domain_context(shared_state)
    architecture_hint = {
        "framework": shared_state.get("user_stack", {}).get("backend", "Express.js"),
        "language": "JavaScript" if "node" in str(shared_state.get("user_stack", {}).get("backend", "")).lower() or "express" in str(shared_state.get("user_stack", {}).get("backend", "")).lower() else "Python",
    }
    
    logger.info("BACKEND ORCHESTRATOR STARTED")
    logger.info("\n" + "="*80)
    logger.info("🚀 PARALLEL MULTI-AGENT BACKEND PLANNING STARTING")
    logger.info("="*80)
    logger.info("Running 6 agents in PARALLEL (not sequential)")
    logger.info("Expected time: 30-45 seconds (not 3-5 minutes)")
    logger.info("="*80 + "\n")
    
    try:
        # Run all 6 agents concurrently
        logger.info("Launching agents...")
        results = await asyncio.wait_for(
            asyncio.gather(
                _run_profiled_agent("Architecture Agent", architecture_agent(shared_state)),
                _run_profiled_agent("Auth Agent", auth_agent(shared_state)),
                _run_profiled_agent("Endpoint Agent", endpoint_agent(shared_state)),
                _run_profiled_agent("Database Agent", database_agent(shared_state)),
                _run_profiled_agent("Folder Structure Agent", folder_structure_agent(shared_state)),
                _run_profiled_agent("Dependency Agent", dependency_agent(shared_state, architecture_hint)),
            ),
            timeout=75,
        )

        (arch, arch_perf), (auth, auth_perf), (endpoints, endpoint_perf), (db, db_perf), (folder, folder_perf), (deps, dep_perf) = results
        backend_perf = [arch_perf, auth_perf, db_perf, endpoint_perf, dep_perf, folder_perf]

        logger.info("[ARCHITECTURE AGENT OUTPUT]\n%s", json.dumps(arch, indent=2, default=str))
        logger.info("[AUTH AGENT OUTPUT]\n%s", json.dumps(auth, indent=2, default=str))
        logger.info("[ENDPOINT AGENT OUTPUT]\n%s", json.dumps(endpoints, indent=2, default=str))
        logger.info("[DATABASE AGENT OUTPUT]\n%s", json.dumps(db, indent=2, default=str))
        logger.info("[FOLDER STRUCTURE AGENT OUTPUT]\n%s", json.dumps(folder, indent=2, default=str))
        logger.info("[DEPENDENCY AGENT OUTPUT]\n%s", json.dumps(deps, indent=2, default=str))
        
        # Update shared state with architecture info for dependent agents
        shared_state["_framework"] = arch.get("framework")
        shared_state["_language"] = arch.get("language")
        
        logger.info("\n" + "="*80)
        logger.info("✅ ALL AGENTS COMPLETE")
        logger.info("="*80)
        
        # Collect results for merger
        all_results = {
            "architecture": arch,
            "authentication": auth,
            "endpoints": endpoints,
            "database": db,
            "folder_structure": folder,
            "dependencies": deps,
        }
        
        logger.info("\nAgent Results Summary:")
        logger.info(f"  🏗️  Architecture: {arch.get('framework')} ({arch.get('language')})")
        logger.info(f"  🔐 Auth: {auth.get('method')}")
        logger.info(f"  📡 Endpoints: {endpoints.get('total_count', 0)}")
        logger.info(f"  💾 Database: {db.get('type')} + {db.get('orm')}")
        logger.info(f"  📁 Structure: {folder.get('structure_type')}")
        logger.info(f"  📦 Dependencies: {deps.get('total_core', 0)} core + {deps.get('total_optional', 0)} optional")
        
        logger.info("\nMerging results into final BackendArchitecturePlan...")

        # Import here to avoid circular imports
        from .merger_parallel import merge_agent_results
        merge_start = time.perf_counter()
        final_result = merge_agent_results(all_results, validation_output)
        merge_time_ms = int((time.perf_counter() - merge_start) * 1000)
        pipeline_total_ms = int((time.perf_counter() - request_start) * 1000)

        logger.info("[PERF]\nBackend Merge Time: %d ms", merge_time_ms)
        logger.info("[PERF]\nBackend Pipeline Total: %d ms", pipeline_total_ms)
        logger.info("=========================\nPERFORMANCE SUMMARY\n=========================")
        logger.info("Backend:")
        for item in backend_perf:
            logger.info("- %s: %.2fs", item["agent"], item["execution_time_ms"] / 1000)
        logger.info("Merge: %.2fs", merge_time_ms / 1000)
        logger.info("TOTAL: %.2fs", pipeline_total_ms / 1000)

        if isinstance(final_result, dict):
            final_result["_perf"] = {
                "pipeline_total_ms": pipeline_total_ms,
                "merge_time_ms": merge_time_ms,
                "agents": backend_perf,
            }
        
        logger.info("\n" + "="*80)
        logger.info("✅ PARALLEL PIPELINE COMPLETE - RETURNING FINAL PLAN")
        logger.info("="*80 + "\n")
        
        return final_result
        
    except asyncio.TimeoutError:
        logger.error("❌ Pipeline timeout: One or more agents exceeded 75s limit")
        return error_response("Backend planning agents timed out (75s limit)", shared_state)
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
        return error_response(f"Orchestration failed: {str(e)}", shared_state)


def error_response(message: str, validation_output: Dict | None = None) -> Dict:
    """Return error response with valid defaults"""
    backend_stack = (validation_output or {}).get("user_stack", {}).get("backend", "FastAPI") if isinstance(validation_output, dict) else "FastAPI"
    framework = backend_stack if isinstance(backend_stack, str) and backend_stack else "FastAPI"
    framework_lower = framework.lower()
    if "node" in framework_lower or "express" in framework_lower:
        framework = "Node.js"
        language = "JavaScript"
        auth_libraries = ["jsonwebtoken", "bcrypt"]
        database_orm = "Prisma"
        core_libraries = ["express", "jsonwebtoken", "prisma", "cors", "dotenv", "bcrypt"]
    elif "spring" in framework_lower:
        framework = "Spring Boot"
        language = "Java"
        auth_libraries = ["Spring Security", "jjwt-api"]
        database_orm = "Spring Data JPA"
        core_libraries = ["spring-boot-starter-web", "spring-boot-starter-security", "spring-boot-starter-data-jpa"]
    else:
        framework = "FastAPI"
        language = "Python"
        auth_libraries = ["python-jose", "passlib[bcrypt]"]
        database_orm = "SQLAlchemy"
        core_libraries = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "passlib[bcrypt]"]
    return {
        "status": "error",
        "framework": framework,
        "language": language,
        "api_style": "REST",
        "authentication": {
            "method": "JWT",
            "storage": "httpOnly cookies",
            "libraries": auth_libraries,
            "security_best_practices": []
        },
        "database": {
            "type": "PostgreSQL",
            "orm": database_orm,
            "connection_pool": True
        },
        "suggested_endpoints": [],
        "folder_structure": [],
        "core_libraries": core_libraries,
        "optional_libraries": {},
        "reasoning": f"ERROR: {message}"
    }
