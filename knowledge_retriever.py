"""Knowledge Retriever — selects relevant knowledge files based on SRS content.

Maps SRS entities, pages, flows, and tech stack to knowledge files:
- architecture/: tech-stack-specific best practices
- ui/: frontend-framework-specific component libraries
- patterns/: domain-specific patterns for entities/pages/flows

Knowledge is now categorized by target bundle type for isolation.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

_KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

# Architecture knowledge mapped by tech stack AND target bundle
_STACK_TO_ARCHITECTURE = {
    # Frontend architecture
    "react": {"file": "bulletproof_react.md", "bundle": "frontend"},
    "next": {"file": "bulletproof_react.md", "bundle": "frontend"},
    "vue": None,
    "angular": None,
    # Backend architecture
    "express": {"file": "node_best_practices.md", "bundle": "backend"},
    "node": {"file": "node_best_practices.md", "bundle": "backend"},
    "fastapi": {"file": "fastapi_best_practices.md", "bundle": "backend"},
    "python": {"file": "fastapi_best_practices.md", "bundle": "backend"},
    "django": None,
    "spring": None,
    "java": None,
    "refine": {"file": "refine.md", "bundle": "frontend"},
}

# UI knowledge - ONLY injected when explicitly requested, not by framework alone
# Maps explicit UI library names to files
_UI_LIBRARY_TO_FILE = {
    "shadcn": "shadcn_ui.md",
    "shadcn/ui": "shadcn_ui.md",
    "tremor": "tremor.md",
    "aceternity": "aceternity_ui.md",
    "origin": "origin_ui.md",
    "magic": "magic_ui.md",
}

# Framework defaults - NO automatic UI library injection
# React alone does NOT trigger shadcn_ui.md
_STACK_TO_UI = {
    "react": None,
    "next": None,
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

# Pattern to bundle mapping
_PATTERN_TO_BUNDLE = {
    "crm.md": "backend",
    "blog.md": "frontend",
    "ecommerce.md": "fullstack",
    "inventory.md": "backend",
    "analytics.md": "frontend",
    "dashboard.md": "frontend",
    "crud.md": "fullstack",
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


def _detect_ui_libraries(srs: dict) -> List[str]:
    """Detect explicitly requested UI libraries from SRS."""
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

    detected = []
    for lib_name in _UI_LIBRARY_TO_FILE.keys():
        if lib_name in text:
            detected.append(lib_name)
    return detected


def retrieve_knowledge(srs: dict) -> dict:
    """Retrieve relevant knowledge files for a given SRS, categorized by bundle.

    Args:
        srs: SRS dict with keys: project_name, project_description, complexity,
             pages, flow, entities, roles, tech_stack, requirements.

    Returns:
        Dict with keys: frontend, backend, database, docs, each containing
        knowledge file content as a list of {file, content, bundle} dicts.
    """
    tech_stack = srs.get("tech_stack", {})
    if not isinstance(tech_stack, dict):
        tech_stack = {}

    backend = (tech_stack.get("backend") or "").lower()
    frontend = (tech_stack.get("frontend") or "").lower()
    is_frontend_only = backend in ("", "none", "frontend only")

    srs_entities = srs.get("entities", []) or []
    srs_pages = srs.get("pages", []) or []

    result = {
        "frontend": [],
        "backend": [],
        "database": [],
        "docs": [],
    }

    # Architecture knowledge — select by tech stack and assign to correct bundle
    for stack_key, arch_info in _STACK_TO_ARCHITECTURE.items():
        if not arch_info:
            continue
        arch_file = arch_info["file"]
        target_bundle = arch_info["bundle"]
        
        # Skip full-stack-oriented architecture files for frontend-only projects
        if is_frontend_only and arch_file == "bulletproof_react.md":
            logger.info("Skipping %s for frontend-only project (full-stack oriented)", arch_file)
            continue
        
        # Check if this stack key matches backend or frontend
        matches_backend = stack_key in backend
        matches_frontend = stack_key in frontend
        
        if (target_bundle == "backend" and matches_backend) or (target_bundle == "frontend" and matches_frontend):
            content = _load_knowledge_file(f"architecture/{arch_file}")
            if content:
                result[target_bundle].append({"file": arch_file, "content": content, "bundle": target_bundle})
                logger.info("Retrieved architecture knowledge for %s: %s", target_bundle, arch_file)

    # UI knowledge — ONLY when explicitly requested in SRS
    ui_libraries = _detect_ui_libraries(srs)
    for lib_name in ui_libraries:
        ui_file = _UI_LIBRARY_TO_FILE.get(lib_name)
        if ui_file:
            content = _load_knowledge_file(f"ui/{ui_file}")
            if content:
                result["frontend"].append({"file": ui_file, "content": content, "bundle": "frontend", "ui_library": lib_name})
                logger.info("Retrieved UI knowledge (explicit): %s", ui_file)

    # Pattern knowledge — score and select by domain match, assign to bundle
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

    for score, pattern_file in scored_patterns:
        if score > 0.15:
            content = _load_knowledge_file(f"patterns/{pattern_file}")
            if content:
                target_bundle = _PATTERN_TO_BUNDLE.get(pattern_file, "frontend")
                result[target_bundle].append({"file": pattern_file, "content": content, "bundle": target_bundle, "score": round(score, 3)})
                logger.info("Retrieved pattern knowledge for %s: %s (score=%.3f)", target_bundle, pattern_file, score)
        else:
            break

    # Fallback: if no patterns matched, add crud.md to both frontend and backend
    # Skip for frontend-only projects — crud.md describes REST API endpoints that contradict localStorage patterns
    if not is_frontend_only and not any(result[b] for b in ["frontend", "backend"] if any(e.get("file") == "crud.md" for e in result[b])):
        content = _load_knowledge_file("patterns/crud.md")
        if content:
            for bundle in ["frontend", "backend"]:
                result[bundle].append({"file": "crud.md", "content": content, "bundle": bundle, "score": 0.0})
            logger.info("Fallback to generic pattern: crud.md")

    return result
