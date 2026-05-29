import asyncio
import json
import logging
from typing import Dict, List
from llm_client import get_llm_response

logger = logging.getLogger(__name__)

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
        
        prompt = ARCHITECTURE_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            backend=backend,
            realtime=realtime
        )
        
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON in architecture response")
            raise ValueError("No JSON found")
        
        result = json.loads(response_text[start:end])
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
        
        prompt = AUTH_PROMPT.format(
            project_type=project_type,
            framework=framework,
            language=language
        )
        
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON in auth response")
            raise ValueError("No JSON found")
        
        result = json.loads(response_text[start:end])
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
        
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON array in endpoint response")
            raise ValueError("No JSON array found")
        
        endpoints = json.loads(response_text[start:end])
        logger.info(f"✅ Endpoint Agent: {len(endpoints)} endpoints designed")
        return {"endpoints": endpoints, "total_count": len(endpoints)}
        
    except Exception as e:
        logger.error(f"Endpoint Agent failed: {e}", exc_info=True)
        return {
            "endpoints": [
                {"method": "POST", "path": "/api/auth/register", "description": "Register user", "auth_required": False, "category": "auth"},
                {"method": "POST", "path": "/api/auth/login", "description": "Login user", "auth_required": False, "category": "auth"},
                {"method": "GET", "path": "/api/users/me", "description": "Get current user", "auth_required": True, "category": "user"},
            ],
            "total_count": 3
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
        
        prompt = DATABASE_PROMPT.format(
            project_type=project_type,
            database=database,
            complexity=complexity
        )
        
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON in database response")
            raise ValueError("No JSON found")
        
        result = json.loads(response_text[start:end])
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
- Complex: src/domains/{domain}/routes, src/domains/{domain}/services, src/domains/{domain}/models
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
        
        prompt = FOLDER_PROMPT.format(
            project_type=project_type,
            complexity=complexity,
            language=language
        )
        
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON in folder response")
            raise ValueError("No JSON found")
        
        result = json.loads(response_text[start:end])
        logger.info(f"✅ Folder Structure Agent: {result.get('structure_type')} structure")
        return result
        
    except Exception as e:
        logger.error(f"Folder Structure Agent failed: {e}", exc_info=True)
        return {
            "folders": [
                {"path": "src/", "type": "directory", "purpose": "main source code"},
                {"path": "src/core/", "type": "directory", "purpose": "shared utilities"},
                {"path": "src/domains/", "type": "directory", "purpose": "domain-driven modules"},
                {"path": "tests/", "type": "directory", "purpose": "test files"},
                {"path": "config/", "type": "directory", "purpose": "configuration"}
            ],
            "total_directories": 5,
            "structure_type": "modular",
            "reasoning": f"Default structure due to error: {str(e)}"
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
        
        prompt = DEPENDENCY_PROMPT.format(
            project_type=project_type,
            language=language,
            framework=framework,
            async_required=str(async_required)
        )
        
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            raise ValueError("Response is not a string")
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            logger.error("No JSON in dependency response")
            raise ValueError("No JSON found")
        
        result = json.loads(response_text[start:end])
        logger.info(f"✅ Dependency Agent: {result.get('total_core')} core + {result.get('total_optional')} optional")
        return result
        
    except Exception as e:
        logger.error(f"Dependency Agent failed: {e}", exc_info=True)
        return {
            "core_libraries": ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "bcrypt"],
            "optional_libraries": {
                "redis": "caching and sessions",
                "websockets": "real-time features",
                "pytest": "testing framework"
            },
            "total_core": 6,
            "total_optional": 3,
            "reasoning": f"Default minimal set due to error: {str(e)}"
        }


async def orchestrate_backend_planning(validation_output: Dict) -> Dict:
    """
    Run all 6 agents IN PARALLEL for fast, intelligent backend planning.
    
    Flow:
    1. Pass shared_state to all agents
    2. Run concurrently with 120s timeout each
    3. Collect results
    4. Merge into final BackendArchitecturePlan
    """
    
    shared_state = validation_output
    
    logger.info("\n" + "="*80)
    logger.info("🚀 PARALLEL MULTI-AGENT BACKEND PLANNING STARTING")
    logger.info("="*80)
    logger.info("Running 6 agents in PARALLEL (not sequential)")
    logger.info("Expected time: 30-45 seconds (not 3-5 minutes)")
    logger.info("="*80 + "\n")
    
    try:
        # Run all 6 agents concurrently
        logger.info("Launching agents...")
        results = await asyncio.gather(
            architecture_agent(shared_state),
            auth_agent(shared_state),
            endpoint_agent(shared_state),
            database_agent(shared_state),
            folder_structure_agent(shared_state),
            dependency_agent(shared_state, {}),  # Will get architecture_data below
            timeout=120  # 2 min per agent
        )
        
        arch, auth, endpoints, db, folder, deps = results
        
        # Update shared state with architecture info for dependent agents
        shared_state["_framework"] = arch.get("framework")
        shared_state["_language"] = arch.get("language")
        
        # Re-run dependency agent with architecture data if needed
        deps = await dependency_agent(shared_state, arch)
        
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
        from merger_parallel import merge_agent_results
        final_result = merge_agent_results(all_results, validation_output)
        
        logger.info("\n" + "="*80)
        logger.info("✅ PARALLEL PIPELINE COMPLETE - RETURNING FINAL PLAN")
        logger.info("="*80 + "\n")
        
        return final_result
        
    except asyncio.TimeoutError:
        logger.error("❌ Pipeline timeout: One or more agents exceeded 120s limit")
        return error_response("Backend planning agents timed out (120s limit)")
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
        return error_response(f"Orchestration failed: {str(e)}")


def error_response(message: str) -> Dict:
    """Return error response with valid defaults"""
    return {
        "status": "error",
        "framework": "FastAPI",
        "language": "Python",
        "api_style": "REST",
        "authentication": {
            "method": "JWT",
            "storage": "httpOnly cookies",
            "libraries": [],
            "security_best_practices": []
        },
        "database": {
            "type": "PostgreSQL",
            "orm": "SQLAlchemy",
            "connection_pool": True
        },
        "suggested_endpoints": [],
        "folder_structure": [],
        "core_libraries": [],
        "optional_libraries": {},
        "reasoning": f"ERROR: {message}"
    }
