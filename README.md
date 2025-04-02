# repo2md

Convert a repository to a Markdown document.

## Installation

You can install the package globally using pipx:

```bash
# Install pipx if you don't have it already
pip install pipx
pipx ensurepath

# Install repo2md (use --force to reinstall if needed)
pipx install . --force
```

## Usage

```bash
# Convert repository and output to stdout (also copies to clipboard)
repo2md /path/to/repository

# Convert repository without copying to clipboard
repo2md /path/to/repository --no-clipboard

# Save output to a file using redirection
repo2md /path/to/repository > output.md
```

The tool outputs to stdout by default and also copies the Markdown to your clipboard for easy pasting.
