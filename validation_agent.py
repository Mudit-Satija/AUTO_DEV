from llm_client import get_llm_response
from schemas import ValidationResponse, TechStack, InteractiveRequest, InteractiveResponse, ConversationMessage, UserStack
from planning_agents.shared.json_utils import extract_json
import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


BACKEND_OPTIONS = ["FastAPI", "Node.js", "Express", "Django", "Spring", "Go", "Python"]
FRONTEND_OPTIONS = ["React", "Next.js", "Vue", "Angular", "Flutter", "React Native", "Svelte"]
DATABASE_OPTIONS = ["PostgreSQL", "MongoDB", "MySQL", "Redis", "SQLite"]
DEPLOYMENT_OPTIONS = ["AWS", "GCP", "Azure", "Vercel", "Netlify", "Docker", "Kubernetes", "Serverless", "Self-hosted"]
REALTIME_OPTIONS = ["WebSocket", "Polling", "SSE", "None"]

FIELD_ORDER = ["backend", "frontend", "database", "deployment", "realtime"]
SLOT_ORDER = ["project_type", "backend_framework", "frontend_framework", "database", "deployment", "realtime"]
SLOT_TO_STACK_FIELD = {
    "backend_framework": "backend",
    "frontend_framework": "frontend",
    "database": "database",
    "deployment": "deployment",
    "realtime": "realtime",
}
SLOT_TO_LABEL = {
    "project_type": "project type",
    "backend_framework": "backend framework",
    "frontend_framework": "frontend framework",
    "database": "database",
    "deployment": "deployment",
    "realtime": "real-time requirements",
}


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _detect_from_text(text: str, keyword_map: Dict[str, List[str]], default_value: Optional[str] = None) -> Dict[str, Any]:
    normalized_text = _normalize_text(text)
    for value, keywords in keyword_map.items():
        for keyword in keywords:
            if keyword in normalized_text:
                return {"value": value, "confidence": 0.96, "source": keyword}
    if default_value is not None:
        return {"value": default_value, "confidence": 0.4, "source": "heuristic default"}
    return {"value": None, "confidence": 0.0, "source": None}


