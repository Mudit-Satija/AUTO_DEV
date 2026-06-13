import os

knowledge_dir = "D:/projects/AUTO_DEV/knowledge"
for root, dirs, files in os.walk(knowledge_dir):
    for f in files:
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        print(f"{path}: {size} chars")

# Also check what gets loaded for ExpenseFlow
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

knowledge = retrieve_knowledge(srs)
print("\n=== Retrieved Knowledge for ExpenseFlow ===")
for category, entries in knowledge.items():
    print(f"\n{category.upper()}:")
    for entry in entries:
        content = entry.get("content", "")
        fname = entry.get("file", "")
        print(f"  {fname}: {len(content)} chars")