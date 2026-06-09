"""Endpoint Agent — suggests REST endpoints based on SRS entities and flow.

No hardcoded auth endpoints (register, login).
No hardcoded domain endpoints (workspaces, projects, tasks).
Driven entirely by SRS content.
"""

import json
import logging
from llm_client import get_llm_response
from planning_agents.shared.json_utils import extract_json
from planning_agents.shared.rules import RuleManager
from planning_agents.shared.domain_intelligence import domain_context_summary

logger = logging.getLogger(__name__)

ENDPOINT_PROMPT = """You are an API design expert. Suggest REST endpoints for this project.

RULES:
- Each endpoint must have: method, path, description
- Return ONLY valid JSON array

PROJECT TYPE: {project_type}
DOMAIN CONTEXT: {domain_context}

{rules}

Return a JSON array of endpoint objects with keys: method, path, description.
No other text."""


def analyze_endpoints(validation_output: dict) -> dict:
    try:
        if not isinstance(validation_output, dict):
            validation_output = {}

        project_type = validation_output.get("project_type", "web app")
        domain_context = validation_output.get("domain_context", {})
        if not isinstance(domain_context, dict):
            domain_context = {}

        rules = RuleManager.from_validation_output(validation_output)

        prompt = ENDPOINT_PROMPT.format(
            project_type=project_type,
            domain_context=domain_context_summary(domain_context),
            rules=rules.prompt_context("endpoints"),
        )

        logger.info("Endpoint Agent: Generating endpoints...")
        response_text = get_llm_response(prompt)

        if not isinstance(response_text, str):
            return {"endpoints": []}

        endpoints = extract_json(response_text)
        if not isinstance(endpoints, list):
            endpoints = []

        logger.info("Endpoint Agent: Generated %d endpoints", len(endpoints))
        return {"endpoints": endpoints}

    except Exception as e:
        logger.error("Endpoint Agent failed: %s", e, exc_info=True)
        return {"endpoints": []}
