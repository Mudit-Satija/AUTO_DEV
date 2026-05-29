import requests
import os
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Default models for different tasks
DEFAULT_MODEL = "meta/llama-3.1-8b-instruct"                    # Fast validation
CODER_MODEL = "qwen/qwen3-next-80b-a3b-instruct"  # ✅ CORRECT

print("=" * 60)
print("LLM CLIENT INITIALIZED")
print("=" * 60)
print(f"Default Model: {DEFAULT_MODEL}")
print(f"Coder Model: {CODER_MODEL}")
print(f"API Key loaded: {NVIDIA_API_KEY[:30] if NVIDIA_API_KEY else 'NONE'}...")
print("=" * 60)


def get_llm_response(prompt: str, model: str = None):
    """Send prompt to NVIDIA API with optional model override
    
    Args:
        prompt: The prompt to send to the LLM
        model: Optional model override (defaults to DEFAULT_MODEL)
               Use CODER_MODEL for backend/code generation tasks
    
    Returns:
        str: The LLM response text
    """
    
    if not model:
        model = DEFAULT_MODEL
    
    if not NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY not found in environment variables")
    
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        print(f"\n{'='*60}")
        print(f"DEBUG: Using model: {model}")
        print(f"DEBUG: Prompt length: {len(prompt)} characters")
        print(f"{'='*60}")
        
        response = requests.post(
            NVIDIA_URL,
            headers=headers,
            json=payload,
            timeout=180
        )
        
        print(f"DEBUG: Status Code: {response.status_code}")
        print(f"DEBUG: Response preview: {response.text[:200]}")
        print(f"{'='*60}\n")
        
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        raise
    except Exception as e:
        print(f"ERROR: Unexpected error: {type(e).__name__}: {str(e)}")
        raise


# Export models for use in agents
__all__ = ["get_llm_response", "DEFAULT_MODEL", "CODER_MODEL"]