#!/usr/bin/env python3

import os
import sys
import shutil
import argparse
import fnmatch
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

RED, GREEN, RESET = '\033[31m', '\033[32m', '\033[0m'
CONFIG_DIR = Path.home() / "repo2md"
ENV_PATH = CONFIG_DIR / ".env"
REQUIRED_VARS = []

IGNORE_DIRS = {'.git', 'node_modules', '.vscode', 'dist', 'build', '.next', '.cache', '__pycache__', 'venv', 'env'}
IGNORE_FILES = {'.DS_Store', '.gitignore', '.env'}
WILDCARD_IGNORES = ['*.log', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dylib', '*.dll']
MAX_FILE_SIZE = 500 * 1024  # 500KB

def log_err(msg): print(f"{RED}{msg}{RESET}")
def log_ok(msg): print(f"{GREEN}{msg}{RESET}")
def fatal(msg): log_err(msg); sys.exit(1)

def setup_env():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not ENV_PATH.exists():
        try:
            shutil.copy(Path(__file__).parent / "configs" / ".env.example", ENV_PATH)
            log_ok(f"✅ Created default env file at {ENV_PATH}")
            print(f"⚠️  Edit this file with your config and rerun.\n🛠️  Use: nano {ENV_PATH}")
        except Exception as e:
            fatal(f"❌ Could not create .env: {e}")
        sys.exit(1)
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        fatal(f"Missing env vars: {', '.join(missing)}")

def should_ignore(path: Path) -> bool:
    name = path.name
    if path.is_dir():
        return name in IGNORE_DIRS
    if name in IGNORE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pattern) for pattern in WILDCARD_IGNORES)

def generate_file_tree(path: Path, indent: str = "") -> str:
    lines = []
    stack = [(path, indent)]
    while stack:
        current_path, current_indent = stack.pop()
        try:
            entries = sorted(current_path.iterdir(), reverse=True)
        except Exception as e:
            print(f"Error reading {current_path}: {e}", file=sys.stderr)
            continue

        for item in entries:
            if should_ignore(item):
                continue
            if item.is_dir():
                lines.append(f"{current_indent}- 📂 {item.name}/")
                stack.append((item, current_indent + "  "))
            else:
                lines.append(f"{current_indent}- 📄 {item.name}")
    return "\n".join(reversed(lines))

def process_file(file_path: Path, rel_path: Path) -> str:
    try:
        size = file_path.stat().st_size
        if size > MAX_FILE_SIZE:
            return f"\n## {rel_path}\n\n*File too large to include ({size / 1024:.2f} KB)*\n\n"
        content = file_path.read_text(encoding='utf-8', errors='replace')
        ext = file_path.suffix.lstrip('.') or 'txt'
        return f"\n## {rel_path}\n\n```{ext}\n{content}\n```\n\n"
    except Exception as e:
        return f"\n## {rel_path}\n\n*Error reading file: {e}*\n\n"

def process_repository(base: Path) -> list[str]:
    results = []
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if not should_ignore(Path(d))]
        for name in files:
            file_path = Path(root) / name
            if should_ignore(file_path):
                continue
            rel_path = file_path.relative_to(base)
            results.append(process_file(file_path, rel_path))
    return results

def generate_markdown(repo_path: Path) -> str:
    abs_repo = repo_path.resolve()
    header = f"# Repository: {abs_repo.name}\n\n*Generated on: {datetime.now().isoformat()}*\n\n"
    tree = generate_file_tree(abs_repo)
    contents = "".join(process_repository(abs_repo))
    return f"{header}## File Tree\n\n```\n{tree}\n```\n\n{contents}"

def main():
    parser = argparse.ArgumentParser(description='Convert a repository to a Markdown file')
    parser.add_argument('repo_path', nargs='?', default='.', help='Path to the repository (default: current directory)')
    parser.add_argument('--no-clipboard', action='store_true', help='Do not copy output to clipboard')
    args = parser.parse_args()

    setup_env()

    repo_path = Path(args.repo_path)
    print(f"Processing: {repo_path.resolve()}", file=sys.stderr)
    markdown = generate_markdown(repo_path)

    if not args.no_clipboard and CLIPBOARD_AVAILABLE:
        try:
            pyperclip.copy(markdown)
            print("✅ Copied to clipboard", file=sys.stderr)
        except Exception as e:
            print(f"❌ Clipboard error: {e}", file=sys.stderr)
    elif not args.no_clipboard:
        print("ℹ️ Install pyperclip for clipboard support: pip install pyperclip", file=sys.stderr)

    print(markdown)

if __name__ == "__main__":
    main()
