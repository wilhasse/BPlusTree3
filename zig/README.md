# B+ Tree Implementation in Zig

A high-performance B+ tree implementation in Zig, following Test-Driven Development (TDD) principles. This implementation provides an ordered key-value data structure with efficient insertion, retrieval, deletion, and range query operations.

## Features

### Fully Implemented ✅
- **Core B+ Tree Operations**
  - Empty tree creation
  - Key-value insertion with automatic sorting
  - Value retrieval by key
  - Key removal with proper rebalancing
  - Duplicate key handling (updates existing value)
  - Tree clearing
  
- **Advanced Features**
  - Range queries with linked leaf traversal
  - Forward and reverse iterators
  - Contains check for key existence
  - Tree height tracking
  - Size tracking
  
- **Tree Structure**
  - Separate leaf and branch node types
  - Linked leaf nodes for efficient sequential access
  - Automatic node splitting when capacity is exceeded
  - Node merging and redistribution during deletion
  - Proper handling of underflow conditions

- **Memory Management**
  - Arena-style allocation for nodes
  - Proper cleanup on tree destruction
  - No memory leaks (verified by test allocator)
  - Iterator safety during modifications

- **Performance**
  - Comprehensive benchmarking suite
  - Optimized for various workloads
  - Cache-friendly sequential access

## Architecture

### Core Design Principles

1. **Generic Implementation**: The tree is parameterized by key and value types
2. **Node Types**: Separate structures for leaf nodes (store data) and branch nodes (store routing info)
3. **Linked Leaves**: Leaf nodes are doubly-linked for efficient range operations
4. **Capacity-Based Operations**: Nodes split/merge based on configurable capacity

### Node Structure

```zig
const Node = struct {
    node_type: NodeType,           // Either .leaf or .branch
    keys: std.ArrayList(KeyType),   // Sorted keys
    
    // For leaf nodes only
    values: ?std.ArrayList(ValueType),  // Corresponding values
    next: ?*Node,                       // Link to next leaf
    prev: ?*Node,                       // Link to previous leaf
    
    // For branch nodes only
    children: ?std.ArrayList(*Node),    // Child pointers
};
```

### Key Algorithms

#### Insertion
1. If tree is empty, create a root leaf node
2. If root is full and is a leaf, split it and create new root
3. Navigate to appropriate leaf node
4. Insert key-value pair maintaining sorted order
5. If node becomes full, split it and propagate split upward

#### Deletion
1. Navigate to leaf containing the key
2. Remove key-value pair
3. If node underflows, try redistribution from siblings
4. If redistribution fails, merge with sibling
5. Propagate merges up the tree if needed
6. Adjust root if it becomes empty

#### Range Query
1. Navigate to first leaf that could contain start key
2. Traverse linked leaves collecting matching entries
3. Stop when key exceeds end of range

## Usage

### Building

```bash
# Build the library
zig build

# Run all tests (40+ tests)
zig build test

# Run specific test suites
zig build test-stress     # Stress tests
zig build test-iterator   # Iterator safety tests
zig build test-deletion   # Deletion logic tests
zig build test-memory     # Memory safety tests

# Run demo
zig build demo

# Run benchmarks
zig build benchmark
```

### Complete Example

```zig
const std = @import("std");
const BPlusTree = @import("bplustree").BPlusTree;

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    // Create a B+ tree with i32 keys and []const u8 values
    const Tree = BPlusTree(i32, []const u8);
    var tree = Tree.init(allocator, 128);
    defer tree.deinit();
    
    // Insert key-value pairs
    try tree.insert(42, "answer");
    try tree.insert(10, "ten");
    try tree.insert(99, "ninety-nine");
    try tree.insert(50, "fifty");
    
    // Retrieve values
    if (tree.get(42)) |value| {
        std.debug.print("Found: {s}\n", .{value});
    }
    
    // Check existence
    if (tree.contains(50)) {
        std.debug.print("Tree contains key 50\n", .{});
    }
    
    // Remove a key
    const removed = try tree.remove(10);
    std.debug.print("Removed value: {s}\n", .{removed});
    
    // Range query
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    try tree.range(40, 60, &results);
    
    for (results.items) |entry| {
        std.debug.print("Range result: {} = {s}\n", .{entry.key, entry.value});
    }
    
    // Forward iteration
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        std.debug.print("Forward: {} = {s}\n", .{entry.key, entry.value});
    }
    
    // Reverse iteration
    var rev_iter = tree.reverseIterator();
    while (rev_iter.next()) |entry| {
        std.debug.print("Reverse: {} = {s}\n", .{entry.key, entry.value});
    }
    
    // Clear the tree
    tree.clear();
    std.debug.print("Tree size after clear: {}\n", .{tree.len()});
}
```

## API Reference

### Types

```zig
pub fn BPlusTree(comptime K: type, comptime V: type) type
```
Creates a generic B+ tree type for the given key and value types.

### Core Methods

