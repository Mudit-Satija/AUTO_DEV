"""Robust JSON extraction from LLM responses.

Handles:
- Plain JSON objects `{...}` and arrays `[...]`
- Markdown-fenced ```json ... ``` blocks
- Extra text before/after the JSON
"""

import json
import re
import logging

logger = logging.getLogger(__name__)


def extract_json(text: str):
    """Extract and parse JSON from LLM response text.

    Tries, in order:
    1. Content inside ```json  or ```  fences
    2. Top-level { ... } or [ ... ] via brace/bracket matching

    Args:
        text: Raw LLM response string

    Returns:
        Parsed dict or list

    Raises:
        ValueError: If input is not a string or no JSON can be extracted
        json.JSONDecodeError: If extracted content is not valid JSON
    """
    if not isinstance(text, str):
        raise ValueError(f"Expected string, got {type(text).__name__}")

    # Strategy 1: extract from markdown fence ```json ... ``` or ``` ... ```
    match = re.search(r'```(?:json)?\s*(.*?)```', text, re.DOTALL | re.IGNORECASE)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            logger.debug("Fenced block is not valid JSON, falling through")

    brace_start = text.find('{')
    bracket_start = text.find('[')

    # Prefer whichever structural element appears first
    if brace_start != -1 and (bracket_start == -1 or brace_start < bracket_start):
        # { appears before [ (or [ absent)
        brace_end = text.rfind('}')
        if brace_end != -1 and brace_end > brace_start:
            return json.loads(text[brace_start:brace_end + 1])

    if bracket_start != -1:
        bracket_end = text.rfind(']')
        if bracket_end != -1 and bracket_end > bracket_start:
            return json.loads(text[bracket_start:bracket_end + 1])

    # Fallback: try the other structural element
    if brace_start != -1:
        brace_end = text.rfind('}')
        if brace_end != -1 and brace_end > brace_start:
            return json.loads(text[brace_start:brace_end + 1])

    raise ValueError("No JSON object or array found in response")
