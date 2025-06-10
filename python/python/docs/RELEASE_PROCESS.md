# Release Process Documentation

This document outlines the complete release process for BPlusTree3 Python package.

## Overview

The release process is largely automated through GitHub Actions, but requires some manual steps for preparation and verification.

## Release Types

### Patch Release (0.1.0 → 0.1.1)
- Bug fixes
- Performance improvements
- Documentation updates
- No breaking changes

### Minor Release (0.1.0 → 0.2.0)
- New features
- Enhancements
- Non-breaking API additions
- Deprecations (with warnings)

### Major Release (0.1.0 → 1.0.0)
- Breaking changes
- Major new features
- API redesigns
- Significant architectural changes

## Automated Release Process

### Method 1: Version Bump in Code (Recommended)

1. **Update version in code**:
   ```bash
   cd python
   python scripts/release.py --bump patch  # or minor, major
   ```

2. **Review and commit changes**:
   ```bash
   git add __init__.py CHANGELOG.md
   git commit -m "chore: release v0.1.1"
   git push origin main
   ```

3. **Automated pipeline triggers**:
   - Version change detection
   - Comprehensive testing
   - Security scanning
   - Performance regression checks
   - Package building (wheels + sdist)
   - PyPI publishing
   - GitHub release creation

### Method 2: Manual GitHub Release

1. **Go to GitHub Releases page**
2. **Click "Create a new release"**
3. **Fill in release information**:
   - Tag: `v1.0.0` (will be created)
   - Title: `v1.0.0`
   - Description: Copy from CHANGELOG.md
4. **Publish release**
5. **Automated pipeline triggers**: Same as Method 1

### Method 3: Workflow Dispatch

1. **Go to GitHub Actions**
2. **Select "Release Automation" workflow**
3. **Click "Run workflow"**
4. **Enter version and options**
5. **Automated pipeline executes**

## Pre-Release Checklist

Before creating any release, ensure:

### Code Quality
- [ ] All tests pass (`pytest tests/`)
- [ ] Code formatting is correct (`black --check .`)
- [ ] Linting passes (`ruff check .`)
- [ ] Type checking passes (`mypy .`)
- [ ] No security vulnerabilities (`bandit -r .`)

### Documentation
- [ ] README.md is up to date
- [ ] CHANGELOG.md has entry for new version
- [ ] API documentation reflects changes
- [ ] Installation instructions are correct

### Performance
- [ ] Performance benchmarks run without regressions
- [ ] Memory usage is within acceptable limits
- [ ] C extension builds correctly on all platforms

### Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests pass
- [ ] Edge cases are tested
- [ ] Performance tests pass

## Manual Release Process

If you need to create a release manually:

### 1. Preparation

```bash
# Ensure clean working directory
git status

# Update to latest main
git checkout main
git pull origin main

# Run full test suite
cd python
pytest tests/ -v
black --check .
ruff check .
```

### 2. Version and Changelog

```bash
# Option A: Use release script
python scripts/release.py --bump patch --changes "Fix memory leak in deletion" "Improve performance"

# Option B: Manual update
# Edit __init__.py to update __version__
# Edit CHANGELOG.md to add new version section
```

### 3. Build and Test Package

```bash
# Clean previous builds
rm -rf build/ dist/

# Build package
python -m build

# Test package installation
pip install dist/*.whl
python -c "import bplustree; print('Import successful')"

# Test with different Python versions using tox
tox
```

### 4. Create Release

```bash
# Commit version changes
git add __init__.py CHANGELOG.md
git commit -m "chore: release v1.0.0"

# Create and push tag
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

### 5. Verify Automated Pipeline

- Monitor GitHub Actions for build status
- Verify wheels are built for all platforms
- Check PyPI upload success
- Verify GitHub release creation

## Post-Release Tasks

### Verification

1. **Check PyPI page**: https://pypi.org/project/bplustree3/
2. **Test installation from PyPI**:
   ```bash
   pip install bplustree3==1.0.0
   python -c "import bplustree; print('Success!')"
   ```
3. **Verify GitHub release**: Check release notes and assets

### Communication

1. **Update project README** with new version info
2. **Announce on social media** (if significant release)
3. **Update documentation** sites if needed
4. **Notify stakeholders** of breaking changes

## Troubleshooting

### Common Issues

#### Build Failures
- **C Extension compilation**: Check compiler flags and dependencies
- **Platform compatibility**: Verify cibuildwheel configuration
- **Missing dependencies**: Update requirements in pyproject.toml

#### Test Failures
- **Performance regressions**: Check benchmark thresholds
- **Platform-specific issues**: Test on different OS/Python combinations
- **Memory leaks**: Run memory profiling tools

#### PyPI Upload Issues
- **Authentication**: Verify GitHub secrets for PyPI
- **Package conflicts**: Check version uniqueness
- **Metadata validation**: Verify pyproject.toml configuration

### Recovery Procedures

#### Failed Release
1. **Delete the problematic tag**: `git tag -d v1.0.0 && git push origin :v1.0.0`
2. **Fix the issues**
3. **Restart release process**

#### PyPI Upload Failure
1. **Fix the issue** (usually build or metadata)
2. **Increment patch version**
3. **Re-release with new version**

#### GitHub Release Issues
1. **Edit the release** on GitHub
2. **Upload assets manually** if needed
3. **Update release notes**

## Security Considerations

### Package Security
- All packages are signed during CI/CD
- Dependencies are scanned for vulnerabilities
- Code is analyzed for security issues

### Access Control
- PyPI uploads use trusted publishing (OIDC)
- GitHub releases require maintainer permissions
- Sensitive data is stored in GitHub secrets

## Monitoring and Metrics

### Release Metrics
- Download statistics from PyPI
- GitHub release engagement
- Performance benchmark trends
- User feedback and issues

### Quality Metrics
- Test coverage percentage
- Performance regression tracking
- Security vulnerability counts
- Documentation completeness

## Release Schedule

### Regular Releases
- **Patch releases**: As needed for critical fixes
- **Minor releases**: Monthly or bi-monthly
- **Major releases**: Quarterly or as needed

### Emergency Releases
- Security vulnerabilities
- Critical bugs affecting data integrity
- Performance regressions > 50%

## Version Strategy

We follow [Semantic Versioning (SemVer)](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

### Pre-release Versions
- **Alpha**: `1.0.0-alpha.1` - Early development
- **Beta**: `1.0.0-beta.1` - Feature complete, testing
- **Release Candidate**: `1.0.0-rc.1` - Ready for production testing

## Tools and Scripts

### Release Script
```bash
python scripts/release.py --help
python scripts/release.py --current              # Show current version
python scripts/release.py --bump patch           # Bump patch version
python scripts/release.py --version 1.0.0        # Set specific version
```

### Performance Tracking
```bash
cd python/python/benchmarks
python track_performance.py --track             # Run and track
python track_performance.py --trends            # Show trends
python track_performance.py --export-ci         # Export for CI
```

### Quality Checks
```bash
# Full quality check suite
pytest tests/ --cov=bplustree --cov-report=html
black --check .
ruff check .
mypy .
bandit -r .
```

This release process ensures high quality, secure, and reliable releases while maintaining development velocity.