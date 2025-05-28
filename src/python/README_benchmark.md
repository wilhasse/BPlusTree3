# B+ Tree vs SortedDict Performance Benchmark

This benchmark utility compares the performance of our B+ Tree implementation against the highly optimized `SortedDict` from the `sortedcontainers` library.

## Quick Start

```bash
# Install dependencies
pip install sortedcontainers

# Quick benchmark
python benchmark.py --quick

# Capacity tuning (recommended for finding optimal settings)
python benchmark.py --capacity-tuning

# Full benchmark with all operations
python benchmark.py

# Custom benchmark
python benchmark.py --sizes 1000,10000 --operations insert,lookup --capacity 16,32
```

## Benchmark Results Summary

### Key Findings

1. **SortedDict is significantly faster** for individual operations (2-100x faster)
2. **Higher B+ Tree capacity improves performance** (capacity 32 is ~84% faster than capacity 3)
3. **Range queries are our competitive advantage** (only ~1.04x slower vs 40x slower for lookups)
4. **Mixed workloads show smaller gaps** (~1.3x slower vs SortedDict)

### Optimal Configuration

**Recommended B+ Tree capacity: 32**
- Best overall performance across all operations
- 84% improvement over default capacity (3-4)
- Good balance between node size and tree depth

### Performance by Operation

| Operation | B+ Tree (cap 32) | SortedDict | Relative Speed |
|-----------|------------------|------------|----------------|
| **Range Queries** | Competitive | Fast | ~1.04x slower |
| **Mixed Workload** | Good | Fast | ~1.3x slower |
| **Insertions** | Moderate | Fast | ~2.7x slower |
| **Lookups** | Slow | Very Fast | ~37x slower |

## When to Use B+ Tree vs SortedDict

### Use B+ Tree when:
- ✅ **Range queries are important** (nearly equal performance)
- ✅ **Sequential access patterns** (efficient leaf chain traversal)
- ✅ **Disk-based storage** (our implementation could be extended)
- ✅ **Predictable memory access** (tree structure vs hash-based)
- ✅ **Bulk operations** (our batch operations)

### Use SortedDict when:
- ✅ **Individual lookups dominate** (37x faster)
- ✅ **Random access patterns** (optimized for this)
- ✅ **Maximum single-operation speed** (highly optimized C implementation)
- ✅ **Memory efficiency** (very compact representation)

## Benchmark Details

### Test Configuration
- **Measurements**: 5 iterations with 3 warmup runs
- **Dataset sizes**: 100 to 50,000 keys (configurable)
- **Key distribution**: Random integers with 10x key space
- **Operations tested**: Insert, lookup, delete, iterate, range queries, mixed workload

### Capacity Analysis
Tested capacities from 3 to 32, showing clear performance improvement with higher values:

```
Capacity |  Relative Speed | Improvement
---------|-----------------|------------
   3     |     0.19x      |  baseline
   8     |     0.30x      |  +58%
  16     |     0.31x      |  +63%
  32     |     0.35x      |  +84%
```

### Hardware Dependencies
Performance characteristics may vary based on:
- **CPU cache size** (affects optimal capacity)
- **Memory bandwidth** (affects large node operations)
- **Python implementation** (CPython vs PyPy)

## Usage Examples

### Basic Benchmarking
```bash
# Compare default settings
python benchmark.py --quick

# Focus on range queries (our strength)
python benchmark.py --operations range --capacity 32

# Test larger datasets
python benchmark.py --sizes 10000,100000 --capacity 32
```

### Capacity Optimization
```bash
# Comprehensive capacity analysis
python benchmark.py --capacity-tuning

# Test specific capacities
python benchmark.py --capacity 16,24,32,64 --operations mixed
```

### Performance Profiling
```bash
# High precision measurements
python benchmark.py --iterations 10 --operations insert

# Specific workload simulation
python benchmark.py --operations mixed --sizes 50000
```

## Implementation Notes

The benchmark measures:
- **Wall-clock time** (most relevant for user experience)
- **Multiple iterations** with statistical analysis
- **Warm-up runs** to minimize JIT compilation effects
- **Garbage collection** between measurements
- **Realistic workloads** with mixed operations

## Future Improvements

Potential enhancements to the B+ Tree for better performance:
1. **Memory layout optimization** (better cache locality)
2. **Node compression** (more keys per node)
3. **Bulk loading** (faster initial construction)
4. **Lazy deletion** (defer expensive restructuring)
5. **SIMD operations** (vectorized search within nodes)

## Conclusion

While SortedDict excels in general-purpose scenarios, our B+ Tree implementation shows its strength in range queries and provides a solid foundation for specialized use cases like database indexes or disk-based storage systems.

**For most applications**: Use SortedDict
**For range-heavy workloads**: Use B+ Tree with capacity 32
**For educational purposes**: Both are excellent examples of different approaches to sorted data structures