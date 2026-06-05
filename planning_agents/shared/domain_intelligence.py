"""Deterministic domain extraction for planning pipelines.

This module classifies the project domain from existing validation output and
derives lightweight planning hints that can be threaded through all agents
without adding extra LLM calls.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Tuple


GENERAL_DOMAIN = {
    "domain": "general_saas",
    "label": "general SaaS",
    "confidence": 0.2,
    "entities": ["user", "record", "dashboard", "settings"],
    "features": ["authentication", "crud", "search", "analytics"],
    "backend": {
        "preferred_endpoints": [
            "/api/auth/login",
            "/api/auth/logout",
            "/api/users/me",
            "/api/dashboard",
            "/api/search",
        ],
        "preferred_models": ["user", "account", "session", "audit_log"],
        "preferred_modules": ["domains/auth", "domains/users", "domains/audit"],
        "preferred_dependencies": ["auth", "validation", "logging"],
        "preferred_patterns": ["RBAC", "service layer", "audit trail"],
    },
    "frontend": {
        "preferred_components": ["Header", "Sidebar", "ContentArea", "DataTable", "FilterBar"],
        "preferred_routes": ["/dashboard", "/settings", "/profile"],
        "preferred_layout_sections": ["header", "sidebar", "content", "footer"],
        "preferred_ui_patterns": ["dashboard shell", "list/detail view"],
        "preferred_motion": ["page transition", "loading skeleton"],
    },
    "database": {
        "preferred_tables": ["users", "sessions", "audit_logs", "settings"],
        "tenancy": "single-tenant",
    },
    "summary": "General SaaS with authentication, CRUD, dashboard, search, and analytics.",
}


DOMAIN_TEMPLATES = {
    "project_management": {
        "domain": "project_management",
        "label": "project management SaaS",
        "confidence": 0.98,
        "entities": [
            "workspace",
            "project",
            "board",
            "task",
            "sprint",
            "comment",
            "attachment",
            "activity_log",
            "notification",
            "team",
            "role",
            "permission",
        ],
        "features": [
            "kanban",
            "RBAC",
            "notifications",
            "file uploads",
            "activity logs",
            "analytics dashboard",
            "team workspaces",
            "mentions",
            "search",
        ],
        "backend": {
            "preferred_endpoints": [
                "/api/workspaces",
                "/api/projects",
                "/api/boards",
                "/api/tasks",
                "/api/comments",
                "/api/attachments",
                "/api/activity",
                "/api/notifications",
                "/api/teams",
                "/api/reports",
            ],
            "preferred_models": [
                "workspace",
                "project",
                "board",
                "task",
                "sprint",
                "comment",
                "attachment",
                "activity_log",
                "notification",
                "team_member",
                "permission",
            ],
            "preferred_modules": [
                "domains/workspaces",
                "domains/projects",
                "domains/boards",
                "domains/tasks",
                "domains/comments",
                "domains/attachments",
                "domains/activity",
                "domains/notifications",
                "domains/teams",
                "domains/reports",
            ],
            "preferred_dependencies": ["RBAC", "file uploads", "notifications", "analytics"],
            "preferred_patterns": ["multi-tenancy", "event-driven activity logging", "board-centric workflow"],
        },
        "frontend": {
            "preferred_components": [
                "WorkspaceSidebar",
                "ProjectBoard",
                "KanbanColumn",
                "TaskCard",
                "TaskDetailsPanel",
                "ActivityFeed",
                "NotificationCenter",
                "TeamMemberList",
                "AttachmentUploader",
                "AnalyticsSummaryCard",
            ],
            "preferred_routes": [
                "/workspaces",
                "/projects",
                "/boards",
                "/tasks",
                "/activity",
                "/notifications",
                "/analytics",
            ],
            "preferred_layout_sections": ["workspace switcher", "board view", "detail drawer", "activity stream"],
            "preferred_ui_patterns": ["kanban board", "split-pane detail view", "notification drawer"],
            "preferred_motion": ["drag and drop", "status change animation", "optimistic save feedback"],
        },
        "database": {
            "preferred_tables": [
                "workspaces",
                "projects",
                "boards",
                "tasks",
                "task_comments",
                "attachments",
                "activity_logs",
                "notifications",
                "teams",
                "permissions",
            ],
            "tenancy": "workspace scoped with row-level permissions",
        },
        "summary": "Project management SaaS with workspaces, projects, tasks, boards, RBAC, notifications, uploads, activity logs, and analytics.",
    },
    "collaboration_messaging": {
        "domain": "collaboration_messaging",
        "label": "collaboration and messaging SaaS",
        "confidence": 0.95,
        "entities": ["workspace", "channel", "message", "thread", "member", "presence", "notification"],
        "features": ["real-time messaging", "presence", "mentions", "reactions", "attachments", "search"],
        "backend": {
            "preferred_endpoints": ["/api/workspaces", "/api/channels", "/api/messages", "/api/presence", "/api/notifications"],
            "preferred_models": ["workspace", "channel", "message", "thread", "presence", "notification"],
            "preferred_modules": ["domains/workspaces", "domains/channels", "domains/messages", "domains/presence"],
            "preferred_dependencies": ["real-time messaging", "presence tracking", "notifications"],
            "preferred_patterns": ["event-driven messaging", "presence service"],
        },
        "frontend": {
            "preferred_components": ["WorkspaceSidebar", "ChannelList", "MessageThread", "Composer", "PresencePill", "NotificationCenter"],
            "preferred_routes": ["/workspaces", "/channels", "/messages", "/notifications"],
            "preferred_layout_sections": ["workspace nav", "channel list", "message thread", "composer"],
            "preferred_ui_patterns": ["chat timeline", "presence indicators"],
            "preferred_motion": ["message arrival", "typing indicator"],
        },
        "database": {
            "preferred_tables": ["workspaces", "channels", "messages", "threads", "presence", "notifications"],
            "tenancy": "workspace scoped",
        },
        "summary": "Real-time collaboration and messaging SaaS with workspaces, channels, messages, presence, and notifications.",
    },
    "ecommerce": {
        "domain": "ecommerce",
        "label": "ecommerce platform",
        "confidence": 0.95,
        "entities": ["store", "product", "cart", "order", "payment", "inventory", "customer"],
        "features": ["catalog", "checkout", "payments", "inventory", "shipping", "promotions"],
        "backend": {
            "preferred_endpoints": ["/api/products", "/api/cart", "/api/orders", "/api/payments", "/api/inventory"],
            "preferred_models": ["product", "cart", "order", "payment", "inventory", "customer"],
            "preferred_modules": ["domains/products", "domains/cart", "domains/orders", "domains/payments", "domains/inventory"],
            "preferred_dependencies": ["checkout", "inventory", "payments"],
            "preferred_patterns": ["catalog service", "order orchestration"],
        },
        "frontend": {
            "preferred_components": ["ProductGrid", "ProductCard", "CartDrawer", "CheckoutStepper", "OrderSummary", "FilterSidebar"],
            "preferred_routes": ["/products", "/cart", "/checkout", "/orders"],
            "preferred_layout_sections": ["catalog", "filters", "cart", "checkout"],
            "preferred_ui_patterns": ["browse and buy", "checkout funnel"],
            "preferred_motion": ["cart add feedback", "checkout progress"],
        },
        "database": {
            "preferred_tables": ["products", "inventory", "carts", "orders", "payments", "customers"],
            "tenancy": "store scoped",
        },
        "summary": "Ecommerce platform with catalog, cart, checkout, orders, payments, and inventory management.",
    },
    "analytics_dashboard": {
        "domain": "analytics_dashboard",
        "label": "analytics and reporting dashboard",
        "confidence": 0.9,
        "entities": ["dashboard", "metric", "report", "chart", "filter", "segment", "alert"],
        "features": ["dashboards", "reports", "filters", "alerts", "exports", "segments"],
        "backend": {
            "preferred_endpoints": ["/api/metrics", "/api/reports", "/api/filters", "/api/exports", "/api/alerts"],
            "preferred_models": ["dashboard", "metric", "report", "segment", "alert", "export_job"],
            "preferred_modules": ["domains/metrics", "domains/reports", "domains/alerts", "domains/exports"],
            "preferred_dependencies": ["reporting", "aggregation", "exports"],
            "preferred_patterns": ["read-optimized analytics", "reporting pipeline"],
        },
        "frontend": {
            "preferred_components": ["MetricCard", "ChartPanel", "FilterBar", "ReportTable", "AlertBanner", "ExportButton"],
            "preferred_routes": ["/dashboard", "/reports", "/metrics", "/alerts"],
            "preferred_layout_sections": ["chart grid", "filters", "report panel"],
            "preferred_ui_patterns": ["dashboard overview", "report drilldown"],
            "preferred_motion": ["chart reveal", "loading shimmer"],
        },
        "database": {
            "preferred_tables": ["dashboards", "metrics", "reports", "segments", "alerts", "exports"],
            "tenancy": "tenant scoped",
        },
        "summary": "Analytics dashboard with dashboards, metrics, reports, filters, alerts, and exports.",
    },
}


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _collect_text(validation_output: Dict[str, Any] | None) -> str:
    validation_output = validation_output or {}
    parts: List[str] = []
    if isinstance(validation_output.get("project_type"), str):
        parts.append(validation_output["project_type"])
    if isinstance(validation_output.get("feedback"), str):
        parts.append(validation_output["feedback"])
    if isinstance(validation_output.get("reasoning"), str):
        parts.append(validation_output["reasoning"])
    user_stack = validation_output.get("user_stack", {}) if isinstance(validation_output.get("user_stack"), dict) else {}
    for key in ("backend", "frontend", "database", "deployment", "realtime"):
        value = user_stack.get(key)
        if isinstance(value, str):
            parts.append(value)
    for key in ("missing_requirements", "features", "tags"):
        value = validation_output.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
    return " ".join(parts).lower()


def _score_domain(text: str, keywords: Iterable[str]) -> Tuple[int, List[str]]:
    matched: List[str] = []
    score = 0
    for keyword in keywords:
        normalized = _normalize_text(keyword)
        if normalized and normalized in text:
            score += 1
            matched.append(keyword)
    return score, matched


def build_domain_context(validation_output: Dict[str, Any] | None) -> Dict[str, Any]:
    """Extract a deterministic domain context from validation output."""

    text = _collect_text(validation_output)
    best_domain = "general_saas"
    best_score = 0
    best_matches: List[str] = []

    domain_keywords = {
        "project_management": [
            "jira",
            "trello",
            "asana",
            "project management",
            "task board",
            "kanban",
            "workspace",
            "team workspace",
            "activity log",
            "activity logs",
            "notification",
            "file upload",
            "rbac",
            "role based access control",
            "sprint",
            "backlog",
            "issue tracker",
            "collaborative todo",
            "project management saas",
        ],
        "collaboration_messaging": ["chat", "messaging", "slack", "presence", "typing indicator", "realtime collaboration", "collaborative chat"],
        "ecommerce": ["ecommerce", "store", "checkout", "cart", "product catalog", "inventory", "payments"],
        "analytics_dashboard": ["analytics", "dashboard", "reporting", "metrics", "chart", "insights", "exports"],
    }

    for domain, keywords in domain_keywords.items():
        score, matches = _score_domain(text, keywords)
        if score > best_score:
            best_domain = domain
            best_score = score
            best_matches = matches

    if best_domain in DOMAIN_TEMPLATES:
        template = deepcopy(DOMAIN_TEMPLATES[best_domain])
    else:
        template = deepcopy(GENERAL_DOMAIN)

    template["matched_terms"] = best_matches
    template["source"] = "deterministic keyword classification"
    template["raw_input"] = {
        "project_type": validation_output.get("project_type") if isinstance(validation_output, dict) else None,
        "feedback": validation_output.get("feedback") if isinstance(validation_output, dict) else None,
        "complexity": validation_output.get("complexity") if isinstance(validation_output, dict) else None,
    }
    return template


def domain_context_summary(domain_context: Dict[str, Any] | None) -> str:
    """Render a compact summary for prompts and logs."""

    context = domain_context or GENERAL_DOMAIN
    entities = ", ".join(context.get("entities", [])[:8]) or "N/A"
    features = ", ".join(context.get("features", [])[:8]) or "N/A"
    backend = context.get("backend", {}) if isinstance(context.get("backend"), dict) else {}
    frontend = context.get("frontend", {}) if isinstance(context.get("frontend"), dict) else {}
    database = context.get("database", {}) if isinstance(context.get("database"), dict) else {}

    parts = [
        f"Domain: {context.get('label', context.get('domain', 'general'))}",
        f"Entities: {entities}",
        f"Features: {features}",
    ]
    if backend.get("preferred_endpoints"):
        parts.append(f"Preferred endpoints: {', '.join(backend['preferred_endpoints'][:8])}")
    if frontend.get("preferred_components"):
        parts.append(f"Preferred components: {', '.join(frontend['preferred_components'][:8])}")
    if backend.get("preferred_modules"):
        parts.append(f"Preferred modules: {', '.join(backend['preferred_modules'][:8])}")
    if database.get("preferred_tables"):
        parts.append(f"Preferred tables: {', '.join(database['preferred_tables'][:8])}")
    return "\n".join(parts)


def frontend_hints(domain_context: Dict[str, Any] | None) -> Dict[str, List[str]]:
    context = domain_context or GENERAL_DOMAIN
    frontend = context.get("frontend", {}) if isinstance(context.get("frontend"), dict) else {}
    return {
        "components": list(frontend.get("preferred_components", [])),
        "routes": list(frontend.get("preferred_routes", [])),
        "layout_sections": list(frontend.get("preferred_layout_sections", [])),
        "ui_patterns": list(frontend.get("preferred_ui_patterns", [])),
        "motion": list(frontend.get("preferred_motion", [])),
    }


def backend_hints(domain_context: Dict[str, Any] | None) -> Dict[str, List[str]]:
    context = domain_context or GENERAL_DOMAIN
    backend = context.get("backend", {}) if isinstance(context.get("backend"), dict) else {}
    database = context.get("database", {}) if isinstance(context.get("database"), dict) else {}
    return {
        "endpoints": list(backend.get("preferred_endpoints", [])),
        "models": list(backend.get("preferred_models", [])),
        "modules": list(backend.get("preferred_modules", [])),
        "dependencies": list(backend.get("preferred_dependencies", [])),
        "patterns": list(backend.get("preferred_patterns", [])),
        "tables": list(database.get("preferred_tables", [])),
    }


def merge_unique(existing: Iterable[str], additions: Iterable[str], limit: int | None = None) -> List[str]:
    seen = set()
    merged: List[str] = []
    for value in list(existing) + list(additions):
        normalized = _normalize_text(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            merged.append(str(value))
        if limit is not None and len(merged) >= limit:
            break
    return merged
