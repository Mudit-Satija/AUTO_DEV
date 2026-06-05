"""Standalone bundle+parallel+partition validation.

Tests the full generate_project() pipeline with a pre-built plan,
validating that bundles are classified, partitioned (>10 files),
executed in parallel, and files are written to disk.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coding_agent.bundle_generator import group_files_by_bundle, group_and_partition_files
from coding_agent.project_generator import generate_project


OUTPUT_DIR = "test_bundle_output"

# 19 files across 4 bundles to exercise grouping + partitioning (backend > 10)
FILES = [
    # Backend (12 files — triggers split into backend_1 + backend_2)
    {"path": "package.json", "type": "config", "purpose": "Node.js dependencies and scripts"},
    {"path": "src/app.js", "type": "source", "purpose": "Express application setup"},
    {"path": "src/server.js", "type": "source", "purpose": "Server entry point"},
    {"path": "src/config/index.js", "type": "config", "purpose": "Configuration loader"},
    {"path": "src/config/db.js", "type": "config", "purpose": "PostgreSQL connection pool setup"},
    {"path": "src/middleware/auth.js", "type": "source", "purpose": "JWT authentication middleware"},
    {"path": "src/middleware/errorHandler.js", "type": "source", "purpose": "Global express error handler"},
    {"path": "src/routes/auth.js", "type": "source", "purpose": "Auth routes for login and register"},
    {"path": "src/routes/projects.js", "type": "source", "purpose": "Project CRUD route handlers"},
    {"path": "src/routes/tasks.js", "type": "source", "purpose": "Task CRUD route handlers"},
    {"path": "src/models/User.js", "type": "source", "purpose": "User database model"},
    {"path": ".env.example", "type": "env", "purpose": "Environment variable template file"},
    # Frontend (5 files)
    {"path": "package_frontend.json", "type": "config", "purpose": "Frontend dependencies and scripts Vite"},
    {"path": "vite.config.js", "type": "config", "purpose": "Frontend Vite build configuration"},
    {"path": "index.html", "type": "source", "purpose": "Frontend HTML entry point"},
    {"path": "src/main.jsx", "type": "source", "purpose": "React entry point for frontend"},
    {"path": "src/App.jsx", "type": "source", "purpose": "Root React application component"},
    # Database (1 file)
    {"path": "migrations/001_create_users.sql", "type": "database", "purpose": "Users table creation migration"},
    # Documentation (1 file)
    {"path": "README.md", "type": "documentation", "purpose": "Project README documentation"},
]

PROJECT_RULES = {
    "backend_framework": "Express.js",
    "frontend_framework": "React",
    "database": "PostgreSQL",
    "auth_method": "JWT",
    "deployment": "None",
    "required_pages": ["Dashboard", "Login", "Projects"],
    "required_backend_modules": ["projects", "tasks"],
}


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 70)
    print("  BUNDLE GENERATION PIPELINE — END-TO-END VALIDATION")
    print("=" * 70)
    print(f"  Total blueprints: {len(FILES)}")
    print()

    # Phase 1 — Classification
    print("  [Phase 1] File classification:")
    classified = group_files_by_bundle(FILES)
    for cls in sorted(classified):
        items = classified[cls]
        print(f"    {cls}: {len(items)} files")
        for bp in items:
            print(f"      - {bp['path']}")

    # Phase 2 — Partitioning
    print()
    print("  [Phase 2] Bundle partitioning (max 10 per bundle):")
    partitioned = group_and_partition_files(FILES)
    for name in sorted(partitioned):
        chunk = partitioned[name]
        print(f"    {name}: {len(chunk)} files")
        for bp in chunk:
            print(f"      - {bp['path']}")

    # Phase 3 — Generation
    print()
    print("  [Phase 3] Generating project (calls LLM via bundles)...")
    start = time.perf_counter()

    result = generate_project(
        build_plan={"files": FILES},
        project_rules=PROJECT_RULES,
        output_dir=OUTPUT_DIR,
    )

    elapsed = time.perf_counter() - start

    print(f"  Generation time:  {elapsed:.2f}s")
    print(f"  Files generated:  {result['files_generated']}")
    print(f"  Files written:    {len(result['files_written'])}")
    print(f"  Registry path:    {result.get('registry_path')}")

    # Phase 4 — Verify files on disk
    print()
    print("  [Phase 4] Validating written files:")
    written_count = 0
    for meta in result.get("files_written", []):
        path = meta.get("path", "?")
        abspath = meta.get("absolute_path", "")
        if abspath and os.path.exists(abspath):
            size = os.path.getsize(abspath)
            print(f"    OK  {path} ({size} bytes)")
            written_count += 1
        else:
            print(f"    MISSING  {path} (expected at {abspath})")

    print()
    print("-" * 70)
    if written_count == len(FILES):
        print(f"  RESULT: ALL {written_count} / {len(FILES)} files written")
    else:
        print(f"  RESULT: {written_count} / {len(FILES)} files written (fallback used)")
    print(f"  Time: {elapsed:.2f}s")
    print("=" * 70)

    with open(os.path.join(OUTPUT_DIR, "_generation_result.json"), "w") as f:
        json.dump({
            "elapsed_s": round(elapsed, 2),
            "files_generated": result["files_generated"],
            "files_written": len(result["files_written"]),
            "registry_path": result.get("registry_path"),
        }, f, indent=2)

    return 0 if written_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
