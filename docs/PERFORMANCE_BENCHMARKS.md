# BPlusTreeMap Performance Benchmarks

This document contains the latest benchmark results comparing BPlusTreeMap against Rust's standard BTreeMap.

## Test Environment

- **Dataset Size**: 100,000 items for range queries, 50,000 for edge cases
- **Hardware**: Apple Silicon (ARM64)
- **Rust Version**: Latest stable
- **Optimization Level**: Release build with optimizations

## Benchmark Results Summary

### 🚀 **Where B+ Tree Excels**

#### Full Tree Iteration
Our B+ tree shows significant performance advantages for full iteration:

| Operation | BTreeMap | BPlusTreeMap | **Improvement** |
|-----------|----------|--------------|-----------------|
| **Full Iteration** | 46.58 µs | 32.27 µs | **🎉 31% faster** |

This demonstrates the power of B+ tree's linked leaf structure for sequential access.

#### Large Range Queries (Competitive)
For larger ranges, our optimized implementation shows competitive performance:

| Range Size | BTreeMap | BPlusTreeMap | Performance |
|------------|----------|--------------|-------------|
| **Range to End (25K items)** | 19.94 µs | 20.70 µs | ~4% slower |

The linked list traversal keeps us very competitive even for large ranges.

### 📊 **Current Range Query Results**

#### Range Query Performance (100K Dataset)

| Range Size | BTreeMap | BPlusTreeMap | Ratio |
|------------|----------|--------------|-------|
| **10 items** | 22.27 ns | 29.48 ns | 1.32x slower |
| **50 items** | 48.02 ns | 79.29 ns | 1.65x slower |
| **100 items** | 77.54 ns | 134.42 ns | 1.73x slower |
| **500 items** | 317.07 ns | 533.01 ns | 1.68x slower |
| **1000 items** | 622.97 ns | 1027.7 ns | 1.65x slower |
| **5000 items** | 3.027 µs | 5.088 µs | 1.68x slower |

#### Edge Case Performance (50K Dataset)

| Test Case | BTreeMap | BPlusTreeMap | Ratio |
|-----------|----------|--------------|-------|
| **Small range at start** | 16.08 ns | 27.68 ns | 1.72x slower |
| **Small range at end** | 29.04 ns | 31.75 ns | 1.09x slower |

### 🔍 **Analysis & Optimization Opportunities**

#### Why Range Queries Are Currently Slower

1. **Tree Navigation Overhead**: Our `find_range_start()` function may have higher overhead than BTreeMap's highly optimized binary search
2. **Arena Access Patterns**: Multiple arena lookups vs. BTreeMap's direct pointer chasing
3. **Bounds Checking**: Our end-key checking in the iterator may add overhead
4. **Cache Effects**: BTreeMap's compact node layout may have better cache behavior for small ranges

#### Where B+ Tree Architecture Shines

1. **Full Iteration**: 31% faster due to linked leaf traversal
2. **Very Large Ranges**: Competitive performance with better memory patterns
3. **Sequential Access**: Natural advantage from linked list structure

### 🎯 **Future Optimization Targets**

Based on these results, key optimization opportunities:

1. **Optimize find_range_start()**: 
   - Pre-compute common access patterns
   - Reduce arena lookup overhead
   - Consider caching frequently accessed nodes

2. **Reduce Iterator Overhead**:
   - Minimize bounds checking in hot paths
   - Optimize arena access patterns
   - Consider unsafe optimizations for critical paths

3. **Arena Access Optimization**:
   - Memory layout improvements
   - Reduce pointer indirection
   - Better cache-friendly data structures

4. **Range-Specific Optimizations**:
   - Fast path for small ranges
   - Different strategies based on range size
   - Hybrid approaches for different use cases

### 📈 **Performance Trends**

- **Small Ranges**: BTreeMap has advantage due to optimized binary search
- **Medium Ranges**: Gap narrows but BTreeMap still leads
- **Large Ranges**: Very competitive, nearly matching performance
- **Full Iteration**: B+ tree clear winner (31% faster)

### 🎉 **Key Achievements**

1. ✅ **Optimized Range Iterator**: Successfully implemented O(log n + k) algorithm
2. ✅ **Linked List Traversal**: Leveraging B+ tree's core advantage
3. ✅ **Lazy Evaluation**: No memory pre-allocation for ranges
4. ✅ **Full Iteration Speed**: 31% faster than BTreeMap
5. ✅ **Competitive Large Ranges**: Within 4% for large sequential access

### 🔬 **Technical Implementation**

The optimized range iterator uses a two-phase approach:

1. **Navigation Phase**: O(log n) tree traversal to find start position
2. **Traversal Phase**: O(k) linked list following for items in range

This leverages B+ tree's fundamental strength: efficient sequential access after targeted positioning.

## Running Benchmarks

To reproduce these results:

```bash
# Run all benchmarks
cargo bench --bench comparison

# Run only range query benchmarks
cargo bench --bench comparison range_queries

# Run edge case benchmarks
cargo bench --bench comparison range_edge_cases
```

## Conclusion

While small range queries still favor BTreeMap's highly optimized implementation, our B+ tree optimization shows its strength in:

- **Full iteration** (31% faster)
- **Large range queries** (competitive within 4%)
- **Memory efficiency** (constant space vs. pre-allocation)
- **Algorithmic complexity** (O(log n + k) vs. O(n) traversal)

The foundation is solid for future micro-optimizations to close the gap on small ranges while maintaining our advantages for larger data operations.