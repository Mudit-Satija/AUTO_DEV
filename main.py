from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from schemas import ValidationRequest, ValidationResponse
from validation_agent import validate_prompt
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


@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    logger.debug("Health check requested")
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
