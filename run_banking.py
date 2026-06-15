"""Generate BankDash — a 6-page frontend-only banking system."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coding_agent.build_plan import generate_build_plan
from coding_agent.rules_engine import build_project_rules
from knowledge_retriever import retrieve_knowledge
from coding_agent.project_generator import generate_project

srs = {
    "project_name": "BankDash",
    "project_description": "A personal banking dashboard for managing accounts, transactions, transfers, statements, and user settings",
    "complexity": "medium",
    "tech_stack": {"frontend": "React", "backend": "none", "database": "none"},
    "pages": [
        {"name": "Overview", "entities": ["Account", "Transaction"]},
        {"name": "Accounts", "entities": ["Account"]},
        {"name": "Transactions", "entities": ["Transaction"]},
        {"name": "Transfer", "entities": ["Account", "Transfer"]},
        {"name": "Statements", "entities": ["Transaction"]},
        {"name": "Settings", "entities": ["Account"]},
    ],
    "entities": [
        {"name": "Account", "fields": ["name", "type", "balance", "accountNumber", "currency"]},
        {"name": "Transaction", "fields": ["accountId", "type", "amount", "description", "date", "category", "status"]},
        {"name": "Transfer", "fields": ["fromAccountId", "toAccountId", "amount", "description", "date", "status"]},
    ],
    "flow": [
        {"name": "View account overview with balances and recent transactions", "entities": ["Account", "Transaction"]},
        {"name": "View all accounts and their details", "entities": ["Account"]},
        {"name": "View and filter transaction history", "entities": ["Transaction"]},
        {"name": "Transfer money between accounts", "entities": ["Account", "Transfer"]},
        {"name": "View monthly spending statements", "entities": ["Transaction"]},
        {"name": "Update user settings and preferences", "entities": ["Account"]},
    ],
    "roles": [],
    "requirements": [],
}

output_dir = f"generated_projects/BankDash_{int(time.time())}"

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
        for line in lines[:5]:
            print(f"    {line.rstrip()}")
        content = "".join(lines)
        issues = []
        if "```" in content:
            issues.append("HAS MARKDOWN FENCES")
        if "useHistory" in content or "history.push" in content:
            issues.append("HAS useHistory (v5)")
        if "from '../App.css'" in content or "from './App.css'" in content:
            issues.append("HAS CSS IMPORT")
        if issues:
            print(f"    \u26a0 ISSUES: {', '.join(issues)}")
        else:
            print(f"    \u2713 No known issues")

from coding_agent.metrics import get_metrics_collector
metrics = get_metrics_collector()
print()
print("--- METRICS ---")
print(f"  Pipeline status: {metrics.pipeline_status}")
print(f"  Total files: {metrics.total_files}")
print(f"  Duration (wall): {metrics.pipeline_duration:.1f}s" if metrics.pipeline_duration else "  Duration: N/A")
if metrics.bundles:
    print()
    print("--- PER-BUNDLE BREAKDOWN ---")
    total_time = 0
    for b in metrics.bundles:
        dur = b.get('duration', 0)
        total_time += dur
        print(f"  {b['name']}: {dur:.1f}s — {b['files_in_bundle']} files, model={b.get('model','?')}, valid={b.get('valid',False)}")
    print(f"  Total (sum): {total_time:.1f}s")

summary = {
    "project": "BankDash",
    "duration_seconds": round(gen_time, 1),
    "files_generated": result["files_generated"],
    "files_written": len(result["files_written"]),
    "all_validations_pass": result["all_validations_pass"],
    "per_bundle": [
        {"name": b["name"], "duration": round(b.get("duration", 0), 1), "files": b["files_in_bundle"], "valid": b.get("valid", False)}
        for b in metrics.bundles
    ],
}
print()
print("--- SUMMARY JSON ---")
print(json.dumps(summary, indent=2))
