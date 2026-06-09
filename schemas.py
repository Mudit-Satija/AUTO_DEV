from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class SRSRequirement(BaseModel):
    """Single requirement in the SRS with traceability."""
    id: str = Field(description="Unique requirement ID (e.g. REQ-001)")
    description: str = Field(description="What the requirement is")


class SRSEntity(BaseModel):
    """Entity definition from SRS."""
    name: str = Field(description="Entity name (e.g. Invoice, Product)")
    fields: List[str] = Field(default_factory=list, description="Entity fields (e.g. ['number', 'amount'])")
    description: Optional[str] = None


class SRSPage(BaseModel):
    """Page definition from SRS."""
    name: str = Field(description="Page name (e.g. Invoices, Create Invoice)")
    purpose: str = Field(description="What this page does")
    entities: List[str] = Field(default_factory=list, description="Entities involved on this page")


class SRSFlow(BaseModel):
    """Flow definition from SRS."""
    name: str = Field(description="Flow name (e.g. Invoice creation)")
    steps: List[str] = Field(default_factory=list, description="Steps in the flow")
    entities: List[str] = Field(default_factory=list, description="Entities involved")


class TechStack(BaseModel):
    """Technology stack configuration."""
    backend: str = Field(default="", description="Backend framework")
    frontend: str = Field(default="", description="Frontend framework")
    database: str = Field(default="", description="Database")
    deployment: Optional[str] = None


class SRSDocument(BaseModel):
    """Software Requirements Specification — single source of truth."""
    project_name: str = Field(description="Project name")
    project_description: str = Field(description="Project description")
    complexity: str = Field(default="intermediate", description="Project complexity: beginner, intermediate, advanced")
    pages: List[SRSPage] = Field(default_factory=list, description="Pages to generate")
    flow: List[SRSFlow] = Field(default_factory=list, description="User flows")
    entities: List[SRSEntity] = Field(default_factory=list, description="Domain entities")
    roles: List[str] = Field(default_factory=list, description="User roles")
    tech_stack: TechStack = Field(default_factory=TechStack, description="Technology choices")
    requirements: List[SRSRequirement] = Field(default_factory=list, description="Functional requirements")


class ValidationRequest(BaseModel):
    """Input for validation endpoint."""
    prompt: str = Field(description="The software project description to analyze")


class ValidationResponse(BaseModel):
    """Structured validation response with deep project analysis."""
    status: str = Field(description="success or error")
    project_type: str = Field(default="unknown")
    complexity: str = Field(default="beginner")
    missing_requirements: List[str] = Field(default_factory=list)
    recommended_stack: TechStack = Field(default_factory=TechStack)
    feedback: str = Field(description="Human-readable explanation of the analysis")
    reasoning: str = Field(description="Explanation of how we arrived at these conclusions")


class ConversationMessage(BaseModel):
    """Single message in conversation."""
    role: str = Field(description="'user' or 'assistant'")
    content: str = Field(description="Message text")


class InteractiveRequest(BaseModel):
    """Interactive validation request."""
    prompt: str = Field(description="Initial project idea")
    conversation: List[ConversationMessage] = Field(default_factory=list)


class UserStack(BaseModel):
    """User-selected technology stack."""
    backend: Optional[str] = None
    frontend: Optional[str] = None
    database: Optional[str] = None
    realtime: Optional[str] = None
    deployment: Optional[str] = None


class InteractiveResponse(BaseModel):
    """Interactive validation response."""
    status: str = Field(description="'collecting_info' or 'success'")
    current_question: Optional[str] = None
    context: Optional[str] = None
    project_type: Optional[str] = None
    complexity: Optional[str] = None
    user_stack: Optional[UserStack] = None
    recommended_stack: Optional[TechStack] = None
    missing_requirements: Optional[List[str]] = None
    alignment_score: Optional[int] = None
    feedback: Optional[str] = None
    reasoning: Optional[str] = None
