import sys
sys.path.insert(0, "D:/projects/AUTO_DEV")

from knowledge_retriever import retrieve_knowledge, _PATTERN_KEYWORDS, _STACK_TO_ARCHITECTURE, _STACK_TO_UI
from coding_agent.rules_engine import build_project_rules
import re

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

# === ARCHITECTURE SELECTION ===
print("=== ARCHITECTURE SELECTION ===")
tech_stack = srs.get("tech_stack", {})
backend = (tech_stack.get("backend") or "").lower()
frontend = (tech_stack.get("frontend") or "").lower()
print(f"Backend: {backend}")
print(f"Frontend: {frontend}")

arch_hits = set()
for stack_key, arch_file in _STACK_TO_ARCHITECTURE.items():
    if arch_file and stack_key in backend:
        arch_hits.add(arch_file)
        print(f"  MATCH: '{stack_key}' in backend '{backend}' -> {arch_file}")
for stack_key, arch_file in _STACK_TO_ARCHITECTURE.items():
    if arch_file and stack_key in frontend:
        arch_hits.add(arch_file)
        print(f"  MATCH: '{stack_key}' in frontend '{frontend}' -> {arch_file}")

print(f"\nArchitecture files selected: {sorted(arch_hits)}")

# === UI SELECTION ===
print("\n=== UI SELECTION ===")
ui_hits = set()
for stack_key, ui_file in _STACK_TO_UI.items():
    if ui_file and stack_key in frontend:
        ui_hits.add(ui_file)
        print(f"  MATCH: '{stack_key}' in frontend '{frontend}' -> {ui_file}")
print(f"UI files selected: {sorted(ui_hits)}")

# === PATTERN SELECTION ===
print("\n=== PATTERN SELECTION ===")
srs_entities = srs.get("entities", []) or []
srs_pages = srs.get("pages", []) or []

text = (
    srs.get("project_name", "")
    + " "
    + srs.get("project_description", "")
    + " "
    + " ".join(p.get("name", "") for p in srs_pages)
    + " "
    + " ".join(e.get("name", "") for e in srs_entities)
    + " "
    + " ".join(f.get("name", "") for f in srs.get("flow", []))
).lower()

print(f"Search text: {text[:500]}...")

scored_patterns = []
for pattern_file, keywords in _PATTERN_KEYWORDS.items():
    if not keywords:
        print(f"  {pattern_file}: NO KEYWORDS (fallback)")
        continue
    matches = sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", text))
    kw_score = matches / len(keywords)
    
    srs_entity_names = {e.get("name", "").lower() for e in srs_entities}
    overlap = len(srs_entity_names & set(keywords))
    entity_score = overlap / len(srs_entity_names) if srs_entity_names else 0
    
    combined = (kw_score * 0.6) + (entity_score * 0.4)
    
    print(f"  {pattern_file}: keywords={keywords}")
    print(f"    kw_matches={matches}/{len(keywords)}={kw_score:.3f}, entity_overlap={overlap}/{len(srs_entity_names)}={entity_score:.3f}")
    print(f"    combined={combined:.3f} {'SELECTED' if combined > 0.15 else 'REJECTED'}")
    
    if combined > 0:
        scored_patterns.append((combined, pattern_file))

scored_patterns.sort(reverse=True, key=lambda x: x[0])
print(f"\nSorted patterns: {scored_patterns}")

# Fallback check
if not [p for p in scored_patterns if p[0] > 0.15]:
    print("  No patterns > 0.15, would fallback to crud.md")

# === FINAL RESULT ===
knowledge = retrieve_knowledge(srs)
print("\n=== FINAL RETRIEVED KNOWLEDGE ===")
for cat, entries in knowledge.items():
    print(f"\n{cat.upper()}:")
    for entry in entries:
        fname = entry.get("file", "")
        content = entry.get("content", "")
        score = entry.get("score", "N/A")
        print(f"  {fname} (score={score}): {len(content)} chars")