from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules

srs = {
    "project_name": "ExpenseFlow",
    "project_description": "",
    "complexity": "medium",
    "pages": [
        {"name": "Dashboard", "purpose": "", "entities": []},
        {"name": "Transactions", "purpose": "", "entities": []},
        {"name": "Budgets", "purpose": "", "entities": []},
        {"name": "Reports", "purpose": "", "entities": []},
        {"name": "Analytics", "purpose": "", "entities": []},
    ],
    "entities": [
        {"name": "Transaction", "fields": ["name", "description", "createdAt"], "description": ""},
        {"name": "Budget", "fields": ["name", "description", "createdAt"], "description": ""},
        {"name": "Category", "fields": ["name", "description", "createdAt"], "description": ""},
    ],
    "flow": [
        {"name": "Add Transaction", "steps": [], "entities": []},
        {"name": "Edit Transaction", "steps": [], "entities": []},
        {"name": "Delete Transaction", "steps": [], "entities": []},
        {"name": "Create Budget", "steps": [], "entities": []},
        {"name": "Update Budget", "steps": [], "entities": []},
        {"name": "Track Spending", "steps": [], "entities": []},
        {"name": "Generate Reports", "steps": [], "entities": []},
        {"name": "View Analytics", "steps": [], "entities": []},
        {"name": "Filter Transactions", "steps": [], "entities": []},
    ],
    "roles": [],
    "tech_stack": {"frontend": "React", "backend": "Express.js", "database": "MongoDB"},
    "requirements": [],
}

project_rules = build_project_rules(srs, {"backend": "Express.js", "frontend": "React", "database": "MongoDB"})
plan = generate_build_plan(project_rules)
print(f"Total files: {len(plan['files'])}")
for f in plan["files"]:
    print(f"  {f['path']} ({f.get('bundle', 'no-bundle')})")