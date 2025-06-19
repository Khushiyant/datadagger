#!/usr/bin/env python3
"""
Script to fix relative imports in all command files
"""

import os
import glob

def fix_imports_in_file(filepath):
    """Fix imports in a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix common import patterns
    replacements = [
        ('from scrapers.', 'from ..scrapers.'),
        ('from analyzers.', 'from ..analyzers.'),
        ('from utils.', 'from ..utils.'),
        ('from visualizers.', 'from ..visualizers.'),
    ]
    
    modified = False
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            modified = True
    
    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Fixed imports in {filepath}")
    else:
        print(f"No changes needed in {filepath}")

def main():
    """Fix imports in all command files"""
    package_dir = '/Users/khushiyantchauhan/Developer/experiments/datadagger/datadagger'
    
    # Fix imports in command files
    commands_dir = os.path.join(package_dir, 'commands')
    for filepath in glob.glob(os.path.join(commands_dir, '*.py')):
        if not filepath.endswith('__init__.py'):
            fix_imports_in_file(filepath)
    
    # Fix imports in scraper files
    scrapers_dir = os.path.join(package_dir, 'scrapers')
    for filepath in glob.glob(os.path.join(scrapers_dir, '*.py')):
        if not filepath.endswith('__init__.py'):
            fix_imports_in_file(filepath)
    
    # Fix imports in analyzer files
    analyzers_dir = os.path.join(package_dir, 'analyzers')
    for filepath in glob.glob(os.path.join(analyzers_dir, '*.py')):
        if not filepath.endswith('__init__.py'):
            fix_imports_in_file(filepath)

if __name__ == '__main__':
    main()
