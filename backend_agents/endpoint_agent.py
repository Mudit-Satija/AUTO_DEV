import json
import logging
from llm_client import get_llm_response
from planning_agents.shared.json_utils import extract_json
from planning_agents.shared.rules import RuleManager
from planning_agents.shared.domain_intelligence import domain_context_summary, backend_hints, merge_unique

logger = logging.getLogger(__name__)

ENDPOINT_PROMPT = """You are an API design expert. Suggest 5-7 practical REST endpoints for this project.

RULES:
- Include auth endpoints (register, login)
- Include resource endpoints (CRUD)
- Return ONLY valid JSON array
- Each endpoint must have: method, path, description, auth_required

PROJECT TYPE: {project_type}

{rules}

Return this JSON array (NO other text):
[
    {{"method": "POST", "path": "/api/auth/register", "description": "Register user", "auth_required": false}},
    {{"method": "POST", "path": "/api/auth/login", "description": "Login user", "auth_required": false}},
    {{"method": "GET", "path": "/api/users/me", "description": "Get current user", "auth_required": true}}
]"""


def analyze_endpoints(validation_output: dict) -> dict:
    """Generate practical REST endpoints"""
    try:
        if not isinstance(validation_output, dict):
            validation_output = {}
            
        project_type = validation_output.get("project_type", "web app")
        domain_context = validation_output.get("domain_context", {}) if isinstance(validation_output.get("domain_context"), dict) else {}
        rules = RuleManager.from_validation_output(validation_output)
        
        # Build a prompt that prefers domain-aware examples when available.
        idx = ENDPOINT_PROMPT.find("Return this JSON array")
        prompt_head = ENDPOINT_PROMPT[:idx].format(
            project_type=project_type,
            rules=rules.prompt_context("endpoints") + "\n" + domain_context_summary(domain_context),
        )

        examples_text = ""
        # When domain hints exist, prefer backend endpoint hints as examples
        if domain_context.get("domain") == "project_management":
            hints = backend_hints(domain_context)
            preferred = hints.get("endpoints", [])
            domain_examples = []
            for p in preferred[:8]:
                desc = p.replace("/api/", "").strip("/").replace("-", " ").replace("_", " ")
                domain_examples.append({
                    "method": "GET",
                    "path": p,
                    "description": f"List {desc}",
                    "auth_required": True,
                })
            # add a few create endpoints to guide the model
            for p in preferred[:4]:
                noun = p.replace("/api/", "").strip("/")
                if noun.endswith("s"):
                    noun_singular = noun[:-1]
                else:
                    noun_singular = noun
                domain_examples.append({
                    "method": "POST",
                    "path": p,
                    "description": f"Create {noun_singular}",
                    "auth_required": True,
                })
            examples_text = json.dumps(domain_examples, indent=4)
        else:
            # Fall back to the original sample array included in the template
            arr_start = ENDPOINT_PROMPT.find("[", idx)
            examples_text = ENDPOINT_PROMPT[arr_start:]

        prompt = prompt_head + examples_text
        logger.info("→ Endpoint Agent: Generating endpoints...")
        response_text = get_llm_response(prompt)
        
        if not isinstance(response_text, str):
            logger.error("Response is not a string")
            return {"endpoints": []}
        
        endpoints = extract_json(response_text)
        endpoints = _apply_domain_context(endpoints, domain_context)
        logger.info(f"✓ Endpoint Agent: Generated {len(endpoints)} endpoints")
        return {"endpoints": endpoints}
        
    except Exception as e:
        logger.error(f"Endpoint Agent failed: {e}", exc_info=True)
        return {"endpoints": _apply_domain_context([], validation_output.get("domain_context", {}) if isinstance(validation_output, dict) else {})}


def _apply_domain_context(endpoints: list, domain_context: dict) -> list:
    if not isinstance(endpoints, list):
        endpoints = []

    if domain_context.get("domain") != "project_management":
        return endpoints

    domain_endpoints = [
        {"method": "GET", "path": "/api/workspaces", "description": "List workspaces", "auth_required": True},
        {"method": "POST", "path": "/api/workspaces", "description": "Create workspace", "auth_required": True},
        {"method": "GET", "path": "/api/projects", "description": "List projects", "auth_required": True},
        {"method": "POST", "path": "/api/projects", "description": "Create project", "auth_required": True},
        {"method": "GET", "path": "/api/tasks", "description": "List tasks", "auth_required": True},
        {"method": "POST", "path": "/api/tasks", "description": "Create task", "auth_required": True},
        {"method": "GET", "path": "/api/comments", "description": "List comments", "auth_required": True},
        {"method": "POST", "path": "/api/comments", "description": "Add comment", "auth_required": True},
        {"method": "GET", "path": "/api/activity", "description": "View activity log", "auth_required": True},
        {"method": "GET", "path": "/api/notifications", "description": "List notifications", "auth_required": True},
    ]

    merged = []
    seen = set()
    # limit non-essential auth endpoints when domain is project_management
    allowed_auth = {"/api/auth/login", "/api/auth/register"}
    for endpoint in domain_endpoints + endpoints:
        if not isinstance(endpoint, dict):
            continue
        path = str(endpoint.get("path", "")).strip().lower()
        if not path or path in seen:
            continue
        # Skip generic auth/user endpoints unless explicitly allowed
        if domain_context.get("domain") == "project_management":
            if (path.startswith("/api/auth") or path.startswith("/api/users")) and path not in allowed_auth:
                continue
        seen.add(path)
        merged.append({
            "method": str(endpoint.get("method", "GET")).upper(),
            "path": str(endpoint.get("path", "/api")),
            "description": str(endpoint.get("description", "API endpoint")),
            "auth_required": bool(endpoint.get("auth_required", True)),
        })

    return merged[:15]
