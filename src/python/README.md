# B+ Tree Python Implementation

A high-performance B+ tree implementation in Python, providing ordered key-value storage with efficient operations.

## Features

- **Efficient Operations**: O(log n) insertion, deletion, and lookup
- **Range Queries**: Efficient iteration over key ranges
- **Ordered Storage**: Keys are maintained in sorted order
- **Configurable Capacity**: Adjustable node capacity for performance tuning
- **Full Python API**: Dictionary-like interface with familiar Python semantics

## Installation

```bash
# From the project root
cd src/python
pip install -e .
```

## Quick Start

```python
from bplus_tree import BPlusTreeMap

# Create a B+ tree with capacity 32
tree = BPlusTreeMap(capacity=32)

# Insert key-value pairs
tree[1] = "one"
tree[2] = "two"
tree[3] = "three"

# Lookup values
print(tree[2])  # "two"

# Check membership
print(1 in tree)  # True

# Delete keys
del tree[2]

# Iterate over keys
for key in tree:
    print(key, tree[key])
```

## API Reference

### BPlusTreeMap

The main B+ tree class providing a dictionary-like interface.

#### Constructor
```python
BPlusTreeMap(capacity: int = 128)
```
- `capacity`: Maximum number of keys per node (minimum 16 recommended)

#### Methods
- `__setitem__(key, value)`: Insert or update a key-value pair
- `__getitem__(key)`: Retrieve value for a key
- `__delitem__(key)`: Delete a key-value pair
- `__contains__(key)`: Check if key exists
- `__len__()`: Get number of key-value pairs
- `__iter__()`: Iterate over keys in sorted order
- `keys()`: Get an iterator over all keys
- `values()`: Get an iterator over all values
- `items()`: Get an iterator over (key, value) pairs

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_bplus_tree.py

# Run with coverage
python -m pytest tests/ --cov=bplus_tree
```

## Performance

The B+ tree implementation is optimized for:
- Large datasets requiring ordered access
- Range queries and sequential access patterns
- Scenarios with mixed read/write workloads

Recommended capacity values:
- Small datasets (< 1000 items): 16-32
- Medium datasets (1000-100k items): 64-128
- Large datasets (> 100k items): 128-256

## Architecture

The implementation consists of:
- `bplus_tree.py`: Core B+ tree implementation
- `_invariant_checker.py`: Internal validation for tree structure
- `tests/`: Comprehensive test suite including unit tests and fuzz tests