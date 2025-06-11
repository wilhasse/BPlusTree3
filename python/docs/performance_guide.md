# Performance Guide

## When to Use B+ Tree vs Alternatives

### B+ Tree Strengths

BPlusTreeMap excels in these scenarios:

1. **Ordered Operations**

   - Need to iterate items in sorted order
   - Frequent range queries
   - Finding min/max values
   - Time-series data with timestamp keys

2. **Predictable Performance**

   - Consistent O(log n) operations
   - No hash collision issues
   - Stable memory layout

3. **Large Datasets with Range Access**
   - Database-like workloads
   - Log processing with time ranges
   - Leaderboards and rankings

### When to Use Alternatives

| Use Case                    | Recommended       | Why                       |
| --------------------------- | ----------------- | ------------------------- |
| Random access only          | `dict`            | O(1) average case         |
| Need ordering + O(1) access | `OrderedDict`     | Maintains insertion order |
| Small datasets (<100 items) | `dict`            | Lower overhead            |
| Thread-safe operations      | `queue.Queue`     | Built-in thread safety    |
| Persistent storage          | Database (SQLite) | ACID guarantees           |

## Performance Characteristics

### Time Complexity

| Operation          | BPlusTreeMap | dict       | Comment         |
| ------------------ | ------------ | ---------- | --------------- |
| Insert             | O(log n)     | O(1)\*     | \*amortized     |
| Lookup             | O(log n)     | O(1)\*     | \*average case  |
| Delete             | O(log n)     | O(1)\*     | \*average case  |
| Iteration (sorted) | O(n)         | O(n log n) | B+ Tree wins    |
| Range query        | O(log n + k) | O(n)       | k = result size |
| Min/Max            | O(log n)     | O(n)       | B+ Tree wins    |

### Space Complexity

- BPlusTreeMap: O(n) with higher constant factor
- dict: O(n) with lower constant factor

B+ Trees use more memory due to:

- Node structure overhead
- Partially filled nodes
- Parent/child pointers

## Optimization Strategies

### 1. Capacity Tuning

The `capacity` parameter controls node size. Larger nodes mean:

- Fewer levels (shallower tree)
- Better cache locality
- More memory usage

```python
# Benchmarking different capacities
import time

def benchmark_capacity(size, capacity):
    tree = BPlusTreeMap(capacity=capacity)

    start = time.perf_counter()
    for i in range(size):
        tree[i] = i
    insert_time = time.perf_counter() - start

    start = time.perf_counter()
    for i in range(size):
        _ = tree[i]
    lookup_time = time.perf_counter() - start

    return insert_time, lookup_time

# Test different capacities
for cap in [8, 16, 32, 64, 128]:
    ins, look = benchmark_capacity(100000, cap)
    print(f"Capacity {cap}: Insert={ins:.3f}s, Lookup={look:.3f}s")
```

**Recommendations:**

- Small datasets (<1,000): capacity=8 (default)
- Medium datasets (1,000-100,000): capacity=32
- Large datasets (>100,000): capacity=64-128
- Range-heavy workloads: capacity=128+

### 2. Batch Operations

Minimize tree traversals by batching operations:

```python
# Slower: Individual operations
tree = BPlusTreeMap()
for i in range(10000):
    if i not in tree:
        tree[i] = compute_value(i)

# Faster: Batch check and insert
tree = BPlusTreeMap()
to_insert = []
for i in range(10000):
    to_insert.append((i, compute_value(i)))
tree.update(to_insert)
```

### 3. Key Design

Key choice significantly impacts performance:

```python
# Integer keys: Fastest
tree[12345] = value

# String keys: Good performance
tree["user:12345"] = value

# Tuple keys: Slower but useful for composite keys
tree[(2024, 1, 15, "event")] = value

# Object keys: Slowest (if hashable)
tree[custom_object] = value
```

**Tips:**

- Use integers when possible
- Keep string keys short
- Avoid complex objects as keys

### 4. Access Patterns

Structure your code to minimize tree traversals:

```python
# Inefficient: Multiple lookups
if key in tree:
    value = tree[key]
    process(value)

# Efficient: Single lookup with exception handling
try:
    value = tree[key]
    process(value)
except KeyError:
    pass

# Or use get() for default values
value = tree.get(key)
if value is not None:
    process(value)
```

### 5. Range Query Optimization

```python
# Inefficient: Filter all items
results = []
for k, v in tree.items():
    if start <= k <= end:
        results.append((k, v))

# Efficient: Use range query
results = list(tree.items(start, end + 1))

# Most efficient: Process during iteration
for k, v in tree.items(start, end + 1):
    process(k, v)  # Avoids building intermediate list
```

## Benchmarking Your Use Case

Always benchmark with your actual data and access patterns:

