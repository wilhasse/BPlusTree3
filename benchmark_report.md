# B+ Tree Cross-Language Benchmark Report

Generated: 2025-07-26T14:07:56.923776

## System Information

- **OS**: Linux godev4 6.1.0-37-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.140-1 (2025-05-22) x86_64 GNU/Linux
- **CPU**: Unknown
- **Memory**: 15Gi

## Performance Comparison

All times in microseconds (µs). Lower is better.

### Iteration

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native |
|------|---------|-------------|-------|-----------|--------|------------|
| 100 | 0.23 | 0.11 | 0.13 | 0.46 | 0.00 | 0.00 |
| 1000 | 2.33 | 1.13 | 1.32 | 5.26 | 0.00 | 0.01 |
| 10000 | 23.81 | 11.39 | 13.19 | 56.14 | 0.00 | 0.01 |
| 100000 | - | - | - | - | 0.00 | 0.00 |

### Lookup

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native |
|------|---------|-------------|-------|-----------|--------|------------|
| 100 | 4.79 | 4.73 | 1.69 | 0.38 | 0.00 | 0.00 |
| 1000 | 11.00 | 12.98 | 19.91 | 4.04 | 0.03 | 0.00 |
| 10000 | 17.11 | 27.92 | 47.23 | 4.43 | 0.05 | 0.00 |
| 100000 | 23.61 | 43.34 | 201.53 | 5.09 | 0.17 | 0.00 |

### Randominsert

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native |
|------|---------|-------------|-------|-----------|--------|------------|
| 100 | 1.56 | 1.62 | 9.78 | 0.97 | - | - |
| 1000 | 22.92 | 20.64 | 180.79 | 9.79 | - | - |
| 10000 | 393.50 | 525.29 | 2042.74 | 112.14 | - | - |
| 100000 | - | - | 34348.77 | 1790.64 | - | - |

### Rangequery

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native |
|------|---------|-------------|-------|-----------|--------|------------|
| 100 | 0.04 | 0.02 | 0.14 | - | - | - |
| 1000 | 0.31 | 0.12 | 0.67 | - | - | - |
| 10000 | 2.82 | 1.08 | 6.46 | - | - | - |

### Sequentialinsert

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native |
|------|---------|-------------|-------|-----------|--------|------------|
| 100 | 1.03 | 1.68 | 3.16 | 0.99 | 0.68 | 0.49 |
| 1000 | 17.17 | 26.86 | 50.95 | 9.94 | 0.35 | 0.12 |
| 10000 | 214.44 | 372.66 | 690.55 | 109.12 | 0.42 | 0.05 |
| 100000 | - | - | 22194.27 | 1707.40 | 0.44 | 0.03 |

## Performance Ratios (B+ Tree vs Native)

Values > 1.0 mean B+ tree is slower, < 1.0 mean B+ tree is faster.

### Iteration

| Language | Size | Ratio |
|----------|------|-------|
| Go | 100 | 🟢 0.28x |
| Go | 1000 | 🟢 0.25x |
| Go | 10000 | 🟢 0.23x |
| Rust | 100 | 🔴 2.09x |
| Rust | 1000 | 🔴 2.07x |
| Rust | 10000 | 🔴 2.09x |
| Zig | 100 | 🟢 0.49x |
| Zig | 1000 | 🟢 0.30x |
| Zig | 10000 | 🟢 0.44x |
| Zig | 100000 | 🔴 1.29x |

### Lookup

| Language | Size | Ratio |
|----------|------|-------|
| Go | 100 | 🔴 4.48x |
| Go | 1000 | 🔴 4.92x |
| Go | 10000 | 🔴 10.66x |
| Go | 100000 | 🔴 39.59x |
| Rust | 100 | 🟡 1.01x |
| Rust | 1000 | 🟢 0.85x |
| Rust | 10000 | 🟢 0.61x |
| Rust | 100000 | 🟢 0.54x |
| Zig | 100 | 🔴 8.57x |
| Zig | 1000 | 🔴 848.39x |
| Zig | 10000 | 🔴 17148.15x |
| Zig | 100000 | 🔴 475000.00x |

### Randominsert

| Language | Size | Ratio |
|----------|------|-------|
| Go | 100 | 🔴 10.10x |
| Go | 1000 | 🔴 18.46x |
| Go | 10000 | 🔴 18.22x |
| Go | 100000 | 🔴 19.18x |
| Rust | 100 | 🟡 0.96x |
| Rust | 1000 | 🔴 1.11x |
| Rust | 10000 | 🟢 0.75x |

### Rangequery

| Language | Size | Ratio |
|----------|------|-------|
| Rust | 100 | 🔴 1.74x |
| Rust | 1000 | 🔴 2.55x |
| Rust | 10000 | 🔴 2.61x |

### Sequentialinsert

| Language | Size | Ratio |
|----------|------|-------|
| Go | 100 | 🔴 3.20x |
| Go | 1000 | 🔴 5.13x |
| Go | 10000 | 🔴 6.33x |
| Go | 100000 | 🔴 13.00x |
| Rust | 100 | 🟢 0.61x |
| Rust | 1000 | 🟢 0.64x |
| Rust | 10000 | 🟢 0.58x |
| Zig | 100 | 🔴 1.38x |
| Zig | 1000 | 🔴 2.84x |
| Zig | 10000 | 🔴 8.27x |
| Zig | 100000 | 🔴 17.54x |

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

### When to Use B+ Trees

1. When you need ordered iteration over keys
2. When range queries are a primary use case
3. When you need predictable worst-case performance
4. When working with disk-based storage (B+ trees are cache-friendly)
5. When implementing databases or file systems

