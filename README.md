# DocSync Agent

**Keep your Python project's documentation in lockstep with its code.**  
The DocSync Agent scans your codebase, inserts missing docstrings and
updates a structured API reference in your README. By automating
documentation maintenance, you can focus on writing quality code while
ensuring your users always have up‑to‑date reference material.

## Motivation

Maintaining documentation is time‑consuming, but it’s crucial for
project adoption. The Real Python tutorial on building project
documentation with MkDocs notes that tools like mkdocstrings can
generate user‑friendly documentation from Markdown files and your
code’s docstrings【387006221501932†L120-L129】. Auto‑generated docs reduce
maintenance effort by linking information between your code and the
documentation pages, but good documentation should still include
examples and narrative【387006221501932†L120-L129】. The same article
encourages starting your documentation in docstrings and then building
it into a deployed resource【387006221501932†L142-L145】. DocSync Agent
embraces this philosophy: it ensures every function has a docstring and
then uses those docstrings to populate an API reference section of
your README.

## Features

- **Docstring insertion** – Scans each Python file in your project and
  inserts a stub docstring into any function lacking one. The stub
  contains a TODO note prompting you to write a real description.
- **README synchronization** – Generates a Markdown API reference from
  the docstrings found in your code and inserts or updates this
  reference between `<!-- DOCS START -->` and `<!-- DOCS END -->`
  markers in your README. If markers are absent, the section is
  appended at the end.
- **CLI interface** – Run `python -m docsync_agent.cli` to scan your
  project, with options to disable docstring insertion or README
  updates.

## Installation

Requires Python 3.8 or later. Clone this repository and install
dependencies (there are no third‑party dependencies):

```bash
pip install -e .
```

## Usage

From your project root, run:

```bash
python -m docsync_agent.cli --project-dir .
```

By default, DocSync Agent will insert stub docstrings and update the
README. To skip inserting docstrings and only update the README, use
`--no-docstrings`. To skip updating the README and only insert
docstrings, use `--no-readme`.

### Example workflow

1. **Write your code**. As you create functions and classes, write
   meaningful docstrings or leave them blank to be filled in later.
2. **Run DocSync Agent**. The agent will insert stub docstrings for
   any functions missing one. Then it will regenerate the API
   reference in your README, listing each function signature and the
   first line of its docstring.
3. **Fill in TODOs**. Edit the generated docstrings in your code to
   provide detailed descriptions, examples, parameter explanations and
   return value notes. Updating your docstrings will automatically
   propagate to the README when you run the agent again.

## How it works

DocSync Agent uses Python’s built‑in `ast` module to parse your source
files and extract information about functions and methods. For each
function without a docstring, it inserts a stub docstring just inside
the function body, preserving indentation. It aggregates all
function signatures and docstrings into an API reference. This
reference is written into your README file between special markers.
If the markers are absent, a new section is appended.

### Markers in README

To customize where the API reference appears in your README, include
the following markers:

```markdown
<!-- DOCS START -->
... (auto‑generated content will be placed here) ...
<!-- DOCS END -->
```

The content between these markers will be replaced each time you run
the agent. You can place these markers anywhere in your README to
control placement of the API reference.

## Research and context

The DocSync Agent takes inspiration from documentation best practices.
The Real Python article on building documentation with MkDocs explains
that mkdocstrings can pull documentation directly from code’s
docstrings to generate user‑friendly documentation pages【387006221501932†L120-L129】.
Auto‑generated documentation reduces effort by linking your code to
your docs, but a project will appeal to users if you supplement auto
generated descriptions with examples and narrative【387006221501932†L120-L129】.
Furthermore, the article recommends starting your documentation in
docstrings and building it into a deployed resource【387006221501932†L142-L145】.  DocSync
Agent helps you follow this approach by ensuring every function has a
docstring and keeping your README’s API reference in sync with your
code.

## License

This project is licensed under the MIT License.
