# BPlusTree3 - Rust Implementation

A high-performance B+ tree implementation in Rust with a dictionary-like API, optimized for range queries and sequential access patterns.

## 🚀 Quick Start

Add this to your `Cargo.toml`:

```toml
[dependencies]
bplustree3 = "0.1.0"
```

## 📖 Basic Usage

```rust
use bplustree3::BPlusTreeMap;

fn main() {
    let mut tree = BPlusTreeMap::new(16).unwrap();
    
    // Insert data
    tree.insert(1, "one");
    tree.insert(3, "three");
    tree.insert(2, "two");
    
    // Lookups
    assert_eq!(tree.get(&2), Some(&"two"));
    assert_eq!(tree.len(), 3);
    
    // Range queries with Rust's range syntax!
    let range: Vec<_> = tree.range(1..=2).collect();
    println!("{:?}", range); // [(&1, &"one"), (&2, &"two")]
    
    // Sequential iteration
    for (key, value) in tree.items() {
        println!("{}: {}", key, value);
    }
}
```

## 🔥 Range Syntax Support

Use familiar Rust range syntax for queries:

```rust
let tree = BPlusTreeMap::new(16).unwrap();
// ... populate tree ...

// Different range types
let a: Vec<_> = tree.range(3..7).collect();        // Exclusive end
let b: Vec<_> = tree.range(3..=7).collect();       // Inclusive end  
let c: Vec<_> = tree.range(5..).collect();         // Open end
let d: Vec<_> = tree.range(..5).collect();         // From start
let e: Vec<_> = tree.range(..).collect();          // Full range
```

## ⚡ Performance

- **Lookup**: O(log n)
- **Range queries**: O(log n + k) where k = result count
- **Sequential iteration**: O(n) with excellent cache locality
- **Optimized for**: Large datasets, range queries, sequential scans

### Benchmark Results

- **Up to 41% faster deletions** compared to previous versions
- **19-30% improvement** in mixed workloads (insert/lookup/delete)
- **Excellent scaling** with larger datasets

## 🔧 Configuration

The node capacity affects performance characteristics:

```rust
// Small capacity: More tree levels, good for testing
let tree = BPlusTreeMap::new(4).unwrap();

// Medium capacity: Balanced performance (recommended)
let tree = BPlusTreeMap::new(16).unwrap();

// Large capacity: Fewer levels, better cache utilization
let tree = BPlusTreeMap::new(128).unwrap();
```

## 🧪 Testing

```bash
# Run tests (requires testing feature)
cargo test --features testing

# Run benchmarks
cargo bench

# Run specific benchmark
cargo bench -- deletion
```

## 📊 Features

- ✅ Full CRUD operations (insert, get, remove)
- ✅ Arena-based memory management 
- ✅ Automatic tree balancing with node splitting/merging
- ✅ Rust range syntax support (`3..7`, `3..=7`, `5..`, etc.)
- ✅ Optimized range queries with hybrid navigation
- ✅ Multiple iterator types (items, keys, values, ranges)
- ✅ BTreeMap-compatible API for easy migration
- ✅ Comprehensive test suite with adversarial testing

## 🏗️ Architecture

This implementation uses:
- **Arena-based allocation** for efficient memory management
- **Optimized rebalancing** with reduced arena lookups
- **Linked leaf nodes** for efficient range queries
- **Hybrid navigation** combining tree traversal + linked list iteration

## 🔗 Links

- [Main Project](../) - Dual Rust/Python implementation
- [Python Implementation](../python/) - Python bindings
- [Documentation](./docs/) - Technical details and benchmarks
- [Examples](./examples/) - More usage examples

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.