# Design Decision: Parallel Vectors vs Single Entry Vector in LeafNode

This document analyzes the design tradeoff between storing keys and values in parallel vectors versus a single vector of entries in the B+ tree leaf nodes.

## Current Design: Parallel Vectors

```rust
pub struct LeafNode<K, V> {
    capacity: usize,
    keys: Vec<K>,
    values: Vec<V>,
    next: NodeId,
}
```

## Alternative Design: Single Vector of Entries

```rust
pub struct Entry<K, V> {
    key: K,
    value: V,
}

pub struct LeafNode<K, V> {
    capacity: usize,
    entries: Vec<Entry<K, V>>,
    next: NodeId,
}
```

## Analysis

### Memory Layout & Cache Performance

#### Parallel Vectors (Current Design)

**Advantages:**
- **Optimal cache locality for searches**: Keys are stored contiguously in memory, maximizing cache line utilization during binary search
- **Smaller cache footprint**: When searching (the most common operation), only key data is loaded into cache
- **Better prefetching**: Modern CPUs can prefetch sequential key data more effectively
- **Separate access patterns**: Can scan keys without touching values at all

**Disadvantages:**
- Two separate heap allocations per leaf node
- Keys and values may be allocated far apart in memory
- Must maintain synchronization between two vectors

#### Single Entry Vector

**Advantages:**
- Single heap allocation per leaf node
- Key and value are adjacent in memory - beneficial when both are needed
- Simpler memory management and allocation pattern
- Natural representation of key-value pairs

**Disadvantages:**
- **Poor cache utilization for searches**: Each cache line loads both keys and values, wasting ~50% of cache on unused value data
- **Worse binary search performance**: Keys are not contiguous, requiring larger strides through memory
- **Increased memory bandwidth**: Searches must load 2x the data even though values are ignored

### Performance Analysis by Operation

#### Binary Search (Most Critical Operation)
- **Parallel vectors**: Touches only the keys array, achieving optimal cache usage
- **Single vector**: Loads entire entries, wasting cache on values that aren't needed
- **Winner**: Parallel vectors (significant advantage)

#### Insertion/Deletion
- **Parallel vectors**: Must update two arrays, maintaining synchronization
- **Single vector**: Single array manipulation, but moves more bytes per operation
- **Winner**: Roughly equivalent

#### Range Iteration
- **Parallel vectors**: Must zip two iterators or use index-based access
- **Single vector**: Direct iteration over entries
- **Winner**: Single vector (minor advantage)

#### Value Updates
- **Parallel vectors**: Direct index into values array
- **Single vector**: Access through entry
- **Winner**: Equivalent

### Real-World B+ Tree Characteristics

B+ trees are specifically optimized for:

1. **Search-heavy workloads**: Keys are accessed orders of magnitude more frequently than values
2. **High branching factors**: Nodes contain many keys (typically 50-200+)
3. **Range scans**: Sequential access after initial search
4. **Disk-based storage**: Originally designed to minimize disk I/O

### Industry Precedent

Production database implementations consistently choose parallel or separated storage:

- **PostgreSQL**: Stores keys separately in interior nodes
- **MySQL InnoDB**: Uses separate key arrays for efficient searching  
- **SQLite**: Separates keys and values in B-tree nodes
- **RocksDB**: Uses separate key storage in memtables

## Benchmarking Approach

To validate this decision, benchmarks should compare:

```rust
#[bench]
fn bench_parallel_vec_search(b: &mut Bencher) {
    let mut leaf = LeafNode::new(64);
    // Fill with realistic data
    for i in 0..60 {
        leaf.keys.push(i);
        leaf.values.push(format!("value_{}", i));
    }
    
    b.iter(|| {
        // Measure search performance
        for i in 0..60 {
            black_box(leaf.keys.binary_search(&i));
        }
    });
}

#[bench]
fn bench_entry_vec_search(b: &mut Bencher) {
    let mut entries = Vec::new();
    for i in 0..60 {
        entries.push(Entry { key: i, value: format!("value_{}", i) });
    }
    
    b.iter(|| {
        // Measure search performance with entries
        for i in 0..60 {
            black_box(entries.binary_search_by_key(&i, |e| &e.key));
        }
    });
}
```

Expected results based on cache analysis:
- Parallel vectors should show 30-50% better search performance
- The advantage increases with node size
- The advantage is more pronounced with larger value types

## Recommendation

**Maintain the current parallel vectors design** for the following reasons:

1. **Cache Efficiency**: B+ trees perform far more searches than modifications. The parallel design optimizes for the common case by keeping search data (keys) dense and contiguous.

2. **Proven Design**: Production databases universally use this approach because the performance benefits are substantial and well-understood.

3. **Scalability**: The performance advantage of parallel vectors increases with node size, making it more suitable for high-performance scenarios.

4. **Memory Overhead**: For typical B+ tree nodes (64-256 entries), the overhead of two allocations is negligible compared to the cache benefits.

## When to Consider Single Entry Vector

The single entry design might be preferable only in these specific scenarios:

1. **Tiny nodes**: With very small branching factors (< 8 keys)
2. **Huge values**: When values are much larger than keys and always accessed together
3. **Memory-constrained embedded systems**: Where allocation overhead matters more than cache performance
4. **Simplicity over performance**: In educational implementations where clarity is paramount

## Conclusion

The current parallel vectors design is optimal for a production B+ tree implementation. The cache locality benefits for search operations (the primary use case) far outweigh the minor complexity of maintaining two vectors. This design decision aligns with decades of database engineering experience and should be maintained unless benchmarks on specific workloads demonstrate otherwise.