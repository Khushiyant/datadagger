# PyPI Publishing Setup Guide

This guide explains how to set up automatic PyPI publishing for the DataDagger OSINT tool using GitHub Actions.

## 🚀 Quick Start

Once configured, publishing a new version is as simple as:

```bash
# Bump version and create tag
./release.sh patch  # or minor, major

# Push to trigger PyPI publication
git push && git push --tags
```

## 📋 Setup Requirements

### 1. PyPI Account Setup

1. **Create PyPI Account**: https://pypi.org/account/register/
2. **Verify Email**: Check your email and verify the account
3. **Enable 2FA**: Highly recommended for security

### 2. GitHub Repository Setup

#### Option A: Trusted Publishing (Recommended)

This is the most secure method and doesn't require storing API tokens.

1. **Configure PyPI Trusted Publisher**:
   - Go to https://pypi.org/manage/account/publishing/
   - Click "Add a new pending publisher"
   - Fill in:
     - **PyPI Project Name**: `datadagger`
     - **Owner**: `khushiyant`
     - **Repository name**: `datadagger`
     - **Workflow filename**: `publish-pypi.yml`
     - **Environment name**: `pypi`

2. **Create GitHub Environment**:
   - Go to your GitHub repository settings
   - Navigate to "Environments" 
   - Create a new environment named `pypi`
   - Add protection rules if desired (e.g., require reviewers)

#### Option B: API Token Method (Alternative)

If you prefer using API tokens:

1. **Generate PyPI Token**:
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token
   - Set scope to "Entire account" or specific to your project

2. **Add GitHub Secret**:
   - Go to repository Settings → Secrets and variables → Actions
   - Add a new secret named `PYPI_API_TOKEN`
   - Paste your PyPI token as the value

3. **Update Workflow** (if using tokens):
   ```yaml
   - name: Publish to PyPI
     uses: pypa/gh-action-pypi-publish@release/v1
     with:
       password: ${{ secrets.PYPI_API_TOKEN }}
   ```

## 🔄 Version Management

### Using the Release Script

The `release.sh` script automates version bumping:

```bash
# Patch version (1.0.0 → 1.0.1)
./release.sh patch

# Minor version (1.0.0 → 1.1.0)
./release.sh minor

# Major version (1.0.0 → 2.0.0)
./release.sh major
```

### Manual Version Management

1. **Update Version**: Edit `pyproject.toml` and `setup.py`
2. **Commit Changes**: `git commit -m "Bump version to X.Y.Z"`
3. **Create Tag**: `git tag -a vX.Y.Z -m "Release version X.Y.Z"`
4. **Push**: `git push && git push --tags`

## 📦 What Happens During Publication

1. **Tests Run**: All Python versions are tested
2. **Package Built**: Source and wheel distributions created
3. **Package Verified**: `twine check` validates the package
4. **PyPI Upload**: Package published to PyPI
5. **GitHub Release**: Automatic release created with artifacts

## 🔍 Monitoring and Troubleshooting

### Check Workflow Status

- Go to your repository's "Actions" tab
- Look for the "Publish to PyPI" workflow
- Check logs for any errors

### Common Issues

1. **Version Already Exists**:
   - Each version can only be uploaded once
   - Bump the version number and try again

2. **Permission Denied**:
   - Check that trusted publishing is configured correctly
   - Verify the GitHub environment name matches

3. **Test Failures**:
   - The workflow will stop if tests fail
   - Fix tests before publishing

4. **Build Errors**:
   - Check `pyproject.toml` and `setup.py` syntax
   - Ensure all dependencies are listed correctly

## 📋 Pre-Publication Checklist

Before creating a release:

- [ ] All tests pass locally: `pytest tests/`
- [ ] Documentation is updated
- [ ] `CHANGELOG.md` is updated with new features/fixes
- [ ] Version number follows semantic versioning
- [ ] No sensitive information in code
- [ ] Dependencies are properly specified

## 🔐 Security Best Practices

1. **Use Trusted Publishing**: More secure than API tokens
2. **Enable 2FA**: On both GitHub and PyPI accounts
3. **Review Dependencies**: Regularly audit package dependencies
4. **Environment Protection**: Use GitHub environment protection rules
5. **Minimal Permissions**: Grant only necessary permissions

## 📚 Additional Resources

- [PyPI Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)

## 🆘 Support

If you encounter issues:

1. Check the GitHub Actions logs
2. Review PyPI upload logs
3. Consult the troubleshooting section above
4. Check GitHub Discussions or Issues

---

**Happy Publishing! 🚀**
