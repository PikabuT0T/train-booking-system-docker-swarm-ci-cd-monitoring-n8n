#!/usr/bin/env python3
"""
Check encoding of Python files
"""
import os
import sys

def check_file_encoding(filepath):
    """Check if file can be read as UTF-8"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read()
        print(f"✓ {filepath} - OK")
        return True
    except UnicodeDecodeError as e:
        print(f"✗ {filepath} - ERROR: {e}")
        return False

def scan_directory(directory='.'):
    """Scan all Python files in directory"""
    errors = []
    
    for root, dirs, files in os.walk(directory):
        # Skip virtual environments and cache
        dirs[:] = [d for d in dirs if d not in ['venv', 'env', '__pycache__', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if not check_file_encoding(filepath):
                    errors.append(filepath)
    
    print("\n" + "="*50)
    if errors:
        print(f"Found {len(errors)} file(s) with encoding issues:")
        for error_file in errors:
            print(f"  - {error_file}")
    else:
        print("All files are correctly encoded!")
    
    return errors

if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    errors = scan_directory(directory)
    sys.exit(1 if errors else 0)
