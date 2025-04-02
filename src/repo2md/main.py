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
REQUIRED_VARS = ["MODEL_ID", "OPENROUTER_BASE_URL", "OPENROUTER_API_KEY"]

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
    output = []
    try:
        for item in sorted(path.iterdir()):
            if should_ignore(item):
                continue
            if item.is_dir():
                output.append(f"{indent}- 📂 {item.name}/")
                output.append(generate_file_tree(item, indent + "  "))
            else:
                output.append(f"{indent}- 📄 {item.name}")
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
    return "\n".join(output)

def process_file(file_path: Path, rel_path: Path) -> str:
    try:
        size = file_path.stat().st_size
        if size > MAX_FILE_SIZE:
            return f"\n## {rel_path}\n\n*File too large to include ({size / 1024:.2f} KB)*\n\n"
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return f"\n## {rel_path}\n\n*Binary file (not included)*\n\n"
        ext = file_path.suffix.lstrip('.')
        return f"\n## {rel_path}\n\n```{ext}\n{content}\n```\n\n"
    except Exception as e:
        return f"\n## {rel_path}\n\n*Error reading file: {e}*\n\n"

def process_repository(base: Path, rel: Path = Path(), acc=None):
    if acc is None:
        acc = []
    current = base / rel
    try:
        for item in sorted(current.iterdir()):
            if should_ignore(item):
                continue
            rel_item = rel / item.name
            if item.is_dir():
                process_repository(base, rel_item, acc)
            else:
                acc.append(process_file(item, rel_item))
    except Exception as e:
        print(f"Error processing {current}: {e}", file=sys.stderr)
    return acc

def generate_markdown(repo_path: Path) -> str:
    abs_repo = repo_path.resolve()
    header = f"# Repository: {abs_repo.name}\n\n*Generated on: {datetime.now().isoformat()}*\n\n"
    file_tree = f"## File Tree\n\n```\n{generate_file_tree(abs_repo)}\n```\n\n"
    contents = "".join(process_repository(abs_repo))
    return header + file_tree + contents

def main():
    parser = argparse.ArgumentParser(description='Convert a repository to a Markdown file')
    parser.add_argument('repo_path', nargs='?', default='.', help='Path to the repository (default: current directory)')
    parser.add_argument('--no-clipboard', action='store_true', help='Do not copy output to clipboard')
    args = parser.parse_args()

    setup_env()

    try:
        repo_path = Path(args.repo_path)
        print(f"Processing repository at: {repo_path.resolve()}", file=sys.stderr)
        markdown = generate_markdown(repo_path)
        if not markdown:
            sys.exit(1)
        if CLIPBOARD_AVAILABLE and not args.no_clipboard:
            try:
                pyperclip.copy(markdown)
                print("✅ Markdown copied to clipboard", file=sys.stderr)
            except Exception as e:
                print(f"❌ Clipboard copy failed: {e}", file=sys.stderr)
        elif not CLIPBOARD_AVAILABLE and not args.no_clipboard:
            print("ℹ️ Install pyperclip for clipboard support: pip install pyperclip", file=sys.stderr)
        print(markdown)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
