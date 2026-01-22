<div align="center">
  <img src="logo.png" alt="repo2md" width="512"/>

  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg)](https://www.python.org/)
  [![PyPI](https://img.shields.io/pypi/v/repo2md)](https://pypi.org/project/repo2md/)

  **📦 Transform any repository into a single Markdown document, perfect for LLM analysis 🤖**

  [Installation](#installation) · [Usage](#usage) · [Configuration](#configuration)
</div>

## Overview

`repo2md` is a CLI tool that converts local repositories into comprehensive Markdown documents. It generates a file tree overview followed by the concatenated content of all files, making codebases easy to share or feed to LLMs for analysis.

**Features:**
- 📁 Recursive file tree generation with visual hierarchy
- 📄 Smart file concatenation with size and binary detection
- 🚫 Automatic filtering of common ignore patterns (`.git`, `node_modules`, etc.)
- 📋 Optional clipboard support via pyperclip

## Installation

```bash
pipx install repo2md
```

Or install from source:

```bash
pipx install . --force
```

## Usage

```bash
# Convert repository in current directory
repo2md

# Convert a specific repository path
repo2md /path/to/your/repository

# Copy output to clipboard
repo2md /path/to/your/repository --clipboard

# Save output to a file
repo2md /path/to/your/repository > output.md
```

## Output Format

```markdown
# Repository: project-name

*Generated on: 2024-01-15T10:30:00*

## 📁 File Tree

- 📂 src/
  - 📄 main.py
  - 📄 utils.py
- 📄 README.md

## 📄 Files

<<< START FILE: src/main.py >>>
# file content here
<<< END FILE: src/main.py >>>
```

## Configuration

### Ignored Patterns

**Directories:** `.git`, `node_modules`, `.vscode`, `dist`, `build`, `.next`, `.cache`, `__pycache__`, `venv`, `env`

**Files:** `.DS_Store`, `.gitignore`, `.env`

**Wildcards:** `*.log`, `*.pyc`, `*.pyo`, `*.pyd`, `*.so`, `*.dylib`, `*.dll`, `*.ipynb`

### Limits

- **File size:** 500KB (files larger than this are skipped)
- **Binary detection:** Files with null bytes in the first 1024 bytes are skipped

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
