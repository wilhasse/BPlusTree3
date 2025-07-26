const std = @import("std");
const testing = std.testing;
const bplustree = @import("bplustree");

test "should create empty B+ tree" {
    const allocator = testing.allocator;
    
    // Create a B+ tree with capacity 4 for testing
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Tree should be empty
    try testing.expectEqual(@as(usize, 0), tree.len());
}

test "should insert single key-value pair" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert a key-value pair
    try tree.insert(42, 100);
    
    // Tree should have one element
    try testing.expectEqual(@as(usize, 1), tree.len());
}

test "should retrieve inserted value" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert a key-value pair
    try tree.insert(42, 100);
    
    // Retrieve the value
    const value = tree.get(42);
    try testing.expect(value != null);
    try testing.expectEqual(@as(i32, 100), value.?);
}

test "should handle multiple insertions and maintain order" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert multiple key-value pairs in random order
    try tree.insert(5, 50);
    try tree.insert(3, 30);
    try tree.insert(7, 70);
    try tree.insert(1, 10);
    
    // Tree should have four elements
    try testing.expectEqual(@as(usize, 4), tree.len());
    
    // All values should be retrievable
    try testing.expectEqual(@as(i32, 10), tree.get(1).?);
    try testing.expectEqual(@as(i32, 30), tree.get(3).?);
    try testing.expectEqual(@as(i32, 50), tree.get(5).?);
    try testing.expectEqual(@as(i32, 70), tree.get(7).?);
}

test "should update value for duplicate key" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert a key-value pair
    try tree.insert(42, 100);
    
    // Insert same key with different value
    try tree.insert(42, 200);
    
    // Tree should still have one element
    try testing.expectEqual(@as(usize, 1), tree.len());
    
    // Value should be updated
    try testing.expectEqual(@as(i32, 200), tree.get(42).?);
}

test "should return null for non-existent key" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Empty tree should return null
    try testing.expect(tree.get(42) == null);
    
    // Insert some values
    try tree.insert(10, 100);
    try tree.insert(20, 200);
    try tree.insert(30, 300);
    
    // Non-existent keys should return null
    try testing.expect(tree.get(5) == null);    // Before first
    try testing.expect(tree.get(15) == null);   // Between keys
    try testing.expect(tree.get(40) == null);   // After last
}

test "should handle node splitting when capacity exceeded" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert more than capacity (4) to trigger split
    try tree.insert(10, 100);
    try tree.insert(20, 200);
    try tree.insert(30, 300);
    try tree.insert(40, 400);
    try tree.insert(50, 500); // This should trigger a split
    
    // Tree should have 5 elements
    try testing.expectEqual(@as(usize, 5), tree.len());
    
    // All values should still be retrievable
    try testing.expectEqual(@as(i32, 100), tree.get(10).?);
    try testing.expectEqual(@as(i32, 200), tree.get(20).?);
    try testing.expectEqual(@as(i32, 300), tree.get(30).?);
    try testing.expectEqual(@as(i32, 400), tree.get(40).?);
    try testing.expectEqual(@as(i32, 500), tree.get(50).?);
    
    // Tree should have proper structure (root should be branch node after split)
    try testing.expect(tree.getHeight() > 1);
}

test "should delete existing key from tree" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert some data
    try tree.insert(10, 100);
    try tree.insert(20, 200);
    try tree.insert(30, 300);
    try tree.insert(40, 400);
    
    // Delete a key
    const deleted_value = try tree.remove(20);
    
    // Verify deletion
    try testing.expectEqual(@as(i32, 200), deleted_value);
    try testing.expectEqual(@as(usize, 3), tree.len());
    try testing.expect(tree.get(20) == null);
    
    // Other keys should still exist
    try testing.expectEqual(@as(i32, 100), tree.get(10).?);
    try testing.expectEqual(@as(i32, 300), tree.get(30).?);
    try testing.expectEqual(@as(i32, 400), tree.get(40).?);
}

test "should return error when deleting non-existent key" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Insert some data
    try tree.insert(10, 100);
    try tree.insert(30, 300);
    
    // Try to delete non-existent key
    try testing.expectError(error.KeyNotFound, tree.remove(20));
    
    // Tree should remain unchanged
    try testing.expectEqual(@as(usize, 2), tree.len());
    try testing.expectEqual(@as(i32, 100), tree.get(10).?);
    try testing.expectEqual(@as(i32, 300), tree.get(30).?);
}

test "should handle deletion from empty tree" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Try to delete from empty tree
    try testing.expectError(error.KeyNotFound, tree.remove(42));
    
    // Tree should remain empty
    try testing.expectEqual(@as(usize, 0), tree.len());
}

test "should handle sequential deletions maintaining tree integrity" {
    const allocator = testing.allocator;
    
    var tree = bplustree.BPlusTree(i32, i32).init(allocator, 4);
    defer tree.deinit();
    
    // Build a tree that will have multiple levels
    const n = 20;
    for (1..n + 1) |i| {
        try tree.insert(@intCast(i), @intCast(i * 100));
    }
    
    // Verify initial state
    try testing.expectEqual(@as(usize, n), tree.len());
    try testing.expect(tree.getHeight() > 1);
    
    // Delete every other key
    var i: i32 = 2;
    while (i <= n) : (i += 2) {
        const value = try tree.remove(i);
        try testing.expectEqual(@as(i32, i * 100), value);
    }
    
    // Verify tree after deletions
    try testing.expectEqual(@as(usize, n / 2), tree.len());
    
    // Check remaining keys
    i = 1;
    while (i <= n) : (i += 2) {
        try testing.expectEqual(@as(i32, i * 100), tree.get(i).?);
    }
    
    // Check deleted keys are gone
    i = 2;
    while (i <= n) : (i += 2) {
        try testing.expect(tree.get(i) == null);
    }
}

