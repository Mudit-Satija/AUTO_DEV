"""Ecosystem rules for stack-consistent planning.

This module keeps the stack rule names requested by the project while
re-exporting the existing rule manager used by the planning pipeline.
"""

from __future__ import annotations

from .rules import FASTAPI_RULES as FASTAPI
from .rules import NODE_RULES as NODE
from .rules import SPRING_RULES as SPRING_BOOT
from .rules import DATABASE_ALIASES, STACK_ALIASES, STACK_RULES, RuleManager


def get_stack_rules(stack_name: str):
    """Return the canonical rule set for a stack name."""
    normalized = str(stack_name or "").strip().lower()
    if "fastapi" in normalized:
        return FASTAPI
    if "node" in normalized or "express" in normalized or "javascript" in normalized:
        return NODE
    return SPRING_BOOT