```python
import time
import random
from bplustree import BPlusTreeMap

def benchmark_implementation(impl_class, data, operations):
    """Benchmark any dict-like implementation."""
    impl = impl_class()

    # Insertion
    start = time.perf_counter()
    for k, v in data:
        impl[k] = v
    insert_time = time.perf_counter() - start

    # Random lookups
    keys = [k for k, _ in data]
    random.shuffle(keys)
    start = time.perf_counter()
    for k in keys[:operations]:
        _ = impl.get(k)
    lookup_time = time.perf_counter() - start

    # Ordered iteration
    start = time.perf_counter()
    if hasattr(impl, 'items'):
        _ = list(impl.items())
    else:
        _ = sorted(impl.items())
    iter_time = time.perf_counter() - start

    return {
        'insert': insert_time,
        'lookup': lookup_time,
        'iteration': iter_time
    }

# Compare implementations
test_data = [(random.randint(0, 1000000), f"value_{i}")
             for i in range(10000)]

results = {
    'BPlusTreeMap': benchmark_implementation(BPlusTreeMap, test_data, 1000),
    'dict': benchmark_implementation(dict, test_data, 1000),
}

for name, times in results.items():
    print(f"\n{name}:")
    for op, t in times.items():
        print(f"  {op}: {t:.4f}s")
```

## Memory Optimization

### Understanding Memory Usage

```python
import sys
from bplustree import BPlusTreeMap

# Measure memory usage
tree = BPlusTreeMap()
base_size = sys.getsizeof(tree)

# Add items and measure growth
sizes = []
for i in range(0, 10000, 1000):
    for j in range(1000):
        tree[i + j] = f"value_{i + j}"
    sizes.append((len(tree), sys.getsizeof(tree)))

# Note: This only measures the tree object itself,
# not the nodes it references
```

### Memory-Efficient Patterns

1. **Reuse trees instead of creating new ones:**

   ```python
   # Inefficient
   def process_batch(items):
       tree = BPlusTreeMap()
       tree.update(items)
       return tree

   # Efficient
   tree = BPlusTreeMap()
   def process_batch(items):
       tree.clear()
       tree.update(items)
       return tree
   ```

2. **Use smaller capacity for small datasets:**

   ```python
   # Wasteful for small data
   small_tree = BPlusTreeMap(capacity=128)

   # Better
   small_tree = BPlusTreeMap(capacity=4)
   ```

## C Extension Performance

The C extension provides significant performance improvements:

```python
from bplustree import get_implementation

print(f"Using: {get_implementation()}")

# Force pure Python for comparison
import os
os.environ['BPLUSTREE_PURE_PYTHON'] = '1'
# Reimport to get pure Python version
```

Typical speedups with C extension:

- Insertion: 2-3x faster
- Lookup: 2-4x faster
- Iteration: 1.5-2x faster
- Memory usage: Similar

## Performance Pitfalls

### 1. Comparing Different Types

```python
# Slow: comparing different types
tree[1] = "value"
tree["1"] = "other"  # Different key!
result = tree.get(1.0)  # Type conversion overhead
```

### 2. Excessive Tree Modifications During Iteration

```python
# Dangerous: modifying during iteration
for key in list(tree.keys()):  # Create list first!
    if should_delete(key):
        del tree[key]
```

### 3. Using B+ Tree for Small, Static Data

```python
# Overkill for small, static data
static_map = BPlusTreeMap()
static_map.update({
    'yes': True,
    'no': False,
    'maybe': None
})

# Better: just use dict
static_map = {'yes': True, 'no': False, 'maybe': None}
```

## Real-World Performance Examples

### Time-Series Data

```python
# Storing 1 million time-series points
# B+ Tree: ~0.5s insert, ~0.001s range query
# dict: ~0.1s insert, ~0.1s range query (full scan)
```

### Log Processing

```python
# Processing 10GB of logs with timestamp ordering
# B+ Tree: Maintains order during insert
# dict: Requires expensive sort at the end
```

### Cache with Expiration

```python
# LRU cache with 100k entries
# B+ Tree: O(log n) to find/remove oldest
# OrderedDict: O(1) with move_to_end()
# Choose OrderedDict for pure LRU
# Choose B+ Tree if you need range queries
```

## Monitoring Performance

```python
import cProfile
import pstats
from io import StringIO

def profile_btree_operations():
    tree = BPlusTreeMap(capacity=32)

    # Various operations to profile
    for i in range(10000):
        tree[i] = f"value_{i}"

    for i in range(0, 10000, 100):
        _ = tree.get(i)

    list(tree.items(1000, 2000))

# Profile the operations
profiler = cProfile.Profile()
profiler.enable()
profile_btree_operations()
profiler.disable()

# Print results
s = StringIO()
ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
ps.print_stats(10)  # Top 10 functions
print(s.getvalue())
```

## Summary

- B+ Trees excel at ordered operations and range queries
- Choose capacity based on dataset size
- Batch operations when possible
- Use integer keys for best performance
- Profile with your actual data and access patterns
- Consider the C extension for performance-critical applications
