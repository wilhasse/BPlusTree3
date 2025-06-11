# Advanced Usage Guide

## Capacity Tuning

The `capacity` parameter is the most important performance tuning knob for B+ Trees.

### Understanding Capacity

Capacity controls the maximum number of items stored in each node:

- **Higher capacity**: Fewer tree levels, better cache locality, more memory per node
- **Lower capacity**: More tree levels, less memory per node, more pointer overhead

### Capacity Selection Strategy

```python
from bplustree import BPlusTreeMap
import time

def benchmark_capacity(size, capacity):
    """Benchmark different capacities for a given dataset size."""
    tree = BPlusTreeMap(capacity=capacity)

    # Time insertions
    start = time.perf_counter()
    for i in range(size):
        tree[i] = f"value_{i}"
    insert_time = time.perf_counter() - start

    # Time lookups
    start = time.perf_counter()
    for i in range(0, size, 10):
        _ = tree[i]
    lookup_time = time.perf_counter() - start

    return insert_time, lookup_time

# Test different capacities
dataset_size = 100000
capacities = [8, 16, 32, 64, 128, 256]

for cap in capacities:
    ins_time, look_time = benchmark_capacity(dataset_size, cap)
    print(f"Capacity {cap:3d}: Insert={ins_time:.3f}s, Lookup={look_time:.3f}s")
```

### Recommended Capacities by Use Case

| Use Case           | Dataset Size  | Recommended Capacity | Rationale            |
| ------------------ | ------------- | -------------------- | -------------------- |
| Configuration data | <100 items    | 4-8                  | Minimize memory      |
| User sessions      | 100-1K items  | 8-16                 | Balanced             |
| Product catalog    | 1K-100K items | 32-64                | Performance focus    |
| Time-series data   | >100K items   | 64-128               | Cache efficiency     |
| Log processing     | >1M items     | 128-256              | Minimize tree height |

## Memory Optimization

### Understanding Memory Usage

```python
import sys
from bplustree import BPlusTreeMap

def analyze_memory_usage():
    """Analyze memory usage patterns."""
    tree = BPlusTreeMap(capacity=32)

    # Measure baseline
    baseline = sys.getsizeof(tree)
    print(f"Empty tree: {baseline} bytes")

    # Measure growth
    sizes = []
    for i in range(0, 10000, 1000):
        # Add 1000 items
        for j in range(1000):
            tree[i + j] = f"value_{i + j}"

        # Measure current size (approximate)
        current_size = sys.getsizeof(tree)
        sizes.append((len(tree), current_size))
        print(f"Items: {len(tree):5d}, Size: {current_size:6d} bytes, "
              f"Per item: {current_size / len(tree):.2f} bytes")

analyze_memory_usage()
```

### Memory-Efficient Patterns

1. **Reuse Trees Instead of Creating New Ones**

   ```python
   # Inefficient: Creates many trees
   def process_batches(batches):
       results = []
       for batch in batches:
           tree = BPlusTreeMap()
           tree.update(batch)
           results.append(tree)
       return results

   # Efficient: Reuse single tree
   tree = BPlusTreeMap()
   def process_batches(batches):
       results = []
       for batch in batches:
           tree.clear()
           tree.update(batch)
           results.append(tree.copy())  # Only copy when needed
       return results
   ```

2. **Choose Appropriate Key Types**

   ```python
   # Memory-heavy: String keys
   tree_strings = BPlusTreeMap()
   for i in range(10000):
       tree_strings[f"key_{i:06d}"] = i

   # Memory-light: Integer keys
   tree_ints = BPlusTreeMap()
   for i in range(10000):
       tree_ints[i] = i

   # Memory usage: integers use ~70% less memory than strings
   ```

3. **Optimal Capacity for Memory**

   ```python
   # For memory-constrained environments
   small_tree = BPlusTreeMap(capacity=8)

   # For performance-critical applications
   fast_tree = BPlusTreeMap(capacity=128)
   ```

## Performance Optimization

### Batch Operations

