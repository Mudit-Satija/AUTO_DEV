"""Concurrency diagnostic test for bundle generation."""

import sys
import os
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "D:/projects/AUTO_DEV")

from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules
from coding_agent.bundle_generator import group_and_partition_files, generate_bundle_with_fallback
from coding_agent.file_registry import register_file, save_registry
from coding_agent.metrics import get_metrics_collector, reset_metrics_collector


def run_generation(max_workers: int, output_dir: str):
    """Run generation with specified max_workers."""
    
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
    print(f"\n=== max_workers={max_workers} ===")
    print(f"Total files: {len(files)}")
    print(f"Total bundles: {len(bundles)}")
    for name, bps in bundles.items():
        print(f"  {name}: {len(bps)} files")
        for bp in bps:
            print(f"    {bp['path']}")
    
    reset_metrics_collector()
    metrics = get_metrics_collector()
    metrics.start_pipeline(len(files))
    
    registry = {}
    written = []
    
    start_time = time.perf_counter()
    
    def run_bundle(bundle_name, file_blueprints):
        local_registry = {}
        written_local = generate_bundle_with_fallback(
            bundle_name, file_blueprints, project_rules, output_dir, local_registry
        )
        return bundle_name, written_local, local_registry
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(run_bundle, name, bundles[name]): name
            for name in sorted(bundles.keys())
        }
        
        for future in as_completed(future_map):
            name = future_map[future]
            try:
                bundle_name, written_local, registry_local = future.result()
                print(f"  Bundle [{bundle_name}] completed: {len(written_local)} files")
                written.extend(written_local)
                registry.update(registry_local)
            except Exception as e:
                print(f"  Bundle [{name}] failed with exception: {e}")
    
    total_time = time.perf_counter() - start_time
    
    if registry:
        save_registry(registry, output_dir)
    
    metrics.end_pipeline("Success" if len(written) > 0 else "Failed")
    summary = metrics.get_summary()
    
    print(f"\nTotal time: {total_time:.1f}s")
    print(f"Files written: {len(written)}")
    print(f"Bundles completed: {summary['pipeline_metrics']['total_bundles']}")
    print(f"Total generation time: {summary['pipeline_metrics']['total_generation_time_ms']}ms")
    print(f"Validation time: {summary['pipeline_metrics']['validation_time_ms']}ms")
    
    for bm in summary['pipeline_metrics']['bundle_metrics']:
        print(f"  {bm['bundle_name']}: {bm['status']}, {bm['generation_duration_ms']}ms, {bm['file_count']} files, {bm['prompt_length']} chars")
    
    return {
        "max_workers": max_workers,
        "total_time_sec": total_time,
        "files_written": len(written),
        "bundles_completed": summary['pipeline_metrics']['total_bundles'],
        "total_generation_time_ms": summary['pipeline_metrics']['total_generation_time_ms'],
        "validation_time_ms": summary['pipeline_metrics']['validation_time_ms'],
        "bundle_details": summary['pipeline_metrics']['bundle_metrics'],
        "overall_status": summary['pipeline_metrics']['overall_status'],
    }


if __name__ == "__main__":
    import shutil
    from pathlib import Path
    
    results = {}
    
    for workers in [1, 2, 8]:
        output_dir = f"generated_outputs/concurrency_test_w{workers}"
        if Path(output_dir).exists():
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        result = run_generation(workers, output_dir)
        results[f"workers_{workers}"] = result
        
        print(f"\n{'='*60}")
        time.sleep(2)
    
    # Save comparison report
    with open("generated_outputs/concurrency_comparison.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n\n=== FINAL COMPARISON ===")
    for key, r in results.items():
        print(f"\n{key}:")
        print(f"  Total time: {r['total_time_sec']:.1f}s")
        print(f"  Files written: {r['files_written']}")
        print(f"  Bundles completed: {r['bundles_completed']}")
        print(f"  Status: {r['overall_status']}")
        for bd in r['bundle_details']:
            print(f"    {bd['bundle_name']}: {bd['status']} ({bd['generation_duration_ms']}ms)")