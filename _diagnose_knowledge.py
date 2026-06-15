"""Diagnose what knowledge is retrieved for RecipeBook and whether it's used."""
import sys, json
sys.path.insert(0, '.')
from knowledge_retriever import retrieve_knowledge
from coding_agent.rules_engine import build_project_rules
from coding_agent.build_plan import generate_build_plan
from coding_agent.bundle_generator import build_bundle_prompt

srs = {
    "project_name": "RecipeBook",
    "project_description": "A recipe collection application",
    "complexity": "medium",
    "tech_stack": {"frontend": "React", "backend": "none", "database": "none"},
    "pages": [
        {"name": "Recipes", "entities": ["Recipe"]},
        {"name": "Add Recipe", "entities": ["Recipe"]},
        {"name": "Favorites", "entities": ["Recipe", "Favorite"]},
        {"name": "Dashboard", "entities": ["Recipe", "Favorite"]},
    ],
    "entities": [
        {"name": "Recipe", "fields": ["title", "ingredients", "instructions", "cookTime", "category"]},
        {"name": "Favorite", "fields": ["recipeId", "dateAdded"]},
    ],
    "flow": [],
    "roles": [],
    "requirements": [],
}

# Step 1: What knowledge is retrieved?
pr = build_project_rules(srs, srs["tech_stack"])
knowledge = retrieve_knowledge(srs)
pr["knowledge"] = knowledge

print("=== RETRIEVED KNOWLEDGE ===")
print(f"  Frontend files: {len(knowledge.get('frontend', []))}")
for e in knowledge.get('frontend', []):
    print(f"    {e['file']}: {len(e['content'])} chars, bundle={e.get('bundle','?')}")
print(f"  Backend files: {len(knowledge.get('backend', []))}")
for e in knowledge.get('backend', []):
    print(f"    {e['file']}: {len(e['content'])} chars, bundle={e.get('bundle','?')}")

# Step 2: Generate build plan
bp = generate_build_plan(pr)
pr["all_files"] = bp.get("files", [])

# Step 3: Reconstruct the Dashboard.jsx prompt
dash_blueprint = [f for f in bp["files"] if "Dashboard" in f.get("path", "")]
if dash_blueprint:
    prompt = build_bundle_prompt("frontend_dashboard", dash_blueprint, pr)
    print(f"\n=== DASHBOARD.JSX PROMPT ({len(prompt)} chars) ===")
    # Check if knowledge is actually in the prompt
    for kw in ["bulletproof", "CRUD", "localStorage", "services/api", "ReactDOM", "export default"]:
        count = prompt.lower().count(kw.lower())
        print(f"  Contains '{kw}': {count > 0} ({count} occurrences)")
    # Show the DATA ACCESS section
    if "DATA ACCESS PATTERN" in prompt:
        idx = prompt.index("DATA ACCESS PATTERN")
        print(f"\n  DATA ACCESS section (from char {idx}):")
        print(prompt[idx:idx+500])