test "should return empty list for range query on empty tree" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Query range on empty tree
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(10, 20, &results);
    
    // Should return empty list
    try testing.expectEqual(@as(usize, 0), results.items.len);
}

test "should return all values in range" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data
    for (1..11) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Query range [3, 7]
    var results = std.ArrayList(Tree.Entry).init(allocator);
    defer results.deinit();
    
    try tree.range(3, 7, &results);
    
    // Should return keys 3, 4, 5, 6, 7
    try testing.expectEqual(@as(usize, 5), results.items.len);
    
    const expected = [_]Tree.Entry{
        .{ .key = 3, .value = 30 },
        .{ .key = 4, .value = 40 },
        .{ .key = 5, .value = 50 },
        .{ .key = 6, .value = 60 },
        .{ .key = 7, .value = 70 },
    };
    
    for (expected, results.items) |exp, res| {
        try testing.expectEqual(exp.key, res.key);
        try testing.expectEqual(exp.value, res.value);
    }
}

test "should iterate all entries in order" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data in random order
    const data = [_]struct { k: i32, v: i32 }{
        .{ .k = 5, .v = 50 },
        .{ .k = 2, .v = 20 },
        .{ .k = 8, .v = 80 },
        .{ .k = 1, .v = 10 },
        .{ .k = 9, .v = 90 },
        .{ .k = 3, .v = 30 },
        .{ .k = 7, .v = 70 },
        .{ .k = 4, .v = 40 },
        .{ .k = 6, .v = 60 },
    };
    
    for (data) |item| {
        try tree.insert(item.k, item.v);
    }
    
    // Iterate and collect all entries
    var entries = std.ArrayList(Tree.Entry).init(allocator);
    defer entries.deinit();
    
    var iter = tree.iterator();
    while (iter.next()) |entry| {
        try entries.append(entry);
    }
    
    // Should have all entries in sorted order
    try testing.expectEqual(@as(usize, 9), entries.items.len);
    
    // Verify sorted order
    for (1..10) |i| {
        try testing.expectEqual(@as(i32, @intCast(i)), entries.items[i - 1].key);
        try testing.expectEqual(@as(i32, @intCast(i * 10)), entries.items[i - 1].value);
    }
}

test "should iterate empty tree" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Iterator on empty tree should return no entries
    var iter = tree.iterator();
    try testing.expect(iter.next() == null);
}

test "should support reverse iteration" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert test data
    for (1..8) |i| {
        try tree.insert(@intCast(i), @intCast(i * 100));
    }
    
    // Reverse iterate and collect entries
    var entries = std.ArrayList(Tree.Entry).init(allocator);
    defer entries.deinit();
    
    var iter = tree.reverseIterator();
    while (iter.next()) |entry| {
        try entries.append(entry);
    }
    
    // Should have all entries in reverse order
    try testing.expectEqual(@as(usize, 7), entries.items.len);
    
    // Verify reverse order
    for (0..7) |i| {
        const expected_key = 7 - @as(i32, @intCast(i));
        try testing.expectEqual(expected_key, entries.items[i].key);
        try testing.expectEqual(expected_key * 100, entries.items[i].value);
    }
}

test "should check if key exists with contains" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Empty tree contains nothing
    try testing.expect(!tree.contains(42));
    
    // Insert some values
    try tree.insert(10, 100);
    try tree.insert(20, 200);
    try tree.insert(30, 300);
    
    // Check existing keys
    try testing.expect(tree.contains(10));
    try testing.expect(tree.contains(20));
    try testing.expect(tree.contains(30));
    
    // Check non-existing keys
    try testing.expect(!tree.contains(5));
    try testing.expect(!tree.contains(15));
    try testing.expect(!tree.contains(40));
    
    // Delete a key and verify contains
    _ = try tree.remove(20);
    try testing.expect(!tree.contains(20));
    try testing.expect(tree.contains(10));
    try testing.expect(tree.contains(30));
}

test "should clear all entries from tree" {
    const allocator = testing.allocator;
    
    const Tree = bplustree.BPlusTree(i32, i32);
    var tree = Tree.init(allocator, 4);
    defer tree.deinit();
    
    // Insert multiple entries
    for (1..21) |i| {
        try tree.insert(@intCast(i), @intCast(i * 10));
    }
    
    // Verify tree has entries and height > 1
    try testing.expectEqual(@as(usize, 20), tree.len());
    try testing.expect(tree.getHeight() > 1);
    
    // Clear the tree
    tree.clear();
    
    // Tree should be empty
    try testing.expectEqual(@as(usize, 0), tree.len());
    try testing.expectEqual(@as(usize, 0), tree.getHeight());
    
    // Should not find any keys
    try testing.expect(!tree.contains(10));
    
    // Iterator should return nothing
    var iter = tree.iterator();
    try testing.expect(iter.next() == null);
    
    // Should be able to insert again
    try tree.insert(42, 420);
    try testing.expectEqual(@as(usize, 1), tree.len());
    try testing.expectEqual(@as(i32, 420), tree.get(42).?);
}