```python
import random
import time

def compare_insertion_methods(size=10000):
    """Compare different insertion methods."""
    data = [(i, f"value_{i}") for i in range(size)]

    # Method 1: Individual insertions
    tree1 = BPlusTreeMap()
    start = time.perf_counter()
    for key, value in data:
        tree1[key] = value
    individual_time = time.perf_counter() - start

    # Method 2: Batch update
    tree2 = BPlusTreeMap()
    start = time.perf_counter()
    tree2.update(data)
    batch_time = time.perf_counter() - start

    print(f"Individual insertions: {individual_time:.3f}s")
    print(f"Batch update: {batch_time:.3f}s")
    print(f"Speedup: {individual_time / batch_time:.2f}x")

compare_insertion_methods()
```

### Range Query Optimization

```python
def optimize_range_queries():
    """Demonstrate range query optimization techniques."""
    tree = BPlusTreeMap()
    tree.update((i, i**2) for i in range(100000))

    # Inefficient: Filter all items
    start = time.perf_counter()
    results1 = [(k, v) for k, v in tree.items() if 1000 <= k < 2000]
    filter_time = time.perf_counter() - start

    # Efficient: Use range query
    start = time.perf_counter()
    results2 = list(tree.items(1000, 2000))
    range_time = time.perf_counter() - start

    print(f"Filter all: {filter_time:.4f}s")
    print(f"Range query: {range_time:.4f}s")
    print(f"Speedup: {filter_time / range_time:.2f}x")

    assert results1 == results2  # Same results

optimize_range_queries()
```

### Iterator Optimization

```python
def optimize_iteration():
    """Optimize iteration patterns."""
    tree = BPlusTreeMap()
    tree.update((i, f"value_{i}") for i in range(50000))

    # Inefficient: Convert to list for processing
    start = time.perf_counter()
    items = list(tree.items())
    for i, (key, value) in enumerate(items):
        if i % 10000 == 0:
            process_item(key, value)
    list_time = time.perf_counter() - start

    # Efficient: Process during iteration
    start = time.perf_counter()
    for i, (key, value) in enumerate(tree.items()):
        if i % 10000 == 0:
            process_item(key, value)
    iter_time = time.perf_counter() - start

    print(f"List conversion: {list_time:.4f}s")
    print(f"Direct iteration: {iter_time:.4f}s")

def process_item(key, value):
    # Simulate processing
    pass

optimize_iteration()
```

## Real-World Use Cases

### 1. Time-Series Database

```python
from datetime import datetime, timedelta
import random

class TimeSeriesDB:
    """Simple time-series database using B+ Tree."""

    def __init__(self):
        self.data = BPlusTreeMap(capacity=128)  # Large capacity for time data

    def insert(self, timestamp, value, tags=None):
        """Insert a time-series point."""
        key = self._make_key(timestamp, tags)
        self.data[key] = value

    def query_range(self, start_time, end_time, tags=None):
        """Query data in time range."""
        start_key = self._make_key(start_time, tags)
        end_key = self._make_key(end_time, tags)

        return list(self.data.items(start_key, end_key))

    def _make_key(self, timestamp, tags):
        """Create composite key from timestamp and tags."""
        if isinstance(timestamp, datetime):
            timestamp = timestamp.timestamp()

        if tags:
            # Include tags in key for filtering
            tag_str = "|".join(f"{k}={v}" for k, v in sorted(tags.items()))
            return (timestamp, tag_str)
        return (timestamp, "")

# Usage example
db = TimeSeriesDB()

# Insert data
base_time = datetime.now()
for i in range(10000):
    timestamp = base_time + timedelta(seconds=i)
    value = random.uniform(0, 100)
    tags = {"sensor": f"sensor_{i % 10}", "location": f"room_{i % 5}"}
    db.insert(timestamp, value, tags)

# Query last hour
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)
recent_data = db.query_range(start_time, end_time)
print(f"Found {len(recent_data)} recent readings")
```

### 2. Ordered Cache with TTL

