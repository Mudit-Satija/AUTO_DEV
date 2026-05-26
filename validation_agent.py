from llm_client import get_llm_response
from schemas import ValidationResponse
import json
import logging

logger = logging.getLogger(__name__)


def validate_prompt(prompt: str) -> ValidationResponse:
    """
    Validate a prompt using NVIDIA API
    
    Returns structured validation response with missing requirements
    """
    logger.info(f"Starting validation for prompt: {prompt[:100]}...")
    
    # Create validation instruction for the LLM
    validation_instruction = f"""Analyze this prompt and identify any missing requirements or issues.

Prompt to validate:
"{prompt}"

Respond ONLY with valid JSON in this exact format (no markdown, no extra text):
{{
    "status": "success",
    "missing_requirements": ["requirement1", "requirement2"],
    "feedback": "Brief feedback on the prompt",
    "reasoning": "Why these requirements are missing"
}}

Be concise. If no issues found, use empty list for missing_requirements."""
    
    try:
        logger.debug("Calling LLM API...")
        response_text = get_llm_response(validation_instruction)
        
        if not response_text:
            logger.warning("API returned empty response")
            return ValidationResponse(
                status="error",
                missing_requirements=[],
                feedback="No response from API"
            )
        
        logger.debug(f"API Response (first 200 chars): {response_text[:200]}")
        
        # Parse JSON response - handle various formats
        response_text = response_text.strip()
        
        # Find JSON object in response (handles markdown code blocks, etc)
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            logger.error(f"No JSON object found in response: {response_text}")
            return ValidationResponse(
                status="error",
                missing_requirements=[],
                feedback="Could not parse API response as JSON"
            )
        
        json_str = response_text[start_idx:end_idx]
        logger.debug(f"Extracted JSON: {json_str}")
        
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}, JSON string: {json_str}")
            return ValidationResponse(
                status="error",
                missing_requirements=[],
                feedback=f"Invalid JSON in API response: {str(e)}"
            )
        
        # Validate required fields
        if not isinstance(parsed.get("missing_requirements"), list):
            logger.warning("missing_requirements is not a list, converting...")
            parsed["missing_requirements"] = []
        
        response = ValidationResponse(
            status=parsed.get("status", "success"),
            missing_requirements=parsed.get("missing_requirements", []),
            feedback=parsed.get("feedback"),
            reasoning=parsed.get("reasoning")
        )
        
        logger.info(f"Validation complete: {len(response.missing_requirements)} issues found")
        return response
        
    except Exception as e:
        logger.error(f"Validation error: {type(e).__name__}: {str(e)}", exc_info=True)
        return ValidationResponse(
            status="error",
            missing_requirements=[],
            feedback=f"Validation failed: {str(e)}"
        )
