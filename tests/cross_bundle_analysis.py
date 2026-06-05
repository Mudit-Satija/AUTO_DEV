"""Analyze cross-bundle dependency edges in the current bundling system."""
import sys; sys.path.insert(0, '.')
from coding_agent.build_plan import generate_build_plan
from coding_agent.bundle_generator import group_and_partition_files

def assess_risk(file_path, purpose, dep_path, dep_purpose):
    """Return None if the LLM can safely infer the import across bundles.
    Return a string reason if the cross-bundle edge risks generation failure."""

    # Controller -> Model: import path is deterministic from module name
    if file_path.startswith('src/controllers/') and dep_path.startswith('src/models/'):
        module = file_path.split('/')[2].replace('.js', '')
        dep_module = dep_path.split('/')[2].replace('.js', '')
        if module == dep_module:
            return None  # deterministic: same module name → import path is obvious

    # Route -> Controller: route imports controller, path is deterministic
    if file_path.startswith('src/routes/') and dep_path.startswith('src/controllers/'):
        return None

    # app.js -> routes/index.js: standard Express pattern
    if 'app.js' in file_path and 'routes/index.js' in dep_path:
        return None

    # app.js -> config/*: deterministic import path
    if 'app.js' in file_path and dep_path.startswith('src/config/'):
        return None

    # app.js -> middleware/*: deterministic import path
    if 'app.js' in file_path and dep_path.startswith('src/middleware/'):
        return None

    # server.js -> app.js: deterministic
    if 'server.js' in file_path and 'app.js' in dep_path:
        return None

    # routes/index.js -> routes/auth.js: deterministic
    if 'routes/index.js' in file_path and dep_path.endswith('.js'):
        return None

    # routes/auth.js -> models/users.js: deterministic
    if 'routes/auth.js' in file_path and 'models/users.js' in dep_path:
        return None

    # routes/auth.js -> config/database.js: deterministic
    if 'routes/auth.js' in file_path and 'config/database.js' in dep_path:
        return None

    # middleware/auth.js -> config/database.js: deterministic
    if 'middleware/auth.js' in file_path and 'config/database.js' in dep_path:
        return None

    # default assumption: non-obvious coupling
    return f"Unknown edge type: {purpose} -> {dep_purpose}"


rules = {
    'backend_framework': 'Express.js',
    'frontend_framework': 'React',
    'database': 'PostgreSQL',
    'auth_method': 'JWT',
    'deployment': 'AWS',
    'required_backend_modules': ['workspaces','projects','tasks'],
    'required_pages': ['Login','Dashboard','Settings'],
}
plan = generate_build_plan(rules)
files = plan['files']
bundles = group_and_partition_files(files)

bundle_of = {}
for name, bps in bundles.items():
    for bp in bps:
        bundle_of[bp['path']] = name

print("=" * 80)
print("BUNDLE COMPOSITION")
print("=" * 80)
for name, bps in sorted(bundles.items()):
    print(f"\n  [{name}] ({len(bps)} files)")
    for bp in bps:
        print(f"    {bp['path']}")

print()
print("=" * 80)
print("CROSS-BUNDLE DEPENDENCY EDGES")
print("=" * 80)

cross_total = 0
high_risk = []
low_risk = []

for f in sorted(files, key=lambda x: x['path']):
    f_bundle = bundle_of[f['path']]
    cross = [d for d in f.get('depends_on', []) if bundle_of.get(d, f_bundle) != f_bundle]
    if cross:
        cross_total += len(cross)
        dep_names = []
        dep_bundles = []
        for d in cross:
            dep_bundle = bundle_of.get(d, 'MISSING')
            dep_names.append(d)
            dep_bundles.append(dep_bundle)
        dep_purpose = ''
        for bp in files:
            if bp['path'] == cross[0]:
                dep_purpose = bp.get('purpose', '')
                break

        risk_reason = assess_risk(f['path'], f.get('purpose',''), cross[0], dep_purpose)
        annotation = "HIGH" if risk_reason else "LOW "
        if risk_reason:
            high_risk.append((f['path'], cross[0], risk_reason))
        else:
            low_risk.append((f['path'], cross[0]))
        print(f"  {annotation}: {f['path']:42s}  [{f_bundle:12s}]  ->  {cross[0]:35s}  [{dep_bundles[0]}]")

print()
print(f"Total cross-bundle edges: {cross_total}")
print(f"  High risk: {len(high_risk)}  |  Low risk: {len(low_risk)}")
if high_risk:
    print()
    print("HIGH-RISK EDGES:")
    for f, d, reason in high_risk:
        print(f"  {f} -> {d}")
        print(f"    {reason}")
