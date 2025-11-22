"""Core scanning and update functions for the DocSync Agent.

This module defines utilities to scan a Python project, insert missing
docstrings into functions, and generate an API reference section for
a project's README. It uses the standard library ``ast`` module to
parse Python source files, detect functions and their signatures, and
handle docstrings.
"""

from __future__ import annotations

import ast
import os
import textwrap
from typing import Dict, List, Tuple


class FunctionInfo:
    """Simple data structure to hold information about a function or method."""

    def __init__(self, name: str, args: List[str], docstring: str | None, lineno: int, col_offset: int, file_path: str) -> None:
        self.name = name
        self.args = args
        self.docstring = docstring
        self.lineno = lineno
        self.col_offset = col_offset
        self.file_path = file_path

    def signature(self) -> str:
        return f"{self.name}({', '.join(self.args)})"


def _gather_functions(node: ast.AST, file_path: str) -> List[FunctionInfo]:
    """Recursively walk an AST node and collect information on functions.

    Args:
        node: The AST node to examine.
        file_path: The file path the node belongs to.

    Returns:
        A list of :class:`FunctionInfo` objects for each top-level function and
        method encountered.
    """
    functions: List[FunctionInfo] = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Build list of argument names (omit self for methods)
            arg_names = []
            for arg in child.args.args:
                if arg.arg == "self":
                    continue
                arg_names.append(arg.arg)
            docstring = ast.get_docstring(child, clean=False)
            info = FunctionInfo(
                name=child.name,
                args=arg_names,
                docstring=docstring,
                lineno=child.lineno,
                col_offset=child.col_offset,
                file_path=file_path,
            )
            functions.append(info)
        # Recurse into classes and functions
        if isinstance(child, ast.ClassDef):
            functions.extend(_gather_functions(child, file_path))
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.extend(_gather_functions(child, file_path))
    return functions


def scan_python_file(file_path: str) -> List[FunctionInfo]:
    """Parse a Python file and return information on all functions and methods.

    Args:
        file_path: The path to the Python file to scan.

    Returns:
        A list of :class:`FunctionInfo` objects describing the file's
        functions and methods.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=file_path)
    except SyntaxError:
        # Skip files with syntax errors
        return []
    return _gather_functions(tree, file_path)


def find_python_files(root_dir: str) -> List[str]:
    """Recursively find Python files under the given directory.

    Args:
        root_dir: The directory to search.

    Returns:
        A list of absolute file paths to Python files.
    """
    files: List[str] = []
    for base, _dirs, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py") and not filename.startswith("."):
                files.append(os.path.join(base, filename))
    return files


def insert_missing_docstrings(functions: List[FunctionInfo]) -> int:
    """Insert stub docstrings into functions that currently have none.

    Args:
        functions: A list of :class:`FunctionInfo` objects, possibly from
            different files.

    Returns:
        The number of docstrings inserted.
    """
    # Group functions by file for efficient writing
    functions_by_file: Dict[str, List[FunctionInfo]] = {}
    for func in functions:
        if func.docstring is None:
            functions_by_file.setdefault(func.file_path, []).append(func)
    count = 0
    for file_path, funcs in functions_by_file.items():
        # Read file lines
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Sort functions by line number descending
        funcs_sorted = sorted(funcs, key=lambda f: f.lineno, reverse=True)
        for func_info in funcs_sorted:
            indent = " " * (func_info.col_offset + 4)
            stub = f'{indent}"""TODO: Document `{func_info.name}`."""\n'
            # Insert after the def line (line numbers are 1-based)
            insert_index = func_info.lineno  # After def line
            lines.insert(insert_index, stub)
            count += 1
        # Write file back
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
    return count


def generate_api_reference(functions: List[FunctionInfo]) -> List[str]:
    """Generate a Markdown API reference section from function information.

    The output is a list of strings, one per line, containing Markdown
    formatted text documenting each function by file.

    Args:
        functions: A list of :class:`FunctionInfo` objects.

    Returns:
        A list of strings forming the API reference section.
    """
    lines: List[str] = []
    # Group functions by file relative name
    grouped: Dict[str, List[FunctionInfo]] = {}
    for func in functions:
        rel = os.path.relpath(func.file_path)
        grouped.setdefault(rel, []).append(func)
    for file_name in sorted(grouped.keys()):
        lines.append(f"### `{file_name}`")
        for func in grouped[file_name]:
            signature = func.signature()
            doc = (func.docstring or "TODO: Write documentation").splitlines()[0].strip()
            # Escape backticks in signature
            signature_escaped = signature.replace("`", "\`")
            lines.append(f"- **{signature_escaped}**: {doc}")
        lines.append("")
    return lines


def update_readme(project_root: str, functions: List[FunctionInfo]) -> None:
    """Update a project's README.md API reference section.

    The function looks for markers ``<!-- DOCS START -->`` and ``<!-- DOCS END -->``
    in the README file located at ``project_root/README.md``. It replaces
    the content between those markers with the generated API reference. If
    the markers do not exist, a new section is appended at the end of the
    README with these markers.

    Args:
        project_root: The root directory of the project.
        functions: A list of :class:`FunctionInfo` objects used to build
            the API reference.
    """
    readme_path = os.path.join(project_root, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            contents = f.read()
    else:
        contents = "# Project Documentation\n\n"
    start_marker = "<!-- DOCS START -->"
    end_marker = "<!-- DOCS END -->"
    api_lines = generate_api_reference(functions)
    api_content = "\n".join([start_marker] + api_lines + [end_marker])
    if start_marker in contents and end_marker in contents:
        # Replace existing section
        before = contents.split(start_marker)[0]
        after = contents.split(end_marker)[1]
        new_contents = before + api_content + after
    else:
        # Append new section
        if not contents.endswith("\n"):
            contents += "\n"
        new_contents = contents + api_content + "\n"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_contents)