#!/usr/bin/env python3
"""
Script to update import statements from 'devices' to 'devint'.
"""
import os
import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update import statements in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace 'from devint.' with 'from devint.'
    updated = re.sub(
        r'from\s+devices\.', 
        'from devint.', 
        content
    )
    
    # Replace 'import devint.' with 'import devint.'
    updated = re.sub(
        r'import\s+devices\.', 
        'import devint.', 
        updated
    )
    
    if updated != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated)
        print(f"Updated: {file_path}")

def main():
    """Main function to update imports in all Python files."""
    project_root = Path(__file__).parent
    
    # Process all Python files in the project
    for py_file in project_root.glob('**/*.py'):
        # Skip virtual environment directories
        if any(part.startswith(('.', '__')) and part not in ['__init__.py'] 
               for part in py_file.parts):
            continue
            
        update_imports_in_file(py_file)

if __name__ == "__main__":
    main()
