import requests
import json

BASE_URL = "http://localhost:8000"

def test_complete_flow():
    """Test complete flow: Validation -> Backend Planning"""
    
    print("🚀 INTERACTIVE VALIDATION + BACKEND PLANNING TESTER")
    print("="*70)
    
    prompt = input("\n📝 What's your project idea? ").strip()
    if not prompt:
        print("❌ Empty prompt. Exiting.")
        return
    
    conversation = []
    validation_result = None
    
    # ============================================================
    # PHASE 1: INTERACTIVE VALIDATION (Asking Questions)
    # ============================================================
    print("\n" + "="*70)
    print("PHASE 1: INTERACTIVE VALIDATION (Asking Questions)")
    print("="*70)
    
    while True:
        # Send validation request
        payload = {
            "prompt": prompt,
            "conversation": conversation
        }
        
        response = requests.post(f"{BASE_URL}/validate-interactive", json=payload)
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        status = data.get('status')
        
        print(f"\n📊 Status: {status}")
        
        if status == 'collecting_info':
            # Still asking questions
            question = data.get('current_question', '')
            print(f"\n🤖 {question}\n")
            
            # Add assistant question to conversation
            conversation.append({
                "role": "assistant",
                "content": question
            })
            
            # Get user answer
            answer = input("You: ").strip()
            if not answer:
                print("⚠️ Skipping question...")
                break
                
            # Add user answer to conversation
            conversation.append({
                "role": "user",
                "content": answer
            })
            
        elif status == 'success':
            # Got final validation result
            validation_result = data
            
            print(f"\n✅ VALIDATION COMPLETE\n")
            print(f"Project Type: {data.get('project_type')}")
            print(f"Complexity: {data.get('complexity')}")
            print(f"Alignment Score: {data.get('alignment_score')}/100")
            
            print(f"\n📊 YOUR CHOSEN STACK:")
            user_stack = data.get('user_stack', {})
            for key, value in user_stack.items():
                if value:
                    print(f"  {key.title()}: {value}")
            
            print(f"\n💡 FEEDBACK:\n{data.get('feedback')}")
            
            break
        else:
            # Error status
            print(f"\n❌ Error: {data.get('reasoning', 'Unknown error')}")
            return
    
    if not validation_result:
        print("\n⚠️ No validation result. Exiting.")
        return
    
    # ============================================================
    # PHASE 2: BACKEND PLANNING (Using Validation Output)
    # ============================================================
    print("\n" + "="*70)
    print("PHASE 2: BACKEND PLANNING (Generating Architecture)")
    print("="*70)
    
    # Prepare backend planning request with validation output
    backend_payload = {
        "validation_output": {
            "project_type": validation_result.get("project_type"),
            "user_stack": validation_result.get("user_stack"),
            "feedback": validation_result.get("feedback")
        }
    }
    
    print("\n🔄 Sending validation output to backend planning agent...")
    print(f"   Project Type: {validation_result.get('project_type')}")
    print(f"   User Stack: {validation_result.get('user_stack')}")
    
    try:
        backend_response = requests.post(
            f"{BASE_URL}/plan-backend",
            json=backend_payload,
            timeout=300  # 5 minutes timeout
        )
        
        if backend_response.status_code != 200:
            print(f"\n❌ Backend Planning Error: {backend_response.status_code}")
            print(backend_response.text)
            return
        
        backend_plan = backend_response.json()
        
        # ============================================================
        # DISPLAY RESULTS
        # ============================================================
        print("\n" + "="*70)
        print("✅ FINAL BACKEND ARCHITECTURE PLAN")
        print("="*70)
        
        print(f"\n🏗️  ARCHITECTURE:")
        print(f"   Framework: {backend_plan.get('framework', 'Unknown')}")
        print(f"   Language: {backend_plan.get('language', 'Unknown')}")
        print(f"   API Style: {backend_plan.get('api_style', 'Unknown')}")
        
        print(f"\n🔐 AUTHENTICATION:")
        auth = backend_plan.get('authentication', {})
        print(f"   Method: {auth.get('method', 'Unknown')}")
        print(f"   Storage: {auth.get('storage', 'Unknown')}")
        print(f"   Refresh Strategy: {auth.get('refresh_strategy', 'Unknown')}")
        if auth.get('libraries'):
            print(f"   Libraries: {', '.join(auth.get('libraries', []))}")
        
        print(f"\n💾 DATABASE:")
        db = backend_plan.get('database', {})
        print(f"   Type: {db.get('type', 'Unknown')}")
        print(f"   ORM: {db.get('orm', 'Unknown')}")
        print(f"   Connection Pool: {db.get('connection_pool', False)}")
        print(f"   Migration Tool: {db.get('migration_tool', 'Unknown')}")
        
        print(f"\n📡 SUGGESTED ENDPOINTS ({len(backend_plan.get('suggested_endpoints', []))}):")
        for endpoint in backend_plan.get('suggested_endpoints', [])[:5]:
            auth_req = "🔐" if endpoint.get('auth_required') else "🔓"
            print(f"   {auth_req} {endpoint.get('method', 'GET')} {endpoint.get('path', 'N/A')}")
            print(f"      → {endpoint.get('description', '')}")
        if len(backend_plan.get('suggested_endpoints', [])) > 5:
            print(f"   ... and {len(backend_plan.get('suggested_endpoints', [])) - 5} more")
        
        print(f"\n📁 FOLDER STRUCTURE:")
        for folder in backend_plan.get('folder_structure', []):
            print(f"   📦 {folder.get('name', 'N/A')}")
            if folder.get('children'):
                for child in folder.get('children', []):
                    print(f"      ├─ {child}")
        
        print(f"\n📚 CORE LIBRARIES:")
        for lib in backend_plan.get('core_libraries', []):
            print(f"   • {lib}")
        
        print(f"\n⚙️  OPTIONAL LIBRARIES:")
        opt_libs = backend_plan.get('optional_libraries', {})
        for lib, desc in opt_libs.items():
            print(f"   • {lib}: {desc}")
        
        print(f"\n🎯 DESIGN PATTERNS:")
        for pattern in backend_plan.get('design_patterns', []):
            print(f"   • {pattern}")
        
        print(f"\n💡 REASONING:")
        print(f"{backend_plan.get('reasoning', 'N/A')}")
        
        print("\n" + "="*70)
        print("✅ FLOW COMPLETE!")
        print("="*70)
        
        # Option to save results
        save = input("\n💾 Save results to file? (y/n): ").strip().lower()
        if save == 'y':
            results = {
                "validation": validation_result,
                "backend_plan": backend_plan
            }
            
            with open("flow_results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            print("✅ Results saved to flow_results.json")
        
    except requests.exceptions.Timeout:
        print("\n❌ Backend planning timed out. The model is taking too long.")
        print("   Try again or simplify your project idea.")
    except Exception as e:
        print(f"\n❌ Error during backend planning: {str(e)}")
        return


if __name__ == "__main__":
    test_complete_flow()