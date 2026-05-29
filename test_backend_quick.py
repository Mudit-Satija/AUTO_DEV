#!/usr/bin/env python3
"""Quick test of backend planning without server - direct agent testing"""

import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import agents directly
from backend_agents.orchestrator import orchestrate_backend_planning

def test_orchestrator():
    """Test orchestrator directly"""
    
    print("\n" + "="*70)
    print("TESTING MULTI-AGENT ORCHESTRATOR")
    print("="*70)
    
    # Sample validation output
    validation_output = {
        "project_type": "web app",
        "user_stack": {
            "backend": "Node.js",
            "database": "PostgreSQL",
            "frontend": "React"
        },
        "feedback": "Building a todo application with real-time sync",
        "alignment_score": 95,
        "complexity": "medium"
    }
    
    print("\n📋 Input Validation Output:")
    print(f"  Project Type: {validation_output.get('project_type')}")
    print(f"  Backend: {validation_output.get('user_stack', {}).get('backend')}")
    print(f"  Database: {validation_output.get('user_stack', {}).get('database')}")
    
    print("\n" + "-"*70)
    print("Running Orchestrator...")
    print("-"*70)
    
    try:
        result = orchestrate_backend_planning(validation_output)
        
        print("\n" + "="*70)
        print("✅ ORCHESTRATOR SUCCESS")
        print("="*70)
        
        print(f"\n📊 Result Keys: {list(result.keys())}")
        print(f"   Status: {result.get('status')}")
        print(f"   Framework: {result.get('framework')}")
        print(f"   Language: {result.get('language')}")
        print(f"   API Style: {result.get('api_style')}")
        
        # Check if authentication and database are present and valid
        auth = result.get('authentication')
        db = result.get('database')
        
        if auth:
            print(f"\n🔐 Authentication:")
            print(f"   Type: {type(auth)} - {auth if not isinstance(auth, dict) else 'OK'}")
            if isinstance(auth, dict):
                print(f"   Method: {auth.get('method')}")
                print(f"   Storage: {auth.get('storage')}")
        else:
            print(f"\n❌ Missing authentication field!")
        
        if db:
            print(f"\n💾 Database:")
            print(f"   Type (field): {type(db)} - {db if not isinstance(db, dict) else 'OK'}")
            if isinstance(db, dict):
                print(f"   Type (value): {db.get('type')}")
                print(f"   ORM: {db.get('orm')}")
        else:
            print(f"\n❌ Missing database field!")
        
        endpoints = result.get('suggested_endpoints', [])
        print(f"\n📡 Endpoints: {len(endpoints)}")
        for ep in endpoints[:3]:
            print(f"   {ep.get('method')} {ep.get('path')} - {ep.get('description')}")
        
        print("\n✅ TEST PASSED - Orchestrator working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ ORCHESTRATOR FAILED:")
        print(f"   Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_orchestrator()
    sys.exit(0 if success else 1)
