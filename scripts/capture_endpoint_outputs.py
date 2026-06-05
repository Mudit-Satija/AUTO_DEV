import json
import backend_agents.endpoint_agent as ep

# Deterministic mock LLM response simulating a model biased toward auth endpoints
sample_response_text = '''[
    {"method": "POST", "path": "/api/auth/register", "description": "Register user", "auth_required": false},
    {"method": "POST", "path": "/api/auth/login", "description": "Login user", "auth_required": false},
    {"method": "GET", "path": "/api/users/me", "description": "Get current user", "auth_required": true},
    {"method": "GET", "path": "/api/projects", "description": "List projects", "auth_required": true},
    {"method": "POST", "path": "/api/projects", "description": "Create project", "auth_required": true}
]'''

# Monkeypatch the LLM call in the module
ep.get_llm_response = lambda prompt: sample_response_text

validation_output = {
    "project_type": "SaaS",
    "feedback": "Jira-like project management SaaS",
    "domain_context": {"domain": "project_management"},
}

result = ep.analyze_endpoints(validation_output)
print(json.dumps(result, indent=2))
