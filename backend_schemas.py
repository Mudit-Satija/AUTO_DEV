from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class APIEndpoint(BaseModel):
    """Single API endpoint specification"""
    method: str = Field(description="HTTP method: GET, POST, PUT, DELETE")
    path: str = Field(description="API path (e.g., /api/users)")
    description: str = Field(description="What this endpoint does")
    auth_required: bool = Field(default=False, description="Whether authentication is required")


class AuthenticationStrategy(BaseModel):
    """Authentication approach for the backend"""
    method: str = Field(description="JWT, OAuth, Session-based, etc")
    storage: str = Field(description="Where to store tokens: httpOnly cookies, localStorage, etc")
    refresh_strategy: str = Field(description="How to refresh expired tokens")
    libraries: List[str] = Field(default_factory=list, description="Required libraries")


class DatabaseStrategy(BaseModel):
    """Database configuration strategy"""
    type: str = Field(description="Database type: MongoDB, PostgreSQL, MySQL, etc")
    orm: str = Field(description="ORM to use: Mongoose, SQLAlchemy, Sequelize, etc")
    connection_pool: bool = Field(default=True, description="Use connection pooling")
    migration_tool: str = Field(description="Migration tool: Alembic, Liquibase, N/A, etc")


class FolderStructure(BaseModel):
    """Folder structure recommendation"""
    name: str = Field(description="Folder name (e.g., src/)")
    description: str = Field(description="What goes in this folder")
    children: List[str] = Field(default_factory=list, description="Sub-folders")


class BackendArchitecturePlan(BaseModel):
    """Complete backend architecture plan"""
    status: str = Field(description="success or needs_clarification")
    framework: str = Field(description="Specific framework (Express.js, FastAPI, etc)")
    language: str = Field(description="Programming language")
    api_style: str = Field(default="REST", description="REST, GraphQL, gRPC")
    
    authentication: AuthenticationStrategy = Field(description="Auth strategy")
    database: DatabaseStrategy = Field(description="Database strategy")
    
    suggested_endpoints: List[APIEndpoint] = Field(default_factory=list, description="Recommended API endpoints")
    folder_structure: List[FolderStructure] = Field(default_factory=list, description="Project folder structure")
    
    core_libraries: List[str] = Field(default_factory=list, description="Essential packages")
    optional_libraries: Dict[str, str] = Field(default_factory=dict, description="Nice-to-have packages with descriptions")
    
    design_patterns: List[str] = Field(default_factory=list, description="Recommended patterns: MVC, Service Layer, etc")
    clarification_questions: List[str] = Field(default_factory=list, description="Questions needing clarification")
    reasoning: str = Field(description="Why these recommendations")


class BackendPlanRequest(BaseModel):
    """Request for backend planning"""
    project_idea: Optional[str] = None
    project_type: Optional[str] = None
    user_stack: Optional[Dict] = None
    validation_output: Optional[Dict] = None
    additional_context: Optional[str] = None
