# B+ Tree Testing Guide

## Overview

This guide covers the testing approach, current test coverage, and guidelines for adding new tests to the B+ tree implementation.

## Running Tests

### Basic Test Execution

```bash
# Run all tests
zig build test

# Run tests with verbose output
zig build test --summary all

# Run specific test file (if separated)
zig test tests/test_bplustree.zig
```

## Current Test Coverage

### Implemented Tests

#### 1. Empty Tree Creation
```zig
test "should create empty B+ tree" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    try testing.expectEqual(@as(usize, 0), tree.len());
}
```
**Tests:** 
- Tree initialization
- Empty tree has zero length
- Memory allocation/deallocation

#### 2. Single Key-Value Insertion
```zig
test "should insert single key-value pair" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    try tree.insert(42, 100);
    
    try testing.expectEqual(@as(usize, 1), tree.len());
}
```
**Tests:**
- Basic insertion
- Size increment
- No errors on valid input

#### 3. Value Retrieval
```zig
test "should retrieve inserted value" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    try tree.insert(42, 100);
    
    const value = tree.get(42);
    try testing.expect(value != null);
    try testing.expectEqual(@as(i32, 100), value.?);
}
```
**Tests:**
- Successful retrieval
- Correct value returned
- Non-null result for existing key

#### 4. Multiple Insertions
```zig
test "should handle multiple insertions and maintain order" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    try tree.insert(5, 50);
    try tree.insert(3, 30);
    try tree.insert(7, 70);
    try tree.insert(1, 10);
    
    try testing.expectEqual(@as(usize, 4), tree.len());
    
    try testing.expectEqual(@as(i32, 10), tree.get(1).?);
    try testing.expectEqual(@as(i32, 30), tree.get(3).?);
    try testing.expectEqual(@as(i32, 50), tree.get(5).?);
    try testing.expectEqual(@as(i32, 70), tree.get(7).?);
}
```
**Tests:**
- Multiple insertions
- Maintained sorted order
- All values retrievable
- Correct size tracking

#### 5. Duplicate Key Handling
```zig
test "should update value for duplicate key" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    try tree.insert(42, 100);
    try tree.insert(42, 200);
    
    try testing.expectEqual(@as(usize, 1), tree.len());
    try testing.expectEqual(@as(i32, 200), tree.get(42).?);
}
```
**Tests:**
- Value update on duplicate key
- Size remains constant
- Latest value retained

#### 6. Non-existent Key Retrieval
```zig
test "should return null for non-existent key" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    try testing.expect(tree.get(42) == null);
    
    try tree.insert(10, 100);
    try tree.insert(20, 200);
    try tree.insert(30, 300);
    
    try testing.expect(tree.get(5) == null);    // Before first
    try testing.expect(tree.get(15) == null);   // Between keys
    try testing.expect(tree.get(40) == null);   // After last
}
```
**Tests:**
- Null return for missing keys
- Empty tree behavior
- Non-existent keys at various positions

#### 7. Node Splitting
```zig
test "should handle node splitting when capacity exceeded" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    try tree.insert(10, 100);
    try tree.insert(20, 200);
    try tree.insert(30, 300);
    try tree.insert(40, 400);
    try tree.insert(50, 500); // Triggers split
    
    try testing.expectEqual(@as(usize, 5), tree.len());
    
    try testing.expectEqual(@as(i32, 100), tree.get(10).?);
    try testing.expectEqual(@as(i32, 200), tree.get(20).?);
    try testing.expectEqual(@as(i32, 300), tree.get(30).?);
    try testing.expectEqual(@as(i32, 400), tree.get(40).?);
    try testing.expectEqual(@as(i32, 500), tree.get(50).?);
    
    try testing.expect(tree.getHeight() > 1);
}
```
**Tests:**
- Node splitting on overflow
- Tree structure integrity
- Height increase
- Data preservation after split

## Test Writing Guidelines

### Test Structure

```zig
test "should [expected behavior]" {
    // 1. Setup
    const allocator = testing.allocator;
    var tree = bplustree.BPlusTree(KeyType, ValueType).init(allocator, capacity);
    defer tree.deinit();
    
    // 2. Action
    try tree.insert(key, value);
    
    // 3. Assert
    try testing.expectEqual(expected, actual);
}
```

### Best Practices

1. **Descriptive Names**: Use "should..." pattern
2. **Single Concern**: Test one behavior per test
3. **Setup-Action-Assert**: Clear test structure
4. **Resource Cleanup**: Always use `defer tree.deinit()`
5. **Edge Cases**: Test boundaries and special cases

