import sys, os, time, shutil, json
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, 'D:/projects/AUTO_DEV')

from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules
from coding_agent.bundle_generator import group_and_partition_files, generate_bundle_with_fallback
from coding_agent.file_registry import register_file, save_registry
from coding_agent.metrics import get_metrics_collector, reset_metrics_collector

srs = {
    'project_name': 'ExpenseFlow', 'project_description': '', 'complexity': 'medium',
    'pages': [{'name': 'Dashboard', 'purpose': '', 'entities': []}, {'name': 'Transactions', 'purpose': '', 'entities': []}, {'name': 'Budgets', 'purpose': '', 'entities': []}, {'name': 'Reports', 'purpose': '', 'entities': []}, {'name': 'Analytics', 'purpose': '', 'entities': []}],
    'entities': [{'name': 'Transaction', 'fields': ['name', 'description', 'createdAt'], 'description': ''}, {'name': 'Budget', 'fields': ['name', 'description', 'createdAt'], 'description': ''}, {'name': 'Category', 'fields': ['name', 'description', 'createdAt'], 'description': ''}],
    'flow': [{'name': 'Add Transaction', 'steps': [], 'entities': []}, {'name': 'Edit Transaction', 'steps': [], 'entities': []}, {'name': 'Delete Transaction', 'steps': [], 'entities': []}, {'name': 'Create Budget', 'steps': [], 'entities': []}, {'name': 'Update Budget', 'steps': [], 'entities': []}, {'name': 'Track Spending', 'steps': [], 'entities': []}, {'name': 'Generate Reports', 'steps': [], 'entities': []}, {'name': 'View Analytics', 'steps': [], 'entities': []}, {'name': 'Filter Transactions', 'steps': [], 'entities': []}],
    'roles': [], 'tech_stack': {'frontend': 'React', 'backend': 'Express.js', 'database': 'MongoDB'}, 'requirements': [],
}

project_rules = build_project_rules(srs, {'backend': 'Express.js', 'frontend': 'React', 'database': 'MongoDB'})
build_plan = generate_build_plan(project_rules)
files = build_plan.get('files', [])
bundles = group_and_partition_files(files)

max_workers = 8
output_dir = 'generated_outputs/concurrency_test_w8'
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir, exist_ok=True)

reset_metrics_collector()
metrics = get_metrics_collector()
metrics.start_pipeline(len(files))

registry = {}
written = []

def run_bundle(bundle_name, file_blueprints):
    local_registry = {}
    written_local = generate_bundle_with_fallback(bundle_name, file_blueprints, project_rules, output_dir, local_registry)
    return bundle_name, written_local, local_registry

start_time = time.perf_counter()
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    future_map = {executor.submit(run_bundle, name, bundles[name]): name for name in sorted(bundles.keys())}
    for future in as_completed(future_map):
        name = future_map[future]
        try:
            bundle_name, written_local, registry_local = future.result()
            print(f'  Bundle [{bundle_name}] completed: {len(written_local)} files')
            written.extend(written_local)
            registry.update(registry_local)
        except Exception as e:
            print(f'  Bundle [{name}] failed: {e}')

total_time = time.perf_counter() - start_time
if registry:
    save_registry(registry, output_dir)
metrics.end_pipeline('Success' if len(written) > 0 else 'Failed')
summary = metrics.get_summary()

print(f'\nTotal time: {total_time:.1f}s')
print(f'Files written: {len(written)}')
print(f'Bundles completed: {summary["pipeline_metrics"]["total_bundles"]}')
for bm in summary['pipeline_metrics']['bundle_metrics']:
    print(f'  {bm["bundle_name"]}: {bm["status"]}, {bm["generation_duration_ms"]}ms, {bm["file_count"]} files')