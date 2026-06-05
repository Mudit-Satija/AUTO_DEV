"""Dependency Graph - validates blueprint dependencies before and after generation."""

import re
from pathlib import Path
from typing import Dict, List, Set


_RESOLVABLE_EXTS = {".js", ".jsx", ".ts", ".tsx", ".py", ".vue"}


class DependencyGraph:
    """Stores and validates dependency edges between file blueprints."""

    def __init__(self, blueprints: List[dict]):
        self.blueprints = {bp["path"]: bp for bp in blueprints}

    def get_all_paths(self) -> Set[str]:
        return set(self.blueprints.keys())

    def get_dependencies(self, path: str) -> List[str]:
        bp = self.blueprints.get(path, {})
        return bp.get("depends_on", [])

    def get_provided(self, path: str) -> List[str]:
        bp = self.blueprints.get(path, {})
        return bp.get("provides", [])


def validate_graph(build_plan: dict) -> List[str]:
    """Validate that all blueprint dependencies exist in the build plan."""
    blueprints = build_plan.get("files", [])
    graph = DependencyGraph(blueprints)
    all_paths = graph.get_all_paths()
    errors: List[str] = []

    for bp in blueprints:
        path = bp["path"]
        for dep in bp.get("depends_on", []):
            if dep not in all_paths:
                errors.append(
                    f"Missing Blueprint:\n"
                    f"    {dep}\n"
                    f"\n"
                    f"Required By:\n"
                    f"    {path}\n"
                )

    return errors


def _extract_local_imports(content: str) -> List[str]:
    """Extract raw local import paths from CommonJS and ES module syntax."""
    imports: List[str] = []
    imports.extend(re.findall(r"""require\(['"](\.?\.?/[^'"]+)['"]\)""", content))
    imports.extend(re.findall(r"""from\s+['"](\.?\.?/[^'"]+)['"]""", content))
    return imports


def _resolve_local_import_target(
    import_path: str,
    current_file: str,
    generated_paths: Set[str],
) -> tuple[str | None, bool]:
    """Resolve a local import to a project path and whether it exists."""
    if not import_path.startswith("."):
        return None, True

    parts = current_file.replace("\\", "/").split("/")
    dir_parts = parts[:-1]

    for part in import_path.replace("\\", "/").split("/"):
        if part == "." or not part:
            continue
        if part == "..":
            if dir_parts:
                dir_parts.pop()
        else:
            dir_parts.append(part)

    base = "/".join(dir_parts)

    if base in generated_paths:
        return base, True

    for ext in _RESOLVABLE_EXTS:
        candidate = f"{base}{ext}"
        if candidate in generated_paths:
            return candidate, True

    for ext in _RESOLVABLE_EXTS:
        candidate = f"{base}/index{ext}"
        if candidate in generated_paths:
            return candidate, True

    return base, False


def _resolve_local_import(
    import_path: str,
    current_file: str,
    generated_paths: Set[str],
) -> str | None:
    """Backward-compatible helper returning only missing import targets."""
    resolved, exists = _resolve_local_import_target(import_path, current_file, generated_paths)
    if exists:
        return None
    return resolved


def validate_imports(build_plan: dict, output_dir: str) -> List[str]:
    """Validate local imports exist and are declared by each file blueprint.

    A generated file may import only files in its own ``depends_on`` list.
    This prevents accidental references to generated-but-unrequested modules.
    """
    generated_paths = {bp["path"] for bp in build_plan.get("files", [])}
    errors: List[str] = []

    for bp in build_plan.get("files", []):
        filepath = Path(output_dir) / bp["path"]
        if not filepath.exists():
            continue

        content = filepath.read_text(encoding="utf-8", errors="replace")
        raw_imports = _extract_local_imports(content)
        allowed_deps = set(bp.get("depends_on", []))

        for raw_imp in raw_imports:
            resolved, exists = _resolve_local_import_target(raw_imp, bp["path"], generated_paths)
            if not exists:
                errors.append(
                    f"Import Validation Failed\n"
                    f"\n"
                    f"    {bp['path']}\n"
                    f"\n"
                    f"references\n"
                    f"\n"
                    f"    {resolved}\n"
                    f"\n"
                    f"which was not generated.\n"
                )
            elif allowed_deps and resolved not in allowed_deps:
                errors.append(
                    f"Import Validation Failed\n"
                    f"\n"
                    f"    {bp['path']}\n"
                    f"\n"
                    f"imports\n"
                    f"\n"
                    f"    {resolved}\n"
                    f"\n"
                    f"which is not declared in its build-plan depends_on list.\n"
                )

    return errors
