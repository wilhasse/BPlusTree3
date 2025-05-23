# BPlusTree3

A B+ tree implementation in Rust, designed as an alternative to `BTreeMap` for specific use cases requiring efficient range queries and sequential access patterns.

## Overview

B+ trees are a variant of B-trees optimized for systems that read and write large blocks of data. Unlike standard B-trees, B+ trees store all values in leaf nodes and maintain a linked list structure between leaves, making them particularly efficient for range queries and sequential scans.

## Installation

Add this to your `Cargo.toml`:

```toml
[dependencies]
bplustree3 = "0.1.0"
```

## Quick Start

```rust
use bplustree3::BPlusTree;

fn main() {
    let mut tree = BPlusTree::new(4);

    // Insert some data
    tree.insert(1, "one");
    tree.insert(3, "three");
    tree.insert(2, "two");

    // Range query
    let range = tree.range(Some(&1), Some(&2));
    println!("{:?}", range); // [(&1, &"one"), (&2, &"two")]

    // Sequential access
    for (key, value) in tree.slice() {
        println!("{}: {}", key, value);
    }
}
```

## Current Status

🚧 **Work in Progress** - This implementation currently provides:

- ✅ Basic insertion with automatic node splitting
- ✅ Key lookup (`get`)
- ✅ Range queries
- ✅ Sequential iteration (`slice`)
- ❌ Key deletion (not yet implemented)
- ❌ Full B+ tree with internal nodes (currently uses linked leaf nodes)

## API

### Creating a B+ Tree

```rust
use bplustree3::BPlusTree;

// Create a tree with branching factor of 4
let mut tree = BPlusTree::new(4);
```

### Basic Operations

```rust
// Insert key-value pairs
tree.insert(10, "ten");
tree.insert(20, "twenty");
tree.insert(5, "five");

// Get values by key
assert_eq!(tree.get(&10), Some(&"ten"));
assert_eq!(tree.get(&99), None);

// Update existing keys (returns old value)
let old_value = tree.insert(10, "TEN");
assert_eq!(old_value, Some("ten"));

// Check tree properties
assert_eq!(tree.len(), 3);
assert!(!tree.is_empty());
```

### Range Queries

```rust
// Get all entries in a range
let entries = tree.range(Some(&5), Some(&15));
// Returns: [(&5, &"five"), (&10, &"TEN")]

// Get all entries from a minimum key
let entries = tree.range(Some(&10), None);
// Returns: [(&10, &"TEN"), (&20, &"twenty")]

// Get all entries up to a maximum key
let entries = tree.range(None, Some(&15));
// Returns: [(&5, &"five"), (&10, &"TEN")]
```

### Sequential Access

```rust
// Get all entries in sorted order
let all_entries = tree.slice();
// Returns: [(&5, &"five"), (&10, &"TEN"), (&20, &"twenty")]
```

## When to Use BPlusTree vs BTreeMap

### Use BPlusTree when:

1. **Frequent Range Queries**: You regularly need to retrieve all keys within a range

   ```rust
   // Efficient in B+ trees due to leaf node linking
   let recent_orders = tree.range(Some(&start_date), Some(&end_date));
   ```

2. **Sequential Scans**: You often iterate through large portions of your data

   ```rust
   // B+ trees excel at sequential access patterns
   for (key, value) in tree.slice() {
       process_in_order(key, value);
   }
   ```

3. **Database-like Workloads**: Your access patterns resemble database queries with range scans

4. **Large Datasets**: Working with datasets where cache efficiency matters for range operations

### Use BTreeMap when:

1. **Random Access**: Primarily doing point lookups and updates
2. **Frequent Deletions**: Need robust deletion support (not yet implemented in BPlusTree)
3. **Memory Efficiency**: Working with smaller datasets where BTreeMap's overhead is acceptable
4. **Mature API**: Need a battle-tested implementation with full standard library integration

## Performance Characteristics

| Operation       | BPlusTree    | BTreeMap           | Notes                         |
| --------------- | ------------ | ------------------ | ----------------------------- |
| Insert          | O(log n)     | O(log n)           | Similar performance           |
| Get             | O(log n)     | O(log n)           | Similar performance           |
| Range Query     | O(log n + k) | O(log n + k log n) | B+ tree advantage for large k |
| Sequential Scan | O(k)         | O(k log n)         | Significant B+ tree advantage |
| Memory Usage    | Higher       | Lower              | B+ trees store more pointers  |

Where `n` is the number of elements and `k` is the number of elements in the result set.

## Configuration

The branching factor determines how many entries each node can hold before splitting:

