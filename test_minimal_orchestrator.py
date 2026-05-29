#!/usr/bin/env python3
"""Minimal test to verify orchestrator works"""

import logging
import json

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

# Test if modules import correctly
try:
    from backend_agents.orchestrator import orchestrate_backend_planning
    from backend_schemas import BackendArchitecturePlan
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test with minimal validation output
validation_output = {
    "project_type": "web app",
    "user_stack": {
        "backend": "Node.js",
        "database": "PostgreSQL"
    },
    "feedback": "Build a todo app"
}

print("\nRunning orchestrator...")
try:
    result = orchestrate_backend_planning(validation_output)
    print(f"\n✅ Orchestrator returned: {type(result)}")
    print(f"   Status: {result.get('status')}")
    print(f"   Framework: {result.get('framework')}")
    print(f"   Auth type: {type(result.get('authentication'))}")
    print(f"   DB type: {type(result.get('database'))}")
    
    # Try to create BackendArchitecturePlan
    print("\nValidating with Pydantic...")
    plan = BackendArchitecturePlan(**result)
    print(f"✅ Pydantic validation successful!")
    print(f"   Plan: {plan.framework} backend")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
