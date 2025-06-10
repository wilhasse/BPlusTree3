# Migration Guide

## Migrating from dict

BPlusTreeMap implements the full dict interface, making migration straightforward:

### Basic Migration

```python
# Before: Using dict
data = {}
data['key'] = 'value'
value = data.get('key', 'default')
del data['key']

# After: Using BPlusTreeMap
from bplus_tree import BPlusTreeMap
data = BPlusTreeMap()
data['key'] = 'value'
value = data.get('key', 'default')
del data['key']
```

### Key Differences

1. **Ordered Iteration**
   ```python
   # dict: arbitrary order (Python 3.7+ maintains insertion order)
   d = {'c': 3, 'a': 1, 'b': 2}
   list(d.keys())  # ['c', 'a', 'b']
   
   # BPlusTreeMap: always sorted by key
   tree = BPlusTreeMap()
   tree.update({'c': 3, 'a': 1, 'b': 2})
   list(tree.keys())  # ['a', 'b', 'c']
   ```

2. **Performance Characteristics**
   ```python
   # dict: O(1) average case
   d[key] = value  # Very fast
   
   # BPlusTreeMap: O(log n)
   tree[key] = value  # Slightly slower, but predictable
   ```

3. **Memory Usage**
   - dict: Lower memory overhead
   - BPlusTreeMap: Higher memory due to tree structure

### Migration Checklist

- [x] Replace `dict()` with `BPlusTreeMap()`
- [x] No code changes needed for basic operations
- [ ] Review performance-critical sections
- [ ] Add capacity parameter for large datasets
- [ ] Utilize range queries where beneficial

## Migrating from OrderedDict

```python
from collections import OrderedDict
# Before
od = OrderedDict()
od['b'] = 2
od['a'] = 1
od.move_to_end('b')  # Not available in BPlusTreeMap

# After
from bplus_tree import BPlusTreeMap
tree = BPlusTreeMap()
tree['b'] = 2
tree['a'] = 1
# Items automatically sorted by key, not insertion order
```

### Key Differences

| Feature | OrderedDict | BPlusTreeMap |
|---------|-------------|--------------|
| Order | Insertion order | Key order |
| move_to_end() | ✓ | ✗ |
| popitem(last=False) | ✓ | ✗ (always smallest) |
| Reversible | ✓ | ✗ |

### When to Keep OrderedDict

Keep OrderedDict if you need:
- Insertion order preservation
- move_to_end() for LRU caches
- Reverse iteration

## Migrating from sortedcontainers.SortedDict

BPlusTreeMap is designed as a drop-in replacement for SortedDict in most cases:

```python
# Before: Using SortedDict
from sortedcontainers import SortedDict
sd = SortedDict()
sd['key'] = 'value'
items = list(sd.items())  # Sorted

# After: Using BPlusTreeMap
from bplus_tree import BPlusTreeMap
tree = BPlusTreeMap()
tree['key'] = 'value'
items = list(tree.items())  # Also sorted
```

### API Compatibility

| Method | SortedDict | BPlusTreeMap | Notes |
|--------|------------|--------------|-------|
| Basic dict API | ✓ | ✓ | Fully compatible |
| items(start, end) | ✗ | ✓ | Range queries |
| irange() | ✓ | ✗ | Use items(start, end) |
| bisect_left/right() | ✓ | ✗ | Not implemented |
| iloc[] | ✓ | ✗ | No index access |

### Migration Example

```python
# SortedDict with irange
from sortedcontainers import SortedDict
sd = SortedDict((i, i**2) for i in range(100))
for key in sd.irange(10, 20):
    print(f"{key}: {sd[key]}")

# BPlusTreeMap equivalent
from bplus_tree import BPlusTreeMap
tree = BPlusTreeMap()
tree.update((i, i**2) for i in range(100))
for key, value in tree.items(10, 21):  # Note: end is exclusive
    print(f"{key}: {value}")
```

### Performance Comparison

| Operation | SortedDict | BPlusTreeMap |
|-----------|------------|--------------|
| Insert | O(log n) | O(log n) |
| Delete | O(log n) | O(log n) |
| Lookup | O(log n) | O(log n) |
| Range query | O(log n + k) | O(log n + k) |
| Memory | Moderate | Higher |

## Migrating from Database Queries

B+ Trees can replace simple database queries for in-memory data:

### Before: SQLite
```python
import sqlite3

conn = sqlite3.connect(':memory:')
c = conn.cursor()
c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)')
c.execute('CREATE INDEX idx_age ON users(age)')

# Insert
c.execute('INSERT INTO users VALUES (?, ?, ?)', (1, 'Alice', 30))

# Range query
c.execute('SELECT * FROM users WHERE age BETWEEN ? AND ?', (25, 35))
results = c.fetchall()
```

### After: BPlusTreeMap
```python
from bplus_tree import BPlusTreeMap

# Using age as key for range queries
users_by_age = BPlusTreeMap()
users_by_age[30] = {'id': 1, 'name': 'Alice', 'age': 30}

# Range query
results = list(users_by_age.items(25, 36))  # end is exclusive
```

### Multiple Indexes
```python
# Maintain multiple B+ Trees for different access patterns
users_by_id = BPlusTreeMap()
users_by_age = BPlusTreeMap()
users_by_name = BPlusTreeMap()

def add_user(id, name, age):
    user = {'id': id, 'name': name, 'age': age}
    users_by_id[id] = user
    users_by_age[age] = user
    users_by_name[name] = user

# Fast lookup by any field
user = users_by_name.get('Alice')
age_range = list(users_by_age.items(25, 36))
```

