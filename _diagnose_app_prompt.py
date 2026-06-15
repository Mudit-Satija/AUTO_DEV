"""Diagnose App.jsx prompt - encoding-safe."""
import sys
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
    "pages": [{"name": "Recipes", "entities": ["Recipe"]}],
    "entities": [{"name": "Recipe", "fields": ["title"]}],
    "flow": [], "roles": [], "requirements": [],
}

pr = build_project_rules(srs, srs["tech_stack"])
pr["knowledge"] = retrieve_knowledge(srs)
bp = generate_build_plan(pr)
pr["all_files"] = bp.get("files", [])

app_bp = [f for f in bp["files"] if "App.jsx" in f.get("path", "")]
if app_bp:
    prompt = build_bundle_prompt("frontend_app", app_bp, pr)
    
    # Save to file to avoid encoding issues
    with open("C:\\Users\\User\\AppData\\Local\\Temp\\app_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"Prompt saved: {len(prompt)} chars, {prompt.count(chr(10))+1} lines")
    
    # Check critical terms (count only, no context)
    checks = {
        "export default": "export default" in prompt,
        "ReactDOM": "ReactDOM" in prompt,
        "main.jsx": "main.jsx" in prompt,
        "mount": "mount" in prompt.lower(),
        "createRoot": "createRoot" in prompt,
        "render(": "render(" in prompt,
        "bulletproof_react": "bulletproof_react" in prompt,
        "crud.md": "crud.md" in prompt,
    }
    for kw, found in checks.items():
        print(f"  '{kw}': {'FOUND' if found else 'NOT FOUND'}")

# Show file inventory section (lines 20-50)
print("\n=== FILE INVENTORY + INSTRUCTIONS ===")
with open("C:\\Users\\User\\AppData\\Local\\Temp\\app_prompt.txt", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if 25 <= i <= 55:
            print(f"{i}: {line.rstrip()}")
        if i > 60:
            break