```rust
// Small branching factor (2-4): More splits, deeper tree, good for testing
let tree = BPlusTree::new(3);

// Medium branching factor (8-16): Balanced performance
let tree = BPlusTree::new(12);

// Large branching factor (32-64): Fewer splits, better cache utilization
let tree = BPlusTree::new(48);
```

## Testing

### Regular Tests

Run the standard test suite:

```bash
cargo test
```

### Fuzz Testing

The project includes comprehensive fuzz tests that are excluded from normal test runs for performance. These tests compare BPlusTree behavior against Rust's standard `BTreeMap` to ensure correctness.

#### Running Fuzz Tests

```bash
# Run all fuzz tests
cargo test --test fuzz_tests -- --ignored

# Run a specific fuzz test with output
cargo test fuzz_test_bplus_tree -- --ignored --nocapture

# Run fuzz test with random insertion patterns
cargo test fuzz_test_with_random_keys -- --ignored --nocapture

# Run fuzz test focusing on updates
cargo test fuzz_test_with_updates -- --ignored --nocapture
```

#### Timed Fuzz Testing

For extended testing, use the timed fuzz test:

```bash
# Default 10-second test
cargo test fuzz_test_timed -- --ignored --nocapture

# Custom duration examples
FUZZ_TIME=30s cargo test fuzz_test_timed -- --ignored --nocapture
FUZZ_TIME=5m cargo test fuzz_test_timed -- --ignored --nocapture
FUZZ_TIME=1h cargo test fuzz_test_timed -- --ignored --nocapture
```

The fuzz tests will:

- Test multiple branching factors (2-10)
- Insert thousands of key-value pairs
- Verify all operations match `BTreeMap` behavior
- Test both sequential and random insertion patterns
- Validate range queries and iteration order
- Report detailed progress and any mismatches

## Examples

### Time Series Data

```rust
use bplustree3::BPlusTree;

let mut time_series = BPlusTree::new(16);

// Insert timestamped data
time_series.insert(1640995200, "2022-01-01 data");
time_series.insert(1641081600, "2022-01-02 data");
time_series.insert(1641168000, "2022-01-03 data");

// Efficient range query for a time period
let start_time = 1640995200;
let end_time = 1641081600;
let period_data = time_series.range(Some(&start_time), Some(&end_time));
```

### Log Processing

```rust
let mut log_index = BPlusTree::new(32);

// Index log entries by timestamp
for entry in log_entries {
    log_index.insert(entry.timestamp, entry.message);
}

// Efficiently scan logs in chronological order
for (timestamp, message) in log_index.slice() {
    process_log_entry(timestamp, message);
}
```

## Implementation Details

### Current Architecture

The current implementation uses a simplified B+ tree structure:

- **Leaf Nodes Only**: All data is stored in leaf nodes connected via a linked list
- **Automatic Splitting**: Nodes split when they exceed the branching factor
- **Sequential Access**: Linked leaf nodes enable efficient range queries
- **No Internal Nodes**: Future versions will add internal nodes for true B+ tree structure

### Key Components

- `BPlusTree<K, V>`: Main tree structure with configurable branching factor
- `LeafNode<K, V>`: Individual nodes storing key-value pairs
- `LeafFinder<K>`: Utility for locating the correct leaf node for operations
- `Entry<K, V>`: Key-value pair storage structure

### Future Roadmap

- [ ] **Internal Nodes**: Add proper B+ tree internal node structure
- [ ] **Deletion**: Implement key removal with node merging
- [ ] **Persistence**: Add serialization/deserialization support
- [ ] **Iterators**: Implement standard Rust iterator traits
- [ ] **Concurrent Access**: Add thread-safe variants
- [ ] **Memory Optimization**: Reduce memory overhead
- [ ] **Bulk Loading**: Efficient bulk insertion methods

## Development Philosophy

This project follows Kent Beck's Test-Driven Development methodology:

1. **Red-Green-Refactor**: Write failing tests, make them pass, then refactor
2. **Tidy First**: Separate structural changes from behavioral changes
3. **Small Steps**: Implement minimal functionality to make tests pass
4. **Comprehensive Testing**: Every feature is validated against `BTreeMap`

## Contributing

Contributions are welcome! Please:

1. Follow TDD practices - write tests first
2. Run the full test suite including fuzz tests
3. Keep commits small and focused
4. Separate structural and behavioral changes
5. Update documentation for new features

### Running the Full Test Suite

```bash
# Quick development tests
cargo test

# Comprehensive validation (takes longer)
cargo test --test fuzz_tests -- --ignored

# Extended stress testing
FUZZ_TIME=10m cargo test fuzz_test_timed -- --ignored --nocapture
```

## License

[Add your license here]