#### `init(allocator: std.mem.Allocator, capacity: usize) Self`
Creates a new empty B+ tree.
- `allocator`: Memory allocator to use
- `capacity`: Maximum number of keys per node (minimum 3)

#### `deinit(self: *Self) void`
Destroys the tree and frees all allocated memory.

#### `insert(self: *Self, key: KeyType, value: ValueType) !void`
Inserts or updates a key-value pair.
- If key exists, updates the value
- Maintains sorted order
- May trigger node splits

#### `get(self: *const Self, key: KeyType) ?ValueType`
Retrieves the value associated with a key.
- Returns `null` if key not found
- O(log n) complexity

#### `remove(self: *Self, key: KeyType) !ValueType`
Removes a key-value pair from the tree.
- Returns the removed value
- Returns `Error.KeyNotFound` if key doesn't exist
- May trigger node merges

#### `contains(self: *const Self, key: KeyType) bool`
Checks if a key exists in the tree.

#### `clear(self: *Self) void`
Removes all entries from the tree.

#### `len(self: *const Self) usize`
Returns the number of key-value pairs in the tree.

#### `getHeight(self: *const Self) usize`
Returns the height of the tree (number of levels).

### Range and Iteration

#### `range(self: *const Self, start: KeyType, end: KeyType, results: *std.ArrayList(Entry)) !void`
Retrieves all entries where `start <= key <= end`.
- Results are appended to the provided ArrayList
- Maintains sorted order

#### `iterator(self: *const Self) Iterator`
Returns a forward iterator (ascending order).

#### `reverseIterator(self: *const Self) ReverseIterator`
Returns a reverse iterator (descending order).

### Entry Type

```zig
pub const Entry = struct {
    key: KeyType,
    value: ValueType,
};
```

## Performance Characteristics

- **Insertion**: O(log n)
- **Search**: O(log n)
- **Deletion**: O(log n)
- **Range Query**: O(log n + k) where k is the number of results
- **Iteration**: O(n)
- **Space**: O(n)

### Benchmark Results (100,000 operations)

| Operation | Time | Throughput |
|-----------|------|------------|
| Sequential Insert | ~165 ns/op | 6M ops/sec |
| Random Insert | ~185 ns/op | 5.4M ops/sec |
| Random Lookup | ~165 ns/op | 6M ops/sec |
| Sequential Contains | ~3.8 ns/op | 260M ops/sec |
| Random Deletion | ~400 ns/op | 2.5M ops/sec |
| Range Query (1000) | ~7.5 μs | 133K queries/sec |
| Full Iteration | ~3.1 ns/op | 320M ops/sec |

### Capacity Tuning

The capacity parameter significantly affects performance:
- **Small (4-8)**: More tree levels, more frequent rebalancing
- **Medium (16-64)**: Balanced performance for most use cases
- **Large (128-256)**: Fewer levels, better cache utilization, recommended default
- **Very Large (512+)**: Best for read-heavy workloads

Benchmarks show 128 provides optimal performance (3.3x faster than capacity 4).

## Memory Safety

The implementation has been thoroughly tested for memory safety:
- No memory leaks detected by Zig's test allocator
- Safe handling of node allocation/deallocation
- Proper cleanup during tree destruction
- Iterator invalidation is handled gracefully

## Testing

Comprehensive test coverage with 40+ tests across multiple categories:

### Test Suites

1. **Basic Operations** (18 tests)
   - Tree creation, insertion, retrieval
   - Deletion, clearing, utilities
   - Forward and reverse iteration

2. **Stress Tests** (7 tests)
   - Random operations (10,000+ ops)
   - Large datasets (100,000+ items)
   - Edge cases (min/max capacity)
   - Extreme scenarios

3. **Iterator Safety** (7 tests)
   - Modifications during iteration
   - Concurrent iterators
   - Iterator invalidation

4. **Advanced Deletion** (5 tests)
   - Node underflow handling
   - Key redistribution
   - Node merging
   - Cascading operations

5. **Memory Safety** (7 tests)
   - Leak detection
   - Heavy splitting/merging
   - Repeated operations
   - Stress testing

## Development Process

This implementation was developed using strict Test-Driven Development:

1. **Red**: Write a failing test for new functionality
2. **Green**: Implement minimal code to pass the test
3. **Refactor**: Improve code structure while keeping tests green

Each feature was built incrementally with comprehensive test coverage.

## Key Implementation Decisions

1. **Generic Types**: Maximum flexibility for different use cases
2. **Linked Leaves**: Optimizes range queries and iteration
3. **Configurable Capacity**: Allows performance tuning
4. **Arena Allocation**: Efficient memory management
5. **Test-First Development**: Ensures correctness and reliability

## Contributing

When contributing, please:
1. Follow TDD principles - write tests first
2. Ensure all tests pass before submitting
3. Add tests for new functionality
4. Update documentation as needed
5. Run the test allocator to check for memory leaks

## License

See the main project LICENSE file.