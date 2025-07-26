# B+ Tree Zig API Reference

## Module Import

```zig
const bplustree = @import("bplustree");
const BPlusTree = bplustree.BPlusTree;
```

## Type Definition

### `BPlusTree(comptime K: type, comptime V: type) type`

Creates a generic B+ tree type for the specified key and value types.

**Type Parameters:**
- `K`: The key type (must support comparison operators)
- `V`: The value type

**Example:**
```zig
// Integer keys, string values
const IntStringTree = BPlusTree(i32, []const u8);

// String keys, struct values
const Person = struct { name: []const u8, age: u32 };
const StringPersonTree = BPlusTree([]const u8, Person);
```

## Initialization

### `init(allocator: std.mem.Allocator, capacity: usize) Self`

Creates a new empty B+ tree instance.

**Parameters:**
- `allocator`: Memory allocator for all tree operations
- `capacity`: Maximum number of keys per node (minimum 3)

**Returns:** A new B+ tree instance

**Example:**
```zig
const std = @import("std");
var gpa = std.heap.GeneralPurposeAllocator(.{}){};
const allocator = gpa.allocator();

var tree = BPlusTree(i32, []const u8).init(allocator, 128);
```

## Cleanup

### `deinit(self: *Self) void`

Destroys the tree and frees all allocated memory.

**Parameters:**
- `self`: The tree instance to destroy

**Example:**
```zig
var tree = BPlusTree(i32, []const u8).init(allocator, 128);
defer tree.deinit();
```

## Core Operations

### `insert(self: *Self, key: KeyType, value: ValueType) !void`

Inserts a key-value pair into the tree. If the key already exists, updates its value.

**Parameters:**
- `self`: The tree instance
- `key`: The key to insert
- `value`: The value to associate with the key

**Errors:**
- `OutOfMemory`: If allocation fails

**Behavior:**
- Maintains sorted order
- Handles duplicate keys by updating value
- Automatically splits nodes when capacity exceeded
- Tree remains balanced

**Example:**
```zig
try tree.insert(42, "forty-two");
try tree.insert(10, "ten");
try tree.insert(42, "updated"); // Updates existing key
```

### `get(self: *const Self, key: KeyType) ?ValueType`

Retrieves the value associated with a key.

**Parameters:**
- `self`: The tree instance
- `key`: The key to search for

**Returns:** 
- The value if key exists
- `null` if key not found

**Example:**
```zig
if (tree.get(42)) |value| {
    std.debug.print("Found: {s}\n", .{value});
} else {
    std.debug.print("Key not found\n", .{});
}

// Direct usage (careful with null)
const value = tree.get(42) orelse "default";
```

## Tree Information

### `len(self: *const Self) usize`

Returns the number of key-value pairs in the tree.

**Parameters:**
- `self`: The tree instance

**Returns:** Number of entries

**Example:**
```zig
const count = tree.len();
std.debug.print("Tree contains {} items\n", .{count});
```

### `getHeight(self: *const Self) usize`

Returns the height of the tree (number of levels).

**Parameters:**
- `self`: The tree instance

**Returns:** 
- 0 for empty tree
- 1 for single leaf node
- 2+ for trees with branch nodes

**Example:**
```zig
const height = tree.getHeight();
std.debug.print("Tree height: {}\n", .{height});
```

## Usage Patterns

### Basic Usage

```zig
const std = @import("std");
const BPlusTree = @import("bplustree").BPlusTree;

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    
    // Create tree
    var tree = BPlusTree(i32, []const u8).init(allocator, 128);
    defer tree.deinit();
    
    // Insert data
    try tree.insert(30, "thirty");
    try tree.insert(10, "ten");
    try tree.insert(20, "twenty");
    
    // Retrieve data
    if (tree.get(20)) |value| {
        std.debug.print("20 = {s}\n", .{value});
    }
    
    // Check size
    std.debug.print("Size: {}\n", .{tree.len()});
}
```

### Error Handling

```zig
// Handle insertion errors
tree.insert(key, value) catch |err| {
    switch (err) {
        error.OutOfMemory => {
            std.debug.print("Memory allocation failed\n", .{});
            return err;
        },
    }
};

// Safe retrieval with default
const value = tree.get(key) orelse default_value;
```

