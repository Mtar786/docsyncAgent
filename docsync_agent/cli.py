"""Command‑line interface for the DocSync Agent.

This CLI provides a simple interface for scanning a Python project,
inserting missing docstrings, and updating the README file with an API
reference section. By default both actions are performed, but you can
disable one or the other with command‑line flags.

Example usage:

    python -m docsync_agent.cli --project-dir path/to/project

"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .scanner import find_python_files, scan_python_file, insert_missing_docstrings, update_readme


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize your Python project's code with its documentation by inserting missing docstrings and updating the README."
    )
    parser.add_argument(
        "--project-dir",
        required=True,
        help="Path to the root of the Python project to scan.",
    )
    parser.add_argument(
        "--no-docstrings",
        action="store_true",
        help="Do not insert missing docstrings. Only update the README.",
    )
    parser.add_argument(
        "--no-readme",
        action="store_true",
        help="Do not update the README. Only insert missing docstrings.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.is_dir():
        raise SystemExit(f"Error: {project_dir} is not a valid directory")
    # Find Python files in the project
    files = find_python_files(str(project_dir))
    functions = []
    for file_path in files:
        functions.extend(scan_python_file(file_path))
    # Insert docstrings if requested
    if not args.no_docstrings:
        inserted = insert_missing_docstrings(functions)
        print(f"Inserted {inserted} stub docstrings.")
        # Re-scan after insertion to update docstring content
        if inserted > 0:
            # Rebuild functions list for README generation
            functions = []
            for file_path in files:
                functions.extend(scan_python_file(file_path))
    # Update README if requested
    if not args.no_readme:
        update_readme(str(project_dir), functions)
        print("Updated README.md with API reference section.")


if __name__ == "__main__":  # pragma: no cover
    main()