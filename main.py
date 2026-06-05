from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from llm_client import get_llm_response, DEFAULT_MODEL, CODER_MODEL, PLANNER_MODEL
from schemas import ValidationRequest, ValidationResponse, InteractiveRequest, InteractiveResponse
from validation_agent import validate_prompt, validate_interactive
from backend_schemas import (
    BackendPlanRequest, 
    BackendArchitecturePlan,
    AuthenticationStrategy,
    DatabaseStrategy,
    APIEndpoint,
    FolderStructure,
)
from backend_agents.planning_agent import plan_backend
from master_orchestrator import orchestrate_full_architecture
from coding_agent.project_generator import generate_project
from coding_agent.file_generator import generate_file
from coding_agent.file_writer import write_file
from coding_agent.prompt_builder import build_file_prompt
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Validation System",
    description="Minimal validation system using NVIDIA API",
    version="0.1.0"
)

# Enable CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/validate", response_model=ValidationResponse)
async def validate(request: ValidationRequest) -> ValidationResponse:
    """
    Validate a prompt and return missing requirements
    
    Returns structured JSON with validation results
    """
    logger.info(f"Received validation request: {request.prompt[:100]}")
    started = time.perf_counter()
    response = validate_prompt(request.prompt)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    feedback_text = getattr(response, "feedback", "") or ""
    logger.info("[PERF]\nValidation Agent: %d ms\nOutput Size: %d chars\nOutput Words: %d", elapsed_ms, len(feedback_text), len(feedback_text.split()))
    logger.info(f"Returning validation response: status={response.status}")
    return response


@app.post("/validate-interactive", response_model=InteractiveResponse)
async def validate_interactive_endpoint(request: InteractiveRequest) -> InteractiveResponse:
    """
    Interactive validation - asks clarifying questions conversationally
    
    Returns either next question or final validation
    """
    logger.info(f"Interactive validation: {request.prompt[:100]}")
    started = time.perf_counter()
    response = validate_interactive(request)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    output_text = (getattr(response, "current_question", "") or "") + " " + (getattr(response, "feedback", "") or "")
    logger.info("[PERF]\nValidation Agent: %d ms\nOutput Size: %d chars\nOutput Words: %d", elapsed_ms, len(output_text), len(output_text.split()))
    logger.info(f"Interactive response status: {response.status}")
    return response


@app.post("/chat")
async def chat_endpoint(request: dict):
    """General conversational endpoint backed by the DEFAULT_MODEL (Llama 3.1).

    Expects JSON: { "prompt": string, "conversation": [{role, content}], "mode": optional }
    Returns: { "reply": string }
    """
    prompt = request.get("prompt") or ""
    conversation = request.get("conversation", [])
    mode = request.get("mode", "assistant")

    # Build a concise prompt that instructs the model to reply helpfully and empathetically
    system_prefix = (
        "You are an expert AI assistant for software architecture. Reply concisely, empathetically, and "
        "provide clear next steps or suggestions when asked. If the user asks for suggestions, include a brief "
        "recommended stack (backend, frontend, database, devops). Do NOT return code blocks unless explicitly requested."
    )

    # Merge conversation into context for the model
    conv_text = "\n".join([f"{m.get('role')}: {m.get('content')}" for m in conversation])

    full_prompt = f"{system_prefix}\n\nConversation:\n{conv_text}\n\nUser: {prompt}\nAssistant:"

    try:
        reply = get_llm_response(full_prompt, model=DEFAULT_MODEL)
        return {"reply": reply}
    except Exception as e:
        logger.error(f"/chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan-backend", response_model=BackendArchitecturePlan)
async def plan_backend_endpoint(request: BackendPlanRequest) -> BackendArchitecturePlan:
    """
    Generate backend architecture plan from validation output or direct input
    
    Accepts either:
    - validation_output: Complete output from /validate-interactive
    - Direct input: project_idea, project_type, user_stack
    
    Example:
    {
        "project_idea": "Create a todo app",
        "project_type": "web app",
        "user_stack": {
            "backend": "Node.js",
            "database": "MongoDB"
        }
    }
    """
    try:
        # Extract data from validation_output or use direct input
        if request.validation_output:
            validation = request.validation_output
            project_idea = validation.get("feedback", "")
            project_type = validation.get("project_type", "unknown")
            user_stack = validation.get("user_stack", {})
        else:
            project_idea = request.project_idea or "Not specified"
            project_type = request.project_type or "unknown"
            user_stack = request.user_stack or {}
        
        additional_context = request.additional_context or ""
        
        logger.info(f"Planning backend for {project_type} with {user_stack.get('backend', 'unknown')}")
        logger.debug(f"Project idea: {project_idea}")
        logger.debug(f"User stack: {user_stack}")
        
        # Build validation_output dict to pass to plan_backend
        validation_data = {
            "project_type": project_type,
            "user_stack": user_stack,
            "feedback": project_idea
        }
        
        # Get the plan as dictionary from the backend planning agent
        plan_dict = plan_backend(validation_output=validation_data)
        
        # Log what we got back
        logger.debug(f"Plan dict status: {plan_dict.get('status')}")
        logger.debug(f"Plan dict keys: {list(plan_dict.keys())}")
        
        # Convert dictionary to Pydantic model
        try:
            plan = BackendArchitecturePlan(**plan_dict)
            logger.info(f"Backend plan created successfully: framework={plan.framework}, status={plan.status}")
            return plan
            
        except ValueError as ve:
            logger.error(f"Pydantic validation error: {str(ve)}")
            logger.error(f"Plan data that failed validation: {plan_dict}")
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid plan data structure: {str(ve)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /plan-backend: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Backend planning failed: {str(e)}"
        )


