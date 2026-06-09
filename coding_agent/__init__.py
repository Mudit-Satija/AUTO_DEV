"""Coding Agent — SRS-driven project generation pipeline.

Pipeline:
  SRS → Knowledge Retrieval → Build Plan → Code Generation

Every generated file traces back to an SRS requirement.
No hardcoded entities, pages, routes, modules, or flows.
"""

from coding_agent.build_plan import generate_build_plan
from coding_agent.project_generator import generate_project
from coding_agent.rules_engine import build_project_rules
