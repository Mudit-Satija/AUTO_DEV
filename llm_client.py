import requests
import os
import time
import threading
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "180"))

# Rate limiter — paces requests to avoid 429 from concurrent bundles
_rate_limiter_lock = threading.Lock()
_last_request_time = 0.0
_MIN_INTERVAL_SECONDS = 0.6  # 0.6s between requests

def _rate_limit_pacer():
    global _last_request_time
    with _rate_limiter_lock:
        now = time.perf_counter()
        elapsed = now - _last_request_time
        if elapsed < _MIN_INTERVAL_SECONDS:
            sleep_time = _MIN_INTERVAL_SECONDS - elapsed
            time.sleep(sleep_time)
        _last_request_time = time.perf_counter()

    
DEFAULT_MODEL = "meta/llama-3.1-8b-instruct"                   
CODER_MODEL = "mistralai/mistral-small-4-119b-2603"  
PLANNER_MODEL = DEFAULT_MODEL

print("=" * 60)
print("LLM CLIENT INITIALIZED")
print("=" * 60)
print(f"Default Model: {DEFAULT_MODEL}")
print(f"Coder Model: {CODER_MODEL}")
print(f"API Key loaded: {'Yes' if NVIDIA_API_KEY else 'NONE'}")
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
    
    max_retries = 5
    backoffs = [3.0, 6.0, 12.0, 24.0, 30.0]

    for attempt in range(max_retries + 1):
        try:
            _rate_limit_pacer()

            print(f"\n{'='*60}")
            print(f"DEBUG: Using model: {model} (Attempt {attempt + 1}/{max_retries + 1})")
            print(f"DEBUG: Prompt length: {len(prompt)} characters")
            print(f"{'='*60}")
            
            response = requests.post(
                NVIDIA_URL,
                headers=headers,
                json=payload,
                timeout=LLM_TIMEOUT_SECONDS
            )
            
            print(f"DEBUG: Status Code: {response.status_code}")
            print(f"DEBUG: Response preview: {response.text[:200]}")
            print(f"{'='*60}\n")
            
            # Check for specific retryable status codes
            if response.status_code == 429 or (500 <= response.status_code < 600):
                if attempt < max_retries:
                    delay = backoffs[attempt]
                    print(f"WARNING: Got status code {response.status_code}. Retrying in {delay}s...")
                    time.sleep(delay)
                    continue
            
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < max_retries:
                delay = backoffs[attempt]
                print(f"WARNING: Network error {type(e).__name__}. Retrying in {delay}s...")
                time.sleep(delay)
                continue
            else:
                print(f"ERROR: Max retries exceeded for network error: {e}")
                raise
        except requests.exceptions.RequestException as e:
            # If we got a response and it's not a 429/5xx, we should raise immediately
            status_code = getattr(getattr(e, 'response', None), 'status_code', None)
            if status_code and status_code != 429 and not (500 <= status_code < 600):
                print(f"ERROR: Non-retryable HTTP error {status_code}: {e}")
                raise
            
            if attempt < max_retries:
                delay = backoffs[attempt]
                print(f"WARNING: HTTP error {status_code}. Retrying in {delay}s...")
                time.sleep(delay)
                continue
            else:
                print(f"ERROR: Max retries exceeded for HTTP error: {e}")
                raise
        except Exception as e:
            print(f"ERROR: Unexpected error: {type(e).__name__}: {str(e)}")
            raise


# Export models for use in agents
__all__ = ["get_llm_response", "DEFAULT_MODEL", "CODER_MODEL", "PLANNER_MODEL"]
