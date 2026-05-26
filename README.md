# AI Validation System - Setup & Testing Guide

## Project Structure
```
Auto_devv/
├── main.py                 # FastAPI app with /validate endpoint
├── llm_client.py          # NVIDIA API wrapper
├── validation_agent.py    # Validation logic
├── schemas.py             # Pydantic models
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## Setup Instructions

### 1. Get NVIDIA API Key
- Go to: https://build.nvidia.com/
- Sign up or login
- Create API key
- Copy the key

### 2. Configure Environment
Edit `.env` file and add your key:
```
NVIDIA_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Server
```bash
python main.py
```

Server will start at: `http://localhost:8000`

## Testing the Endpoint

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "ok"}
```

### Validate a Prompt

Using curl:
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build a login system"}'
```

Using Python requests:
```python
import requests

response = requests.post(
    "http://localhost:8000/validate",
    json={"prompt": "Build a login system"}
)

print(response.json())
```

Using PowerShell:
```powershell
$body = @{prompt = "Build a login system"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:8000/validate" `
  -Method POST -Body $body -ContentType "application/json"
$response | ConvertTo-Json
```

## Example Response

```json
{
  "status": "success",
  "missing_requirements": [
    "Database schema not specified",
    "Authentication method not mentioned",
    "User password hashing strategy missing"
  ],
  "feedback": "Good starting point but needs more technical details",
  "reasoning": "A login system requires clear specification of storage, security, and authentication approach"
}
```

## API Documentation

Once server is running, visit:
```
http://localhost:8000/docs
```

This shows interactive API documentation (Swagger UI)

## How It Works

1. User sends prompt to `/validate` endpoint
2. `validation_agent.py` creates a validation instruction
3. `llm_client.py` sends it to NVIDIA API (DeepSeek R1)
4. Response is parsed as JSON
5. Structured response returned to user

## Error Handling

If API key is missing:
```
ValueError: NVIDIA_API_KEY not found in environment variables
```

If API fails:
```json
{
  "status": "error",
  "missing_requirements": [],
  "feedback": "API Error details"
}
```

## Next Steps (When Ready)

- [ ] Test with multiple prompts
- [ ] Add validation rules beyond LLM
- [ ] Create simple test suite
- [ ] Add logging
- [ ] Handle rate limiting
- [ ] Add more endpoints (when needed)
