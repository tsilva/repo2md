# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`repo2md` is a command-line tool that converts local repositories into single Markdown documents. It generates a file tree overview followed by the concatenated content of all non-ignored files, making repositories easy to share or feed to LLMs for analysis.

## Build and Development Commands

**Installation (local development):**
```bash
pipx install . --force
```

**Run the tool:**
```bash
# Current directory
repo2md

# Specific path
repo2md /path/to/repository

# With clipboard support
repo2md /path/to/repository --clipboard
```

## Architecture

### Code Structure

The codebase uses a **src-layout** with the main logic in `src/repo2md/main.py`. The package is built with hatchling.

**Single-module architecture:**
- `src/repo2md/main.py` - Contains all functionality:
  - Environment setup with `.env` file in `~/.repo2md/`
  - File tree generation (recursive directory traversal)
  - File processing with size/binary checks
  - Markdown output generation
  - Optional clipboard integration via pyperclip

### Key Behaviors

**Ignored patterns:**
- Directories: `.git`, `node_modules`, `.vscode`, `dist`, `build`, `.next`, `.cache`, `__pycache__`, `venv`, `env`
- Files: `.DS_Store`, `.gitignore`, `.env`
- Wildcards: `*.log`, `*.pyc`, `*.pyo`, `*.pyd`, `*.so`, `*.dylib`, `*.dll`, `*.ipynb`

**File size limit:** 500KB (configurable via `MAX_FILE_SIZE`)

**Binary detection:** Checks for null bytes in first 1024 bytes

**Output format:**
```markdown
# Repository: {name}
*Generated on: {timestamp}*

## 📁 File Tree
{recursive tree with 📂/📄 emojis}

## 📄 Files
<<< START FILE: {path} >>>
{content}
<<< END FILE: {path} >>>
```

### Environment Configuration

The tool creates a `.env` file at `~/.repo2md/.env` on first run (though currently `REQUIRED_VARS` is empty, so no variables are mandatory).

## Important Considerations

- **README.md must be kept up to date** with any significant project changes
- When modifying ignore patterns, update `IGNORE_DIRS`, `IGNORE_FILES`, or `WILDCARD_IGNORES` in main.py
- The tool outputs to stdout by default; stderr is used for status messages
- Clipboard functionality is optional and gracefully degrades if pyperclip is not installed
