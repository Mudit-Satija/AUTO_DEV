from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from llm_client import DEFAULT_MODEL, CODER_MODEL
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
from backend_planning_agent import plan_backend
import logging

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
    response = validate_prompt(request.prompt)
    logger.info(f"Returning validation response: status={response.status}")
    return response


@app.post("/validate-interactive", response_model=InteractiveResponse)
async def validate_interactive_endpoint(request: InteractiveRequest) -> InteractiveResponse:
    """
    Interactive validation - asks clarifying questions conversationally
    
    Returns either next question or final validation
    """
    logger.info(f"Interactive validation: {request.prompt[:100]}")
    response = validate_interactive(request)
    logger.info(f"Interactive response status: {response.status}")
    return response


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
        from frontend_orchestrator import orchestrate_frontend_planning
        
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


@app.get("/info")
async def model_info():
    """Return model metadata for the frontend dashboard."""
    return {
        "validation_model": DEFAULT_MODEL,
        "backend_model": CODER_MODEL,
        "frontend_model": CODER_MODEL,
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