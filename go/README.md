# B+ Tree Implementation in Go

A high-performance, generic B+ tree implementation in Go featuring type safety, efficient memory usage, and comprehensive testing.

## Features

- **Generic Implementation**: Full type safety using Go 1.18+ generics
- **Efficient Operations**: O(log n) insert, search, and delete
- **Range Queries**: Optimized range searches using linked leaf nodes
- **Bidirectional Iterators**: Forward and reverse iteration support
- **Thread-Safe Design**: Safe for concurrent reads (writes need external synchronization)
- **Comprehensive Testing**: 40+ tests including stress and safety tests
- **Zero Dependencies**: Uses only Go standard library

## Installation

```bash
go get github.com/example/bplustree
```

## Quick Start

```go
package main

import (
    "fmt"
    "github.com/example/bplustree/internal/bplustree"
)

func main() {
    // Create a B+ tree with int keys and string values
    tree := bplustree.New[int, string](128) // capacity = 128
    
    // Insert key-value pairs
    tree.Insert(42, "answer")
    tree.Insert(1, "one")
    tree.Insert(100, "hundred")
    
    // Lookup values
    if value, found := tree.Get(42); found {
        fmt.Printf("Found: %s\n", value)
    }
    
    // Range query
    results := tree.Range(1, 100)
    for _, entry := range results {
        fmt.Printf("%d: %s\n", entry.Key, entry.Value)
    }
    
    // Iterate over all entries
    iter := tree.Iterator()
    for iter.Next() {
        fmt.Printf("%d: %s\n", iter.Key(), iter.Value())
    }
}
```

## API Reference

### Creating a Tree

```go
tree := bplustree.New[K, V](capacity)
```

- `K`: Key type (must satisfy `cmp.Ordered` constraint)
- `V`: Value type (can be any type)
- `capacity`: Maximum keys per node (minimum 3, recommended 128)

### Basic Operations

```go
// Insert or update
tree.Insert(key, value)

// Lookup
value, found := tree.Get(key)

// Check existence
exists := tree.Contains(key)

// Delete
oldValue, err := tree.Delete(key)

// Get size
count := tree.Len()

// Get height
height := tree.Height()

// Clear all entries
tree.Clear()
```

### Range Queries

```go
// Get all entries where start <= key <= end
entries := tree.Range(startKey, endKey)

for _, entry := range entries {
    fmt.Printf("%v: %v\n", entry.Key, entry.Value)
}
```

### Iteration

```go
// Forward iteration (ascending order)
iter := tree.Iterator()
for iter.Next() {
    key := iter.Key()
    value := iter.Value()
    // Process entry
}

// Reverse iteration (descending order)
revIter := tree.ReverseIterator()
for revIter.Next() {
    key := revIter.Key()
    value := revIter.Value()
    // Process entry
}
```

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Insert | O(log n) | O(1) amortized |
| Search | O(log n) | O(1) |
| Delete | O(log n) | O(1) |
| Range Query | O(log n + k) | O(k) |
| Iteration | O(n) | O(1) |

### Benchmark Results

On Intel Core i9-12900KS (100,000 operations):

| Operation | Performance |
|-----------|-------------|
| Sequential Insert | 1.87 μs/op |
| Random Insert | 1.92 μs/op |
| Sequential Lookup | 174 ns/op |
| Random Lookup | 180 ns/op |
| Contains Check | 175 ns/op |
| Range Query (1000 items) | 8.2 μs |
| Full Iteration | 3.5 ns/item |

## Design Details

### Architecture

The B+ tree implementation uses:
- **Separate node types**: Branch nodes for navigation, leaf nodes for data storage
- **Linked leaves**: Doubly-linked leaf nodes for efficient range queries
- **Dynamic balancing**: Automatic node splitting and merging
- **Generic types**: Type-safe operations with compile-time checks

### Node Structure

```go
type node[K cmp.Ordered, V any] struct {
    nodeType nodeType        // leaf or branch
    keys     []K            // Sorted keys
    
    // For leaf nodes
    values []V              // Corresponding values
    next   *node[K, V]      // Next leaf link
    prev   *node[K, V]      // Previous leaf link
    
    // For branch nodes
    children []*node[K, V]  // Child pointers
}
```

### Capacity Tuning

The capacity parameter affects performance:
- **Small (4-16)**: More tree levels, more rebalancing
- **Medium (32-64)**: Balanced for mixed workloads
- **Large (128-256)**: Better for read-heavy workloads
- **Very Large (512+)**: Maximum read performance

Recommended default: **128**

## Building and Testing

### Run Tests

```bash
# Run all tests
go test ./...

# Run with coverage
go test -cover ./...

# Run specific test suite
go test ./internal/bplustree -v
go test ./test -v              # Stress tests
```

### Run Benchmarks

```bash
# Run all benchmarks
go test -bench=. ./benchmark

# Run specific benchmark
go test -bench=BenchmarkSequentialInsert ./benchmark

# Run with memory profiling
go test -bench=. -benchmem ./benchmark
```

### Run Demo

```bash
go run cmd/demo/main.go
```

## Test Coverage

The implementation includes comprehensive testing:

1. **Unit Tests** (27 tests)
   - Basic operations
   - Edge cases
   - Node splitting/merging
   - Error conditions

2. **Stress Tests** (7 tests)
   - Random operations (10k+)
   - Large datasets (100k+)
   - Concurrent operations
   - Memory pressure

3. **Iterator Safety** (7 tests)
   - Modifications during iteration
   - Iterator invalidation
   - Concurrent iterators

## Advanced Usage

### Custom Key Types

Any type satisfying `cmp.Ordered` can be used as a key:

```go
// String keys
stringTree := bplustree.New[string, int](128)

// Float keys
floatTree := bplustree.New[float64, string](128)

// Time keys
timeTree := bplustree.New[time.Time, Event](128)
```

### Iterator Safety

Iterators in Go hold references to nodes and remain valid during tree modifications:

```go
iter := tree.Iterator()
for iter.Next() {
    // Safe to modify tree during iteration
    tree.Insert(newKey, newValue)
    
    // Current iteration continues with snapshot
    key := iter.Key()
}
```

### Memory Efficiency

The implementation is memory-efficient:
- Nodes allocated only when needed
- Slices used for dynamic arrays
- No unnecessary copying during rebalancing

## Comparison with Other Implementations

| Feature | Go B+ Tree | Go map | [google/btree](https://github.com/google/btree) |
|---------|------------|--------|----------------|
| Ordered Keys | ✓ | ✗ | ✓ |
| Range Queries | ✓ | ✗ | ✓ |
| Generics | ✓ | ✓ | ✗ |
| Iterator Safety | ✓ | ✗ | ✗ |
| Reverse Iteration | ✓ | ✗ | ✗ |

## Contributing

When contributing:
1. Follow TDD methodology - write tests first
2. Ensure all tests pass
3. Add benchmarks for performance-critical changes
4. Update documentation as needed
5. Follow Go best practices and idioms

## Implementation Notes

This implementation follows the same design principles as the Rust and Python versions in this repository:
- Arena-based allocation pattern (using slices)
- Linked leaf nodes for range efficiency
- Optimized node merging/splitting
- Comprehensive test coverage

The Go version leverages:
- Type parameters for compile-time safety
- Slice operations for efficiency
- Standard library constraints
- Idiomatic error handling

## License

See the main project LICENSE file.