### Common Test Patterns

#### Testing Error Conditions
```zig
test "should handle allocation failure gracefully" {
    var failing_allocator = testing.FailingAllocator.init(testing.allocator, 0);
    
    var tree = bplustree.BPlusTree(i32, i32).init(failing_allocator.allocator(), 4);
    defer tree.deinit();
    
    // Should return OutOfMemory error
    try testing.expectError(error.OutOfMemory, tree.insert(1, 1));
}
```

#### Testing Invariants
```zig
test "should maintain tree invariants after operations" {
    // After insertions:
    // - All leaves at same depth
    // - Keys in sorted order
    // - Node capacity respected
}
```

#### Performance Tests
```zig
test "should handle large datasets efficiently" {
    const allocator = testing.allocator;
    var tree = bplustree.BPlusTree(u32, u32).init(allocator, 128);
    defer tree.deinit();
    
    const n = 10000;
    var timer = try std.time.Timer.start();
    
    for (0..n) |i| {
        try tree.insert(@intCast(i), @intCast(i * 2));
    }
    
    const elapsed = timer.read();
    std.debug.print("Inserted {} items in {}ns\n", .{n, elapsed});
    
    try testing.expect(tree.len() == n);
}
```

## Future Tests to Implement

### Deletion Tests
```zig
test "should delete existing key"
test "should handle deletion from leaf node"
test "should handle deletion causing node merge"
test "should maintain tree balance after deletion"
```

### Range Query Tests
```zig
test "should return empty range for non-existent keys"
test "should return all keys in range"
test "should handle partial ranges"
test "should support inclusive/exclusive bounds"
```

### Iterator Tests
```zig
test "should iterate all keys in order"
test "should support reverse iteration"
test "should handle modifications during iteration"
test "should provide key-value pairs"
```

### Stress Tests
```zig
test "should handle random operations"
test "should maintain consistency under load"
test "should handle worst-case scenarios"
test "should recover from errors gracefully"
```

### Edge Case Tests
```zig
test "should handle minimum capacity (3)"
test "should handle very large capacity"
test "should handle all keys being identical"
test "should handle alternating insert/delete"
```

## Property-Based Testing (Future)

```zig
test "tree properties hold for random operations" {
    // Properties to verify:
    // 1. Sorted order maintained
    // 2. All inserted keys retrievable
    // 3. Tree height = O(log n)
    // 4. Node capacity constraints met
}
```

## Benchmarking

### Basic Benchmark Structure
```zig
test "benchmark insertion performance" {
    const sizes = [_]usize{ 100, 1000, 10000, 100000 };
    const capacities = [_]usize{ 4, 16, 64, 128, 256 };
    
    for (capacities) |capacity| {
        for (sizes) |size| {
            // Benchmark with given parameters
            // Report time and memory usage
        }
    }
}
```

### Comparison Benchmarks
```zig
test "compare with std.hash_map" {
    // Benchmark equivalent operations
    // Compare performance characteristics
}
```

## Test Coverage Analysis

### Current Coverage
- ✅ Basic operations (insert, get, len)
- ✅ Empty tree handling
- ✅ Node splitting
- ✅ Duplicate key handling
- ❌ Deletion
- ❌ Range queries
- ❌ Iterators
- ❌ Concurrent access
- ❌ Error recovery

### Adding New Tests

When adding features:
1. Write failing test first (Red)
2. Implement minimal code to pass (Green)
3. Refactor if needed (Refactor)
4. Ensure all existing tests still pass

## Debugging Failed Tests

### Common Issues

1. **Memory Leaks**
   ```bash
   # Run with leak detection
   zig build test --verbose-link
   ```

2. **Assertion Failures**
   - Check expected vs actual values
   - Verify test setup is correct
   - Add debug prints if needed

3. **Segmentation Faults**
   - Check null pointer access
   - Verify array bounds
   - Use debug allocator

### Debug Helpers

```zig
// Add temporary debug function
fn debugPrintTree(tree: *const Self) void {
    std.debug.print("Tree: size={}, height={}\n", .{tree.len(), tree.getHeight()});
    // Print tree structure
}

// Use in tests
test "debug failing test" {
    // ... setup ...
    
    debugPrintTree(&tree);
    
    // ... assertions ...
}
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: goto-bus-stop/setup-zig@v2
      - run: zig build test
```

## Contributing Tests

When contributing:
1. Follow existing test patterns
2. Add tests for new features
3. Add regression tests for bugs
4. Update this guide with new test categories
5. Ensure all tests pass before submitting