# BPlusTree Python API Reference

## Overview

The `BPlusTreeMap` class provides a dictionary-like interface to a B+ tree data structure, offering efficient ordered storage with fast range queries and iteration.

## Class: BPlusTreeMap

### Constructor

#### `BPlusTreeMap(capacity=128)`

Create a new B+ tree instance.

**Parameters:**
- `capacity` (int, optional): Maximum number of keys per node. Default is 128.
  - Higher values (64-128): Better for large datasets, fewer tree levels
  - Lower values (4-16): Better for small datasets, testing

**Raises:**
- `InvalidCapacityError`: If capacity < 4

**Example:**
```python
from bplus_tree import BPlusTreeMap

# Default capacity (recommended for most use cases)
tree = BPlusTreeMap()

# Custom capacity for performance tuning
large_tree = BPlusTreeMap(capacity=64)
small_tree = BPlusTreeMap(capacity=8)
```

---

## Dictionary Interface Methods

### Basic Operations

#### `tree[key] = value`
Set a key-value pair.

**Parameters:**
- `key`: Must be orderable (support `<`, `>`, `==`)
- `value`: Any Python object

**Example:**
```python
tree[1] = "one"
tree["hello"] = "world"
```

#### `tree[key]`
Get value for a key.

**Returns:** The value associated with the key

**Raises:** `KeyError` if key not found

**Example:**
```python
value = tree[1]  # Returns "one"
```

#### `del tree[key]`
Remove a key-value pair.

**Raises:** `KeyError` if key not found

**Example:**
```python
del tree[1]  # Removes key 1
```

#### `key in tree`
Check if key exists.

**Returns:** `bool`

**Example:**
```python
if 1 in tree:
    print("Key 1 exists")
```

#### `len(tree)`
Get number of items.

**Returns:** `int`

**Example:**
```python
count = len(tree)
```

#### `bool(tree)`
Check if tree is non-empty.

**Returns:** `bool`

**Example:**
```python
if tree:
    print("Tree has items")
```

---

### Dictionary Methods

#### `get(key, default=None)`
Get value with optional default.

**Parameters:**
- `key`: The key to look up
- `default`: Value to return if key not found

**Returns:** Value associated with key, or default

**Example:**
```python
value = tree.get(1, "not found")
```

#### `pop(key, *args)`
Remove and return value for key.

**Parameters:**
- `key`: The key to remove
- `*args`: Optional default value if key not found

**Returns:** Value that was associated with key, or default

**Raises:** `KeyError` if key not found and no default provided

**Example:**
```python
value = tree.pop(1)                    # Raises KeyError if not found
value = tree.pop(1, "default")         # Returns "default" if not found
```

#### `popitem()`
Remove and return an arbitrary (key, value) pair.

**Returns:** `tuple` of (key, value)

**Raises:** `KeyError` if tree is empty

**Note:** In B+ trees, this returns the first (smallest) key-value pair.

**Example:**
```python
key, value = tree.popitem()
```

#### `setdefault(key, default=None)`
Get value for key, setting default if not present.

**Parameters:**
- `key`: The key to look up
- `default`: Value to set and return if key not found

**Returns:** Existing value for key, or default if key was not present

**Example:**
```python
value = tree.setdefault(1, "default")  # Sets and returns "default" if key 1 doesn't exist
```

#### `update(other)`
Update tree with key-value pairs from another mapping or iterable.

**Parameters:**
- `other`: Can be:
  - A mapping (dict-like object with `items()` method)
  - An object with `keys()` method
  - An iterable of (key, value) pairs

**Example:**
```python
tree.update({1: "one", 2: "two"})                    # From dict
tree.update(other_tree)                               # From another BPlusTreeMap
tree.update([(3, "three"), (4, "four")])            # From list of pairs
```

#### `copy()`
Create a shallow copy of the tree.

**Returns:** New `BPlusTreeMap` with same key-value pairs

**Example:**
```python
new_tree = tree.copy()
```

#### `clear()`
Remove all items from the tree.

**Example:**
```python
tree.clear()
assert len(tree) == 0
```

---

## Iteration Methods

#### `keys(start_key=None, end_key=None)`
Return iterator over keys in the given range.

**Parameters:**
- `start_key` (optional): Start of range (inclusive)
- `end_key` (optional): End of range (exclusive)

**Returns:** Iterator over keys

**Example:**
```python
for key in tree.keys():
    print(key)

for key in tree.keys(5, 10):  # Keys from 5 to 9
    print(key)
```

#### `values(start_key=None, end_key=None)`
Return iterator over values in the given range.

**Parameters:**
- `start_key` (optional): Start of range (inclusive)
- `end_key` (optional): End of range (exclusive)

**Returns:** Iterator over values