def _merge_detected_fields(*detected_maps: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for detected_map in detected_maps:
        for field, data in detected_map.items():
            if not data.get("value"):
                continue
            existing = merged.get(field)
            if existing is None or data.get("confidence", 0.0) >= existing.get("confidence", 0.0):
                merged[field] = data
    return merged


def _build_missing_fields(detected_fields: Dict[str, Dict[str, Any]]) -> List[str]:
    return [field for field in FIELD_ORDER if not detected_fields.get(field, {}).get("value")]


def _build_slot_ledger(prompt: str, conversation: Optional[List[ConversationMessage]] = None) -> Dict[str, Dict[str, Any]]:
    detected_information = extract_detected_information(prompt, conversation)
    slot_ledger: Dict[str, Dict[str, Any]] = {}

    project_type = detected_information.get("project_type", {})
    project_type_value = project_type.get("value") if isinstance(project_type, dict) else None
    slot_ledger["project_type"] = {
        "value": project_type_value,
        "status": "confirmed" if project_type_value else "missing",
    }

    for slot_name, stack_field in SLOT_TO_STACK_FIELD.items():
        slot_data = detected_information.get(stack_field, {})
        value = slot_data.get("value") if isinstance(slot_data, dict) else None
        source = slot_data.get("source") if isinstance(slot_data, dict) else None
        slot_ledger[slot_name] = {
            "value": value,
            "status": "confirmed" if value and source != "heuristic default" else "missing",
        }

    return slot_ledger


def _ledger_missing_slots(slot_ledger: Dict[str, Dict[str, Any]]) -> List[str]:
    return [slot for slot in SLOT_ORDER if slot_ledger.get(slot, {}).get("status") == "missing"]


def _ledger_to_user_stack(slot_ledger: Dict[str, Dict[str, Any]]) -> UserStack:
    return UserStack(
        backend=slot_ledger.get("backend_framework", {}).get("value"),
        frontend=slot_ledger.get("frontend_framework", {}).get("value"),
        database=slot_ledger.get("database", {}).get("value"),
        realtime=slot_ledger.get("realtime", {}).get("value"),
        deployment=slot_ledger.get("deployment", {}).get("value"),
    )


def extract_detected_information(prompt: str, conversation: Optional[List[ConversationMessage]] = None) -> Dict[str, Any]:
    """Infer known requirements from the initial prompt and conversation."""

    conversation = conversation or []
    prompt_text = _normalize_text(prompt)
    conversation_text = _normalize_text("\n".join(msg.content for msg in conversation if msg.role == "user"))
    combined_text = f"{prompt_text} {conversation_text}".strip()

    backend_map = {
        "FastAPI": ["fastapi", "fast api"],
        "Node.js": ["node.js", "nodejs", " node ", " node.js ", "node backend"],
        "Express": ["express"],
        "Django": ["django"],
        "Spring": ["spring boot", "spring"],
        "Go": ["golang", " go ", " go backend"],
        "Python": ["python"],
    }
    frontend_map = {
        "React": ["react"],
        "Next.js": ["next.js", "nextjs", "next"],
        "Vue": ["vue"],
        "Angular": ["angular"],
        "Flutter": ["flutter"],
        "React Native": ["react native"],
        "Svelte": ["svelte"],
    }
    database_map = {
        "PostgreSQL": ["postgresql", "postgres"],
        "MongoDB": ["mongodb", "mongo"],
        "MySQL": ["mysql"],
        "Redis": ["redis"],
        "SQLite": ["sqlite"],
    }
    deployment_map = {
        "AWS": ["aws"],
        "GCP": ["gcp", "google cloud", "google cloud platform"],
        "Azure": ["azure"],
        "Vercel": ["vercel"],
        "Netlify": ["netlify"],
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes", "k8s"],
        "Serverless": ["serverless"],
        "Self-hosted": ["self-hosted", "self hosted"],
    }
    realtime_map = {
        "WebSocket": ["websocket", "websockets", "real-time", "realtime", "live updates"],
        "Polling": ["polling"],
        "SSE": ["server sent events", "sse"],
        "None": ["no real-time", "no realtime", "without realtime", "without real-time"],
    }
    project_type_map = {
        "AI system": ["chatbot", "ai", "llm", "assistant", "copilot"],
        "SaaS": ["saas", "jira", "multi-tenant", "multi tenant", "workspace", "dashboard"],
        "CRUD backend": ["crud", "api", "rest api", "backend"],
        "automation": ["automation", "workflow", "bot", "script"],
        "web app": ["web app", "website", "frontend"],
        "mobile app": ["mobile", "ios", "android", "react native", "flutter"],
    }

    detected_fields = {
        "backend": _detect_from_text(combined_text, backend_map),
        "frontend": _detect_from_text(combined_text, frontend_map),
        "database": _detect_from_text(combined_text, database_map),
        "deployment": _detect_from_text(combined_text, deployment_map),
        "realtime": _detect_from_text(combined_text, realtime_map),
        "project_type": _detect_from_text(combined_text, project_type_map, default_value="web app"),
    }

    assumptions = []
    if detected_fields["project_type"]["confidence"] < 0.7:
        assumptions.append("Assume a web app unless the prompt indicates a different product type.")
    if not detected_fields["realtime"]["value"]:
        assumptions.append("Assume real-time behavior is not required until confirmed.")

    detected_values = {field: detected_fields[field]["value"] for field in FIELD_ORDER if detected_fields[field]["value"]}
    missing_fields = _build_missing_fields(detected_fields)
    missing_information = list(missing_fields)
    if detected_fields["project_type"]["value"] == "AI system":
        if not any(token in combined_text for token in ["llm", "openai", "anthropic", "hugging face", "local model", "model provider"]):
            missing_information.insert(0, "LLM provider or model")
        if not any(token in combined_text for token in ["memory", "chat history", "vector", "rag", "retrieval"]):
            missing_information.append("memory strategy")

    return {
        "detected_values": detected_values,
        "field_confidence": {field: detected_fields[field]["confidence"] for field in detected_fields},
        "field_sources": {field: detected_fields[field]["source"] for field in detected_fields},
        "missing_fields": missing_fields,
        "missing_information": missing_information,
        "assumptions": assumptions,
        "project_type": detected_fields["project_type"],
        "backend": detected_fields["backend"],
        "frontend": detected_fields["frontend"],
        "database": detected_fields["database"],
        "deployment": detected_fields["deployment"],
        "realtime": detected_fields["realtime"],
        "confidence": round(sum(item["confidence"] for item in detected_fields.values()) / len(detected_fields), 3),
        "summary": summarize_detected_information(detected_fields, missing_fields),
    }

# Enhanced system prompt with explicit instructions and examples
SYSTEM_PROMPT = """You are a software requirements analyzer. Analyze the prompt and return ONLY valid JSON.

RULES:
1. project_type MUST be one of: "web app", "mobile app", "AI system", "automation", "CRUD backend", "SaaS"
2. complexity MUST be one of: "beginner", "intermediate", "advanced"
3. recommended_stack should include programming languages/frameworks, NOT AWS services
4. missing_requirements should list specific technical gaps
5. Return ONLY JSON, no other text

TECH STACK GUIDELINES:
- backend: FastAPI, Django, Node.js, Express, Spring, Go, Python
- frontend: React, Vue, Angular, Next.js, Flutter, React Native
- database: PostgreSQL, MongoDB, MySQL, Redis, SQLite
- devops: Docker, Kubernetes, GitHub Actions, Jenkins, GitLab CI

EXAMPLES:

Example 1 - Input: "build a simple todo app"
Output:
{
    "status": "success",
    "project_type": "web app",
    "complexity": "beginner",
    "missing_requirements": ["database choice", "authentication approach", "deployment platform"],
    "recommended_stack": {"backend": ["FastAPI", "Node.js"], "frontend": ["React", "Vue"], "database": ["PostgreSQL", "SQLite"], "devops": ["Docker"]},
    "feedback": "Simple todo app is a good beginner project. You need to choose a database and decide on deployment.",
    "reasoning": "Todo apps are straightforward CRUD operations. Missing auth and deployment details make it incomplete."
}

Example 2 - Input: "create an AI chatbot with real-time chat, user authentication, chat history, and web interface"
Output:
{
    "status": "success",
    "project_type": "AI system",
    "complexity": "advanced",
    "missing_requirements": ["LLM provider choice (OpenAI/Hugging Face/local)", "real-time protocol (WebSocket/polling)", "vector database for embeddings"],
    "recommended_stack": {"backend": ["FastAPI", "Python"], "frontend": ["React", "Next.js"], "database": ["PostgreSQL", "Redis"], "devops": ["Docker", "Kubernetes"]},
    "feedback": "This is a complex AI project requiring LLM integration, real-time communication, and persistent storage. The requirements are mostly clear but LLM provider is missing.",
    "reasoning": "Chatbots need LLM integration (advanced), WebSockets for real-time (advanced), and vector DB for context (advanced). Three missing critical details."
}

Example 3 - Input: "REST API for user management"
Output:
{
    "status": "success",
    "project_type": "CRUD backend",
    "complexity": "beginner",
    "missing_requirements": ["authentication method (JWT/OAuth)", "API documentation format (OpenAPI/Swagger)", "rate limiting requirements"],
    "recommended_stack": {"backend": ["FastAPI", "Django", "Node.js"], "frontend": [], "database": ["PostgreSQL", "MySQL"], "devops": ["Docker"]},
    "feedback": "User management API is straightforward. Add authentication method and API documentation approach.",
    "reasoning": "CRUD backend is intermediate complexity. Missing auth method and rate limiting details."
}

Now analyze this prompt and return ONLY JSON:"""


def validate_prompt(prompt: str) -> ValidationResponse:
    """Validate a software prompt and return structured analysis"""
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nPrompt to analyze: {prompt}"
        response_text = get_llm_response(full_prompt)
        
        if not response_text:
            logger.warning("Empty response from LLM")
            return error_response("No response from API")
        
        logger.debug(f"Raw LLM response: {response_text[:300]}")
        
        # Extract JSON from response (in case LLM adds extra text)
        try:
            parsed = extract_json(response_text)
        except (ValueError, json.JSONDecodeError):
            logger.error(f"No JSON found in response: {response_text}")
            return error_response("Invalid JSON response from LLM")
        logger.debug(f"Parsed JSON: {parsed}")
        
        # Validate and clean project_type
        valid_project_types = ["web app", "mobile app", "AI system", "automation", "CRUD backend", "SaaS"]
        project_type = parsed.get("project_type", "unknown")
        if project_type not in valid_project_types:
            logger.warning(f"Invalid project_type '{project_type}', defaulting to 'unknown'")
            project_type = "unknown"
        
        # Validate and clean complexity
        valid_complexities = ["beginner", "intermediate", "advanced"]
        complexity = parsed.get("complexity", "beginner")
        if complexity not in valid_complexities:
            logger.warning(f"Invalid complexity '{complexity}', defaulting to 'beginner'")
            complexity = "beginner"
        
        # Extract other fields with defaults
        status = parsed.get("status", "success")
        missing_requirements = parsed.get("missing_requirements", [])
        feedback = parsed.get("feedback", "Analysis complete")
        reasoning = parsed.get("reasoning", "")
        
        # Validate missing_requirements is a list
        if not isinstance(missing_requirements, list):
            missing_requirements = [str(missing_requirements)]
        
        # Build tech stack with validation
        tech_stack_data = parsed.get("recommended_stack", {})
        tech_stack = TechStack(
            backend=_validate_list(tech_stack_data.get("backend", [])),
            frontend=_validate_list(tech_stack_data.get("frontend", [])),
            database=_validate_list(tech_stack_data.get("database", [])),
            devops=_validate_list(tech_stack_data.get("devops", []))
        )
        
        # Create response
        response = ValidationResponse(
            status=status,
            project_type=project_type,
            complexity=complexity,
            missing_requirements=missing_requirements,
            recommended_stack=tech_stack,
            feedback=feedback,
            reasoning=reasoning
        )
        
        logger.info(f"Validation successful for project type: {project_type}")
        return response
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return error_response(f"Could not parse LLM response as JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Validation error: {type(e).__name__}: {str(e)}", exc_info=True)
        return error_response(f"Validation failed: {str(e)}")


def _validate_list(value) -> list:
    """Ensure value is a list of strings"""
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def error_response(feedback: str) -> ValidationResponse:
    """Return error response with all required fields"""
    return ValidationResponse(
        status="error",
        project_type="unknown",
        complexity="beginner",
        missing_requirements=[],
        recommended_stack=TechStack(),
        feedback=feedback,
        reasoning="Error occurred during validation"
    )


def validate_interactive(request: InteractiveRequest) -> InteractiveResponse:
    """Interactive validation - ask questions until we have enough info"""
    try:
        # Build conversation context
        conversation_text = "\n".join([f"{msg.role}: {msg.content}" for msg in request.conversation])

        slot_ledger = _build_slot_ledger(request.prompt, request.conversation)
        detected_information = extract_detected_information(request.prompt, request.conversation)
        user_stack = _ledger_to_user_stack(slot_ledger)
        
        if _interactive_validation_complete(slot_ledger, detected_information):
            # Finalize and return validation
            return finalize_validation(request.prompt, request.conversation, user_stack)
        
        # Ask next question
        next_question = determine_next_question(
            request.prompt,
            user_stack,
            conversation_text,
            {**detected_information, "slot_ledger": slot_ledger},
        )
        context_summary = summarize_context(request.prompt, user_stack, detected_information)
        
        return InteractiveResponse(
            status="collecting_info",
            current_question=next_question,
            context=context_summary
        )
        
    except Exception as e:
        logger.error(f"Interactive validation error: {str(e)}")
        return InteractiveResponse(
            status="error",
            current_question="An error occurred. Please try again.",
            context=str(e)
        )


def extract_user_stack(conversation: List[ConversationMessage]) -> UserStack:
    """Extract tech choices from conversation"""
    full_text = "\n".join([msg.content for msg in conversation if msg.role == "user"])
    return _extract_user_stack_from_text(full_text)


def _extract_user_stack_from_text(text: str) -> UserStack:
    stack = UserStack()
    full_text = _normalize_text(text)

    if any(word in full_text for word in ["fastapi", "fast api"]):
        stack.backend = "FastAPI"
    elif "node.js" in full_text or "nodejs" in full_text or "node" in full_text:
        stack.backend = "Node.js"
    elif "express" in full_text:
        stack.backend = "Express"
    elif "django" in full_text:
        stack.backend = "Django"
    elif "spring" in full_text:
        stack.backend = "Spring"
    elif "go" in full_text or "golang" in full_text:
        stack.backend = "Go"
    elif "python" in full_text:
        stack.backend = "Python"

    if "react native" in full_text:
        stack.frontend = "React Native"
    elif "react" in full_text:
        stack.frontend = "React"
    elif "vue" in full_text:
        stack.frontend = "Vue"
    elif "next" in full_text:
        stack.frontend = "Next.js"
    elif "angular" in full_text:
        stack.frontend = "Angular"
    elif "flutter" in full_text:
        stack.frontend = "Flutter"
    elif "svelte" in full_text:
        stack.frontend = "Svelte"
    elif "typescript" in full_text:
        stack.frontend = "TypeScript (likely React/Next)"
    elif "no frontend" in full_text or "none" in full_text:
        stack.frontend = "None"

    if "postgresql" in full_text or "postgres" in full_text:
        stack.database = "PostgreSQL"
    elif "mongodb" in full_text or "mongo" in full_text:
        stack.database = "MongoDB"
    elif "mysql" in full_text:
        stack.database = "MySQL"
    elif "redis" in full_text:
        stack.database = "Redis"
    elif "sqlite" in full_text:
        stack.database = "SQLite"

    if any(word in full_text for word in ["websocket", "websockets", "real-time", "real time", "realtime", "live updates"]):
        stack.realtime = "WebSocket"
    elif "polling" in full_text:
        stack.realtime = "Polling"
    elif "sse" in full_text or "server sent events" in full_text:
        stack.realtime = "SSE"
    elif "no real" in full_text or "no realtime" in full_text:
        stack.realtime = "None"

    if "aws" in full_text:
        stack.deployment = "AWS"
    elif "gcp" in full_text or "google" in full_text:
        stack.deployment = "GCP"
    elif "azure" in full_text:
        stack.deployment = "Azure"
    elif "vercel" in full_text:
        stack.deployment = "Vercel"
    elif "netlify" in full_text:
        stack.deployment = "Netlify"
    elif "docker" in full_text:
        stack.deployment = "Docker"
    elif "kubernetes" in full_text or "k8s" in full_text:
        stack.deployment = "Kubernetes"
    elif "serverless" in full_text:
        stack.deployment = "Serverless"
    elif "self-hosted" in full_text or "self hosted" in full_text:
        stack.deployment = "Self-hosted"

    return stack


def has_enough_info(user_stack: UserStack) -> bool:
    """Check if we have minimum required info: backend + frontend + database for complete project"""
    has_core_stack = (
        user_stack.backend is not None
        and user_stack.frontend is not None
        and user_stack.database is not None
    )
    if not has_core_stack:
        return False

    # Redis is excellent for cache, queues, sessions, and real-time presence,
    # but most web apps still need a durable primary database.
    return user_stack.database != "Redis"


def determine_next_question(prompt: str, user_stack: UserStack, conversation_text: str, detected_information: Optional[Dict[str, Any]] = None) -> str:
    """Determine which question to ask next conversationally - never repeat questions"""

    if detected_information and isinstance(detected_information, dict):
        priority_missing = [item for item in detected_information.get("missing_information", []) if item]
        if "LLM provider or model" in priority_missing:
            return (
                "Which LLM provider or model should we assume for the AI system? "
                "Examples: OpenAI, Anthropic, Hugging Face, or a local model."
            )
        if "memory strategy" in priority_missing:
            return (
                "Do you need persistent memory or retrieval for chat history, or should I assume a stateless AI workflow?"
            )

        slot_ledger = detected_information.get("slot_ledger")
        if isinstance(slot_ledger, dict):
            missing_slots = _ledger_missing_slots(slot_ledger)
            if not missing_slots:
                return "Tell me more about your project so I can help refine the requirements."

            next_slot = missing_slots[0]
            if next_slot == "project_type":
                return "What kind of project is this: web app, mobile app, AI system, automation, CRUD backend, or SaaS?"
            if next_slot == "backend_framework":
                return "What backend framework are you thinking of using? Something like FastAPI, Node.js, Django, Spring, or Go?"
            if next_slot == "frontend_framework":
                return "What frontend framework are you thinking of using? React, Vue, Next.js, Angular, Flutter, or something else?"
            if next_slot == "database":
                return "For the database, would you prefer PostgreSQL, MongoDB, MySQL, Redis, or SQLite?"
            if next_slot == "deployment":
                return "Where are you planning to deploy this? AWS, GCP, Azure, Vercel, Netlify, self-hosted, Docker, or serverless?"
            if next_slot == "realtime":
                return "Do you need real-time features like WebSockets, or is polling sufficient, or no real-time at all?"

    if user_stack.database == "Redis":
        return (
            "Redis is a strong choice for caching, sessions, queues, or real-time presence. "
            "For durable app data, what primary database should we pair with it: PostgreSQL, MongoDB, MySQL, or SQLite?"
        )

    missing_fields = []
    if detected_information and isinstance(detected_information, dict):
        missing_fields = [field for field in detected_information.get("missing_fields", []) if field in FIELD_ORDER]

    if not missing_fields:
        # Fallback to legacy detection if the caller did not provide detected info.
        lower_text = _normalize_text(conversation_text)
        seen = set()
        if any(k in lower_text for k in ["fastapi", "fast api", "node.js", "nodejs", "node", "django", "spring", "go", "express", "flask", "python"]):
            seen.add("backend")
        if any(k in lower_text for k in ["react", "vue", "next", "next.js", "angular", "flutter", "react native", "svelte", "typescript"]):
            seen.add("frontend")
        if any(k in lower_text for k in ["postgresql", "postgres", "mongodb", "mongo", "mysql", "redis", "sqlite"]):
            seen.add("database")
        if any(k in lower_text for k in ["aws", "gcp", "google", "azure", "serverless", "self-hosted", "self hosted", "docker", "vercel", "netlify"]):
            seen.add("deployment")
        if any(k in lower_text for k in ["websocket", "websockets", "real-time", "realtime", "polling", "sse", "server sent events", "live updates"]):
            seen.add("realtime")
        missing_fields = [field for field in FIELD_ORDER if getattr(user_stack, field) is None and field not in seen]

    if not missing_fields:
        return "Tell me more about your project so I can help refine the requirements."

    next_field = missing_fields[0]
    if next_field == "backend":
        return f"What backend framework are you thinking of using for {prompt}? Something like FastAPI, Node.js, Django, Spring, or Go?"
    if next_field == "frontend":
        return "What about the frontend? Are you thinking React, Vue, Next.js, Angular, Flutter, or something else?"
    if next_field == "database":
        return "For the database, would you prefer PostgreSQL, MongoDB, MySQL, Redis, or SQLite?"
    if next_field == "deployment":
        return "Where are you planning to deploy this? AWS, GCP, Azure, Vercel, Netlify, self-hosted, Docker, or serverless?"
    if next_field == "realtime":
        return "Do you need real-time features like WebSockets, or is polling sufficient, or no real-time at all?"

    return "Tell me more about your project so I can help refine the requirements."


def summarize_context(prompt: str, user_stack: UserStack, detected_information: Optional[Dict[str, Any]] = None) -> str:
    """Summarize what we know so far"""
    details = []
    details.append(f"Your idea: {prompt}")

    if detected_information and isinstance(detected_information, dict):
        detected_values = detected_information.get("detected_values", {})
        if detected_values:
            detected_summary = ", ".join(f"{field}: {value}" for field, value in detected_values.items())
            details.append(f"Detected: {detected_summary}")
        assumptions = detected_information.get("assumptions", [])
        if assumptions:
            details.append("Assumptions: " + "; ".join(assumptions))
    
    if user_stack.backend:
        details.append(f"Backend: {user_stack.backend}")
    if user_stack.frontend:
        details.append(f"Frontend: {user_stack.frontend}")
    if user_stack.database:
        details.append(f"Database: {user_stack.database}")
    if user_stack.realtime:
        details.append(f"Real-time: {user_stack.realtime}")
    if user_stack.deployment:
        details.append(f"Deployment: {user_stack.deployment}")
    
    return " | ".join(details)


def _interactive_validation_complete(slot_ledger: Dict[str, Dict[str, Any]], detected_information: Optional[Dict[str, Any]]) -> bool:
    """Finalize only when the prompt-inferred gaps are resolved."""
    if _ledger_missing_slots(slot_ledger):
        return False
    if not isinstance(detected_information, dict):
        return True
    return not detected_information.get("missing_information")


def summarize_detected_information(detected_fields: Dict[str, Dict[str, Any]], missing_fields: List[str]) -> str:
    detected_summary = []
    for field in FIELD_ORDER:
        value = detected_fields.get(field, {}).get("value")
        if value:
            detected_summary.append(f"{field}: {value}")
    parts = []
    if detected_summary:
        parts.append("Detected: " + "; ".join(detected_summary))
    if missing_fields:
        parts.append("Missing: " + ", ".join(missing_fields))
    return " | ".join(parts)


def _merge_user_stacks(*stacks: UserStack) -> UserStack:
    merged = UserStack()
    for stack in stacks:
        if stack.backend and not merged.backend:
            merged.backend = stack.backend
        if stack.frontend and not merged.frontend:
            merged.frontend = stack.frontend
        if stack.database and not merged.database:
            merged.database = stack.database
        if stack.realtime and not merged.realtime:
            merged.realtime = stack.realtime
        if stack.deployment and not merged.deployment:
            merged.deployment = stack.deployment
    return merged


def _user_stack_from_detected_information(detected_information: Dict[str, Any]) -> UserStack:
    detected_values = detected_information.get("detected_values", {}) if isinstance(detected_information, dict) else {}
    return UserStack(
        backend=detected_values.get("backend"),
        frontend=detected_values.get("frontend"),
        database=detected_values.get("database"),
        realtime=detected_values.get("realtime"),
        deployment=detected_values.get("deployment"),
    )


def finalize_validation(prompt: str, conversation: List[ConversationMessage], user_stack: UserStack) -> InteractiveResponse:
    """Generate final validation with user's chosen stack and recommendations"""
    
    # Create prompt for final validation
    stack_desc = f"Backend: {user_stack.backend}, Frontend: {user_stack.frontend}, Database: {user_stack.database}"
    if user_stack.realtime:
        stack_desc += f", Real-time: {user_stack.realtime}"
    if user_stack.deployment:
        stack_desc += f", Deployment: {user_stack.deployment}"
    
    validation_prompt = f"""Analyze this project idea and the user's chosen tech stack. ALWAYS include recommended_stack. Return ONLY JSON:

Project: {prompt}
User's Stack: {stack_desc}

IMPORTANT: You MUST include recommended_stack in your response.

Return JSON with:
{{
    "project_type": "web app|mobile app|AI system|automation|CRUD backend|SaaS",
    "complexity": "beginner|intermediate|advanced",
    "alignment_score": 0-100,
    "missing_requirements": ["list of missing things"],
    "recommended_stack": {{
        "backend": ["3-4 backend options that fit this project"],
        "frontend": ["3-4 frontend options that fit this project"],
        "database": ["3-4 database options that fit this project"],
        "devops": ["3-4 devops/tools that fit this project"]
    }},
    "feedback": "explanation of the stack fit",
    "reasoning": "why this analysis"
}}

CRITICAL: Always include "recommended_stack" with all 4 categories populated."""
    
    try:
        response_text = get_llm_response(validation_prompt)
        
        if not response_text:
            return InteractiveResponse(status="error", current_question="Failed to generate final validation")
        
        try:
            parsed = extract_json(response_text)
        except (ValueError, json.JSONDecodeError):
            return InteractiveResponse(status="error", current_question="Invalid response format")
        logger.debug(f"Parsed final validation: {parsed}")
        
        # Extract recommended stack - ensure it exists
        rec_stack_data = parsed.get("recommended_stack", {})
        if not rec_stack_data:
            logger.warning("No recommended_stack in response, using defaults")
            rec_stack_data = {
                "backend": ["FastAPI", "Node.js", "Django"],
                "frontend": ["React", "Vue", "Angular"],
                "database": ["PostgreSQL", "MongoDB", "MySQL"],
                "devops": ["Docker", "GitHub Actions"]
            }
        
        recommended_stack = TechStack(
            backend=_validate_list(rec_stack_data.get("backend", [])),
            frontend=_validate_list(rec_stack_data.get("frontend", [])),
            database=_validate_list(rec_stack_data.get("database", [])),
            devops=_validate_list(rec_stack_data.get("devops", []))
        )
        
        return InteractiveResponse(
            status="success",
            project_type=parsed.get("project_type", "unknown"),
            complexity=parsed.get("complexity", "beginner"),
            user_stack=user_stack,
            recommended_stack=recommended_stack,
            alignment_score=parsed.get("alignment_score", 0),
            missing_requirements=parsed.get("missing_requirements", []),
            feedback=parsed.get("feedback", ""),
            reasoning=parsed.get("reasoning", "")
        )
        
    except Exception as e:
        logger.error(f"Finalize validation error: {str(e)}")
        return InteractiveResponse(
            status="error",
            current_question=f"Error during finalization: {str(e)}"
        )
