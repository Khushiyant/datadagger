#!/bin/bash

# DataDagger Version Management Script
# Usage: ./release.sh [patch|minor|major]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository!"
    exit 1
fi

# Check if working directory is clean
if [[ -n $(git status --porcelain) ]]; then
    print_error "Working directory is not clean. Please commit or stash your changes."
    git status --short
    exit 1
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep -E '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

if [[ -z "$CURRENT_VERSION" ]]; then
    print_error "Could not find version in pyproject.toml"
    exit 1
fi

print_info "Current version: $CURRENT_VERSION"

# Parse version components
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Determine new version based on argument
BUMP_TYPE=${1:-patch}

case $BUMP_TYPE in
    patch)
        NEW_PATCH=$((PATCH + 1))
        NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"
        ;;
    minor)
        NEW_MINOR=$((MINOR + 1))
        NEW_VERSION="$MAJOR.$NEW_MINOR.0"
        ;;
    major)
        NEW_MAJOR=$((MAJOR + 1))
        NEW_VERSION="$NEW_MAJOR.0.0"
        ;;
    *)
        print_error "Invalid bump type. Use: patch, minor, or major"
        exit 1
        ;;
esac

print_info "New version will be: $NEW_VERSION"

# Confirm with user
echo
read -p "Do you want to proceed with version $NEW_VERSION? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Release cancelled."
    exit 0
fi

print_info "Updating version in pyproject.toml..."
sed -i.bak "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
rm pyproject.toml.bak

# Also update setup.py if it exists
if [[ -f "setup.py" ]]; then
    print_info "Updating version in setup.py..."
    sed -i.bak "s/version=\"$CURRENT_VERSION\"/version=\"$NEW_VERSION\"/" setup.py
    rm setup.py.bak
fi

print_info "Running tests before release..."
if command -v pytest &> /dev/null; then
    python -m pytest tests/ || {
        print_error "Tests failed! Rolling back version changes."
        git checkout pyproject.toml setup.py 2>/dev/null || true
        exit 1
    }
else
    print_warning "pytest not found, skipping tests"
fi

print_info "Building package to verify..."
python -m build || {
    print_error "Build failed! Rolling back version changes."
    git checkout pyproject.toml setup.py 2>/dev/null || true
    exit 1
}

print_info "Committing version bump..."
git add pyproject.toml setup.py 2>/dev/null || git add pyproject.toml
git commit -m "Bump version to $NEW_VERSION"

print_info "Creating git tag..."
git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"

print_success "Version bumped to $NEW_VERSION and tagged!"
echo
print_info "To publish to PyPI, push the tag:"
print_info "  git push origin v$NEW_VERSION"
echo
print_info "Or push everything including the commit:"
print_info "  git push && git push --tags"
echo
print_warning "This will trigger the GitHub Actions workflow to automatically publish to PyPI."
