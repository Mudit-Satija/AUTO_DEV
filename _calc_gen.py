"""Generate calculator project with no auth."""
import sys, os, shutil, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coding_agent.build_plan import generate_build_plan
from coding_agent.project_generator import generate_project

OUTPUT_DIR = r'D:\projects\AUTO_DEV\generated_calculator'

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

rules = {
    "backend_framework": "Express.js",
    "frontend_framework": "React",
    "database": "MongoDB",
    "auth_method": "no auth",
    "deployment": "Not specified",
    "required_pages": ["Calculator"],
    "required_backend_modules": ["calculator"],
}

plan = generate_build_plan(rules)
print(f'Build plan has {len(plan["files"])} files:')
fpaths = []
for f in plan["files"]:
    fpaths.append(f["path"])
    print(f'  {f["path"]} ({f["type"]})')

result = generate_project(plan, rules, OUTPUT_DIR, max_repair_attempts=0)

print(f'\nFiles generated: {result["files_generated"]}')
print(f'Files written: {len(result["files_written"])}')
print(f'Repair attempts: {result["repair_attempts"]}')
print(f'All validations pass: {result["all_validations_pass"]}')

# Write results summary
summary = {
    "validations_pass": result["all_validations_pass"],
    "files_generated": result["files_generated"],
    "files_written": len(result["files_written"]),
    "repair_attempts": result["repair_attempts"],
    "file_paths": fpaths,
}
summary_path = os.path.join(OUTPUT_DIR, "..", "calc_summary.json")
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"\nSummary saved to {summary_path}")
