#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import argparse
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

# Configuration
IGNORE_DIRS = ['.git', 'node_modules', '.vscode', 'dist', 'build', '.next', '.cache', '__pycache__', 'venv', 'env']
IGNORE_FILES = ['.DS_Store', '.gitignore', '.env', '*.log', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dylib', '*.dll']
MAX_FILE_SIZE = 500 * 1024  # 500KB limit

def should_ignore(path):
    """Check if a path should be ignored."""
    basename = os.path.basename(path)
    
    # Check directory ignores
    if os.path.isdir(path):
        return basename in IGNORE_DIRS
    
    # Check specific file ignores
    if basename in IGNORE_FILES:
        return True
    
    # Check wildcard ignores
    for pattern in IGNORE_FILES:
        if pattern.startswith('*') and basename.endswith(pattern[1:]):
            return True
    
    return False

def get_extension(filename):
    """Get file extension without the dot."""
    ext = os.path.splitext(filename)[1]
    return ext[1:] if ext else ""

def generate_file_tree(root_path, indent=""):
    """Generate a file tree representation."""
    result = ""
    
    try:
        items = sorted(os.listdir(root_path))
        for item in items:
            item_path = os.path.join(root_path, item)
            
            # Skip ignored paths
            if should_ignore(item_path):
                continue
            
            if os.path.isdir(item_path):
                result += f"{indent}- 📂 {item}/\n"
                result += generate_file_tree(item_path, f"{indent}  ")
            else:
                result += f"{indent}- 📄 {item}\n"
    except Exception as e:
        print(f"Error processing {root_path}: {str(e)}", file=sys.stderr)
    
    return result

def process_file(file_path, relative_path):
    """Process a file and generate its markdown representation."""
    try:
        file_size = os.path.getsize(file_path)
        
        # Skip files that are too large
        if file_size > MAX_FILE_SIZE:
            return f"\n## {relative_path}\n\n*File too large to include ({file_size / 1024:.2f} KB)*\n\n"
        
        # Skip binary files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return f"\n## {relative_path}\n\n*Binary file (not included)*\n\n"
        
        extension = get_extension(file_path)
        
        return f"\n## {relative_path}\n\n```{extension}\n{content}\n```\n\n"
    except Exception as e:
        return f"\n## {relative_path}\n\n*Error reading file: {str(e)}*\n\n"

def process_repository(root_path, current_path="", result=None):
    """Recursively process all files in the repository."""
    if result is None:
        result = []
    
    full_current_path = os.path.join(root_path, current_path)
    
    try:
        items = sorted(os.listdir(full_current_path))
        for item in items:
            relative_path = os.path.join(current_path, item)
            full_path = os.path.join(root_path, relative_path)
            
            # Skip ignored paths
            if should_ignore(full_path):
                continue
            
            if os.path.isdir(full_path):
                process_repository(root_path, relative_path, result)
            else:
                file_content = process_file(full_path, relative_path)
                result.append(file_content)
    except Exception as e:
        print(f"Error processing {full_current_path}: {str(e)}", file=sys.stderr)
    
    return result

def generate_markdown(repo_path):
    """Generate markdown content for the entire repository."""
    try:
        # Get absolute path to repository
        abs_repo_path = os.path.abspath(repo_path)
        
        # Generate repository information
        repo_name = os.path.basename(abs_repo_path)
        header_info = f"# Repository: {repo_name}\n\n*Generated on: {datetime.now().isoformat()}*\n\n"
        
        # Generate file tree
        file_tree = generate_file_tree(repo_path)
        file_tree_section = f"## File Tree\n\n```\n{file_tree}```\n\n"
        
        # Generate file contents
        file_contents = process_repository(repo_path)
        
        # Combine all sections
        return header_info + file_tree_section + "".join(file_contents)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description='Convert a repository to a Markdown file')
    parser.add_argument('repo_path', nargs='?', default='.', help='Path to the repository (default: current directory)')
    parser.add_argument('--no-clipboard', action='store_true', help='Do not copy output to clipboard')
    args = parser.parse_args()
    
    repo_path = args.repo_path
    
    try:
        print(f"Processing repository at: {os.path.abspath(repo_path)}", file=sys.stderr)
        
        # Generate markdown content
        markdown_content = generate_markdown(repo_path)
        if not markdown_content:
            sys.exit(1)
        
        # Copy to clipboard if available and not disabled
        if CLIPBOARD_AVAILABLE and not args.no_clipboard:
            try:
                pyperclip.copy(markdown_content)
                print("✅ Markdown copied to clipboard", file=sys.stderr)
            except Exception as e:
                print(f"❌ Failed to copy to clipboard: {str(e)}", file=sys.stderr)
        elif not CLIPBOARD_AVAILABLE and not args.no_clipboard:
            print("ℹ️ Clipboard functionality not available. Install pyperclip: pip install pyperclip", file=sys.stderr)
        
        # Write to stdout
        print(markdown_content)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()