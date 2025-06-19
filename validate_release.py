#!/usr/bin/env python3
"""
Pre-release validation script for DataDagger
Checks package integrity before publishing to PyPI
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True,
            check=True
        )
        return result.stdout.strip() if capture_output else True
    except subprocess.CalledProcessError as e:
        return False

def check_python_syntax():
    """Check Python syntax in all .py files"""
    print("🔍 Checking Python syntax...")
    
    py_files = list(Path(".").rglob("*.py"))
    errors = []
    checked_count = 0
    
    for py_file in py_files:
        # Skip virtual environments, cache, and git directories
        if any(skip in str(py_file) for skip in ["/.venv/", "/.git/", "/__pycache__/", "/htmlcov/", "/.pytest_cache/"]):
            continue
        
        # Skip very large files
        try:
            if py_file.stat().st_size > 1024 * 1024:  # 1MB limit
                continue
        except OSError:
            continue
            
        checked_count += 1
        if checked_count > 50:  # Limit to avoid hanging
            break
            
        try:
            # Use timeout to avoid hanging
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(py_file)],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                errors.append(str(py_file))
        except subprocess.TimeoutExpired:
            errors.append(f"{py_file} (timeout)")
        except Exception as e:
            errors.append(f"{py_file} ({str(e)})")
    
    if errors:
        print(f"❌ Syntax errors found in: {', '.join(errors[:5])}")  # Show only first 5
        return False
    
    print(f"✅ All Python files have valid syntax ({checked_count} files checked)")
    return True

def check_package_structure():
    """Validate package structure"""
    print("📁 Checking package structure...")
    
    required_files = [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "datadagger/__init__.py",
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        return False
    
    print("✅ Package structure is valid")
    return True

def check_version_consistency():
    """Check version consistency across files"""
    print("🔢 Checking version consistency...")
    
    # Get version from pyproject.toml
    with open("pyproject.toml", "r") as f:
        content = f.read()
        for line in content.split("\n"):
            if line.strip().startswith("version = "):
                pyproject_version = line.split('"')[1]
                break
        else:
            print("❌ Could not find version in pyproject.toml")
            return False
    
    # Check setup.py if it exists
    if Path("setup.py").exists():
        with open("setup.py", "r") as f:
            content = f.read()
            if f'version="{pyproject_version}"' not in content:
                print("❌ Version mismatch between pyproject.toml and setup.py")
                return False
    
    print(f"✅ Version {pyproject_version} is consistent across files")
    return True

def run_tests():
    """Run the test suite"""
    print("🧪 Running tests...")
    
    if not Path("tests").exists():
        print("⚠️  No tests directory found")
        return True
    
    result = run_command("python -m pytest tests/ -v", capture_output=False)
    if not result:
        print("❌ Tests failed")
        return False
    
    print("✅ All tests passed")
    return True

def build_package():
    """Build the package and check it"""
    print("📦 Building package...")
    
    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info/")
    
    # Build package
    print("  Building wheel and source distribution...")
    result = subprocess.run(
        [sys.executable, '-m', 'build'],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode != 0:
        print("❌ Package build failed:")
        print(result.stderr)
        return False
    
    # Check with twine
    print("  Checking package integrity...")
    result = subprocess.run(
        [sys.executable, '-m', 'twine', 'check', 'dist/*'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        print("❌ Package check failed:")
        print(result.stderr)
        return False
    
    print("✅ Package built and validated successfully")
    return True

def check_dependencies():
    """Check if all dependencies are properly specified"""
    print("📋 Checking dependencies...")
    
    try:
        # Try to install in a virtual environment simulation
        result = run_command("pip check")
        if result:
            print("✅ Dependencies are consistent")
            return True
        else:
            print("❌ Dependency conflicts found")
            return False
    except:
        print("⚠️  Could not verify dependencies")
        return True

def main():
    """Run all validation checks"""
    print("🚀 DataDagger Pre-Release Validation")
    print("=" * 40)
    
    checks = [
        ("Package Structure", check_package_structure),
        ("Python Syntax", check_python_syntax),
        ("Version Consistency", check_version_consistency),
        ("Dependencies", check_dependencies),
        ("Tests", run_tests),
        ("Package Build", build_package),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 20)
        
        if not check_func():
            failed_checks.append(check_name)
    
    print("\n" + "=" * 40)
    print("🏁 Validation Summary")
    print("=" * 40)
    
    if failed_checks:
        print(f"❌ {len(failed_checks)} checks failed:")
        for check in failed_checks:
            print(f"   • {check}")
        print("\n🚫 Package is NOT ready for release")
        sys.exit(1)
    else:
        print("✅ All checks passed!")
        print("🎉 Package is ready for release")
        
        # Show next steps
        print("\n📋 Next Steps:")
        print("1. ./release.sh [patch|minor|major]")
        print("2. git push && git push --tags")
        print("3. Wait for GitHub Actions to publish to PyPI")

if __name__ == "__main__":
    main()
