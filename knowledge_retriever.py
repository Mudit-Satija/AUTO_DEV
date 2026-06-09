"""Knowledge Retriever — selects relevant knowledge files based on SRS content.

Maps SRS entities, pages, flows, and tech stack to knowledge files:
- architecture/: tech-stack-specific best practices
- ui/: frontend-framework-specific component libraries
- patterns/: domain-specific patterns for entities/pages/flows
"""

import logging
import re
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

_STACK_TO_ARCHITECTURE = {
    "react": "bulletproof_react.md",
    "next": "bulletproof_react.md",
    "vue": None,
    "angular": None,
    "express": "node_best_practices.md",
    "node": "node_best_practices.md",
    "fastapi": "fastapi_best_practices.md",
    "python": "fastapi_best_practices.md",
    "django": None,
    "spring": None,
    "java": None,
    "refine": "refine.md",
}

_STACK_TO_UI = {
    "react": "shadcn_ui.md",
    "next": "shadcn_ui.md",
    "vue": None,
    "angular": None,
}

_PATTERN_KEYWORDS = {
    "crm.md": ["contact", "company", "deal", "pipeline", "lead", "account", "opportunity"],
    "blog.md": ["post", "article", "blog", "author", "category", "tag", "comment", "newsletter"],
    "ecommerce.md": ["product", "cart", "order", "checkout", "payment", "catalog", "shop", "store"],
    "inventory.md": ["inventory", "stock", "sku", "warehouse", "supplier", "batch", "lot"],
    "analytics.md": ["analytics", "metric", "dashboard", "report", "chart", "kpi", "cohort", "funnel"],
    "dashboard.md": ["dashboard", "kpi", "metric", "chart", "widget"],
    "crud.md": [],
}


def _load_knowledge_file(relative_path: str) -> str:
    """Load a knowledge file from the knowledge directory."""
    filepath = _KNOWLEDGE_DIR / relative_path
    if not filepath.exists():
        return ""
    return filepath.read_text(encoding="utf-8", errors="replace")


def _match_domain_keywords(srs: dict, pattern_file: str, keywords: List[str]) -> float:
    """Score how well an SRS matches a domain pattern based on keyword overlap."""
    text = (
        srs.get("project_name", "")
        + " "
        + srs.get("project_description", "")
        + " "
        + " ".join(p.get("name", "") for p in srs.get("pages", []))
        + " "
        + " ".join(e.get("name", "") for e in srs.get("entities", []))
        + " "
        + " ".join(f.get("name", "") for f in srs.get("flow", []))
    ).lower()

    if not keywords:
        return 0.0

    matches = sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", text))
    return matches / len(keywords)


def _match_entity_overlap(srs_entities: List[Dict], pattern_file: str, keywords: List[str]) -> float:
    """Score entity name overlap between SRS and domain pattern."""
    srs_entity_names = {e.get("name", "").lower() for e in srs_entities}
    if not srs_entity_names:
        return 0.0

    overlap = len(srs_entity_names & set(keywords))
    return overlap / len(srs_entity_names)


def retrieve_knowledge(srs: dict) -> dict:
    """Retrieve relevant knowledge files for a given SRS.

    Args:
        srs: SRS dict with keys: project_name, project_description, complexity,
             pages, flow, entities, roles, tech_stack, requirements.

    Returns:
        Dict with keys: architecture, ui, patterns, each containing
        knowledge file content as a list of {file, content} dicts.
    """
    tech_stack = srs.get("tech_stack", {})
    if not isinstance(tech_stack, dict):
        tech_stack = {}

    backend = (tech_stack.get("backend") or "").lower()
    frontend = (tech_stack.get("frontend") or "").lower()

    srs_entities = srs.get("entities", []) or []
    srs_pages = srs.get("pages", []) or []

    result = {
        "architecture": [],
        "ui": [],
        "patterns": [],
    }

    # Architecture knowledge — select by backend/frontend
    arch_hits = set()
    for stack_key, arch_file in _STACK_TO_ARCHITECTURE.items():
        if arch_file and stack_key in backend:
            arch_hits.add(arch_file)
    for stack_key, arch_file in _STACK_TO_ARCHITECTURE.items():
        if arch_file and stack_key in frontend:
            arch_hits.add(arch_file)
    for arch_file in sorted(arch_hits):
        content = _load_knowledge_file(f"architecture/{arch_file}")
        if content:
            result["architecture"].append({"file": arch_file, "content": content})
            logger.info("Retrieved architecture knowledge: %s", arch_file)

    # UI knowledge — select by frontend framework
    ui_hits = set()
    for stack_key, ui_file in _STACK_TO_UI.items():
        if ui_file and stack_key in frontend:
            ui_hits.add(ui_file)
    for ui_file in sorted(ui_hits):
        content = _load_knowledge_file(f"ui/{ui_file}")
        if content:
            result["ui"].append({"file": ui_file, "content": content})
            logger.info("Retrieved UI knowledge: %s", ui_file)

    # Pattern knowledge — score and select by domain match
    scored_patterns = []
    for pattern_file, keywords in _PATTERN_KEYWORDS.items():
        if not keywords:
            continue
        kw_score = _match_domain_keywords(srs, pattern_file, keywords)
        entity_score = _match_entity_overlap(srs_entities, pattern_file, keywords)
        combined = (kw_score * 0.6) + (entity_score * 0.4)
        if combined > 0:
            scored_patterns.append((combined, pattern_file))

    scored_patterns.sort(reverse=True, key=lambda x: x[0])

    # Select top patterns with score > 0.15
    for score, pattern_file in scored_patterns:
        if score > 0.15:
            content = _load_knowledge_file(f"patterns/{pattern_file}")
            if content:
                result["patterns"].append({"file": pattern_file, "content": content, "score": round(score, 3)})
                logger.info("Retrieved pattern knowledge: %s (score=%.3f)", pattern_file, score)
        else:
            break

    # If no pattern matched, try crud.md as generic fallback
    if not result["patterns"]:
        content = _load_knowledge_file("patterns/crud.md")
        if content:
            result["patterns"].append({"file": "crud.md", "content": content, "score": 0.0})
            logger.info("Fallback to generic pattern: crud.md")

    return result