**Example:**
```python
for value in tree.values():
    print(value)
```

#### `items(start_key=None, end_key=None)`
Return iterator over (key, value) pairs in the given range.

**Parameters:**
- `start_key` (optional): Start of range (inclusive)
- `end_key` (optional): End of range (exclusive)

**Returns:** Iterator over (key, value) tuples

**Example:**
```python
for key, value in tree.items():
    print(f"{key}: {value}")

for key, value in tree.items(5, 10):  # Items with keys 5-9
    print(f"{key}: {value}")
```

---

## Range Query Methods

#### `range(start_key, end_key)`
Return iterator over (key, value) pairs in the specified range.

**Parameters:**
- `start_key`: Start of range (inclusive). Use `None` for beginning of tree.
- `end_key`: End of range (exclusive). Use `None` for end of tree.

**Returns:** Iterator over (key, value) tuples

**Example:**
```python
# Range with both bounds
for key, value in tree.range(5, 10):
    print(f"{key}: {value}")

# Open-ended ranges
for key, value in tree.range(10, None):      # From 10 to end
    print(f"{key}: {value}")

for key, value in tree.range(None, 10):     # From beginning to 10
    print(f"{key}: {value}")

# Full range
for key, value in tree.range(None, None):
    print(f"{key}: {value}")
```

---

## Properties

#### `capacity`
Get the node capacity of the tree.

**Returns:** `int`

**Example:**
```python
print(f"Tree capacity: {tree.capacity}")
```

#### `root`
Access to the root node (for advanced use).

**Returns:** Root node object

**Note:** This exposes internal tree structure. Use with caution.

#### `leaves`
Access to the leftmost leaf node (for advanced use).

**Returns:** Leftmost leaf node

**Note:** This exposes internal tree structure. Use with caution.

---

## Class Methods

#### `from_sorted_items(items, capacity=128)`
Bulk load from sorted key-value pairs for faster construction.

**Parameters:**
- `items`: Iterable of (key, value) pairs that MUST be sorted by key
- `capacity`: Node capacity

**Returns:** `BPlusTreeMap` instance with loaded data

**Performance:** 3-5x faster than individual insertions for large datasets

**Example:**
```python
sorted_data = [(1, "one"), (2, "two"), (3, "three")]
tree = BPlusTreeMap.from_sorted_items(sorted_data, capacity=64)
```

---

## Performance Characteristics

### Time Complexity
- **Lookup**: O(log n)
- **Insertion**: O(log n)
- **Deletion**: O(log n)
- **Range query**: O(log n + k) where k = number of items in range
- **Iteration**: O(n) with excellent cache locality

### Space Complexity
- **Memory**: O(n) with good cache efficiency due to node locality

### When to Use B+ Tree vs Alternatives

**Choose B+ Tree when:**
- ✅ Need range queries
- ✅ Frequently iterate in sorted order
- ✅ Large datasets (1000+ items)
- ✅ Database-like access patterns
- ✅ "Top N" or pagination queries

**Choose dict when:**
- ❌ Mostly random single-key lookups
- ❌ Very small datasets (< 100 items)
- ❌ Memory is extremely constrained
- ❌ Keys are not orderable

---

## Error Handling

### Exceptions

#### `BPlusTreeError`
Base exception for B+ tree operations.

#### `InvalidCapacityError`
Raised when invalid capacity is specified (< 4).

#### `KeyError`
Raised when accessing non-existent keys (standard Python behavior).

#### `TypeError` 
Raised when keys cannot be compared (e.g., mixing incompatible types).

---

## Threading and Concurrency

**Thread Safety:** BPlusTreeMap is **NOT thread-safe**. Use external synchronization (locks) when accessing from multiple threads.

**Example:**
```python
import threading

tree = BPlusTreeMap()
tree_lock = threading.Lock()

def safe_insert(key, value):
    with tree_lock:
        tree[key] = value
```

---

## Performance Tuning

### Capacity Selection
- **Small datasets (< 1K items)**: capacity=8-16
- **Medium datasets (1K-100K items)**: capacity=32-64 (default)
- **Large datasets (> 100K items)**: capacity=64-128

### Memory Usage
- Higher capacity = fewer tree levels = less memory overhead
- Lower capacity = more tree levels = more memory overhead
- Optimal capacity depends on key size and access patterns

### Range Query Optimization
- Use specific ranges instead of full iteration when possible
- Early termination with break statements is very efficient
- Consider bulk loading with `from_sorted_items()` for initialization

---

## Examples and Use Cases

See the examples directory for comprehensive usage examples:
- `basic_usage.py` - Fundamental operations
- `range_queries.py` - Range query patterns
- `performance_demo.py` - Performance comparisons
- `migration_guide.py` - Migration from dict/SortedDict