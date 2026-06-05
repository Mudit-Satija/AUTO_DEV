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


def _extract_import_symbols(content: str) -> List[tuple[str, List[str], bool]]:
    """Extract (import_path, [imported_symbols], is_destructured) from CommonJS
    and ES module imports.

    Returns a list of ``(local_import_path, [symbol_names], is_destructured)``
    for every local import found in *content*.  Symbol aliases (``{ a as b }``)
    are resolved to the original export name (``a``).  The *is_destructured*
    flag is True when the import uses ``{ ... }`` syntax, False for bare or
    namespace imports.
    """
    imports: List[tuple[str, List[str], bool]] = []

    for m in re.finditer(
        r"""(?:const|let|var)\s*\{([^}]+)\}\s*=\s*require\(['"](\.\.?/[^'"]+)['"]\)""",
        content,
    ):
        path = m.group(2).strip()
        symbols: List[str] = []
        for s in m.group(1).split(","):
            s = s.strip()
            if " as " in s:
                s = s.split(" as ")[0].strip()
            if s:
                symbols.append(s)
        imports.append((path, symbols, True))

    for m in re.finditer(
        r"""(?:const|let|var)\s+(\w+)\s*=\s*require\(['"](\.\.?/[^'"]+)['"]\)""",
        content,
    ):
        path = m.group(2).strip()
        imports.append((path, [m.group(1).strip()], False))

    for m in re.finditer(
        r"""import\s+\*\s+as\s+(\w+)\s+from\s+['"](\.\.?/[^'"]+)['"]""",
        content,
    ):
        path = m.group(2).strip()
        imports.append((path, [m.group(1).strip()], False))

    for m in re.finditer(
        r"""import\s+\{([^}]+)\}\s+from\s+['"](\.\.?/[^'"]+)['"]""",
        content,
    ):
        path = m.group(2).strip()
        symbols = []
        for s in m.group(1).split(","):
            s = s.strip()
            if " as " in s:
                s = s.split(" as ")[0].strip()
            if s:
                symbols.append(s)
        imports.append((path, symbols, True))

    for m in re.finditer(
        r"""import\s+(\w+)\s+from\s+['"](\.\.?/[^'"]+)['"]""",
        content,
    ):
        path = m.group(2).strip()
        imports.append((path, [m.group(1).strip()], False))

    return imports


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

    When a dependency declares a non-empty ``provides`` list, each import
    from that dependency is additionally validated: the imported symbol
    must appear in the dependency's ``provides`` list.
    """
    generated_paths = {bp["path"] for bp in build_plan.get("files", [])}
    errors: List[str] = []

    provides_by_path: Dict[str, List[str]] = {}
    for bp in build_plan.get("files", []):
        p = bp.get("provides", [])
        if p:
            provides_by_path[bp["path"]] = p

    for bp in build_plan.get("files", []):
        filepath = Path(output_dir) / bp["path"]
        if not filepath.exists():
            continue

        content = filepath.read_text(encoding="utf-8", errors="replace")
        raw_imports = _extract_local_imports(content)
        allowed_deps = set(bp.get("depends_on", []))

        import_symbols: Dict[str, tuple] = {}
        for imp_path, symbols, is_destructured in _extract_import_symbols(content):
            import_symbols[imp_path] = (symbols, is_destructured)

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

            # Export shape validation — only when the dependency declares provides
            # and the import is destructured ({ ... }).  Bare require() variable
            # names are arbitrary and should not be checked against provides.
            if exists and (not allowed_deps or resolved in allowed_deps):
                dep_provides = provides_by_path.get(resolved, [])
                if dep_provides:
                    sym_info = import_symbols.get(raw_imp, ([], False))
                    symbols, is_destructured = sym_info
                    if is_destructured:
                        for sym in symbols:
                            if sym not in dep_provides:
                                errors.append(
                                    f"Export Validation Failed\n"
                                    f"\n"
                                    f"    {bp['path']}\n"
                                    f"\n"
                                    f"imports\n"
                                    f"\n"
                                    f"    {sym}\n"
                                    f"\n"
                                    f"from {resolved}, which does not export '{sym}' "
                                    f"(provides: {', '.join(dep_provides)}).\n"
                                )

    return errors
