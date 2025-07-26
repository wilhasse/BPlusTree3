# B+ Tree Cross-Language Benchmark Report

Generated: 2025-07-26T14:30:54.632734

## System Information

- **OS**: Linux godev4 6.1.0-37-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.140-1 (2025-05-22) x86_64 GNU/Linux
- **CPU**: Unknown
- **Memory**: 15Gi

## Performance Comparison

All times in microseconds (µs). Lower is better.

### Iteration

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native | C B+ | C Native |
|------|---------|-------------|-------|-----------|--------|------------|------|----------|
| 100 | 0.23 | 0.11 | 0.13 | 0.47 | 0.00 | 0.00 | 0.00 | 0.01 |
| 1000 | 2.33 | 1.13 | 1.29 | 5.19 | 0.00 | 0.01 | 0.00 | 0.00 |
| 10000 | 23.28 | 11.45 | 13.04 | 56.01 | 0.00 | 0.00 | 0.00 | 0.00 |
| 100000 | - | - | - | - | 0.00 | 0.00 | 0.00 | 0.02 |

### Lookup

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native | C B+ | C Native |
|------|---------|-------------|-------|-----------|--------|------------|------|----------|
| 100 | 4.84 | 4.84 | 1.61 | 0.40 | 0.00 | 0.00 | 0.02 | 0.00 |
| 1000 | 11.04 | 13.09 | 20.27 | 3.90 | 0.02 | 0.00 | 0.11 | 0.00 |
| 10000 | 16.98 | 28.20 | 47.60 | 4.62 | 0.02 | 0.00 | 0.98 | 0.00 |
| 100000 | 23.61 | 43.74 | 200.77 | 5.08 | 0.18 | 0.00 | 9.69 | 0.27 |

### Randominsert

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native | C B+ | C Native |
|------|---------|-------------|-------|-----------|--------|------------|------|----------|
| 100 | 1.60 | 1.60 | 10.19 | 0.91 | - | - | - | - |
| 1000 | 22.40 | 20.93 | 167.07 | 9.63 | - | - | - | - |
| 10000 | 393.25 | 521.85 | 1912.65 | 116.47 | - | - | - | - |
| 100000 | - | - | 32334.69 | 1759.38 | - | - | - | - |

### Rangequery

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native | C B+ | C Native |
|------|---------|-------------|-------|-----------|--------|------------|------|----------|
| 100 | 0.04 | 0.02 | 0.13 | - | - | - | - | - |
| 1000 | 0.31 | 0.12 | 0.63 | - | - | - | - | - |
| 10000 | 2.77 | 1.07 | 6.13 | - | - | - | - | - |

### Sequentialinsert

| Size | Rust B+ | Rust Native | Go B+ | Go Native | Zig B+ | Zig Native | C B+ | C Native |
|------|---------|-------------|-------|-----------|--------|------------|------|----------|
| 100 | 1.03 | 1.68 | 3.00 | 0.95 | 0.66 | 0.47 | 0.04 | 0.01 |
| 1000 | 16.38 | 26.48 | 47.63 | 9.08 | 0.39 | 0.13 | 0.21 | 0.01 |
| 10000 | 218.19 | 369.50 | 674.79 | 109.65 | 0.31 | 0.03 | 1.98 | 0.01 |
| 100000 | - | - | 22019.47 | 1719.94 | 0.44 | 0.03 | 19.64 | 0.25 |

## Performance Ratios (B+ Tree vs Native)

Values > 1.0 mean B+ tree is slower, < 1.0 mean B+ tree is faster.

### Iteration

| Language | Size | Ratio |
|----------|------|-------|
| C | 100 | 🟢 0.25x |
| C | 1000 | 🔴 1.12x |
| C | 10000 | 🔴 1.50x |
| C | 100000 | 🟢 0.10x |
| Go | 100 | 🟢 0.27x |
| Go | 1000 | 🟢 0.25x |
| Go | 10000 | 🟢 0.23x |
| Rust | 100 | 🔴 2.10x |
| Rust | 1000 | 🔴 2.07x |
| Rust | 10000 | 🔴 2.03x |
| Zig | 100 | 🟢 0.58x |
| Zig | 1000 | 🟢 0.27x |
| Zig | 10000 | 🟢 0.37x |
| Zig | 100000 | 🔴 1.26x |

### Lookup

| Language | Size | Ratio |
|----------|------|-------|
| C | 100 | 🔴 26.79x |
| C | 1000 | 🔴 329.06x |
| C | 10000 | 🔴 466.90x |
| C | 100000 | 🔴 36.09x |
| Go | 100 | 🔴 4.03x |
| Go | 1000 | 🔴 5.19x |
| Go | 10000 | 🔴 10.30x |
| Go | 100000 | 🔴 39.55x |
| Rust | 100 | 🟡 1.00x |
| Rust | 1000 | 🟢 0.84x |
| Rust | 10000 | 🟢 0.60x |
| Rust | 100000 | 🟢 0.54x |
| Zig | 100 | 🔴 10.59x |
| Zig | 1000 | 🔴 676.00x |
| Zig | 10000 | 🔴 8032.26x |
| Zig | 100000 | 🔴 475675.68x |

### Randominsert

| Language | Size | Ratio |
|----------|------|-------|
| Go | 100 | 🔴 11.19x |
| Go | 1000 | 🔴 17.35x |
| Go | 10000 | 🔴 16.42x |
| Go | 100000 | 🔴 18.38x |
| Rust | 100 | 🟡 1.00x |
| Rust | 1000 | 🟡 1.07x |
| Rust | 10000 | 🟢 0.75x |

### Rangequery

| Language | Size | Ratio |
|----------|------|-------|
| Rust | 100 | 🔴 1.74x |
| Rust | 1000 | 🔴 2.55x |
| Rust | 10000 | 🔴 2.59x |

### Sequentialinsert

| Language | Size | Ratio |
|----------|------|-------|
| C | 100 | 🔴 3.71x |
| C | 1000 | 🔴 25.28x |
| C | 10000 | 🔴 199.92x |
| C | 100000 | 🔴 78.88x |
| Go | 100 | 🔴 3.17x |
| Go | 1000 | 🔴 5.25x |
| Go | 10000 | 🔴 6.15x |
| Go | 100000 | 🔴 12.80x |
| Rust | 100 | 🟢 0.61x |
| Rust | 1000 | 🟢 0.62x |
| Rust | 10000 | 🟢 0.59x |
| Zig | 100 | 🔴 1.42x |
| Zig | 1000 | 🔴 3.10x |
| Zig | 10000 | 🔴 9.72x |
| Zig | 100000 | 🔴 17.44x |

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