```python
import time

class OrderedTTLCache:
    """Cache with TTL using B+ Tree for efficient expiration."""

    def __init__(self, max_size=10000, default_ttl=3600):
        self.data = {}  # key -> (value, expiry_time)
        self.expiry_index = BPlusTreeMap(capacity=64)  # expiry_time -> key
        self.max_size = max_size
        self.default_ttl = default_ttl

    def put(self, key, value, ttl=None):
        """Store a value with TTL."""
        if ttl is None:
            ttl = self.default_ttl

        expiry_time = time.time() + ttl

        # Remove old entry if exists
        if key in self.data:
            old_expiry = self.data[key][1]
            del self.expiry_index[old_expiry]

        # Add new entry
        self.data[key] = (value, expiry_time)
        self.expiry_index[expiry_time] = key

        # Cleanup if needed
        self._cleanup()
        self._enforce_size_limit()

    def get(self, key):
        """Get a value, returning None if expired or missing."""
        if key not in self.data:
            return None

        value, expiry_time = self.data[key]
        if time.time() > expiry_time:
            self._remove_key(key)
            return None

        return value

    def _cleanup(self):
        """Remove expired entries."""
        now = time.time()
        expired_keys = []

        # Find all expired entries efficiently
        for expiry_time, key in self.expiry_index.items(end_key=now):
            expired_keys.append(key)

        # Remove expired entries
        for key in expired_keys:
            self._remove_key(key)

    def _remove_key(self, key):
        """Remove a key from both indexes."""
        if key in self.data:
            _, expiry_time = self.data[key]
            del self.data[key]
            del self.expiry_index[expiry_time]

    def _enforce_size_limit(self):
        """Remove oldest entries if over size limit."""
        while len(self.data) > self.max_size:
            # Remove entry with earliest expiry time
            expiry_time, key = self.expiry_index.popitem()
            del self.data[key]

# Usage
cache = OrderedTTLCache(max_size=1000, default_ttl=60)

# Store values
cache.put("user:123", {"name": "Alice", "score": 95})
cache.put("user:456", {"name": "Bob", "score": 87}, ttl=30)  # Custom TTL

# Retrieve values
user = cache.get("user:123")
print(f"User: {user}")
```

### 3. Leaderboard System

```python
class Leaderboard:
    """Game leaderboard using B+ Tree for efficient ranking."""

    def __init__(self):
        # Use negative scores for descending order
        self.scores = BPlusTreeMap(capacity=32)
        self.players = {}  # player_id -> current_score

    def update_score(self, player_id, score):
        """Update a player's score."""
        # Remove old score if exists
        if player_id in self.players:
            old_score = self.players[player_id]
            del self.scores[-old_score, player_id]

        # Add new score (negative for descending order)
        self.scores[-score, player_id] = {"player_id": player_id, "score": score}
        self.players[player_id] = score

    def get_top_n(self, n=10):
        """Get top N players."""
        results = []
        for i, ((neg_score, player_id), data) in enumerate(self.scores.items()):
            if i >= n:
                break
            results.append((player_id, -neg_score))  # Convert back to positive
        return results

    def get_rank(self, player_id):
        """Get a player's current rank (1-indexed)."""
        if player_id not in self.players:
            return None

        player_score = self.players[player_id]
        rank = 1

        # Count players with higher scores
        for (neg_score, pid), _ in self.scores.items():
            if -neg_score > player_score:
                rank += 1
            elif pid == player_id:
                break

        return rank

    def get_players_in_score_range(self, min_score, max_score):
        """Get all players within a score range."""
        players = []

        # Convert to negative scores and reverse order
        start_key = (-max_score, "")  # Empty string sorts before any player_id
        end_key = (-min_score, "~")   # "~" sorts after any reasonable player_id

        for (neg_score, player_id), data in self.scores.items(start_key, end_key):
            if isinstance(player_id, str):  # Skip boundary markers
                players.append((player_id, -neg_score))

        return players

# Usage
leaderboard = Leaderboard()

# Add players
players_data = [
    ("alice", 95), ("bob", 87), ("charlie", 92), ("diana", 98),
    ("eve", 85), ("frank", 90), ("grace", 96), ("henry", 88)
]

for player_id, score in players_data:
    leaderboard.update_score(player_id, score)

# Get top 3
top_3 = leaderboard.get_top_n(3)
print(f"Top 3: {top_3}")

# Get rank for specific player
alice_rank = leaderboard.get_rank("alice")
print(f"Alice's rank: {alice_rank}")

# Players with scores 90-95
mid_range = leaderboard.get_players_in_score_range(90, 95)
print(f"Players scoring 90-95: {mid_range}")
```

## Debugging and Introspection

### Tree Structure Inspection

