# Changelog

All notable changes to the B+ Tree Python implementation will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern Python packaging with pyproject.toml
- Cross-platform CI/CD with GitHub Actions
- Comprehensive test matrix across Python 3.8-3.12
- Automated wheel building for Linux, macOS, and Windows
- Complete dictionary API compatibility

### Changed
- Updated setup.py to work with modern packaging standards
- Improved C extension build configuration with platform-specific optimizations
- Enhanced error handling and memory safety in C extension

### Fixed
- Critical memory safety issues in C extension node splitting
- Reference counting bugs that caused segmentation faults
- Circular import issues in pure Python implementation

## [0.1.0] - 2024-XX-XX

### Added
- Initial B+ Tree implementation with pure Python fallback
- C extension for high-performance operations
- Basic dictionary-like API (`__getitem__`, `__setitem__`, `__delitem__`)
- Range query support with `items(start_key, end_key)`
- Comprehensive test suite with 115+ tests
- Performance benchmarks and analysis
- Basic documentation and examples

### Performance
- 1.4-2.5x faster than SortedDict for range queries
- Efficient insertion and deletion operations
- Memory-efficient arena-based allocation in Rust implementation

---

## Release Types

- **Major** (X.0.0): Breaking API changes
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes, no new features

## Contributing

When making changes:
1. Add entry under `[Unreleased]` section
2. Use standard categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. Include issue/PR numbers where applicable
4. Update version number in `__init__.py` before release