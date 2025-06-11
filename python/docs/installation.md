# Installation Guide

## Requirements

- Python 3.8 or higher
- C compiler (optional, for C extension)
- pip package manager

## Quick Install

### From PyPI (Coming Soon)

Once released, you'll be able to install directly from PyPI:

```bash
pip install bplustree
```

### From Source

#### 1. Clone the Repository

```bash
git clone https://github.com/KentBeck/BPlusTree.git
cd BPlusTree/python
```

#### 2. Install in Development Mode

```bash
pip install -e .
```

This installs the package in editable mode, allowing you to modify the source code and see changes immediately.

#### 3. Install with Optional Dependencies

For development and testing:

```bash
pip install -e ".[dev]"
```

For benchmarking:

```bash
pip install -e ".[benchmark]"
```

For all extras:

```bash
pip install -e ".[dev,benchmark]"
```

## Building from Source

### Prerequisites

To build the C extension, you'll need:

- **Linux**: GCC or Clang
- **macOS**: Xcode Command Line Tools
- **Windows**: Microsoft Visual C++ 14.0 or greater

### Build Steps

1. **Install build dependencies:**

   ```bash
   pip install setuptools wheel cython
   ```

2. **Build the package:**

   ```bash
   python -m build
   ```

   This creates both source distribution and wheel in the `dist/` directory.

3. **Build only the C extension:**
   ```bash
   python setup.py build_ext --inplace
   ```

## Installation Options

### Pure Python Only

If you want to use only the pure Python implementation:

```python
import os
os.environ['BPLUSTREE_PURE_PYTHON'] = '1'
import bplustree
```

### Verify Installation

```python
from bplustree import BPlusTreeMap, get_implementation

# Check which implementation is being used
print(get_implementation())  # "C extension" or "Pure Python"

# Create and test a tree
tree = BPlusTreeMap()
tree[1] = "hello"
print(tree[1])  # "hello"
```

## Platform-Specific Notes

### Linux

No special requirements. The C extension builds automatically if a compiler is available.

### macOS

1. Install Xcode Command Line Tools if not already installed:

   ```bash
   xcode-select --install
   ```

2. For Apple Silicon (M1/M2) Macs, the package builds universal binaries by default.

### Windows

1. Install Microsoft C++ Build Tools:

   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "Desktop development with C++"

2. Alternative: Use pre-built wheels (when available on PyPI)

## Troubleshooting

### C Extension Build Failures

If the C extension fails to build, the package automatically falls back to the pure Python implementation. Common issues:

1. **Missing compiler:**

   - Solution: Install a C compiler for your platform
   - Alternative: Use pure Python implementation

2. **Cython not installed:**

   ```bash
   pip install cython>=0.29.30
   ```

3. **Permission errors:**
   ```bash
   pip install --user bplustree
   ```

### Import Errors

If you get import errors:

1. **Check Python version:**

   ```bash
   python --version  # Should be 3.8+
   ```

2. **Verify installation:**

   ```bash
   pip show bplustree
   ```

3. **Check for conflicts:**
   ```bash
   pip check
   ```

### Performance Issues

If performance is slower than expected:

1. **Verify C extension is loaded:**

   ```python
   from bplustree import get_implementation
   assert get_implementation() == "C extension"
   ```

2. **Check node capacity:**
   ```python
   tree = BPlusTreeMap(capacity=128)  # Larger capacity for better performance
   ```

## Docker Installation

For containerized environments:

```dockerfile
FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install package
COPY . /app
WORKDIR /app
RUN pip install ./python

# Verify installation
RUN python -c "from bplustree import BPlusTreeMap; print('Installation successful')"
```

## Next Steps

- See [Quickstart Guide](quickstart.md) for usage examples
- Read [API Reference](api_reference.md) for detailed documentation
- Check [Performance Guide](performance_guide.md) for optimization tips
