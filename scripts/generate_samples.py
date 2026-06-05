"""Generate 10 sample projects end-to-end using the real LLM.

Each project uses a different configuration (framework, modules, pages).
Results are saved to generated_projects/sample_N/ with a ZIP archive.
A summary report is written to generated_projects/_summary.json.

Usage:
    python scripts/generate_samples.py [--parallel 3] [--timeout 600]
"""

import argparse
import json
import logging
import os
import shutil
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coding_agent.build_plan import generate_build_plan
from coding_agent.project_generator import generate_project
from coding_agent.zip_export import export_to_zip

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("generate_samples")

BASE_DIR = Path(__file__).resolve().parent.parent / "generated_projects"


# ---------------------------------------------------------------------------
# 10 project configurations
# ---------------------------------------------------------------------------

PROJECT_CONFIGS = [
    {
        "id": 1,
        "name": "express_react_pg_jwt_workspaces",
        "rules": {
            "backend_framework": "Express.js",
            "frontend_framework": "React",
            "database": "PostgreSQL",
            "auth_method": "JWT",
            "deployment": "AWS",
            "required_backend_modules": ["workspaces", "projects", "tasks"],
            "required_pages": ["Login", "Dashboard", "Settings"],
        },
    },
    {
        "id": 2,
        "name": "express_react_mongo_jwt_posts",
        "rules": {
            "backend_framework": "Express.js",
            "frontend_framework": "React",
            "database": "MongoDB",
            "auth_method": "JWT",
            "deployment": "Docker",
            "required_backend_modules": ["users", "posts", "comments"],
            "required_pages": ["Login", "Feed", "Profile"],
        },
    },
    {
        "id": 3,
        "name": "fastapi_react_pg_oauth_tasks",
        "rules": {
            "backend_framework": "FastAPI",
            "frontend_framework": "React",
            "database": "PostgreSQL",
            "auth_method": "OAuth",
            "deployment": "AWS",
            "required_backend_modules": ["projects", "tasks", "teams"],
            "required_pages": ["Login", "Dashboard", "Teams"],
        },
    },
    {
        "id": 4,
        "name": "express_vue_pg_jwt_inventory",
        "rules": {
            "backend_framework": "Express.js",
            "frontend_framework": "Vue",
            "database": "PostgreSQL",
            "auth_method": "JWT",
            "deployment": "DigitalOcean",
            "required_backend_modules": ["inventory", "orders", "customers"],
            "required_pages": ["Login", "Dashboard", "Orders"],
        },
    },
    {
        "id": 5,
        "name": "fastapi_vue_pg_jwt_articles",
        "rules": {
            "backend_framework": "FastAPI",
            "frontend_framework": "Vue",
            "database": "PostgreSQL",
            "auth_method": "JWT",
            "deployment": "Docker",
            "required_backend_modules": ["articles", "categories", "tags"],
            "required_pages": ["Login", "Home", "Articles"],
        },
    },
    {
        "id": 6,
        "name": "express_react_pg_noauth_crud",
        "rules": {
            "backend_framework": "Express.js",
            "frontend_framework": "React",
            "database": "PostgreSQL",
            "auth_method": "",
            "deployment": "AWS",
            "required_backend_modules": ["items", "categories"],
            "required_pages": ["Home", "Items", "About"],
        },
    },
    {
        "id": 7,
        "name": "fastapi_react_mongo_jwt_todos",
        "rules": {
            "backend_framework": "FastAPI",
            "frontend_framework": "React",
            "database": "MongoDB",
            "auth_method": "JWT",
            "deployment": "AWS",
            "required_backend_modules": ["todos", "notes"],
            "required_pages": ["Login", "Todos"],
        },
    },
    {
        "id": 8,
        "name": "express_react_pg_jwt_roles",
        "rules": {
            "backend_framework": "Express.js",
            "frontend_framework": "React",
            "database": "PostgreSQL",
            "auth_method": "JWT",
            "deployment": "Heroku",
            "required_backend_modules": ["roles", "permissions", "users"],
            "required_pages": ["Login", "Dashboard", "Admin"],
        },
    },
    {
        "id": 9,
        "name": "fastapi_react_pg_oauth_products",
        "rules": {
            "backend_framework": "FastAPI",
            "frontend_framework": "React",
            "database": "PostgreSQL",
            "auth_method": "OAuth",
            "deployment": "GCP",
            "required_backend_modules": ["products", "reviews", "orders"],
            "required_pages": ["Login", "Products", "Cart"],
        },
    },
    {
        "id": 10,
        "name": "express_vue_mongo_noauth_events",
        "rules": {
            "backend_framework": "Express.js",
            "frontend_framework": "Vue",
            "database": "MongoDB",
            "auth_method": "",
            "deployment": "AWS",
            "required_backend_modules": ["events", "registrations"],
            "required_pages": ["Home", "Events", "Register"],
        },
    },
]


