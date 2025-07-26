const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "should handle extreme i32 key values" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Test with min and max i32 values
    const min_i32 = std.math.minInt(i32);
    const max_i32 = std.math.maxInt(i32);
    
    // Insert extreme values
    try tree.insert(min_i32, -1);
    try tree.insert(max_i32, 1);
    try tree.insert(0, 0);
    
    // Verify retrieval
    try testing.expectEqual(@as(i32, -1), tree.get(min_i32).?);
    try testing.expectEqual(@as(i32, 1), tree.get(max_i32).?);
    try testing.expectEqual(@as(i32, 0), tree.get(0).?);
    
    // Test ordering with iterator
    var entries = std.ArrayList(Tree.Entry).init(allocator);
    defer entries.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try entries.append(entry);
    }
    
    try testing.expectEqual(@as(usize, 3), entries.items.len);
    try testing.expectEqual(min_i32, entries.items[0].key);
    try testing.expectEqual(@as(i32, 0), entries.items[1].key);
    try testing.expectEqual(max_i32, entries.items[2].key);
}

test "should handle extreme u64 key values" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(u64, u64);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Test with min and max u64 values
    const min_u64: u64 = 0;
    const max_u64 = std.math.maxInt(u64);
    
    // Insert extreme values
    try tree.insert(min_u64, 100);
    try tree.insert(max_u64, 200);
    try tree.insert(max_u64 / 2, 150);
    
    // Verify retrieval
    try testing.expectEqual(@as(u64, 100), tree.get(min_u64).?);
    try testing.expectEqual(@as(u64, 200), tree.get(max_u64).?);
    try testing.expectEqual(@as(u64, 150), tree.get(max_u64 / 2).?);
    
    // Test ordering
    var entries = std.ArrayList(Tree.Entry).init(allocator);
    defer entries.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try entries.append(entry);
    }
    
    try testing.expectEqual(@as(usize, 3), entries.items.len);
    try testing.expectEqual(min_u64, entries.items[0].key);
    try testing.expectEqual(max_u64 / 2, entries.items[1].key);
    try testing.expectEqual(max_u64, entries.items[2].key);
}

test "should handle all same key insertions" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert same key multiple times with different values
    const key = 42;
    for (0..10) |i| {
        try tree.insert(key, @intCast(i));
    }
    
    // Should only have one entry
    try testing.expectEqual(@as(usize, 1), tree.len());
    
    // Should have the last value
    try testing.expectEqual(@as(i32, 9), tree.get(key).?);
}

test "should handle alternating min/max insertions" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Alternating insertions to stress tree structure
    for (0..20) |i| {
        if (i % 2 == 0) {
            try tree.insert(@intCast(i), @intCast(i));
        } else {
            try tree.insert(@intCast(1000 - i), @intCast(1000 - i));
        }
    }
    
    try testing.expectEqual(@as(usize, 20), tree.len());
    
    // Verify all keys are present
    for (0..20) |i| {
        if (i % 2 == 0) {
            try testing.expectEqual(@as(i32, @intCast(i)), tree.get(@intCast(i)).?);
        } else {
            const key: i32 = @intCast(1000 - i);
            try testing.expectEqual(key, tree.get(key).?);
        }
    }
}

test "should handle sequential insertions at boundaries" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 2); // Minimum capacity
    defer tree.deinit();
    
    // Insert enough to cause multiple splits
    for (0..100) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    try testing.expectEqual(@as(usize, 100), tree.len());
    
    // Verify structure integrity
    for (0..100) |i| {
        try testing.expectEqual(@as(i32, @intCast(i * 10)), tree.get(@intCast(i)).?);
    }
}

test "should handle reverse sequential insertions" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert in reverse order
    var i: i32 = 99;
    while (i >= 0) : (i -= 1) {
        try tree.insert(i, i * 10);
    }
    
    try testing.expectEqual(@as(usize, 100), tree.len());
    
    // Verify ascending order with iterator
    var entries = std.ArrayList(Tree.Entry).init(allocator);
    defer entries.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try entries.append(entry);
    }
    
    try testing.expectEqual(@as(usize, 100), entries.items.len);
    
    // Verify correct ordering
    for (0..100) |j| {
        try testing.expectEqual(@as(i32, @intCast(j)), entries.items[j].key);
        try testing.expectEqual(@as(i32, @intCast(j * 10)), entries.items[j].value);
    }
}

test "should handle large value types" {
    const allocator = testing.allocator;
    
    // Large struct as value type
    const LargeValue = struct {
        data: [1024]u8,
        id: u64,
        
        fn init(id: u64) @This() {
            var value = @This(){
                .data = undefined,
                .id = id,
            };
            // Fill data with pattern
            for (&value.data, 0..) |*byte, idx| {
                byte.* = @truncate(id +% idx);
            }
            return value;
        }
        
        fn verify(self: @This()) bool {
            for (self.data, 0..) |byte, idx| {
                if (byte != @as(u8, @truncate(self.id +% idx))) {
                    return false;
                }
            }
            return true;
        }
    };
    
    const Tree = bplustree.BPlusTree(u64, LargeValue);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert large values
    for (0..10) |i| {
        const key: u64 = i;
        try tree.insert(key, LargeValue.init(key));
    }
    
    // Verify values
    for (0..10) |i| {
        const key: u64 = i;
        const value = tree.get(key).?;
        try testing.expectEqual(key, value.id);
        try testing.expect(value.verify());
    }
}

test "should handle empty tree edge cases" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Operations on empty tree
    try testing.expect(tree.get(42) == null);
    try testing.expect(!tree.contains(42));
    try testing.expectEqual(@as(usize, 0), tree.len());
    try testing.expectEqual(@as(usize, 0), tree.getHeight());
    
    // Iterator on empty tree
    var iter = tree.iterator();
    try testing.expect(iter.next() == null);
    
    // Reverse iterator on empty tree
    var rev_iter = tree.reverseIterator();
    try testing.expect(rev_iter.next() == null);
    
    // Range query on empty tree
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    try tree.range(0, 100, &results);
    try testing.expectEqual(@as(usize, 0), results.items.len);
    
    // Remove from empty tree
    try testing.expectError(Tree.Error.KeyNotFound, tree.remove(42));
    
    // Clear empty tree (should be no-op)
    tree.clear();
    try testing.expectEqual(@as(usize, 0), tree.len());
}