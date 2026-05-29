---
name: validation-schema
description: "Use when working on the Auto_devv validation system. Ensures all validation responses follow the strict 7-field schema: status, project_type, complexity, missing_requirements, recommended_stack, feedback, reasoning."
---

# AI Validation System Schema Skill

## Schema Definition

All validation responses MUST include these 7 fields:

```json
{
  "status": "success or error",
  "project_type": "web app | mobile app | AI system | automation | CRUD backend | SaaS",
  "complexity": "beginner | intermediate | advanced",
  "missing_requirements": ["array of strings"],
  "recommended_stack": {
    "backend": ["tools"],
    "frontend": ["tools"],
    "database": ["tools"],
    "devops": ["tools"]
  },
  "feedback": "human readable explanation",
  "reasoning": "why we detected these conclusions"
}
```

## Pydantic Models

### ValidationResponse
- status: str (required)
- project_type: str (required, default="unknown")
- complexity: str (required, default="beginner")
- missing_requirements: List[str] (required, default=[])
- recommended_stack: TechStack (required, default=empty TechStack)
- feedback: str (required)
- reasoning: str (required)

### TechStack
- backend: List[str] (default=[])
- frontend: List[str] (default=[])
- database: List[str] (default=[])
- devops: List[str] (default=[])

## Implementation Rules

1. **Never mark fields as Optional** - All fields must be present in response
2. **Always populate with defaults** if LLM doesn't provide them:
   - project_type: "unknown"
   - complexity: "beginner"
   - recommended_stack: empty TechStack
3. **Force all fields in code** before returning response
4. **Don't rely on Pydantic to add missing fields** - explicitly set them in validation_agent.py
5. **Error responses must include all 7 fields** with defaults

## Code Pattern

```python
response = ValidationResponse(
    status=status,
    project_type=project_type or "unknown",
    complexity=complexity or "beginner",
    missing_requirements=missing_requirements or [],
    recommended_stack=tech_stack,  # TechStack with defaults
    feedback=feedback or "",
    reasoning=reasoning or ""
)
```

## Files Affected

- `schemas.py` - Pydantic models (NO Optional fields)
- `validation_agent.py` - Force defaults in validate_prompt()
- `main.py` - FastAPI endpoint (no changes needed)
- `llm_client.py` - LLM client (no changes needed)

## Testing

Every validation response should include all 7 fields:

```powershell
$body = @{prompt = "Build a chat app"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/validate" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json -Depth 10
```

Response must have: status, project_type, complexity, missing_requirements, recommended_stack, feedback, reasoning
