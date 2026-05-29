from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class TechStack(BaseModel):
    """Recommended technology stack breakdown"""
    backend: List[str] = Field(default_factory=list, description="Backend technologies")
    frontend: List[str] = Field(default_factory=list, description="Frontend technologies")
    database: List[str] = Field(default_factory=list, description="Database options")
    devops: List[str] = Field(default_factory=list, description="DevOps/Infrastructure tools")


class ValidationRequest(BaseModel):
    """Input for validation endpoint"""
    prompt: str = Field(description="The software project description to analyze")


class ValidationResponse(BaseModel):
    """Structured validation response with deep project analysis"""
    status: str = Field(description="success or error")
    project_type: str = Field(default="unknown", description="Detected project type (web app, mobile app, AI system, automation, CRUD backend, SaaS)")
    complexity: str = Field(default="beginner", description="Project complexity: beginner, intermediate, or advanced")
    missing_requirements: List[str] = Field(default_factory=list, description="List of missing or unclear requirements")
    recommended_stack: TechStack = Field(default_factory=TechStack, description="Recommended technology stack")
    feedback: str = Field(description="Human-readable explanation of the analysis")
    reasoning: str = Field(description="Explanation of how we arrived at these conclusions")


class ConversationMessage(BaseModel):
    """Single message in conversation"""
    role: str = Field(description="'user' or 'assistant'")
    content: str = Field(description="Message text")


class InteractiveRequest(BaseModel):
    """Interactive validation request"""
    prompt: str = Field(description="Initial project idea")
    conversation: List[ConversationMessage] = Field(default_factory=list, description="Previous conversation messages")


class UserStack(BaseModel):
    """User-selected technology stack"""
    backend: Optional[str] = None
    frontend: Optional[str] = None
    database: Optional[str] = None
    realtime: Optional[str] = None
    deployment: Optional[str] = None


class InteractiveResponse(BaseModel):
    """Interactive validation response"""
    status: str = Field(description="'collecting_info' or 'success'")
    current_question: Optional[str] = Field(None, description="Question to ask user (if collecting_info)")
    context: Optional[str] = Field(None, description="Summary of conversation so far")
    
    # Fields below only for final validation
    project_type: Optional[str] = None
    complexity: Optional[str] = None
    user_stack: Optional[UserStack] = None
    recommended_stack: Optional[TechStack] = None
    missing_requirements: Optional[List[str]] = None
    alignment_score: Optional[int] = None
    feedback: Optional[str] = None
    reasoning: Optional[str] = None
