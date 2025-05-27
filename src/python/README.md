# B+ Tree Python Implementation

A Python implementation of a B+ tree data structure with a dict-like API.

## Features

- **Dict-like API**: Use familiar Python dictionary operations
- **Fixed capacity nodes**: Both leaf and branch nodes have configurable capacity
- **Ordered key storage**: Keys are maintained in sorted order
- **Efficient lookups**: O(log n) search complexity

## Basic Usage

```python
from bplus_tree import BPlusTreeMap

# Create a B+ tree with node capacity of 4
tree = BPlusTreeMap(capacity=4)

# Insert items using dict-like syntax
tree[1] = "one"
tree[2] = "two" 
tree[3] = "three"

# Access items
print(tree[1])  # "one"
print(tree.get(2))  # "two"
print(tree.get(4, "default"))  # "default"

# Check membership
if 1 in tree:
    print("Key 1 exists")

# Get size
print(len(tree))  # 3
```

## Architecture

### Node Types

1. **LeafNode**: Contains actual key-value pairs
   - Stores keys and values in sorted order
   - Links to next leaf node for range operations
   - Capacity determines when splitting occurs

2. **BranchNode**: Internal navigation nodes
   - Contains separator keys and child pointers
   - Routes searches to appropriate child nodes
   - Also has fixed capacity

3. **BPlusTreeMap**: Main tree structure
   - Provides dict-like API
   - Manages root node (can be leaf or branch)
   - Handles tree operations and rebalancing

## Current Implementation Status

✅ Implemented:
- Basic tree structure with leaf and branch nodes
- Dict-like API (`__getitem__`, `__setitem__`, `__contains__`)
- Single-level tree operations (leaf-only)
- Key lookup and insertion
- Update existing keys

🚧 TODO:
- Node splitting when capacity exceeded
- Tree growth (leaf to branch promotion)
- Multi-level tree navigation
- Deletion operations
- Range queries and iteration
- Tree rebalancing on deletion

## Running Tests

```bash
cd src/python
python -m pytest test_bplus_tree.py -v
```

All 13 initial tests are passing, covering:
- Basic tree operations
- LeafNode functionality
- BranchNode child navigation
- Dict-like API compliance