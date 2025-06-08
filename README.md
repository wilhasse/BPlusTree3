# BPlusTree3

High-performance B+ tree implementations for **Rust** and **Python**, designed for efficient range queries and sequential access patterns.

## 🚀 **Dual-Language Implementation**

This project provides **complete, optimized B+ tree implementations** in both languages:

- **🦀 [Rust Implementation](./rust/)** - Zero-cost abstractions, arena-based memory management
- **🐍 [Python Implementation](./python/)** - Competitive with SortedDict, optimized for specific use cases

## 📊 **Performance Highlights** 

### **Rust Implementation**
- **Up to 41% faster deletions** with optimized rebalancing
- **19-30% improvement** in mixed workloads
- **Full Rust range syntax support** (`3..7`, `3..=7`, `5..`, etc.)

### **Python Implementation**  
- **Up to 2.5x faster** than SortedDict for partial range scans
- **1.4x faster** for medium range queries
- **Excellent scaling** for large dataset iteration

## 🎯 **Choose Your Implementation**

| Use Case | Rust | Python |
|----------|------|--------|
| **Systems programming** | ✅ Primary choice | ❌ |
| **High-performance applications** | ✅ Zero-cost abstractions | ⚠️ Good for specific patterns |
| **Database engines** | ✅ Full control | ⚠️ Limited |
| **Data analytics** | ✅ Fast | ✅ Great for range queries |
| **Rapid prototyping** | ⚠️ Learning curve | ✅ Easy integration |
| **Existing Python codebase** | ❌ | ✅ Drop-in replacement |

## 🚀 **Quick Start**

### Rust
```rust
use bplustree3::BPlusTreeMap;

let mut tree = BPlusTreeMap::new(16).unwrap();
tree.insert(1, "one");
tree.insert(2, "two");

// Range queries with Rust syntax!
for (key, value) in tree.range(1..=2) {
    println!("{}: {}", key, value);
}
```

### Python  
```python
from bplustree import BPlusTree

tree = BPlusTree(capacity=128)
tree[1] = "one"
tree[2] = "two"

# Range queries
for key, value in tree.range(1, 2):
    print(f"{key}: {value}")
```

## 📖 **Documentation**

- **📚 [Technical Documentation](./rust/docs/)** - Architecture, algorithms, benchmarks
- **🦀 [Rust Documentation](./rust/README.md)** - Rust-specific usage and examples
- **🐍 [Python Documentation](./python/README.md)** - Python-specific usage and examples

## ⚡ **Performance Analysis**

Comprehensive benchmarking shows **significant advantages** in specific scenarios:

### **Key Strengths**
- **Range queries**: O(log n + k) complexity with excellent cache locality
- **Sequential scans**: Linked leaf nodes enable efficient iteration  
- **Deletion-heavy workloads**: Optimized rebalancing algorithms
- **Large datasets**: Performance improves with scale

### **Benchmark Results**
- **Rust**: 19-41% faster deletions, excellent overall performance
- **Python**: 2.5x faster partial scans, competitive with highly optimized libraries

See [performance documentation](./rust/docs/) for detailed analysis and charts.

## 🏗️ **Architecture**

Both implementations share core design principles:

- **Arena-based memory management** for efficiency
- **Linked leaf nodes** for fast sequential access
- **Hybrid navigation** combining tree traversal + linked list iteration
- **Optimized rebalancing** with reduced duplicate lookups
- **Comprehensive testing** including adversarial test patterns

## 🛠️ **Development**

### Rust Development
```bash
cd rust/
cargo test --features testing
cargo bench
```

### Python Development  
```bash
cd python/
pip install -e .
python -m pytest tests/
```

### Cross-Language Benchmarking
```bash
python scripts/analyze_benchmarks.py
```

## 🤝 **Contributing**

This project follows **Test-Driven Development** and **Tidy First** principles:

1. **Write tests first** - All features start with failing tests
2. **Small, focused commits** - Separate structural and behavioral changes  
3. **Comprehensive validation** - Both implementations tested against reference implementations
4. **Performance awareness** - All changes benchmarked for performance impact

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 **Links**

- **[GitHub Repository](https://github.com/KentBeck/BPlusTree3)**
- **[Rust Crate](https://crates.io/crates/bplustree3)** _(coming soon)_
- **[Python Package](https://pypi.org/project/bplustree3/)** _(coming soon)_

---

> Built with ❤️ following Kent Beck's **Test-Driven Development** methodology.