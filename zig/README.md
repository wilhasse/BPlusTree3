# B+ Tree Implementation in Zig

A high-performance B+ tree implementation in Zig, following Test-Driven Development (TDD) principles. This implementation provides an ordered key-value data structure with efficient insertion, retrieval, and (planned) range query operations.

## Features

### Implemented
- ✅ **Basic B+ Tree Operations**
  - Empty tree creation
  - Key-value insertion with automatic sorting
  - Value retrieval by key
  - Duplicate key handling (updates existing value)
  
- ✅ **Tree Structure**
  - Separate leaf and branch node types
  - Linked leaf nodes for efficient sequential access
  - Automatic node splitting when capacity is exceeded
  - Tree height tracking

- ✅ **Memory Management**
  - Arena-style allocation for nodes
  - Proper cleanup on tree destruction
  - No memory leaks

### Planned
- ❌ Deletion operations
- ❌ Range queries
- ❌ Iterator support
- ❌ Bulk loading
- ❌ Persistence

## Architecture

### Core Design Principles

1. **Generic Implementation**: The tree is parameterized by key and value types
2. **Node Types**: Separate structures for leaf nodes (store data) and branch nodes (store routing info)
3. **Linked Leaves**: Leaf nodes are doubly-linked for efficient range operations
4. **Capacity-Based Splitting**: Nodes split when they reach the configured capacity

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

#### Search
1. Start at root
2. For branch nodes: find appropriate child based on key comparisons
3. Navigate down to leaf level
4. Linear search within leaf node

#### Node Splitting
1. Create new node
2. Move half of entries to new node
3. Update parent with new separator key
4. Maintain leaf node links

## Usage

### Building

```bash
# Build the library
zig build

# Run tests
zig build test
```

### Basic Example

```zig
const std = @import("std");
const BPlusTree = @import("bplustree").BPlusTree;

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    // Create a B+ tree with capacity 128
    var tree = BPlusTree(i32, []const u8).init(allocator, 128);
    defer tree.deinit();
    
    // Insert key-value pairs
    try tree.insert(42, "answer");
    try tree.insert(10, "ten");
    try tree.insert(99, "ninety-nine");
    
    // Retrieve values
    if (tree.get(42)) |value| {
        std.debug.print("Found: {s}\n", .{value});
    }
    
    // Check tree size
    std.debug.print("Tree size: {}\n", .{tree.len()});
}
```

## API Reference

### Types

```zig
pub fn BPlusTree(comptime K: type, comptime V: type) type
```
Creates a generic B+ tree type for the given key and value types.

### Methods

#### `init(allocator: std.mem.Allocator, capacity: usize) Self`
Creates a new empty B+ tree.
- `allocator`: Memory allocator to use
- `capacity`: Maximum number of keys per node (must be >= 3)

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

#### `len(self: *const Self) usize`
Returns the number of key-value pairs in the tree.

#### `getHeight(self: *const Self) usize`
Returns the height of the tree (number of levels).

## Performance Characteristics

- **Insertion**: O(log n)
- **Search**: O(log n)
- **Space**: O(n)
- **Cache-friendly**: Sequential access within nodes

### Capacity Tuning

The capacity parameter affects performance:
- **Small capacity (3-8)**: More tree levels, less memory per node
- **Medium capacity (16-128)**: Balanced performance
- **Large capacity (256+)**: Fewer levels, more memory, better cache utilization

Recommended default: 128 (based on benchmarks from Rust/Python implementations)

## Implementation Details

### Memory Layout

```
Tree Structure:
    Root (Branch)
    ├── Keys: [30, 60]
    └── Children: [↓, ↓, ↓]
                   │  │  │
    ┌─────────────┘  │  └─────────────┐
    ↓                ↓                ↓
  Leaf 1          Leaf 2          Leaf 3
  Keys: [10,20]   Keys: [30,40,50] Keys: [60,70,80]
  Values: [...]   Values: [...]    Values: [...]
  Next: →Leaf2    Next: →Leaf3     Next: null
  Prev: null      Prev: →Leaf1     Prev: →Leaf2
```

### Key Invariants

1. **Sorted Order**: Keys within each node are sorted
2. **Capacity Constraints**: Each node has between ⌈capacity/2⌉ and capacity keys (except root)
3. **Leaf Links**: All leaf nodes are linked in sorted order
4. **Tree Balance**: All leaf nodes are at the same depth

## Testing

The implementation follows strict TDD principles:

```bash
# Run all tests
zig build test

# Tests included:
# - Empty tree creation
# - Single insertion
# - Multiple insertions
# - Duplicate key handling
# - Non-existent key retrieval
# - Node splitting
```

### Test Coverage

- ✅ Basic operations
- ✅ Edge cases (empty tree, single element)
- ✅ Capacity overflow handling
- ❌ Large-scale stress tests (TODO)
- ❌ Concurrent access tests (TODO)

## Development Process

This implementation was developed using Test-Driven Development:

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code structure

Each feature was built incrementally, ensuring all tests pass before moving forward.

## Comparison with Other Implementations

This Zig implementation follows the same design principles as the Rust and Python versions:
- Arena-based memory management
- Linked leaf nodes
- Optimized for cache locality
- Similar API design

## Future Enhancements

1. **Deletion Support**: Remove keys while maintaining tree invariants
2. **Range Queries**: Efficiently retrieve all keys in a range
3. **Iterators**: Support for forward and reverse iteration
4. **Persistence**: Save/load tree to/from disk
5. **Concurrent Access**: Thread-safe operations
6. **Bulk Operations**: Efficient bulk insert/delete

## Contributing

When contributing, please:
1. Follow TDD principles
2. Write tests before implementation
3. Ensure all tests pass
4. Update documentation

## License

(Add your license here)