```python
def inspect_tree_structure(tree):
    """Inspect internal tree structure (pure Python only)."""
    if hasattr(tree, 'root'):
        print(f"Tree structure:")
        print(f"  Root type: {type(tree.root).__name__}")
        print(f"  Tree height: {_calculate_height(tree.root)}")
        print(f"  Number of nodes: {_count_nodes(tree.root)}")
        print(f"  Leaf nodes: {_count_leaf_nodes(tree.root)}")

def _calculate_height(node):
    """Calculate tree height."""
    if node.is_leaf:
        return 1
    return 1 + max(_calculate_height(child) for child in node.children)

def _count_nodes(node):
    """Count total nodes."""
    if node.is_leaf:
        return 1
    return 1 + sum(_count_nodes(child) for child in node.children)

def _count_leaf_nodes(node):
    """Count leaf nodes."""
    if node.is_leaf:
        return 1
    return sum(_count_leaf_nodes(child) for child in node.children)

# Usage
tree = BPlusTreeMap(capacity=8)
tree.update((i, i**2) for i in range(1000))
inspect_tree_structure(tree)
```

### Performance Profiling

```python
import cProfile
import pstats
from io import StringIO

def profile_tree_operations(size=10000):
    """Profile B+ Tree operations."""

    def operations():
        tree = BPlusTreeMap(capacity=32)

        # Insertions
        for i in range(size):
            tree[i] = f"value_{i}"

        # Lookups
        for i in range(0, size, 10):
            _ = tree[i]

        # Range queries
        for start in range(0, size, 1000):
            _ = list(tree.items(start, start + 100))

        # Deletions
        for i in range(0, size, 2):
            del tree[i]

    # Profile the operations
    profiler = cProfile.Profile()
    profiler.enable()
    operations()
    profiler.disable()

    # Print results
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(10)
    print(s.getvalue())

profile_tree_operations()
```

## Error Handling and Recovery

### Robust Error Handling

```python
import logging

logger = logging.getLogger(__name__)

class RobustBPlusTree:
    """B+ Tree wrapper with comprehensive error handling."""

    def __init__(self, capacity=32):
        self.tree = BPlusTreeMap(capacity=capacity)
        self.backup_data = {}  # Simple backup

    def safe_insert(self, key, value):
        """Insert with error handling and backup."""
        try:
            self.tree[key] = value
            self.backup_data[key] = value
            return True
        except Exception as e:
            logger.error(f"Failed to insert {key}: {e}")
            return False

    def safe_get(self, key, default=None):
        """Get with fallback to backup."""
        try:
            return self.tree[key]
        except KeyError:
            logger.debug(f"Key {key} not found in tree, checking backup")
            return self.backup_data.get(key, default)
        except Exception as e:
            logger.error(f"Error accessing key {key}: {e}")
            return self.backup_data.get(key, default)

    def recover_from_backup(self):
        """Recover tree from backup data."""
        logger.info("Recovering tree from backup")
        try:
            self.tree.clear()
            self.tree.update(self.backup_data)
            logger.info(f"Recovered {len(self.backup_data)} items")
            return True
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            return False

    def validate_integrity(self):
        """Validate tree integrity."""
        try:
            # Check that all items are accessible
            tree_items = dict(self.tree.items())

            # Check ordering
            keys = list(tree_items.keys())
            if keys != sorted(keys):
                logger.error("Tree ordering is corrupted")
                return False

            # Check against backup
            mismatches = 0
            for key, value in self.backup_data.items():
                if key not in tree_items:
                    mismatches += 1
                    logger.warning(f"Key {key} missing from tree")
                elif tree_items[key] != value:
                    mismatches += 1
                    logger.warning(f"Value mismatch for key {key}")

            if mismatches > 0:
                logger.error(f"Found {mismatches} integrity issues")
                return False

            logger.info("Tree integrity validated successfully")
            return True

        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False

# Usage
robust_tree = RobustBPlusTree()

# Safe operations
for i in range(1000):
    robust_tree.safe_insert(i, f"value_{i}")

# Validate periodically
if not robust_tree.validate_integrity():
    robust_tree.recover_from_backup()
```

## Summary

- **Capacity tuning** is the primary performance optimization
- **Memory efficiency** comes from appropriate key types and tree reuse
- **Batch operations** provide significant performance improvements
- **Range queries** are a key advantage over standard dictionaries
- **Real-world applications** include time-series data, caches, and leaderboards
- **Error handling** should include validation and recovery mechanisms
- **Profiling** helps identify performance bottlenecks in your specific use case
