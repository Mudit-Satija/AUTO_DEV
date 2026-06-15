"""Real LLM generation test — delete old artifacts first, then generate."""
from coding_agent.build_plan import generate_build_plan
from coding_agent.project_generator import generate_project
from pathlib import Path
import shutil
import json

OUTPUT_DIR = "generated_task_manager_real"

if Path(OUTPUT_DIR).exists():
    shutil.rmtree(OUTPUT_DIR)

rules = {
    "backend_framework": "Express.js",
    "frontend_framework": "React",
    "database": "MongoDB",
    "auth_method": "",
    "required_backend_modules": ["calculator"],
    "required_pages": ["Calculator"],
}

plan = generate_build_plan(rules)
print(f"Build plan has {len(plan['files'])} files:")
for f in plan["files"]:
    print(f"  {f['path']} ({f['type']})")

result = generate_project(plan, rules, OUTPUT_DIR, max_repair_attempts=0)

print(f"\nFiles generated: {result['files_generated']}")
print(f"Files written: {len(result['files_written'])}")
print(f"Repair attempts: {result['repair_attempts']}")
print(f"All validations pass: {result['all_validations_pass']}")
