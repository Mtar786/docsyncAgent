"""DocSync Agent package.

The DocSync Agent provides tools to keep your Python project's
documentation synchronized with its source code. It can scan Python
modules to detect functions lacking docstrings, insert stub docstrings
where needed, and update a project's README with an up‑to‑date API
reference section. The API reference is generated from the docstrings
found in your code.

The core functionality lives in :mod:`docsync_agent.scanner`, and a
command line interface is exposed via :mod:`docsync_agent.cli`.
"""

__all__: list[str] = []