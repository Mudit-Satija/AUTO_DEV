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

# Find frontend_2 bundle
frontend_2_files = bundles.get("frontend_2", [])
print(f"frontend_2 files: {len(frontend_2_files)}")
for f in frontend_2_files:
    print(f"  {f['path']}")

# Build the prompt
knowledge = retrieve_knowledge(srs)
project_rules["knowledge"] = knowledge
prompt = build_bundle_prompt("frontend_2", frontend_2_files, project_rules)

print(f"\n=== TOTAL PROMPT SIZE: {len(prompt)} chars ===")
print(f"=== ESTIMATED TOKENS: {len(prompt)//4} ===")

# Analyze sections
sections = prompt.split("### ")
print(f"\n=== SECTIONS ({len(sections)}) ===")
for i, sec in enumerate(sections):
    if not sec.strip():
        continue
    header = sec.split("\n")[0] if sec else ""
    print(f"  {i}: {header[:80]}... ({len(sec)} chars)")

# Check knowledge injection
print("\n=== KNOWLEDGE INJECTION ===")
for category, entries in knowledge.items():
    for entry in entries:
        fname = entry.get("file", "")
        content = entry.get("content", "")
        print(f"  {category}/{fname}: {len(content)} chars ({len(content)//4} tokens)")

# Check CSS classes and layouts size
from coding_agent.prompt_constraints import _CSS_CLASS_LIST, _PAGE_LAYOUTS
css_size = len(_CSS_CLASS_LIST)
layouts_size = sum(len(v) for v in _PAGE_LAYOUTS.values())
print(f"\n=== STATIC INJECTIONS ===")
print(f"  CSS Class List: {css_size} chars ({css_size//4} tokens)")
print(f"  Page Layouts: {layouts_size} chars ({layouts_size//4} tokens)")

# Break down prompt components
lines = prompt.split("\n")
system_inst = []
gen_inst = []
blueprint_data = []
requirement_lineage = []
knowledge_injected = []
examples = []
existing_context = []

current_section = "system"
for line in lines:
    if "Project context:" in line:
        current_section = "blueprint"
    elif "Use this exact delimiter" in line:
        current_section = "gen_inst"
    elif "Files to generate:" in line:
        current_section = "blueprint"
    elif "Instructions:" in line:
        current_section = "gen_inst"
    elif "### CSS CLASS REFERENCE" in line or "### PAGE LAYOUT TEMPLATES" in line:
        current_section = "knowledge"
    elif "### UI DESIGN CONVENTIONS" in line or "### DOMAIN PATTERNS" in line or "### ARCHITECTURE CONVENTIONS" in line:
        current_section = "knowledge"
    elif "### CSS COORDINATION RULES" in line:
        current_section = "gen_inst"
    elif "### VISUAL DESIGN STANDARDS" in line:
        current_section = "gen_inst"
    elif "### PAGE LAYOUT GUIDELINES" in line:
        current_section = "gen_inst"
    elif "### REFERENCE" in line:
        current_section = "knowledge"
    elif "### SEED DATA" in line or "### BACKEND API INTEGRATION" in line:
        current_section = "gen_inst"
    elif "### DATA FLOW AND STATE" in line:
        current_section = "gen_inst"

    if current_section == "system":
        system_inst.append(line)
    elif current_section == "gen_inst":
        gen_inst.append(line)
    elif current_section == "blueprint":
        blueprint_data.append(line)
    elif current_section == "knowledge":
        knowledge_injected.append(line)

system_text = "\n".join(system_inst)
gen_text = "\n".join(gen_inst)
blueprint_text = "\n".join(blueprint_data)
knowledge_text = "\n".join(knowledge_injected)

print(f"\n=== PROMPT COMPOSITION BREAKDOWN ===")
print(f"  System/Role Instructions: {len(system_text)} chars ({len(system_text)//4} tokens) - {len(system_text)/len(prompt)*100:.1f}%")
print(f"  Generation Instructions: {len(gen_text)} chars ({len(gen_text)//4} tokens) - {len(gen_text)/len(prompt)*100:.1f}%")
print(f"  Blueprint Data (file list): {len(blueprint_text)} chars ({len(blueprint_text)//4} tokens) - {len(blueprint_text)/len(prompt)*100:.1f}%")
print(f"  Knowledge Injected: {len(knowledge_text)} chars ({len(knowledge_text)//4} tokens) - {len(knowledge_text)/len(prompt)*100:.1f}%")
print(f"  Other/Whitespace: {len(prompt) - len(system_text) - len(gen_text) - len(blueprint_text) - len(knowledge_text)} chars")

# Detailed knowledge breakdown
print(f"\n=== DETAILED KNOWLEDGE FILES INJECTED ===")
for category, entries in knowledge.items():
    for entry in entries:
        fname = entry.get("file", "")
        content = entry.get("content", "")
        print(f"  [{category}] {fname}: {len(content)} chars, {len(content)//4} tokens")

# Check for duplicates
print(f"\n=== DUPLICATE CHECK ===")
all_knowledge = ""
for category, entries in knowledge.items():
    for entry in entries:
        all_knowledge += entry.get("content", "") + "\n"

# Check if CSS classes repeated
css_in_knowledge = _CSS_CLASS_LIST in all_knowledge
print(f"  CSS Class List appears in knowledge: {css_in_knowledge}")

# Check if layouts repeated
for ptype, layout in _PAGE_LAYOUTS.items():
    if layout in all_knowledge:
        print(f"  Layout '{ptype}' appears in knowledge files")

# Rank by size
components = [
    ("System/Role", len(system_text)),
    ("Generation Instructions", len(gen_text)),
    ("Blueprint Data", len(blueprint_text)),
    ("Knowledge Injected", len(knowledge_text)),
]
components.sort(key=lambda x: x[1], reverse=True)
print(f"\n=== RANKED BY SIZE ===")
for name, size in components:
    print(f"  {name}: {size} chars ({size//4} tokens) - {size/len(prompt)*100:.1f}%")