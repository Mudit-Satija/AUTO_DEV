"""Generate a React + Express + PostgreSQL + JWT project and validate output."""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coding_agent.build_plan import generate_build_plan
from coding_agent.project_generator import generate_project
from coding_agent.file_registry import load_registry

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "generated_project")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROJECT_RULES = {
    "backend_framework": "Express.js",
    "frontend_framework": "React",
    "database": "PostgreSQL",
    "auth_method": "JWT",
    "deployment": "Not specified",
    "required_pages": ["Home", "Login", "Dashboard", "Settings"],
    "required_backend_modules": ["workspaces", "projects", "tasks"],
}

def section(title):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)

# Phase 1 — Build Plan
section("PHASE 1: BUILD PLAN")
plan = generate_build_plan(PROJECT_RULES)
files = plan["files"]
print(f"  Blueprint files: {len(files)}")
for f in files:
    print(f"    [{f['type']:15s}] {f['path']}")

section("PHASE 2: IMPORT VALIDATION (before generation)")
file_paths = {f["path"] for f in files}

# Known patterns: files that import other files
import_checks = []

# Check server.js expectations (Express) — imports app.js, routes, config
if "src/server.js" in file_paths:
    import_checks.append(("src/server.js", "src/app.js", file_paths))
if "src/app.js" in file_paths:
    import_checks.append(("src/app.js", "src/routes/index.js", file_paths))
    import_checks.append(("src/app.js", "src/middleware/auth.js", file_paths))
    import_checks.append(("src/app.js", "src/middleware/errorHandler.js", file_paths))
if "src/routes/index.js" in file_paths:
    for f in files:
        p = f["path"]
        if p.startswith("src/routes/") and p != "src/routes/index.js":
            import_checks.append(("src/routes/index.js", p, file_paths))

all_ok = True
for importer, imported, paths in import_checks:
    exists = imported in paths
    status = "OK" if exists else "MISSING"
    if not exists:
        all_ok = False
    print(f"    [{status:7s}] {importer} -> {imported}")

print(f"\n  Import validation result: {'ALL PASS' if all_ok else 'ISSUES FOUND'}")

if all_ok:
    print("\n  Proceeding to generation...")

# Phase 3 — Generate
section("PHASE 3: GENERATION")
print("  Calling LLM (Qwen) for each bundle...")
print("  This may take several minutes.")
sys.stdout.flush()

start = time.perf_counter()
result = generate_project(
    build_plan={"files": files},
    project_rules=PROJECT_RULES,
    output_dir=OUTPUT_DIR,
    max_repair_attempts=0,
)
elapsed = time.perf_counter() - start

print()
print(f"  Generation time: {elapsed:.2f}s")
print(f"  Files generated:  {result['files_generated']}")
print(f"  Files written:    {len(result['files_written'])}")
print(f"  Registry path:    {result.get('registry_path')}")

# Phase 4 — Validation
section("PHASE 4: OUTPUT VALIDATION")

written_paths = [meta["path"] for meta in result.get("files_written", [])]

# 1. Total count
print(f"\n  1. Generated file count: {len(written_paths)}")

# 2. src/routes/auth.js exists
auth_route = "src/routes/auth.js" in written_paths
print(f"  2. src/routes/auth.js exists: {'YES' if auth_route else 'NO'}")

# 3. server.js imports only existing files
print(f"  3. server.js import validation:")
server_meta = next((m for m in result.get("files_written", []) if m["path"] == "src/server.js"), None)
if server_meta and server_meta.get("absolute_path") and os.path.exists(server_meta["absolute_path"]):
    with open(server_meta["absolute_path"], encoding="utf-8") as fh:
        server_content = fh.read()
    import re
    requires = re.findall(r"require\(['\"](.+?)['\"]\)", server_content)
    resolved_imports = set()
    for imp in requires:
        if imp.startswith("."):
            base_dir = os.path.dirname(server_meta["absolute_path"])
            imp_path = os.path.normpath(os.path.join(base_dir, imp))
            resolved = os.path.relpath(imp_path, os.path.dirname(server_meta["absolute_path"]))
            resolved_imports.add(imp)
    print(f"     Requires found: {resolved_imports}")
    all_resolved = all(
        any(
            imp.replace(".js", "") in p.replace(".js", "")
            or imp.split("/")[-1].replace(".js", "") in p.replace(".js", "")
            for p in written_paths
        )
        for imp in resolved_imports
    )
    for imp in resolved_imports:
        matching = [p for p in written_paths if imp.replace(".js", "") in p.replace(".js", "")]
        status = "OK" if matching else "MISSING"
        print(f"     [{status:7s}] require('{imp}') -> {matching if matching else 'NOT FOUND'}")
else:
    print(f"     server.js not written to disk yet — check printed content.")

# 4. package.json and package_frontend.json
has_backend_pkg = any("package.json" in p and "frontend" not in p for p in written_paths)
has_frontend_pkg = any("package_frontend.json" in p for p in written_paths)
print(f"  4. package.json exists:           {'YES' if has_backend_pkg else 'NO'}")
print(f"     package_frontend.json exists:  {'YES' if has_frontend_pkg else 'NO'}")

# 5. Files on disk
print(f"  5. Files written to disk:")
disk_count = 0
for meta in result.get("files_written", []):
    abspath = meta.get("absolute_path", "")
    if abspath and os.path.exists(abspath):
        size = os.path.getsize(abspath)
        print(f"     OK  {meta['path']} ({size:,} bytes)")
        disk_count += 1
    else:
        print(f"     MISSING  {meta['path']}")

# 6. Missing imports report
print(f"  6. Missing imports report:")
author_route = "src/routes/auth.js" in written_paths
if auth_route:
    print(f"     src/routes/auth.js — PRESENT (generated via auth_method=JWT)")
else:
    print(f"     src/routes/auth.js — ABSENT")

# Summary
section("SUMMARY")
print(f"  Total blueprints:      {len(files)}")
print(f"  Files written:         {disk_count}")
print(f"  Generation time:       {elapsed:.2f}s")
print(f"  Auth route generated:  {'YES' if auth_route else 'NO'}")
print(f"  Package files:         backend={'YES' if has_backend_pkg else 'NO'}, frontend={'YES' if has_frontend_pkg else 'NO'}")
print(f"  Import validation:     {'ALL PASS' if all_ok else 'ISSUES FOUND (see above)'}")
print()

# Write summary
with open(os.path.join(OUTPUT_DIR, "_generation_result.json"), "w") as f:
    json.dump({
        "elapsed_s": round(elapsed, 2),
        "blueprint_count": len(files),
        "files_written": disk_count,
        "registry_path": result.get("registry_path"),
    }, f, indent=2)
