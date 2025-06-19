#!/usr/bin/env python3
"""
Test runner script for DataDagger
"""

import sys
import subprocess
import os


def run_tests():
    """Run the complete test suite"""
    
    print("🧪 DataDagger Test Suite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('datadagger'):
        print("❌ Error: Run this script from the project root directory")
        return 1
    
    # Install test dependencies
    print("📦 Installing test dependencies...")
    result = subprocess.run([
        sys.executable, "-m", "pip", "install", "-r", "tests/requirements-test.txt"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to install test dependencies: {result.stderr}")
        return 1
    
    print("✅ Test dependencies installed")
    
    # Run different test categories
    test_commands = [
        {
            'name': 'Unit Tests',
            'cmd': [sys.executable, "-m", "pytest", "tests/test_*.py", "-v", "--tb=short"],
            'description': 'Core functionality tests'
        },
        {
            'name': 'Integration Tests', 
            'cmd': [sys.executable, "-m", "pytest", "tests/test_integration.py", "-v"],
            'description': 'End-to-end workflow tests'
        },
        {
            'name': 'CLI Tests',
            'cmd': [sys.executable, "-m", "pytest", "tests/test_cli.py", "-v"],
            'description': 'Command-line interface tests'
        }
    ]
    
    overall_success = True
    
    for test_suite in test_commands:
        print(f"\n🔍 Running {test_suite['name']}...")
        print(f"   {test_suite['description']}")
        print("-" * 40)
        
        result = subprocess.run(test_suite['cmd'])
        
        if result.returncode == 0:
            print(f"✅ {test_suite['name']} passed")
        else:
            print(f"❌ {test_suite['name']} failed")
            overall_success = False
    
    # Optional: Run performance tests
    print(f"\n🚀 Performance Tests (optional)...")
    print("   Run with: pytest tests/test_performance.py -v -m slow")
    
    # Generate coverage report
    print(f"\n📊 Generating coverage report...")
    subprocess.run([
        sys.executable, "-m", "pytest", 
        "--cov=datadagger", 
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "tests/"
    ])
    
    print(f"\n📈 Coverage report saved to: htmlcov/index.html")
    
    # Summary
    print("\n" + "=" * 50)
    if overall_success:
        print("🎉 All tests passed! DataDagger is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1


def run_quick_tests():
    """Run quick tests only (no performance tests)"""
    print("⚡ Quick Test Suite")
    print("=" * 30)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/test_*.py",
        "-v", "--tb=short",
        "-x",  # Stop on first failure
        "--durations=10"  # Show 10 slowest tests
    ])
    
    return result.returncode


def run_specific_test(test_file):
    """Run a specific test file"""
    print(f"🎯 Running specific test: {test_file}")
    print("=" * 40)
    
    if not os.path.exists(f"tests/{test_file}"):
        print(f"❌ Test file not found: tests/{test_file}")
        return 1
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        f"tests/{test_file}",
        "-v", "--tb=short"
    ])
    
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            exit_code = run_quick_tests()
        elif sys.argv[1].startswith("test_"):
            exit_code = run_specific_test(sys.argv[1])
        else:
            print("Usage:")
            print("  python run_tests.py           # Run full test suite")
            print("  python run_tests.py quick     # Run quick tests only")
            print("  python run_tests.py test_*.py # Run specific test file")
            exit_code = 1
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)
