from planning_agents.shared.domain_intelligence import build_domain_context
from frontend_agents.layout_agent import _apply_domain_context as apply_layout_domain_context
from frontend_agents.component_agent import _apply_domain_context as apply_component_domain_context


def test_project_management_domain_context_is_detected():
    validation_output = {
        "project_type": "web app",
        "feedback": "Build a multi-tenant project management SaaS similar to Jira with role-based access control, notifications, file uploads, activity logs, analytics dashboard, and team workspaces.",
        "user_stack": {
            "backend": "Node.js",
            "frontend": "React",
            "database": "PostgreSQL",
        },
    }

    domain_context = build_domain_context(validation_output)

    assert domain_context["domain"] == "project_management"
    assert "workspace" in domain_context["entities"]
    assert "task" in domain_context["entities"]
    assert "/api/workspaces" in domain_context["backend"]["preferred_endpoints"]
    assert "WorkspaceSidebar" in domain_context["frontend"]["preferred_components"]


def test_frontend_layout_domain_enrichment_adds_project_management_routes():
    domain_context = build_domain_context({
        "project_type": "web app",
        "feedback": "Jira-like project management SaaS",
    })
    result = apply_layout_domain_context({"routing_structure": {"/": "Home"}, "navigation_menu": [], "structure": []}, domain_context)

    assert "/workspaces" in result["routing_structure"]
    assert "/boards" in result["routing_structure"]
    assert any(item["name"] == "WorkspaceSidebar" for item in result["structure"])
    assert any(item["label"] == "Projects" for item in result["navigation_menu"])


def test_frontend_component_domain_enrichment_adds_domain_components():
    domain_context = build_domain_context({
        "project_type": "web app",
        "feedback": "Jira-like project management SaaS",
    })
    result = apply_component_domain_context({"components": [{"name": "Button", "type": "atom", "props": ["label"]}], "component_library": "shadcn/ui"}, domain_context)

    component_names = {component["name"] for component in result["components"]}

    assert "WorkspaceSidebar" in component_names
    assert "ProjectBoard" in component_names
    assert "TaskCard" in component_names