## Common Migration Patterns

### 1. Time-Series Data
```python
# Before: List with binary search
import bisect
from datetime import datetime

timestamps = []
values = []

def add_reading(timestamp, value):
    idx = bisect.bisect_left(timestamps, timestamp)
    timestamps.insert(idx, timestamp)
    values.insert(idx, value)

# After: BPlusTreeMap
readings = BPlusTreeMap()

def add_reading(timestamp, value):
    readings[timestamp] = value  # Automatically sorted

# Query time range
start = datetime(2024, 1, 1).timestamp()
end = datetime(2024, 1, 2).timestamp()
day_readings = list(readings.items(start, end))
```

### 2. Leaderboard/Ranking
```python
# Before: Sorted list with manual management
scores = []  # [(score, player), ...]

def add_score(player, score):
    scores.append((score, player))
    scores.sort(reverse=True)

def get_top_n(n):
    return scores[:n]

# After: BPlusTreeMap (note: for reverse order, negate scores)
leaderboard = BPlusTreeMap()

def add_score(player, score):
    # Negative score for descending order
    leaderboard[-score] = player

def get_top_n(n):
    return [(player, -score) for score, player in 
            itertools.islice(leaderboard.items(), n)]
```

### 3. Cache with Range Expiration
```python
# Before: Dict with periodic cleanup
import time
cache = {}

def set_with_ttl(key, value, ttl):
    cache[key] = (value, time.time() + ttl)

def cleanup():
    now = time.time()
    expired = [k for k, (_, exp) in cache.items() if exp < now]
    for k in expired:
        del cache[k]

# After: BPlusTreeMap indexed by expiration
from bplus_tree import BPlusTreeMap
cache_by_key = {}
cache_by_expiry = BPlusTreeMap()

def set_with_ttl(key, value, ttl):
    expiry = time.time() + ttl
    cache_by_key[key] = (value, expiry)
    cache_by_expiry[expiry] = key

def cleanup():
    now = time.time()
    # Efficiently remove all expired items
    for expiry, key in cache_by_expiry.items(end_key=now):
        del cache_by_key[key]
        del cache_by_expiry[expiry]
```

## Testing After Migration

Always test thoroughly after migration:

```python
import unittest
from bplus_tree import BPlusTreeMap

class TestMigration(unittest.TestCase):
    def test_basic_operations(self):
        # Test all operations your code uses
        tree = BPlusTreeMap()
        
        # Test insertion
        tree['key'] = 'value'
        self.assertEqual(tree['key'], 'value')
        
        # Test update
        tree['key'] = 'new_value'
        self.assertEqual(tree['key'], 'new_value')
        
        # Test deletion
        del tree['key']
        self.assertNotIn('key', tree)
        
    def test_ordering(self):
        tree = BPlusTreeMap()
        tree.update({3: 'c', 1: 'a', 2: 'b'})
        
        # Verify sorted order
        keys = list(tree.keys())
        self.assertEqual(keys, [1, 2, 3])
        
    def test_range_queries(self):
        tree = BPlusTreeMap()
        tree.update((i, i**2) for i in range(100))
        
        # Test range query
        results = list(tree.items(10, 20))
        self.assertEqual(len(results), 10)
        self.assertEqual(results[0], (10, 100))
        self.assertEqual(results[-1], (19, 361))
```

## Performance Testing

Compare performance before and after migration:

```python
import time
import random

def benchmark_operations(implementation, size=10000):
    impl = implementation()
    data = [(random.randint(0, size*10), f"value_{i}") 
            for i in range(size)]
    
    # Insertion
    start = time.perf_counter()
    for k, v in data:
        impl[k] = v
    insert_time = time.perf_counter() - start
    
    # Lookup
    keys = [k for k, _ in data]
    random.shuffle(keys)
    start = time.perf_counter()
    for k in keys[:1000]:
        _ = impl.get(k)
    lookup_time = time.perf_counter() - start
    
    # Iteration
    start = time.perf_counter()
    _ = list(impl.items())
    iter_time = time.perf_counter() - start
    
    return insert_time, lookup_time, iter_time

# Compare implementations
dict_times = benchmark_operations(dict)
btree_times = benchmark_operations(BPlusTreeMap)

print(f"dict: insert={dict_times[0]:.3f}, lookup={dict_times[1]:.3f}, iter={dict_times[2]:.3f}")
print(f"BPlusTreeMap: insert={btree_times[0]:.3f}, lookup={btree_times[1]:.3f}, iter={btree_times[2]:.3f}")
```

## Rollback Plan

If migration causes issues:

1. **Feature flag approach:**
   ```python
   USE_BTREE = os.environ.get('USE_BTREE', 'false').lower() == 'true'
   
   if USE_BTREE:
       from bplus_tree import BPlusTreeMap as DataStore
   else:
       DataStore = dict
   
   data = DataStore()
   ```

2. **Gradual migration:**
   - Migrate one component at a time
   - Monitor performance and correctness
   - Keep old code for easy rollback

3. **Compatibility wrapper:**
   ```python
   class CompatibleBPlusTree(BPlusTreeMap):
       """Add missing methods for compatibility"""
       
       def move_to_end(self, key):
           # Simulate OrderedDict.move_to_end
           value = self.pop(key)
           self[key] = value
   ```

## Summary

- BPlusTreeMap is a drop-in replacement for dict in most cases
- Main benefit: automatic sorting and efficient range queries
- Main cost: slightly slower random access
- Always benchmark with your specific use case
- Consider gradual migration for large codebases