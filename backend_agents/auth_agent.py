"""Auth Agent — authentication strategy analysis.

Note: Authentication is disabled by default in the new pipeline.
This agent remains for backward compatibility with the old pipeline.
"""

import json
import logging
from llm_client import get_llm_response
from planning_agents.shared.json_utils import extract_json

logger = logging.getLogger(__name__)


def analyze_authentication(validation_output: dict) -> dict:
    return {
        "method": "",
        "storage": "",
        "libraries": [],
        "recommendations": ["Authentication is disabled in the current configuration"],
    }