@app.post("/plan-frontend")
async def plan_frontend(request: BackendPlanRequest):
    """
    Plan frontend architecture based on validation output.
    
    Runs 6 frontend agents in parallel:
    - layout_agent
    - component_agent
    - styling_agent
    - navigation_agent
    - animation_agent
    - accessibility_agent
    
    Returns merged frontend architecture plan.
    """
    try:
        if request.validation_output:
            validation = request.validation_output
            project_type = validation.get("project_type", request.project_type or "unknown")
            user_stack = validation.get("user_stack", request.user_stack or {})
            project_idea = validation.get("feedback", request.project_idea or "")
            complexity = validation.get("complexity", "intermediate")
            alignment_score = validation.get("alignment_score", 85)
            missing_requirements = validation.get("missing_requirements", [])
        else:
            project_type = request.project_type or "unknown"
            user_stack = request.user_stack or {}
            project_idea = request.project_idea or ""
            complexity = "beginner" if "beginner" in project_idea.lower() else ("advanced" if "advanced" in project_idea.lower() else "intermediate")
            alignment_score = 85
            missing_requirements = []
        
        logger.info(f"Planning frontend for {project_type}")
        logger.debug(f"Project idea: {project_idea}")
        logger.debug(f"User stack: {user_stack}")
        
        # Build validation_output dict to pass to frontend orchestrator
        validation_data = {
            "project_type": project_type,
            "complexity": complexity,
            "user_stack": user_stack,
            "feedback": project_idea,
            "alignment_score": alignment_score,
            "missing_requirements": missing_requirements,
        }
        
        # Import and run frontend orchestrator
        from frontend_agents.orchestrator import orchestrate_frontend_planning
        
        # FastAPI already runs this handler inside an event loop, so await directly.
        frontend_plan = await orchestrate_frontend_planning(validation_data)

        if frontend_plan.get("status") != "success":
            raise HTTPException(
                status_code=500,
                detail=frontend_plan.get("error", "Frontend planning failed"),
            )
        
        logger.info(f"Frontend plan created successfully: framework={frontend_plan.get('frontend_architecture', {}).get('framework', 'N/A')}")
        
        return frontend_plan
        
    except Exception as e:
        logger.error(f"Error in /plan-frontend: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Frontend planning failed: {str(e)}"
        )


@app.post("/plan-full-architecture")
async def plan_full_architecture_endpoint(request: dict) -> dict:
    """Run backend and frontend planning in parallel from a validation payload."""

    validation_output = request.get("validation_output")
    if not isinstance(validation_output, dict):
        raise HTTPException(status_code=400, detail="Missing validation_output")

    request_start = time.perf_counter()
    logger.info(
        "Starting full architecture planning for %s",
        validation_output.get("project_type", "unknown"),
    )

    result = await orchestrate_full_architecture(validation_output)
    elapsed_ms = int((time.perf_counter() - request_start) * 1000)
    logger.info("[PERF]\nTotal Request Time: %d ms", elapsed_ms)
    return result


@app.post("/generate-file")
async def generate_single_file_endpoint(request: dict) -> dict:
    """Generate, log timing for, and persist a single file.

    Input: { "file_blueprint": {...}, "project_rules": {...}, "output_dir": "..." }
    """
    file_blueprint = request.get("file_blueprint")
    project_rules = request.get("project_rules")
    output_dir = request.get("output_dir", "generated_project")

    if not isinstance(file_blueprint, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid file_blueprint")
    if not isinstance(project_rules, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid project_rules")

    # 1. Build prompt and log its size
    prompt = build_file_prompt(file_blueprint, project_rules)
    logger.info("PROMPT length: %d characters", len(prompt))

    # 2. Generate — measure timing
    file_path = file_blueprint.get("path", "unknown")
    logger.info("GENERATE START: %s", file_path)
    gen_start = time.perf_counter()
    generated = generate_file(file_blueprint, project_rules)
    gen_end = time.perf_counter()
    gen_duration = gen_end - gen_start
    logger.info(
        "GENERATE END:   %s  (%.2f s)",
        file_path,
        gen_duration,
    )

    # 3. Write to disk
    metadata = write_file(generated, output_dir)

    logger.info(
        "WRITE:          %s  (%d bytes)",
        metadata.get("path"),
        metadata.get("bytes_written", 0),
    )

    return {
        "path": metadata.get("path"),
        "bytes_written": metadata.get("bytes_written", 0),
        "generation_duration_s": round(gen_duration, 2),
    }


@app.post("/generate-project")
async def generate_project_endpoint(request: dict) -> dict:
    """Generate project files from a build plan and project rules.

    Expects JSON: { "build_plan": {...}, "project_rules": {...}, "output_dir": "..." }
    """
    build_plan = request.get("build_plan")
    project_rules = request.get("project_rules")
    output_dir = request.get("output_dir", "generated_project")

    if not isinstance(build_plan, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid build_plan")
    if not isinstance(project_rules, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid project_rules")

    try:
        result = generate_project(build_plan, project_rules, output_dir)
        logger.info(
            "Project generation complete: %d files written to %s",
            result["files_generated"],
            output_dir,
        )
        return result
    except Exception as e:
        logger.error(f"Project generation failed: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Project generation failed: {str(e)}")


@app.get("/info")
async def model_info():
    """Return model metadata for the frontend dashboard."""
    return {
        "validation_model": DEFAULT_MODEL,
        "backend_model": CODER_MODEL,
        "frontend_model": PLANNER_MODEL,
        "frontend_planning_agents": [
            "layout_agent",
            "component_agent",
            "styling_agent",
            "navigation_agent",
            "animation_agent",
            "accessibility_agent",
        ],
    }


@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
