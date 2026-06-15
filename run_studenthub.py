"""Generate StudentHub — a 6-page frontend-only student dashboard."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules
from knowledge_retriever import retrieve_knowledge
from coding_agent.project_generator import generate_project

srs = {
    "project_name": "StudentHub",
    "project_description": "A student academic dashboard for tracking courses, marks, assignments, schedule, and profile",
    "complexity": "medium",
    "tech_stack": {"frontend": "React", "backend": "none", "database": "none"},
    "pages": [
        {"name": "Dashboard", "entities": ["Course", "Mark", "Assignment"]},
        {"name": "Courses", "entities": ["Course"]},
        {"name": "Marks", "entities": ["Mark"]},
        {"name": "Assignments", "entities": ["Assignment"]},
        {"name": "Schedule", "entities": ["Course"]},
        {"name": "Profile", "entities": ["Student"]},
    ],
    "entities": [
        {"name": "Course", "fields": ["name", "code", "instructor", "credits", "schedule"]},
        {"name": "Mark", "fields": ["courseId", "assignmentName", "score", "total", "grade", "date"]},
        {"name": "Assignment", "fields": ["courseId", "title", "description", "dueDate", "status", "grade"]},
        {"name": "Student", "fields": ["name", "email", "major", "semester"]},
    ],
    "flow": [
        {"name": "View dashboard with GPA, upcoming deadlines, recent marks", "entities": ["Course", "Mark", "Assignment"]},
        {"name": "View all enrolled courses", "entities": ["Course"]},
        {"name": "View marks and grades", "entities": ["Mark"]},
        {"name": "Track assignments and due dates", "entities": ["Assignment"]},
        {"name": "View class schedule", "entities": ["Course"]},
        {"name": "Edit student profile", "entities": ["Student"]},
    ],
    "roles": [],
    "requirements": [],
}

output_dir = f"generated_projects/StudentHub_{int(time.time())}"

print(f"SRS: {srs['project_name']} — {srs['project_description']}")
print(f"Tech: frontend={srs['tech_stack']['frontend']}, backend={srs['tech_stack']['backend']}")
print(f"Pages: {[p['name'] for p in srs['pages']]}")
print(f"Entities: {[e['name'] for e in srs['entities']]}")
print(f"Output: {output_dir}")
print()

t0 = time.perf_counter()
project_rules = build_project_rules(srs, srs["tech_stack"])
print(f"[{time.perf_counter()-t0:.1f}s] build_project_rules done")

t1 = time.perf_counter()
knowledge = retrieve_knowledge(srs)
project_rules["knowledge"] = knowledge
print(f"[{time.perf_counter()-t1:.1f}s] retrieve_knowledge done — frontend:{len(knowledge.get('frontend',[]))}, backend:{len(knowledge.get('backend',[]))}")

t2 = time.perf_counter()
build_plan = generate_build_plan(project_rules)
print(f"[{time.perf_counter()-t2:.1f}s] generate_build_plan done — {len(build_plan.get('files',[]))} files")

print()
print("--- FILES IN BUILD PLAN ---")
for f in build_plan.get("files", []):
    print(f"  {f['path']}  [{f.get('bundle','?')}]")
print()

t3 = time.perf_counter()
result = generate_project(build_plan, project_rules, output_dir)
gen_time = time.perf_counter() - t3

print(f"[{gen_time:.1f}s] generate_project done")
print(f"  files_generated: {result['files_generated']}")
print(f"  files_written: {len(result['files_written'])}")
print(f"  registry_path: {result['registry_path']}")
print(f"  all_validations_pass: {result['all_validations_pass']}")

print()
print("--- GENERATED FILES ---")
for w in sorted(result.get("files_written", []), key=lambda x: x.get("path", "")):
    path = w.get("path", "?")
    size = w.get("size", 0)
    dest = w.get("dest_path", "")
    print(f"\n  {path}  ({size} bytes, -> {dest})")
    if dest and os.path.exists(dest):
        with open(dest, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        for line in lines[:4]:
            print(f"    {line.rstrip()}")
        content = "".join(lines)
        issues = []
        if "```" in content:
            issues.append("HAS MARKDOWN FENCES")
        if "useHistory" in content or "history.push" in content:
            issues.append("HAS useHistory (v5)")
        if issues:
            print(f"    \u26a0 ISSUES: {', '.join(issues)}")
        else:
            print(f"    \u2713 No known import issues")
