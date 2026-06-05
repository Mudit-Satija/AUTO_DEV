"""Bundle Generator â€” generates multiple files per Qwen call using delimiter format.

Groups a flat file list into bundles (backend, frontend, database, docs),
sends one prompt per bundle, parses delimited responses, and falls back
to single-file generation when a bundle fails validation.
"""

import logging
import re
from typing import Any, Dict, List, Tuple

from llm_client import CODER_MODEL, get_llm_response
from coding_agent.file_generator import generate_file as generate_single_file
from coding_agent.file_writer import write_file
from coding_agent.file_registry import register_file
from coding_agent.prompt_constraints import auth_is_enabled, build_prompt_constraints

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Grouping
# ---------------------------------------------------------------------------

BUNDLE_NAMES = ("backend", "frontend", "database", "docs")


def group_files_by_bundle(file_blueprints: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """Classify a flat list of file blueprints into named bundles.

    Returns a dict with keys "backend", "frontend", "database", "docs".
    Each value is the subset of blueprints that belong to that bundle.
    """
    bundles: Dict[str, List[Dict[str, str]]] = {name: [] for name in BUNDLE_NAMES}

    for bp in file_blueprints:
        bundle = _classify(bp)
        bundles[bundle].append(bp)

    # Remove empty bundles
    return {k: v for k, v in bundles.items() if v}


def _classify(blueprint: dict) -> str:
    path = blueprint.get("path", "")
    ftype = blueprint.get("type", "")
    purpose = blueprint.get("purpose", "")

    # Documentation
    if ftype == "documentation" or path == "README.md":
        return "docs"

    # Database
    if ftype == "database":
        return "database"
    if path.startswith("migrations/") or path.startswith("seeds/"):
        return "database"
    if "database" in purpose.lower() or "migration" in purpose.lower() or "seed" in purpose.lower():
        return "database"
    if "mongo" in purpose.lower():
        return "database"

    # Frontend
    if ftype == "page":
        return "frontend"
    if "frontend" in purpose.lower() or "react" in purpose.lower() or "vue" in purpose.lower():
        return "frontend"
    if path.startswith("src/pages/") or path.startswith("src/views/"):
        return "frontend"
    if path in ("vite.config.js", "index.html", "postcss.config.js", "src/main.jsx", "src/main.js",
                 "src/App.jsx", "src/App.vue", "src/App.css", "src/router/index.js"):
        return "frontend"
    if path == "package.json" and "frontend" in purpose.lower():
        return "frontend"
    if "services/api" in path:
        return "frontend"

    # Backend (catch-all â€” most files land here)
    return "backend"


# ---------------------------------------------------------------------------
# Partitioning
# ---------------------------------------------------------------------------

DEFAULT_MAX_BUNDLE_SIZE = 10


def partition_blueprints(
    blueprints: List[Dict[str, str]],
    max_size: int = DEFAULT_MAX_BUNDLE_SIZE,
) -> List[List[Dict[str, str]]]:
    """Split a list of blueprints into groups of at most *max_size*.

    Blueprints are sorted by path first so that related files (same
    directory) stay together.  Returns a single group when the input
    already fits within *max_size*.
    """
    sorted_bps = sorted(blueprints, key=lambda bp: bp.get("path", ""))

    if len(sorted_bps) <= max_size:
        return [sorted_bps]

    return [sorted_bps[i:i + max_size] for i in range(0, len(sorted_bps), max_size)]


def group_and_partition_files(
    file_blueprints: List[Dict[str, str]],
    max_size: int = DEFAULT_MAX_BUNDLE_SIZE,
) -> Dict[str, List[Dict[str, str]]]:
    """Classify files into bundles and partition large bundles into chunks.

    Bundle names are suffixed with ``_1``, ``_2`` etc. when the original
    bundle exceeds *max_size*.  Small bundles keep their original name.
    """
    bundles = group_files_by_bundle(file_blueprints)
    result: Dict[str, List[Dict[str, str]]] = {}

    for name, bps in sorted(bundles.items()):
        chunks = partition_blueprints(bps, max_size)
        if len(chunks) == 1:
            result[name] = chunks[0]
        else:
            for i, chunk in enumerate(chunks):
                result[f"{name}_{i + 1}"] = chunk

    return result


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------


def build_bundle_prompt(bundle_name: str, file_blueprints: List[Dict[str, str]], project_rules: dict) -> str:
    """Build a single prompt instructing Qwen to generate all files in a bundle."""
    backend_fw = project_rules.get("backend_framework", "Unknown")
    frontend_fw = project_rules.get("frontend_framework", "Unknown")
    database = project_rules.get("database", "Unknown")
    auth_method = project_rules.get("auth_method", "Unknown")

    lines = [
        f"You are a code generation assistant. Generate the following {len(file_blueprints)} files for the {bundle_name} of a project.",
        "",
        "Project context:",
        f"- Backend framework: {backend_fw}",
        f"- Frontend framework: {frontend_fw}",
        f"- Database: {database}",
        f"- Auth method: {auth_method}",
        f"- Required backend modules: {', '.join(str(m) for m in project_rules.get('required_backend_modules', [])) or 'none'}",
        f"- Required frontend pages: {', '.join(str(p) for p in project_rules.get('required_pages', [])) or 'none'}",
        f"- Auth enabled: {'yes' if auth_is_enabled(auth_method) else 'no'}",
        "",
        f"Use this exact delimiter format for each file (no JSON, no markdown, no explanations):",
        "",
        "===FILE: <path>===",
        "<file content here>",
        "===END===",
        "",
        "Files to generate:",
    ]

    for i, bp in enumerate(file_blueprints, 1):
        lines.append(f"{i}. Path: {bp.get('path', 'unknown')}  â€”  Purpose: {bp.get('purpose', '')}")

    lines.extend([
        "",
        "Instructions:",
        "- Write file content with real newlines and real quotes.",
        "- Do NOT escape anything.",
        "- Do NOT wrap in markdown code blocks.",
        "- Do NOT add text before the first ===FILE or after the last ===END.",
        "- Generate ALL listed files â€” do not skip any.",
        "- The code must be complete, functional, and follow best practices.",
        "- Return ONLY the delimiter-formatted content.",
        "- Each file may only import from other files that are EXPLICITLY listed in this prompt. Never import from unlisted paths.",
    ])

    lines.extend(build_prompt_constraints(project_rules, file_blueprints))

    if "frontend" in bundle_name:
        lines.append("- Use Vite environment variables (import.meta.env.VITE_*), not process.env.REACT_APP_*.")
        lines.append("- The api.js service must use axios and import.meta.env.VITE_API_BASE_URL for the base URL.")
        lines.append("- The api.js service must use export default api (default export). All page files must import it with: import api from '../services/api' (no braces, no named import).")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

DELIMITER_PATTERN = re.compile(
    r"===FILE:\s*(.+?)===\s*\n(.*?)\n===END===",
    re.DOTALL,
)


def parse_bundle_response(raw_text: str) -> Dict[str, str]:
    """Parse ===FILE: path=== ... ===END=== blocks into {path: content}."""
    files = {}
    for match in DELIMITER_PATTERN.finditer(raw_text):
        path = match.group(1).strip()
        content = match.group(2)
        files[path] = content
    return files


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_bundle(parsed: Dict[str, str], expected_blueprints: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
    """Check that all expected files are present in the parsed output.

    Returns (is_valid, list_of_missing_paths).
    """
    expected_paths = {bp.get("path") for bp in expected_blueprints}
    present = set(parsed.keys())
    missing = sorted(expected_paths - present)
    return len(missing) == 0, missing


# ---------------------------------------------------------------------------
# Generation with fallback
# ---------------------------------------------------------------------------


def generate_bundle(
    bundle_name: str,
    file_blueprints: List[Dict[str, str]],
    project_rules: dict,
) -> Dict[str, str]:
    """Generate all files in a bundle via a single Qwen call.

    Returns {path: content} for successfully parsed files.
    May return fewer files than requested if parse misses some.
    """
    prompt = build_bundle_prompt(bundle_name, file_blueprints, project_rules)
    logger.info(
        "Bundle [%s] prompt: %d chars, %d files",
        bundle_name,
        len(prompt),
        len(file_blueprints),
    )

    raw = get_llm_response(prompt, model=CODER_MODEL)
    parsed = parse_bundle_response(raw)

    logger.info(
        "Bundle [%s] response: %d chars, %d files parsed of %d expected",
        bundle_name,
        len(raw),
        len(parsed),
        len(file_blueprints),
    )

    return parsed


def generate_bundle_with_fallback(
    bundle_name: str,
    file_blueprints: List[Dict[str, str]],
    project_rules: dict,
    output_dir: str,
    registry: dict,
) -> List[dict]:
    """Try bundle generation; fall back to per-file for any missing files.

    Args:
        bundle_name: One of "backend", "frontend", "database", "docs".
        file_blueprints: List of file blueprints for this bundle.
        project_rules: Rules dict from rules_engine.
        output_dir: Root directory for generated files.
        registry: In-memory registry dict (mutated in place).

    Returns:
        List of metadata dicts from write_file(), one per file.
    """
    written: List[dict] = []

    # Attempt bundle generation
    parsed = generate_bundle(bundle_name, file_blueprints, project_rules)
    is_valid, missing = validate_bundle(parsed, file_blueprints)

    if is_valid:
        logger.info("Bundle [%s] valid â€” all %d files present", bundle_name, len(file_blueprints))
        for bp in file_blueprints:
            path = bp.get("path", "unknown")
            content = parsed.get(path, "")
            metadata = write_file({"path": path, "content": content}, output_dir)
            register_file(registry, bp, metadata)
            written.append(metadata)
        return written

    # Fallback: generate missing files individually
    logger.warning(
        "Bundle [%s] validation failed â€” missing %d files. Falling back to per-file generation.",
        bundle_name,
        len(missing),
    )
    for bp in file_blueprints:
        path = bp.get("path", "unknown")
        if path in parsed:
            content = parsed[path]
            logger.info("Bundle [%s] using bundled content for %s", bundle_name, path)
        else:
            logger.info("Bundle [%s] generating individually: %s", bundle_name, path)
            result = generate_single_file(bp, project_rules)
            content = result.get("content", "")
        metadata = write_file({"path": path, "content": content}, output_dir)
        register_file(registry, bp, metadata)
        written.append(metadata)

    return written