### Custom Types

```zig
// Custom struct as value
const Student = struct {
    id: u32,
    name: []const u8,
    gpa: f32,
};

var students = BPlusTree(u32, Student).init(allocator, 64);
defer students.deinit();

try students.insert(1001, .{
    .id = 1001,
    .name = "Alice",
    .gpa = 3.8,
});

if (students.get(1001)) |student| {
    std.debug.print("Student: {} - {s} (GPA: {d:.2})\n", 
        .{student.id, student.name, student.gpa});
}
```

### Checking Operations

```zig
// Before insertion
const size_before = tree.len();
const exists = tree.get(key) != null;

// Insert
try tree.insert(key, value);

// After insertion
const size_after = tree.len();
const was_update = (size_before == size_after);

if (was_update) {
    std.debug.print("Updated existing key\n", .{});
} else {
    std.debug.print("Inserted new key\n", .{});
}
```

## Performance Considerations

### Capacity Selection

The capacity parameter affects performance:

```zig
// Small capacity (4-8): More tree levels, frequent splits
var small_tree = BPlusTree(i32, i32).init(allocator, 4);

// Medium capacity (32-128): Balanced performance
var medium_tree = BPlusTree(i32, i32).init(allocator, 64);

// Large capacity (256+): Fewer levels, better cache usage
var large_tree = BPlusTree(i32, i32).init(allocator, 256);
```

**Guidelines:**
- Small datasets (<1000 items): capacity 32-64
- Medium datasets (<100K items): capacity 128
- Large datasets: capacity 256-512
- Consider key/value sizes when choosing

### Memory Usage

Approximate memory per node:
```
Node overhead + (capacity × sizeof(Key)) + (capacity × sizeof(Value or *Node))
```

### Best Practices

1. **Reuse Trees**: Create once, insert many times
2. **Batch Operations**: Group related insertions
3. **Check Existence**: Use `get()` before insert if needed
4. **Appropriate Types**: Use small key types when possible

## Limitations

### Current Limitations
- No deletion support
- No range query support
- No iterator support
- No concurrent access safety
- No persistence

### Key Type Requirements
Keys must support:
- Comparison operators (`<`, `==`)
- Copy semantics

### Value Type Requirements
Values must support:
- Copy or move semantics
- No special requirements

## Examples

### Integer to Integer Mapping
```zig
var map = BPlusTree(u32, u32).init(allocator, 128);
defer map.deinit();

// Insert squares
for (1..11) |i| {
    try map.insert(@intCast(i), @intCast(i * i));
}

// Retrieve
if (map.get(5)) |square| {
    std.debug.print("5^2 = {}\n", .{square}); // Prints: 5^2 = 25
}
```

### String Index
```zig
var index = BPlusTree([]const u8, usize).init(allocator, 64);
defer index.deinit();

const words = [_][]const u8{ "apple", "banana", "cherry" };
for (words, 0..) |word, i| {
    try index.insert(word, i);
}

if (index.get("banana")) |pos| {
    std.debug.print("'banana' is at position {}\n", .{pos});
}
```

### Configuration Storage
```zig
const Config = struct {
    value: []const u8,
    modified: i64,
};

var config = BPlusTree([]const u8, Config).init(allocator, 32);
defer config.deinit();

try config.insert("timeout", .{
    .value = "30s",
    .modified = std.time.timestamp(),
});

if (config.get("timeout")) |setting| {
    std.debug.print("timeout = {s} (modified: {})\n", 
        .{setting.value, setting.modified});
}
```

## Future API (Planned)

### Deletion
```zig
pub fn remove(self: *Self, key: KeyType) ?ValueType
```

### Range Queries
```zig
pub fn range(self: *Self, start: KeyType, end: KeyType) RangeIterator
```

### Iteration
```zig
pub fn iterator(self: *Self) Iterator
pub fn reverseIterator(self: *Self) ReverseIterator
```

### Bulk Operations
```zig
pub fn insertMany(self: *Self, items: []const KVPair) !void
pub fn fromSorted(allocator: Allocator, items: []const KVPair, capacity: usize) !Self
```