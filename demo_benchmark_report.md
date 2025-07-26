# B+ Tree Cross-Language Benchmark Report (DEMO)

Generated: 2025-07-26T13:16:16.615792

⚠️ **Note**: This is a demo report with sample data showing the format.
Run `./run_all_benchmarks.py` for actual benchmark results.

## System Information

- **OS**: Linux 6.1.0-37-amd64 x86_64
- **CPU**: 12th Gen Intel(R) Core(TM) i9-12900KS
- **Memory**: 32Gi

## Performance Comparison

All times in microseconds (µs). Lower is better.

### Lookup

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native |
|------|---------|-------------|-------|-----------|--------|------------|
| 100 | 12.70 | 8.43 | 1.58 | 0.38 | 1.63 | 0.40 |
| 1000 | 14.80 | 11.30 | 19.60 | 4.04 | 16.30 | 4.00 |
| 10000 | 24.30 | 29.50 | 48.10 | 4.33 | 163.00 | 40.00 |

### Sequentialinsert

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native |
|------|---------|-------------|-------|-----------|--------|------------|
| 100 | 6.03 | 3.07 | 2.96 | 0.96 | 4.41 | 1.50 |
| 1000 | 86.20 | 49.80 | 47.30 | 9.01 | 44.10 | 15.00 |
| 10000 | 1072.00 | 640.00 | 679.00 | 110.00 | 441.00 | 150.00 |

### Iteration

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native |
|------|---------|-------------|-------|-----------|--------|------------|
| 100 | 0.27 | 0.11 | 0.13 | 0.48 | 0.32 | 0.50 |
| 1000 | 2.69 | 2.25 | 1.30 | 5.22 | 3.15 | 5.00 |
| 10000 | 29.80 | 22.70 | 12.80 | 55.50 | 31.50 | 50.00 |

## Performance Ratios (B+ Tree vs Native)

Values > 1.0 mean B+ tree is slower, < 1.0 mean B+ tree is faster.

### Lookup

| Language | Size | Ratio |
|----------|------|-------|
| Go | 100 | 🔴 4.16x |
| Go | 1000 | 🔴 4.85x |
| Go | 10000 | 🔴 11.11x |
| Rust | 100 | 🔴 1.51x |
| Rust | 1000 | 🔴 1.31x |
| Rust | 10000 | 🟢 0.82x |
| Zig | 100 | 🔴 4.07x |
| Zig | 1000 | 🔴 4.08x |
| Zig | 10000 | 🔴 4.08x |

### Sequentialinsert

| Language | Size | Ratio |
|----------|------|-------|
| Go | 100 | 🔴 3.08x |
| Go | 1000 | 🔴 5.25x |
| Go | 10000 | 🔴 6.17x |
| Rust | 100 | 🔴 1.96x |
| Rust | 1000 | 🔴 1.73x |
| Rust | 10000 | 🔴 1.68x |
| Zig | 100 | 🔴 2.94x |
| Zig | 1000 | 🔴 2.94x |
| Zig | 10000 | 🔴 2.94x |

### Iteration

| Language | Size | Ratio |
|----------|------|-------|
| Go | 100 | 🟢 0.27x |
| Go | 1000 | 🟢 0.25x |
| Go | 10000 | 🟢 0.23x |
| Rust | 100 | 🔴 2.50x |
| Rust | 1000 | 🔴 1.20x |
| Rust | 10000 | 🔴 1.31x |
| Zig | 100 | 🟢 0.63x |
| Zig | 1000 | 🟢 0.63x |
| Zig | 10000 | 🟢 0.63x |

## Key Insights

### B+ Tree Advantages

- **Ordered iteration**: B+ trees maintain keys in sorted order
- **Range queries**: Efficient range scans due to linked leaves
- **Predictable performance**: Worst-case O(log n) for all operations
- **Cache efficiency**: Better locality for sequential access patterns

### Native Structure Advantages

- **Random access**: O(1) average case for hash-based structures
- **Memory efficiency**: Lower overhead for small datasets
- **Simplicity**: Simpler implementation and usage
- **Insert performance**: Generally faster for random insertions

### Language-Specific Observations

- **Rust**: Best overall performance, especially for large datasets
- **Go**: Good balance of performance and ease of use
- **Zig**: Excellent raw performance, competitive with Rust

### Sample Insights from Demo Data

- **B+ trees excel at iteration**: All languages show B+ trees outperforming native structures for iteration
- **Native structures win at random access**: Hash maps and regular maps are faster for lookup operations
- **Zig shows consistent performance**: Most balanced ratios across operations
- **Rust B+ tree competitive at scale**: Performance gap narrows with larger datasets

### When to Use B+ Trees

1. When you need ordered iteration over keys
2. When range queries are a primary use case
3. When you need predictable worst-case performance
4. When working with disk-based storage (B+ trees are cache-friendly)
5. When implementing databases or file systems

