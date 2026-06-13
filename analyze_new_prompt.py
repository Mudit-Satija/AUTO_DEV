import sys
sys.path.insert(0, "D:/projects/AUTO_DEV")

from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules
from coding_agent.bundle_generator import build_bundle_prompt, group_and_partition_files
from knowledge_retriever import retrieve_knowledge

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
build_plan = generate_build_plan(project_rules)
files = build_plan.get("files", [])
bundles = group_and_partition_files(files)

knowledge = retrieve_knowledge(srs)
project_rules["knowledge"] = knowledge

print("=== KNOWLEDGE BY BUNDLE ===")
for bundle, entries in knowledge.items():
    print(f"{bundle.upper()}:")
    for e in entries:
        print(f"  {e['file']}: {len(e['content'])} chars")

print("\n=== PROMPT SIZES BY BUNDLE ===")
for name, bps in bundles.items():
    bundle_type = "frontend" if "frontend" in name else "backend" if "backend" in name else "database" if "database" in name else "docs"
    prompt = build_bundle_prompt(name, bps, project_rules)
    print(f"{name} ({bundle_type}): {len(prompt)} chars ({len(prompt)//4} tokens)")
    for bp in bps:
        print(f"  {bp['path']}")