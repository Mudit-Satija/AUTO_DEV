import backend_agents.endpoint_agent as endpoint_agent


def test_project_management_endpoints_prioritized_and_auth_limited(monkeypatch):
    sample_response_text = '''[
        {"method": "POST", "path": "/api/auth/register", "description": "Register user", "auth_required": false},
        {"method": "POST", "path": "/api/auth/login", "description": "Login user", "auth_required": false},
        {"method": "GET", "path": "/api/users/me", "description": "Get current user", "auth_required": true},
        {"method": "GET", "path": "/api/projects", "description": "List projects", "auth_required": true},
        {"method": "POST", "path": "/api/projects", "description": "Create project", "auth_required": true}
    ]'''

    monkeypatch.setattr(endpoint_agent, "get_llm_response", lambda prompt: sample_response_text)

    validation_output = {
        "project_type": "SaaS",
        "feedback": "Jira-like project management SaaS",
        "domain_context": {"domain": "project_management"},
    }

    result = endpoint_agent.analyze_endpoints(validation_output)
    endpoints = result.get("endpoints", [])
    paths = [e.get("path") for e in endpoints]

    # Domain endpoints should be present and prioritized
    assert "/api/workspaces" in paths
    assert "/api/projects" in paths

    # Non-essential user endpoint should be suppressed
    assert "/api/users/me" not in paths

    # Essential auth endpoints allowed but should not dominate (there should be domain endpoints before auth)
    auth_positions = [i for i, p in enumerate(paths) if p in ("/api/auth/login", "/api/auth/register")]
    assert auth_positions, "Auth endpoints should be present"
    assert min(auth_positions) >= 5, "Auth endpoints should appear after domain endpoints"

    # Output schema preserved
    for e in endpoints:
        assert set(e.keys()) >= {"method", "path", "description", "auth_required"}
