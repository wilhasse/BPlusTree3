# B+ Tree Zig Implementation - Detailed Architecture

## Table of Contents
1. [Overview](#overview)
2. [Data Structures](#data-structures)
3. [Core Algorithms](#core-algorithms)
4. [Memory Management](#memory-management)
5. [Design Decisions](#design-decisions)
6. [Performance Optimizations](#performance-optimizations)

## Overview

The Zig B+ tree implementation is a self-balancing tree data structure that maintains sorted data and allows searches, sequential access, insertions, and deletions in logarithmic time.

### Key Properties
- All data is stored in leaf nodes
- Internal nodes only store keys for routing
- Leaf nodes are linked for efficient range queries
- All leaves are at the same depth
- Nodes split when they exceed capacity

## Data Structures

### Tree Structure

```zig
pub fn BPlusTree(comptime K: type, comptime V: type) type {
    return struct {
        allocator: std.mem.Allocator,  // Memory allocator
        capacity: usize,               // Max keys per node
        size: usize,                   // Total key-value pairs
        root: ?*Node,                  // Root node (may be null)
    };
}
```

### Node Structure

```zig
const Node = struct {
    node_type: NodeType,              // .leaf or .branch
    keys: std.ArrayList(KeyType),     // Sorted keys
    
    // Leaf node fields
    values: ?std.ArrayList(ValueType), // Values (leaf only)
    next: ?*Node,                      // Next leaf link
    prev: ?*Node,                      // Previous leaf link
    
    // Branch node fields
    children: ?std.ArrayList(*Node),   // Child pointers (branch only)
};
```

### Node Types

1. **Leaf Nodes**
   - Store actual key-value pairs
   - Linked to adjacent leaves via next/prev pointers
   - No child pointers

2. **Branch Nodes**
   - Store keys for routing
   - Store pointers to child nodes
   - No values or leaf links

## Core Algorithms

### Insertion Algorithm

```
insert(key, value):
    1. If tree is empty:
        - Create root as leaf node
        
    2. If root is full leaf:
        - Split root
        - Create new root as branch
        
    3. Navigate to correct leaf:
        - Start at root
        - At each branch: find child based on key
        - Continue until leaf reached
        
    4. Insert into leaf:
        - If key exists: update value
        - Else: insert maintaining order
        
    5. If leaf is full:
        - Split leaf
        - Propagate split up tree
```

#### Detailed Insertion Flow

```zig
pub fn insert(self: *Self, key: KeyType, value: ValueType) !void {
    // Handle empty tree
    if (self.root == null) {
        self.root = try Node.initLeaf(self.allocator);
    }
    
    // Handle full root
    if (self.root.?.node_type == .leaf and self.root.?.isFull(self.capacity)) {
        // Split root and create new parent
        const old_root = self.root.?;
        const new_leaf = try self.splitLeaf(old_root);
        
        var new_root = try Node.initBranch(self.allocator);
        try new_root.keys.append(new_leaf.keys.items[0]);
        try new_root.children.?.append(old_root);
        try new_root.children.?.append(new_leaf);
        
        self.root = new_root;
    }
    
    // Insert normally
    try self.insertIntoNode(self.root.?, key, value);
    self.size += 1;
}
```

### Search Algorithm

```
get(key):
    1. Start at root
    2. While current node is branch:
        - Find appropriate child index
        - Move to that child
    3. At leaf node:
        - Linear search for key
        - Return value if found, null otherwise
```

#### Search Implementation

```zig
pub fn get(self: *const Self, key: KeyType) ?ValueType {
    if (self.root == null) return null;
    
    var current = self.root.?;
    
    // Navigate to leaf
    while (current.node_type == .branch) {
        var child_idx: usize = 0;
        for (current.keys.items, 0..) |k, i| {
            if (key < k) break;
            child_idx = i + 1;
        }
        if (child_idx >= current.children.?.items.len) {
            child_idx = current.children.?.items.len - 1;
        }
        current = current.children.?.items[child_idx];
    }
    
    // Search in leaf
    for (current.keys.items, 0..) |k, i| {
        if (k == key) {
            return current.values.?.items[i];
        }
    }
    return null;
}
```

### Node Splitting Algorithm

```
splitLeaf(leaf):
    1. Create new leaf node
    2. Calculate midpoint
    3. Move half of entries to new leaf
    4. Update leaf links:
        - new.next = leaf.next
        - new.prev = leaf
        - leaf.next = new
        - if new.next: new.next.prev = new
    5. Return new leaf
```

## Memory Management

### Allocation Strategy

1. **Node Allocation**
   - Each node allocated individually via `allocator.create(Node)`
   - ArrayLists for dynamic key/value/child storage

2. **Deallocation**
   - Recursive cleanup from root
   - Each node frees its ArrayLists
   - Parent frees child nodes

### Memory Layout

```
Tree Instance
├── Metadata (capacity, size, allocator)
└── Root Pointer → Node
                   ├── Node Type
                   ├── Keys ArrayList
                   ├── Values ArrayList (leaf)
                   └── Children ArrayList (branch)
```

## Design Decisions

### 1. Generic Implementation
- **Decision**: Use comptime generics for key/value types
- **Rationale**: Zero-cost abstraction, type safety
- **Trade-off**: Longer compile times for many instantiations

### 2. ArrayList for Node Storage
- **Decision**: Use `std.ArrayList` for keys/values/children
- **Rationale**: Dynamic sizing, familiar API
- **Trade-off**: Some overhead vs fixed arrays

### 3. Separate Node Types
- **Decision**: Single Node struct with optional fields
- **Rationale**: Simpler than tagged union, less type juggling
- **Trade-off**: Some memory overhead for unused fields

### 4. Linked Leaf Nodes
- **Decision**: Doubly-linked leaf nodes
- **Rationale**: Efficient range queries, forward/backward iteration
- **Trade-off**: Extra memory per leaf, maintenance complexity

### 5. Eager Splitting
- **Decision**: Split nodes when full before insertion
- **Rationale**: Simpler logic, predictable behavior
- **Trade-off**: May split unnecessarily if updating existing key

## Performance Optimizations

### 1. Cache-Friendly Access
- Keys stored contiguously in ArrayList
- Sequential search within nodes utilizes cache lines
- Minimizes pointer chasing

### 2. Balanced Tree Structure
- All operations O(log n) due to balanced nature
- Height grows logarithmically with data size

### 3. Bulk Operations (Planned)
- Future: Batch insertions with single rebalance
- Future: Optimized bulk loading for sorted data

### 4. Memory Pooling (Potential)
- Could implement node pooling to reduce allocations
- Reuse freed nodes instead of deallocating

## Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Insert    | O(log n)       | O(1) amortized  |
| Search    | O(log n)       | O(1)            |
| Delete    | O(log n)*      | O(1)            |
| Range     | O(log n + k)*  | O(k)            |

*Not yet implemented

Where:
- n = number of keys in tree
- k = number of keys in range

## Future Enhancements

### 1. Deletion Support
- Implement key removal
- Handle node merging/redistribution
- Maintain tree invariants

### 2. Iterator Support
```zig
const Iterator = struct {
    current: ?*Node,
    index: usize,
    
    pub fn next(self: *Iterator) ?KVPair {
        // Implementation
    }
};
```

### 3. Range Queries
```zig
pub fn range(self: *Self, start: KeyType, end: KeyType) RangeIterator {
    // Navigate to start leaf
    // Return iterator that follows leaf links
}
```

### 4. Concurrent Access
- Read-write locks per node
- Copy-on-write for concurrent readers
- Lock-free leaf traversal

### 5. Persistence
- Serialize/deserialize to disk
- Memory-mapped file support
- Write-ahead logging

## Code Examples

### Creating a Tree
```zig
var tree = BPlusTree(i32, []const u8).init(allocator, 128);
defer tree.deinit();
```

### Batch Insertion Pattern
```zig
const items = [_]struct { key: i32, value: []const u8 }{
    .{ .key = 10, .value = "ten" },
    .{ .key = 20, .value = "twenty" },
    .{ .key = 30, .value = "thirty" },
};

for (items) |item| {
    try tree.insert(item.key, item.value);
}
```

### Safe Value Retrieval
```zig
if (tree.get(key)) |value| {
    // Use value
} else {
    // Handle not found
}
```

## Testing Strategy

### Unit Tests
- Each core operation tested in isolation
- Edge cases (empty tree, single element, full nodes)
- Invariant checking after operations

### Integration Tests
- Complex sequences of operations
- Large data sets
- Performance benchmarks

### Property-Based Tests (Future)
- Random operation sequences
- Invariant preservation
- Comparison with reference implementation