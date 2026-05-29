# AI Project Planning & Backend Architecture System

Complete system for project validation, interactive planning, and backend architecture generation using NVIDIA LLM API.

## System Architecture

```
User Input
    ↓
/validate (Quick validation)
    ↓
/validate-interactive (Conversational Q&A)
    ↓
/plan-backend (Architecture planning)
```

## Project Structure
```
Auto_devv/
├── main.py                      # FastAPI app with 3 endpoints
├── llm_client.py               # NVIDIA API wrapper
├── validation_agent.py          # Validation logic & interactive Q&A
├── backend_planning_agent.py    # Backend architecture planning
├── schemas.py                   # Pydantic models for validation
├── backend_schemas.py           # Pydantic models for backend planning
├── requirements.txt             # Dependencies
├── .env                         # Environment variables
├── test_simple.py              # Interactive test script
└── README.md                   # This file
```

## Setup Instructions

### 1. Get NVIDIA API Key
- Go to: https://build.nvidia.com/
- Sign up or login
- Create API key
- Copy the key

### 2. Configure Environment
Edit `.env` file:
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

Server runs at: `http://localhost:8000`

## API Endpoints

### 1. Health Check
**Endpoint:** `GET /health`

Check if server is running.

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "ok"}
```

---

### 2. Quick Validation
**Endpoint:** `POST /validate`

Quickly validate a project idea (one API call, no conversation).

**Request:**
```json
{
  "prompt": "I want to build a real-time chat app with user accounts"
}
```

**PowerShell:**
```powershell
$body = @{prompt = "Build a chat app"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/validate" `
  -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json
```

**Response:**
```json
{
  "status": "success",
  "project_type": "AI system",
  "complexity": "intermediate",
  "missing_requirements": ["LLM provider choice", "real-time protocol"],
  "recommended_stack": {
    "backend": ["FastAPI", "Node.js"],
    "frontend": ["React", "Vue"],
    "database": ["PostgreSQL", "MongoDB"],
    "devops": ["Docker", "Kubernetes"]
  },
  "feedback": "Chat app requires LLM integration and WebSocket support",
  "reasoning": "Complex project with multiple moving parts"
}
```

---

### 3. Interactive Validation
**Endpoint:** `POST /validate-interactive`

Multi-turn conversation where LLM asks clarifying questions until enough info is gathered.

**Flow:**
1. Send project idea with empty conversation
2. LLM asks: "What backend?" → You answer
3. LLM asks: "What frontend?" → You answer
4. LLM asks: "What database?" → You answer
5. (Optional) LLM asks: "Real-time features?" → You answer
6. (Optional) LLM asks: "Where deploy?" → You answer
7. Returns final validation with alignment_score

**First Message:**
```json
{
  "prompt": "I want to build a chatbot",
  "conversation": []
}
```

**Subsequent Messages (add Q&A to conversation array):**
```json
{
  "prompt": "I want to build a chatbot",
  "conversation": [
    {
      "role": "assistant",
      "content": "What backend framework are you thinking of?"
    },
    {
      "role": "user",
      "content": "FastAPI"
    }
  ]
}
```

**Final Response (when enough info gathered):**
```json
{
  "status": "success",
  "project_type": "AI system",
  "complexity": "intermediate",
  "user_stack": {
    "backend": "FastAPI",
    "frontend": "React",
    "database": "PostgreSQL",
    "deployment": "AWS"
  },
  "recommended_stack": {...},
  "alignment_score": 85,
  "missing_requirements": [...],
  "feedback": "Good stack fit for chatbot",
  "reasoning": "FastAPI+PostgreSQL is solid for AI backends"
}
```

**Interactive Test (Easy!):**
```bash
python test_simple.py
```
Just type answers as it asks questions!

---

### 4. Backend Architecture Planning
**Endpoint:** `POST /plan-backend`

Generate detailed backend architecture plan from validation output or direct input.

**Option A: From Validation Output**
```json
{
  "validation_output": {
    "project_type": "web app",
    "feedback": "Todo app with user accounts",
    "user_stack": {
      "backend": "Node.js",
      "frontend": "React",
      "database": "MongoDB"
    }
  }
}
```

**Option B: Direct Input**
```json
{
  "project_idea": "Create a todo app",
  "project_type": "web app",
  "user_stack": {
    "backend": "FastAPI",
    "database": "PostgreSQL"
  }
}
```

**PowerShell:**
```powershell
$body = @{
    project_idea = "Todo app with user accounts"
    project_type = "web app"
    user_stack = @{
        backend = "Node.js"
        database = "MongoDB"
        deployment = "AWS"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/plan-backend" `
  -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json -Depth 10
```

**Response:**
```json
{
  "status": "success",
  "framework": "Express.js",
  "language": "Node.js",
  "api_style": "REST",
  "authentication": {
    "method": "JWT",
    "storage": "httpOnly cookies",
    "refresh_strategy": "Refresh token rotation",
    "libraries": ["jsonwebtoken", "bcryptjs"]
  },
  "database": {
    "type": "MongoDB",
    "orm": "Mongoose",
    "connection_pool": true,
    "migration_tool": "N/A"
  },
  "suggested_endpoints": [
    {"method": "POST", "path": "/api/auth/register", "description": "Register user", "auth_required": false},
    {"method": "POST", "path": "/api/auth/login", "description": "Login user", "auth_required": false},
    {"method": "GET", "path": "/api/users/me", "description": "Get profile", "auth_required": true},
    {"method": "GET", "path": "/api/todos", "description": "List todos", "auth_required": true},
    {"method": "POST", "path": "/api/todos", "description": "Create todo", "auth_required": true}
  ],
  "folder_structure": [
    {"name": "src/", "description": "Main code", "children": ["routes/", "controllers/", "models/", "services/"]},
    {"name": "tests/", "description": "Test files", "children": []},
    {"name": "config/", "description": "Configuration", "children": []}
  ],
  "core_libraries": ["express", "mongoose", "jsonwebtoken", "bcryptjs", "dotenv", "cors"],
  "optional_libraries": {
    "morgan": "HTTP logging",
    "helmet": "Security headers",
    "redis": "Caching"
  },
  "design_patterns": ["MVC", "Service Layer", "Repository Pattern"],
  "clarification_questions": [],
  "reasoning": "Express.js is production-ready for REST APIs, Mongoose handles MongoDB elegantly, JWT+httpOnly cookies is industry standard for web apps"
}
```

---

## Complete Workflow Example

**Step 1: Interactive validation to gather requirements**
```bash
python test_simple.py
# Answer questions: FastAPI → React → PostgreSQL → AWS
```

**Step 2: Get final validation output**
```
Status: success
Project Type: web app
Alignment Score: 88/100
```

**Step 3: Use validation output for backend planning**
```powershell
$validation = <output from step 2>
$body = @{ validation_output = $validation } | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/plan-backend" `
  -Method POST -Body $body -ContentType "application/json"
```

**Step 4: Get backend architecture**
- Framework choice: FastAPI
- Authentication strategy: JWT
- Database setup: SQLAlchemy with PostgreSQL
- 7 REST endpoints ready to implement
- Folder structure defined
- Libraries listed (core + optional)
- Design patterns recommended

---

## How It Works

### /validate Flow
1. User sends prompt
2. LLM analyzes project requirements
3. Returns: project_type, complexity, missing_requirements, recommended_stack

### /validate-interactive Flow
1. First call: Send project idea + empty conversation
2. LLM asks: "What backend?" → Extract user's answer
3. Check if we have enough info (backend + frontend + database)
4. If not enough: Return next question
5. If enough: Return final validation with alignment_score

### /plan-backend Flow
1. Extract user's stack choices from validation output
2. Send to LLM with architecture planning prompt
3. LLM matches backend framework to tech stack
4. LLM suggests: auth strategy, database ORM, endpoints, folder structure
5. LLM recommends: core libraries, optional libraries, design patterns
6. Return complete architecture plan as JSON

---

## Error Handling

**Missing API Key:**
```
ValueError: NVIDIA_API_KEY not found in environment variables
```

**API Request Failed:**
```json
{
  "status": "error",
  "framework": "unknown",
  "reasoning": "API Error details"
}
```

**Interactive Mode - Vague Answer:**
```
Status: collecting_info
Question: "Can you be more specific? PostgreSQL, MongoDB, MySQL, or Redis?"
```

---

## Interactive API Docs

Once server is running, visit:
```
http://localhost:8000/docs
```

This shows Swagger UI with:
- All endpoints
- Request/response schemas
- Try-it-out feature
- Full API documentation

---

## What Each System Does

| System | Input | Output |
|--------|-------|--------|
| `/validate` | Project idea string | 7-field validation (type, complexity, missing, stack) |
| `/validate-interactive` | Idea + conversation history | Either next question OR final validation with alignment_score |
| `/plan-backend` | Validation output OR direct stack | Backend architecture plan (framework, auth, database, endpoints, structure) |

---

## Why This Architecture

✅ **Modular**: Each endpoint solves one problem  
✅ **Conversational**: Interactive mode gathers info naturally  
✅ **Practical**: Backend plan is ready to implement  
✅ **Minimal**: Only planning, no code generation  
✅ **Stack-aware**: Suggests only technologies user chose  
✅ **LLM-powered**: Uses NVIDIA's DeepSeek for reasoning  

---

## Limitations & Notes

- Only PLANNING (no code generation)
- No database persistence (in-memory conversations)
- No authentication on endpoints (for testing)
- NVIDIA API required (register at build.nvidia.com)
- Max ~5 interactive turns before finalization
- Best results with clear project descriptions

---

## Next Steps (Optional Future Work)

- [ ] Add code generation from architecture plan
- [ ] Persist conversations to database
- [ ] Add authentication to endpoints
- [ ] Frontend UI for interactive flow
- [ ] Support for more backends (Go, Rust, etc)
- [ ] Multi-phase planning (database schema, frontend components)
- [ ] Export architecture to markdown/diagrams
