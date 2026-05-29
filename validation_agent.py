from llm_client import get_llm_response
from schemas import ValidationResponse, TechStack, InteractiveRequest, InteractiveResponse, ConversationMessage, UserStack
import json
import logging
from typing import List

logger = logging.getLogger(__name__)

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
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            logger.error(f"No JSON found in response: {response_text}")
            return error_response("Invalid JSON response from LLM")
        
        json_str = response_text[start:end]
        parsed = json.loads(json_str)
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
        
        # Check if we have enough info to finalize
        user_stack = extract_user_stack(request.conversation)
        
        if has_enough_info(user_stack):
            # Finalize and return validation
            return finalize_validation(request.prompt, request.conversation, user_stack)
        
        # Ask next question
        next_question = determine_next_question(request.prompt, user_stack, conversation_text)
        context_summary = summarize_context(request.prompt, user_stack)
        
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
    stack = UserStack()
    
    full_text = "\n".join([msg.content.lower() for msg in conversation if msg.role == "user"])
    
    # Extract backend
    if any(word in full_text for word in ["fastapi", "fast api"]):
        stack.backend = "FastAPI"
    elif "node.js" in full_text or "nodejs" in full_text or "node" in full_text:
        stack.backend = "Node.js"
    elif "django" in full_text:
        stack.backend = "Django"
    elif "spring" in full_text:
        stack.backend = "Spring"
    elif "go" in full_text:
        stack.backend = "Go"
    
    # Extract frontend
    if "react" in full_text:
        stack.frontend = "React"
    elif "vue" in full_text:
        stack.frontend = "Vue"
    elif "next" in full_text:
        stack.frontend = "Next.js"
    elif "flutter" in full_text:
        stack.frontend = "Flutter"
    elif "no frontend" in full_text or "none" in full_text:
        stack.frontend = "None"
    
    # Extract database
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
    
    # Extract real-time
    if "websocket" in full_text:
        stack.realtime = "WebSocket"
    elif "polling" in full_text:
        stack.realtime = "Polling"
    elif "no real" in full_text or "no realtime" in full_text:
        stack.realtime = "None"
    
    # Extract deployment
    if "aws" in full_text:
        stack.deployment = "AWS"
    elif "gcp" in full_text or "google" in full_text:
        stack.deployment = "GCP"
    elif "azure" in full_text:
        stack.deployment = "Azure"
    elif "self-hosted" in full_text or "self hosted" in full_text:
        stack.deployment = "Self-hosted"
    elif "serverless" in full_text:
        stack.deployment = "Serverless"
    
    return stack


def has_enough_info(user_stack: UserStack) -> bool:
    """Check if we have minimum required info: backend + frontend + database for complete project"""
    return user_stack.backend is not None and user_stack.frontend is not None and user_stack.database is not None


def determine_next_question(prompt: str, user_stack: UserStack, conversation_text: str) -> str:
    """Determine which question to ask next conversationally - never repeat questions"""
    
    # Check what questions have already been asked (look for characteristic keywords)
    asked_questions = set()
    lower_text = conversation_text.lower()
    
    # Detect if backend question was already asked
    if "backend" in lower_text and "framework" in lower_text:
        asked_questions.add("backend")
    
    # Detect if frontend question was already asked
    if "frontend" in lower_text and ("react" in lower_text or "vue" in lower_text or "angular" in lower_text):
        asked_questions.add("frontend")
    
    # Detect if database question was already asked
    if "database" in lower_text and ("postgresql" in lower_text or "mongodb" in lower_text or "mysql" in lower_text):
        asked_questions.add("database")
    
    # Detect if real-time question was already asked
    if "websocket" in lower_text or ("real" in lower_text and "time" in lower_text):
        asked_questions.add("realtime")
    
    # Detect if deployment question was already asked
    if ("deploy" in lower_text or "serverless" in lower_text) and ("aws" in lower_text or "gcp" in lower_text or "azure" in lower_text):
        asked_questions.add("deployment")
    
    # Ask for backend if missing and not already asked
    if not user_stack.backend and "backend" not in asked_questions:
        return f"I'd like to help you flesh out your idea: {prompt}. What backend framework are you thinking of using? Something like FastAPI, Node.js, Django, Spring, or Go?"
    
    # Ask for frontend if missing and not already asked (needed for complete project)
    if not user_stack.frontend and "frontend" not in asked_questions:
        return f"What about the frontend? Are you thinking React, Vue, Next.js, Angular, Flutter, or something else?"
    
    # Ask for database if missing and not already asked
    if not user_stack.database and "database" not in asked_questions:
        return f"For the database, would you prefer PostgreSQL, MongoDB, MySQL, Redis, or SQLite?"
    
    # Ask for real-time if missing and not already asked (optional but helpful)
    if not user_stack.realtime and "realtime" not in asked_questions:
        return f"Do you need real-time features like WebSockets, or is polling sufficient, or no real-time at all?"
    
    # Ask for deployment if missing and not already asked
    if not user_stack.deployment and "deployment" not in asked_questions:
        return f"Where are you planning to deploy this? AWS, GCP, Azure, self-hosted, or serverless?"
    
    return "Tell me more about your project so I can help refine the requirements."


def summarize_context(prompt: str, user_stack: UserStack) -> str:
    """Summarize what we know so far"""
    details = []
    details.append(f"Your idea: {prompt}")
    
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
        
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start == -1 or end == 0:
            return InteractiveResponse(status="error", current_question="Invalid response format")
        
        parsed = json.loads(response_text[start:end])
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