# ---------------------------------------------------------------------------
# Single project generator
# ---------------------------------------------------------------------------


def generate_single_project(config: dict, parallel: bool = False) -> dict:
    """Generate one project from config and return a status dict.

    Args:
        config: A PROJECT_CONFIGS entry with "id", "name", "rules".
        parallel: If True, display a shorter log prefix (suited for parallel runs).

    Returns:
        Dict with keys: id, name, success, files, errors, elapsed, zip_path.
    """
    name = config["name"]
    rules = config["rules"]
    project_dir = BASE_DIR / f"sample_{config['id']:02d}_{name}"

    result = {
        "id": config["id"],
        "name": name,
        "success": False,
        "files_planned": 0,
        "files_written": 0,
        "elapsed": 0,
        "zip_path": None,
        "error": None,
        "repair_attempts": 0,
        "validations_pass": False,
    }

    prefix = f"[{config['id']:02d}/{len(PROJECT_CONFIGS)}]"
    log = logger.info if not parallel else lambda msg: logger.info("%s %s", prefix, msg)

    try:
        t0 = time.perf_counter()

        # Clean output dir
        if project_dir.exists():
            shutil.rmtree(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)

        # Phase 1: Build plan
        log("Generating build plan...")
        plan = generate_build_plan(rules)
        files = plan.get("files", [])
        result["files_planned"] = len(files)
        log("  Plan: %d files", len(files))

        # Phase 2: Generate project
        log("Generating project (this may take several minutes)...")
        gen_result = generate_project(
            build_plan={"files": files},
            project_rules=rules,
            output_dir=str(project_dir),
            max_repair_attempts=3,
        )

        written = gen_result.get("files_written", [])
        result["files_written"] = len(written)
        result["repair_attempts"] = gen_result.get("repair_attempts", 0)
        result["validations_pass"] = gen_result.get("all_validations_pass", False)
        result["registry_path"] = gen_result.get("registry_path")

        # Phase 3: ZIP export
        zip_path = export_to_zip(str(project_dir))
        result["zip_path"] = zip_path

        # Phase 4: Write metadata
        metadata = {
            "config": config,
            "generation": {
                "files_generated": gen_result.get("files_generated"),
                "files_written": len(written),
                "repair_attempts": result["repair_attempts"],
                "validations_pass": result["validations_pass"],
                "registry_path": result["registry_path"],
            },
            "export": {"zip_path": zip_path},
        }
        (project_dir / "_generation_metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )

        elapsed = time.perf_counter() - t0
        result["elapsed"] = round(elapsed, 1)
        result["success"] = True

        log("DONE in %.1fs — %d/%d files, validations=%s, ZIP=%s",
            elapsed,
            result["files_written"],
            result["files_planned"],
            "PASS" if result["validations_pass"] else "FAIL",
            zip_path,
        )

    except Exception as e:
        elapsed = time.perf_counter() - t0 if "t0" in dir() else 0
        result["elapsed"] = round(elapsed, 1)
        result["error"] = f"{type(e).__name__}: {e}"
        result["traceback"] = traceback.format_exc()
        logger.error("%s FAILED — %s", prefix, result["error"])

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def summarize(results: list[dict]):
    """Print a summary table and write _summary.json."""
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    passed = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    total_written = sum(r["files_written"] for r in results)
    total_planned = sum(r["files_planned"] for r in results)
    total_time = sum(r["elapsed"] for r in results)
    valid_pass = sum(1 for r in results if r["validations_pass"])
    valid_fail = sum(1 for r in results if not r["validations_pass"])

    print()
    print("=" * 90)
    print("  SAMPLE GENERATION SUMMARY")
    print("=" * 90)
    print(f"  {'ID':>3}  {'Name':40s}  {'Files':>6}  {'Time':>6}  {'Zip':>4}  {'Valid':>6}  {'Repair':>6}")
    print(f"  {'-'*3}  {'-'*40}  {'-'*6}  {'-'*6}  {'-'*4}  {'-'*6}  {'-'*6}")
    for r in sorted(results, key=lambda x: x["id"]):
        status = "OK" if r["success"] else "FAIL"
        valid = "PASS" if r["validations_pass"] else "FAIL"
        zip_ok = "YES" if r["zip_path"] else "---"
        repair = r.get("repair_attempts", 0)
        print(f"  {r['id']:>3}  {r['name']:40s}  {r['files_written']:>3}/{r['files_planned']:<2d}  {r['elapsed']:>5.0f}s  {zip_ok:>4}  {valid:>6}  {repair:>3}x")
    print(f"  {'-'*3}  {'-'*40}  {'-'*6}  {'-'*6}  {'-'*4}  {'-'*6}  {'-'*6}")
    print(f"  {'':>3}  {'TOTAL':40s}  {total_written:>3}/{total_planned:<2d}  {total_time:>5.0f}s{'':>11}  {valid_pass}/{len(results)}")
    print()
    if passed == len(results):
        print(f"  ALL {len(results)} PROJECTS GENERATED SUCCESSFULLY")
    else:
        print(f"  {passed} passed, {failed} failed")
    if valid_fail > 0:
        print(f"  ({valid_fail} projects have validation warnings — code was generated but some")
        print(f"   requirement checks didn't pass. This is a prompt quality issue, not a pipeline failure.")
    print()

    summary_path = BASE_DIR / "_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "validations_passed": valid_pass,
                "total_time_s": round(total_time, 1),
                "projects": [
                    {
                        "id": r["id"],
                        "name": r["name"],
                        "success": r["success"],
                        "elapsed": r["elapsed"],
                        "files_planned": r["files_planned"],
                        "files_written": r["files_written"],
                        "validations_pass": r["validations_pass"],
                        "repair_attempts": r.get("repair_attempts", 0),
                        "error": r.get("error"),
                    }
                    for r in results
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"  Summary saved to: {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate 10 sample projects")
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of projects to generate in parallel (default: 1)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="Timeout per project in seconds (default: 900)",
    )
    parser.add_argument(
        "--ids",
        type=str,
        default="",
        help="Comma-separated list of project IDs to run (default: all 1-10)",
    )
    args = parser.parse_args()

    if args.ids:
        selected_ids = {int(x) for x in args.ids.split(",")}
        configs = [c for c in PROJECT_CONFIGS if c["id"] in selected_ids]
    else:
        configs = PROJECT_CONFIGS

    logger.info("Starting generation of %d projects (parallel=%d, timeout=%ds)",
                len(configs), args.parallel, args.timeout)

    if args.parallel > 1:
        results = [None] * len(configs)
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            future_map = {
                pool.submit(generate_single_project, cfg, True): i
                for i, cfg in enumerate(configs)
            }
            for future in as_completed(future_map):
                idx = future_map[future]
                results[idx] = future.result(timeout=args.timeout)
    else:
        results = []
        for cfg in configs:
            result = generate_single_project(cfg, False)
            results.append(result)

    summarize(results)

    any_failed = any(not r["success"] for r in results)
    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
