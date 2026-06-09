"""Generate Express+React+MongoDB no-auth with tasks, categories modules."""
import sys, os, shutil, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coding_agent.build_plan import generate_build_plan
from coding_agent.project_generator import generate_project

ts = str(int(time.time()))
OUTPUT_DIR = rf'D:\projects\AUTO_DEV\generated_output\{ts}'

rules = {
    "backend_framework": "Express.js",
    "frontend_framework": "React",
    "database": "MongoDB",
    "auth_method": "",
    "deployment": "Not specified",
    "required_backend_modules": ["tasks", "categories"],
    "required_pages": ["Dashboard", "Tasks", "Categories"],
}

plan = generate_build_plan(rules)
print(f'Build plan has {len(plan["files"])} files:')
fpaths = []
for f in plan["files"]:
    fpaths.append(f["path"])
    print(f'  {f["path"]} ({f["type"]})')

result = generate_project(plan, rules, OUTPUT_DIR, max_repair_attempts=3)

print(f'\nFiles generated: {result["files_generated"]}')
print(f'Files written: {len(result["files_written"])}')
print(f'Repair attempts: {result["repair_attempts"]}')
print(f'All validations pass: {result["all_validations_pass"]}')

summary = {
    "validations_pass": result["all_validations_pass"],
    "files_generated": result["files_generated"],
    "files_written": len(result["files_written"]),
    "repair_attempts": result["repair_attempts"],
    "file_paths": fpaths,
}
summary_path = os.path.join(OUTPUT_DIR, "..", f"summary_{ts}.json")
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSummary saved to {summary_path}")
