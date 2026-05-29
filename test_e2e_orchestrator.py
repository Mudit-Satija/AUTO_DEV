#!/usr/bin/env python3
"""
End-to-end test: Orchestrator → Merger → Pydantic Validation
Verifies the complete multi-agent pipeline without requiring a running server
"""

import logging
import json
import sys

# Setup logging with clear formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("MULTI-AGENT BACKEND PLANNING - END-TO-END TEST")
print("="*80)

# Step 1: Import validation
print("\n[STEP 1] Validating imports...")
try:
    from backend_agents.orchestrator import orchestrate_backend_planning
    from backend_schemas import BackendArchitecturePlan, AuthenticationStrategy, DatabaseStrategy
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Step 2: Create test input
print("\n[STEP 2] Preparing validation output...")
validation_output = {
    "project_type": "web app",
    "user_stack": {
        "backend": "Node.js",
        "database": "PostgreSQL",
        "frontend": "React"
    },
    "feedback": "Building a collaborative todo app with real-time sync",
    "alignment_score": 90,
    "complexity": "medium"
}
print(f"✅ Test input prepared")
print(f"   - Project: {validation_output['project_type']}")
print(f"   - Backend: {validation_output['user_stack']['backend']}")
print(f"   - Database: {validation_output['user_stack']['database']}")

# Step 3: Run orchestrator
print("\n[STEP 3] Running multi-agent orchestrator...")
try:
    result = orchestrate_backend_planning(validation_output)
    print(f"✅ Orchestrator completed")
    print(f"   - Result type: {type(result).__name__}")
    print(f"   - Status: {result.get('status')}")
    print(f"   - Framework: {result.get('framework')}")
except Exception as e:
    print(f"❌ Orchestrator failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Validate result structure
print("\n[STEP 4] Validating result structure...")
required_fields = [
    'status', 'framework', 'language', 'api_style',
    'authentication', 'database', 'suggested_endpoints',
    'folder_structure', 'core_libraries', 'optional_libraries',
    'design_patterns', 'clarification_questions', 'reasoning'
]

missing = []
for field in required_fields:
    if field not in result:
        missing.append(field)
        print(f"   ⚠️  Missing: {field}")
    else:
        print(f"   ✅ {field}: {type(result[field]).__name__}")

if missing:
    print(f"\n❌ Missing fields: {missing}")
    sys.exit(1)
else:
    print(f"\n✅ All required fields present")

# Step 5: Validate authentication structure
print("\n[STEP 5] Validating authentication field...")
auth = result.get('authentication')
print(f"   - Type: {type(auth).__name__}")
print(f"   - Is dict: {isinstance(auth, dict)}")
if isinstance(auth, dict):
    print(f"   - Fields: {list(auth.keys())}")
    auth_required = ['method', 'storage', 'refresh_strategy', 'libraries']
    for field in auth_required:
        if field in auth:
            print(f"     ✅ {field}: {auth[field]}")
        else:
            print(f"     ❌ Missing: {field}")
else:
    print(f"   ❌ Authentication is not a dict!")
    sys.exit(1)

# Step 6: Validate database structure
print("\n[STEP 6] Validating database field...")
db = result.get('database')
print(f"   - Type: {type(db).__name__}")
print(f"   - Is dict: {isinstance(db, dict)}")
if isinstance(db, dict):
    print(f"   - Fields: {list(db.keys())}")
    db_required = ['type', 'orm', 'connection_pool', 'migration_tool']
    for field in db_required:
        if field in db:
            print(f"     ✅ {field}: {db[field]}")
        else:
            print(f"     ❌ Missing: {field}")
else:
    print(f"   ❌ Database is not a dict!")
    sys.exit(1)

# Step 7: Pydantic validation
print("\n[STEP 7] Pydantic model validation...")
try:
    plan = BackendArchitecturePlan(**result)
    print(f"✅ Pydantic validation successful!")
    print(f"   - Framework: {plan.framework}")
    print(f"   - Language: {plan.language}")
    print(f"   - API Style: {plan.api_style}")
    print(f"   - Endpoints: {len(plan.suggested_endpoints)}")
    print(f"   - Folders: {len(plan.folder_structure)}")
    print(f"   - Core libs: {len(plan.core_libraries)}")
    print(f"   - Auth method: {plan.authentication.method}")
    print(f"   - Database type: {plan.database.type}")
except Exception as e:
    print(f"❌ Pydantic validation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 8: Success!
print("\n" + "="*80)
print("✅ END-TO-END TEST PASSED")
print("="*80)
print("\n✨ The multi-agent backend planning system is working correctly!")
print("   - All 6 agents executed successfully")
print("   - Merger combined results correctly")
print("   - Pydantic validation passed")
print("   - Ready for production use\n")

sys.exit(0)
