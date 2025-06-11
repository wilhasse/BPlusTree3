# Quickstart Guide

Get up and running with BPlusTree in 5 minutes!

## Basic Usage

### Creating a B+ Tree

```python
from bplus_tree import BPlusTreeMap

# Create an empty tree
tree = BPlusTreeMap()

# Create with custom node capacity (default is 8)
tree = BPlusTreeMap(capacity=32)
```

### Adding Items

```python
# Add single items
tree[1] = "apple"
tree[2] = "banana"
tree[3] = "cherry"

# Add multiple items
items = {4: "date", 5: "elderberry", 6: "fig"}
tree.update(items)
```

### Retrieving Items

```python
# Get a value
value = tree[3]  # "cherry"

# Get with default
value = tree.get(10, "not found")  # "not found"

# Check if key exists
if 5 in tree:
    print(f"Found: {tree[5]}")
```

### Removing Items

```python
# Remove single item
del tree[2]

# Remove and return value
value = tree.pop(4)  # "date"
value = tree.pop(10, "default")  # "default" (key doesn't exist)

# Remove arbitrary item
key, value = tree.popitem()  # Removes and returns any (key, value) pair

# Clear all items
tree.clear()
```

## Iteration and Ordering

B+ Trees maintain items in sorted order, making them perfect for ordered operations:

```python
tree = BPlusTreeMap()
for i in [5, 2, 8, 1, 9, 3]:
    tree[i] = f"value_{i}"

# Iterate in sorted order
for key, value in tree.items():
    print(f"{key}: {value}")
# Output:
# 1: value_1
# 2: value_2
# 3: value_3
# 5: value_5
# 8: value_8
# 9: value_9

# Get all keys (sorted)
keys = list(tree.keys())  # [1, 2, 3, 5, 8, 9]

# Get all values (in key order)
values = list(tree.values())  # ['value_1', 'value_2', ...]
```

## Range Queries

One of the key advantages of B+ Trees is efficient range queries:

```python
tree = BPlusTreeMap()
for i in range(100):
    tree[i] = f"item_{i}"

# Get items in range [20, 30)
for key, value in tree.items(20, 30):
    print(f"{key}: {value}")

# Get all items >= 50
for key, value in tree.items(50):
    print(f"{key}: {value}")

# Get all items < 10
for key, value in tree.items(end_key=10):
    print(f"{key}: {value}")
```

## Common Patterns

### Using as a Cache with Ordering

```python
class OrderedCache:
    def __init__(self, max_size=1000):
        self.cache = BPlusTreeMap()
        self.max_size = max_size

    def put(self, key, value):
        self.cache[key] = value
        # Remove oldest entries if over limit
        while len(self.cache) > self.max_size:
            self.cache.popitem()  # Removes smallest key

    def get(self, key, default=None):
        return self.cache.get(key, default)

    def get_range(self, start, end):
        return list(self.cache.items(start, end))
```

### Time-Series Data

```python
from datetime import datetime
import time

# Store time-series data
timeseries = BPlusTreeMap()

# Add readings
for i in range(10):
    timestamp = datetime.now().timestamp()
    timeseries[timestamp] = {"temperature": 20 + i, "humidity": 50 + i}
    time.sleep(0.1)

# Query recent data
one_minute_ago = datetime.now().timestamp() - 60
recent_data = list(timeseries.items(one_minute_ago))
```

### Dictionary Replacement

```python
# B+ Tree as a drop-in dict replacement
data = BPlusTreeMap()

# All dict operations work
data["name"] = "Alice"
data["age"] = 30
data.update({"city": "New York", "country": "USA"})

# But with ordering!
for key in sorted(data.keys()):
    print(f"{key}: {data[key]}")
```

## Performance Tips

### 1. Choose the Right Capacity

```python
# Small datasets (< 1000 items)
small_tree = BPlusTreeMap(capacity=8)  # Default

# Medium datasets (1000-100,000 items)
medium_tree = BPlusTreeMap(capacity=32)

# Large datasets (> 100,000 items)
large_tree = BPlusTreeMap(capacity=128)
```

### 2. Batch Operations

```python
# Slower: individual insertions
for i in range(10000):
    tree[i] = i

# Faster: batch update
tree.update((i, i) for i in range(10000))
```

### 3. Use Range Queries

```python
# Slower: filter all items
result = [(k, v) for k, v in tree.items() if 100 <= k <= 200]

# Faster: use range query
result = list(tree.items(100, 201))
```

## Comparison with dict

| Operation         | dict         | BPlusTreeMap |
| ----------------- | ------------ | ------------ |
| Insert            | O(1) average | O(log n)     |
| Lookup            | O(1) average | O(log n)     |
| Delete            | O(1) average | O(log n)     |
| Ordered iteration | O(n log n)   | O(n)         |
| Range query       | O(n)         | O(log n + k) |
| Memory            | Lower        | Higher       |

Use BPlusTreeMap when you need:

- Ordered iteration
- Range queries
- Sorted keys
- Predictable performance

Use dict when you need:

- Fastest possible random access
- Minimal memory usage
- No ordering requirements

## Error Handling

```python
tree = BPlusTreeMap()

# KeyError on missing key
try:
    value = tree[999]
except KeyError:
    print("Key not found")

# Safe access with get()
value = tree.get(999, "default")

# Check before access
if 999 in tree:
    value = tree[999]
```

## Next Steps

- Explore [Advanced Usage](advanced_usage.md) for performance tuning
- See [API Reference](API_REFERENCE.md) for complete method documentation
- Read [Performance Guide](performance_guide.md) for optimization strategies
- Check [Examples](../examples/) for real-world use cases
