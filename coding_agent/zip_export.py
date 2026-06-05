"""ZIP Export — packages a generated project directory into a ZIP archive."""

import shutil
from pathlib import Path


def export_to_zip(project_dir: str, output_path: str = None) -> str:
    """Package a generated project directory into a ZIP archive.

    Args:
        project_dir: Root directory of the generated project.
        output_path: Desired ZIP path. If None, uses project_dir + '.zip'.

    Returns:
        Absolute path to the created ZIP archive.
    """
    root = Path(project_dir)
    if not root.is_dir():
        raise ValueError(f"Project directory not found: {project_dir}")

    if output_path is None:
        output_path = str(root.resolve()) + ".zip"

    base_name = str(Path(output_path).with_suffix(""))
    archive_path = shutil.make_archive(
        base_name=base_name,
        format="zip",
        root_dir=root,
    )

    return str(Path(archive_path).resolve())
