# B+ Tree Performance Optimization Plan

## Goal
Achieve performance parity with Python's sortedcontainers.SortedDict while maintaining clean, simple Python code.

## Current Performance Gap
- B+ Tree: ~25 function calls per lookup, ~95ns per operation
- SortedDict: ~0.0004 function calls per lookup, ~4ns per operation
- Target: 20-25x performance improvement needed

## Key Design Changes

### 1. Single Array Node Structure
Replace separate keys/values/children arrays with a single contiguous array:
```python
# Current structure (inefficient)
class LeafNode:
    keys = [k1, k2, k3, ...]
    values = [v1, v2, v3, ...]

# Proposed structure (cache-friendly)
class LeafNode:
    # Single array: [k1, k2, k3, ..., v1, v2, v3, ...]
    data = [keys..., values...]
```

**Benefits:**
- Better cache locality (single memory allocation)
- Reduced Python object overhead
- Easier to map to C struct
- SIMD-friendly for parallel comparisons

### 2. C Extension Architecture

#### Phase 1: Core Node Operations
Implement in C:
- Node allocation/deallocation with memory pool
- Binary search within nodes
- Key/value/child access
- Node splitting and merging

Keep in Python:
- High-level tree operations
- Iterator protocol
- Dictionary interface

#### Phase 2: Tree Traversal
Move to C:
- Complete search path from root to leaf
- Batch insertions
- Range queries
- Tree rebalancing

#### Phase 3: Full C Implementation
- Entire tree structure in C
- Python wrapper for dict compatibility
- Memory-mapped persistence option

### 3. Structural Optimizations

#### A. Fixed-Capacity Nodes
```c
typedef struct {
    uint8_t num_keys;
    uint8_t is_leaf;
    uint16_t capacity;
    // Aligned for SIMD
    int64_t data[256];  // keys[0:128], values/children[128:256]
} BPlusNode;
```

#### B. Memory Pool
- Pre-allocate node pool
- Reuse deallocated nodes
- Reduce allocation overhead

#### C. Vectorized Search
- Use SIMD instructions for key comparisons
- Process 4-8 keys simultaneously
- ~4x speedup for intra-node search

#### D. Prefetching
- Prefetch child nodes during traversal
- Hide memory latency
- Especially beneficial for large trees

### 4. Python Interface Design

```python
class BPlusTree:
    def __init__(self, order=128):
        # Create C tree structure
        self._tree = _cext.create_tree(order)
    
    def __getitem__(self, key):
        # Single C call for entire lookup
        return _cext.tree_get(self._tree, key)
    
    def __setitem__(self, key, value):
        # Single C call for insert
        _cext.tree_insert(self._tree, key, value)
```

### 5. Optimization Priorities

1. **Lookup Performance** (highest impact)
   - Inline all node operations
   - Vectorized binary search
   - Eliminate Python function calls

2. **Bulk Operations**
   - Batch API for multiple insertions
   - Optimized tree building from sorted data
   - Parallel operations where possible

3. **Memory Efficiency**
   - Compact node representation
   - Configurable node sizes
   - Support for billions of keys

### 6. Benchmarking Strategy

Compare against sortedcontainers.SortedDict:
- Random lookups (1M operations)
- Sequential inserts
- Random inserts
- Range queries
- Mixed workloads
- Memory usage

Target metrics:
- Lookup: < 10ns per operation
- Insert: < 50ns per operation
- Memory: < 2x overhead vs raw data

### 7. Implementation Phases

**Phase 1 (Week 1-2): Single Array Structure**
- Design C struct layout
- Implement single-array node in pure Python
- **Expected Performance:** 20-30% improvement from better cache locality
- **Measurement:** Benchmark lookups/sec before and after change

**Phase 2 (Week 3-4): Core C Operations**
- Create C extension module
- Implement node search, insert, split operations
- **Expected Performance:** 3-5x improvement from eliminating Python overhead
- **Measurement:** Profile function call counts and operation timing

**Phase 3 (Week 5-6): Advanced Optimizations**
- Vectorized search with SIMD
- Memory pool for node allocation
- Prefetching for tree traversal
- **Expected Performance:** Additional 2-3x improvement
- **Measurement:** Cache misses, memory allocation overhead

**Phase 4 (Week 7-8): Final Optimizations**
- Inline critical paths
- Branch prediction hints
- Custom allocator tuning
- **Expected Performance:** Final 20-50% improvement
- **Measurement:** Full benchmark suite vs SortedDict

**Performance Validation at Each Step:**
1. Run standardized benchmark suite
2. Compare against baseline and SortedDict
3. Profile to identify next bottleneck
4. Document improvement percentage
5. Ensure no regression in any operation

## Expected Results

With these optimizations:
- 10-20x performance improvement
- Competitive with or faster than SortedDict
- Maintains O(log n) guarantees
- Better performance for large datasets
- Lower memory usage due to B+ tree structure

## Risks and Mitigation

1. **Complexity**: Keep Python layer simple, complexity in C
2. **Portability**: Use standard C99, optional SIMD
3. **Debugging**: Comprehensive test suite, debug builds
4. **API Changes**: Maintain backward compatibility

## Success Criteria

- Lookup performance within 2x of SortedDict
- Insert performance within 5x of SortedDict
- Memory usage < 1.5x of theoretical minimum
- All existing tests pass
- No API breaking changes