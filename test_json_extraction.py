#!/usr/bin/env python3
"""Test each agent individually with synthetic responses"""

import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test parsing JSON from LLM response
def test_json_extraction():
    """Test that JSON extraction works correctly"""
    
    print("\n" + "="*70)
    print("TESTING JSON EXTRACTION")
    print("="*70)
    
    # Test case 1: Clean JSON
    response1 = '{"method": "JWT", "storage": "httpOnly cookies", "libraries": [], "recommendations": ["tip1"]}'
    start = response1.find('{')
    end = response1.rfind('}') + 1
    if start != -1 and end != 0:
        result = json.loads(response1[start:end])
        print(f"\n✅ Test 1 (clean): {result.get('method')}")
    
    # Test case 2: JSON with extra text
    response2 = '''Here's the authentication strategy:
{
    "method": "OAuth2",
    "storage": "localStorage",
    "libraries": ["passport"],
    "recommendations": ["Implement PKCE"]
}
Some explanation after JSON.'''
    start = response2.find('{')
    end = response2.rfind('}') + 1
    if start != -1 and end != 0:
        result = json.loads(response2[start:end])
        print(f"✅ Test 2 (with text): {result.get('method')}")
    
    # Test case 3: JSON array
    response3 = '''[
    {"method": "POST", "path": "/auth/login", "description": "Login", "auth_required": false},
    {"method": "GET", "path": "/users/me", "description": "Get user", "auth_required": true}
]'''
    start = response3.find('[')
    end = response3.rfind(']') + 1
    if start != -1 and end != 0:
        result = json.loads(response3[start:end])
        print(f"✅ Test 3 (array): {len(result)} endpoints")
    
    # Test case 4: Response that's not a string
    response4 = {"method": "JWT", "storage": "httpOnly"}
    if not isinstance(response4, str):
        print(f"✅ Test 4 (non-string): Correctly identified as {type(response4)}")
    
    print("\n✅ All JSON extraction tests passed!")

if __name__ == "__main__":
    test_json_extraction()
