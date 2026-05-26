from pydantic import BaseModel
from typing import List, Optional


class ValidationRequest(BaseModel):
    """Input for validation endpoint"""
    prompt: str


class ValidationResponse(BaseModel):
    """Output from validation endpoint"""
    status: str  # "success" or "error"
    missing_requirements: List[str]
    feedback: Optional[str] = None
    reasoning: Optional[str] = None
